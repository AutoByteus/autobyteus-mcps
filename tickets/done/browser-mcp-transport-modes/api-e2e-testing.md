# API/E2E Testing

Use this document for Stage 7 API/E2E test implementation and execution.

## Testing Scope

- Ticket: `browser-mcp-transport-modes`
- Scope classification: `Small`
- Workflow state source: `tickets/in-progress/browser-mcp-transport-modes/workflow-state.md`
- Requirements source: `tickets/in-progress/browser-mcp-transport-modes/requirements.md`
- Call stack source: `tickets/in-progress/browser-mcp-transport-modes/future-state-runtime-call-stack.md`
- Design source (`Medium/Large`): N/A

## Acceptance Criteria Coverage Matrix (Mandatory)

| Acceptance Criteria ID | Requirement ID | Criterion Summary | Scenario ID(s) | Current Status (`Unmapped`/`Not Run`/`Passed`/`Failed`/`Blocked`/`Waived`) | Last Updated |
| --- | --- | --- | --- | --- | --- |
| AC-001 | R-001,R-002 | stdio startup transport selected | AV-001 | Passed | 2026-02-26 |
| AC-002 | R-001,R-002 | streamable-http startup transport selected | AV-002 | Passed | 2026-02-26 |
| AC-003 | R-003 | host/port config applied | AV-003 | Passed | 2026-02-26 |
| AC-004 | R-004 | invalid transport rejected deterministically | AV-004 | Passed | 2026-02-26 |
| AC-005 | R-005 | existing tools remain behaviorally available | AV-005 | Passed | 2026-02-26 |
| AC-006 | R-006 | README documents both transports | AV-006 | Passed | 2026-02-26 |

## Scenario Catalog

| Scenario ID | Source Type (`Requirement`/`Design-Risk`) | Acceptance Criteria ID(s) | Requirement ID(s) | Use Case ID(s) | Level (`API`/`E2E`) | Objective/Risk | Expected Outcome | Command/Harness | Status (`Not Started`/`In Progress`/`Passed`/`Failed`/`Blocked`/`N/A`) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AV-001 | Requirement | AC-001 | R-001,R-002 | UC-001 | API | Verify stdio path | `main()` runs with `transport="stdio"` | `cd browser-mcp && uv run python -m pytest tests/test_server.py -k "test_main_uses_stdio_transport"` | Passed |
| AV-002 | Requirement | AC-002 | R-001,R-002 | UC-002 | API | Verify streamable-http path | `main()` runs with `transport="streamable-http"` | `cd browser-mcp && uv run python -m pytest tests/test_server.py -k "test_main_uses_configured_transport"` | Passed |
| AV-003 | Requirement | AC-003 | R-003 | UC-003 | API | Verify host/port applied | `create_server()` reflects runtime host/port settings | `cd browser-mcp && uv run python -m pytest tests/test_server.py -k "test_create_server_applies_runtime_host_port"` | Passed |
| AV-004 | Requirement | AC-004 | R-004 | UC-004 | API | Verify invalid transport failure | invalid transport raises deterministic config error | `cd browser-mcp && uv run python -m pytest tests/test_server.py -k "test_runtime_config_invalid_transport or test_main_invalid_runtime_config_exits"` | Passed |
| AV-005 | Requirement | AC-005 | R-005 | UC-005 | API | Ensure tool behavior unchanged | existing tool session flows still pass | `cd browser-mcp && uv run python -m pytest tests/test_server.py -k "test_open_and_close_tab or test_read_page_with_explicit_tab_id or test_run_script_with_explicit_tab_id"` | Passed |
| AV-006 | Requirement | AC-006 | R-006 | UC-001,UC-002 | API | Verify docs sync | README documents both stdio + streamable-http env config | manual review of `browser-mcp/README.md` | Passed |

## Failure Escalation Log

| Date | Scenario ID | Failure Summary | Investigation Required (`Yes`/`No`) | Classification (`Local Fix`/`Design Impact`/`Requirement Gap`/`Unclear`) | Action Path | `investigation-notes.md` Updated | Requirements Updated | Design Updated | Call Stack Regenerated | Review Re-Entry Round | Resolved |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| None | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |

## Feasibility And Risk Record

- Any infeasible scenarios (`Yes`/`No`): No
- Environment constraints (secrets/tokens/access limits/dependencies): none blocking Stage 7
- Compensating automated evidence: N/A
- Residual risk notes: low; startup transport flow fully unit-tested
- User waiver for infeasible acceptance criteria recorded (`Yes`/`No`): No

## Stage 7 Gate Decision

- Stage 7 complete: `Yes`
- All in-scope acceptance criteria mapped to scenarios: `Yes`
- All executable in-scope acceptance criteria status = `Passed`: `Yes`
- Critical executable scenarios passed: `Yes`
- Any infeasible acceptance criteria: `No`
- Explicit user waiver recorded for each infeasible acceptance criterion (if any): `N/A`
- Unresolved escalation items: `No`
- Ready to enter Stage 8 code review: `Yes`
