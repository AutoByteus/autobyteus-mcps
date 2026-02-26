# computer-use-mcp

MCP server for deterministic Linux desktop control over X11.

## Features

- HTTP-friendly MCP transport (`streamable-http`) for container port mapping.
- X11 health/tooling probe.
- Screen + window inspection (`xwininfo`, `xdotool`, `xprop`).
- Pointer controls (move/click/scroll/drag).
- Keyboard controls (type text/key combo).
- Screenshot capture via `scrot`.
- Structured error taxonomy: `validation`, `dependency`, `execution`, `timeout`.

## Tools

- `x11_health_check`
- `x11_get_screen_info`
- `x11_get_active_window`
- `x11_list_windows`
- `x11_focus_window`
- `x11_mouse_move`
- `x11_mouse_click`
- `x11_mouse_scroll`
- `x11_mouse_drag`
- `x11_type_text`
- `x11_key_press`
- `x11_capture_screenshot`

## Environment

- `X11_MCP_TRANSPORT` (`streamable-http` default)
- `X11_MCP_HOST` (`0.0.0.0` default)
- `X11_MCP_PORT` (`8765` default)
- `X11_MCP_DISPLAY` (`:99` default)
- `X11_MCP_TIMEOUT_SECONDS` (`10` default)
- `X11_MCP_REQUIRED_TOOLS` (`xdotool,xwininfo,xprop,scrot` default)
- `X11_MCP_COMMAND_PREFIX` (optional; example: `docker exec llm-server-0`)
- `X11_MCP_SCREENSHOT_DIR` (`artifacts/screenshots` default)
- `X11_MCP_MAX_TEXT_CHARS` (`2000` default)
- `X11_MCP_MAX_KEY_COMBO_CHARS` (`256` default)
- `X11_MCP_MAX_WINDOWS` (`50` default)

## Install

```bash
cd computer-use-mcp
pip install -e .
```

## Run (HTTP)

```bash
export X11_MCP_TRANSPORT=streamable-http
export X11_MCP_HOST=0.0.0.0
export X11_MCP_PORT=8765
export X11_MCP_DISPLAY=:99
computer-use-mcp-server
```

## Run (STDIO)

```bash
export X11_MCP_TRANSPORT=stdio
computer-use-mcp-server
```

## Host -> Container Control Mode

If MCP runs on host but should control a container desktop:

```bash
export X11_MCP_COMMAND_PREFIX="docker exec llm-server-0"
export X11_MCP_DISPLAY=:99
computer-use-mcp-server
```

## Test

```bash
cd computer-use-mcp
pytest
```
