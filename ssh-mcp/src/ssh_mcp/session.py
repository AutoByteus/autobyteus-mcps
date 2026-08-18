from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import secrets
import tempfile
import threading

from .config import ConfigError


@dataclass(slots=True)
class SessionRecord:
    session_id: str
    destination: str
    host: str
    user: str | None
    port: int | None
    default_cwd: str | None
    control_path: str
    created_at: float
    last_used_at: float


class SessionManager:
    def __init__(self, session_dir: str | None = None) -> None:
        short_tmp_dir = Path("/tmp")
        if session_dir is None:
            self._root_dir = Path(tempfile.mkdtemp(prefix="sshmcp-", dir=str(short_tmp_dir)))
        else:
            self._root_dir = Path(session_dir)
            self._root_dir.mkdir(parents=True, exist_ok=True)

        self._fallback_socket_dir = short_tmp_dir / "ssh-mcp-sockets"
        self._fallback_socket_dir.mkdir(parents=True, exist_ok=True)
        self._askpass_script_path = self._root_dir / "ssh-askpass.sh"

        self._lock = threading.Lock()
        self._sessions: dict[str, SessionRecord] = {}

    @property
    def root_dir(self) -> str:
        return str(self._root_dir)

    def control_path_for(self, session_id: str) -> str:
        socket_name = f"s-{session_id}.sock"
        preferred = str(self._root_dir / socket_name)
        if len(preferred) <= 100:
            return preferred

        fallback = str(self._fallback_socket_dir / socket_name)
        if len(fallback) <= 100:
            return fallback

        raise ConfigError("Unable to allocate a valid SSH control socket path within length limits.")

    def askpass_script_path(self) -> str:
        return str(self._askpass_script_path)

    def generate_session_id(self) -> str:
        with self._lock:
            for _ in range(50):
                candidate = secrets.token_hex(4)
                if candidate not in self._sessions:
                    return candidate
        raise ConfigError("Failed to allocate a unique session_id.")

    def ensure_capacity(self, max_sessions: int) -> None:
        with self._lock:
            if len(self._sessions) >= max_sessions:
                raise ConfigError(
                    f"Session limit reached ({max_sessions}). Close a session before opening a new one."
                )

    def add(self, record: SessionRecord, max_sessions: int) -> None:
        with self._lock:
            if len(self._sessions) >= max_sessions:
                raise ConfigError(
                    f"Session limit reached ({max_sessions}). Close a session before opening a new one."
                )
            self._sessions[record.session_id] = record

    def get(self, session_id: str) -> SessionRecord | None:
        with self._lock:
            return self._sessions.get(session_id)

    def pop(self, session_id: str) -> SessionRecord | None:
        with self._lock:
            return self._sessions.pop(session_id, None)

    def touch(self, session_id: str, used_at: float) -> SessionRecord | None:
        with self._lock:
            record = self._sessions.get(session_id)
            if record is None:
                return None
            record.last_used_at = used_at
            return record

    def remove_expired(self, idle_timeout_seconds: int, now: float) -> list[SessionRecord]:
        with self._lock:
            expired_ids = [
                session_id
                for session_id, record in self._sessions.items()
                if now - record.last_used_at >= idle_timeout_seconds
            ]
            return [self._sessions.pop(session_id) for session_id in expired_ids]

    def count(self) -> int:
        with self._lock:
            return len(self._sessions)
