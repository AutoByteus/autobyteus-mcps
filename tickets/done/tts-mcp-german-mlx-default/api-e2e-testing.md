Status: Pass

# API / E2E Testing

## Executed Scenarios

1. Config selection check
   - `MLX_TTS_DEFAULT_LANG_CODE=de`
   - confirmed settings resolved to:
     - preset `german_orpheus_hq`
     - model `mlx-community/3b-de-ft-research_release-bf16`

2. Real local runtime direct execution
   - command: `mlx_audio.tts.generate --model mlx-community/3b-de-ft-research_release-bf16 --lang_code de ...`
   - result: first-use download completed and WAV file was generated at `/tmp/tts-mcp-german-orpheus-smoke.wav`

3. Real repo-level wrapper execution
   - command path: `tts_mcp.runner.run_speak(...)`
   - env path: `MLX_TTS_DEFAULT_LANG_CODE=de`
   - result: `ok=True`, no warnings, WAV file generated at `/tmp/tts-mcp-german-orpheus-run-speak.wav`

4. Real MCP tool execution
   - path: `tts_mcp.server.create_server(...)` + in-memory MCP client session
   - tool call: `speak(text=..., output_path=..., play=false)`
   - result: `structuredContent={"ok": True}`, WAV file generated at `/tmp/tts-mcp-german-mcp-tool/real_mcp_german.wav`

## Acceptance Criteria Mapping

- English remains default unless German is explicitly configured: covered by config/unit validation.
- German opt-in path selects German model automatically: covered by config/unit validation and real wrapper execution.
- First real use downloads model weights: covered by direct runtime execution.
- German WAV generation succeeds locally on Apple Silicon: covered by direct runtime execution and wrapper execution.
- The actual MCP `speak` tool succeeds with the German config path: covered by real tool execution.
