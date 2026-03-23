# API / E2E Testing

## Status

- Ticket: `tts-mcp-xtts-chatterbox-backends`
- Stage: `7`
- Validation Status: `Pass`
- Last Updated: `2026-03-23`

## Testing Scope

- Scope classification: `Medium`
- Workflow state source: `tickets/done/tts-mcp-xtts-chatterbox-backends/workflow-state.md`
- Requirements source: `tickets/done/tts-mcp-xtts-chatterbox-backends/requirements.md`
- Call stack source: `tickets/done/tts-mcp-xtts-chatterbox-backends/future-state-runtime-call-stack.md`
- Design source: `tickets/done/tts-mcp-xtts-chatterbox-backends/proposed-design.md`

## Re-Entry Validation Note

- This Stage 7 pass was refreshed after the Stage 8 design-impact re-entry.
- The refactor changed ownership boundaries, not public behavior.
- New post-refactor regression evidence was added alongside the earlier real XTTS, Chatterbox, and MLX outputs.
- This Stage 7 pass is now refreshed again after the Stage 8 local-fix re-entry.
- The local-fix cycle changed XTTS preflight validation and the package-boundary runtime path/bootstrap behavior without changing the MCP `speak` signature.
- New wheel-content evidence and targeted runtime-path tests were added for the packaged-install boundary that previously failed code review.

## Acceptance Criteria Coverage Matrix

| Acceptance Criteria ID | Requirement ID | Criterion Summary | Scenario ID(s) | Current Status | Last Updated |
| --- | --- | --- | --- | --- | --- |
| AC-001 | R-001 | `TTS_MCP_BACKEND=xtts` reaches XTTS execution path through `speak` | `AV-001`, `AV-002`, `AV-008`, `AV-010`, `AV-011` | Passed | 2026-03-23 |
| AC-002 | R-001 | `TTS_MCP_BACKEND=chatterbox` reaches Chatterbox execution path through `speak` | `AV-003`, `AV-004`, `AV-008`, `AV-010`, `AV-011` | Passed | 2026-03-23 |
| AC-003 | R-001 | Existing `auto`, `mlx_audio`, `kokoro_onnx`, and `llama_cpp` behavior remains unchanged unless explicitly configured otherwise | `AV-005`, `AV-006`, `AV-008`, `AV-009`, `AV-010` | Passed | 2026-03-23 |
| AC-004 | R-001 | Unit and integration tests cover backend selection and runner command-building behavior | `AV-001`, `AV-003`, `AV-005`, `AV-008`, `AV-010` | Passed | 2026-03-23 |
| AC-005 | R-001 | Runtime bootstrap/version-check behavior for XTTS and Chatterbox is implemented or clearly documented | `AV-001`, `AV-003`, `AV-007`, `AV-010`, `AV-011` | Passed | 2026-03-23 |
| AC-006 | R-001 | `tts-mcp/README.md` documents how to install and configure XTTS and Chatterbox support | `AV-007` | Passed | 2026-03-23 |
| AC-007 | R-001 | Real local execution is validated on the current Apple Silicon host for any feasible backend or blockers are precisely recorded | `AV-002`, `AV-004`, `AV-006`, `AV-009` | Passed | 2026-03-23 |

## Spine Coverage Matrix

| Spine ID | Spine Scope | Governing Owner | Scenario ID(s) | Coverage Status | Notes |
| --- | --- | --- | --- | --- | --- |
| DS-001 | Primary End-to-End | `tts_mcp.runner.run_speak` XTTS explicit backend path | `AV-001`, `AV-002`, `AV-008`, `AV-010`, `AV-011` | Passed | Includes MCP-native terms acceptance wiring, XTTS preflight validation, real XTTS German generation, and packaged-wrapper wheel evidence. |
| DS-002 | Primary End-to-End | `tts_mcp.runner.run_speak` Chatterbox explicit backend path | `AV-003`, `AV-004`, `AV-008`, `AV-010`, `AV-011` | Passed | Includes real German generation after the watermarker compatibility fix, runtime-path regression validation, and packaged-wrapper wheel evidence. |
| DS-003 | Primary End-to-End | Existing `auto` backend routing path | `AV-005`, `AV-006`, `AV-008`, `AV-009`, `AV-010`, `AV-011` | Passed | Preserved Apple Silicon MLX auto behavior, retained real MLX evidence, and added packaged bootstrap asset coverage. |

