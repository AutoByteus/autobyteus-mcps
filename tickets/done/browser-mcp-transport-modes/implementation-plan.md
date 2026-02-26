# Implementation Plan

## Scope Classification

- Classification: `Small`
- Reasoning:
  - Localized startup/config wiring enhancement in `browser_mcp.server`.
  - No browser tool behavior change.
- Workflow Depth:
  - `Small` -> draft implementation plan (solution sketch) -> future-state runtime call stack -> future-state runtime call stack review (iterative rounds until `Go Confirmed`) -> finalize implementation plan -> implementation progress tracking -> API/E2E testing -> code review gate -> docs sync.

## Upstream Artifacts (Required)

- Workflow state: `tickets/in-progress/browser-mcp-transport-modes/workflow-state.md`
- Investigation notes: `tickets/in-progress/browser-mcp-transport-modes/investigation-notes.md`
- Requirements: `tickets/in-progress/browser-mcp-transport-modes/requirements.md`
  - Current Status: `Design-ready`
- Runtime call stacks: `tickets/in-progress/browser-mcp-transport-modes/future-state-runtime-call-stack.md`
- Runtime review: `tickets/in-progress/browser-mcp-transport-modes/future-state-runtime-call-stack-review.md`
- Proposed design (required for `Medium/Large`): N/A (`Small` scope)

## Plan Maturity

- Current Status: `Ready For Implementation`
- Notes: Stage 5 review reached `Go Confirmed` with two clean rounds.

## Preconditions (Must Be True Before Finalizing This Plan)

- `requirements.md` is at least `Design-ready` (`Refined` allowed): Yes
- Acceptance criteria use stable IDs (`AC-*`) with measurable expected outcomes: Yes
- `workflow-state.md` is current and Stage 5 review-gate evidence is recorded: Yes
- Runtime call stack review artifact exists and is current: Yes
- All in-scope use cases reviewed: Yes
- No unresolved blocking findings: Yes
- Runtime review has `Go Confirmed` with two consecutive clean deep-review rounds (no blockers, no required persisted artifact updates, no newly discovered use cases): Yes
- Missing-use-case discovery sweeps completed for the final two clean rounds: Yes
- No newly discovered use cases in the final two clean rounds: Yes

## Solution Sketch (Required For `Small`, Optional Otherwise)

- Use Cases In Scope: UC-001..UC-005
- Requirement Coverage Guarantee (all requirements mapped to at least one use case): Yes
- Design-Risk Use Cases (if any, with risk/objective): none currently
- Target Architecture Shape (for `Small`, mandatory): keep `server.py` as startup/config + tool registration boundary, add explicit validated runtime settings object to avoid ad-hoc env parsing in `main()`.
- New Layers/Modules/Boundary Interfaces To Introduce: none required; keep in `server.py` to match current package shape.
- Touched Files/Modules:
  - `browser-mcp/src/browser_mcp/server.py`
  - `browser-mcp/tests/test_server.py`
  - `browser-mcp/README.md`
- API/Behavior Delta:
  - Add env vars: `BROWSER_MCP_TRANSPORT`, `BROWSER_MCP_HOST`, `BROWSER_MCP_PORT`.
  - Default transport remains `stdio`.
  - Startup runs `server.run(transport=<mode>)`.
- Key Assumptions: FastMCP host/port constructor options remain stable.
- Known Risks: startup wiring tests may need controlled monkeypatching around `FastMCP.run` invocation.

## Runtime Call Stack Review Gate Summary (Required)

| Round | Review Result | Findings Requiring Persisted Updates | New Use Cases Discovered | Persisted Updates Completed | Classification (`Design Impact`/`Requirement Gap`/`Unclear`/`N/A`) | Required Re-Entry Path | Round State (`Reset`/`Candidate Go`/`Go Confirmed`) | Clean Streak After Round |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Pass | No | No | N/A | N/A | N/A | Candidate Go | 1 |
| 2 | Pass | No | No | N/A | N/A | N/A | Go Confirmed | 2 |

## Go / No-Go Decision

- Decision: `Go`
- Evidence:
  - Final review round: 2
  - Clean streak at final round: 2
  - Final review gate line (`Implementation can start`): Yes

## Principles

- Keep startup/config explicit and deterministic.
- Do not introduce backward-compatibility shims.
- Keep tool registration untouched.
- Update tests/docs alongside runtime changes.

## Dependency And Sequencing Map

| Order | File/Module | Depends On | Why This Order |
| --- | --- | --- | --- |
| 1 | `browser-mcp/src/browser_mcp/server.py` | requirements/design basis | central startup/config wiring |
| 2 | `browser-mcp/tests/test_server.py` | server transport/config changes | verify startup wiring + preserve tool behavior |
| 3 | `browser-mcp/README.md` | final behavior | document both transports and env vars |

## Requirement And Design Traceability

| Requirement | Acceptance Criteria ID(s) | Design Section | Use Case / Call Stack | Planned Task ID(s) | Stage 6 Verification (Unit/Integration) | Stage 7 Scenario ID(s) |
| --- | --- | --- | --- | --- | --- | --- |
| R-001 | AC-001, AC-002 | Solution Sketch | UC-001, UC-002 | T-001 | unit | AV-001, AV-002 |
| R-002 | AC-001, AC-002 | Solution Sketch | UC-001, UC-002 | T-001 | unit | AV-001, AV-002 |
| R-003 | AC-003 | Solution Sketch | UC-003 | T-001 | unit | AV-003 |
| R-004 | AC-004 | Solution Sketch | UC-004 | T-001,T-002 | unit | AV-004 |
| R-005 | AC-005 | Solution Sketch | UC-005 | T-001,T-002 | integration | AV-005 |
| R-006 | AC-006 | Solution Sketch | UC-001,UC-002,UC-005 | T-002,T-003 | unit/manual | AV-006 |

