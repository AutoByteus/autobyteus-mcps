# Implementation Plan

## Scope Classification

- Classification: `Medium`
- Reasoning:
  - New package with multiple public MCP tools and transport/runtime config.
  - Requires structured runner layer plus MCP integration tests.
  - Requires docker-backed scenario validation evidence.
- Workflow Depth:
  - `Medium` -> proposed design doc -> future-state runtime call stack -> future-state runtime call stack review (`Go Confirmed`) -> implementation plan -> implementation progress tracking -> internal code review gate -> aggregated API/E2E validation -> docs sync.

## Upstream Artifacts (Required)

- Workflow state: `tickets/in-progress/x11-computer-use-mcp/workflow-state.md`
- Investigation notes: `tickets/in-progress/x11-computer-use-mcp/investigation-notes.md`
- Requirements: `tickets/in-progress/x11-computer-use-mcp/requirements.md`
  - Current Status: `Design-ready`
- Runtime call stacks: `tickets/in-progress/x11-computer-use-mcp/future-state-runtime-call-stack.md`
- Runtime review: `tickets/in-progress/x11-computer-use-mcp/future-state-runtime-call-stack-review.md`
- Proposed design: `tickets/in-progress/x11-computer-use-mcp/proposed-design.md`

## Plan Maturity

- Current Status: `Ready For Implementation`
- Notes: Stage 4 gate is `Go Confirmed` with two clean rounds and no blockers.

## Preconditions (Must Be True Before Finalizing This Plan)

- `requirements.md` is at least `Design-ready`: Yes
- Acceptance criteria use stable IDs: Yes
- `workflow-state.md` is current and Stage 4 review-gate evidence is recorded: Yes
- Runtime call stack review artifact exists and is current: Yes
- All in-scope use cases reviewed: Yes
- No unresolved blocking findings: Yes
- Runtime review has `Go Confirmed` with two consecutive clean deep-review rounds: Yes

## Runtime Call Stack Review Gate Summary (Required)

| Round | Review Result | Findings Requiring Write-Back | Write-Back Completed | Round State (`Reset`/`Candidate Go`/`Go Confirmed`) | Clean Streak After Round |
| --- | --- | --- | --- | --- | --- |
| 1 | Pass | No | N/A | Candidate Go | 1 |
| 2 | Pass | No | N/A | Go Confirmed | 2 |

## Go / No-Go Decision

- Decision: `Go`
- Evidence:
  - Final review round: 2
  - Clean streak at final round: 2
  - Final review gate line (`Implementation can start`): Yes

## Principles

- Bottom-up: config + runner base first, then server tool wiring, then tests and docs.
- Test-driven: add/maintain unit/integration tests while implementing.
- No backward-compatibility shims or legacy branches.
- Keep runner deterministic and avoid shell interpolation shortcuts.

## Dependency And Sequencing Map

| Order | File/Module | Depends On | Why This Order |
| --- | --- | --- | --- |
| 1 | `computer-use-mcp/src/computer_use_mcp/config.py` | N/A | shared typed settings needed by runner/server |
| 2 | `computer-use-mcp/src/computer_use_mcp/runner.py` | `config.py` | core behavior and validation |
| 3 | `computer-use-mcp/src/computer_use_mcp/server.py` | `config.py`, `runner.py` | MCP surface over validated runner |
| 4 | `computer-use-mcp/tests/test_config.py` | `config.py` | guardrails for env parsing |
| 5 | `computer-use-mcp/tests/test_runner.py` | `runner.py` | command and parse behavior |
| 6 | `computer-use-mcp/tests/test_server.py` | `server.py` | tool wiring and responses |
| 7 | `computer-use-mcp/README.md` + root `README.md` | implementation complete | user-facing docs and project registry |

## Requirement And Design Traceability

