from __future__ import annotations

from typing import TypedDict


class SshToolResult(TypedDict):
    ok: bool
    action: str
    command: list[str]
    session_id: str | None
    destination: str | None
    host: str | None
    user: str | None
    port: int | None
    remote_command: str | None
    cwd: str | None
    stdout: str | None
    stderr: str | None
    exit_code: int | None
    duration_ms: int | None
    error_type: str | None
    error_message: str | None
    session_count: int | None
    created_at: float | None
    last_used_at: float | None
