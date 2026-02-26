# Investigation Notes - x11-computer-use-mcp

## Sources Consulted
- User request in this session.
- Existing MCP implementations:
  - `browser-mcp/src/browser_mcp/server.py`
  - `ssh-mcp/src/ssh_mcp/server.py`
  - `ssh-mcp/src/ssh_mcp/config.py`
  - `ssh-mcp/src/ssh_mcp/runner.py`
  - `autobyteus-image-audio/src/image_audio_mcp/server.py`
- Existing MCP package/test patterns:
  - `ssh-mcp/pyproject.toml`
  - `browser-mcp/pyproject.toml`
  - `ssh-mcp/tests/test_server.py`
  - `browser-mcp/tests/test_server.py`
  - `autobyteus-image-audio/tests/test_integration.py`
- FastMCP runtime behavior (installed package source):
  - `/home/ryan-ai/.local/lib/python3.10/site-packages/mcp/server/fastmcp/server.py`
- Sibling Docker/runtime context:
  - `../autobyteus_rpa_llm_server/docker/README.md`
  - `../autobyteus_rpa_llm_server/docker/Dockerfile`
  - `../autobyteus_rpa_llm_server/docker/docker-compose.yml`
- Live runtime checks against active container `llm-server-0`:
  - `docker exec llm-server-0 which xdotool xwininfo xprop scrot xwd xclip`
  - `docker exec llm-server-0 xdotool getmouselocation --shell`
  - `docker exec llm-server-0 xwininfo -root -tree`
  - `docker exec llm-server-0 supervisorctl -u dummy -p dummy status`
  - Stage 6 runtime checks:
    - `docker exec llm-server-0 env DISPLAY=:99 xdotool windowactivate --sync <id>` (hang/timeout observed)
    - `docker exec llm-server-0 env DISPLAY=:99 xdotool windowactivate <id>` (success)
    - `docker exec llm-server-0 env DISPLAY=:99 xdotool mousemove --sync ...` (hang/timeout observed in drag flow)

## Key Findings
- FastMCP supports `stdio`, `sse`, and `streamable-http` transports through `FastMCP.run(transport=...)`.
- FastMCP supports configurable HTTP host/port at server creation time (`host`, `port`).
- Existing MCPs in this repo mostly default to `server.run()` (stdio), so HTTP mode is currently not first-class in project MCP patterns.
- The active Chrome-VNC based container environment (`llm-server-0`) already has the key X11 tools required for deterministic desktop control:
  - `xdotool`
  - `xwininfo`
  - `xprop`
  - `scrot`
  - `xwd`
  - `xclip`
- The container uses `DISPLAY=:99`, and X11 interaction commands succeed (`xdotool getmouselocation`, `xwininfo -root -tree`).
- Container runtime already runs desktop stack + chrome via supervisord (`tigervnc`, `websockify`, `xfce`, `chrome`).
- In this Chrome-VNC container runtime, some `xdotool` `--sync` operations can hang (focus/mouse movement), while non-sync equivalents complete reliably.

## Entrypoints / Boundaries Identified
- FastMCP entrypoint pattern in this repo:
  - `create_server(...)` registers tools and dependencies.
  - `main()` loads config and calls `server.run(...)`.
- Typical decomposition pattern used by robust MCPs (`ssh-mcp`):
  - `config.py` for environment parsing + validation.
  - `runner.py` for core command execution and typed results.
  - `server.py` for MCP tool registration and context progress messages.

## Naming / Structure Conventions
- Folder naming at repo root uses kebab-case (`ssh-mcp`, `browser-mcp`).
- Python package naming uses snake_case under `src` (`ssh_mcp`, `browser_mcp`).
- Tests split into unit-like runner/config tests and MCP tool invocation tests.

## Open Unknowns
- Whether MCP should run primarily inside container or support host-side command-prefix execution against a target container.
- Whether screenshot return should include raw bytes or file-path-only contract.
- Whether first version should include advanced features (drag paths, window-relative coordinates, clipboard, OCR hooks) or keep a strict deterministic core set.

## Implications For Requirements/Design
- Transport must include `streamable-http` as first-class mode for container port mapping convenience.
- Implementation should use deterministic shell/X11 commands, not fragile pixel vision, for core control primitives.
- Runner command selections should prefer non-blocking `xdotool` forms in containerized X11 environments unless sync behavior is explicitly proven stable.
- Design should include clear validation/error taxonomy so agents can handle retries deterministically.
- Medium-scope workflow is appropriate:
  - New MCP package introduction.
  - Multiple tool APIs.
  - Transport mode additions.
  - Test coverage across unit + MCP integration + docker-backed validation evidence.
