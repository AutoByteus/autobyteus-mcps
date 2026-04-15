from __future__ import annotations

from pathlib import Path

import pytest

from real_smoke_support import resolve_mlx_command
from real_mcp_speak_tool_support import IS_APPLE_SILICON_MAC, RUN_REAL_MCP_SPEAK
from mcp_session_test_support import _run_with_session
from tts_mcp.config import ServerConfig, load_settings
import tts_mcp.server as server_module


def _create_real_mcp_english_server(tmp_path: Path):
    mlx_command = resolve_mlx_command()
    if mlx_command is None:
        pytest.skip(
            "Missing MLX audio command. Run scripts/install_mlx_audio_macos.sh or set MLX_TTS_COMMAND."
        )

    settings = load_settings(
        {
            "TTS_MCP_BACKEND": "mlx_audio",
            "TTS_MCP_OUTPUT_DIR": str(tmp_path),
            "TTS_MCP_TIMEOUT_SECONDS": "1200",
            "TTS_MCP_ENFORCE_LATEST": "false",
            "TTS_MCP_AUTO_INSTALL_RUNTIME": "false",
            "TTS_MCP_MLX_MODEL_PRESET": "kokoro_fast",
            "MLX_TTS_MODEL": "mlx-community/Kokoro-82M-bf16",
            "MLX_TTS_COMMAND": mlx_command,
        }
    )
    return server_module.create_server(
        settings=settings,
        server_config=ServerConfig(name="tts-real-mcp-english-test"),
    )


@pytest.mark.skipif(
    not RUN_REAL_MCP_SPEAK,
    reason="Set TTS_MCP_RUN_REAL_MCP_SPEAK=1 to run real MCP speak-tool playback test.",
)
@pytest.mark.skipif(
    not IS_APPLE_SILICON_MAC,
    reason="Real MCP speak-tool playback test requires Apple Silicon macOS.",
)
@pytest.mark.anyio
async def test_real_mcp_speak_tool_routes_english_to_apple_silicon_kokoro(tmp_path: Path) -> None:
    server = _create_real_mcp_english_server(tmp_path)

    async def run_client(session) -> None:
        explicit_output = tmp_path / "real_mcp_speak_english.wav"
        result = await session.call_tool(
            "speak",
            {
                "text": "Real MCP speak tool playback check.",
                "output_path": str(explicit_output),
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
    reason="Set TTS_MCP_RUN_REAL_MCP_SPEAK=1 to run real MCP speak-tool playback test.",
)
@pytest.mark.skipif(
    not IS_APPLE_SILICON_MAC,
    reason="Real MCP speak-tool playback test requires Apple Silicon macOS.",
)
@pytest.mark.anyio
async def test_real_mcp_speak_tool_routes_explicit_english_voice_to_apple_silicon_kokoro(
    tmp_path: Path,
) -> None:
    server = _create_real_mcp_english_server(tmp_path)

    async def run_client(session) -> None:
        explicit_output = tmp_path / "real_mcp_speak_english_voice.wav"
        result = await session.call_tool(
            "speak",
            {
                "text": "Real MCP speak tool English voice check.",
                "language": "en",
                "voice": "af_heart",
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
