Status: In Progress

# Investigation Notes

## Current `tts-mcp` Behavior

- `speak` is the existing MCP tool for text-to-speech conversion.
- The MLX default language remains English when `MLX_TTS_DEFAULT_LANG_CODE` is unset.
- German auto-selection is opt-in only:
  - when `MLX_TTS_DEFAULT_LANG_CODE` resolves to German such as `de` or `de-DE`,
  - and only when `TTS_MCP_MLX_MODEL_PRESET` and `MLX_TTS_MODEL` are not explicitly set.
- Explicit MLX preset or model settings continue to override the language-based default selection.

## Current Code Evidence

- MLX preset selection is handled in `tts-mcp/src/tts_mcp/config.py`.
- MLX language normalization is handled in `tts-mcp/src/tts_mcp/runner.py`.
- README now documents that German MLX selection is a config-driven opt-in path.

## Conclusion

The intended behavior described by the user is already the current implementation:
- English stays the default.
- German model selection only happens when the MCP config explicitly sets German as the default MLX language.
