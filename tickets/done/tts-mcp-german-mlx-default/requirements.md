Status: Design-ready

# Requirements

## User Intent

Clarify and preserve the `tts-mcp` German MLX behavior so that English remains the default, and German model selection happens only when the MCP configuration explicitly sets the MLX default language to German (for example `MLX_TTS_DEFAULT_LANG_CODE=de`).

## Draft Requirements

- `speak` continues to exist as the MCP tool that converts text to speech audio.
- Default MLX behavior remains English-oriented when the user does not explicitly select German in MCP config.
- German MLX model selection is activated only when the configured default MLX language resolves to German such as `de` or `de-DE`.
- Explicit MLX model or preset selection in MCP config overrides language-based auto-selection.
- The first real German generation may download model weights through `mlx-audio`; subsequent runs should reuse cache.

## Acceptance Criteria

- With no German language configuration, the default MLX preset remains the English default.
- With `MLX_TTS_DEFAULT_LANG_CODE=de`, the German Orpheus MLX preset is selected automatically unless an explicit MLX preset/model is configured.
- Documentation states that English is still the default and German is opt-in via MCP config.
- A real local Apple Silicon MLX run with `MLX_TTS_DEFAULT_LANG_CODE=de` succeeds with `play=false` and produces a WAV file.

## Notes

- German model download is expected to happen on first real use through `mlx-audio`, not through a separate bootstrap installer.
- The handoff should explicitly state whether the first real run downloaded the German model or reused an existing cache.
