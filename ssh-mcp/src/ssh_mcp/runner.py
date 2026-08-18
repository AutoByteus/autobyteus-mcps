from __future__ import annotations

import os
from pathlib import Path
import shlex
import shutil
import subprocess
import time

from .config import (
    ConfigError,
    SshSettings,
    normalize_remote_command,
    normalize_session_id,
    resolve_password,
    resolve_remote_cwd,
    resolve_target,
)
from .execution import ExecutionSpec, error_result, execute
from .session import SessionManager, SessionRecord
from .types import SshToolResult


def create_session_manager(settings: SshSettings) -> SessionManager:
    return SessionManager(session_dir=settings.session_dir)


def run_health_check(settings: SshSettings) -> SshToolResult:
    if shutil.which(settings.command) is None:
        return error_result(
            action="health_check",
            command=[settings.command],
            session_id=None,
            destination=None,
            host=None,
            user=None,
            port=None,
            remote_command=None,
            cwd=None,
            created_at=None,
            last_used_at=None,
            error_type="config",
            error_message=f"SSH command '{settings.command}' was not found.",
            session_count=None,
        )

    spec = ExecutionSpec(
        action="health_check",
        command=[settings.command, *settings.health_check_args],
        session_id=None,
        destination=None,
        host=None,
        user=None,
        port=None,
        remote_command=None,
        cwd=None,
        created_at=None,
        last_used_at=None,
        env=None,
    )
    return execute(spec=spec, timeout_seconds=settings.timeout_seconds, max_output_chars=settings.max_output_chars)


def run_open_session(
    settings: SshSettings,
    manager: SessionManager,
    host: str | None = None,
    user: str | None = None,
    port: int | None = None,
    cwd: str | None = None,
) -> SshToolResult:
    _cleanup_expired_sessions(settings=settings, manager=manager)

    try:
        target = resolve_target(settings=settings, host=host, user=user, port=port)
        normalized_cwd = resolve_remote_cwd(cwd)
        manager.ensure_capacity(settings.max_sessions)
        execution_env = _build_execution_env(settings=settings, manager=manager)
    except ConfigError as exc:
        return error_result(
            action="open_session",
            command=[settings.command],
            session_id=None,
            destination=None,
            host=host.strip() if host else settings.default_host,
            user=user.strip() if user else None,
            port=port,
            remote_command=None,
            cwd=cwd.strip() if cwd else None,
            created_at=None,
            last_used_at=None,
            error_type="validation",
            error_message=str(exc),
            session_count=manager.count(),
        )

    session_id = manager.generate_session_id()
    control_path = manager.control_path_for(session_id)
    password_auth_enabled = execution_env is not None
    open_command = _build_open_command(
        settings=settings,
        destination=target.destination,
        port=target.port,
        control_path=control_path,
        password_auth_enabled=password_auth_enabled,
    )
    spec = ExecutionSpec(
        action="open_session",
        command=open_command,
        session_id=session_id,
        destination=target.destination,
        host=target.host,
        user=target.user,
        port=target.port,
        remote_command=None,
        cwd=normalized_cwd,
        created_at=None,
        last_used_at=None,
        env=execution_env,
    )
    open_result = execute(spec=spec, timeout_seconds=settings.timeout_seconds, max_output_chars=settings.max_output_chars)
    if not open_result["ok"]:
        open_result["session_count"] = manager.count()
        return open_result

    now = time.time()
    record = SessionRecord(
        session_id=session_id,
        destination=target.destination,
        host=target.host,
        user=target.user,
        port=target.port,
        default_cwd=normalized_cwd,
        control_path=control_path,
        created_at=now,
        last_used_at=now,
    )

    try:
        manager.add(record, settings.max_sessions)
    except ConfigError as exc:
        _best_effort_close_control_master(settings=settings, record=record)
        _safe_unlink(record.control_path)
        return error_result(
            action="open_session",
            command=open_command,
            session_id=session_id,
            destination=target.destination,
            host=target.host,
            user=target.user,
            port=target.port,
            remote_command=None,
            cwd=normalized_cwd,
            created_at=now,
            last_used_at=now,
            error_type="validation",
            error_message=str(exc),
            session_count=manager.count(),
        )

    return SshToolResult(
        ok=True,
        action="open_session",
        command=open_command,
        session_id=session_id,
        destination=target.destination,
        host=target.host,
        user=target.user,
        port=target.port,
        remote_command=None,
        cwd=normalized_cwd,
        stdout=open_result["stdout"],
        stderr=open_result["stderr"],
        exit_code=open_result["exit_code"],
        duration_ms=open_result["duration_ms"],
        error_type=None,
        error_message=None,
        session_count=manager.count(),
        created_at=now,
        last_used_at=now,
    )


