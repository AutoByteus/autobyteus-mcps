# Stage 7 Executable Validation: Image/Audio CLI generation_config JSON support

## Validation Round Meta

- Current Validation Round: `1`
- Trigger Stage: `6`
- Prior Round Reviewed: `None`
- Latest Authoritative Round: `1`

## Testing Scope

- Ticket: `image-audio-cli-generation-config-json`
- Scope classification: `Small`
- Workflow state source: `tickets/in-progress/image-audio-cli-generation-config-json/workflow-state.md`
- Requirements source: `tickets/in-progress/image-audio-cli-generation-config-json/requirements.md`
- Call stack source: `tickets/in-progress/image-audio-cli-generation-config-json/future-state-runtime-call-stack.md`
- Design source: `implementation.md` solution sketch
- Interface/system shape in scope: `CLI`
- Platform/runtime targets: local Python 3.11 via `uv --directory autobyteus-image-audio run --frozen`
- Lifecycle boundaries in scope: `None`

## Validation Asset Strategy

- Durable validation assets updated in the repository:
  - `autobyteus-image-audio/tests/test_cli_local.py`
- Temporary validation methods:
  - CLI invalid JSON usage-error probe.
  - Help text grep inspection.
  - Source grep inspection for absence of API-key CLI arguments.
- Cleanup expectation: no temporary repo files retained.

## Round History

| Round | Trigger | Prior Unresolved Failures Rechecked | New Failures Found | Gate Result | Latest Authoritative | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Stage 6 exit | N/A | No | Pass | Yes | 31 local tests passed; CLI probes passed. |

## Acceptance Criteria Coverage Matrix

| Acceptance Criteria ID | Requirement ID | Criterion Summary | Scenario ID(s) | Current Status | Last Updated |
| --- | --- | --- | --- | --- | --- |
| AC-001 | REQ-001 | Inline multi-speaker speech JSON dict dispatch | SCN-001 | Passed | 2026-06-25 |
| AC-002 | REQ-001 | Inline image JSON dict dispatch | SCN-002 | Passed | 2026-06-25 |
| AC-003 | REQ-002 | JSON file config dispatch | SCN-003 | Passed | 2026-06-25 |
| AC-004 | REQ-003 | Existing `--config` behavior remains | SCN-004 | Passed | 2026-06-25 |
| AC-005 | REQ-004 | Existing `--speaker/--voice` behavior remains | SCN-005 | Passed | 2026-06-25 |
| AC-006 | REQ-005 | Invalid/non-object JSON returns UsageError | SCN-006 | Passed | 2026-06-25 |
| AC-007 | REQ-005 | Conflicting config sources return UsageError | SCN-007 | Passed | 2026-06-25 |
| AC-008 | REQ-006 | Help includes new options | SCN-008 | Passed | 2026-06-25 |
| AC-009 | REQ-006 | README documents nested JSON and file config | SCN-009 | Passed | 2026-06-25 |
| AC-010 | REQ-007 | No API-key CLI argument introduced | SCN-010 | Passed | 2026-06-25 |

## Spine Coverage Matrix

| Spine ID | Spine Scope | Governing Owner | Scenario ID(s) | Coverage Status | Notes |
| --- | --- | --- | --- | --- | --- |
| DS-001 | Primary End-to-End | `image_audio_mcp.cli` | SCN-001, SCN-002, SCN-003 | Passed | Dispatch-level tests monkeypatch service calls and inspect generation_config dict. |
| DS-002 | Bounded Local | `_load_generation_config` | SCN-001 through SCN-007 | Passed | Parser, merge, conflict, and error behavior covered. |
| DS-003 | Primary Documentation | argparse help + README | SCN-008, SCN-009, SCN-010 | Passed | Help/readme/source inspections passed. |

## Scenario Catalog

