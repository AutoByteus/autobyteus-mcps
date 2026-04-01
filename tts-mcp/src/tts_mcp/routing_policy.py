from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .config import (
    DEFAULT_KOKORO_DEFAULT_VOICE,
    DEFAULT_KOKORO_MODEL_PATH,
    DEFAULT_KOKORO_VOICES_PATH,
    DEFAULT_KOKORO_ZH_DEFAULT_VOICE,
    DEFAULT_KOKORO_ZH_MODEL_PATH,
    DEFAULT_KOKORO_ZH_VOCAB_CONFIG_PATH,
    DEFAULT_KOKORO_ZH_VOICES_PATH,
    DEFAULT_MLX_CHINESE_MODEL_PRESET,
    DEFAULT_MLX_GERMAN_MODEL_PRESET,
    DEFAULT_MLX_MODEL_PRESET,
    MLX_MODEL_PRESETS,
    TtsSettings,
)
from .runtime_paths import resolve_runtime_file_path


_PUBLIC_LANGUAGE_ALIASES: dict[str, str] = {
    "de-de": "de",
    "de_de": "de",
    "german": "de",
    "deutsch": "de",
    "en-us": "en",
    "en_us": "en",
    "english": "en",
    "zh": "zh",
    "zh-cn": "zh",
    "zh-hans": "zh",
    "zh-hant": "zh",
    "zh_cn": "zh",
    "zh_hans": "zh",
    "zh_hant": "zh",
    "cmn": "zh",
    "mandarin": "zh",
    "chinese": "zh",
}

