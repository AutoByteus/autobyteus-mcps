from __future__ import annotations

import pytest

from mcp_session_test_support import _run_with_session
from tts_mcp.config import ServerConfig, load_settings
import tts_mcp.server as server_module


@pytest.mark.anyio
async def test_speak_tool_schema_describes_temperature_input() -> None:
    server = server_module.create_server(
        settings=load_settings({"TTS_MCP_AUTO_INSTALL_RUNTIME": "false"}),
        server_config=ServerConfig(name="tts-test"),
    )

    async def run_client(session) -> None:
        tools = await session.list_tools()
        speak_tool = next(tool for tool in tools.tools if tool.name == "speak")
        schema_properties = speak_tool.inputSchema.get("properties") or {}
        temperature_schema = schema_properties["temperature"]
        assert "0.0" in temperature_schema["description"]
        assert "MLX" in temperature_schema["description"]
        assert temperature_schema["examples"] == [0.0, 0.4]

    await _run_with_session(server, run_client)


@pytest.mark.anyio
async def test_speak_tool_delegates_temperature_to_runner(monkeypatch):
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
            {"text": "hello", "temperature": 0.4, "play": False},
        )
        assert not result.isError
        assert result.structuredContent == {"ok": True}
        assert captured["temperature"] == 0.4

    await _run_with_session(server, run_client)
