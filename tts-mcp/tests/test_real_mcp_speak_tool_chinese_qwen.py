from __future__ import annotations

import os
from pathlib import Path
import platform

import anyio
import pytest

pytest.importorskip("mcp")

from mcp.client.session import ClientSession
from mcp.shared.message import SessionMessage

from real_smoke_support import resolve_mlx_command
from tts_mcp.config import ServerConfig, load_settings
import tts_mcp.server as server_module


RUN_REAL_MCP_SPEAK = os.getenv("TTS_MCP_RUN_REAL_MCP_SPEAK") == "1"
IS_APPLE_SILICON_MAC = (
    platform.system() == "Darwin"
    and platform.machine().strip().lower() in {"arm64", "aarch64"}
)


async def _run_with_session(server, client_callable):
    client_to_server_send, server_read_stream = anyio.create_memory_object_stream[SessionMessage | Exception](0)
    server_to_client_send, client_read_stream = anyio.create_memory_object_stream[SessionMessage](0)

    async def server_task():
        await server._mcp_server.run(  # type: ignore[attr-defined]
            server_read_stream,
            server_to_client_send,
            server._mcp_server.create_initialization_options(),  # type: ignore[attr-defined]
            raise_exceptions=True,
        )

    async with anyio.create_task_group() as tg:
        tg.start_soon(server_task)
        async with ClientSession(client_read_stream, client_to_server_send) as session:
            await session.initialize()
            await client_callable(session)
        await client_to_server_send.aclose()
        await server_to_client_send.aclose()
        tg.cancel_scope.cancel()


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

    server = server_module.create_server(
        settings=settings,
        server_config=ServerConfig(name="tts-real-mcp-chinese-qwen-test"),
    )

    async def run_client(session: ClientSession) -> None:
        explicit_output = tmp_path / "real_mcp_speak_chinese_qwen.wav"
        result = await session.call_tool(
            "speak",
            {
                "text": "你好，这是苹果芯片中文端到端测试。",
                "language_code": "zh",
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
