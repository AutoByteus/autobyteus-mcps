from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import wave
from typing import TypedDict

from .backend_contracts import normalize_optional_text, resolve_kokoro_language_code
from .config import (
    DEFAULT_KOKORO_DEFAULT_VOICE,
    DEFAULT_KOKORO_MODEL_PATH,
    DEFAULT_KOKORO_VOICES_PATH,
    DEFAULT_KOKORO_ZH_DEFAULT_VOICE,
    DEFAULT_KOKORO_ZH_MODEL_PATH,
    DEFAULT_KOKORO_ZH_VOCAB_CONFIG_PATH,
    DEFAULT_KOKORO_ZH_VOICES_PATH,
    TtsSettings,
)
from .execution_support import ExecutionResult
class KokoroRuntimeConfig(TypedDict):
    model_path: str
    voices_path: str
    vocab_config_path: str | None
    selected_voice: str


def run_kokoro_generation(
    settings: TtsSettings,
    text: str,
    output_path: Path,
    voice: str | None,
    speed: float,
    language_code: str | None,
) -> ExecutionResult:
    try:
        import numpy as np  # type: ignore
    except Exception as exc:
        return ExecutionResult(
            stdout=None,
            stderr=None,
            exit_code=None,
            error_type="dependency",
            error_message=f"numpy dependency is unavailable for kokoro_onnx backend: {exc}",
        )

    selected_language = resolve_kokoro_language_code(language_code, settings.kokoro_default_language_code)
    runtime_config = resolve_kokoro_runtime_config(settings, selected_language, voice)

    try:
        kokoro = load_kokoro_runtime(
            model_path=resolve_runtime_path(runtime_config["model_path"]),
            voices_path=resolve_runtime_path(runtime_config["voices_path"]),
            vocab_config_path=(
                resolve_runtime_path(runtime_config["vocab_config_path"])
                if runtime_config["vocab_config_path"]
                else None
            ),
        )
    except Exception as exc:
        return ExecutionResult(
            stdout=None,
            stderr=None,
            exit_code=None,
            error_type="dependency",
            error_message=str(exc),
        )

    selected_voice = runtime_config["selected_voice"]
    use_misaki_zh = should_use_kokoro_misaki_zh(selected_language, runtime_config["vocab_config_path"])

    synthesis_text = text
    create_kwargs: dict[str, object] = {}
    if use_misaki_zh:
        try:
            g2p = load_misaki_zh_g2p(version=settings.kokoro_misaki_zh_version)
        except Exception as exc:
            return ExecutionResult(
                stdout=None,
                stderr=None,
                exit_code=None,
                error_type="dependency",
                error_message=str(exc),
            )
        synthesis_text, _ = g2p(text)
        create_kwargs["is_phonemes"] = True
    else:
        create_kwargs["lang"] = selected_language

    try:
        samples, sample_rate = kokoro.create(text=synthesis_text, voice=selected_voice, speed=speed, **create_kwargs)
        audio = np.asarray(samples, dtype=np.float32)
        audio = np.clip(audio, -1.0, 1.0)
        pcm16 = (audio * 32767.0).astype(np.int16)

        with wave.open(str(output_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(int(sample_rate))
            wav_file.writeframes(pcm16.tobytes())
    except Exception as exc:
        return ExecutionResult(
            stdout=None,
            stderr=None,
            exit_code=1,
            error_type="execution",
            error_message=f"Kokoro generation failed: {exc}",
        )

    return ExecutionResult(stdout=f"kokoro_onnx generated voice={selected_voice} lang={selected_language} misaki_zh={use_misaki_zh}", stderr=None, exit_code=0, error_type=None, error_message=None)


def resolve_kokoro_runtime_config(settings: TtsSettings, selected_language: str, requested_voice: str | None) -> KokoroRuntimeConfig:
    normalized_voice = normalize_optional_text(requested_voice)
    if normalized_voice:
        selected_voice = normalized_voice
    else:
        selected_voice = settings.kokoro_default_voice

    default_paths_in_use = (
        settings.kokoro_model_path == DEFAULT_KOKORO_MODEL_PATH
        and settings.kokoro_voices_path == DEFAULT_KOKORO_VOICES_PATH
        and settings.kokoro_vocab_config_path is None
    )
    language_is_chinese = selected_language.strip().lower() in {"cmn", "z"}

    if language_is_chinese and default_paths_in_use:
        if (
            normalized_voice is None
            and settings.kokoro_default_voice == DEFAULT_KOKORO_DEFAULT_VOICE
        ):
            selected_voice = DEFAULT_KOKORO_ZH_DEFAULT_VOICE
        return KokoroRuntimeConfig(
            model_path=DEFAULT_KOKORO_ZH_MODEL_PATH,
            voices_path=DEFAULT_KOKORO_ZH_VOICES_PATH,
            vocab_config_path=DEFAULT_KOKORO_ZH_VOCAB_CONFIG_PATH,
            selected_voice=selected_voice,
        )

    auto_vocab_for_zh_profile = (
        language_is_chinese
        and settings.kokoro_vocab_config_path is None
        and settings.kokoro_model_path == DEFAULT_KOKORO_ZH_MODEL_PATH
        and settings.kokoro_voices_path == DEFAULT_KOKORO_ZH_VOICES_PATH
    )
    return KokoroRuntimeConfig(model_path=settings.kokoro_model_path, voices_path=settings.kokoro_voices_path, vocab_config_path=(DEFAULT_KOKORO_ZH_VOCAB_CONFIG_PATH if auto_vocab_for_zh_profile else settings.kokoro_vocab_config_path), selected_voice=selected_voice)


def should_use_kokoro_misaki_zh(selected_language: str, vocab_config_path: str | None) -> bool:
    return bool(vocab_config_path) and selected_language.strip().lower() in {"cmn", "z"}

@lru_cache(maxsize=4)
def load_kokoro_runtime(model_path: Path, voices_path: Path, vocab_config_path: Path | None):
    if not model_path.exists():
        raise RuntimeError(
            f"Kokoro model file not found: {model_path}. "
            "Run scripts/install_kokoro_onnx_linux.sh or set KOKORO_TTS_MODEL_PATH."
        )
    if not voices_path.exists():
        raise RuntimeError(
            f"Kokoro voices file not found: {voices_path}. "
            "Run scripts/install_kokoro_onnx_linux.sh or set KOKORO_TTS_VOICES_PATH."
        )
    if vocab_config_path is not None and not vocab_config_path.exists():
        raise RuntimeError(
            f"Kokoro vocab config file not found: {vocab_config_path}. "
            "Set KOKORO_TTS_VOCAB_CONFIG_PATH to a valid file path."
        )

    try:
        from kokoro_onnx import Kokoro  # type: ignore
    except Exception as exc:
        raise RuntimeError(
            "kokoro-onnx package is not installed. "
            "Install with: pip install --upgrade kokoro-onnx"
        ) from exc

    kwargs: dict[str, str] = {}
    if vocab_config_path is not None:
        kwargs["vocab_config"] = str(vocab_config_path)
    return Kokoro(str(model_path), str(voices_path), **kwargs)


@lru_cache(maxsize=2)
def load_misaki_zh_g2p(version: str):
    try:
        from misaki import zh  # type: ignore
    except Exception as exc:
        raise RuntimeError(
            "misaki-fork[zh] package is not installed for Kokoro Chinese phonemization. "
            "Install with: pip install --upgrade 'misaki-fork[zh]'"
        ) from exc

    return zh.ZHG2P(version=version)


def resolve_runtime_path(value: str) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    root_dir = Path(__file__).resolve().parents[2]
    return (root_dir / path).resolve(strict=False)
