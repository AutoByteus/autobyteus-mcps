from __future__ import annotations

import anyio
from pathlib import Path

import pytest
from PIL import Image

from mcp.client.session import ClientSession
from mcp.shared.message import SessionMessage

import image_audio_mcp.services as services_module
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


@pytest.mark.anyio
async def test_list_image_models_local(monkeypatch):
    monkeypatch.setattr(services_module.ImageClientFactory, "ensure_initialized", lambda: None)
    monkeypatch.setattr(services_module, "ImageModel", [_DummyImageModel()])

    server = create_server()

    async def run_client(session: ClientSession) -> None:
        result = await session.call_tool("list_image_models", {})
        assert not result.isError
        structured = result.structuredContent
        assert structured is not None
        assert structured["models"][0]["model_identifier"] == "dummy-image"

    await _run_with_session(server, run_client)


@pytest.mark.anyio
async def test_tool_list_excludes_hidden_grounding_tools():
    server = create_server()

    async def run_client(session: ClientSession) -> None:
        tools = await session.list_tools()
        tool_names = {tool.name for tool in tools.tools}
        assert tool_names == {
            "health_check",
            "list_audio_models",
            "list_image_models",
            "generate_image",
            "edit_image",
            "generate_speech",
            "find_target_coordinates",
        }
        assert "find_target_coordinates_vlm" not in tool_names
        assert "list_visual_grounding_models" not in tool_names

    await _run_with_session(server, run_client)


@pytest.mark.anyio
async def test_generate_speech_tool_schema_includes_prompt_description():
    server = create_server()

    async def run_client(session: ClientSession) -> None:
        tools = await session.list_tools()
        generate_speech_tool = next(tool for tool in tools.tools if tool.name == "generate_speech")
        prompt_schema = generate_speech_tool.inputSchema["properties"]["prompt"]
        generation_config_schema = generate_speech_tool.inputSchema["properties"]["generation_config"]

        assert "description" in prompt_schema
        assert "[amused]" in prompt_schema["description"]
        assert "speaker_mapping" in prompt_schema["description"]
        assert "up to 2 distinct speakers" in prompt_schema["description"]
        assert "description" in generation_config_schema
        assert "Please call `list_audio_models` first" in generation_config_schema["description"]
        assert "generation_config" in generation_config_schema["description"]

    await _run_with_session(server, run_client)


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


def test_extract_normalized_coordinates_normalized_output():
    x, y, confidence, reason, coordinate_mode = services_module._extract_normalized_coordinates(
        {"x": 0.25, "y": 0.5, "confidence": 0.92, "reason": "The login button center."},
        image_size=(100, 200),
    )

    assert x == 0.25
    assert y == 0.5
    assert confidence == 0.92
    assert reason == "The login button center."
    assert coordinate_mode == "normalized_0_1"


@pytest.mark.anyio
async def test_find_target_coordinates_via_edit_marker_local(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("AUTOBYTEUS_AGENT_WORKSPACE", str(tmp_path))
    monkeypatch.setattr(
        services_module.ImageClientFactory,
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

    monkeypatch.setattr(services_module, "download_file_from_url", _fake_download)

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


def test_extract_normalized_coordinates_pixel_output():
    x, y, confidence, reason, coordinate_mode = services_module._extract_normalized_coordinates(
        {"x": 25, "y": 100, "confidence": 0.91, "reason": "Absolute pixel point."},
        image_size=(100, 200),
    )

    assert x == 0.25
    assert y == 0.5
    assert confidence == 0.91
    assert reason == "Absolute pixel point."
    assert coordinate_mode == "pixel_absolute"


def test_extract_normalized_coordinates_qwen_relative_output():
    x, y, confidence, reason, coordinate_mode = services_module._extract_normalized_coordinates(
        {"x": 250, "y": 500, "confidence": 0.9, "reason": "Relative 0..1000 point."},
        image_size=(100, 200),
    )

    assert x == 0.25
    assert y == 0.5
    assert confidence == 0.9
    assert reason == "Relative 0..1000 point."
    assert coordinate_mode == "relative_0_1000"
