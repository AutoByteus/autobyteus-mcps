# Implementation Progress

## Status

- Ticket: `tts-mcp-xtts-chatterbox-backends`
- Stage: `6`
- Progress Status: `Complete`
- Last Updated: `2026-03-23`

## Current Cycle

- Cycle type: `Stage 8 local-fix re-entry`
- Goal:
  - preserve the split-owner architecture
  - harden XTTS preflight validation
  - remove packaged-install dependence on repo-root script paths

## Checklist

| Item | Status | Notes |
| --- | --- | --- |
| Local-fix implementation artifacts refreshed | Complete | Stage 8 findings are translated into a concrete Stage 6 plan. |
| Stage 6 unlock for local-fix cycle | Complete | Workflow-state unlocked code edits for the package-boundary hardening cycle. |
| Add XTTS preflight validation | Complete | XTTS now fails fast when `XTTS_DEFAULT_SPEAKER_WAV` is missing or points to a nonexistent file. |
| Add runtime script/path resolver | Complete | `runtime_paths.py` now resolves runtime root plus wrapper/installer scripts from either a source checkout or packaged assets. |
| Package runtime wrapper and installer assets | Complete | Canonical runtime assets now ship under `src/tts_mcp/runtime_assets/`, and root `scripts/` files are checkout-only shims. |
| Re-run tests, wheel build, and review gates | Complete | Targeted suites passed, smoke harness still collects cleanly, and the rebuilt wheel now includes the required runtime assets. |

## Work Log

| Date | Entry |
| --- | --- |
| 2026-03-16 | Initialized Stage 6 implementation tracking after Stage 5 runtime review reached `Go Confirmed`. |
| 2026-03-16 | Implemented explicit `xtts` and `chatterbox` backends across config, selection, runtime bootstrap, version checks, runner command construction, wrapper scripts, and docs. |
| 2026-03-16 | Fixed XTTS installer issues discovered during real validation: explicit Python 3.10+ resolution, explicit `torch`/`torchaudio` install, `transformers<5` compatibility pin, and `coqui-tts[codec]` for `torchcodec`. |
| 2026-03-16 | Re-entered Stage 6 for a local fix to split real smoke coverage into backend-specific files and improve hearable validation organization. |
| 2026-03-16 | Split the real smoke suite into dedicated backend files for MLX, Kokoro, XTTS, and Chatterbox, plus a shared helper module for runtime gating. |
| 2026-03-16 | Re-entered Stage 6 again for a Chatterbox runtime compatibility fix after the multilingual backend failed when `perth.PerthImplicitWatermarker` was unavailable on this host. |
| 2026-03-16 | Patched the Chatterbox wrapper to fall back to Perth's dummy watermarker when the implicit implementation is unavailable, then reran German generation successfully. |
| 2026-03-16 | Re-entered Stage 6 again for an XTTS local fix to wire Coqui TOS acceptance through MCP config/runtime instead of relying on out-of-band shell environment. |
| 2026-03-16 | Added `XTTS_COQUI_TOS_AGREED` to `tts-mcp` config/runtime, propagated it to the XTTS subprocess as `COQUI_TOS_AGREED=1`, and improved the XTTS error path to report the real terms-acceptance blocker. |
| 2026-03-23 | User manually accepted the Coqui XTTS terms and completed a real XTTS German generation using `outputs/jana_probe.wav` as the configured speaker reference. |
| 2026-03-23 | Generated longer comparison samples for the German Orpheus voices `jana`, `thomas`, and `max` to confirm the preferred German path remains the MLX Orpheus backend. |
| 2026-03-23 | Stage 8 failed on architecture quality because `runner.py` absorbed too many owners; the ticket re-entered Stage 1 -> 5 and the redesign targeted a split runner area before resuming code changes. |
| 2026-03-23 | Refactored the runner area into explicit owners: `backend_contracts.py`, `backend_commands.py`, `kokoro_runtime.py`, and `execution_support.py`, then reduced `runner.py` to orchestration and result shaping. |
| 2026-03-23 | Realigned `tests/test_runner.py` to the new owners and reran the targeted post-refactor validation suites successfully. |
| 2026-03-23 | Stage 8 failed again on local-fix findings: XTTS does not preflight its required speaker reference, and explicit backend/bootstrap script resolution still assumes a source checkout. |
| 2026-03-23 | Refreshed the Stage 6 plan for a package-boundary hardening cycle covering XTTS validation, packaged runtime assets, and checkout-independent script resolution. |
| 2026-03-23 | Added `runtime_paths.py`, resolved XTTS and Chatterbox wrapper paths through checkout-or-package asset lookup, and normalized runtime-owned command paths against the resolved runtime root. |
| 2026-03-23 | Added packaged runtime assets under `src/tts_mcp/runtime_assets/` and converted root `scripts/` entrypoints into thin source-checkout shims. |
| 2026-03-23 | Hardened XTTS preflight validation so missing or nonexistent `XTTS_DEFAULT_SPEAKER_WAV` now fails as a config error before subprocess launch. |
| 2026-03-23 | Rebuilt the wheel and confirmed the shipped artifact now contains the runtime wrappers, installer scripts, and the new runtime-path helper. |

## Verification Log