_MLX_LANGUAGE_ALIASES: dict[str, str] = {
    "de-de": "de",
    "de_de": "de",
    "german": "de",
    "deutsch": "de",
    "en-us": "en",
    "en_us": "en",
    "english": "en",
    "zh-cn": "zh",
    "zh-hans": "zh",
    "zh-hant": "zh",
    "zh_cn": "zh",
    "zh_hans": "zh",
    "zh_hant": "zh",
    "cmn": "zh",
    "mandarin": "zh",
    "chinese": "zh",
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

_KOKORO_LANGUAGE_ALIASES: dict[str, str] = {
    "zh": "cmn",
    "zh-cn": "cmn",
    "zh-hans": "cmn",
    "zh_cn": "cmn",
    "zh_hans": "cmn",
    "mandarin": "cmn",
}

ManagedKokoroProfile = Literal["v1_0", "zh_v1_1"]


@dataclass(frozen=True, slots=True)
class ResolvedMlxRequest:
    model_id: str
    language_code: str
    auto_model_selection_applied: bool


@dataclass(frozen=True, slots=True)
class ResolvedKokoroRequest:
    language_code: str
    model_path: str
    voices_path: str
    vocab_config_path: str | None
    selected_voice: str
    managed_profile: ManagedKokoroProfile | None
    uses_explicit_assets: bool
    auto_install_allowed: bool
    use_misaki_zh: bool


def normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned if cleaned else None


def canonicalize_public_language(value: str | None) -> str | None:
    normalized = _normalize_language_token(value)
    if normalized is None:
        return None
    return _PUBLIC_LANGUAGE_ALIASES.get(normalized, normalized)


def resolve_mlx_request(
    settings: TtsSettings,
    language_code: str | None,
) -> ResolvedMlxRequest:
    normalized_language = (
        canonicalize_public_language(language_code)
        or canonicalize_public_language(settings.mlx_default_language_code)
        or "en"
    )
    explicit_mlx_selection = settings.mlx_model_preset_explicit or settings.mlx_model_explicit

    if explicit_mlx_selection:
        model_id = settings.mlx_model
        auto_model_selection_applied = False
    elif normalized_language == "de":
        model_id = MLX_MODEL_PRESETS[DEFAULT_MLX_GERMAN_MODEL_PRESET][0]
        auto_model_selection_applied = True
    elif normalized_language == "zh":
        model_id = MLX_MODEL_PRESETS[DEFAULT_MLX_CHINESE_MODEL_PRESET][0]
        auto_model_selection_applied = True
    else:
        model_id = MLX_MODEL_PRESETS[DEFAULT_MLX_MODEL_PRESET][0]
        auto_model_selection_applied = True

    return ResolvedMlxRequest(
        model_id=model_id,
        language_code=resolve_mlx_language_code(
            model_id=model_id,
            language_code=normalized_language,
            default_language_code=settings.mlx_default_language_code,
        ),
        auto_model_selection_applied=auto_model_selection_applied,
    )


def resolve_mlx_language_code(
    model_id: str,
    language_code: str | None,
    default_language_code: str,
) -> str:
    resolved = normalize_optional_text(language_code) or default_language_code.strip()
    normalized = _MLX_LANGUAGE_ALIASES.get(resolved.lower(), resolved)
    if model_id == "mlx-community/Kokoro-82M-bf16" and normalized.lower() == "en":
        return "a"
    return normalized


def resolve_xtts_language_code(
    language_code: str | None,
    default_language_code: str,
) -> str:
    return _resolve_backend_language(language_code, default_language_code, _XTTS_LANGUAGE_ALIASES)


def resolve_chatterbox_language_code(
    language_code: str | None,
    default_language_code: str,
) -> str:
    return _resolve_backend_language(
        language_code,
        default_language_code,
        _CHATTERBOX_LANGUAGE_ALIASES,
    )


def resolve_kokoro_language_code(
    language_code: str | None,
    default_language_code: str,
) -> str:
    return _resolve_backend_language(
        language_code,
        default_language_code,
        _KOKORO_LANGUAGE_ALIASES,
    )


def resolve_kokoro_request(
    settings: TtsSettings,
    language_code: str | None,
    requested_voice: str | None,
) -> ResolvedKokoroRequest:
    selected_language = resolve_kokoro_language_code(
        language_code,
        settings.kokoro_default_language_code,
    )
    selected_voice = normalize_optional_text(requested_voice) or settings.kokoro_default_voice
    default_model_path = resolve_runtime_file_path(DEFAULT_KOKORO_MODEL_PATH)
    default_voices_path = resolve_runtime_file_path(DEFAULT_KOKORO_VOICES_PATH)
    zh_model_path = resolve_runtime_file_path(DEFAULT_KOKORO_ZH_MODEL_PATH)
    zh_voices_path = resolve_runtime_file_path(DEFAULT_KOKORO_ZH_VOICES_PATH)
    zh_vocab_config_path = resolve_runtime_file_path(DEFAULT_KOKORO_ZH_VOCAB_CONFIG_PATH)
    language_is_chinese = _is_kokoro_chinese(selected_language)
    uses_explicit_assets = _kokoro_asset_pins_are_explicit(settings)

    model_path = settings.kokoro_model_path
    voices_path = settings.kokoro_voices_path
    vocab_config_path = settings.kokoro_vocab_config_path
    managed_profile: ManagedKokoroProfile | None = None
    auto_install_allowed = False

    if uses_explicit_assets:
        matched_profile = _match_managed_kokoro_profile(
            model_path=model_path,
            voices_path=voices_path,
            vocab_config_path=vocab_config_path,
            default_model_path=default_model_path,
            default_voices_path=default_voices_path,
            zh_model_path=zh_model_path,
            zh_voices_path=zh_voices_path,
            zh_vocab_config_path=zh_vocab_config_path,
        )
        if matched_profile == "zh_v1_1" and vocab_config_path is None:
            vocab_config_path = zh_vocab_config_path
        managed_profile = matched_profile
    else:
        auto_install_allowed = True
        if language_is_chinese:
            model_path = zh_model_path
            voices_path = zh_voices_path
            vocab_config_path = zh_vocab_config_path
            managed_profile = "zh_v1_1"
        else:
            managed_profile = "v1_0"

    if (
        language_is_chinese
        and normalize_optional_text(requested_voice) is None
        and not settings.kokoro_default_voice_explicit
        and managed_profile == "zh_v1_1"
    ):
        selected_voice = DEFAULT_KOKORO_ZH_DEFAULT_VOICE

    use_misaki_zh = bool(vocab_config_path) and language_is_chinese
    return ResolvedKokoroRequest(
        language_code=selected_language,
        model_path=model_path,
        voices_path=voices_path,
        vocab_config_path=vocab_config_path,
        selected_voice=selected_voice,
        managed_profile=managed_profile,
        uses_explicit_assets=uses_explicit_assets,
        auto_install_allowed=auto_install_allowed,
        use_misaki_zh=use_misaki_zh,
    )


def _resolve_backend_language(
    language_code: str | None,
    default_language_code: str,
    aliases: dict[str, str],
) -> str:
    resolved = (language_code or default_language_code).strip()
    normalized = resolved.lower().replace("_", "-")
    return aliases.get(normalized, resolved)


def _normalize_language_token(value: str | None) -> str | None:
    cleaned = normalize_optional_text(value)
    if cleaned is None:
        return None
    return cleaned.lower().replace("_", "-")


def _is_kokoro_chinese(language_code: str) -> bool:
    return language_code.strip().lower().replace("_", "-") in {"cmn", "z"}


def _kokoro_asset_pins_are_explicit(settings: TtsSettings) -> bool:
    return any(
        (
            settings.kokoro_model_path_explicit,
            settings.kokoro_voices_path_explicit,
            settings.kokoro_vocab_config_path_explicit,
        )
    )


def _match_managed_kokoro_profile(
    *,
    model_path: str,
    voices_path: str,
    vocab_config_path: str | None,
    default_model_path: str,
    default_voices_path: str,
    zh_model_path: str,
    zh_voices_path: str,
    zh_vocab_config_path: str,
) -> ManagedKokoroProfile | None:
    if model_path == default_model_path and voices_path == default_voices_path and vocab_config_path is None:
        return "v1_0"
    if model_path == zh_model_path and voices_path == zh_voices_path:
        if vocab_config_path is None or vocab_config_path == zh_vocab_config_path:
            return "zh_v1_1"
    return None
