from __future__ import annotations

import argparse
import json

import image_audio_mcp.cli as cli


def _stdout_payload(capsys):
    captured = capsys.readouterr()
    return json.loads(captured.out), captured.err


def test_generate_image_cli_accepts_mcp_style_generation_config_json(monkeypatch, capsys):
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
            "--generation-config",
            '{"size":"1024x1024","steps":4,"safety":false,"image_config":{"aspect_ratio":"16:9"}}',
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


def test_edit_image_cli_accepts_mcp_style_generation_config_json(monkeypatch, capsys):
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
            "--generation-config",
            '{"quality":"high"}',
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


def test_generate_video_cli_accepts_mcp_style_generation_config_json(monkeypatch, capsys):
    seen = {}

    async def fake_generate_video(
        prompt,
        output_file_path,
        input_images,
        input_audios,
        input_videos,
        generation_config,
    ):
        seen.update(
            prompt=prompt,
            output_file_path=output_file_path,
            input_images=input_images,
            input_audios=input_audios,
            input_videos=input_videos,
            generation_config=generation_config,
        )
        return {"file_path": "/tmp/out.mp4", "model": "video-model"}

    monkeypatch.setattr(cli.services, "generate_video", fake_generate_video)

    code = cli.run(
        [
            "generate-video",
            "--prompt",
            "make video",
            "--input-image",
            "frame.png",
            "--input-audio",
            "voice.wav",
            "--input-video",
            "clip.mp4",
            "--generation-config",
            '{"duration_seconds":10,"camera":{"motion":"slow_pan"}}',
            "--output-file-path",
            "out.mp4",
        ]
    )

    payload, stderr = _stdout_payload(capsys)
    assert code == 0
    assert stderr == ""
    assert payload == {
        "ok": True,
        "command": "generate-video",
        "result": {"file_path": "/tmp/out.mp4", "model": "video-model"},
    }
    assert seen == {
        "prompt": "make video",
        "output_file_path": "out.mp4",
        "input_images": ["frame.png"],
        "input_audios": ["voice.wav"],
        "input_videos": ["clip.mp4"],
        "generation_config": {"duration_seconds": 10, "camera": {"motion": "slow_pan"}},
    }


def test_list_video_models_cli_prints_standard_json_envelope(monkeypatch, capsys):
    async def fake_list_video_models():
        return {"models": [{"model_identifier": "video-model"}]}

    monkeypatch.setattr(cli.services, "list_video_models", fake_list_video_models)

    code = cli.run(["list-video-models"])

    payload, stderr = _stdout_payload(capsys)
    assert code == 0
    assert stderr == ""
    assert payload == {
        "ok": True,
        "command": "list-video-models",
        "result": {"models": [{"model_identifier": "video-model"}]},
    }


def test_generate_speech_cli_prints_standard_json_envelope_without_generation_config(monkeypatch, capsys):
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
    assert seen == {"prompt": "Hello", "output_file_path": "speech.wav", "generation_config": None}


def test_generate_speech_cli_accepts_mcp_style_generation_config_json(monkeypatch, capsys):
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
            "--generation-config",
            '{"mode":"multi-speaker","speaker_mapping":{"Joe":"Kore","Jane":"Puck"}}',
            "--output-file-path",
            "dialog.wav",
        ]
    )

    payload, stderr = _stdout_payload(capsys)
    assert code == 0
    assert stderr == ""
    assert payload["ok"] is True
    assert seen == {
        "prompt": "Joe: Hi.\nJane: Hello.",
        "output_file_path": "dialog.wav",
        "generation_config": {"mode": "multi-speaker", "speaker_mapping": {"Joe": "Kore", "Jane": "Puck"}},
    }


def test_generate_image_cli_accepts_generation_config_file_and_inline_config_merge(monkeypatch, capsys, tmp_path):
    seen = {}

    async def fake_generate_image(prompt, output_file_path, input_images, generation_config):
        seen.update(
            prompt=prompt,
            output_file_path=output_file_path,
            input_images=input_images,
            generation_config=generation_config,
        )
        return {"file_path": "/tmp/out.png", "model": "image-model", "revised_prompt": None}

    config_path = tmp_path / "generation_config.json"
    config_path.write_text('{"image_config":{"aspect_ratio":"16:9"},"quality":"high"}', encoding="utf-8")
    monkeypatch.setattr(cli.services, "generate_image", fake_generate_image)

    code = cli.run(
        [
            "generate-image",
            "--prompt",
            "make image",
            "--generation-config-file",
            str(config_path),
            "--generation-config",
            '{"image_config":{"seed":123}}',
            "--output-file-path",
            "out.png",
        ]
    )

    payload, stderr = _stdout_payload(capsys)
    assert code == 0
    assert stderr == ""
    assert payload["ok"] is True
    assert seen["generation_config"] == {
        "image_config": {"aspect_ratio": "16:9", "seed": 123},
        "quality": "high",
    }