| Scenario ID | Spine ID(s) | Source Type | Acceptance Criteria ID(s) | Requirement ID(s) | Use Case ID(s) | Validation Mode | Platform / Runtime | Lifecycle Boundary | Objective/Risk | Expected Outcome | Durable Validation Asset(s) | Temporary Validation Method / Setup | Command/Harness | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SCN-001 | DS-001, DS-002 | Requirement | AC-001 | REQ-001 | UC-001 | CLI | local pytest | None | N/A | Speech receives nested multi-speaker dict | `tests/test_cli_local.py::test_generate_speech_cli_accepts_mcp_style_generation_config_json` | N/A | `pytest tests/test_cli_local.py` | Passed |
| SCN-002 | DS-001, DS-002 | Requirement | AC-002 | REQ-001 | UC-001 | CLI | local pytest | None | N/A | Image receives nested dict | `tests/test_cli_local.py::test_generate_image_cli_accepts_generation_config_file_and_config_merge` also validates nested merge | N/A | `pytest tests/test_cli_local.py` | Passed |
| SCN-003 | DS-001, DS-002 | Requirement | AC-003 | REQ-002 | UC-002 | CLI | local pytest | None | N/A | File JSON loads and merges | `tests/test_cli_local.py::test_generate_image_cli_accepts_generation_config_file_and_config_merge` | N/A | `pytest tests/test_cli_local.py` | Passed |
| SCN-004 | DS-002 | Requirement | AC-004 | REQ-003 | UC-003 | CLI | local pytest | None | Regression | Existing `--config` tests pass | Existing CLI tests | N/A | `pytest tests/test_cli_local.py` | Passed |
| SCN-005 | DS-002 | Requirement | AC-005 | REQ-004 | UC-004 | CLI | local pytest | None | Regression | Existing speaker/voice tests pass | Existing CLI tests | N/A | `pytest tests/test_cli_local.py` | Passed |
| SCN-006 | DS-002 | Requirement | AC-006 | REQ-005 | UC-005 | CLI | local pytest + wrapper probe | None | Error handling | Invalid/non-object JSON gives UsageError | New CLI tests | Wrapper invalid JSON probe | see commands below | Passed |
| SCN-007 | DS-002 | Requirement | AC-007 | REQ-005 | UC-005 | CLI | local pytest | None | Error handling | Conflict gives UsageError | New CLI tests | N/A | `pytest tests/test_cli_local.py` | Passed |
| SCN-008 | DS-003 | Requirement | AC-008 | REQ-006 | UC-006 | CLI | local shell | None | Discoverability | Help includes new options | `test_cli_help_is_task_oriented_and_config_first` | grep help output | `./cli/... generate-speech --help | grep ...` | Passed |
| SCN-009 | DS-003 | Requirement | AC-009 | REQ-006 | UC-006 | Other | file inspection | None | Documentation | README documents nested JSON/file config | README update | inspection | `grep generation-config README.md` | Passed |
| SCN-010 | DS-001 | Requirement | AC-010 | REQ-007 | UC-001/2/3/4 | Other | source inspection | None | Security / credential handling unchanged | No API-key CLI arg added | N/A | grep source | `! grep -R -- '--api-key\|api_key' cli.py` | Passed |

## Validation Assets Implemented Or Updated

| Asset Path / Name | Asset Type | Durable In Repo | Scenario ID(s) | Notes |
| --- | --- | --- | --- | --- |
| `autobyteus-image-audio/tests/test_cli_local.py` | CLI Harness | Yes | SCN-001 through SCN-008 | Covers parser/dispatch/error/help behavior without provider calls. |
| `autobyteus-image-audio/README.md` | Documentation | Yes | SCN-009 | Documents direct MCP-shaped JSON and config-file path. |

## Temporary Validation Methods / Setup Used

| Method / Setup | Why Needed | Scenario ID(s) | Cleanup Required | Cleanup Status |
| --- | --- | --- | --- | --- |
| Wrapper invalid JSON probe | Proves real CLI envelope path before provider call. | SCN-006 | No | No temp repo files created. |
| Help grep | Confirms installed wrapper help exposes new options. | SCN-008 | No | No temp repo files created. |
| API-key arg grep | Confirms credential handling unchanged. | SCN-010 | No | No temp repo files created. |

## Prior Failure Resolution Check

N/A; first validation round.

## Failure Escalation Log

None.

## Feasibility And Risk Record

- Any infeasible scenarios: `No`
- Environment constraints: provider credentials are not needed because validation uses monkeypatched service calls and parser-level probes.
- Human-assisted execution steps required: `No`
- User waiver for infeasible acceptance criteria recorded: `N/A`
- Temporary validation-only scaffolding cleaned up: `Yes`; none retained.

## Evidence Commands

```bash
uv --directory autobyteus-image-audio run --frozen --extra test pytest tests/test_cli_local.py
# 17 passed

uv --directory autobyteus-image-audio run --frozen --extra test pytest tests/test_cli_local.py tests/test_server_local.py tests/test_services_local.py
# 31 passed

./cli/autobyteus-image-audio generate-image --prompt test --generation-config '[' --output-file-path out.png
# {"ok":false,"command":"generate-image","error_type":"UsageError",...}

./cli/autobyteus-image-audio generate-speech --help | grep -E -- '--generation-config|--generation-config-file'
# matched both options

! grep -R -- '--api-key\|api_key' autobyteus-image-audio/src/image_audio_mcp/cli.py
# passed; no CLI API-key argument introduced
```

## Stage 7 Gate Decision

