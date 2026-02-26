# Future-State Runtime Call Stacks (Debug-Trace Style)

Use this document as a future-state (`to-be`) execution model derived from the design basis.
Prefer exact `file:function` frames, explicit branching, and clear state/persistence boundaries.
Do not treat this document as an as-is trace of current code behavior.

## Conventions

- Frame format: `path/to/file.py:function_name(args?)`
- Boundary tags:
  - `[ENTRY]` external entrypoint
  - `[ASYNC]` async boundary
  - `[STATE]` in-memory mutation
  - `[IO]` file/network/process IO
  - `[FALLBACK]` non-primary branch
  - `[ERROR]` error path

## Design Basis

- Scope Classification: `Small`
- Call Stack Version: `v1`
- Requirements: `tickets/in-progress/browser-mcp-transport-modes/requirements.md` (status `Design-ready`)
- Source Artifact:
  - `tickets/in-progress/browser-mcp-transport-modes/implementation-plan.md` (solution sketch)
- Source Design Version: `v1-draft`
- Referenced Sections:
  - `Solution Sketch`
  - `Step-By-Step Plan`

## Future-State Modeling Rule (Mandatory)

- Model target design behavior even when current code diverges.
- No migration branches are needed for this small startup/config enhancement.

## Use Case Index (Stable IDs)

| use_case_id | Source Type (`Requirement`/`Design-Risk`) | Requirement ID(s) | Design-Risk Objective (if source=`Design-Risk`) | Use Case Name | Coverage Target (Primary/Fallback/Error) |
| --- | --- | --- | --- | --- | --- |
| UC-001 | Requirement | R-001,R-002 | N/A | Start in stdio mode | Yes/Yes/Yes |
| UC-002 | Requirement | R-001,R-002 | N/A | Start in streamable-http mode | Yes/Yes/Yes |
| UC-003 | Requirement | R-003 | N/A | Apply host/port config for HTTP mode | Yes/Yes/Yes |
| UC-004 | Requirement | R-004 | N/A | Reject invalid transport config | Yes/N/A/Yes |
| UC-005 | Requirement | R-005,R-006 | N/A | Preserve tool registration and behavior | Yes/N/A/Yes |

## Transition Notes

- Temporary migration behavior needed: none.
- Retirement plan for temporary logic: N/A.

## Use Case: UC-001 [Start in stdio mode]

### Goal
- Start `browser-mcp` in stdio transport when configured explicitly or by default.

### Preconditions
- Environment contains either `BROWSER_MCP_TRANSPORT=stdio` or transport unset.

### Expected Outcome
- FastMCP server starts via `server.run(transport="stdio")` with existing tools registered.

### Primary Runtime Call Stack

```text
[ENTRY] browser-mcp/src/browser_mcp/server.py:main()
├── browser-mcp/src/browser_mcp/server.py:logging.basicConfig(...)
├── browser-mcp/src/browser_mcp/server.py:RuntimeConfig.from_env(...) [STATE]
│   ├── browser-mcp/src/browser_mcp/server.py:_parse_transport(...) [STATE]
│   └── browser-mcp/src/browser_mcp/server.py:_parse_port(...) [STATE]
├── browser-mcp/src/browser_mcp/server.py:ServerConfig.from_env(...) [STATE]
├── browser-mcp/src/browser_mcp/server.py:create_server(config, runtime_config)
│   ├── mcp.server.fastmcp:FastMCP.__init__(name, instructions, host, port)
│   ├── browser-mcp/src/browser_mcp/tabs.py:TabManager.__init__() [STATE]
│   └── browser-mcp/src/browser_mcp/tools/__init__.py:register_tools(...) [STATE]
└── mcp.server.fastmcp:FastMCP.run(transport="stdio") [IO]
```

### Branching / Fallback Paths

```text
[FALLBACK] if BROWSER_MCP_TRANSPORT is unset
browser-mcp/src/browser_mcp/server.py:RuntimeConfig.from_env(...)
└── browser-mcp/src/browser_mcp/server.py:_parse_transport(default="stdio")
```

```text
[ERROR] if runtime config parsing fails
browser-mcp/src/browser_mcp/server.py:main()
└── raise SystemExit("Invalid browser MCP configuration: ...")
```

### Coverage Status
- Primary Path: `Covered`
- Fallback Path: `Covered`
- Error Path: `Covered`

## Use Case: UC-002 [Start in streamable-http mode]

### Goal
- Start `browser-mcp` in streamable-http transport for network-accessible MCP clients.

