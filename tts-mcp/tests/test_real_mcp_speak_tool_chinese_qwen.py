from __future__ import annotations

import hashlib
from pathlib import Path
import pytest

from real_smoke_support import resolve_mlx_command
from real_mcp_speak_tool_support import IS_APPLE_SILICON_MAC, RUN_REAL_MCP_SPEAK
from mcp_session_test_support import _run_with_session
from tts_mcp.config import ServerConfig, load_settings
import tts_mcp.server as server_module


def _create_real_mcp_chinese_server(tmp_path: Path):
    mlx_command = resolve_mlx_command()
    if mlx_command is None:
        pytest.skip(
            "Missing MLX audio command. Run scripts/install_mlx_audio_macos.sh or set MLX_TTS_COMMAND."
        )

    settings = load_settings(
        {
            "TTS_MCP_BACKEND": "auto",
            "TTS_MCP_OUTPUT_DIR": str(tmp_path),
            "TTS_MCP_TIMEOUT_SECONDS": "2400",
            "TTS_MCP_ENFORCE_LATEST": "false",
            "TTS_MCP_AUTO_INSTALL_RUNTIME": "false",
            "MLX_TTS_COMMAND": mlx_command,
        }
    )
    return server_module.create_server(
        settings=settings,
        server_config=ServerConfig(name="tts-real-mcp-chinese-qwen-test"),
    )


@pytest.mark.skipif(
    not RUN_REAL_MCP_SPEAK,
    reason="Set TTS_MCP_RUN_REAL_MCP_SPEAK=1 to run real MCP speak-tool playback tests.",
)
@pytest.mark.skipif(
    not IS_APPLE_SILICON_MAC,
    reason="Real MCP speak-tool Chinese Qwen test requires Apple Silicon macOS.",
)
@pytest.mark.anyio
async def test_real_mcp_speak_tool_routes_chinese_to_apple_silicon_mlx(tmp_path: Path) -> None:
    server = _create_real_mcp_chinese_server(tmp_path)

    async def run_client(session) -> None:
        explicit_output = tmp_path / "real_mcp_speak_chinese_qwen.wav"
        result = await session.call_tool(
            "speak",
            {
                "text": "你好，这是苹果芯片中文端到端测试。",
                "language": "zh",
                "output_path": str(explicit_output),
                "play": False,
            },
        )
        assert not result.isError
        payload = result.structuredContent
        assert payload["ok"] is True
        assert explicit_output.exists()
        assert explicit_output.stat().st_size > 44

    await _run_with_session(server, run_client)


@pytest.mark.skipif(
    not RUN_REAL_MCP_SPEAK,
    reason="Set TTS_MCP_RUN_REAL_MCP_SPEAK=1 to run real MCP speak-tool playback tests.",
)
@pytest.mark.skipif(
    not IS_APPLE_SILICON_MAC,
    reason="Real MCP speak-tool Chinese Qwen test requires Apple Silicon macOS.",
)
@pytest.mark.anyio
async def test_real_mcp_speak_tool_routes_explicit_chinese_voice_to_apple_silicon_mlx(
    tmp_path: Path,
) -> None:
    server = _create_real_mcp_chinese_server(tmp_path)

    async def run_client(session) -> None:
        explicit_output = tmp_path / "real_mcp_speak_chinese_qwen_voice.wav"
        result = await session.call_tool(
            "speak",
            {
                "text": "你好，这是苹果芯片中文语音角色测试。",
                "language": "zh",
                "voice": "Vivian",
                "output_path": str(explicit_output),
                "play": False,
            },
        )
        assert not result.isError
        payload = result.structuredContent
        assert payload["ok"] is True
        assert explicit_output.exists()
        assert explicit_output.stat().st_size > 44

    await _run_with_session(server, run_client)


@pytest.mark.skipif(
    not RUN_REAL_MCP_SPEAK,
    reason="Set TTS_MCP_RUN_REAL_MCP_SPEAK=1 to run real MCP speak-tool playback tests.",
)
@pytest.mark.skipif(
    not IS_APPLE_SILICON_MAC,
    reason="Real MCP speak-tool Chinese Qwen test requires Apple Silicon macOS.",
)
@pytest.mark.anyio
async def test_real_mcp_speak_tool_defaults_chinese_temperature_to_deterministic_output(
    tmp_path: Path,
) -> None:
    server = _create_real_mcp_chinese_server(tmp_path)

    async def run_client(session) -> None:
        digests: list[str] = []
        for index in range(1, 4):
            explicit_output = tmp_path / f"real_mcp_speak_chinese_qwen_stable_{index}.wav"
            result = await session.call_tool(
                "speak",
                {
                    "text": "你好，这是稳定的中文温度默认值测试。",
                    "language": "zh",
                    "voice": "eric",
                    "output_path": str(explicit_output),
                    "play": False,
                },
            )
            assert not result.isError
            payload = result.structuredContent
            assert payload["ok"] is True
            assert explicit_output.exists()
            assert explicit_output.stat().st_size > 44
            digests.append(hashlib.sha256(explicit_output.read_bytes()).hexdigest())

        assert digests[0] == digests[1] == digests[2]

    await _run_with_session(server, run_client)
