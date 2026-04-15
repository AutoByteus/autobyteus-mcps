from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Literal, Mapping

from .runtime_paths import resolve_runtime_command_path, resolve_runtime_file_path, resolve_runtime_root

BackendName = Literal["auto", "mlx_audio", "llama_cpp", "kokoro_onnx", "xtts", "chatterbox"]
LinuxRuntimeName = Literal["llama_cpp", "kokoro_onnx"]
MlxModelPreset = Literal[
    "kokoro_fast",
    "qwen_base_hq",
    "qwen_customvoice_hq",
    "qwen_voicedesign_hq",
    "german_orpheus_hq",
]
HfHubOfflineMode = Literal["auto", "true", "false"]
TorchDevice = Literal["auto", "cpu", "cuda", "mps"]

DEFAULT_MLX_MODEL_PRESET: MlxModelPreset = "kokoro_fast"
DEFAULT_MLX_GERMAN_MODEL_PRESET: MlxModelPreset = "german_orpheus_hq"
DEFAULT_MLX_CHINESE_MODEL_PRESET: MlxModelPreset = "qwen_customvoice_hq"
DEFAULT_MLX_DEFAULT_LANGUAGE_CODE = "en"
DEFAULT_MLX_CHINESE_DEFAULT_VOICE = "Vivian"
DEFAULT_MLX_DEFAULT_TEMPERATURE = 0.0

DEFAULT_SERVER_NAME = "tts-mcp"
DEFAULT_INSTRUCTIONS = (
    "Expose one speak tool that converts text to speech. "
    "Auto-route to MLX Audio on Apple Silicon, and on Linux route by runtime policy "
    "(llama.cpp or Kokoro ONNX). Also allow explicit XTTS and Chatterbox selection "
    "through MCP environment configuration."
)

MLX_MODEL_PRESETS: dict[MlxModelPreset, tuple[str, str, bool]] = {
    "kokoro_fast": (
        "mlx-community/Kokoro-82M-bf16",
        "Fast and small; best default for low-latency speech.",
        False,
    ),
    "qwen_base_hq": (
        "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16",
        "Higher-quality general model.",
        False,
    ),
    "qwen_customvoice_hq": (
        "mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16",
        "Higher-quality predefined-speaker model for stable named voices.",
        False,
    ),
    "qwen_voicedesign_hq": (
        "mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16",
        "Highest flexibility for designed voices; requires instruct.",
        True,
    ),
    "german_orpheus_hq": (
        "mlx-community/3b-de-ft-research_release-bf16",
        "Best-quality German-first MLX preset on Apple Silicon.",
        False,
    ),
}

SUPPORTED_MLX_MODEL_IDS: tuple[str, ...] = tuple(
    preset[0] for preset in MLX_MODEL_PRESETS.values()
)

DEFAULT_KOKORO_MODEL_PATH = ".tools/kokoro-current/kokoro-v1.0.int8.onnx"
DEFAULT_KOKORO_VOICES_PATH = ".tools/kokoro-current/voices-v1.0.bin"
DEFAULT_KOKORO_DEFAULT_VOICE = "af_heart"
DEFAULT_KOKORO_DEFAULT_LANGUAGE_CODE = "en-us"

DEFAULT_KOKORO_ZH_MODEL_PATH = ".tools/kokoro-v1.1-zh/kokoro-v1.1-zh.onnx"
DEFAULT_KOKORO_ZH_VOICES_PATH = ".tools/kokoro-v1.1-zh/voices-v1.1-zh.bin"
DEFAULT_KOKORO_ZH_VOCAB_CONFIG_PATH = ".tools/kokoro-v1.1-zh/config.json"
DEFAULT_KOKORO_ZH_DEFAULT_VOICE = "zf_001"

DEFAULT_XTTS_COMMAND = ".venv-xtts/bin/python"
DEFAULT_XTTS_MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
DEFAULT_XTTS_DEFAULT_LANGUAGE_CODE = "en"

