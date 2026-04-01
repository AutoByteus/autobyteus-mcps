from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import wave

from .config import TtsSettings
from .execution_support import ExecutionResult
from .routing_policy import ResolvedKokoroRequest


def run_kokoro_generation(
    settings: TtsSettings,
    text: str,
    output_path: Path,
    speed: float,
    kokoro_request: ResolvedKokoroRequest | None,
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

    if kokoro_request is None:
        return ExecutionResult(
            stdout=None,
            stderr=None,
            exit_code=None,
            error_type="dependency",
            error_message="Kokoro request resolution was missing before generation.",
        )

    try:
        kokoro = load_kokoro_runtime(
            model_path=Path(kokoro_request.model_path),
            voices_path=Path(kokoro_request.voices_path),
            vocab_config_path=(
                Path(kokoro_request.vocab_config_path)
                if kokoro_request.vocab_config_path
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

    synthesis_text = text
    create_kwargs: dict[str, object] = {}
    if kokoro_request.use_misaki_zh:
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
        create_kwargs["lang"] = kokoro_request.language_code

    try:
        samples, sample_rate = kokoro.create(
            text=synthesis_text,
            voice=kokoro_request.selected_voice,
            speed=speed,
            **create_kwargs,
        )
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

    return ExecutionResult(
        stdout=(
            "kokoro_onnx generated "
            f"voice={kokoro_request.selected_voice} "
            f"lang={kokoro_request.language_code} "
            f"misaki_zh={kokoro_request.use_misaki_zh}"
        ),
        stderr=None,
        exit_code=0,
        error_type=None,
        error_message=None,
    )

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
