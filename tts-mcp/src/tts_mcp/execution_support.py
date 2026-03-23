from __future__ import annotations

from datetime import datetime
import fcntl
import os
from pathlib import Path
import shutil
import subprocess
import time
from typing import TypedDict

from .config import ConfigError


class OutputSignature(TypedDict):
    size: int
    mtime_ns: int


class ResolvedOutputPath(TypedDict):
    path: Path
    is_auto_generated: bool


class ExecutionResult(TypedDict):
    stdout: str | None
    stderr: str | None
    exit_code: int | None
    error_type: str | None
    error_message: str | None


_GLOBAL_LOCK_FILE = Path("/tmp/tts_mcp_global_generation.lock")


def resolve_output_path(
    candidate: str | None,
    default_output_dir: str,
) -> ResolvedOutputPath:
    is_auto_generated = candidate is None
    if candidate is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        raw_path = Path(default_output_dir) / f"speak_{timestamp}.wav"
    else:
        raw_path = Path(candidate).expanduser()

    if not raw_path.is_absolute():
        raw_path = Path.cwd() / raw_path

    if raw_path.suffix == "":
        raw_path = raw_path.with_suffix(".wav")
    if raw_path.suffix.lower() != ".wav":
        raise ConfigError("output_path must end with .wav")

    raw_path.parent.mkdir(parents=True, exist_ok=True)
    return ResolvedOutputPath(
        path=raw_path.resolve(strict=False),
        is_auto_generated=is_auto_generated,
    )


def build_linux_play_command(
    audio_path: Path,
    linux_player: str,
) -> list[str] | None:
    if linux_player == "none":
        return None

    candidates: list[tuple[str, list[str]]]
    if linux_player == "ffplay":
        candidates = [("ffplay", ["-nodisp", "-autoexit", str(audio_path)])]
    elif linux_player == "aplay":
        candidates = [("aplay", [str(audio_path)])]
    elif linux_player == "paplay":
        candidates = [("paplay", [str(audio_path)])]
    else:
        candidates = [
            ("ffplay", ["-nodisp", "-autoexit", str(audio_path)]),
            ("afplay", [str(audio_path)]),
            ("aplay", [str(audio_path)]),
            ("paplay", [str(audio_path)]),
        ]

    for binary, args in candidates:
        if shutil.which(binary):
            return [binary, *args]
    return None


def execute_command(
    command: list[str],
    timeout_seconds: int,
    env_overrides: dict[str, str] | None = None,
) -> ExecutionResult:
    merged_env = None
    if env_overrides:
        merged_env = os.environ.copy()
        merged_env.update(env_overrides)

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
            env=merged_env,
        )
    except FileNotFoundError:
        return ExecutionResult(
            stdout=None,
            stderr=None,
            exit_code=None,
            error_type="dependency",
            error_message=f"Command not found: {command[0]}",
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.output if isinstance(exc.output, str) else None
        stderr = exc.stderr if isinstance(exc.stderr, str) else None
        return ExecutionResult(
            stdout=stdout,
            stderr=stderr,
            exit_code=None,
            error_type="timeout",
            error_message=f"Command timed out after {timeout_seconds} seconds.",
        )
    except OSError as exc:
        return ExecutionResult(
            stdout=None,
            stderr=None,
            exit_code=None,
            error_type="execution",
            error_message=f"Failed to execute command: {exc}",
        )

    return ExecutionResult(
        stdout=_clean_output(completed.stdout),
        stderr=_clean_output(completed.stderr),
        exit_code=completed.returncode,
        error_type=None,
        error_message=None,
    )


def linux_playback_confirmed(
    command: list[str],
    playback: ExecutionResult,
) -> bool:
    if playback["exit_code"] != 0:
        return False

    binary = Path(command[0]).name.lower()
    if binary == "ffplay":
        combined = f"{playback['stdout'] or ''}\n{playback['stderr'] or ''}".lower()
        ffplay_failure_markers = (
            "audio open failed",
            "failed to open file",
            "configure filtergraph",
        )
        if any(marker in combined for marker in ffplay_failure_markers):
            return False

    return True


def acquire_global_generation_lock(timeout_seconds: int) -> int | None:
    _GLOBAL_LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(_GLOBAL_LOCK_FILE, os.O_CREAT | os.O_RDWR, 0o600)
    deadline = time.monotonic() + timeout_seconds

    while True:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return fd
        except BlockingIOError:
            if time.monotonic() >= deadline:
                os.close(fd)
                return None
            time.sleep(0.1)
        except OSError:
            os.close(fd)
            return None


def release_global_generation_lock(fd: int) -> None:
    try:
        fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def output_signature(path: Path) -> OutputSignature | None:
    if not path.exists():
        return None

    stat = path.stat()
    return OutputSignature(size=stat.st_size, mtime_ns=stat.st_mtime_ns)


def _clean_output(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned if cleaned else None
