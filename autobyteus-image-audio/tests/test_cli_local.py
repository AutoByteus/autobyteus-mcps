from __future__ import annotations

import json
import argparse

import image_audio_mcp.cli as cli


def _stdout_payload(capsys):
    captured = capsys.readouterr()
    return json.loads(captured.out), captured.err


def test_generate_image_cli_parses_repeatable_input_images_and_config(monkeypatch, capsys):
    seen = {}

    async def fake_generate_image(prompt, output_file_path, input_images, generation_config):
        seen.update(
            prompt=prompt,
            output_file_path=output_file_path,
            input_images=input_images,
            generation_config=generation_config,
        )
        return {"file_path": "/tmp/out.png", "model": "image-model", "revised_prompt": None}

    monkeypatch.setattr(cli.services, "generate_image", fake_generate_image)

    code = cli.run(
        [
            "generate-image",
            "--prompt",
            "make image",
            "--input-image",
            "a.png",
            "--input-image",
            "b.png",
            "--config",
            "size=1024x1024",
            "--config",
            "steps=4",
            "--config",
            "safety=false",
            "--config",
            "image_config.aspect_ratio=16:9",
            "--output-file-path",
            "out.png",
        ]
    )

    payload, stderr = _stdout_payload(capsys)
    assert code == 0
    assert stderr == ""
    assert payload == {
        "ok": True,
        "command": "generate-image",
        "result": {"file_path": "/tmp/out.png", "model": "image-model", "revised_prompt": None},
    }
    assert seen == {
        "prompt": "make image",
        "output_file_path": "out.png",
        "input_images": ["a.png", "b.png"],
        "generation_config": {
            "size": "1024x1024",
            "steps": 4,
            "safety": False,
            "image_config": {"aspect_ratio": "16:9"},
        },
    }


def test_edit_image_cli_parses_mask_and_config(monkeypatch, capsys):
    seen = {}

    async def fake_edit_image(prompt, output_file_path, input_images, mask_image, generation_config):
        seen.update(
            prompt=prompt,
            output_file_path=output_file_path,
            input_images=input_images,
            mask_image=mask_image,
            generation_config=generation_config,
        )
        return {"file_path": "/tmp/edited.png", "model": "edit-model"}

    monkeypatch.setattr(cli.services, "edit_image", fake_edit_image)

    code = cli.run(
        [
            "edit-image",
            "--prompt",
            "edit image",
            "--input-image",
            "source.png",
            "--mask-image",
            "mask.png",
            "--config",
            "quality=high",
            "--output-file-path",
            "edited.png",
        ]
    )

    payload, stderr = _stdout_payload(capsys)
    assert code == 0
    assert stderr == ""
    assert payload["ok"] is True
    assert payload["command"] == "edit-image"
    assert payload["result"] == {"file_path": "/tmp/edited.png", "model": "edit-model"}
    assert seen == {
        "prompt": "edit image",
        "output_file_path": "edited.png",
        "input_images": ["source.png"],
        "mask_image": "mask.png",
        "generation_config": {"quality": "high"},
    }


def test_generate_speech_cli_prints_standard_json_envelope(monkeypatch, capsys):
    seen = {}

    async def fake_generate_speech(prompt, output_file_path, generation_config):
        seen.update(prompt=prompt, output_file_path=output_file_path, generation_config=generation_config)
        return {"file_path": "/tmp/speech.wav", "model": "speech-model"}

    monkeypatch.setattr(cli.services, "generate_speech", fake_generate_speech)

    code = cli.run(
        [
            "generate-speech",
            "--prompt",
            "Hello",
            "--config",
            "voice=Kore",
            "--output-file-path",
            "speech.wav",
        ]
    )

    payload, stderr = _stdout_payload(capsys)
    assert code == 0
    assert stderr == ""
    assert payload == {
        "ok": True,
        "command": "generate-speech",
        "result": {"file_path": "/tmp/speech.wav", "model": "speech-model"},
    }
    assert seen == {"prompt": "Hello", "output_file_path": "speech.wav", "generation_config": {"voice": "Kore"}}