def run_session_exec(
    settings: SshSettings,
    manager: SessionManager,
    session_id: str,
    command: str,
    cwd: str | None = None,
) -> SshToolResult:
    _cleanup_expired_sessions(settings=settings, manager=manager)

    try:
        normalized_session_id = normalize_session_id(session_id)
        normalized_command = normalize_remote_command(command, max_chars=settings.max_command_chars)
        normalized_cwd = resolve_remote_cwd(cwd)
        execution_env = _build_execution_env(settings=settings, manager=manager)
    except ConfigError as exc:
        return error_result(
            action="session_exec",
            command=[settings.command],
            session_id=session_id.strip().lower() if session_id else None,
            destination=None,
            host=None,
            user=None,
            port=None,
            remote_command=None,
            cwd=cwd.strip() if cwd else None,
            created_at=None,
            last_used_at=None,
            error_type="validation",
            error_message=str(exc),
            session_count=manager.count(),
        )

    record = manager.get(normalized_session_id)
    if record is None:
        return error_result(
            action="session_exec",
            command=[settings.command],
            session_id=normalized_session_id,
            destination=None,
            host=None,
            user=None,
            port=None,
            remote_command=None,
            cwd=normalized_cwd,
            created_at=None,
            last_used_at=None,
            error_type="execution",
            error_message=f"Session '{normalized_session_id}' was not found or has expired.",
            session_count=manager.count(),
        )

    effective_cwd = normalized_cwd if normalized_cwd is not None else record.default_cwd
    remote_command = _compose_remote_command(command=normalized_command, cwd=effective_cwd)
    exec_command = _build_session_exec_command(
        settings=settings,
        record=record,
        remote_command=remote_command,
        password_auth_enabled=execution_env is not None,
    )
    spec = ExecutionSpec(
        action="session_exec",
        command=exec_command,
        session_id=record.session_id,
        destination=record.destination,
        host=record.host,
        user=record.user,
        port=record.port,
        remote_command=remote_command,
        cwd=effective_cwd,
        created_at=record.created_at,
        last_used_at=record.last_used_at,
        env=execution_env,
    )
    result = execute(spec=spec, timeout_seconds=settings.timeout_seconds, max_output_chars=settings.max_output_chars)

    touched = manager.touch(record.session_id, time.time())
    if touched is not None:
        result["last_used_at"] = touched.last_used_at
    result["session_count"] = manager.count()
    return result


def run_close_session(settings: SshSettings, manager: SessionManager, session_id: str) -> SshToolResult:
    _cleanup_expired_sessions(settings=settings, manager=manager)

    try:
        normalized_session_id = normalize_session_id(session_id)
    except ConfigError as exc:
        return error_result(
            action="close_session",
            command=[settings.command],
            session_id=session_id.strip().lower() if session_id else None,
            destination=None,
            host=None,
            user=None,
            port=None,
            remote_command=None,
            cwd=None,
            created_at=None,
            last_used_at=None,
            error_type="validation",
            error_message=str(exc),
            session_count=manager.count(),
        )

    record = manager.pop(normalized_session_id)
    if record is None:
        return error_result(
            action="close_session",
            command=[settings.command],
            session_id=normalized_session_id,
            destination=None,
            host=None,
            user=None,
            port=None,
            remote_command=None,
            cwd=None,
            created_at=None,
            last_used_at=None,
            error_type="execution",
            error_message=f"Session '{normalized_session_id}' was not found or has already been closed.",
            session_count=manager.count(),
        )

    close_command = _build_close_command(settings=settings, record=record, password_auth_enabled=False)
    spec = ExecutionSpec(
        action="close_session",
        command=close_command,
        session_id=record.session_id,
        destination=record.destination,
        host=record.host,
        user=record.user,
        port=record.port,
        remote_command=None,
        cwd=record.default_cwd,
        created_at=record.created_at,
        last_used_at=record.last_used_at,
        env=None,
    )
    result = execute(spec=spec, timeout_seconds=settings.timeout_seconds, max_output_chars=settings.max_output_chars)
    _safe_unlink(record.control_path)
    result["session_count"] = manager.count()
    return result


