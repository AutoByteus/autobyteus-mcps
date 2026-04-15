from __future__ import annotations

import pytest

from mcp_session_test_support import _run_with_session
from tts_mcp.config import ServerConfig, load_settings
import tts_mcp.server as server_module


@pytest.mark.anyio
async def test_speak_tool_schema_describes_voice_input() -> None:
    server = server_module.create_server(
        settings=load_settings({"TTS_MCP_AUTO_INSTALL_RUNTIME": "false"}),
        server_config=ServerConfig(name="tts-test"),
    )

    async def run_client(session) -> None:
        tools = await session.list_tools()
        speak_tool = next(tool for tool in tools.tools if tool.name == "speak")
        schema_properties = speak_tool.inputSchema.get("properties") or {}
        voice_schema = schema_properties["voice"]
        assert "af_heart" in voice_schema["description"]
        assert "Vivian" in voice_schema["description"]
        assert "eric" in voice_schema["description"]
        assert "serena" in voice_schema["description"]
        assert "XTTS" in voice_schema["description"]
        assert voice_schema["examples"] == ["af_heart", "Vivian", "eric", "serena"]

    await _run_with_session(server, run_client)


@pytest.mark.anyio
async def test_speak_tool_delegates_voice_to_runner(monkeypatch):
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
        result = await session.call_tool(
            "speak",
            {"text": "hello", "voice": "Vivian", "play": False},
        )
        assert not result.isError
        assert result.structuredContent == {"ok": True}
        assert captured["voice"] == "Vivian"

    await _run_with_session(server, run_client)