DEFAULT_CHATTERBOX_COMMAND = ".venv-chatterbox/bin/python"
DEFAULT_CHATTERBOX_DEFAULT_LANGUAGE_CODE = "en"


class ConfigError(ValueError):
    """Raised when configuration values are invalid."""


@dataclass(frozen=True, slots=True)
class ServerConfig:
    name: str = DEFAULT_SERVER_NAME
    instructions: str = DEFAULT_INSTRUCTIONS

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "ServerConfig":
        actual_env = env if env is not None else os.environ
        return cls(
            name=actual_env.get("TTS_MCP_NAME", DEFAULT_SERVER_NAME),
            instructions=actual_env.get("TTS_MCP_INSTRUCTIONS", DEFAULT_INSTRUCTIONS),
        )


@dataclass(frozen=True, slots=True)
class TtsSettings:
    default_backend: BackendName
    linux_runtime: LinuxRuntimeName
    timeout_seconds: int
    process_lock_timeout_seconds: int
    output_dir: str
    delete_auto_output: bool
    enforce_latest_runtime: bool
    version_check_timeout_seconds: int
    auto_install_runtime: bool
    auto_install_llama_on_macos: bool
    hf_hub_offline_mode: HfHubOfflineMode
    default_speed: float

    mlx_command: str
    mlx_model_preset: MlxModelPreset
    mlx_model_preset_explicit: bool
    mlx_model: str
    mlx_model_explicit: bool
    mlx_default_voice: str | None
    mlx_default_temperature: float
    mlx_default_language_code: str
    mlx_default_instruct: str | None

    llama_command: str
    llama_use_oute_default: bool
    llama_model_path: str | None
    llama_vocoder_path: str | None
    llama_n_gpu_layers: int

    kokoro_model_path: str
    kokoro_model_path_explicit: bool
    kokoro_voices_path: str
    kokoro_voices_path_explicit: bool
    kokoro_vocab_config_path: str | None
    kokoro_vocab_config_path_explicit: bool
    kokoro_misaki_zh_version: str
    kokoro_default_voice: str
    kokoro_default_voice_explicit: bool
    kokoro_default_language_code: str

    xtts_command: str
    xtts_model_name: str
    xtts_default_language_code: str
    xtts_default_speaker_wav: str | None
    xtts_device: TorchDevice
    xtts_coqui_tos_agreed: bool

    chatterbox_command: str
    chatterbox_default_language_code: str
    chatterbox_audio_prompt_path: str | None
    chatterbox_device: TorchDevice

    linux_player: Literal["auto", "ffplay", "aplay", "paplay", "none"]