def _cleanup_expired_sessions(settings: SshSettings, manager: SessionManager) -> None:
    now = time.time()
    expired = manager.remove_expired(settings.session_idle_timeout_seconds, now)
    for record in expired:
        _best_effort_close_control_master(settings=settings, record=record)
        _safe_unlink(record.control_path)


def _build_open_command(
    settings: SshSettings,
    destination: str,
    port: int | None,
    control_path: str,
    password_auth_enabled: bool,
) -> list[str]:
    command = [settings.command, *_build_auth_args(settings, password_auth_enabled=password_auth_enabled)]
    if port is not None:
        command.extend(["-p", str(port)])
    command.extend(
        [
            "-o",
            "ControlMaster=yes",
            "-o",
            f"ControlPath={control_path}",
            "-o",
            f"ControlPersist={settings.session_idle_timeout_seconds}",
            destination,
            "--",
            "echo __ssh_mcp_session_opened__",
        ]
    )
    return command


def _build_session_exec_command(
    settings: SshSettings,
    record: SessionRecord,
    remote_command: str,
    password_auth_enabled: bool,
) -> list[str]:
    command = [settings.command, *_build_auth_args(settings, password_auth_enabled=password_auth_enabled)]
    if record.port is not None:
        command.extend(["-p", str(record.port)])
    command.extend(
        [
            "-o",
            "ControlMaster=no",
            "-o",
            f"ControlPath={record.control_path}",
            record.destination,
            "--",
            remote_command,
        ]
    )
    return command


def _build_close_command(
    settings: SshSettings,
    record: SessionRecord,
    password_auth_enabled: bool,
) -> list[str]:
    command = [settings.command, *_build_auth_args(settings, password_auth_enabled=password_auth_enabled)]
    if record.port is not None:
        command.extend(["-p", str(record.port)])
    command.extend(["-o", f"ControlPath={record.control_path}", "-O", "exit", record.destination])
    return command


def _build_auth_args(settings: SshSettings, password_auth_enabled: bool) -> list[str]:
    auth_args: list[str] = []
    if settings.private_key_file is not None:
        auth_args.extend(["-i", settings.private_key_file, "-o", "IdentitiesOnly=yes"])

    if password_auth_enabled:
        auth_args.extend(
            [
                "-o",
                "BatchMode=no",
                "-o",
                "PubkeyAuthentication=no",
                "-o",
                "PreferredAuthentications=password,keyboard-interactive",
            ]
        )
    else:
        auth_args.extend(["-o", "BatchMode=yes"])

    return auth_args


def _build_execution_env(settings: SshSettings, manager: SessionManager) -> dict[str, str] | None:
    password = resolve_password(settings)
    if password is None:
        return None

    askpass_path = _ensure_askpass_script(manager.askpass_script_path())
    env = dict(os.environ)
    env["SSH_ASKPASS"] = askpass_path
    env["SSH_ASKPASS_REQUIRE"] = "force"
    env["DISPLAY"] = env.get("DISPLAY", ":0")
    env["SSH_MCP_TOOL_PASSWORD"] = password
    return env


def _ensure_askpass_script(path: str) -> str:
    script = Path(path)
    if not script.exists():
        script.write_text(
            "#!/bin/sh\n"
            "printf '%s\\n' \"$SSH_MCP_TOOL_PASSWORD\"\n",
            encoding="utf-8",
        )
        script.chmod(0o700)
    return str(script)


def _compose_remote_command(command: str, cwd: str | None) -> str:
    if cwd is None:
        return command
    return f"cd {shlex.quote(cwd)} && {command}"


def _best_effort_close_control_master(settings: SshSettings, record: SessionRecord) -> None:
    try:
        subprocess.run(
            _build_close_command(settings=settings, record=record, password_auth_enabled=False),
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
            timeout=settings.timeout_seconds,
            check=False,
        )
    except Exception:
        return


def _safe_unlink(path: str) -> None:
    try:
        Path(path).unlink(missing_ok=True)
    except OSError:
        return
