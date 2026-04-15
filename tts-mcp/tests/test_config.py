from __future__ import annotations

import pytest

from pathlib import Path

from tts_mcp.config import ConfigError, SUPPORTED_MLX_MODEL_IDS, load_settings, model_requires_instruct
from tts_mcp.runtime_paths import resolve_runtime_root


def test_load_settings_defaults() -> None:
    settings = load_settings({})

    assert settings.default_backend == "auto"
    assert settings.linux_runtime == "kokoro_onnx"
    assert settings.timeout_seconds == 180
    assert settings.process_lock_timeout_seconds == 30
    assert settings.delete_auto_output is True
    assert settings.enforce_latest_runtime is True
    assert settings.version_check_timeout_seconds == 6
    assert settings.auto_install_runtime is True
    assert settings.auto_install_llama_on_macos is False
    assert settings.hf_hub_offline_mode == "auto"
    assert settings.default_speed == 1.0
    assert settings.mlx_command == "mlx_audio.tts.generate"
    assert settings.mlx_model_preset == "kokoro_fast"
    assert settings.mlx_model_preset_explicit is False
    assert settings.mlx_model in SUPPORTED_MLX_MODEL_IDS
    assert settings.mlx_model_explicit is False
    assert settings.mlx_default_temperature == 0.0
    assert settings.llama_command == "llama-tts"
    assert settings.kokoro_model_path.endswith("kokoro-v1.0.int8.onnx")
    assert settings.kokoro_model_path_explicit is False
    assert settings.kokoro_voices_path.endswith("voices-v1.0.bin")
    assert settings.kokoro_voices_path_explicit is False
    assert settings.kokoro_vocab_config_path is None
    assert settings.kokoro_vocab_config_path_explicit is False
    assert settings.kokoro_misaki_zh_version == "1.1"
    assert settings.kokoro_default_voice == "af_heart"
    assert settings.kokoro_default_voice_explicit is False
    assert settings.kokoro_default_language_code == "en-us"
    assert Path(settings.xtts_command).resolve(strict=False) == (
        resolve_runtime_root() / ".venv-xtts" / "bin" / "python"
    ).resolve(strict=False)
    assert settings.xtts_model_name == "tts_models/multilingual/multi-dataset/xtts_v2"
    assert settings.xtts_default_language_code == "en"
    assert settings.xtts_default_speaker_wav is None
    assert settings.xtts_device == "auto"
    assert settings.xtts_coqui_tos_agreed is False
    assert Path(settings.chatterbox_command).resolve(strict=False) == (
        resolve_runtime_root() / ".venv-chatterbox" / "bin" / "python"
    ).resolve(strict=False)
    assert settings.chatterbox_default_language_code == "en"
    assert settings.chatterbox_audio_prompt_path is None
    assert settings.chatterbox_device == "auto"


def test_load_settings_keeps_default_mlx_preset_even_when_default_language_is_german() -> None:
    settings = load_settings({"MLX_TTS_DEFAULT_LANG_CODE": "de-DE"})

    assert settings.mlx_model_preset == "kokoro_fast"
    assert settings.mlx_model == "mlx-community/Kokoro-82M-bf16"


def test_load_settings_keeps_default_mlx_preset_even_when_default_language_is_chinese() -> None:
    settings = load_settings({"MLX_TTS_DEFAULT_LANG_CODE": "zh"})

    assert settings.mlx_model_preset == "kokoro_fast"
    assert settings.mlx_model == "mlx-community/Kokoro-82M-bf16"


def test_load_settings_keeps_explicit_mlx_preset_even_when_default_language_is_german() -> None:
    settings = load_settings(
        {
            "MLX_TTS_DEFAULT_LANG_CODE": "de",
            "TTS_MCP_MLX_MODEL_PRESET": "qwen_base_hq",
        }
    )

    assert settings.mlx_model_preset == "qwen_base_hq"
    assert settings.mlx_model == "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16"
    assert settings.mlx_model_preset_explicit is True
    assert settings.mlx_model_explicit is False


def test_load_settings_infers_mlx_preset_from_explicit_model() -> None:
    settings = load_settings(
        {
            "MLX_TTS_MODEL": "mlx-community/3b-de-ft-research_release-bf16",
        }
    )

    assert settings.mlx_model_preset == "german_orpheus_hq"
    assert settings.mlx_model == "mlx-community/3b-de-ft-research_release-bf16"
    assert settings.mlx_model_preset_explicit is False
    assert settings.mlx_model_explicit is True


def test_load_settings_rejects_invalid_backend() -> None:
    with pytest.raises(ConfigError, match="TTS_MCP_BACKEND"):
        load_settings({"TTS_MCP_BACKEND": "bad"})


def test_load_settings_rejects_invalid_linux_runtime() -> None:
    with pytest.raises(ConfigError, match="TTS_MCP_LINUX_RUNTIME"):
        load_settings({"TTS_MCP_LINUX_RUNTIME": "bad"})


def test_load_settings_rejects_invalid_preset() -> None:
    with pytest.raises(ConfigError, match="TTS_MCP_MLX_MODEL_PRESET"):
        load_settings({"TTS_MCP_MLX_MODEL_PRESET": "unknown"})


