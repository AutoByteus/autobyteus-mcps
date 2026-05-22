from __future__ import annotations

import argparse
import asyncio
import json
import sys
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


def _parse_config_value(raw: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def _merge_config_value(config: dict[str, Any], dotted_key: str, value: Any) -> None:
    key_parts = dotted_key.split(".")
    if not dotted_key or any(not part for part in key_parts):
        raise CliUsageError(f"--config key must be non-empty dot notation: {dotted_key!r}")

    cursor = config
    for part in key_parts[:-1]:
        existing = cursor.setdefault(part, {})
        if not isinstance(existing, dict):
            raise CliUsageError(f"--config {dotted_key} conflicts with non-object key {part!r}.")
        cursor = existing

    final_key = key_parts[-1]
    if final_key in cursor:
        raise CliUsageError(f"--config {dotted_key} was provided more than once or conflicts with nested config.")
    cursor[final_key] = value


def _parse_config_item(item: str) -> tuple[str, Any]:
    if "=" not in item:
        raise CliUsageError(f"--config entries must use key=value syntax: {item!r}")
    key, raw_value = item.split("=", 1)
    if not key:
        raise CliUsageError("--config key must not be empty.")
    return key, _parse_config_value(raw_value)


def _load_generation_config(args: argparse.Namespace) -> dict[str, Any] | None:
    config: dict[str, Any] = {}
    for item in getattr(args, "config", None) or []:
        key, value = _parse_config_item(item)
        _merge_config_value(config, key, value)

    speakers = getattr(args, "speakers", None) or []
    voices = getattr(args, "voices", None) or []
    if len(speakers) != len(voices):
        raise CliUsageError(
            f"--speaker and --voice must be provided in matching counts; got {len(speakers)} speaker(s) and {len(voices)} voice(s)."
        )
    if speakers:
        if "speaker_mapping" in config:
            raise CliUsageError("Use either --speaker/--voice pairs or --config speaker_mapping..., not both.")
        config["speaker_mapping"] = dict(zip(speakers, voices))

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
        "--config",
        action="append",
        metavar="KEY=VALUE",
        help=(
            "Model-specific generation_config setting. Repeat for multiple settings. "
            "Use dot notation for nested keys, e.g. --config image_config.aspect_ratio=16:9. "
            "Values parse as JSON scalars/arrays/objects when valid; otherwise they remain strings."
        ),
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
    generate_speech.add_argument("--speaker", dest="speakers", action="append", help="Speaker label for multi-speaker TTS. Pair by order with --voice.")
    generate_speech.add_argument("--voice", dest="voices", action="append", help="Voice name for multi-speaker TTS. Pair by order with --speaker.")

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
