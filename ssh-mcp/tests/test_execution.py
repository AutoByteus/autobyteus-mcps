from __future__ import annotations

import subprocess

from ssh_mcp import execution
from ssh_mcp.execution import ExecutionSpec


def _spec() -> ExecutionSpec:
    return ExecutionSpec(
        action="open_session",
        command=["ssh", "host-a"],
        session_id="abc12345",
        destination="host-a",
        host="host-a",
        user=None,
        port=None,
        remote_command=None,
        cwd=None,
        created_at=None,
        last_used_at=None,
        env=None,
    )


def test_timeout_preserves_bytes_output(monkeypatch) -> None:
    def fake_run(*_args: object, **_kwargs: object):
        raise subprocess.TimeoutExpired(
            ["ssh", "host-a"],
            timeout=1,
            output=b"partial stdout",
            stderr=b"host key rejected",
        )

    monkeypatch.setattr(execution.subprocess, "run", fake_run)

    result = execution.execute(_spec(), timeout_seconds=1, max_output_chars=200)

    assert result["ok"] is False
    assert result["error_type"] == "timeout"
    assert result["stdout"] == "partial stdout"
    assert result["stderr"] == "host key rejected"
