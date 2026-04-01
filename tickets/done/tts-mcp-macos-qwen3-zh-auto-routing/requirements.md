Status: Design-ready

# Requirements

## User Intent

Extend `tts-mcp` so the public `speak` MCP tool can accept a language hint and auto-route gracefully by platform and language. On Apple Silicon macOS, Chinese requests should use a Qwen3-TTS MLX path, while existing English-oriented defaults should keep working without extra per-call backend selection. The change should include a separate real test file for the Apple Silicon Chinese path.

## Refined Requirements

- `speak` remains the public MCP tool for text-to-speech generation and playback.
- `speak` accepts exactly one optional per-call language selector so callers can request Chinese without reconfiguring the server.
- The public tool should expose `language_code` as the only public language field.
- The public API should not expose a second alias field such as `language`; the surface should stay minimal and unambiguous.
- Backend selection remains automatic by default and continues to account for host platform.
- On Apple Silicon macOS, Chinese requests should auto-route to an MLX-backed Qwen3-TTS solution rather than the current default English-oriented MLX path.
- The Apple Silicon Chinese route should use the existing supported MLX preset `qwen_base_hq` unless the user explicitly overrides the MLX preset/model in MCP configuration.
- On Apple Silicon macOS, English requests should continue to use the current English-oriented MLX path and German requests should continue to use the existing German MLX path.
- Existing non-Chinese Apple Silicon behavior should remain compatible for English and existing default MLX flows.
- Existing Linux and Intel macOS behavior should remain intact unless language-aware routing explicitly requires a different supported backend.
- Explicit MLX configuration remains authoritative:
  - `TTS_MCP_MLX_MODEL_PRESET` and `MLX_TTS_MODEL` must still override automatic language-based model selection.
- Per-call language on Apple Silicon must affect the effective MLX model choice when explicit MLX overrides are not configured; server-startup defaults alone are insufficient.
- The implementation should add a separate real test file for the Apple Silicon Chinese MLX/Qwen path.
- Stage 7 executable validation must include an end-to-end public MCP `speak`-tool scenario for Apple Silicon Chinese, not only unit or runner-level coverage.
- Documentation should describe the new language-aware `speak` behavior and the Apple Silicon Chinese route.

## Acceptance Criteria

- The public `speak` MCP tool accepts `language_code` without breaking existing callers that omit it.
- `language_code` is forwarded into speech generation when supplied.
- The public MCP schema does not expose a second alias field for language intent.
- On Apple Silicon macOS with backend `auto` and without explicit MLX preset/model overrides:
  - English resolves to the current English MLX path.
  - German resolves to the existing German MLX path.
  - Chinese resolves to the Qwen3-TTS MLX path.
- On Apple Silicon macOS with `language_code=zh` or equivalent alias and without explicit MLX overrides, the generated MLX command uses the Qwen base model rather than the default Kokoro model.
- When `TTS_MCP_MLX_MODEL_PRESET` or `MLX_TTS_MODEL` is explicitly configured, that explicit MLX choice remains in effect even if the per-call language is Chinese.
- Existing Linux Kokoro Chinese behavior remains unchanged.
- A separate Apple Silicon real smoke test file exists for the Chinese MLX/Qwen path and exercises generation with `play=false`.
- Stage 7 validation evidence includes an end-to-end public MCP `speak`-tool execution for the Chinese Apple Silicon path.
- README documentation describes the new public arguments and the Apple Silicon Chinese Qwen route.

## Notes

- The implementation should prefer extending the existing MLX path over introducing a new backend for Apple Silicon Chinese.
- The initial Apple Silicon Chinese route should use the repo's already-supported Qwen3-TTS MLX model rather than expanding the supported-model matrix in the same change.
- Environment defaults remain valid:
  - if `language_code` is omitted, language continues to resolve from backend-specific MCP env defaults such as `MLX_TTS_DEFAULT_LANG_CODE`.
