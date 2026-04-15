from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import Context, FastMCP
from pydantic import Field

from .config import ServerConfig, TtsSettings, load_settings
from .routing_policy import canonicalize_public_language
from .runner import run_speak

_PUBLIC_LANGUAGE_DESCRIPTION = (
    "Optional language hint for routing. Leave unset to use the backend default. "
    "Prefer canonical values `zh` (Chinese), `en` (English), or `de` (German). "
    "Chinese aliases such as `zh-cn`, `zh_hans`, `cmn`, `mandarin`, and `chinese` "
    "normalize to `zh`; `en-us` and `english` normalize to `en`; `de-de`, "
    "`german`, and `deutsch` normalize to `de`."
)

_PUBLIC_LANGUAGE_EXAMPLES = ["zh", "zh-cn", "en", "de"]

_PUBLIC_VOICE_DESCRIPTION = (
    "Optional named voice selection. Leave unset to use the backend default voice. "
    "On the default English/Kokoro route, tested examples include `af_heart`. "
    "On speaker-capable Chinese/Qwen CustomVoice routes, tested examples on the "
    "installed runtime include `Vivian`, `eric`, and `serena`. Backend support is "
    "not uniform: MLX supports "
    "named voices, while "
    "some backends such as XTTS and Chatterbox may reject named voice selection "
    "through this MCP surface."
)

_PUBLIC_VOICE_EXAMPLES = ["af_heart", "Vivian", "eric", "serena"]

_PUBLIC_TEMPERATURE_DESCRIPTION = (
    "Optional MLX sampling temperature. Leave unset to use the MCP default `0.0` "
    "for deterministic MLX speech. Higher values allow more variation. "
    "Temperature is currently supported only on MLX routes."
)

_PUBLIC_TEMPERATURE_EXAMPLES = [0.0, 0.4]


def create_server(
    settings: TtsSettings | None = None,
    server_config: ServerConfig | None = None,
) -> FastMCP:
    resolved_settings = settings or load_settings()
    resolved_server_config = server_config or ServerConfig.from_env()

    server = FastMCP(
        name=resolved_server_config.name,
        instructions=resolved_server_config.instructions,
    )

    @server.tool(
        name="speak",
        title="Text to speech",
        description=(
            "Speak input text by auto-selecting MLX Audio on Apple Silicon macOS "
            "or Linux runtime policy backend (llama.cpp or Kokoro ONNX), with "
            "explicit XTTS and Chatterbox backends available through MCP config. "
            "Optional language input lets callers steer language-aware routing; "
            "for Chinese, use `zh`. Optional voice can request route-compatible "
            "speakers such as English/Kokoro `af_heart` or speaker-capable "
            "Chinese/Qwen CustomVoice `Vivian`. Optional temperature can override "
            "the deterministic MLX default `0.0`."
        ),
        structured_output=True,
    )
    async def speak(
        text: str,
        output_path: str | None = None,
        play: bool = True,
        language: Annotated[
            str | None,
            Field(
                description=_PUBLIC_LANGUAGE_DESCRIPTION,
                examples=_PUBLIC_LANGUAGE_EXAMPLES,
            ),
        ] = None,
        voice: Annotated[
            str | None,
            Field(
                description=_PUBLIC_VOICE_DESCRIPTION,
                examples=_PUBLIC_VOICE_EXAMPLES,
            ),
        ] = None,
        temperature: Annotated[
            float | None,
            Field(
                description=_PUBLIC_TEMPERATURE_DESCRIPTION,
                examples=_PUBLIC_TEMPERATURE_EXAMPLES,
                ge=0.0,
            ),
        ] = None,
        *,
        context: Context | None = None,
    ) -> dict[str, object]:
        if context is not None:
            await context.report_progress(0, 1, "Preparing speech generation")
        effective_language = canonicalize_public_language(language)

        run_kwargs: dict[str, object] = {
            "settings": resolved_settings,
            "text": text,
            "output_path": output_path,
            "play": play,
            "speed": resolved_settings.default_speed,
        }
        if effective_language is not None:
            run_kwargs["language_code"] = effective_language
        if voice is not None:
            run_kwargs["voice"] = voice
        if temperature is not None:
            run_kwargs["temperature"] = temperature

        result = run_speak(**run_kwargs)

        if context is not None:
            await context.report_progress(1, 1, "Speech generation completed")

        if result["ok"]:
            if play and not result["played"]:
                warning = "; ".join(result["warnings"]).strip()
                reason = "Speech generated but playback did not complete."
                if warning:
                    reason = f"{reason} {warning}"
                return {"ok": False, "reason": reason}
            return {"ok": True}
        reason = (result.get("error_message") or "").strip() or "Speech generation failed."
        return {"ok": False, "reason": reason}

    return server


def main() -> None:
    from .app_runtime import main as app_runtime_main

    app_runtime_main()


if __name__ == "__main__":
    main()
