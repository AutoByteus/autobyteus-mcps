# Proposed Design Document

## Design Version

- Current Version: `v1`

## Revision History

| Version | Trigger | Summary Of Changes | Related Review Round |
| --- | --- | --- | --- |
| v1 | Initial draft | Defined new `computer-use-mcp` package architecture, tool surface, transport model, and test strategy. | 1 |

## Artifact Basis

- Investigation Notes: `tickets/in-progress/x11-computer-use-mcp/investigation-notes.md`
- Requirements: `tickets/in-progress/x11-computer-use-mcp/requirements.md`
- Requirements Status: `Design-ready`

## Summary

Create a new MCP package `computer-use-mcp` focused on deterministic X11 desktop control primitives, with HTTP-first transport support for containerized deployments and optional command-prefix execution for host-to-container control.

## Goals

- Deliver deterministic computer-control MCP tools for X11 environments.
- Support `streamable-http` transport for Docker-friendly deployment.
- Provide structured, machine-parseable failure contracts for robust agent retry behavior.
- Keep architecture simple: config parsing, command runner, and MCP tool layer separated.

## Legacy Removal Policy (Mandatory)

- Policy: `No backward compatibility; remove legacy code paths.`
- Required action: this is a net-new package; no legacy carry-over layer will be introduced.

## Requirements And Use Cases

| Requirement ID | Description | Acceptance Criteria ID(s) | Acceptance Criteria Summary | Use Case IDs |
| --- | --- | --- | --- | --- |
| R-001 | HTTP transport support | AC-001 | MCP starts in `streamable-http` with env host/port | UC-001, UC-009 |
| R-002 | Health/tooling readiness | AC-002 | Tool availability + display probe output | UC-002 |
| R-003 | Screen/window inspection | AC-003, AC-004 | Geometry + active/listed window metadata | UC-003, UC-004 |
| R-004 | Pointer tools | AC-006 | move/click/scroll/drag with validation | UC-005 |
| R-005 | Keyboard tools | AC-007 | type text + key combos | UC-006 |
| R-006 | Screenshot capture | AC-008 | screenshot path + metadata | UC-007 |
| R-007 | Structured error taxonomy | AC-009 | stable error_type in all failures | UC-008 |
| R-008 | Command execution context | AC-001, AC-009 | direct execution + optional command-prefix mode | UC-001, UC-009 |
| R-009 | Automated tests | AC-010 | config/runner/server test coverage | UC-009 |
| R-010 | Docker-backed validation | AC-010 | scenario evidence in Chrome-VNC | UC-009 |

## Codebase Understanding Snapshot (Pre-Design Mandatory)

| Area | Findings | Evidence (files/functions) | Open Unknowns |
| --- | --- | --- | --- |
| Entrypoints / Boundaries | Existing MCPs isolate `config`, `runner`, `server` concerns. | `ssh-mcp/src/ssh_mcp/{config.py,runner.py,server.py}` | None blocking |
| Current Naming Conventions | repo folder kebab-case, Python module snake_case | `browser-mcp`, `ssh-mcp`, `browser_mcp`, `ssh_mcp` | None |
| Impacted Modules / Responsibilities | New package can be fully isolated; no existing module rewrite required | repo root package layout | None |
| Data / Persistence / External IO | command-driven tooling, local file output for screenshots, subprocess execution | live checks: `docker exec llm-server-0 ...` | screenshot backend fallback policy |

## Current State (As-Is)

- No dedicated X11 MCP package in this repo.
- Existing MCPs are mostly stdio-default entrypoints.
- Chrome-VNC runtime already contains required X11 binaries and active desktop stack.

## Target State (To-Be)

- New package `computer-use-mcp` exposing X11 control tools with typed/structured outputs.
- HTTP transport available through env-driven config and FastMCP settings.
- Tests cover validation, command construction, and MCP tool wiring.
- Docker-backed validation scenario recorded in ticket artifacts.

## Architecture Direction Decision (Mandatory)

- Chosen direction: add new isolated package with layered structure (`config` -> `runner` -> `server`) and no modifications to existing MCP packages.
- Rationale (`complexity`, `testability`, `operability`, `evolution cost`):
  - Low coupling and clear ownership.
  - Runner layer can be unit-tested with subprocess stubs.
  - Server layer remains thin and easy to extend with new tools.
  - Minimal operational risk to current MCPs.
- Layering fitness assessment (are current layering and interactions still coherent?): `Yes`
- Outcome (`Keep`/`Add`/`Split`/`Merge`/`Move`/`Remove`): `Add`

### Optional Alternatives (Use For Non-Trivial Or Uncertain Changes)