def test_generate_speech_cli_builds_speaker_mapping_from_pairs(monkeypatch, capsys):
    seen = {}

    async def fake_generate_speech(prompt, output_file_path, generation_config):
        seen.update(prompt=prompt, output_file_path=output_file_path, generation_config=generation_config)
        return {"file_path": "/tmp/dialog.wav", "model": "speech-model"}

    monkeypatch.setattr(cli.services, "generate_speech", fake_generate_speech)

    code = cli.run(
        [
            "generate-speech",
            "--prompt",
            "Joe: Hi.\nJane: Hello.",
            "--config",
            "mode=multi-speaker",
            "--speaker",
            "Joe",
            "--voice",
            "Kore",
            "--speaker",
            "Jane",
            "--voice",
            "Puck",
            "--output-file-path",
            "dialog.wav",
        ]
    )

    payload, stderr = _stdout_payload(capsys)
    assert code == 0
    assert stderr == ""
    assert payload["ok"] is True
    assert list(seen["generation_config"]["speaker_mapping"].items()) == [("Joe", "Kore"), ("Jane", "Puck")]
    assert seen["generation_config"]["mode"] == "multi-speaker"


def test_find_target_coordinates_cli_maps_ergonomic_flags(monkeypatch, capsys):
    seen = {}

    async def fake_find_target_coordinates(image, target, marked_image_output_path, grounding_model_identifier):
        seen.update(
            image=image,
            target=target,
            marked_image_output_path=marked_image_output_path,
            grounding_model_identifier=grounding_model_identifier,
        )
        return {"pixel_coordinates": {"x": 10, "y": 20}, "normalized_coordinates": {"x": 0.1, "y": 0.2}}

    monkeypatch.setattr(cli.services, "find_target_coordinates", fake_find_target_coordinates)

    code = cli.run(
        [
            "find-target-coordinates",
            "--image",
            "screen.png",
            "--target",
            "Submit button",
            "--marked-image-output-path",
            "marked.png",
            "--grounding-model-identifier",
            "grounding-model",
        ]
    )

    payload, stderr = _stdout_payload(capsys)
    assert code == 0
    assert stderr == ""
    assert payload["ok"] is True
    assert payload["command"] == "find-target-coordinates"
    assert payload["result"]["pixel_coordinates"] == {"x": 10, "y": 20}
    assert seen == {
        "image": "screen.png",
        "target": "Submit button",
        "marked_image_output_path": "marked.png",
        "grounding_model_identifier": "grounding-model",
    }


def test_invalid_config_syntax_returns_usage_json(capsys):
    code = cli.run(["generate-image", "--prompt", "make image", "--config", "not-json", "--output-file-path", "out.png"])

    payload, stderr = _stdout_payload(capsys)
    assert code == 2
    assert payload["ok"] is False
    assert payload["command"] == "generate-image"
    assert payload["error_type"] == "UsageError"
    assert "key=value" in payload["error_message"]
    assert "UsageError" in stderr


def test_config_parent_child_conflict_returns_usage_json(capsys):
    code = cli.run(
        [
            "generate-image",
            "--prompt",
            "make image",
            "--config",
            "image_config=flat",
            "--config",
            "image_config.aspect_ratio=16:9",
            "--output-file-path",
            "out.png",
        ]
    )

    payload, _stderr = _stdout_payload(capsys)
    assert code == 2
    assert payload["error_type"] == "UsageError"
    assert "conflicts" in payload["error_message"]


def test_speaker_voice_mismatch_returns_usage_json(capsys):
    code = cli.run(
        ["generate-speech", "--prompt", "Joe: Hi.", "--speaker", "Joe", "--output-file-path", "speech.wav"]
    )

    payload, stderr = _stdout_payload(capsys)
    assert code == 2
    assert payload["error_type"] == "UsageError"
    assert "matching counts" in payload["error_message"]
    assert "UsageError" in stderr


def test_cli_help_is_task_oriented_and_config_first():
    parser = cli.build_parser()
    help_text = parser.format_help()
    subparsers = next(action for action in parser._actions if isinstance(action, argparse._SubParsersAction))
    speech_help = subparsers.choices["generate-speech"].format_help()
    assert "generate-image" in help_text
    assert "find-target-coordinates" in help_text
    assert "AUTOBYTEUS_AGENT_WORKSPACE" in help_text
    assert "--config" in speech_help
    assert "--speaker" in speech_help
    assert "--voice" in speech_help
    assert "call-tool" not in help_text
    assert "generation-config-json" not in help_text + speech_help
