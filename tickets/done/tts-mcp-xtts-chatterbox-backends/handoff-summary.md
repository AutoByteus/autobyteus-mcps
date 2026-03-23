# Handoff Summary

## Status

- Ticket: `tts-mcp-xtts-chatterbox-backends`
- Stage: `10`
- Handoff Status: `Complete / Merged To Main`
- Last Updated: `2026-03-23`

## What Changed

- Added explicit support for:
  - `xtts`
  - `chatterbox`
- Preserved:
  - the minimal MCP `speak` API
  - existing `auto` backend routing
  - existing MLX / Kokoro / llama behavior
- Resolved the Stage 8 architecture failure by splitting the runner area into:
  - `tts-mcp/src/tts_mcp/backend_contracts.py`
  - `tts-mcp/src/tts_mcp/backend_commands.py`
  - `tts-mcp/src/tts_mcp/kokoro_runtime.py`
  - `tts-mcp/src/tts_mcp/execution_support.py`
  - with `tts-mcp/src/tts_mcp/runner.py` reduced to orchestration
- Resolved the later Stage 8 package-boundary failure by:
  - preflighting XTTS's required `XTTS_DEFAULT_SPEAKER_WAV`
  - centralizing checkout-vs-packaged runtime path resolution in `tts-mcp/src/tts_mcp/runtime_paths.py`
  - shipping wrapper and installer assets inside `tts-mcp/src/tts_mcp/runtime_assets/`
  - turning repo-root `scripts/` into thin source-checkout shims

## Validation Summary

- Post-refactor compilation passed.
- Post-refactor targeted test suite passed:
  - `tests/test_server.py`
  - `tests/test_runner.py`
  - `tests/test_platform.py`
  - `tests/test_config.py`
  - `tests/test_runtime_bootstrap.py`
  - `tests/test_runtime_paths.py`
  - `tests/test_version_check.py`
- Post-refactor real-smoke harness still collects cleanly:
  - `tests/test_real_mlx_smoke.py`
  - `tests/test_real_kokoro_smoke.py`
  - `tests/test_real_xtts_smoke.py`
  - `tests/test_real_chatterbox_smoke.py`
- Package-boundary validation passed:
  - built wheel contains `tts_mcp/runtime_assets/*`
  - installed-wheel smoke in a fresh Python 3.11 virtualenv resolves packaged wrapper and installer assets from `site-packages`
- Earlier real backend outputs remain available for listening:
  - `tts-mcp/real_smoke_outputs/german_mlx_audio_orpheus.wav`
  - `tts-mcp/real_smoke_outputs/german_chatterbox_multilingual_pcm.wav`
  - `tts-mcp/real_smoke_outputs/german_xtts_v2.wav`

## User-Facing Impact

- No additional docs changes were needed in this refactor cycle.
- Existing README guidance for XTTS and Chatterbox remains current.

## Residual Notes

- XTTS still depends on a configured speaker reference WAV for good quality.
- German Orpheus MLX remains the preferred German-quality path based on the generated samples.
- The latest review found no new code-review findings; remaining risk is limited to heavyweight runtime behavior that was not re-executed from inside the temporary wheel-smoke environment.

## Release Notes Decision

- Release notes required: `No`
- Rationale:
  - You explicitly requested a direct merge to `main`, not a separate versioned release.
  - This repository does not expose a project release script that must be run for this ticket closure path.

## Waiting On

- Nothing for this ticket. The archived ticket branch was merged and pushed directly to `main`.
