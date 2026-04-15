from __future__ import annotations

from pathlib import Path

from .backend_contracts import mlx_supports_flag
from .config import ConfigError, TtsSettings
from .routing_policy import (
    ResolvedMlxRequest,
    normalize_optional_text,
    resolve_chatterbox_language_code,
    resolve_xtts_language_code,
)
from .runtime_paths import resolve_runtime_script_path


def build_mlx_command(
    settings: TtsSettings,
    text: str,
    output_path: Path,
    play: bool,
    voice: str | None,
    temperature: float,
    speed: float,
    mlx_request: ResolvedMlxRequest,
    instruct: str | None,
) -> list[str]:
    chosen_voice = normalize_optional_text(voice) or mlx_request.effective_voice
    file_prefix = str(output_path.with_suffix(""))

    command = [
        settings.mlx_command,
        "--model",
        mlx_request.model_id,
        "--text",
        text,
        "--lang_code",
        mlx_request.language_code,
        "--temperature",
        str(temperature),
        "--speed",
        str(speed),
        "--file_prefix",
        file_prefix,
        "--audio_format",
        "wav",
        "--join_audio",
    ]

    if chosen_voice:
        command.extend(["--voice", chosen_voice])
    if instruct:
        if not mlx_supports_flag(settings.mlx_command, "--instruct"):
            raise ConfigError(
                "Configured MLX command does not support --instruct. "
                "Upgrade mlx-audio or switch to a non-VoiceDesign model."
            )
        command.extend(["--instruct", instruct])
    if play:
        command.append("--play")

    return command


def build_llama_command(
    settings: TtsSettings,
    text: str,
    output_path: Path,
) -> list[str]:
    command = [
        settings.llama_command,
        "-p",
        text,
        "-o",
        str(output_path),
        "--n-gpu-layers",
        str(settings.llama_n_gpu_layers),
    ]

    if settings.llama_model_path:
        if not settings.llama_vocoder_path:
            raise ConfigError("llama vocoder model path is required when model path is set.")
        command.extend(["-m", settings.llama_model_path, "-mv", settings.llama_vocoder_path])
    elif settings.llama_use_oute_default:
        command.append("--tts-oute-default")
    else:
        raise ConfigError(
            "No llama.cpp model configured. Enable LLAMA_TTS_USE_OUTE_DEFAULT or set model paths."
        )

    return command


def build_xtts_command(
    settings: TtsSettings,
    text: str,
    output_path: Path,
    voice: str | None,
    speed: float,
    language_code: str | None,
) -> list[str]:
    if normalize_optional_text(voice):
        raise ConfigError(
            "xtts backend does not support named voice selection. "
            "Use XTTS_DEFAULT_SPEAKER_WAV for voice cloning."
        )
    if not settings.xtts_default_speaker_wav:
        raise ConfigError(
            "xtts backend requires XTTS_DEFAULT_SPEAKER_WAV because this MCP surface "
            "does not expose speaker_id."
        )
    speaker_wav_path = Path(settings.xtts_default_speaker_wav).expanduser()
    if not speaker_wav_path.exists():
        raise ConfigError(f"XTTS_DEFAULT_SPEAKER_WAV not found: {speaker_wav_path}")

    language = resolve_xtts_language_code(
        language_code=language_code,
        default_language_code=settings.xtts_default_language_code,
    )
    script_path = resolve_runtime_script_path("xtts_generate.py")
    command = [
        settings.xtts_command,
        str(script_path),
        "--text",
        text,
        "--output-path",
        str(output_path),
        "--model-name",
        settings.xtts_model_name,
        "--language",
        language,
        "--speed",
        str(speed),
        "--device",
        settings.xtts_device,
    ]
    command.extend(["--speaker-wav", str(speaker_wav_path)])
    return command


def build_chatterbox_command(
    settings: TtsSettings,
    text: str,
    output_path: Path,
    voice: str | None,
    language_code: str | None,
) -> list[str]:
    if normalize_optional_text(voice):
        raise ConfigError(
            "chatterbox backend does not support named voice selection. "
            "Use CHATTERBOX_AUDIO_PROMPT_PATH for voice cloning."
        )

    language = resolve_chatterbox_language_code(
        language_code=language_code,
        default_language_code=settings.chatterbox_default_language_code,
    )
    script_path = resolve_runtime_script_path("chatterbox_generate.py")
    command = [
        settings.chatterbox_command,
        str(script_path),
        "--text",
        text,
        "--output-path",
        str(output_path),
        "--language",
        language,
        "--device",
        settings.chatterbox_device,
    ]
    if settings.chatterbox_audio_prompt_path:
        prompt_path = Path(settings.chatterbox_audio_prompt_path).expanduser()
        if not prompt_path.exists():
            raise ConfigError(f"CHATTERBOX_AUDIO_PROMPT_PATH not found: {prompt_path}")
        command.extend(["--audio-prompt-path", settings.chatterbox_audio_prompt_path])
    return command
