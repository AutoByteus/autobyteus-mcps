from __future__ import annotations

from dataclasses import dataclass
import subprocess
import time

from .types import SshToolResult


@dataclass(frozen=True, slots=True)
class ExecutionSpec:
    action: str
    command: list[str]
    session_id: str | None
    destination: str | None
    host: str | None
    user: str | None
    port: int | None
    remote_command: str | None
    cwd: str | None
    created_at: float | None
    last_used_at: float | None
    env: dict[str, str] | None


def execute(spec: ExecutionSpec, timeout_seconds: int, max_output_chars: int) -> SshToolResult:
    started_at = time.monotonic()
    try:
        completed = subprocess.run(
            spec.command,
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
            env=spec.env,
            timeout=timeout_seconds,
            check=False,
        )
    except FileNotFoundError:
        return error_result(
            action=spec.action,
            command=spec.command,
            session_id=spec.session_id,
            destination=spec.destination,
            host=spec.host,
            user=spec.user,
            port=spec.port,
            remote_command=spec.remote_command,
            cwd=spec.cwd,
            created_at=spec.created_at,
            last_used_at=spec.last_used_at,
            error_type="config",
            error_message=f"Command '{spec.command[0]}' was not found.",
            duration_ms=_duration_ms(started_at),
            session_count=None,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = _normalize_output(exc.output, max_output_chars)
        stderr = _normalize_output(exc.stderr, max_output_chars)
        return error_result(
            action=spec.action,
            command=spec.command,
            session_id=spec.session_id,
            destination=spec.destination,
            host=spec.host,
            user=spec.user,
            port=spec.port,
            remote_command=spec.remote_command,
            cwd=spec.cwd,
            created_at=spec.created_at,
            last_used_at=spec.last_used_at,
            error_type="timeout",
            error_message=f"Command timed out after {timeout_seconds} seconds.",
            stdout=_normalize_output(stdout, max_output_chars),
            stderr=_normalize_output(stderr, max_output_chars),
            duration_ms=_duration_ms(started_at),
            session_count=None,
        )
    except OSError as exc:
        return error_result(
            action=spec.action,
            command=spec.command,
            session_id=spec.session_id,
            destination=spec.destination,
            host=spec.host,
            user=spec.user,
            port=spec.port,
            remote_command=spec.remote_command,
            cwd=spec.cwd,
            created_at=spec.created_at,
            last_used_at=spec.last_used_at,
            error_type="execution",
            error_message=f"Failed to execute command: {exc}",
            duration_ms=_duration_ms(started_at),
            session_count=None,
        )

    stdout = _normalize_output(completed.stdout, max_output_chars)
    stderr = _normalize_output(completed.stderr, max_output_chars)
    duration_ms = _duration_ms(started_at)

    if completed.returncode != 0:
        return error_result(
            action=spec.action,
            command=spec.command,
            session_id=spec.session_id,
            destination=spec.destination,
            host=spec.host,
            user=spec.user,
            port=spec.port,
            remote_command=spec.remote_command,
            cwd=spec.cwd,
            created_at=spec.created_at,
            last_used_at=spec.last_used_at,
            error_type="execution",
            error_message=f"Command exited with status {completed.returncode}.",
            stdout=stdout,
            stderr=stderr,
            exit_code=completed.returncode,
            duration_ms=duration_ms,
            session_count=None,
        )

    return SshToolResult(
        ok=True,
        action=spec.action,
        command=spec.command,
        session_id=spec.session_id,
        destination=spec.destination,
        host=spec.host,
        user=spec.user,
        port=spec.port,
        remote_command=spec.remote_command,
        cwd=spec.cwd,
        stdout=stdout,
        stderr=stderr,
        exit_code=completed.returncode,
        duration_ms=duration_ms,
        error_type=None,
        error_message=None,
        session_count=None,
        created_at=spec.created_at,
        last_used_at=spec.last_used_at,
    )


def error_result(
    action: str,
    command: list[str],
    session_id: str | None,
    destination: str | None,
    host: str | None,
    user: str | None,
    port: int | None,
    remote_command: str | None,
    cwd: str | None,
    created_at: float | None,
    last_used_at: float | None,
    error_type: str,
    error_message: str,
    stdout: str | None = None,
    stderr: str | None = None,
    exit_code: int | None = None,
    duration_ms: int | None = None,
    session_count: int | None = None,
) -> SshToolResult:
    return SshToolResult(
        ok=False,
        action=action,
        command=command,
        session_id=session_id,
        destination=destination,
        host=host,
        user=user,
        port=port,
        remote_command=remote_command,
        cwd=cwd,
        stdout=stdout,
        stderr=stderr,
        exit_code=exit_code,
        duration_ms=duration_ms,
        error_type=error_type,
        error_message=error_message,
        session_count=session_count,
        created_at=created_at,
        last_used_at=last_used_at,
    )


def _duration_ms(started_at: float) -> int:
    return max(0, int((time.monotonic() - started_at) * 1000))


def _normalize_output(value: str | bytes | None, max_output_chars: int) -> str | None:
    if value is None:
        return None
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    if not normalized:
        return None
    if len(normalized) <= max_output_chars:
        return normalized
    return normalized[:max_output_chars] + f"\n...[truncated to {max_output_chars} chars]"
