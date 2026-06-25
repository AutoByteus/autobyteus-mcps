from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from image_audio_mcp import services


class CliUsageError(Exception):
    """Raised when command-line arguments are syntactically valid shell args but invalid CLI input."""


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # pragma: no cover - exercised through parse_args callers
        raise CliUsageError(message)


def _json_dump(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))


def _emit_success(command: str, result: dict[str, Any]) -> None:
    _json_dump({"ok": True, "command": command, "result": result})


def _emit_failure(command: str, error_type: str, error_message: str) -> None:
    _json_dump({"ok": False, "command": command, "error_type": error_type, "error_message": error_message})
    print(f"{error_type}: {error_message}", file=sys.stderr)


def _requested_command(argv: Sequence[str] | None) -> str:
    args = list(sys.argv[1:] if argv is None else argv)
    for item in args:
        if item.startswith("-"):
            continue
        return item
    return "autobyteus-image-audio"


def _merge_config_object(config: dict[str, Any], incoming: dict[str, Any], source_label: str, prefix: str = "") -> None:
    for key, value in incoming.items():
        if not isinstance(key, str) or not key:
            dotted_key = f"{prefix}.{key}" if prefix else str(key)
            raise CliUsageError(f"{source_label} contains an invalid generation_config key: {dotted_key!r}")

        dotted_key = f"{prefix}.{key}" if prefix else key
        if key not in config:
            config[key] = value
            continue

        existing = config[key]
        if isinstance(existing, dict) and isinstance(value, dict):
            _merge_config_object(existing, value, source_label, dotted_key)
            continue

        raise CliUsageError(f"{source_label} conflicts with existing generation_config key {dotted_key!r}.")


def _parse_generation_config_json(raw: str, source_label: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CliUsageError(f"{source_label} must be valid JSON: {exc.msg} at line {exc.lineno} column {exc.colno}.") from exc

    if not isinstance(parsed, dict):
        raise CliUsageError(f"{source_label} must be a JSON object for generation_config.")
    return parsed


def _load_generation_config_file(path: str) -> dict[str, Any]:
    try:
        raw = Path(path).expanduser().read_text(encoding="utf-8")
    except OSError as exc:
        raise CliUsageError(f"--generation-config-file could not be read: {path!r}: {exc}") from exc
    return _parse_generation_config_json(raw, f"--generation-config-file {path!r}")


def _load_generation_config(args: argparse.Namespace) -> dict[str, Any] | None:
    config: dict[str, Any] = {}

    generation_config_file = getattr(args, "generation_config_file", None)
    if generation_config_file is not None:
        _merge_config_object(
            config,
            _load_generation_config_file(generation_config_file),
            "--generation-config-file",
        )

    generation_config_json = getattr(args, "generation_config", None)
    if generation_config_json is not None:
        _merge_config_object(
            config,
            _parse_generation_config_json(generation_config_json, "--generation-config"),
            "--generation-config",
        )

    return config or None


async def _dispatch(args: argparse.Namespace) -> dict[str, Any]:
    command = args.command
    if command == "health-check":
        return await services.health_check()
    if command == "list-image-models":
        return await services.list_image_models()
    if command == "list-audio-models":
        return await services.list_audio_models()
    if command == "list-video-models":
        return await services.list_video_models()
    if command == "generate-image":
        return await services.generate_image(args.prompt, args.output_file_path, args.input_images, _load_generation_config(args))
    if command == "generate-video":
        return await services.generate_video(
            args.prompt,
            args.output_file_path,
            args.input_images,
            args.input_audios,
            args.input_videos,
            _load_generation_config(args),
        )
    if command == "edit-image":
        return await services.edit_image(
            args.prompt, args.output_file_path, args.input_images, args.mask_image, _load_generation_config(args)
        )
    if command == "generate-speech":
        return await services.generate_speech(args.prompt, args.output_file_path, _load_generation_config(args))
    if command == "find-target-coordinates":
        return await services.find_target_coordinates(
            args.image, args.target, args.marked_image_output_path, args.grounding_model_identifier
        )
    raise CliUsageError(f"Unknown command: {command}")


def _add_generation_config_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--generation-config",
        metavar="JSON_OBJECT",
        help=(
            "Full MCP-style generation_config JSON object. This preserves nested config shape, "
            'e.g. --generation-config \'{"voice":"alloy","audio_config":{"format":"mp3"}}\'.'
        ),
    )
    parser.add_argument(
        "--generation-config-file",
        metavar="PATH",
        help="Path to a JSON file containing a generation_config object. Useful for larger nested configs.",
    )


def _add_output_path_option(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--output-file-path",
        required=True,
        help=(
            "Required output path for generated media. Relative paths resolve under "
            "AUTOBYTEUS_AGENT_WORKSPACE when set, otherwise the current working directory."
        ),
    )


def _add_input_image_option(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--input-image",
        dest="input_images",
        action="append",
        help=(
            "Reference/input image. Repeat this flag for multiple images. Values may be URLs, "
            "data URIs, or safe local paths."
        ),
    )


def _add_input_audio_option(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--input-audio",
        dest="input_audios",
        action="append",
        help=(
            "Reference/input audio. Repeat this flag for multiple audio files. Values may be URLs, "
            "data URIs, or safe local paths."
        ),
    )


def _add_input_video_option(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--input-video",
        dest="input_videos",
        action="append",
        help=(
            "Reference/input video. Repeat this flag for multiple videos. Values may be URLs, "
            "data URIs, or safe local paths."
        ),
    )