### Preconditions
- Environment contains `BROWSER_MCP_TRANSPORT=streamable-http`.

### Expected Outcome
- FastMCP server starts via `server.run(transport="streamable-http")`.

### Primary Runtime Call Stack

```text
[ENTRY] browser-mcp/src/browser_mcp/server.py:main()
├── browser-mcp/src/browser_mcp/server.py:RuntimeConfig.from_env(...) [STATE]
├── browser-mcp/src/browser_mcp/server.py:create_server(config, runtime_config)
└── mcp.server.fastmcp:FastMCP.run(transport="streamable-http") [IO]
```

### Branching / Fallback Paths

```text
[FALLBACK] if host/port are not set explicitly
browser-mcp/src/browser_mcp/server.py:RuntimeConfig.from_env(...)
├── default host = "0.0.0.0"
└── default port = 8765
```

```text
[ERROR] if FastMCP run fails to bind host/port
mcp.server.fastmcp:FastMCP.run(...)
└── exception bubbled to process runtime [IO]
```

### Coverage Status
- Primary Path: `Covered`
- Fallback Path: `Covered`
- Error Path: `Covered`

## Use Case: UC-003 [Apply host/port config for HTTP mode]

### Goal
- Ensure host/port environment values are parsed and applied to server construction.

### Preconditions
- `BROWSER_MCP_TRANSPORT=streamable-http`.
- Optional `BROWSER_MCP_HOST`, `BROWSER_MCP_PORT` values supplied.

### Expected Outcome
- `FastMCP(host=<parsed_host>, port=<parsed_port>)` receives validated values.

### Primary Runtime Call Stack

```text
[ENTRY] browser-mcp/src/browser_mcp/server.py:RuntimeConfig.from_env(...)
├── browser-mcp/src/browser_mcp/server.py:_require_non_empty(BROWSER_MCP_HOST)
├── browser-mcp/src/browser_mcp/server.py:_parse_port(BROWSER_MCP_PORT)
└── browser-mcp/src/browser_mcp/server.py:create_server(...)
    └── mcp.server.fastmcp:FastMCP.__init__(host, port)
```

### Branching / Fallback Paths

```text
[FALLBACK] if host/port envs are unset
RuntimeConfig.from_env(...)
├── host default "0.0.0.0"
└── port default 8765
```

```text
[ERROR] if port is invalid (non-int or out of range)
_parse_port(...)
└── raise ConfigError -> main() maps to SystemExit
```

### Coverage Status
- Primary Path: `Covered`
- Fallback Path: `Covered`
- Error Path: `Covered`

## Use Case: UC-004 [Reject invalid transport config]

### Goal
- Prevent unsupported transport values from reaching `FastMCP.run`.

### Preconditions
- `BROWSER_MCP_TRANSPORT` set to unsupported value.

### Expected Outcome
- Startup exits deterministically with validation error.

### Primary Runtime Call Stack

```text
[ENTRY] browser-mcp/src/browser_mcp/server.py:main()
├── browser-mcp/src/browser_mcp/server.py:RuntimeConfig.from_env(...)
│   └── browser-mcp/src/browser_mcp/server.py:_parse_transport(...)
│       └── raise ConfigError("BROWSER_MCP_TRANSPORT must be one of: ...")
└── browser-mcp/src/browser_mcp/server.py:main() catches ConfigError -> SystemExit [ERROR]
```

### Branching / Fallback Paths
- N/A.

### Coverage Status
- Primary Path: `Covered`
- Fallback Path: `N/A`
- Error Path: `Covered`

## Use Case: UC-005 [Preserve tool registration and behavior]

### Goal
- Keep existing browser tool set and behavior unchanged after startup wiring changes.

### Preconditions
- Server created through `create_server(...)` with valid config.

### Expected Outcome
- Existing tools remain registered and current test suite behavior stays green.

### Primary Runtime Call Stack

```text
[ENTRY] browser-mcp/src/browser_mcp/server.py:create_server(config, runtime_config)
├── mcp.server.fastmcp:FastMCP.__init__(...)
├── browser-mcp/src/browser_mcp/tabs.py:TabManager.__init__() [STATE]
└── browser-mcp/src/browser_mcp/tools/__init__.py:register_tools(server, tab_manager) [STATE]
```

### Branching / Fallback Paths
- N/A.

### Coverage Status
- Primary Path: `Covered`
- Fallback Path: `N/A`
- Error Path: `Covered`