- Latest authoritative round: `1`
- Latest authoritative result: `Pass`
- Stage 7 complete: `Yes`
- Durable executable validation that should live in the repository was implemented or updated: `Yes`
- All in-scope acceptance criteria mapped to scenarios: `Yes`
- All relevant spines mapped to scenarios: `Yes`
- All executable in-scope acceptance criteria status = `Passed`: `Yes`
- All executable relevant spines status = `Passed`: `Yes`
- Critical executable scenarios passed: `Yes`
- Any infeasible acceptance criteria: `No`
- Explicit user waiver recorded for each infeasible acceptance criterion: `N/A`
- Temporary validation-only scaffolding cleaned up or intentionally retained with rationale: `Yes`
- Unresolved escalation items: `No`
- Ready to enter Stage 8 code review: `Yes`

---

# Re-Entry Validation Round 2: Removed split config flags

## Validation Round Meta

- Current Validation Round: `2`
- Trigger Stage: `6` re-entry exit
- Prior Round Reviewed: `1`
- Latest Authoritative Round: `2`

## Round History Addendum

| Round | Trigger | Prior Unresolved Failures Rechecked | New Failures Found | Gate Result | Latest Authoritative | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | Re-entry Stage 6 exit | Yes | No | Pass | Yes | Refined acceptance criteria passed; removed flags are rejected. |

## Updated Acceptance Criteria Coverage Matrix

| Acceptance Criteria ID | Requirement ID | Criterion Summary | Scenario ID(s) | Current Status | Last Updated |
| --- | --- | --- | --- | --- | --- |
| AC-001 | REQ-001 | Inline multi-speaker speech JSON dict dispatch | SCN-001 | Passed | 2026-06-25 |
| AC-002 | REQ-001 | Inline image JSON dict dispatch | SCN-002 | Passed | 2026-06-25 |
| AC-003 | REQ-002 | JSON file config dispatch | SCN-003 | Passed | 2026-06-25 |
| AC-004 | REQ-003 | Invalid JSON/file inputs return UsageError | SCN-004 | Passed | 2026-06-25 |
| AC-005 | REQ-003 | Conflicting full-object config sources return UsageError | SCN-005 | Passed | 2026-06-25 |
| AC-006 | REQ-004 | Help includes MCP-shaped options | SCN-006 | Passed | 2026-06-25 |
| AC-007 | REQ-004 | README documents only nested JSON/file config for model settings | SCN-007 | Passed | 2026-06-25 |
| AC-008 | REQ-005 | Help excludes `--config`, `--speaker`, and `--voice` | SCN-008 | Passed | 2026-06-25 |
| AC-009 | REQ-005 | Removed flags return usage errors | SCN-009 | Passed | 2026-06-25 |
| AC-010 | REQ-006 | No API-key CLI arg introduced | SCN-010 | Passed | 2026-06-25 |

## Updated Spine Coverage Matrix

| Spine ID | Spine Scope | Governing Owner | Scenario ID(s) | Coverage Status | Notes |
| --- | --- | --- | --- | --- | --- |
| DS-001 | Primary End-to-End | `image_audio_mcp.cli` | SCN-001, SCN-002, SCN-003 | Passed | Dispatch tests verify native dict passed to services. |
| DS-002 | Bounded Local | `_load_generation_config` | SCN-001 through SCN-005 | Passed | Full-object parsing, file loading, and conflict behavior covered. |
| DS-003 | Primary Documentation | argparse help + README | SCN-006, SCN-007, SCN-010 | Passed | Docs/help updated and inspected. |
| DS-004 | Error Boundary | argparse + `JsonArgumentParser` | SCN-008, SCN-009 | Passed | Removed flags rejected as unrecognized args. |

## Re-Entry Evidence Commands

```bash
uv --directory autobyteus-image-audio run --frozen --extra test pytest tests/test_cli_local.py tests/test_server_local.py tests/test_services_local.py
# 31 passed

./cli/autobyteus-image-audio generate-speech --help
# shows --generation-config and --generation-config-file only for model config

./cli/autobyteus-image-audio generate-image --prompt test --config voice=Kore --output-file-path out.png
# {"ok":false,"command":"generate-image","error_type":"UsageError","error_message":"unrecognized arguments: --config voice=Kore"}
```

## Re-Entry Stage 7 Gate Decision

- Latest authoritative round: `2`
- Latest authoritative result: `Pass`
- Stage 7 complete: `Yes`
- Durable executable validation updated: `Yes`
- All refined acceptance criteria mapped to scenarios: `Yes`
- All relevant spines mapped to scenarios: `Yes`
- All executable refined acceptance criteria status = `Passed`: `Yes`
- Critical executable scenarios passed: `Yes`
- Infeasible criteria: `No`
- Unresolved escalation items: `No`
- Ready to enter Stage 8 code review: `Yes`
