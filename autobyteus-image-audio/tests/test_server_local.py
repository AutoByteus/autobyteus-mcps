from __future__ import annotations

import anyio
from pathlib import Path

import pytest
from PIL import Image

from mcp.client.session import ClientSession
from mcp.shared.message import SessionMessage

import image_audio_mcp.server as server_module
from image_audio_mcp.server import create_server


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


class _DummySchema:
    def to_json_schema_dict(self):
        return {"type": "object", "properties": {}}


class _DummyConfig:
    def to_dict(self):
        return {"n": 1}


class _DummyImageModel:
    model_identifier = "dummy-image"
    name = "dummy-image"
    value = "dummy-image"

    class _Provider:
        value = "OPENAI"

    class _Runtime:
        value = "api"

    provider = _Provider()
    runtime = _Runtime()
    parameter_schema = _DummySchema()
    default_config = _DummyConfig()


class _DummyVisionModel:
    model_identifier = "dummy-vision"
    name = "dummy-vision"
    value = "dummy-vision"
    canonical_name = "dummy-vision"

    class _Provider:
        value = "OPENAI"

    class _Runtime:
        value = "api"

    provider = _Provider()
    runtime = _Runtime()
    config_schema = _DummySchema()
    default_config = _DummyConfig()


@pytest.mark.anyio
async def test_list_image_models_local(monkeypatch):
    monkeypatch.setattr(server_module.ImageClientFactory, "ensure_initialized", lambda: None)
    monkeypatch.setattr(server_module, "ImageModel", [_DummyImageModel()])

    server = create_server()

    async def run_client(session: ClientSession) -> None:
        result = await session.call_tool("list_image_models", {})
        assert not result.isError
        structured = result.structuredContent
        assert structured is not None
        assert structured["models"][0]["model_identifier"] == "dummy-image"

    await _run_with_session(server, run_client)


@pytest.mark.anyio
async def test_list_visual_grounding_models_local(monkeypatch):
    monkeypatch.setattr(server_module.LLMFactory, "ensure_initialized", lambda: None)
    monkeypatch.setattr(server_module, "LLMModel", [_DummyVisionModel()])

    server = create_server()

    async def run_client(session: ClientSession) -> None:
        result = await session.call_tool("list_visual_grounding_models", {})
        assert not result.isError
        structured = result.structuredContent
        assert structured is not None
        assert structured["models"][0]["model_identifier"] == "dummy-vision"

    await _run_with_session(server, run_client)


class _DummyResponse:
    def __init__(self, content: str):
        self.content = content


class _DummyLLM:
    def configure_system_prompt(self, _prompt: str):
        return None

    async def send_user_message(self, user_message):
        assert user_message.image_urls
        return _DummyResponse(
            '{"x": 0.25, "y": 0.5, "confidence": 0.92, "reason": "The login button center."}'
        )

    async def cleanup(self):
        return None


class _DummyLLMPixelCoords:
    def configure_system_prompt(self, _prompt: str):
        return None

    async def send_user_message(self, user_message):
        assert user_message.image_urls
        return _DummyResponse(
            '{"x": 25, "y": 100, "confidence": 0.91, "reason": "Absolute pixel point."}'
        )

    async def cleanup(self):
        return None


class _DummyLLMQwenRelative:
    def configure_system_prompt(self, _prompt: str):
        return None

    async def send_user_message(self, user_message):
        assert user_message.image_urls
        return _DummyResponse(
            '{"x": 250, "y": 500, "confidence": 0.9, "reason": "Relative 0..1000 point."}'
        )

    async def cleanup(self):
        return None


class _DummyImageEditResponse:
    def __init__(self, image_urls):
        self.image_urls = image_urls


class _DummyImageClient:
    async def edit_image(self, prompt, input_image_urls, mask_url, generation_config):
        assert "magenta crosshair" in prompt
        assert "Look very, very carefully at the exact target sentence/label" in prompt
        assert "mark only the exact requested one" in prompt
        assert "Never choose the nearest neighbor or a semantically similar alternative." in prompt
        assert input_image_urls
        return _DummyImageEditResponse(["https://example.invalid/edited.png"])

    async def cleanup(self):
        return None