| Requirement | Acceptance Criteria ID(s) | Design Section | Use Case / Call Stack | Planned Task ID(s) | Stage 5 Verification (Unit/Integration) | Stage 6 Scenario ID(s) |
| --- | --- | --- | --- | --- | --- | --- |
| R-001 | AC-001 | transport decision | UC-001 | T-003,T-006 | `tests/test_server.py` | AV-001 |
| R-002 | AC-002 | runner health checks | UC-002 | T-002,T-006 | `tests/test_runner.py`,`tests/test_server.py` | AV-002 |
| R-003 | AC-003,AC-004,AC-005 | inspection tools | UC-003,UC-004 | T-002,T-006 | `tests/test_runner.py`,`tests/test_server.py` | AV-003,AV-004,AV-005 |
| R-004 | AC-006 | pointer APIs | UC-005 | T-002,T-006 | `tests/test_runner.py`,`tests/test_server.py` | AV-006 |
| R-005 | AC-007 | keyboard APIs | UC-006 | T-002,T-006 | `tests/test_runner.py`,`tests/test_server.py` | AV-007 |
| R-006 | AC-008 | screenshot API | UC-007 | T-002,T-006 | `tests/test_runner.py`,`tests/test_server.py` | AV-008 |
| R-007 | AC-009 | error schema | UC-008 | T-002,T-006 | all tests | AV-009 |
| R-008 | AC-001,AC-009 | command-prefix path | UC-001,UC-010 | T-001,T-002 | `tests/test_config.py`,`tests/test_runner.py` | AV-001,AV-009 |
| R-009 | AC-010 | testing strategy | UC-009 | T-004,T-005,T-006 | pytest runs | AV-010 |
| R-010 | AC-010 | docker validation flow | UC-009 | T-009 | docker-backed command sequence | AV-010 |

## Acceptance Criteria To Stage 6 Mapping (Mandatory)

| Acceptance Criteria ID | Requirement ID | Expected Outcome | Stage 6 Scenario ID(s) | Validation Level (`API`/`E2E`) | Initial Status (`Planned`/`Blocked`) |
| --- | --- | --- | --- | --- | --- |
| AC-001 | R-001 | HTTP transport startup works | AV-001 | API | Planned |
| AC-002 | R-002 | health readiness structured output | AV-002 | API | Planned |
| AC-003 | R-003 | screen info schema stable | AV-003 | API | Planned |
| AC-004 | R-003 | active/list windows schema stable | AV-004 | API | Planned |
| AC-005 | R-003 | focus behavior by id/name | AV-005 | API | Planned |
| AC-006 | R-004 | pointer behavior + validation | AV-006 | API | Planned |
| AC-007 | R-005 | keyboard behavior + validation | AV-007 | API | Planned |
| AC-008 | R-006 | screenshot output path + metadata | AV-008 | API | Planned |
| AC-009 | R-007 | structured failure taxonomy | AV-009 | API | Planned |
| AC-010 | R-009,R-010 | tests + docker scenario evidence | AV-010 | E2E | Planned |

## Design Delta Traceability (Required For `Medium/Large`)

| Change ID (from proposed design doc) | Change Type | Planned Task ID(s) | Includes Remove/Rename Work | Verification |
| --- | --- | --- | --- | --- |
| C-001..C-006 | Add | T-001,T-002,T-003 | No | unit + integration |
| C-007..C-009 | Add | T-004,T-005,T-006 | No | pytest |
| C-010 | Modify | T-008 | No | doc diff |

## Decommission / Rename Execution Tasks

| Task ID | Item | Action (`Remove`/`Rename`/`Move`) | Cleanup Steps | Risk Notes |
| --- | --- | --- | --- | --- |
| T-DEL-001 | N/A | N/A | N/A | no decommission scope |

## Step-By-Step Plan

1. Create package scaffold and implement validated config models + loaders (`T-001`).
2. Implement runner operations with deterministic subprocess wrappers and structured result schema (`T-002`).
3. Implement MCP server registration + transport mode startup (`T-003`).
4. Add config/runner/server tests and execute targeted pytest suite (`T-004` to `T-006`).
5. Add package README and update root project index (`T-007`,`T-008`).
6. Run docker-backed validation scenario in active Chrome-VNC runtime (`T-009`).
7. Local-fix re-entry (if Stage 6 fails): update focus command behavior for container runtimes lacking EWMH support and rerun Stage 5.5 -> Stage 6 (`T-010`).

## Per-File Definition Of Done

| File | Implementation Done Criteria | Unit Test Criteria | Integration Test Criteria | Notes |
| --- | --- | --- | --- | --- |
| `config.py` | all env fields parsed/validated and typed | `test_config.py` passes | N/A | includes transport + command-prefix |
| `runner.py` | all core tool run functions implemented | `test_runner.py` passes | used by `test_server.py` | no FastMCP imports |
| `server.py` | all tools registered and wired to runner | N/A | `test_server.py` passes | async tool wrappers |

