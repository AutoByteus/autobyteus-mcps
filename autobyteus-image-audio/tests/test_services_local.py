from __future__ import annotations

from pathlib import Path

import pytest

import image_audio_mcp.services as services


@pytest.fixture
def anyio_backend():
    return "asyncio"


class _ImageResponse:
    def __init__(self, urls, revised_prompt=None):
        self.image_urls = urls
        self.revised_prompt = revised_prompt


class _AudioResponse:
    def __init__(self, urls):
        self.audio_urls = urls


class _GenerateImageClient:
    def __init__(self):
        self.cleaned = False
        self.calls = []

    async def generate_image(self, prompt, input_image_urls, generation_config):
        self.calls.append((prompt, input_image_urls, generation_config))
        return _ImageResponse(["https://example.invalid/generated.png"], revised_prompt="revised")

    async def cleanup(self):
        self.cleaned = True


class _EditImageClient:
    def __init__(self):
        self.cleaned = False
        self.calls = []

    async def edit_image(self, prompt, input_image_urls, mask_url, generation_config):
        self.calls.append((prompt, input_image_urls, mask_url, generation_config))
        return _ImageResponse(["https://example.invalid/edited.png"])

    async def cleanup(self):
        self.cleaned = True


class _SpeechClient:
    def __init__(self):
        self.cleaned = False
        self.calls = []

    async def generate_speech(self, prompt, generation_config):
        self.calls.append((prompt, generation_config))
        return _AudioResponse(["https://example.invalid/speech.wav"])

    async def cleanup(self):
        self.cleaned = True


@pytest.mark.anyio
async def test_generate_image_uses_safe_paths_downloads_and_cleans_up(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("AUTOBYTEUS_AGENT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("DEFAULT_IMAGE_GENERATION_MODEL", "test-image-model")
    input_image = tmp_path / "input.png"
    input_image.write_bytes(b"input")
    output_path = tmp_path / "generated.png"
    client = _GenerateImageClient()

    async def fake_download(url, destination):
        assert url == "https://example.invalid/generated.png"
        Path(destination).write_bytes(b"generated")

    monkeypatch.setattr(services.ImageClientFactory, "create_image_client", lambda model_id: client)
    monkeypatch.setattr(services, "download_file_from_url", fake_download)

    result = await services.generate_image(
        prompt="make image",
        output_file_path="generated.png",
        input_images=["input.png"],
        generation_config={"size": "1024x1024"},
    )

    assert result == {"file_path": str(output_path), "model": "test-image-model", "revised_prompt": "revised"}
    assert output_path.read_bytes() == b"generated"
    assert client.cleaned is True
    assert client.calls == [("make image", [str(input_image)], {"size": "1024x1024"})]


@pytest.mark.anyio
async def test_edit_image_uses_safe_inputs_mask_downloads_and_cleans_up(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("AUTOBYTEUS_AGENT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("DEFAULT_IMAGE_EDIT_MODEL", "test-edit-model")
    input_image = tmp_path / "input.png"
    mask_image = tmp_path / "mask.png"
    output_path = tmp_path / "edited.png"
    input_image.write_bytes(b"input")
    mask_image.write_bytes(b"mask")
    client = _EditImageClient()

    async def fake_download(url, destination):
        assert url == "https://example.invalid/edited.png"
        Path(destination).write_bytes(b"edited")

    monkeypatch.setattr(services.ImageClientFactory, "create_image_client", lambda model_id: client)
    monkeypatch.setattr(services, "download_file_from_url", fake_download)

    result = await services.edit_image(
        prompt="edit image",
        output_file_path="edited.png",
        input_images=["input.png"],
        mask_image="mask.png",
        generation_config={"quality": "high"},
    )

    assert result == {"file_path": str(output_path), "model": "test-edit-model"}
    assert output_path.read_bytes() == b"edited"
    assert client.cleaned is True
    assert client.calls == [("edit image", [str(input_image)], str(mask_image), {"quality": "high"})]


@pytest.mark.anyio
async def test_generate_speech_downloads_and_cleans_up(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("AUTOBYTEUS_AGENT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("DEFAULT_SPEECH_GENERATION_MODEL", "test-speech-model")
    output_path = tmp_path / "speech.wav"
    client = _SpeechClient()

    async def fake_download(url, destination):
        assert url == "https://example.invalid/speech.wav"
        Path(destination).write_bytes(b"speech")

    monkeypatch.setattr(services.AudioClientFactory, "create_audio_client", lambda model_id: client)
    monkeypatch.setattr(services, "download_file_from_url", fake_download)

    result = await services.generate_speech(
        prompt="hello",
        output_file_path="speech.wav",
        generation_config={"voice": "Kore"},
    )

    assert result == {"file_path": str(output_path), "model": "test-speech-model"}
    assert output_path.read_bytes() == b"speech"
    assert client.cleaned is True
    assert client.calls == [("hello", {"voice": "Kore"})]
