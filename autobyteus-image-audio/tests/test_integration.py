from __future__ import annotations

import anyio
import os
from pathlib import Path

import pytest
from PIL import Image, ImageDraw

from mcp.client.session import ClientSession
from mcp.shared.message import SessionMessage

from autobyteus.llm.llm_factory import LLMFactory
from autobyteus.llm.runtimes import LLMRuntime
from image_audio_mcp.server import create_server

PLACEHOLDER_VALUES = {
    "",
    "YOUR_AUTOBYTEUS_API_KEY",
    "YOUR_LLM_SERVER_HOSTS",
    "YOUR_IMAGE_MODEL_ID",
    "YOUR_SPEECH_MODEL_ID",
}


def _is_missing(value: str | None) -> bool:
    return not value or value in PLACEHOLDER_VALUES


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if _is_missing(value):
        pytest.skip(f"{name} not set in .env.test; skipping remote integration tests.")
    return value


def _get_autobyteus_host() -> str:
    hosts = os.getenv("AUTOBYTEUS_LLM_SERVER_HOSTS") or ""
    first_host = hosts.split(",")[0].strip() if hosts else ""
    if _is_missing(first_host):
        pytest.skip("AUTOBYTEUS_LLM_SERVER_HOSTS not set in .env.test; skipping.")
    return first_host


def _normalize_value(value: str | None) -> str:
    if not value:
        return ""
    return value.strip().strip('"').strip("'")


def _get_image_model_id() -> str:
    return _normalize_value(_require_env("DEFAULT_IMAGE_GENERATION_MODEL"))


def _get_audio_model_id() -> str:
    return _normalize_value(_require_env("DEFAULT_SPEECH_GENERATION_MODEL"))


def _get_grounding_model_id() -> str:
    configured = _normalize_value(os.getenv("DEFAULT_GROUNDING_MODEL"))
    if configured:
        return configured

    manual = _normalize_value(os.getenv("LMSTUDIO_MODEL_ID"))
    if manual:
        return manual

    target_visual_model = "qwen/qwen3-vl-30b"

    LLMFactory.reinitialize()
    models = LLMFactory.list_models_by_runtime(LLMRuntime.LMSTUDIO)
    if not models:
        pytest.skip("No LM Studio models found for grounding test.")

    visual_model = next(
        (m for m in models if target_visual_model in m.model_identifier.lower()),
        None,
    )
    if not visual_model:
        pytest.skip(
            "LM Studio model matching 'qwen/qwen3-vl-30b' not found. "
            "Set DEFAULT_GROUNDING_MODEL to a valid visual grounding model identifier."
        )
    return visual_model.model_identifier


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
    _require_env("AUTOBYTEUS_API_KEY")
    _get_autobyteus_host()
    _get_image_model_id()
    _get_audio_model_id()


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


@pytest.mark.anyio
async def test_find_target_coordinates_lmstudio(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOBYTEUS_AGENT_WORKSPACE", str(tmp_path))

    grounding_model_id = _get_grounding_model_id()
    server = create_server()

    async def run_client(session: ClientSession) -> None:
        image_path = tmp_path / "grounding_test.png"
        image = Image.new("RGB", (640, 360), color="white")
        draw = ImageDraw.Draw(image)
        draw.rectangle((220, 130, 420, 230), fill="red")
        draw.text((250, 160), "TARGET", fill="white")
        image.save(image_path)

        result = await session.call_tool(
            "find_target_coordinates_vlm",
            {
                "image": str(image_path),
                "intent": "Find the center of the red TARGET box.",
                "model_identifier": grounding_model_id,
            },
        )

        assert not result.isError
        structured = result.structuredContent
        assert structured is not None
        assert structured["model"] == grounding_model_id

        normalized = structured.get("normalized_coordinates")
        if normalized is None:
            pytest.skip("Model returned no coordinates for synthetic grounding image.")
        assert 0.0 <= float(normalized["x"]) <= 1.0
        assert 0.0 <= float(normalized["y"]) <= 1.0

    await _run_with_session(server, run_client)