## Acceptance Criteria To Stage 7 Mapping (Mandatory)

| Acceptance Criteria ID | Requirement ID | Expected Outcome | Stage 7 Scenario ID(s) | Test Level (`API`/`E2E`) | Initial Status (`Planned`/`Blocked`) |
| --- | --- | --- | --- | --- | --- |
| AC-001 | R-001,R-002 | stdio startup path selected | AV-001 | API | Planned |
| AC-002 | R-001,R-002 | streamable-http startup path selected | AV-002 | API | Planned |
| AC-003 | R-003 | host/port config applied | AV-003 | API | Planned |
| AC-004 | R-004 | invalid transport rejected deterministically | AV-004 | API | Planned |
| AC-005 | R-005 | tools remain registered/working | AV-005 | API | Planned |
| AC-006 | R-006 | docs updated for both transports | AV-006 | API | Planned |

## Decommission / Rename Execution Tasks

| Task ID | Item | Action (`Remove`/`Rename`/`Move`) | Cleanup Steps | Risk Notes |
| --- | --- | --- | --- | --- |
| T-DEL-001 | N/A | N/A | N/A | no decommission scope |

## Step-By-Step Plan

1. T-001: add validated runtime transport settings and startup wiring in `server.py`.
2. T-002: add/update tests for config parsing and startup transport selection.
3. T-003: update README transport docs and run tests.

## Per-File Definition Of Done

| File | Implementation Done Criteria | Unit Test Criteria | Integration Test Criteria | Notes |
| --- | --- | --- | --- | --- |
| `browser-mcp/src/browser_mcp/server.py` | transport/host/port env parsed and validated; `server.run(transport=...)` | new config/startup tests pass | existing tool tests still pass | no tool behavior changes |
| `browser-mcp/tests/test_server.py` | startup wiring tests added | tests pass in local suite | existing in-memory tool tests pass | patch `FastMCP.run` to avoid real startup |
| `browser-mcp/README.md` | documents both modes and env vars | N/A | N/A | include streamable-http example |

## Code Review Gate Plan (Stage 8)

- Gate artifact path: `tickets/in-progress/browser-mcp-transport-modes/code-review.md`
- Scope (source + tests): `server.py`, `test_server.py`, `README.md`.
- line-count measurement command (`effective non-empty`): `rg -n "\\S" <file> | wc -l`
- `501-700` effective-line source files SoC assessment approach: verify no concern bleed from tool logic into transport config.
- `>700` effective-line source file policy and expected action: not expected in this scope.
- per-file diff delta gate (`>220` changed lines) assessment approach: if exceeded, split helper/config extraction.
- Allowed exceptions and required rationale style: concise local-fix rationale only.

## Test Strategy

- Unit tests: startup config parsing and transport validation.
- Integration tests: existing tool session tests in `tests/test_server.py`.
- Stage 6 boundary: file/module/service-level verification only.
- Stage 7 handoff notes for API/E2E testing:
  - expected acceptance criteria count: 6
  - critical flows: stdio start, streamable-http start, invalid transport fail, tool availability unchanged
  - expected scenario count: 6
  - known environment constraints: no external browser required for config/startup path checks
- Stage 8 handoff notes for code review:
  - predicted design-impact hotspots: startup config expansion in `server.py`
  - files likely to exceed size/SoC thresholds: none

## API/E2E Testing Scenario Catalog (Stage 7 Input)

| Scenario ID | Source Type (`Requirement`/`Design-Risk`) | Acceptance Criteria ID(s) | Requirement ID(s) | Use Case ID(s) | Test Level (`API`/`E2E`) | Expected Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| AV-001 | Requirement | AC-001 | R-001,R-002 | UC-001 | API | stdio transport passed to `run()` |
| AV-002 | Requirement | AC-002 | R-001,R-002 | UC-002 | API | streamable-http transport passed to `run()` |
| AV-003 | Requirement | AC-003 | R-003 | UC-003 | API | host/port parsed and applied |
| AV-004 | Requirement | AC-004 | R-004 | UC-004 | API | invalid transport causes deterministic failure |
| AV-005 | Requirement | AC-005 | R-005 | UC-005 | API | existing tool calls in tests still pass |
| AV-006 | Requirement | AC-006 | R-006 | UC-001,UC-002 | API | README documents both startup modes |

## API/E2E Testing Escalation Policy (Stage 7 Guardrail)

- Classification rules for failures:
  - `Local Fix`: bounded startup/test wiring issue; no requirement/design change.
  - `Design Impact`: startup config requires structural separation beyond current boundary.
  - `Requirement Gap`: missing/ambiguous behavior in requirements.
  - `Unclear`: cross-cutting uncertainty.

## Cross-Reference Exception Protocol

| File | Cross-Reference With | Why Unavoidable | Temporary Strategy | Unblock Condition | Design Follow-Up Status | Owner |
| --- | --- | --- | --- | --- | --- | --- |
| None planned | N/A | N/A | N/A | N/A | `Not Needed` | N/A |

## Design Feedback Loop

| Smell/Issue | Evidence (Files/Call Stack) | Design Section To Update | Action | Status |
| --- | --- | --- | --- | --- |
| None at plan finalization | N/A | N/A | monitor during implementation | Pending |