def load_settings(env: Mapping[str, str] | None = None) -> TtsSettings:
    actual_env = env if env is not None else os.environ

    default_backend = _parse_backend(actual_env.get("TTS_MCP_BACKEND", "auto"))
    linux_runtime = _parse_linux_runtime(actual_env.get("TTS_MCP_LINUX_RUNTIME", "kokoro_onnx"))
    timeout_seconds = _parse_positive_int(
        actual_env.get("TTS_MCP_TIMEOUT_SECONDS", "180"),
        "TTS_MCP_TIMEOUT_SECONDS",
    )
    process_lock_timeout_seconds = _parse_positive_int(
        actual_env.get("TTS_MCP_PROCESS_LOCK_TIMEOUT_SECONDS", "30"),
        "TTS_MCP_PROCESS_LOCK_TIMEOUT_SECONDS",
    )
    output_dir = actual_env.get("TTS_MCP_OUTPUT_DIR", "outputs").strip() or "outputs"
    delete_auto_output = _parse_bool(
        actual_env.get("TTS_MCP_DELETE_AUTO_OUTPUT", "true"),
        "TTS_MCP_DELETE_AUTO_OUTPUT",
    )
    enforce_latest_runtime = _parse_bool(
        actual_env.get("TTS_MCP_ENFORCE_LATEST", "true"),
        "TTS_MCP_ENFORCE_LATEST",
    )
    version_check_timeout_seconds = _parse_positive_int(
        actual_env.get("TTS_MCP_VERSION_CHECK_TIMEOUT_SECONDS", "6"),
        "TTS_MCP_VERSION_CHECK_TIMEOUT_SECONDS",
    )
    auto_install_runtime = _parse_bool(
        actual_env.get("TTS_MCP_AUTO_INSTALL_RUNTIME", "true"),
        "TTS_MCP_AUTO_INSTALL_RUNTIME",
    )
    auto_install_llama_on_macos = _parse_bool(
        actual_env.get("TTS_MCP_AUTO_INSTALL_LLAMA_ON_MACOS", "false"),
        "TTS_MCP_AUTO_INSTALL_LLAMA_ON_MACOS",
    )
    hf_hub_offline_mode = _parse_hf_hub_offline_mode(
        actual_env.get("TTS_MCP_HF_HUB_OFFLINE_MODE", "auto")
    )
    default_speed = _parse_positive_float(
        actual_env.get("TTS_MCP_DEFAULT_SPEED", "1.0"),
        "TTS_MCP_DEFAULT_SPEED",
    )

    mlx_command = resolve_runtime_command_path(
        _require_non_empty(actual_env, "MLX_TTS_COMMAND", default="mlx_audio.tts.generate")
    )

    explicit_mlx_preset = _optional_text(actual_env.get("TTS_MCP_MLX_MODEL_PRESET"))
    explicit_mlx_model = _optional_text(actual_env.get("MLX_TTS_MODEL"))

    mlx_model_preset = _resolve_mlx_model_preset(actual_env)
    preset_model = MLX_MODEL_PRESETS[mlx_model_preset][0]
    mlx_model = _require_non_empty(
        actual_env,
        "MLX_TTS_MODEL",
        default=preset_model,
    )

    if mlx_model not in SUPPORTED_MLX_MODEL_IDS:
        allowed = ", ".join(SUPPORTED_MLX_MODEL_IDS)
        raise ConfigError(
            f"MLX_TTS_MODEL must be one of supported models: {allowed}."
        )

    mlx_default_voice = _optional_text(actual_env.get("MLX_TTS_DEFAULT_VOICE"))
    mlx_default_temperature = _parse_non_negative_float(
        actual_env.get("MLX_TTS_DEFAULT_TEMPERATURE", str(DEFAULT_MLX_DEFAULT_TEMPERATURE)),
        "MLX_TTS_DEFAULT_TEMPERATURE",
    )
    mlx_default_language_code = _require_non_empty(
        actual_env,
        "MLX_TTS_DEFAULT_LANG_CODE",
        default=DEFAULT_MLX_DEFAULT_LANGUAGE_CODE,
    )
    mlx_default_instruct = _optional_text(actual_env.get("MLX_TTS_DEFAULT_INSTRUCT"))

    llama_command = resolve_runtime_command_path(
        _require_non_empty(actual_env, "LLAMA_TTS_COMMAND", default="llama-tts")
    )
    llama_use_oute_default = _parse_bool(
        actual_env.get("LLAMA_TTS_USE_OUTE_DEFAULT", "true"),
        "LLAMA_TTS_USE_OUTE_DEFAULT",
    )
    llama_model_path = resolve_runtime_file_path(_optional_text(actual_env.get("LLAMA_TTS_MODEL_PATH")))
    llama_vocoder_path = resolve_runtime_file_path(
        _optional_text(actual_env.get("LLAMA_TTS_VOCODER_PATH"))
    )
    llama_n_gpu_layers = _parse_int(
        actual_env.get("LLAMA_TTS_N_GPU_LAYERS", "-1"),
        "LLAMA_TTS_N_GPU_LAYERS",
    )

    if llama_model_path and not llama_vocoder_path:
        raise ConfigError(
            "LLAMA_TTS_VOCODER_PATH is required when LLAMA_TTS_MODEL_PATH is set."
        )
    if not llama_model_path and not llama_use_oute_default:
        raise ConfigError(
            "Set LLAMA_TTS_USE_OUTE_DEFAULT=true or provide both LLAMA_TTS_MODEL_PATH "
            "and LLAMA_TTS_VOCODER_PATH."
        )

    explicit_kokoro_model_path = _optional_text(actual_env.get("KOKORO_TTS_MODEL_PATH"))
    explicit_kokoro_voices_path = _optional_text(actual_env.get("KOKORO_TTS_VOICES_PATH"))
    explicit_kokoro_vocab_config_path = _optional_text(actual_env.get("KOKORO_TTS_VOCAB_CONFIG_PATH"))
    explicit_kokoro_default_voice = _optional_text(actual_env.get("KOKORO_TTS_DEFAULT_VOICE"))

    kokoro_model_path = resolve_runtime_file_path(
        _require_non_empty(
            actual_env,
            "KOKORO_TTS_MODEL_PATH",
            default=DEFAULT_KOKORO_MODEL_PATH,
        )
    )
    kokoro_voices_path = resolve_runtime_file_path(
        _require_non_empty(
            actual_env,
            "KOKORO_TTS_VOICES_PATH",
            default=DEFAULT_KOKORO_VOICES_PATH,
        )
    )
    kokoro_vocab_config_path = resolve_runtime_file_path(explicit_kokoro_vocab_config_path)
    kokoro_misaki_zh_version = _require_non_empty(
        actual_env,
        "KOKORO_TTS_MISAKI_ZH_VERSION",
        default="1.1",
    )
    kokoro_default_voice = _require_non_empty(
        actual_env,
        "KOKORO_TTS_DEFAULT_VOICE",
        default=DEFAULT_KOKORO_DEFAULT_VOICE,
    )
    kokoro_default_language_code = _require_non_empty(
        actual_env,
        "KOKORO_TTS_DEFAULT_LANG_CODE",
        default=DEFAULT_KOKORO_DEFAULT_LANGUAGE_CODE,
    )

    xtts_command = resolve_runtime_command_path(
        _require_non_empty(
            actual_env,
            "XTTS_TTS_COMMAND",
            default=DEFAULT_XTTS_COMMAND,
        )
    )
    xtts_model_name = _require_non_empty(
        actual_env,
        "XTTS_MODEL_NAME",
        default=DEFAULT_XTTS_MODEL_NAME,
    )
    xtts_default_language_code = _require_non_empty(
        actual_env,
        "XTTS_DEFAULT_LANGUAGE_CODE",
        default=DEFAULT_XTTS_DEFAULT_LANGUAGE_CODE,
    )
    xtts_default_speaker_wav = resolve_runtime_file_path(
        _optional_text(actual_env.get("XTTS_DEFAULT_SPEAKER_WAV"))
    )
    xtts_device = _parse_torch_device(actual_env.get("XTTS_DEVICE", "auto"))
    xtts_coqui_tos_agreed = _parse_bool(
        actual_env.get("XTTS_COQUI_TOS_AGREED", "false"),
        "XTTS_COQUI_TOS_AGREED",
    )

    chatterbox_command = resolve_runtime_command_path(
        _require_non_empty(
            actual_env,
            "CHATTERBOX_TTS_COMMAND",
            default=DEFAULT_CHATTERBOX_COMMAND,
        )
    )
    chatterbox_default_language_code = _require_non_empty(
        actual_env,
        "CHATTERBOX_DEFAULT_LANGUAGE_CODE",
        default=DEFAULT_CHATTERBOX_DEFAULT_LANGUAGE_CODE,
    )
    chatterbox_audio_prompt_path = resolve_runtime_file_path(
        _optional_text(actual_env.get("CHATTERBOX_AUDIO_PROMPT_PATH"))
    )
    chatterbox_device = _parse_torch_device(actual_env.get("CHATTERBOX_DEVICE", "auto"))

    linux_player = _parse_linux_player(actual_env.get("TTS_MCP_LINUX_PLAYER", "auto"))

    return TtsSettings(
        default_backend=default_backend,
        linux_runtime=linux_runtime,
        timeout_seconds=timeout_seconds,
        process_lock_timeout_seconds=process_lock_timeout_seconds,
        output_dir=output_dir,
        delete_auto_output=delete_auto_output,
        enforce_latest_runtime=enforce_latest_runtime,
        version_check_timeout_seconds=version_check_timeout_seconds,
        auto_install_runtime=auto_install_runtime,
        auto_install_llama_on_macos=auto_install_llama_on_macos,
        hf_hub_offline_mode=hf_hub_offline_mode,
        default_speed=default_speed,
        mlx_command=mlx_command,
        mlx_model_preset=mlx_model_preset,
        mlx_model_preset_explicit=explicit_mlx_preset is not None,
        mlx_model=mlx_model,
        mlx_model_explicit=explicit_mlx_model is not None,
        mlx_default_voice=mlx_default_voice,
        mlx_default_temperature=mlx_default_temperature,
        mlx_default_language_code=mlx_default_language_code,
        mlx_default_instruct=mlx_default_instruct,
        llama_command=llama_command,
        llama_use_oute_default=llama_use_oute_default,
        llama_model_path=llama_model_path,
        llama_vocoder_path=llama_vocoder_path,
        llama_n_gpu_layers=llama_n_gpu_layers,
        kokoro_model_path=kokoro_model_path,
        kokoro_model_path_explicit=explicit_kokoro_model_path is not None,
        kokoro_voices_path=kokoro_voices_path,
        kokoro_voices_path_explicit=explicit_kokoro_voices_path is not None,
        kokoro_vocab_config_path=kokoro_vocab_config_path,
        kokoro_vocab_config_path_explicit=explicit_kokoro_vocab_config_path is not None,
        kokoro_misaki_zh_version=kokoro_misaki_zh_version,
        kokoro_default_voice=kokoro_default_voice,
        kokoro_default_voice_explicit=explicit_kokoro_default_voice is not None,
        kokoro_default_language_code=kokoro_default_language_code,
        xtts_command=xtts_command,
        xtts_model_name=xtts_model_name,
        xtts_default_language_code=xtts_default_language_code,
        xtts_default_speaker_wav=xtts_default_speaker_wav,
        xtts_device=xtts_device,
        xtts_coqui_tos_agreed=xtts_coqui_tos_agreed,
        chatterbox_command=chatterbox_command,
        chatterbox_default_language_code=chatterbox_default_language_code,
        chatterbox_audio_prompt_path=chatterbox_audio_prompt_path,
        chatterbox_device=chatterbox_device,
        linux_player=linux_player,
    )


