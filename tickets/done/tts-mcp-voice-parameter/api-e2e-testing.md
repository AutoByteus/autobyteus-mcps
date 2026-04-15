# Stage 7 Executable Validation (API/E2E)

## Validation Round Meta

- Current Validation Round: `6`
- Trigger Stage: `Re-entry`
- Prior Round Reviewed: `5`
- Latest Authoritative Round: `6`

## Testing Scope

- Ticket: `tts-mcp-voice-parameter`
- Scope classification: `Small`
- Workflow state source: `tickets/in-progress/tts-mcp-voice-parameter/workflow-state.md`
- Requirements source: `tickets/in-progress/tts-mcp-voice-parameter/requirements.md`
- Call stack source: `tickets/in-progress/tts-mcp-voice-parameter/future-state-runtime-call-stack.md`
- Interface/system shape in scope: `API`
- Platform/runtime targets:
  - local in-process MCP server harness
  - Apple Silicon macOS MLX runtime for real `speak` tool execution
- Lifecycle boundaries in scope (`Install` / `Startup` / `Update` / `Restart` / `Migration` / `Shutdown` / `Recovery` / `None`): `None`

## Validation Asset Strategy

- Durable validation assets to add/update in the repository:
  - `tts-mcp/tests/test_config.py`
  - `tts-mcp/tests/test_server.py`
  - `tts-mcp/tests/test_speak_voice.py`
  - `tts-mcp/tests/test_speak_temperature.py`
  - `tts-mcp/tests/test_mlx_language_chinese.py`
  - `tts-mcp/tests/test_mlx_language_english.py`
  - `tts-mcp/tests/test_runner.py`
  - `tts-mcp/tests/test_real_mcp_speak_tool_english.py`
  - `tts-mcp/tests/test_real_mcp_speak_tool_chinese_qwen.py`
- Temporary validation methods or setup to use only if needed:
  - none required in the authoritative round
- Cleanup expectation for temporary validation:
  - not applicable

## Round History

| Round | Trigger | Prior Unresolved Failures Rechecked (`Yes`/`No`/`N/A`) | New Failures Found (`Yes`/`No`) | Gate Result (`Pass`/`Fail`/`Blocked`) | Latest Authoritative (`Yes`/`No`) | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `1` | `Stage 6 exit` | `N/A` | `No` | `Pass` | `No` | Initial scope validated schema exposure and earlier real MCP route coverage, but not explicit English/Chinese voice scenarios in a canonical Stage 7 artifact. |
| `2` | `Re-entry` | `Yes` | `No` | `Pass` | `No` | Support-structure cleanup rerun completed with focused regression coverage. |
| `3` | `Re-entry` | `Yes` | `No` | `Pass` | `No` | Added explicit English+voice and Chinese+voice real MCP scenarios plus user-listenable sample audio generation. |
| `4` | `Re-entry` | `Yes` | `No` | `Pass` | `No` | Renamed the public field to `language` and reran validation against the renamed boundary. |
| `5` | `Re-entry` | `Yes` | `No` | `Pass` | `No` | Fixed the Chinese route to use a speaker-capable model path, added deterministic Chinese no-voice behavior, and added incompatible pinned-model failure coverage. |
| `6` | `Re-entry` | `Yes` | `No` | `Pass` | `Yes` | Added public `temperature`, default MLX `0.0` propagation, truthful Chinese speaker examples, non-MLX rejection coverage, and a real repeated Chinese deterministic-hash test. |

## Acceptance Criteria Coverage Matrix (Mandatory)

| Acceptance Criteria ID | Requirement ID | Criterion Summary | Scenario ID(s) | Current Status (`Unmapped`/`Not Run`/`Passed`/`Failed`/`Blocked`/`Waived`) | Last Updated |
| --- | --- | --- | --- | --- | --- |
| `AC-001` | `R-001`, `R-002`, `R-003` | Public schema exposes `language`, `voice`, and `temperature` | `AV-001` | `Passed` | `2026-04-15` |
| `AC-002` | `R-008` | Voice schema/examples stay route-aware and truthful | `AV-001`, `AV-008` | `Passed` | `2026-04-15` |
| `AC-003` | `R-004`, `R-009` | Omitted MLX temperature defaults to deterministic `0.0` | `AV-001`, `AV-002`, `AV-005`, `AV-008` | `Passed` | `2026-04-15` |
| `AC-004` | `R-005` | Repeated Chinese no-voice calls resolve to a deterministic default voice path | `AV-002`, `AV-008` | `Passed` | `2026-04-15` |
| `AC-005` | `R-006` | Repeated Chinese named-voice calls use a speaker-capable Qwen model variant | `AV-004`, `AV-005`, `AV-008` | `Passed` | `2026-04-15` |
| `AC-006` | `R-003` | Explicit temperature overrides are forwarded to MLX | `AV-003`, `AV-008` | `Passed` | `2026-04-15` |
| `AC-007` | `R-007` | Incompatible pinned-model named-voice requests fail clearly | `AV-006`, `AV-008` | `Passed` | `2026-04-15` |
| `AC-008` | `R-010` | English/Kokoro named-voice regression remains clean | `AV-007` | `Passed` | `2026-04-15` |
| `AC-009` | `R-012` | Updated focused tests pass under `uv run --extra test python -m pytest` | `AV-008` | `Passed` | `2026-04-15` |