@pytest.mark.anyio
async def test_find_target_coordinates_vlm_local(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("AUTOBYTEUS_AGENT_WORKSPACE", str(tmp_path))
    monkeypatch.setattr(server_module.LLMFactory, "create_llm", lambda _model_id, _cfg=None: _DummyLLM())

    image_path = tmp_path / "screen.png"
    Image.new("RGB", (100, 200), color="white").save(image_path)

    server = create_server()

    async def run_client(session: ClientSession) -> None:
        result = await session.call_tool(
            "find_target_coordinates_vlm",
            {
                "image": str(image_path),
                "intent": "Click the Login button",
                "model_identifier": "gpt-5.2",
            },
        )
        assert not result.isError
        structured = result.structuredContent
        assert structured is not None

        assert structured["normalized_coordinates"] == {"x": 0.25, "y": 0.5}
        assert structured["pixel_coordinates"] == {"x": 25, "y": 100}
        assert structured["image_size"] == {"width": 100, "height": 200}
        assert structured["confidence"] == 0.92
        assert structured["coordinate_mode"] == "normalized_0_1"

    await _run_with_session(server, run_client)


@pytest.mark.anyio
async def test_find_target_coordinates_via_edit_marker_local(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("AUTOBYTEUS_AGENT_WORKSPACE", str(tmp_path))
    monkeypatch.setattr(
        server_module.ImageClientFactory,
        "create_image_client",
        lambda _model_id, _cfg=None: _DummyImageClient(),
    )

    original = tmp_path / "orig.png"
    edited_fixture = tmp_path / "edited_fixture.png"
    marked_output = tmp_path / "marked_out.png"

    # Original image (larger)
    Image.new("RGB", (200, 100), color="white").save(original)
    # Edited image (smaller) with magenta dot around (30,20)
    edited = Image.new("RGB", (100, 50), color="white")
    for x in range(26, 35):
        for y in range(16, 25):
            edited.putpixel((x, y), (255, 0, 255))
    edited.save(edited_fixture)

    async def _fake_download(_url, destination):
        Path(destination).write_bytes(edited_fixture.read_bytes())

    monkeypatch.setattr(server_module, "download_file_from_url", _fake_download)

    server = create_server()

    async def run_client(session: ClientSession) -> None:
        result = await session.call_tool(
            "find_target_coordinates",
            {
                "image": str(original),
                "target": "repository_prisma",
                "marked_image_output_path": str(marked_output),
            },
        )
        assert not result.isError
        structured = result.structuredContent
        assert structured is not None

        assert structured["strategy"] == "edit_marker"
        assert structured["detection_method"] in {"color_magenta", "llm_fallback"}
        assert structured["marked_image_size"] == {"width": 100, "height": 50}
        assert structured["original_image_size"] == {"width": 200, "height": 100}

        px = structured["pixel_coordinates"]["x"]
        py = structured["pixel_coordinates"]["y"]
        # Expected around (60,40) after scaling by 2x from edited to original.
        assert 55 <= px <= 65
        assert 35 <= py <= 45

    await _run_with_session(server, run_client)


@pytest.mark.anyio
async def test_find_target_coordinates_pixel_output_local(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("AUTOBYTEUS_AGENT_WORKSPACE", str(tmp_path))
    monkeypatch.setattr(
        server_module.LLMFactory, "create_llm", lambda _model_id, _cfg=None: _DummyLLMPixelCoords()
    )

    image_path = tmp_path / "screen.png"
    Image.new("RGB", (100, 200), color="white").save(image_path)

    server = create_server()

    async def run_client(session: ClientSession) -> None:
        result = await session.call_tool(
            "find_target_coordinates_vlm",
            {
                "image": str(image_path),
                "intent": "Click the Login button",
                "model_identifier": "qwen/qwen3-vl-30b:lmstudio@localhost:1234",
            },
        )
        assert not result.isError
        structured = result.structuredContent
        assert structured is not None

        assert structured["normalized_coordinates"] == {"x": 0.25, "y": 0.5}
        assert structured["pixel_coordinates"] == {"x": 25, "y": 100}
        assert structured["coordinate_mode"] == "pixel_absolute"

    await _run_with_session(server, run_client)


@pytest.mark.anyio
async def test_find_target_coordinates_qwen_relative_output_local(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("AUTOBYTEUS_AGENT_WORKSPACE", str(tmp_path))
    monkeypatch.setattr(
        server_module.LLMFactory,
        "create_llm",
        lambda _model_id, _cfg=None: _DummyLLMQwenRelative(),
    )

    image_path = tmp_path / "screen.png"
    Image.new("RGB", (100, 200), color="white").save(image_path)

    server = create_server()

    async def run_client(session: ClientSession) -> None:
        result = await session.call_tool(
            "find_target_coordinates_vlm",
            {
                "image": str(image_path),
                "intent": "Click the Login button",
                "model_identifier": "qwen/qwen3-vl-30b:lmstudio@localhost:1234",
            },
        )
        assert not result.isError
        structured = result.structuredContent
        assert structured is not None

        assert structured["normalized_coordinates"] == {"x": 0.25, "y": 0.5}
        assert structured["pixel_coordinates"] == {"x": 25, "y": 100}
        assert structured["coordinate_mode"] == "relative_0_1000"

    await _run_with_session(server, run_client)