def model_requires_instruct(model_id: str) -> bool:
    for configured_model, _, requires_instruct in MLX_MODEL_PRESETS.values():
        if configured_model == model_id:
            return requires_instruct
    return False


def _resolve_mlx_model_preset(env: Mapping[str, str]) -> MlxModelPreset:
    explicit_preset = _optional_text(env.get("TTS_MCP_MLX_MODEL_PRESET"))
    if explicit_preset is not None:
        return _parse_model_preset(explicit_preset)

    explicit_model = _optional_text(env.get("MLX_TTS_MODEL"))
    if explicit_model is not None:
        inferred = _infer_mlx_model_preset(explicit_model)
        if inferred is not None:
            return inferred
        return DEFAULT_MLX_MODEL_PRESET

    return DEFAULT_MLX_MODEL_PRESET


def _infer_mlx_model_preset(model_id: str) -> MlxModelPreset | None:
    for preset_name, (configured_model, _, _) in MLX_MODEL_PRESETS.items():
        if configured_model == model_id:
            return preset_name
    return None


def _parse_model_preset(raw: str) -> MlxModelPreset:
    value = raw.strip().lower()
    allowed = set(MLX_MODEL_PRESETS.keys())
    if value not in allowed:
        allowed_values = ", ".join(sorted(allowed))
        raise ConfigError(f"TTS_MCP_MLX_MODEL_PRESET must be one of: {allowed_values}.")
    return value  # type: ignore[return-value]