| Option | Summary | Pros | Cons | Decision (`Chosen`/`Rejected`) | Rationale |
| --- | --- | --- | --- | --- | --- |
| A | Add X11 tools into existing `browser-mcp` | fewer packages | mixes browser DOM automation with OS desktop control concerns | Rejected | boundary drift and larger blast radius |
| B | New `computer-use-mcp` package | clean responsibility boundary and transport autonomy | new package overhead | Chosen | clearer ownership and easier testing |

## Change Inventory (Delta)

| Change ID | Change Type (`Add`/`Modify`/`Rename/Move`/`Remove`) | Current Path | Target Path | Rationale | Impacted Areas | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| C-001 | Add | N/A | `computer-use-mcp/pyproject.toml` | package metadata and script entrypoint | packaging | new package |
| C-002 | Add | N/A | `computer-use-mcp/README.md` | usage and env docs | docs | includes HTTP examples |
| C-003 | Add | N/A | `computer-use-mcp/src/computer_use_mcp/config.py` | validated settings and env parsing | runtime config | includes transport + command prefix |
| C-004 | Add | N/A | `computer-use-mcp/src/computer_use_mcp/runner.py` | deterministic X11 command execution | core runtime | structured result builders |
| C-005 | Add | N/A | `computer-use-mcp/src/computer_use_mcp/server.py` | MCP tool registration and transport startup | MCP boundary | tool API contracts |
| C-006 | Add | N/A | `computer-use-mcp/src/computer_use_mcp/__init__.py` | package export | packaging | minimal |
| C-007 | Add | N/A | `computer-use-mcp/tests/test_config.py` | settings validation tests | unit tests | input guard checks |
| C-008 | Add | N/A | `computer-use-mcp/tests/test_runner.py` | runner behavior tests | unit tests | subprocess mocking |
| C-009 | Add | N/A | `computer-use-mcp/tests/test_server.py` | MCP tool wiring tests | integration tests | in-memory MCP session |
| C-010 | Modify | `README.md` | `README.md` | register new MCP project | repo docs | table update |

## Target Architecture Shape And Boundaries (Mandatory)

| Layer/Boundary | Purpose | Owns | Must Not Own | Notes |
| --- | --- | --- | --- | --- |
| Config Layer (`config.py`) | Environment parsing + validation | settings dataclasses and field validators | command execution logic | deterministic normalization |
| Runner Layer (`runner.py`) | Command construction + subprocess execution + parsing | X11 operation implementations | MCP tool registration | no FastMCP imports |
| MCP Layer (`server.py`) | Tool registration and context progress | MCP tool functions + transport startup | command parsing internals | thin adapter layer |
| Test Layer (`tests/*`) | behavior verification | config, runner, server tests | production runtime logic | isolates regression checks |

## File And Module Breakdown

| File/Module | Change Type | Layer / Boundary | Concern / Responsibility | Public APIs | Inputs/Outputs | Dependencies |
| --- | --- | --- | --- | --- | --- | --- |
| `config.py` | Add | Config | Parse env and validate runtime settings | `load_settings`, `ServerConfig` | env -> typed settings | stdlib |
| `runner.py` | Add | Core Runtime | Execute X11 actions and parse results | `run_*` functions per tool | tool args -> structured dict | `subprocess`, `pathlib` |
| `server.py` | Add | MCP | Register MCP tools + run transport | `create_server`, `main` | settings + tool params -> MCP responses | `mcp.server.fastmcp` |

## Layer-Appropriate Separation Of Concerns Check

- UI/frontend scope: N/A.
- Non-UI scope: responsibilities split across config/runner/server modules.
- Integration/infrastructure scope: X11 command adapter is isolated in runner.

## Naming Decisions (Natural And Implementation-Friendly)

| Item Type (`File`/`Module`/`API`) | Current Name | Proposed Name | Reason | Notes |
| --- | --- | --- | --- | --- |
| File | N/A | `computer-use-mcp` | matches user-facing "computer use" target | repo folder |
| Module | N/A | `computer_use_mcp` | python naming convention | package path |
| API | N/A | `x11_*` tool prefix | clearly conveys desktop X11 semantics | avoids collisions |

## Naming Drift Check (Mandatory)

| Item | Current Responsibility | Does Name Still Match? (`Yes`/`No`) | Corrective Action (`Rename`/`Split`/`Move`/`N/A`) | Mapped Change ID |
| --- | --- | --- | --- | --- |
| `computer-use-mcp` package | desktop computer control MCP | Yes | N/A | C-001..C-009 |
| `x11_*` tools | X11 deterministic control primitives | Yes | N/A | C-005 |

## Existing-Structure Bias Check (Mandatory)

