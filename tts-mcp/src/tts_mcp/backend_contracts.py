from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import subprocess

from .config import BackendName, TtsSettings
from .execution_support import ExecutionResult


_KOKORO_LANGUAGE_ALIASES: dict[str, str] = {
    "zh": "cmn",
    "zh-cn": "cmn",
    "zh-hans": "cmn",
    "zh_cn": "cmn",
    "zh_hans": "cmn",
    "mandarin": "cmn",
}
_MLX_LANGUAGE_ALIASES: dict[str, str] = {
    "de-de": "de",
    "de_de": "de",
    "german": "de",
    "deutsch": "de",
    "en-us": "en",
    "en_us": "en",
    "english": "en",
}
_XTTS_LANGUAGE_ALIASES: dict[str, str] = {
    "de-de": "de",
    "de_de": "de",
    "german": "de",
    "deutsch": "de",
    "en-us": "en",
    "en_us": "en",
    "english": "en",
    "zh": "zh-cn",
    "zh_cn": "zh-cn",
    "zh-cn": "zh-cn",
    "zh_hans": "zh-cn",
    "zh-hans": "zh-cn",
    "mandarin": "zh-cn",
    "chinese": "zh-cn",
}
_CHATTERBOX_LANGUAGE_ALIASES: dict[str, str] = {
    "de-de": "de",
    "de_de": "de",
    "german": "de",
    "deutsch": "de",
    "en-us": "en",
    "en_us": "en",
    "english": "en",
    "zh-cn": "zh",
    "zh_cn": "zh",
    "zh_hans": "zh",
    "zh-hans": "zh",
    "mandarin": "zh",
    "chinese": "zh",
}


def normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned if cleaned else None


def resolve_mlx_subprocess_env(settings: TtsSettings) -> dict[str, str] | None:
    mode = settings.hf_hub_offline_mode
    if mode == "true":
        return {"HF_HUB_OFFLINE": "1"}
    if mode == "false":
        return None
    if is_hf_model_cached(settings.mlx_model):
        return {"HF_HUB_OFFLINE": "1"}
    return None


def resolve_xtts_subprocess_env(settings: TtsSettings) -> dict[str, str] | None:
    if settings.xtts_coqui_tos_agreed:
        return {"COQUI_TOS_AGREED": "1"}
    return None


def classify_generation_failure(
    backend: BackendName,
    generation: ExecutionResult,
) -> tuple[str, str]:
    combined = f"{generation['stdout'] or ''}\n{generation['stderr'] or ''}"

    if backend == "xtts" and _looks_like_xtts_tos_failure(combined):
        return (
            "validation",
            "XTTS requires explicit Coqui terms acceptance before first model download. "
            "After reviewing and accepting those terms, set XTTS_COQUI_TOS_AGREED=true "
            "for the MCP runtime and retry.",
        )

    return (
        generation["error_type"] or "execution",
        generation["error_message"] or "Speech command failed.",
    )


def mlx_playback_confirmed(generation: ExecutionResult) -> bool:
    combined = f"{generation['stdout'] or ''}\n{generation['stderr'] or ''}".lower()
    markers = (
        "starting audio stream",
        "audio stream started",
    )
    return any(marker in combined for marker in markers)


def resolve_mlx_language_code(
    model_id: str,
    language_code: str | None,
    default_language_code: str,
) -> str:
    resolved = (language_code or default_language_code).strip()
    normalized = _MLX_LANGUAGE_ALIASES.get(resolved.lower(), resolved)
    if model_id == "mlx-community/Kokoro-82M-bf16" and normalized.lower() == "en":
        return "a"
    return normalized


def resolve_xtts_language_code(
    language_code: str | None,
    default_language_code: str,
) -> str:
    resolved = (language_code or default_language_code).strip()
    return _XTTS_LANGUAGE_ALIASES.get(resolved.lower(), resolved)


def resolve_chatterbox_language_code(
    language_code: str | None,
    default_language_code: str,
) -> str:
    resolved = (language_code or default_language_code).strip()
    return _CHATTERBOX_LANGUAGE_ALIASES.get(resolved.lower(), resolved)


def resolve_kokoro_language_code(
    language_code: str | None,
    default_language_code: str,
) -> str:
    resolved = (language_code or default_language_code).strip()
    normalized = resolved.lower().replace("_", "-")
    return _KOKORO_LANGUAGE_ALIASES.get(normalized, resolved)


@lru_cache(maxsize=32)
def is_hf_model_cached(model_id: str) -> bool:
    if not _looks_like_hf_repo_id(model_id):
        return False

    cache_root = Path.home() / ".cache" / "huggingface" / "hub"
    model_cache_dir = cache_root / f"models--{model_id.replace('/', '--')}"
    snapshots_dir = model_cache_dir / "snapshots"
    if not snapshots_dir.exists():
        return False

    try:
        return any(child.is_dir() for child in snapshots_dir.iterdir())
    except OSError:
        return False


@lru_cache(maxsize=8)
def mlx_supports_flag(command: str, flag: str) -> bool:
    try:
        completed = subprocess.run(
            [command, "-h"],
            capture_output=True,
            text=True,
            check=False,
            timeout=8,
        )
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        return False

    help_text = f"{completed.stdout}\n{completed.stderr}"
    return flag in help_text


def _looks_like_hf_repo_id(value: str) -> bool:
    if "://" in value:
        return False
    if value.startswith("/") or value.startswith("./") or value.startswith("../"):
        return False
    return value.count("/") == 1


def _looks_like_xtts_tos_failure(output: str) -> bool:
    normalized = output.lower()
    markers = (
        "i agree to the terms of the non-commercial cpml",
        "coqui_tos_agreed",
        "you must agree to the terms of service",
        "you must confirm the following",
    )
    return any(marker in normalized for marker in markers)
