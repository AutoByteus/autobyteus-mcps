from __future__ import annotations

import os
from pathlib import Path
import platform
import shutil


RUN_REAL_LANGUAGE_SMOKE = os.getenv("TTS_MCP_RUN_REAL_LANGUAGE_SMOKE") == "1"
RUN_SLOW_REAL_LANGUAGE_SMOKE = os.getenv("TTS_MCP_RUN_SLOW_REAL_LANGUAGE_SMOKE") == "1"
IS_APPLE_SILICON_MAC = (
    platform.system() == "Darwin"
    and platform.machine().strip().lower() in {"arm64", "aarch64"}
)
IS_LINUX = platform.system() == "Linux"
ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_MLX_COMMAND = ROOT_DIR / ".venv-mlx" / "bin" / "mlx_audio.tts.generate"
DEFAULT_XTTS_COMMAND = ROOT_DIR / ".venv-xtts" / "bin" / "python"
DEFAULT_CHATTERBOX_COMMAND = ROOT_DIR / ".venv-chatterbox" / "bin" / "python"
DEFAULT_GERMAN_SPEAKER_WAV = ROOT_DIR / "outputs" / "jana_probe.wav"
ZH_MODEL_PATH = ROOT_DIR / ".tools" / "kokoro-v1.1-zh" / "kokoro-v1.1-zh.onnx"
ZH_VOICES_PATH = ROOT_DIR / ".tools" / "kokoro-v1.1-zh" / "voices-v1.1-zh.bin"
ZH_CONFIG_PATH = ROOT_DIR / ".tools" / "kokoro-v1.1-zh" / "config.json"


def resolve_mlx_command() -> str | None:
    env_command = os.getenv("MLX_TTS_COMMAND")
    if env_command:
        return env_command
    if DEFAULT_MLX_COMMAND.exists():
        return str(DEFAULT_MLX_COMMAND)
    return shutil.which("mlx_audio.tts.generate")


def resolve_xtts_command() -> str | None:
    env_command = os.getenv("XTTS_TTS_COMMAND")
    if env_command:
        return env_command
    if DEFAULT_XTTS_COMMAND.exists():
        return str(DEFAULT_XTTS_COMMAND)
    return shutil.which("python3") or shutil.which("python")


def resolve_chatterbox_command() -> str | None:
    env_command = os.getenv("CHATTERBOX_TTS_COMMAND")
    if env_command:
        return env_command
    if DEFAULT_CHATTERBOX_COMMAND.exists():
        return str(DEFAULT_CHATTERBOX_COMMAND)
    return shutil.which("python3") or shutil.which("python")


def assert_valid_wav(path: Path) -> None:
    assert path.exists()
    assert path.stat().st_size > 44
