from __future__ import annotations

import anyio
import os
from pathlib import Path

import pytest
from PIL import Image

from mcp.client.session import ClientSession
from mcp.shared.message import SessionMessage

from image_audio_mcp.server import create_server

PLACEHOLDER_VALUES = {
    "",
    "YOUR_AUTOBYTEUS_API_KEY",
    "YOUR_LLM_SERVER_HOSTS",
    "YOUR_IMAGE_MODEL_ID",
    "YOUR_SPEECH_MODEL_ID",
    "YOUR_VIDEO_MODEL_ID",
}


def _is_missing(value: str | None) -> bool:
    return not value or value in PLACEHOLDER_VALUES


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if _is_missing(value):
        pytest.skip(f"{name} not set; skipping remote integration tests.")
    return value


def _get_autobyteus_host() -> str:
    hosts = os.getenv("AUTOBYTEUS_LLM_SERVER_HOSTS") or ""
    first_host = hosts.split(",")[0].strip() if hosts else ""
    if _is_missing(first_host):
        pytest.skip("AUTOBYTEUS_LLM_SERVER_HOSTS not set; skipping.")
    return first_host


def _normalize_value(value: str | None) -> str:
    if not value:
        return ""
    return value.strip().strip('"').strip("'")


def _get_image_model_id() -> str:
    return _normalize_value(_require_env("DEFAULT_IMAGE_GENERATION_MODEL"))


def _get_audio_model_id() -> str:
    return _normalize_value(_require_env("DEFAULT_SPEECH_GENERATION_MODEL"))


def _get_video_model_id() -> str:
    return _normalize_value(_require_env("DEFAULT_VIDEO_GENERATION_MODEL"))


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


@pytest.fixture
def anyio_backend():
    return "asyncio"


def _require_autobyteus_config() -> None:
    if _normalize_value(os.getenv("RUN_REMOTE_IMAGE_AUDIO_TESTS")).lower() not in {"1", "true", "yes"}:
        pytest.skip("RUN_REMOTE_IMAGE_AUDIO_TESTS is not enabled; skipping remote provider tests.")
    _require_env("AUTOBYTEUS_API_KEY")
    _get_autobyteus_host()
    _get_image_model_id()
    _get_audio_model_id()


def _require_video_config() -> None:
    if _normalize_value(os.getenv("RUN_REMOTE_IMAGE_AUDIO_TESTS")).lower() not in {"1", "true", "yes"}:
        pytest.skip("RUN_REMOTE_IMAGE_AUDIO_TESTS is not enabled; skipping remote provider tests.")
    _require_env("AUTOBYTEUS_API_KEY")
    _get_autobyteus_host()
    _get_video_model_id()


@pytest.mark.anyio
async def test_generate_image_remote(tmp_path, monkeypatch):
    _require_autobyteus_config()
    monkeypatch.setenv("AUTOBYTEUS_AGENT_WORKSPACE", str(tmp_path))

    server = create_server()

    async def run_client(session: ClientSession) -> None:
        output_path = "generated.png"
        result = await session.call_tool(
            "generate_image",
            {
                "prompt": "A nice dog sitting in a sunny park, friendly expression, realistic photo style.",
                "output_file_path": output_path,
            },
        )
        assert not result.isError
        structured = result.structuredContent
        assert structured is not None

        final_path = Path(structured["file_path"])
        assert final_path.exists()
        assert final_path.stat().st_size > 0

    await _run_with_session(server, run_client)


@pytest.mark.anyio
async def test_generate_video_remote(tmp_path, monkeypatch):
    _require_video_config()
    monkeypatch.setenv("AUTOBYTEUS_AGENT_WORKSPACE", str(tmp_path))

    server = create_server()

    async def run_client(session: ClientSession) -> None:
        output_path = "generated.mp4"
        result = await session.call_tool(
            "generate_video",
            {
                "prompt": "A calm ten second cinematic shot of a small blue cube rotating on a white table.",
                "output_file_path": output_path,
            },
        )
        assert not result.isError
        structured = result.structuredContent
        assert structured is not None

        final_path = Path(structured["file_path"])
        assert final_path.exists()
        assert final_path.stat().st_size > 0

    await _run_with_session(server, run_client)


@pytest.mark.anyio
async def test_generate_speech_remote(tmp_path, monkeypatch):
    _require_autobyteus_config()
    monkeypatch.setenv("AUTOBYTEUS_AGENT_WORKSPACE", str(tmp_path))

    server = create_server()

    async def run_client(session: ClientSession) -> None:
        output_path = "speech.wav"
        result = await session.call_tool(
            "generate_speech",
            {
                "prompt": "Hello from Autobyteus MCP integration test.",
                "output_file_path": output_path,
            },
        )
        assert not result.isError
        structured = result.structuredContent
        assert structured is not None

        final_path = Path(structured["file_path"])
        assert final_path.exists()
        assert final_path.stat().st_size > 0

    await _run_with_session(server, run_client)