def _parse_backend(raw: str) -> BackendName:
    value = raw.strip().lower()
    allowed = {"auto", "mlx_audio", "llama_cpp", "kokoro_onnx", "xtts", "chatterbox"}
    if value not in allowed:
        raise ConfigError(
            "TTS_MCP_BACKEND must be one of: auto, mlx_audio, llama_cpp, "
            "kokoro_onnx, xtts, chatterbox."
        )
    return value  # type: ignore[return-value]


def _parse_linux_runtime(raw: str) -> LinuxRuntimeName:
    value = raw.strip().lower()
    allowed = {"llama_cpp", "kokoro_onnx"}
    if value not in allowed:
        raise ConfigError(
            "TTS_MCP_LINUX_RUNTIME must be one of: llama_cpp, kokoro_onnx."
        )
    return value  # type: ignore[return-value]


def _parse_linux_player(raw: str) -> Literal["auto", "ffplay", "aplay", "paplay", "none"]:
    value = raw.strip().lower()
    allowed = {"auto", "ffplay", "aplay", "paplay", "none"}
    if value not in allowed:
        raise ConfigError(
            "TTS_MCP_LINUX_PLAYER must be one of: auto, ffplay, aplay, paplay, none."
        )
    return value  # type: ignore[return-value]


def _parse_hf_hub_offline_mode(raw: str) -> HfHubOfflineMode:
    value = raw.strip().lower()
    allowed = {"auto", "true", "false"}
    if value not in allowed:
        raise ConfigError(
            "TTS_MCP_HF_HUB_OFFLINE_MODE must be one of: auto, true, false."
        )
    return value  # type: ignore[return-value]


