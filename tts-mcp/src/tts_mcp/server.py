from __future__ import annotations

from mcp.server.fastmcp import Context, FastMCP

from .config import ServerConfig, TtsSettings, load_settings
from .routing_policy import canonicalize_public_language
from .runner import run_speak


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
            "Optional language_code input lets callers steer language-aware routing."
        ),
        structured_output=True,
    )
    async def speak(
        text: str,
        output_path: str | None = None,
        play: bool = True,
        language_code: str | None = None,
        *,
        context: Context | None = None,
    ) -> dict[str, object]:
        if context is not None:
            await context.report_progress(0, 1, "Preparing speech generation")
        effective_language = canonicalize_public_language(language_code)

        run_kwargs: dict[str, object] = {
            "settings": resolved_settings,
            "text": text,
            "output_path": output_path,
            "play": play,
            "speed": resolved_settings.default_speed,
        }
        if effective_language is not None:
            run_kwargs["language_code"] = effective_language

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