def test_load_settings_rejects_unsupported_mlx_model() -> None:
    with pytest.raises(ConfigError, match="MLX_TTS_MODEL"):
        load_settings({"MLX_TTS_MODEL": "my-org/custom"})


def test_load_settings_requires_vocoder_when_model_is_set() -> None:
    with pytest.raises(ConfigError, match="LLAMA_TTS_VOCODER_PATH"):
        load_settings({"LLAMA_TTS_MODEL_PATH": "/tmp/model.gguf"})


def test_load_settings_rejects_invalid_hf_hub_offline_mode() -> None:
    with pytest.raises(ConfigError, match="TTS_MCP_HF_HUB_OFFLINE_MODE"):
        load_settings({"TTS_MCP_HF_HUB_OFFLINE_MODE": "maybe"})


def test_load_settings_rejects_invalid_process_lock_timeout() -> None:
    with pytest.raises(ConfigError, match="TTS_MCP_PROCESS_LOCK_TIMEOUT_SECONDS"):
        load_settings({"TTS_MCP_PROCESS_LOCK_TIMEOUT_SECONDS": "0"})


def test_load_settings_rejects_invalid_default_speed() -> None:
    with pytest.raises(ConfigError, match="TTS_MCP_DEFAULT_SPEED"):
        load_settings({"TTS_MCP_DEFAULT_SPEED": "0"})


def test_load_settings_records_explicit_mlx_default_temperature() -> None:
    settings = load_settings({"MLX_TTS_DEFAULT_TEMPERATURE": "0.4"})

    assert settings.mlx_default_temperature == 0.4


def test_load_settings_rejects_negative_mlx_default_temperature() -> None:
    with pytest.raises(ConfigError, match="MLX_TTS_DEFAULT_TEMPERATURE"):
        load_settings({"MLX_TTS_DEFAULT_TEMPERATURE": "-0.1"})


def test_load_settings_accepts_explicit_xtts_backend() -> None:
    settings = load_settings({"TTS_MCP_BACKEND": "xtts"})

    assert settings.default_backend == "xtts"


def test_load_settings_accepts_explicit_chatterbox_backend() -> None:
    settings = load_settings({"TTS_MCP_BACKEND": "chatterbox"})

    assert settings.default_backend == "chatterbox"


def test_load_settings_rejects_invalid_torch_device() -> None:
    with pytest.raises(ConfigError, match="Torch device"):
        load_settings({"XTTS_DEVICE": "metal"})


def test_load_settings_normalizes_relative_backend_file_paths(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("TTS_MCP_ROOT_DIR", str(tmp_path))

    settings = load_settings(
        {
            "XTTS_DEFAULT_SPEAKER_WAV": "speakers/default.wav",
            "CHATTERBOX_AUDIO_PROMPT_PATH": "prompts/clone.wav",
            "LLAMA_TTS_MODEL_PATH": "models/model.gguf",
            "LLAMA_TTS_VOCODER_PATH": "models/vocoder.gguf",
        }
    )

    assert settings.xtts_default_speaker_wav == str(
        (tmp_path / "speakers" / "default.wav").resolve(strict=False)
    )
    assert settings.chatterbox_audio_prompt_path == str(
        (tmp_path / "prompts" / "clone.wav").resolve(strict=False)
    )
    assert settings.llama_model_path == str(
        (tmp_path / "models" / "model.gguf").resolve(strict=False)
    )
    assert settings.llama_vocoder_path == str(
        (tmp_path / "models" / "vocoder.gguf").resolve(strict=False)
    )


def test_load_settings_normalizes_relative_kokoro_asset_paths(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("TTS_MCP_ROOT_DIR", str(tmp_path))

    settings = load_settings(
        {
            "KOKORO_TTS_MODEL_PATH": ".tools/custom/model.onnx",
            "KOKORO_TTS_VOICES_PATH": ".tools/custom/voices.bin",
            "KOKORO_TTS_VOCAB_CONFIG_PATH": ".tools/custom/config.json",
        }
    )

    assert settings.kokoro_model_path == str(
        (tmp_path / ".tools" / "custom" / "model.onnx").resolve(strict=False)
    )
    assert settings.kokoro_voices_path == str(
        (tmp_path / ".tools" / "custom" / "voices.bin").resolve(strict=False)
    )
    assert settings.kokoro_vocab_config_path == str(
        (tmp_path / ".tools" / "custom" / "config.json").resolve(strict=False)
    )
    assert settings.kokoro_model_path_explicit is True
    assert settings.kokoro_voices_path_explicit is True
    assert settings.kokoro_vocab_config_path_explicit is True


def test_load_settings_records_explicit_kokoro_default_voice() -> None:
    settings = load_settings({"KOKORO_TTS_DEFAULT_VOICE": "zf_008"})

    assert settings.kokoro_default_voice == "zf_008"
    assert settings.kokoro_default_voice_explicit is True


def test_model_requires_instruct_for_voicedesign() -> None:
    assert model_requires_instruct("mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16") is True
    assert model_requires_instruct("mlx-community/Kokoro-82M-bf16") is False
    assert model_requires_instruct("mlx-community/3b-de-ft-research_release-bf16") is False