## Spine Coverage Matrix (Mandatory)

| Spine ID | Spine Scope (`Primary End-to-End`/`Return-Event`/`Bounded Local`) | Governing Owner | Scenario ID(s) | Coverage Status (`Unmapped`/`Planned`/`Passed`/`Failed`/`Blocked`/`N/A`) | Notes |
| --- | --- | --- | --- | --- | --- |
| `DS-001` | `Primary End-to-End` | MCP tool discovery boundary | `AV-001` | `Passed` | Proves the public tool now exposes `language`, `voice`, and `temperature` with truthful guidance. |
| `DS-002` | `Primary End-to-End` | public MCP `speak` boundary -> Chinese MLX auto-route with omitted `voice` and omitted `temperature` | `AV-002`, `AV-008` | `Passed` | Proves the command path injects deterministic default speaker + temperature. |
| `DS-003` | `Primary End-to-End` | public MCP `speak` boundary -> MLX explicit temperature override | `AV-003`, `AV-008` | `Passed` | Proves explicit MLX temperature overrides are preserved. |
| `DS-004` | `Primary End-to-End` | public MCP `speak` boundary -> Chinese MLX named-speaker route | `AV-004`, `AV-005`, `AV-008` | `Passed` | Proves Chinese named-voice requests hit a speaker-capable model and remain deterministic under the default temperature. |
| `DS-005` | `Primary End-to-End` | public MCP `speak` boundary -> pinned incompatible Chinese Base model error | `AV-006`, `AV-008` | `Passed` | Proves named Chinese voices still fail clearly on incompatible explicit model pins. |
| `DS-006` | `Primary End-to-End` | public MCP `speak` boundary -> English/Kokoro named-voice route | `AV-007` | `Passed` | Proves the English route remains unchanged by the temperature-control fix. |

## Scenario Catalog