## Scenario Catalog

| Scenario ID | Spine ID(s) | Source Type | Acceptance Criteria ID(s) | Requirement ID(s) | Use Case ID(s) | Level | Objective/Risk | Expected Outcome | Command/Harness | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AV-001 | DS-001 | Requirement | AC-001, AC-004, AC-005 | R-001 | UC-001 | API | Prove XTTS explicit backend selection, config parsing, runtime bootstrap, runner command construction, and version-check support | Targeted XTTS-related test coverage passes | `uv --directory tts-mcp run python -m pytest -q tests/test_config.py tests/test_platform.py tests/test_runtime_bootstrap.py tests/test_runner.py tests/test_version_check.py` and `uv --directory tts-mcp run python -m pytest -q tests/test_config.py tests/test_runner.py tests/test_real_xtts_smoke.py` | Passed |
| AV-002 | DS-001 | Requirement | AC-001, AC-007 | R-001 | UC-001 | E2E | Prove real XTTS German generation works on this host once the user accepts Coqui terms and provides a reference speaker clip | XTTS writes a valid German WAV file | `COQUI_TOS_AGREED=1 ./.venv-xtts/bin/python scripts/xtts_generate.py --text ... --output-path real_smoke_outputs/german_xtts_v2.wav --model-name tts_models/multilingual/multi-dataset/xtts_v2 --language de --speaker-wav outputs/jana_probe.wav --device cpu` | Passed |
| AV-003 | DS-002 | Requirement | AC-002, AC-004, AC-005 | R-001 | UC-002 | API | Prove Chatterbox explicit backend selection, config parsing, runtime bootstrap, runner command construction, and version-check support | Targeted Chatterbox-related coverage passes | `uv --directory tts-mcp run python -m pytest -q tests/test_config.py tests/test_platform.py tests/test_runtime_bootstrap.py tests/test_runner.py tests/test_version_check.py` | Passed |
| AV-004 | DS-002 | Requirement | AC-002, AC-007 | R-001 | UC-002 | E2E | Prove real Chatterbox German generation works on this host | Chatterbox writes a valid German WAV file | `.venv-chatterbox/bin/python scripts/chatterbox_generate.py ...` with output persisted at `tts-mcp/real_smoke_outputs/german_chatterbox_multilingual_pcm.wav` | Passed |
| AV-005 | DS-003 | Requirement | AC-003, AC-004 | R-001 | UC-003 | API | Prove explicit XTTS/Chatterbox support does not break existing backend selection and command building | Existing platform and runner suites continue to pass | `uv --directory tts-mcp run python -m pytest -q tests/test_config.py tests/test_platform.py tests/test_runtime_bootstrap.py tests/test_runner.py tests/test_version_check.py` | Passed |
| AV-006 | DS-003 | Requirement | AC-003, AC-007 | R-001 | UC-003 | E2E | Prove the existing Apple Silicon MLX path still produces good German output | MLX Orpheus writes a valid German WAV file | `.venv-mlx/bin/mlx_audio.tts.generate ... --file_prefix real_smoke_outputs/german_mlx_audio_orpheus` and persisted output at `tts-mcp/real_smoke_outputs/german_mlx_audio_orpheus.wav` | Passed |
| AV-007 | DS-001, DS-002 | Design-Risk | AC-005, AC-006 | R-001 | UC-001, UC-002 | API | Prove operator-facing guidance is present for runtime install and XTTS first-run acceptance | README documents backend install/config and the XTTS terms-acceptance workflow | `tts-mcp/README.md` review | Passed |
| AV-008 | DS-001, DS-002, DS-003 | Design-Risk | AC-001, AC-002, AC-003, AC-004 | R-001 | UC-001, UC-002, UC-003, UC-004 | API | Prove the post-refactor owner split preserved runner behavior across MCP boundary, command-backed backends, and Kokoro orchestration | Targeted post-refactor suite passes | `uv --directory tts-mcp run python -m pytest -q tests/test_server.py tests/test_runner.py tests/test_platform.py tests/test_config.py tests/test_runtime_bootstrap.py tests/test_version_check.py` | Passed |
| AV-009 | DS-003 | Design-Risk | AC-003, AC-007 | R-001 | UC-003, UC-004 | API | Prove the real-smoke harness still maps to the existing backend paths after the refactor | Backend-specific real smoke files still collect cleanly under opt-in gates | `uv --directory tts-mcp run python -m pytest -q tests/test_real_mlx_smoke.py tests/test_real_kokoro_smoke.py tests/test_real_xtts_smoke.py tests/test_real_chatterbox_smoke.py` | Passed |
| AV-010 | DS-001, DS-002, DS-003 | Design-Risk | AC-001, AC-002, AC-003, AC-004, AC-005 | R-001 | UC-001, UC-002, UC-003, UC-004 | API | Prove the local-fix build preserves behavior while adding XTTS preflight validation and checkout-independent runtime-path handling | Targeted local-fix suite passes | `uv --directory tts-mcp run python -m pytest -q tests/test_server.py tests/test_config.py tests/test_runner.py tests/test_runtime_bootstrap.py tests/test_platform.py tests/test_version_check.py tests/test_runtime_paths.py` | Passed |
| AV-011 | DS-001, DS-002, DS-003 | Design-Risk | AC-001, AC-002, AC-005 | R-001 | UC-001, UC-002, UC-003 | API | Prove a built wheel now ships the wrapper and installer assets required by explicit backends and runtime bootstrap | Wheel listing includes `tts_mcp/runtime_assets/*` | `uv --directory tts-mcp build --wheel` and `unzip -l dist/tts_mcp-0.1.0-py3-none-any.whl` | Passed |