## Internal Code Review Gate Plan (Stage 5.5)

- Gate artifact path: `tickets/in-progress/x11-computer-use-mcp/internal-code-review.md`
- Source-file scope only (exclude tests).
- `>300` line changed source files SoC assessment approach: measure line counts after implementation and verify single-responsibility.
- `>400` line changed source file policy and expected action: classify as design-impact unless explicit split infeasible rationale documented.

| File | Current Line Count | Adds/Expands Functionality (`Yes`/`No`) | SoC Risk (`Low`/`Medium`/`High`) | Required Action (`Keep`/`Split`/`Move`/`Refactor`) | Expected Review Classification if not addressed |
| --- | --- | --- | --- | --- | --- |
| `config.py` | TBD | Yes | Low | Keep | Local Fix |
| `runner.py` | TBD | Yes | Medium | Keep/Split if >300 | Design Impact if >400 unsplit |
| `server.py` | TBD | Yes | Low | Keep | Local Fix |

## Test Strategy

- Unit tests: config parsing and runner command behavior via mocks.
- Integration tests: in-memory MCP server tool invocations.
- Stage 5 boundary: file/module/service-level verification only.
- Stage 6 handoff notes for aggregated validation:
  - expected acceptance criteria count: 10
  - critical flows: health, inspect, focus, pointer, keyboard, screenshot, error taxonomy, docker path
  - expected scenario count: 10
  - known environment constraints: docker container availability and X11 runtime state.

## Aggregated API/E2E Validation Scenario Catalog (Stage 6 Input)

| Scenario ID | Source Type (`Requirement`/`Design-Risk`) | Acceptance Criteria ID(s) | Requirement ID(s) | Use Case ID(s) | Validation Level (`API`/`E2E`) | Expected Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| AV-001 | Requirement | AC-001 | R-001 | UC-001 | API | server starts in streamable-http on configured host/port |
| AV-002 | Requirement | AC-002 | R-002 | UC-002 | API | health payload includes tool/display status |
| AV-003 | Requirement | AC-003 | R-003 | UC-003 | API | screen info returns width/height/root ID |
| AV-004 | Requirement | AC-004 | R-003 | UC-003,UC-004 | API | active/list windows return stable schema |
| AV-005 | Requirement | AC-005 | R-003 | UC-004 | API | focus by id/name works |
| AV-006 | Requirement | AC-006 | R-004 | UC-005 | API | pointer actions + validation behavior pass |
| AV-007 | Requirement | AC-007 | R-005 | UC-006 | API | keyboard actions + validation behavior pass |
| AV-008 | Requirement | AC-008 | R-006 | UC-007 | API | screenshot file + metadata pass |
| AV-009 | Requirement | AC-009 | R-007 | UC-008 | API | structured error taxonomy consistent |
| AV-010 | Requirement | AC-010 | R-009,R-010 | UC-009 | E2E | tests pass and docker-backed control loop evidence recorded |

## Aggregated Validation Escalation Policy (Stage 6 Guardrail)

- Follow workflow classification path exactly for failures:
  - `Local Fix` only if no requirements/design change and no boundary drift.
  - `Design Impact` when boundary drift or architecture update needed.
  - `Requirement Gap` when missing/ambiguous requirement is discovered.
- No code edits before required upstream artifact updates are logged.

## Cross-Reference Exception Protocol

| File | Cross-Reference With | Why Unavoidable | Temporary Strategy | Unblock Condition | Design Follow-Up Status | Owner |
| --- | --- | --- | --- | --- | --- | --- |
| None planned | N/A | N/A | N/A | N/A | Not Needed | N/A |

## Design Feedback Loop

| Smell/Issue | Evidence (Files/Call Stack) | Design Section To Update | Action | Status |
| --- | --- | --- | --- | --- |
| None at plan finalization | N/A | N/A | monitor during implementation | Pending |
| focus_window uses `windowactivate --sync` and can hang in Chrome-VNC container | Stage 6 docker validation AV-005 timeout | runner focus behavior details | add non-blocking activation path (remove `--sync`) and revalidate | Updated |
| mouse move/drag paths using `--sync` can hang in container runtime | Stage 6 docker validation AV-006 partial failure | runner pointer behavior details | remove sync move flags and revalidate pointer scenarios | Updated |