def _command_parser(
    subparsers: argparse._SubParsersAction,
    name: str,
    help_text: str,
    description: str,
    example: str,
) -> argparse.ArgumentParser:
    return subparsers.add_parser(
        name,
        help=help_text,
        description=description,
        epilog=f"Example:\n  {example}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = JsonArgumentParser(
        prog="autobyteus-image-audio",
        description=(
            "Task-oriented CLI for Autobyteus image/audio/video capabilities. Output is JSON by default.\n"
            "The repo-level cli/autobyteus-image-audio wrapper runs this command through uv and "
            "auto-prepares the project runtime; callers do not need to run uv sync or activate .venv."
        ),
        epilog=(
            "Environment and path notes:\n"
            "  AUTOBYTEUS_AGENT_WORKSPACE constrains relative file paths. Without it, paths resolve from cwd.\n"
            "  DEFAULT_IMAGE_GENERATION_MODEL, DEFAULT_IMAGE_EDIT_MODEL, DEFAULT_SPEECH_GENERATION_MODEL,\n"
            "  DEFAULT_VIDEO_GENERATION_MODEL, and DEFAULT_GROUNDING_MODEL select the configured default models.\n"
            "  Provider credentials such as OPENAI_API_KEY, GEMINI_API_KEY, or Vertex AI env vars may be required.\n\n"
            "Examples:\n"
            "  autobyteus-image-audio health-check\n"
            "  autobyteus-image-audio generate-image --prompt 'A calm lake' --output-file-path lake.png\n"
            "  autobyteus-image-audio generate-video --prompt 'A calm lake at sunrise' --output-file-path lake.mp4\n"
            "  autobyteus-image-audio find-target-coordinates --image screen.png --target 'Submit button'"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True, parser_class=JsonArgumentParser)

    _command_parser(subparsers, "health-check", "Return status and default models.", "Return status and configured default models.", "autobyteus-image-audio health-check")
    _command_parser(subparsers, "list-image-models", "List image models and schemas.", "List image models, providers, schemas, and default configs.", "autobyteus-image-audio list-image-models")
    _command_parser(subparsers, "list-audio-models", "List audio models and schemas.", "List audio/TTS models, providers, schemas, and default configs.", "autobyteus-image-audio list-audio-models")
    _command_parser(subparsers, "list-video-models", "List video models and schemas.", "List video models, providers, schemas, and default configs.", "autobyteus-image-audio list-video-models")

    generate_image = _command_parser(
        subparsers, "generate-image", "Generate an image from a prompt.", "Generate an image, optionally with reference images.", "autobyteus-image-audio generate-image --prompt 'A lake' --output-file-path lake.png"
    )
    generate_image.add_argument("--prompt", required=True, help="Text prompt for image generation.")
    _add_output_path_option(generate_image)
    _add_input_image_option(generate_image)
    _add_generation_config_options(generate_image)

    generate_video = _command_parser(
        subparsers,
        "generate-video",
        "Generate a video from a prompt.",
        "Generate a video, optionally with image, audio, or video references.",
        "autobyteus-image-audio generate-video --prompt 'A lake at sunrise' --output-file-path lake.mp4",
    )
    generate_video.add_argument("--prompt", required=True, help="Text prompt for video generation.")
    _add_output_path_option(generate_video)
    _add_input_image_option(generate_video)
    _add_input_audio_option(generate_video)
    _add_input_video_option(generate_video)
    _add_generation_config_options(generate_video)

    edit_image = _command_parser(
        subparsers, "edit-image", "Edit existing image(s).", "Edit images with an optional mask image.", "autobyteus-image-audio edit-image --prompt 'Replace sky' --input-image photo.png --output-file-path out.png"
    )
    edit_image.add_argument("--prompt", required=True, help="Instruction for the image edit.")
    _add_output_path_option(edit_image)
    _add_input_image_option(edit_image)
    edit_image.add_argument("--mask-image", help="Optional mask image URL, data URI, or safe local path.")
    _add_generation_config_options(edit_image)

    generate_speech = _command_parser(
        subparsers, "generate-speech", "Generate spoken audio from text.", "Generate spoken audio from text.", "autobyteus-image-audio generate-speech --prompt 'Hello' --output-file-path hello.wav"
    )
    generate_speech.add_argument("--prompt", required=True, help="Text to speak.")
    _add_output_path_option(generate_speech)
    _add_generation_config_options(generate_speech)

    coordinates = _command_parser(
        subparsers, "find-target-coordinates", "Find target UI coordinates.", "Find target coordinates with the edit-marker pipeline.", "autobyteus-image-audio find-target-coordinates --image screen.png --target 'Submit'"
    )
    coordinates.add_argument("--image", required=True, help="Screenshot/image URL, data URI, or safe local path.")
    coordinates.add_argument("--target", required=True, help="Visible target text or UI element description.")
    coordinates.add_argument("--marked-image-output-path", help="Optional path to save the marker image for inspection.")
    coordinates.add_argument("--grounding-model-identifier", help="Optional fallback grounding model identifier.")

    return parser


def run(argv: Sequence[str] | None = None) -> int:
    command = _requested_command(argv)
    try:
        parser = build_parser()
        args = parser.parse_args(argv)
        command = args.command
        result = asyncio.run(_dispatch(args))
    except CliUsageError as exc:
        _emit_failure(command, "UsageError", str(exc))
        return 2
    except Exception as exc:
        _emit_failure(command, type(exc).__name__, str(exc))
        return 1

    _emit_success(command, result)
    return 0


def main(argv: Sequence[str] | None = None) -> None:
    raise SystemExit(run(argv))


if __name__ == "__main__":
    main()