## Failure Escalation Log

| Date | Scenario ID | Failure Summary | Investigation Required | Classification | Action Path | `investigation-notes.md` Updated | Requirements Updated | Design Updated | Call Stack Regenerated | Review Re-Entry Round | Resolved |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-03-16 | AV-002 | XTTS first-run model download was blocked by Coqui terms acceptance in non-interactive execution | No | Local Fix | `Stage 6 -> Stage 7` to add MCP-native terms-acceptance wiring, then rerun XTTS validation after user acceptance | No | No | No | No | N/A | Yes |
| 2026-03-16 | AV-004 | Chatterbox multilingual generation failed when `perth.PerthImplicitWatermarker` was unavailable on this host | No | Local Fix | `Stage 6 -> Stage 7` to add a dummy-watermarker fallback, then rerun real Chatterbox validation | No | No | No | No | N/A | Yes |

## Feasibility And Risk Record

- Any infeasible scenarios: `No`
- Environment constraints: XTTS required explicit user acceptance of Coqui's CPML/commercial-license gate before the first model download; that acceptance was provided manually on 2026-03-23.
- Compensating automated evidence: backend-specific real smoke tests collect cleanly behind opt-in env gates, the new runtime-path suite passes, and the built wheel now contains the packaged runtime assets required by explicit backends and auto-bootstrap.
- Residual risk notes: XTTS quality remains dependent on the quality of the configured reference speaker WAV; the validation here proves execution and packaging closure, not best-voice quality. A true wheel-installed end-to-end runtime smoke test still does not exist.
- User waiver for infeasible acceptance criteria recorded: `N/A`

## Stage 7 Gate Decision

- Stage 7 complete: `Yes`
- All in-scope acceptance criteria mapped to scenarios: `Yes`
- All relevant spines mapped to scenarios: `Yes`
- All executable in-scope acceptance criteria status = `Passed`: `Yes`
- All executable relevant spines status = `Passed`: `Yes`
- Critical executable scenarios passed: `Yes`
- Any infeasible acceptance criteria: `No`
- Explicit user waiver recorded for each infeasible acceptance criterion (if any): `N/A`
- Unresolved escalation items: `No`
- Ready to enter Stage 8 code review: `Yes`
- Notes:
  - Real German outputs now exist for XTTS, Chatterbox, and MLX Orpheus on this host.
  - XTTS requires a configured reference speaker WAV; execution is now verified after manual acceptance of Coqui's terms and use of `outputs/jana_probe.wav`.
  - The post-refactor regression suite passed, and the Stage 7 gate is now refreshed again from the local-fix package-boundary build rather than inherited from the earlier review-failure state.