| Date | Command / Check | Result | Notes |
| --- | --- | --- | --- |
| 2026-03-16 | `uv --directory tts-mcp run python -m pytest -q tests/test_config.py tests/test_platform.py tests/test_runtime_bootstrap.py tests/test_runner.py tests/test_version_check.py` | Pass | Baseline targeted unit suite for the backend-addition work. |
| 2026-03-16 | `uv run python -m py_compile src/tts_mcp/*.py scripts/xtts_generate.py scripts/chatterbox_generate.py` | Pass | Baseline compile check for the current implementation. |
| 2026-03-16 | `./scripts/install_xtts_runtime.sh` | Pass | Installed isolated XTTS runtime at `.venv-xtts`. |
| 2026-03-16 | `./scripts/install_chatterbox_runtime.sh` | Pass | Installed isolated Chatterbox runtime at `.venv-chatterbox`. |
| 2026-03-16 | `.venv-chatterbox/bin/python scripts/chatterbox_generate.py ...` | Pass | German Chatterbox generation completed after the dummy-watermarker fallback. |
| 2026-03-16 | `uv --directory tts-mcp run python -m pytest -q tests/test_real_mlx_smoke.py tests/test_real_kokoro_smoke.py tests/test_real_xtts_smoke.py tests/test_real_chatterbox_smoke.py` | Pass | Backend-specific real smoke files collect cleanly and skip by default when opt-in env gates are unset. |
| 2026-03-16 | `.venv-mlx/bin/mlx_audio.tts.generate ... --file_prefix real_smoke_outputs/german_mlx_audio_orpheus` | Pass | Generated a hearable German MLX sample at `real_smoke_outputs/german_mlx_audio_orpheus.wav`. |
| 2026-03-16 | `uv --directory tts-mcp run python -m pytest -q tests/test_config.py tests/test_runner.py tests/test_real_xtts_smoke.py` | Pass | XTTS config/runtime acceptance wiring and smoke-test gating passed. |
| 2026-03-23 | `COQUI_TOS_AGREED=1 ./.venv-xtts/bin/python scripts/xtts_generate.py --text ... --output-path real_smoke_outputs/german_xtts_v2.wav --model-name tts_models/multilingual/multi-dataset/xtts_v2 --language de --speaker-wav outputs/jana_probe.wav --device cpu` | Pass | XTTS generated a valid German WAV after explicit user acceptance of Coqui's terms. |
| 2026-03-23 | `.venv-mlx/bin/mlx_audio.tts.generate ... --voice jana/thomas/max --file_prefix real_smoke_outputs/german_<voice>_long_orpheus` | Pass | Generated long Orpheus comparison WAVs for `jana`, `thomas`, and `max`. |
| 2026-03-23 | `uv --directory tts-mcp run python -m py_compile src/tts_mcp/config.py src/tts_mcp/platform.py src/tts_mcp/runtime_bootstrap.py src/tts_mcp/version_check.py src/tts_mcp/backend_contracts.py src/tts_mcp/backend_commands.py src/tts_mcp/kokoro_runtime.py src/tts_mcp/execution_support.py src/tts_mcp/runner.py` | Pass | Post-refactor source compilation passed for the split runner area and adjacent package files. |
| 2026-03-23 | `uv --directory tts-mcp run python -m pytest -q tests/test_server.py tests/test_runner.py tests/test_platform.py tests/test_config.py tests/test_runtime_bootstrap.py tests/test_version_check.py` | Pass | Post-refactor targeted unit/integration suite passed after the ownership split. |
| 2026-03-23 | `uv --directory tts-mcp run python -m pytest -q tests/test_real_mlx_smoke.py tests/test_real_kokoro_smoke.py tests/test_real_xtts_smoke.py tests/test_real_chatterbox_smoke.py` | Pass | Post-refactor real-smoke harness still collects cleanly under its opt-in gates. |
| 2026-03-23 | `uv --directory tts-mcp run python -m py_compile scripts/xtts_generate.py scripts/chatterbox_generate.py src/tts_mcp/config.py src/tts_mcp/backend_commands.py src/tts_mcp/runtime_bootstrap.py src/tts_mcp/runtime_paths.py src/tts_mcp/runtime_assets/xtts_generate.py src/tts_mcp/runtime_assets/chatterbox_generate.py` | Pass | Local-fix compile check passed for the new runtime-path helper, packaged assets, and source-checkout shims. |
| 2026-03-23 | `bash -n scripts/install_*.sh src/tts_mcp/runtime_assets/install_*.sh` | Pass | Both the packaged installer assets and the source-checkout shim scripts parse cleanly. |
| 2026-03-23 | `uv --directory tts-mcp run python -m pytest -q tests/test_server.py tests/test_config.py tests/test_runner.py tests/test_runtime_bootstrap.py tests/test_platform.py tests/test_version_check.py tests/test_runtime_paths.py` | Pass | Local-fix targeted suite passed, including new XTTS preflight and runtime-path tests. |
| 2026-03-23 | `uv --directory tts-mcp run python -m pytest -q tests/test_real_mlx_smoke.py tests/test_real_kokoro_smoke.py tests/test_real_xtts_smoke.py tests/test_real_chatterbox_smoke.py` | Pass | Real smoke harness still collects cleanly behind opt-in gates after the package-boundary fix. |
| 2026-03-23 | `uv --directory tts-mcp build --wheel` and `unzip -l dist/tts_mcp-0.1.0-py3-none-any.whl` | Pass | The rebuilt wheel now includes `tts_mcp/runtime_assets/*`, closing the packaged-install script gap found in Stage 8. |

## Risks / Open Points

- XTTS still needs a real speaker reference for output quality; this cycle hardens validation and execution behavior, not cloning quality itself.
- Packaged-install behavior is now covered structurally and by wheel contents, but a true wheel-installed end-to-end runtime smoke test still does not exist.
