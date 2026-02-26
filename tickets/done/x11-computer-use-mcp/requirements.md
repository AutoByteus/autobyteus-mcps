# Requirements - x11-computer-use-mcp

## Status
- Design-ready

## Goal / Problem Statement
- Provide a dedicated MCP for Linux desktop/X11 computer control so agents can operate software inside Dockerized desktop containers (for example Chrome-VNC based runtimes).
- Remove the current usability bottleneck of STDIO-only deployment by making HTTP transport a first-class option for containerized execution with exposed ports.

## Scope Classification
- Classification: Medium
- Rationale:
  - New MCP package with a non-trivial tool surface (inspection, mouse, keyboard, screenshot, focus control).
  - Runtime transport support must explicitly include HTTP for container deployment.
  - Requires deterministic command execution and structured error handling across process boundaries.
  - Requires automated verification beyond pure unit tests (MCP-level and Docker-backed scenario validation).

## In-Scope Use Cases
- UC-001: Start MCP in HTTP mode with configurable host/port and pass health check.
- UC-002: Verify X11 runtime/tool availability and display readiness.
- UC-003: Inspect root screen geometry and currently active window.
- UC-004: Enumerate windows and focus a target window.
- UC-005: Execute pointer actions (move, click, scroll, drag).
- UC-006: Execute keyboard actions (type text and key combos/hotkeys).
- UC-007: Capture screenshot to a predictable output path.
- UC-008: Return structured, machine-parseable errors for invalid inputs and command/runtime failures.
- UC-009: Execute an end-to-end agent control loop in Chrome-VNC environment (inspect -> focus -> input/action -> screenshot).

## Out Of Scope (Current Ticket)
- OCR, semantic UI understanding, and vision-based target detection.
- Wayland-native control.
- Multi-display orchestration and remote clipboard synchronization protocols.

## Requirements
- R-001: MCP shall support HTTP transport mode (`streamable-http`) with configurable bind host and port.
  - Expected outcome: service runs and accepts MCP HTTP sessions at configured endpoint.
- R-002: MCP shall expose a health/tooling readiness tool.
  - Expected outcome: tool reports display target, required X11 binary availability, and probe readiness.
- R-003: MCP shall expose screen/window inspection tools.
  - Expected outcome: tools return structured geometry/metadata for screen, active window, and searched windows.
- R-004: MCP shall expose deterministic pointer control tools.
  - Expected outcome: move/click/scroll/drag execute through X11 commands and return resulting cursor state.
- R-005: MCP shall expose deterministic keyboard tools.
  - Expected outcome: text typing and key combo actions execute with configurable delay/clearmodifier behavior.
- R-006: MCP shall expose screenshot capture tool.
  - Expected outcome: screenshot is written to requested or generated path with returned path + dimensions metadata.
- R-007: MCP shall return structured error taxonomy.
  - Expected outcome: failures are classified (`validation`, `dependency`, `execution`, `timeout`) with stable fields.
- R-008: MCP shall support configurable command execution context for X11 targeting.
  - Expected outcome: default direct execution works in-container; optional command prefix supports host-driven container exec mode.
- R-009: MCP shall include automated tests for config parsing, runner behavior, and MCP tool invocation.
  - Expected outcome: repeatable local tests validate command construction, validation, and tool wiring.
- R-010: Ticket deliverables shall include docker-backed validation evidence for Chrome-VNC runtime.
  - Expected outcome: at least one automated or scripted validation path demonstrates in-container X11 action flow.

## Acceptance Criteria
- AC-001: `main()` supports `X11_MCP_TRANSPORT=streamable-http` and binds to `X11_MCP_HOST`/`X11_MCP_PORT`.
- AC-002: `x11_health_check` returns `ok`, `display`, `tool_status`, `missing_tools`, and probe result fields.
- AC-003: `x11_get_screen_info` returns width/height and root window metadata with numeric fields.
- AC-004: `x11_get_active_window` and `x11_list_windows` return stable structured window metadata including IDs.
- AC-005: `x11_focus_window` can focus by `window_id` or `name_contains` and returns focused target metadata.
- AC-006: pointer tools validate inputs and return deterministic output; invalid inputs return `error_type=validation`.
- AC-007: keyboard tools support text + key combo actions and enforce max input-size guards.
- AC-008: screenshot tool writes output file, returns file path + geometry metadata, and validates output path input.
- AC-009: command/runtime failures return structured `error_type` and non-crashing MCP responses.
- AC-010: test suite includes runner/config + MCP tool tests and a Docker-backed validation scenario for Chrome-VNC environment.

## Constraints / Dependencies
- Linux X11 runtime with valid `DISPLAY` (default `:99` for Chrome-VNC base runtime).
- Required binaries: `xdotool`, `xwininfo`, `xprop`, `scrot` (plus optional `xwd`, `xclip` for future expansion).
- MCP framework dependency: `mcp>=1.13.1` (consistent with existing repo MCPs).
- Docker availability for Chrome-VNC validation scenario.

## Assumptions
- Exposing MCP HTTP port in container network is acceptable in target deployment.
- Security/network access controls for HTTP MCP endpoint are handled by outer deployment boundary.
- No backward compatibility obligation with legacy/previous computer-control tool naming.

## Open Questions / Risks
- Whether to make HTTP the default transport or require explicit env configuration.
- Potential mismatch between host-side prefix execution and container environment behavior if container name/lifecycle changes.
- X11 command timing variability under heavy container load may require bounded retries in future iterations.

## Requirement Coverage Map
| requirement_id | Covered By Use Case IDs |
| --- | --- |
| R-001 | UC-001, UC-009 |
| R-002 | UC-002 |
| R-003 | UC-003, UC-004 |
| R-004 | UC-005, UC-009 |
| R-005 | UC-006, UC-009 |
| R-006 | UC-007, UC-009 |
| R-007 | UC-008 |
| R-008 | UC-001, UC-009 |
| R-009 | UC-009 |
| R-010 | UC-009 |

## Acceptance Criteria Coverage Map To Stage 6 Scenarios
| acceptance_criteria_id | Planned Stage 6 Scenario IDs |
| --- | --- |
| AC-001 | AV-001 |
| AC-002 | AV-002 |
| AC-003 | AV-003 |
| AC-004 | AV-004 |
| AC-005 | AV-005 |
| AC-006 | AV-006 |
| AC-007 | AV-007 |
| AC-008 | AV-008 |
| AC-009 | AV-009 |
| AC-010 | AV-010 |
