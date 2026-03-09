Status: Final
Scope: Small

# Implementation Plan

## Design Basis

- Keep English as the default MLX behavior.
- Add a German-first MLX preset for Apple Silicon.
- Auto-select the German preset only when `MLX_TTS_DEFAULT_LANG_CODE` resolves to German and no explicit MLX model or preset is configured.
- Normalize German language aliases for MLX command generation.
- Document that the first real German use downloads the model through `mlx-audio`.

## Validation Plan

- Unit tests for config-driven German preset selection.
- Unit tests for MLX German language normalization and command generation.
- One real local German `run_speak(play=false)` execution from source using the German config path.