| Scenario ID | Spine ID(s) | Source Type (`Requirement`/`Design-Risk`) | Acceptance Criteria ID(s) | Requirement ID(s) | Use Case ID(s) | Validation Mode (`API`/`Browser-E2E`/`Desktop-UI`/`CLI`/`Integration`/`Process`/`Lifecycle`/`Other`) | Platform / Runtime | Objective/Risk | Expected Outcome | Durable Validation Asset(s) | Command/Harness | Status (`Not Started`/`In Progress`/`Passed`/`Failed`/`Blocked`/`N/A`) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `AV-001` | `DS-001` | `Requirement` | `AC-001`, `AC-002`, `AC-003` | `R-001`, `R-002`, `R-003`, `R-008`, `R-009` | `UC-002`, `UC-004`, `UC-005`, `UC-006` | `API` | in-process MCP server test harness | Public schema must stay concise and truthful | `session.list_tools()` shows public `language`, route-aware `voice`, and MLX `temperature` guidance with deterministic default `0.0` | `tts-mcp/tests/test_server.py`, `tts-mcp/tests/test_speak_voice.py`, `tts-mcp/tests/test_speak_temperature.py` | `uv run --project tts-mcp --extra test python -m pytest -q tests/test_server.py tests/test_speak_voice.py tests/test_speak_temperature.py` | `Passed` |
| `AV-002` | `DS-002` | `Requirement` | `AC-003`, `AC-004` | `R-004`, `R-005` | `UC-001`, `UC-005` | `Integration` | local pytest runtime | Omitted Chinese `voice` and omitted MLX `temperature` must not drift to backend defaults | MLX command uses `mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16` plus `--voice Vivian` and `--temperature 0.0` when the caller omitted both | `tts-mcp/tests/test_mlx_language_chinese.py`, `tts-mcp/tests/test_runner.py` | `uv run --project tts-mcp --extra test python -m pytest -q tests/test_mlx_language_chinese.py tests/test_runner.py` | `Passed` |
| `AV-003` | `DS-003` | `Requirement` | `AC-006` | `R-003` | `UC-006` | `Integration` | local pytest runtime | Explicit MLX temperature overrides must not be clobbered by the deterministic default | MLX command uses the caller-provided `--temperature 0.4` | `tts-mcp/tests/test_mlx_language_chinese.py`, `tts-mcp/tests/test_runner.py` | `uv run --project tts-mcp --extra test python -m pytest -q tests/test_mlx_language_chinese.py tests/test_runner.py` | `Passed` |
| `AV-004` | `DS-004` | `Requirement` | `AC-005` | `R-006` | `UC-002` | `API` | Apple Silicon macOS MLX runtime | Explicit Chinese named voices must still use the speaker-capable model path | Real `speak(text, language=\"zh\", voice=\"Vivian\")` succeeds on the updated route | `tts-mcp/tests/test_real_mcp_speak_tool_chinese_qwen.py` | `TTS_MCP_RUN_REAL_MCP_SPEAK=1 uv run --project tts-mcp --extra test python -m pytest -q tests/test_real_mcp_speak_tool_chinese_qwen.py::test_real_mcp_speak_tool_routes_explicit_chinese_voice_to_apple_silicon_mlx` | `Passed` |
| `AV-005` | `DS-004` | `Design-Risk` | `AC-003`, `AC-005` | `R-004`, `R-006` | `UC-005` | `API` | Apple Silicon macOS MLX runtime | The new default temperature must actually remove run-to-run drift in the real MCP path | Three repeated real `speak(text, language=\"zh\", voice=\"eric\")` calls with omitted `temperature` produce identical output hashes | `tts-mcp/tests/test_real_mcp_speak_tool_chinese_qwen.py` | `TTS_MCP_RUN_REAL_MCP_SPEAK=1 uv run --project tts-mcp --extra test python -m pytest -q tests/test_real_mcp_speak_tool_chinese_qwen.py::test_real_mcp_speak_tool_defaults_chinese_temperature_to_deterministic_output` | `Passed` |
| `AV-006` | `DS-005` | `Design-Risk` | `AC-007` | `R-007` | `UC-004` | `API` | in-process MCP server test harness | Incompatible pinned Base model + named Chinese voice must fail clearly | Public `speak` returns `ok=false` with a clear reason instead of silently generating audio | `tts-mcp/tests/test_mlx_language_chinese.py` | `uv run --project tts-mcp --extra test python -m pytest -q tests/test_mlx_language_chinese.py` | `Passed` |
| `AV-007` | `DS-006` | `Requirement` | `AC-008` | `R-010` | `UC-003` | `API` | Apple Silicon macOS MLX runtime | English/Kokoro named voice must remain unchanged | Real `speak(text, language=\"en\", voice=\"af_heart\")` succeeds | `tts-mcp/tests/test_real_mcp_speak_tool_english.py` | `TTS_MCP_RUN_REAL_MCP_SPEAK=1 uv run --project tts-mcp --extra test python -m pytest -q tests/test_real_mcp_speak_tool_english.py` | `Passed` |
| `AV-008` | `DS-001`, `DS-002`, `DS-003`, `DS-004`, `DS-005` | `Design-Risk` | `AC-002`, `AC-003`, `AC-004`, `AC-005`, `AC-006`, `AC-007`, `AC-009` | `R-003`, `R-004`, `R-005`, `R-006`, `R-007`, `R-008`, `R-009`, `R-012` | `UC-001`, `UC-002`, `UC-004`, `UC-005`, `UC-006` | `Integration` | local pytest runtime | The changed config/server/runner/command path must stay coherent under focused regression coverage | Focused repo suite remains green across config, schema, MLX routing, MLX temperature propagation, non-MLX rejection, and runner behavior | `tts-mcp/tests/test_config.py`, `tts-mcp/tests/test_server.py`, `tts-mcp/tests/test_speak_voice.py`, `tts-mcp/tests/test_speak_temperature.py`, `tts-mcp/tests/test_mlx_language_chinese.py`, `tts-mcp/tests/test_mlx_language_english.py`, `tts-mcp/tests/test_runner.py` | `uv run --project tts-mcp --extra test python -m pytest -q tests/test_config.py tests/test_server.py tests/test_speak_voice.py tests/test_speak_temperature.py tests/test_mlx_language_chinese.py tests/test_mlx_language_english.py tests/test_runner.py` | `Passed` |

## Validation Assets Implemented Or Updated

