# Handoff Summary

## Summary Meta

- Ticket: `tts-mcp-macos-qwen3-zh-auto-routing`
- Date: `2026-04-01`
- Current Status: `Verified`
- Workflow State Source: `tickets/done/tts-mcp-macos-qwen3-zh-auto-routing/workflow-state.md`

## Delivery Summary

- Delivered scope:
  - preserved the public `tts-mcp` `speak(text, output_path=None, play=True, language_code=None)` surface with one canonical language field
  - kept Apple Silicon `auto` routing on MLX and preserved the Chinese Qwen route when MLX model selection is not explicitly pinned
  - replaced the old startup-only Kokoro bootstrap path with `runtime_installation.py`, which now owns startup preparation and request-time managed-profile readiness
  - added explicit Kokoro override metadata in `config.py` so explicit model and asset pins are represented directly instead of being inferred from path equality
  - refactored runtime policy ownership so MLX routing, Kokoro managed-profile versus explicit-pin resolution, and XTTS or Chatterbox language normalization live in `routing_policy.py`
  - simplified `kokoro_runtime.py` so it only synthesizes from an already-resolved, runtime-ready request
  - repaired the real English public MCP test setup in `tests/test_real_mcp_speak_tool.py` so it resolves and injects `MLX_TTS_COMMAND`, matching the working Chinese public MCP test setup on this Mac
- Planned scope reference:
  - `tickets/done/tts-mcp-macos-qwen3-zh-auto-routing/requirements.md`
- Deferred / not delivered:
  - no new backend families were added beyond the existing supported matrix
  - no real Linux or Intel-mac Kokoro executable rerun was performed from this Darwin arm64 host
- Key architectural or ownership changes:
  - executable startup assembly moved to `app_runtime.py`
  - runtime routing policy is centralized in `routing_policy.py`
  - backend path semantics are centralized in `runtime_paths.py`
  - runtime installation and managed-profile readiness are centralized in `runtime_installation.py`
- Removed / decommissioned items:
  - obsolete `runtime_bootstrap.py`
  - obsolete `tests/test_runtime_bootstrap.py`

## Verification Summary

- Unit / integration verification:
  - `uv --directory tts-mcp run python -m pytest -q tests/test_app_runtime.py tests/test_config.py tests/test_runtime_installation.py tests/test_runner.py`
  - `uv --directory tts-mcp run python -m pytest -q tests/test_platform.py`
  - `uv --directory tts-mcp run python -m pytest -q tests/test_server.py`
- API / E2E verification:
  - `TTS_MCP_RUN_REAL_MCP_SPEAK=1 MLX_TTS_COMMAND=/Users/normy/autobyteus_org/autobyteus_mcps/tts-mcp/.venv-mlx/bin/mlx_audio.tts.generate uv --directory tts-mcp run python -m pytest -q tests/test_real_mcp_speak_tool_chinese_qwen.py`
  - `TTS_MCP_RUN_REAL_MCP_SPEAK=1 MLX_TTS_COMMAND=/Users/normy/autobyteus_org/autobyteus_mcps/tts-mcp/.venv-mlx/bin/mlx_audio.tts.generate uv --directory tts-mcp run python -m pytest -q tests/test_real_mcp_speak_tool.py tests/test_real_mcp_speak_tool_chinese_qwen.py`
- Acceptance-criteria closure summary:
  - Apple Silicon public `speak` now supports per-call `language_code`
  - Apple Silicon Chinese requests route to MLX Qwen when MLX model selection is not explicitly pinned
  - environment-default language behavior remains supported
  - English and Chinese real public MCP checks both pass on this host
- Infeasible criteria / user waivers (if any):
  - none
- Residual risk:
  - the Kokoro contract change is covered by focused routing and runtime-installation tests, but a real Linux or Intel-mac Kokoro executable rerun was not performed from this host

## Documentation Sync Summary

- Docs sync artifact:
  - `tickets/done/tts-mcp-macos-qwen3-zh-auto-routing/docs-sync.md`
- Docs result: `Updated`
- Docs updated:
  - `tts-mcp/README.md`
- Notes:
  - the README now documents request-time Kokoro managed-profile readiness, authoritative explicit Kokoro pins, and preserved runtime-root-relative backend path behavior

## Release Notes Status

- Release notes required: `No`
- Release notes artifact:
  - `Not required`
- Notes:
  - release/publication/deployment is not required for this ticket

## User Verification Hold

- Waiting for explicit user verification: `No`
- User verification received:
  - `2026-04-01`: user said the ticket is done and asked to proceed with finalization
- Notes:
  - Stage 10 repository finalization started after the explicit completion signal

## Finalization Record

- Ticket archived to:
  - `tickets/done/tts-mcp-macos-qwen3-zh-auto-routing`
- Ticket worktree path:
  - `/Users/normy/autobyteus_org/autobyteus_mcps__tts-mcp-macos-qwen3-zh-auto-routing`
- Ticket branch:
  - `codex/tts-mcp-macos-qwen3-zh-auto-routing`
- Finalization target remote:
  - `origin`
- Finalization target branch:
  - `main`
- Commit status:
  - `In progress`
- Push status:
  - `In progress`
- Merge status:
  - `In progress`
- Release/publication/deployment status:
  - `Not required`
- Worktree cleanup status:
  - `Pending repository finalization`
- Local branch cleanup status:
  - `Pending repository finalization`
- Blockers / notes:
  - none at handoff-record update time