def _parse_torch_device(raw: str) -> TorchDevice:
    value = raw.strip().lower()
    allowed = {"auto", "cpu", "cuda", "mps"}
    if value not in allowed:
        raise ConfigError("Torch device must be one of: auto, cpu, cuda, mps.")
    return value  # type: ignore[return-value]


def _parse_positive_int(raw: str, field_name: str) -> int:
    value = _parse_int(raw, field_name)
    if value <= 0:
        raise ConfigError(f"{field_name} must be greater than zero.")
    return value


def _parse_positive_float(raw: str, field_name: str) -> float:
    try:
        value = float(raw)
    except ValueError as exc:
        raise ConfigError(f"{field_name} must be a number.") from exc
    if value <= 0:
        raise ConfigError(f"{field_name} must be greater than zero.")
    return value


def _parse_non_negative_float(raw: str, field_name: str) -> float:
    try:
        value = float(raw)
    except ValueError as exc:
        raise ConfigError(f"{field_name} must be a number.") from exc
    if value < 0:
        raise ConfigError(f"{field_name} must be greater than or equal to zero.")
    return value


def _parse_int(raw: str, field_name: str) -> int:
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigError(f"{field_name} must be an integer.") from exc


def _parse_bool(raw: str, field_name: str) -> bool:
    value = raw.strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    raise ConfigError(f"{field_name} must be a boolean string (true/false).")


def _optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned if cleaned else None


def _require_non_empty(env: Mapping[str, str], key: str, default: str | None = None) -> str:
    if default is not None:
        value = env.get(key, default)
    else:
        value = env.get(key, "")
    cleaned = value.strip()
    if not cleaned:
        raise ConfigError(f"{key} is required and must be non-empty.")
    return cleaned
