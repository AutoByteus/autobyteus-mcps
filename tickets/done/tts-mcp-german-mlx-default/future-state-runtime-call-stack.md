Status: Current

# Future-State Runtime Call Stack

## Use Case

Generate German speech on Apple Silicon macOS by setting `MLX_TTS_DEFAULT_LANG_CODE=de` in MCP config and calling `speak`.

## Call Stack

1. MCP host starts `tts-mcp.server`.
2. `tts_mcp.config.load_settings(...)` reads MCP env.
3. If `MLX_TTS_DEFAULT_LANG_CODE` resolves to German and no explicit MLX model override is present, `config.py` selects:
   - preset `german_orpheus_hq`
   - model `mlx-community/3b-de-ft-research_release-bf16`
4. User invokes `speak(text=..., play=false)`.
5. `tts_mcp.runner.run_speak(...)` selects the `mlx_audio` backend on Apple Silicon.
6. `runner._build_mlx_command(...)` resolves `--lang_code de`.
7. `mlx_audio.tts.generate` runs with the German model.
8. If the model is not cached yet, `mlx-audio` downloads it from Hugging Face during first use.
9. WAV output is written and returned as a successful `speak` result.

## Non-German Default Path

1. MCP host starts `tts-mcp.server` without German MLX language config.
2. `load_settings(...)` retains the default English preset.
3. `speak(...)` uses the English-oriented MLX model path unchanged.
