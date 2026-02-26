# Investigation Notes - browser-mcp-transport-modes

## Sources Consulted
- User request in this session.
- Browser MCP runtime and docs:
  - `browser-mcp/src/browser_mcp/server.py`
  - `browser-mcp/README.md`
  - `browser-mcp/pyproject.toml`
- Browser MCP tests:
  - `browser-mcp/tests/test_server.py`
  - `browser-mcp/tests/conftest.py`
- Existing transport-enabled MCP reference in this repo:
  - `computer-use-mcp/src/computer_use_mcp/config.py`
  - `computer-use-mcp/src/computer_use_mcp/server.py`

## Key Findings
- `browser-mcp` currently starts with `server.run()` and no explicit transport argument; effective mode is stdio.
- `FastMCP` already supports runtime transport selection (`server.run(transport=...)`) and host/port constructor options.
- `browser-mcp` has no dedicated runtime config model; only server name/instructions are read from environment.
- Existing server tests focus on tool behavior via in-memory MCP session and do not currently assert startup transport selection.
- README currently documents stdio-only startup.

## Entrypoints / Boundaries
- Entry point: `browser_mcp.server:main` (`pyproject.toml` script: `browser-mcp-server`).
- Runtime wiring is centralized in `browser-mcp/src/browser_mcp/server.py`:
  - `ServerConfig.from_env()`
  - `create_server(...)`
  - `main()`

## Naming / Structure Conventions
- Server modules follow simple flat layout; config and startup logic currently live in `server.py`.
- Existing package does not use a separate `config.py` file.
- Environment variable naming follows `BROWSER_MCP_*` prefix.

## Constraints
- Keep existing tool registration and behavior unchanged.
- Minimize churn in tests by adding focused config/startup assertions.
- Preserve backward compatibility expectations for local stdio usage.

## Open Unknowns
- Whether to include `sse` as allowed transport (FastMCP supports it) or limit scope strictly to stdio + streamable-http.

## Triage
- Scope classification: `Small`.
- Rationale:
  - Change is limited to startup/config wiring + docs/tests.
  - No tool contract or runtime browser action behavior changes.
  - Expected source impact is localized to `server.py` and test/docs updates.

## Implications For Requirements/Design
- Add explicit transport/host/port env parsing in `server.py` with validation.
- Keep default transport as `stdio` to preserve existing behavior.
- Add tests to verify transport validation and startup call wiring.
