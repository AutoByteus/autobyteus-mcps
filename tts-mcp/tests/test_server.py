from __future__ import annotations

import pytest

from tts_mcp.config import ServerConfig, load_settings
from mcp_session_test_support import _run_with_session
import tts_mcp.server as server_module


@pytest.mark.anyio
async def test_speak_tool_schema_exposes_language_and_voice_inputs() -> None:
    server = server_module.create_server(
        settings=load_settings({"TTS_MCP_AUTO_INSTALL_RUNTIME": "false"}),
        server_config=ServerConfig(name="tts-test"),
    )

    async def run_client(session) -> None:
        tools = await session.list_tools()
        speak_tool = next(tool for tool in tools.tools if tool.name == "speak")
        schema_properties = speak_tool.inputSchema.get("properties") or {}
        properties = set(schema_properties.keys())
        assert properties == {"text", "output_path", "play", "language", "voice", "temperature"}
        assert speak_tool.inputSchema.get("required") == ["text"]
        language_schema = schema_properties["language"]
        assert "zh" in language_schema["description"]
        assert "zh-cn" in language_schema["description"]
        assert "mandarin" in language_schema["description"]
        assert language_schema["examples"] == ["zh", "zh-cn", "en", "de"]

    await _run_with_session(server, run_client)


@pytest.mark.anyio
async def test_speak_tool_returns_reason_on_failure(monkeypatch):
    runner_result = {
        "ok": False,
        "backend": "mlx_audio",
        "platform": "Darwin",
        "machine": "arm64",
        "command": ["mlx_audio.tts.generate", "--text", "hi"],
        "output_path": None,
        "played": False,
        "playback_command": None,
        "warnings": [],
        "stdout": None,
        "stderr": "bad",
        "exit_code": 1,
        "error_type": "execution",
        "error_message": "Backend command failed.",
    }
    expected = {"ok": False, "reason": "Backend command failed."}

    monkeypatch.setattr(server_module, "run_speak", lambda **_: runner_result)

    server = server_module.create_server(
        settings=load_settings({"TTS_MCP_AUTO_INSTALL_RUNTIME": "false"}),
        server_config=ServerConfig(name="tts-test"),
    )

    async def run_client(session) -> None:
        result = await session.call_tool("speak", {"text": "hello"})
        assert not result.isError
        assert result.structuredContent == expected

    await _run_with_session(server, run_client)


@pytest.mark.anyio
async def test_speak_tool_returns_failure_when_playback_not_confirmed(monkeypatch):
    runner_result = {
        "ok": True,
        "backend": "kokoro_onnx",
        "platform": "Linux",
        "machine": "x86_64",
        "command": ["kokoro_onnx.generate", "/tmp/out.wav"],
        "output_path": "/tmp/out.wav",
        "played": False,
        "playback_command": ["ffplay", "-nodisp", "-autoexit", "/tmp/out.wav"],
        "warnings": ["Audio generation succeeded, but playback command failed."],
        "stdout": "ok",
        "stderr": None,
        "exit_code": 0,
        "error_type": None,
        "error_message": None,
    }

    monkeypatch.setattr(server_module, "run_speak", lambda **_: runner_result)

    server = server_module.create_server(
        settings=load_settings({"TTS_MCP_AUTO_INSTALL_RUNTIME": "false"}),
        server_config=ServerConfig(name="tts-test"),
    )

    async def run_client(session) -> None:
        result = await session.call_tool("speak", {"text": "hello", "play": True})
        assert not result.isError
        payload = result.structuredContent
        assert payload["ok"] is False
        assert "playback did not complete" in payload["reason"].lower()

    await _run_with_session(server, run_client)


@pytest.mark.anyio
async def test_speak_tool_allows_generation_only_when_play_false(monkeypatch):
    runner_result = {
        "ok": True,
        "backend": "kokoro_onnx",
        "platform": "Linux",
        "machine": "x86_64",
        "command": ["kokoro_onnx.generate", "/tmp/out.wav"],
        "output_path": "/tmp/out.wav",
        "played": False,
        "playback_command": None,
        "warnings": [],
        "stdout": "ok",
        "stderr": None,
        "exit_code": 0,
        "error_type": None,
        "error_message": None,
    }

    monkeypatch.setattr(server_module, "run_speak", lambda **_: runner_result)

    server = server_module.create_server(
        settings=load_settings({"TTS_MCP_AUTO_INSTALL_RUNTIME": "false"}),
        server_config=ServerConfig(name="tts-test"),
    )

    async def run_client(session) -> None:
        result = await session.call_tool("speak", {"text": "hello", "play": False})
        assert not result.isError
        assert result.structuredContent == {"ok": True}

    await _run_with_session(server, run_client)