| Asset Path / Name | Asset Type (`API Test`/`Browser Test`/`Desktop Automation`/`CLI Harness`/`Lifecycle Harness`/`Process Probe`/`Harness`/`Fixture`/`Helper`/`Other`) | Durable In Repo (`Yes`/`No`) | Scenario ID(s) | Notes |
| --- | --- | --- | --- | --- |
| `tts-mcp/tests/test_config.py` | `API Test` | `Yes` | `AV-008` | Added deterministic MLX default-temperature config coverage. |
| `tts-mcp/tests/test_server.py`, `tts-mcp/tests/test_speak_voice.py`, `tts-mcp/tests/test_speak_temperature.py` | `API Test` | `Yes` | `AV-001`, `AV-008` | Public schema now covers `language`, truthful `voice`, and optional `temperature`. |
| `tts-mcp/tests/test_mlx_language_chinese.py` | `API Test` | `Yes` | `AV-002`, `AV-003`, `AV-006`, `AV-008` | Added command-level default-temperature and explicit override coverage for Chinese MLX. |
| `tts-mcp/tests/test_mlx_language_english.py` | `API Test` | `Yes` | `AV-008` | Added command-level default-temperature coverage for the English/Kokoro MLX route. |
| `tts-mcp/tests/test_runner.py` | `API Test` | `Yes` | `AV-002`, `AV-003`, `AV-008` | Added non-MLX temperature rejection coverage and kept MLX path coherence checks. |
| `tts-mcp/tests/test_real_mcp_speak_tool_chinese_qwen.py` | `API Test` | `Yes` | `AV-004`, `AV-005` | Added a real repeated-hash deterministic Chinese regression. |
| `tts-mcp/tests/test_real_mcp_speak_tool_english.py` | `API Test` | `Yes` | `AV-007` | English/Kokoro named-voice regression remains green. |

## Temporary Validation Methods / Setup Used

| Method / Setup | Why Needed | Scenario ID(s) | Cleanup Required (`Yes`/`No`) | Cleanup Status |
| --- | --- | --- | --- | --- |
| none | no temporary validation assets were required in the authoritative round | `N/A` | `No` | `N/A` |

## Prior Failure Resolution Check (Mandatory On Round >1)

| Prior Round | Scenario ID | Previous Classification | Current Resolution (`Resolved`/`Partially Resolved`/`Still Failing`/`Not Applicable After Rework`) | Evidence | Notes |
| --- | --- | --- | --- | --- | --- |
| `5` | `AV-001`, `AV-002`, `AV-005` | `Requirement Gap` | `Resolved` | Public schema now advertises truthful Chinese CustomVoice examples, and omitted MLX temperature now defaults to deterministic `0.0` through both focused and real validation. | The repeated real Chinese hash check closes the earlier “valid WAV but drifting voice” gap. |

## Failure Escalation Log

| Date | Scenario ID | Failure Summary | Investigation Required (`Yes`/`No`) | Classification (`Local Fix`/`Design Impact`/`Requirement Gap`/`Unclear`) | Action Path | `investigation-notes.md` Updated | Requirements Updated | Design Updated | Call Stack Regenerated | Review Re-Entry Round | Resolved |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `2026-04-15` | `AV-001`, `AV-002`, `AV-005` | The MCP still overclaimed unsupported Chinese speaker examples and left MLX sampling on its runtime default, so repeated named-speaker output could drift even after the earlier speaker-capable routing fix. | `Yes` | `Requirement Gap` | `Stage 2 -> Stage 3 -> Stage 4 -> Stage 5 -> Stage 6 -> Stage 7` | `Yes` | `Yes` | `Yes` | `Yes` | `Round 6` | `Yes` |

## Feasibility And Risk Record

- Any infeasible scenarios (`Yes`/`No`): `No`
- Environment constraints (secrets/tokens/access limits/dependencies):
  - Real MCP temperature/voice scenarios require Apple Silicon macOS and an available `mlx_audio.tts.generate` command.
- Platform/runtime specifics:
  - Apple Silicon macOS, local MLX runtime from `tts-mcp/.venv-mlx/bin/mlx_audio.tts.generate`
- Compensating automated evidence:
  - Focused config/schema/routing/runner suite passed.
  - Real MCP English and Chinese tests passed with `TTS_MCP_RUN_REAL_MCP_SPEAK=1`.
  - Repeated real Chinese default-temperature outputs hashed identically under the public MCP boundary.
- Residual risk notes:
  - Curated Chinese speaker examples remain tied to the installed/runtime model inventory and should be resynced if the upstream CustomVoice speaker set changes in a future runtime upgrade.
  - The live app-facing MCP process will still need a restart/reconnect before it begins using this updated code path.

## Stage 7 Gate Decision

- Latest authoritative round: `6`
- Latest authoritative result (`Pass`/`Fail`/`Blocked`): `Pass`
- Stage 7 complete: `Yes`
- Durable executable validation that should live in the repository was implemented or updated: `Yes`
- All in-scope acceptance criteria mapped to scenarios: `Yes`
- All relevant spines mapped to scenarios: `Yes`
- All executable in-scope acceptance criteria status = `Passed`: `Yes`
- All executable relevant spines status = `Passed`: `Yes`
- Critical executable scenarios passed: `Yes`
- Any infeasible acceptance criteria: `No`
- Unresolved escalation items: `No`
- Ready to enter Stage 8 code review: `Yes`
- Notes:
  - The changed public contract is now validated at the schema layer, command/routing layer, and real MCP execution layer.