def test_generation_config_json_conflict_returns_usage_json(capsys, tmp_path):
    config_path = tmp_path / "generation_config.json"
    config_path.write_text('{"image_config":{"aspect_ratio":"16:9"}}', encoding="utf-8")

    code = cli.run(
        [
            "generate-image",
            "--prompt",
            "make image",
            "--generation-config-file",
            str(config_path),
            "--generation-config",
            '{"image_config":{"aspect_ratio":"1:1"}}',
            "--output-file-path",
            "out.png",
        ]
    )

    payload, stderr = _stdout_payload(capsys)
    assert code == 2
    assert payload["ok"] is False
    assert payload["error_type"] == "UsageError"
    assert "conflicts" in payload["error_message"]
    assert "UsageError" in stderr


def test_invalid_generation_config_json_returns_usage_json(capsys):
    code = cli.run(
        [
            "generate-image",
            "--prompt",
            "make image",
            "--generation-config",
            '{"image_config":',
            "--output-file-path",
            "out.png",
        ]
    )

    payload, stderr = _stdout_payload(capsys)
    assert code == 2
    assert payload["ok"] is False
    assert payload["error_type"] == "UsageError"
    assert "valid JSON" in payload["error_message"]
    assert "UsageError" in stderr


def test_non_object_generation_config_json_returns_usage_json(capsys):
    code = cli.run(
        [
            "generate-image",
            "--prompt",
            "make image",
            "--generation-config",
            '["not","object"]',
            "--output-file-path",
            "out.png",
        ]
    )

    payload, stderr = _stdout_payload(capsys)
    assert code == 2
    assert payload["ok"] is False
    assert payload["error_type"] == "UsageError"
    assert "JSON object" in payload["error_message"]
    assert "UsageError" in stderr


def test_invalid_generation_config_file_returns_usage_json(capsys, tmp_path):
    config_path = tmp_path / "generation_config.json"
    config_path.write_text('{"image_config":', encoding="utf-8")

    code = cli.run(
        [
            "generate-image",
            "--prompt",
            "make image",
            "--generation-config-file",
            str(config_path),
            "--output-file-path",
            "out.png",
        ]
    )

    payload, stderr = _stdout_payload(capsys)
    assert code == 2
    assert payload["ok"] is False
    assert payload["error_type"] == "UsageError"
    assert "valid JSON" in payload["error_message"]
    assert "UsageError" in stderr


def test_generation_config_file_must_be_json_object(capsys, tmp_path):
    config_path = tmp_path / "generation_config.json"
    config_path.write_text('["not","object"]', encoding="utf-8")

    code = cli.run(
        [
            "generate-image",
            "--prompt",
            "make image",
            "--generation-config-file",
            str(config_path),
            "--output-file-path",
            "out.png",
        ]
    )

    payload, stderr = _stdout_payload(capsys)
    assert code == 2
    assert payload["ok"] is False
    assert payload["error_type"] == "UsageError"
    assert "JSON object" in payload["error_message"]
    assert "UsageError" in stderr


def test_generation_config_file_missing_returns_usage_json(capsys, tmp_path):
    missing_path = tmp_path / "missing.json"

    code = cli.run(
        [
            "generate-image",
            "--prompt",
            "make image",
            "--generation-config-file",
            str(missing_path),
            "--output-file-path",
            "out.png",
        ]
    )

    payload, stderr = _stdout_payload(capsys)
    assert code == 2
    assert payload["ok"] is False
    assert payload["error_type"] == "UsageError"
    assert "could not be read" in payload["error_message"]
    assert "UsageError" in stderr


def test_removed_config_flag_returns_usage_json(capsys):
    code = cli.run(["generate-image", "--prompt", "make image", "--config", "voice=Kore", "--output-file-path", "out.png"])

    payload, stderr = _stdout_payload(capsys)
    assert code == 2
    assert payload["error_type"] == "UsageError"
    assert "unrecognized arguments" in payload["error_message"]
    assert "--config" in payload["error_message"]
    assert "UsageError" in stderr


def test_removed_speaker_voice_flags_return_usage_json(capsys):
    code = cli.run(
        [
            "generate-speech",
            "--prompt",
            "Joe: Hi.",
            "--speaker",
            "Joe",
            "--voice",
            "Kore",
            "--output-file-path",
            "speech.wav",
        ]
    )

    payload, stderr = _stdout_payload(capsys)
    assert code == 2
    assert payload["error_type"] == "UsageError"
    assert "unrecognized arguments" in payload["error_message"]
    assert "--speaker" in payload["error_message"]
    assert "--voice" in payload["error_message"]
    assert "UsageError" in stderr


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


def test_cli_help_is_task_oriented_and_generation_config_native():
    parser = cli.build_parser()
    help_text = parser.format_help()
    subparsers = next(action for action in parser._actions if isinstance(action, argparse._SubParsersAction))
    speech_help = subparsers.choices["generate-speech"].format_help()
    assert "generate-image" in help_text
    assert "generate-video" in help_text
    assert "list-video-models" in help_text
    assert "find-target-coordinates" in help_text
    assert "AUTOBYTEUS_AGENT_WORKSPACE" in help_text
    assert "DEFAULT_VIDEO_GENERATION_MODEL" in help_text
    assert "--generation-config" in speech_help
    assert "--generation-config-file" in speech_help
    assert "--config" not in speech_help
    assert "--speaker" not in speech_help
    assert "--voice" not in speech_help
    assert "--api-key" not in speech_help
    assert "call-tool" not in help_text
