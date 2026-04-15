from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

from tts_mcp.config import ServerConfig, load_settings
from tts_mcp.platform import BackendSelection
import tts_mcp.execution_support as execution_support
import tts_mcp.routing_policy as routing_policy
import tts_mcp.runner as runner
import tts_mcp.server as server_module

from mcp_session_test_support import _run_with_session
from mlx_language_test_support import _MIN_VALID_WAV_BYTES, _mlx_host, _mock_runtime_version_check


@pytest.mark.anyio
async def test_speak_tool_omits_public_language_when_caller_uses_default_language(monkeypatch):
    runner_result = {
        "ok": True,
        "backend": "mlx_audio",
        "platform": "Darwin",
        "machine": "arm64",
        "command": ["mlx_audio.tts.generate", "--text", "hi"],
        "output_path": "/tmp/out.wav",
        "played": True,
        "playback_command": None,
        "warnings": [],
        "stdout": "ok",
        "stderr": None,
        "exit_code": 0,
        "error_type": None,
        "error_message": None,
    }
    captured: dict[str, object] = {}

    def fake_run_speak(**kwargs):
        captured.update(kwargs)
        return runner_result

    monkeypatch.setattr(server_module, "run_speak", fake_run_speak)

    server = server_module.create_server(
        settings=load_settings({"TTS_MCP_AUTO_INSTALL_RUNTIME": "false"}),
        server_config=ServerConfig(name="tts-test"),
    )

    async def run_client(session) -> None:
        result = await session.call_tool("speak", {"text": "hello"})
        assert not result.isError
        assert result.structuredContent == {"ok": True}
        assert captured["play"] is True
        assert captured["speed"] == 1.0
        assert "language_code" not in captured
        assert "voice" not in captured

    await _run_with_session(server, run_client)


def test_run_speak_mlx_defaults_to_english_model_and_language(monkeypatch, tmp_path: Path) -> None:
    settings = load_settings({"TTS_MCP_OUTPUT_DIR": str(tmp_path)})

    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="mlx_audio", command=settings.mlx_command, host=_mlx_host()),
    )

    output_file = tmp_path / "mlx.wav"

    def fake_run(command, **kwargs):
        assert command[0] == settings.mlx_command
        assert command[command.index("--model") + 1] == "mlx-community/Kokoro-82M-bf16"
        assert command[command.index("--lang_code") + 1] == "a"
        assert command[command.index("--temperature") + 1] == "0.0"
        prefix = command[command.index("--file_prefix") + 1]
        Path(f"{prefix}.wav").write_bytes(_MIN_VALID_WAV_BYTES)
        return subprocess.CompletedProcess(command, 0, "ok", "")

    monkeypatch.setattr(execution_support.subprocess, "run", fake_run)

    result = runner.run_speak(
        settings=settings,
        text="Hello from MLX",
        output_path=str(output_file),
        play=False,
    )

    assert result["ok"] is True
    assert result["backend"] == "mlx_audio"
    assert result["output_path"] == str(output_file)
    assert result["warnings"] == []


def test_resolve_mlx_request_defaults_to_kokoro_for_english() -> None:
    settings = load_settings({})

    resolved = routing_policy.resolve_mlx_request(settings=settings, language_code=None)

    assert resolved.model_id == "mlx-community/Kokoro-82M-bf16"
    assert resolved.language_code == "a"
    assert resolved.auto_model_selection_applied is True