| Candidate Area | Current-File-Layout Bias Risk | Architecture-First Alternative | Decision | Why |
| --- | --- | --- | --- | --- |
| Reuse `browser-mcp` for X11 control | High | Isolated `computer-use-mcp` package | Change | keeps browser and OS control concerns separate |

## Anti-Hack Check (Mandatory)

| Candidate Change | Shortcut/Hack Risk | Proper Structural Fix | Decision | Notes |
| --- | --- | --- | --- | --- |
| Put all logic in `server.py` tool callbacks | High | split into `config.py` + `runner.py` + thin server adapter | Reject shortcut | preserves maintainability |

## Dependency Flow And Cross-Reference Risk

| Module/File | Upstream Dependencies | Downstream Dependents | Cross-Reference Risk | Mitigation / Boundary Strategy |
| --- | --- | --- | --- | --- |
| `config.py` | env/stdlib | `runner.py`, `server.py` | Low | keep validation pure |
| `runner.py` | `config.py`, stdlib | `server.py`, tests | Medium | avoid MCP imports in runner |
| `server.py` | `config.py`, `runner.py`, FastMCP | runtime entrypoint | Low | thin adapter only |

## Allowed Dependency Direction (Mandatory)

- Allowed direction rules: `server.py -> runner.py -> config.py` and `server.py -> config.py`.
- Temporary boundary violations and cleanup deadline: none.

## Decommission / Cleanup Plan

| Item To Remove/Rename | Cleanup Actions | Legacy Removal Notes | Verification |
| --- | --- | --- | --- |
| None (new package) | N/A | No legacy code introduced | N/A |

## Data Models (If Needed)

- `X11Settings`: runtime execution and transport config.
- `ServerConfig`: MCP name/instructions override.
- Structured operation result payloads with stable keys (`ok`, `action`, `error_type`, etc.).

## Error Handling And Edge Cases

- Validation failures: invalid coordinates/buttons/text length/window selectors.
- Dependency failures: required binaries missing.
- Execution failures: subprocess non-zero exit with stderr payload.
- Timeout failures: command exceeds configured timeout.
- Empty search/focus results return non-crash structured output (either empty list or validation/execution classification depending on API contract).

## Use-Case Coverage Matrix (Design Gate)

| use_case_id | Requirement | Use Case | Primary Path Covered (`Yes`/`No`) | Fallback Path Covered (`Yes`/`No`/`N/A`) | Error Path Covered (`Yes`/`No`/`N/A`) | Runtime Call Stack Section |
| --- | --- | --- | --- | --- | --- | --- |
| UC-001 | R-001,R-008 | HTTP startup + transport config | Yes | N/A | Yes | UC-001 |
| UC-002 | R-002 | health/tooling readiness | Yes | N/A | Yes | UC-002 |
| UC-003 | R-003 | screen and active window inspection | Yes | N/A | Yes | UC-003 |
| UC-004 | R-003 | list/focus windows | Yes | Yes | Yes | UC-004 |
| UC-005 | R-004 | pointer controls | Yes | Yes | Yes | UC-005 |
| UC-006 | R-005 | keyboard controls | Yes | N/A | Yes | UC-006 |
| UC-007 | R-006 | screenshot capture | Yes | Yes | Yes | UC-007 |
| UC-008 | R-007 | structured error handling | Yes | N/A | Yes | UC-008 |
| UC-009 | R-009,R-010 | docker-backed scenario validation | Yes | N/A | Yes | UC-009 |

## Performance / Security Considerations

- Keep command execution bounded with configurable timeout.
- Limit text/key payload sizes to avoid command abuse and accidental huge payloads.
- Keep endpoint security externalized (network/container policy), but avoid unsafe shell interpolation inside runner.

## Migration / Rollout (If Needed)

- No migration needed; package is additive.
- Rollout: install new package, expose configured HTTP port, register MCP in agent runtime.

## Change Traceability To Implementation Plan

| Change ID | Implementation Plan Task(s) | Verification (Unit/Integration/API/E2E) | Status |
| --- | --- | --- | --- |
| C-001..C-006 | T-001..T-006 | Unit + MCP integration + AV scenarios | Planned |
| C-007..C-009 | T-007..T-009 | Pytest | Planned |
| C-010 | T-010 | doc check | Planned |

## Design Feedback Loop Notes (From Review/Implementation)

| Date | Trigger (Review/File/Test/Blocker) | Classification (`Local Fix`/`Design Impact`/`Requirement Gap`) | Design Smell | Requirements Updated? | Design Update Applied | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-02-26 | Initial draft | N/A | N/A | No | v1 authored | Open for review |

## Open Questions

- If first integration cycle shows flaky window discovery under load, should we add optional retry/backoff settings in runner APIs.
