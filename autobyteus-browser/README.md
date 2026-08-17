# AutoByteus Browser

`autobyteus-browser/` is one relocatable browser-automation skill bundle. It contains the agent instructions, Bash launcher, locked Python runtime, task-oriented CLI, shared browser application core, and a retained thin MCP adapter.

## Agent skill and CLI

An agent that loaded this folder's `SKILL.md` derives `SKILL_DIR` from that loaded file and runs:

```bash
SKILL_DIR="<absolute directory containing the loaded SKILL.md>"
bash "$SKILL_DIR/scripts/autobyteus-browser" health-check
bash "$SKILL_DIR/scripts/autobyteus-browser" --help
```

The launcher locates this bundle relative to itself and runs the lockfile with `uv run --frozen`. The first call prepares the environment automatically. No package installation, virtual-environment activation, PATH registration, or vendor-specific skill-home variable is part of the workflow.

Every non-help CLI result is one schema-v1 JSON value on stdout. Diagnostics use stderr. Stable exit categories are:

| Exit | Category |
| --- | --- |
| `0` | Success |
| `2` | Usage, validation, or artifact policy |
| `3` | Bootstrap, configuration, or browser connectivity |
| `4` | Tab discovery or stale target |
| `5` | Browser/application operation |

Use `list-tabs`, `attach-tab`, or `open-tab` to obtain an opaque browser-owned `tab_id`. Pass it explicitly to `navigate`, `read-page`, `screenshot`, `dom-snapshot`, `run-script`, or `close-tab`. IDs remain usable by later independent CLI processes while the Chrome target exists. There is no active-tab fallback, numeric alias registry, daemon, or global Chrome-close command.

Artifact and input paths are workspace-relative. The launcher captures the caller directory in `AUTOBYTEUS_AGENT_WORKSPACE` unless the caller already supplied an absolute existing workspace. Existing output files require `--overwrite`.

## Retained MCP adapter

MCP remains available as a thin adapter over the same `BrowserApplication`:

```json
{
  "mcpServers": {
    "browser": {
      "command": "/absolute/path/to/autobyteus-browser/scripts/autobyteus-browser-mcp"
    }
  }
}
```

The wrapper self-locates and reserves stdout for JSON-RPC. The server defaults to stdio. Streamable HTTP defaults to loopback:

```bash
BROWSER_MCP_TRANSPORT=streamable-http \
BROWSER_MCP_HOST=127.0.0.1 \
BROWSER_MCP_PORT=8765 \
bash scripts/autobyteus-browser-mcp
```

An explicitly configured non-loopback host is accepted but emits a prominent warning: this adapter has no built-in authentication and must be protected by a trusted network or external boundary.

## Development checks

```bash
uv run --frozen --extra test python -m pytest tests/unit
```

Chrome/Chromium over CDP is the supported browser runtime. If AutoByteus launches Chrome on Chrome 136+, configure a non-default `CHROME_USER_DATA_DIR`. For an already-running browser container, configure its `CHROME_REMOTE_DEBUGGING_PORT` and do not replace its profile.
