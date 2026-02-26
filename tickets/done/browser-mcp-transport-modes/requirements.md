# Requirements - browser-mcp-transport-modes

## Status
- Design-ready

## Goal / Problem Statement
- Enable `browser-mcp` to run in both `stdio` and `streamable-http` transports.
- Keep existing browser tool contracts and behavior unchanged while adding startup transport configurability.

## Scope Classification
- Classification: Small
- Rationale:
  - Expected source impact is localized to startup/config wiring in `browser_mcp.server`.
  - Tool implementations and runtime browser control behavior are unchanged.
  - Test/doc updates are focused and non-architectural.

## In-Scope Use Cases
- UC-001: Start server in stdio mode for local MCP clients.
- UC-002: Start server in streamable-http mode for container/networked clients.
- UC-003: Configure host/port when streamable-http mode is selected.
- UC-004: Reject invalid transport values at startup with explicit error message.
- UC-005: Preserve existing tool registration and callable behavior across transports.

## Out Of Scope
- New browser tools or behavior changes for existing tools.
- Authentication/security layer changes for HTTP endpoint.
- Transport support beyond `stdio` and `streamable-http` in this ticket.

## Requirements
- R-001: Server startup must parse transport mode from environment.
  - Expected outcome: startup picks configured mode without code changes.
- R-002: Server must support both `stdio` and `streamable-http` runtime modes.
  - Expected outcome: startup runs successfully in either mode.
- R-003: Server must parse and validate HTTP host/port settings.
  - Expected outcome: host/port are applied for streamable-http mode and invalid ports fail fast.
- R-004: Invalid transport setting must fail with deterministic startup validation error.
  - Expected outcome: unsupported values cause immediate `SystemExit` with actionable message.
- R-005: Existing server configuration fields (name/instructions/workspace init) and tool registration remain intact.
  - Expected outcome: all existing tool tests keep passing.
- R-006: Automated tests and docs must cover dual-transport startup behavior.
  - Expected outcome: tests assert transport/config wiring; README documents both modes.

## Acceptance Criteria
- AC-001: With `BROWSER_MCP_TRANSPORT=stdio`, `main()` calls `server.run(transport="stdio")`.
- AC-002: With `BROWSER_MCP_TRANSPORT=streamable-http`, `main()` calls `server.run(transport="streamable-http")`.
- AC-003: `BROWSER_MCP_HOST` and `BROWSER_MCP_PORT` are parsed and applied to FastMCP server construction.
- AC-004: Unsupported transport values raise deterministic validation error before `server.run`.
- AC-005: Existing browser tool registration remains available (current server tests still pass).
- AC-006: README documents both stdio and streamable-http startup configuration.

## Constraints / Dependencies
- Continue using FastMCP startup model in `browser_mcp.server`.
- Keep `BROWSER_MCP_NAME`, `BROWSER_MCP_INSTRUCTIONS`, and workspace initialization behavior.
- Keep default behavior compatible with current users (default transport remains `stdio`).

## Assumptions
- FastMCP transport string `streamable-http` is stable and supported in current dependency version.
- Host/port values are still needed in stdio mode for config consistency even if not used by runtime transport.

## Open Questions / Risks
- Whether future requirement should add `sse`; currently intentionally excluded for explicit scope control.
- Existing real integration tests may depend on local browser setup and can be skipped in this ticket if unrelated to transport wiring.

## Requirement Coverage Map
| requirement_id | Covered By Use Case IDs |
| --- | --- |
| R-001 | UC-001, UC-002 |
| R-002 | UC-001, UC-002 |
| R-003 | UC-002, UC-003 |
| R-004 | UC-004 |
| R-005 | UC-005 |
| R-006 | UC-001, UC-002, UC-005 |

## Acceptance Criteria Coverage Map To Stage 7 Scenarios
| acceptance_criteria_id | Planned Stage 7 Scenario IDs |
| --- | --- |
| AC-001 | AV-001 |
| AC-002 | AV-002 |
| AC-003 | AV-003 |
| AC-004 | AV-004 |
| AC-005 | AV-005 |
| AC-006 | AV-006 |
