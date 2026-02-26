# Future-State Runtime Call Stacks (Debug-Trace Style)

## Conventions

- Frame format: `path/to/file.py:function_name(...)`
- Boundary tags:
  - `[ENTRY]` external entrypoint (MCP tool call)
  - `[ASYNC]` async boundary
  - `[STATE]` in-memory mutation
  - `[IO]` file/network/process IO
  - `[FALLBACK]` non-primary branch
  - `[ERROR]` error path

## Design Basis

- Scope Classification: `Medium`
- Call Stack Version: `v1`
- Requirements: `tickets/in-progress/x11-computer-use-mcp/requirements.md` (status `Design-ready`)
- Source Artifact: `tickets/in-progress/x11-computer-use-mcp/proposed-design.md`
- Source Design Version: `v1`
- Referenced Sections: architecture boundaries, change inventory C-001..C-010

## Future-State Modeling Rule (Mandatory)

- Model target design behavior even when current code diverges.
- No legacy compatibility branches are introduced.

## Use Case Index (Stable IDs)

| use_case_id | Source Type (`Requirement`/`Design-Risk`) | Requirement ID(s) | Design-Risk Objective (if source=`Design-Risk`) | Use Case Name | Coverage Target (Primary/Fallback/Error) |
| --- | --- | --- | --- | --- | --- |
| UC-001 | Requirement | R-001,R-008 | N/A | HTTP transport startup | Yes/N/A/Yes |
| UC-002 | Requirement | R-002 | N/A | X11 health/tool readiness | Yes/N/A/Yes |
| UC-003 | Requirement | R-003 | N/A | Screen + active window inspection | Yes/N/A/Yes |
| UC-004 | Requirement | R-003 | N/A | List windows and focus target | Yes/Yes/Yes |
| UC-005 | Requirement | R-004 | N/A | Pointer controls | Yes/Yes/Yes |
| UC-006 | Requirement | R-005 | N/A | Keyboard controls | Yes/N/A/Yes |
| UC-007 | Requirement | R-006 | N/A | Screenshot capture | Yes/Yes/Yes |
| UC-008 | Requirement | R-007 | N/A | Structured error responses | Yes/N/A/Yes |
| UC-009 | Requirement | R-009,R-010 | N/A | MCP tests + docker validation loop | Yes/N/A/Yes |
| UC-010 | Design-Risk | R-008 | Ensure command-prefix mode preserves DISPLAY and deterministic subprocess behavior | Prefix execution behavior | Yes/N/A/Yes |

## Transition Notes

- None. This is a new package with additive rollout.

## Use Case: UC-001 [HTTP transport startup]

### Goal
- Start MCP with HTTP transport bound to configured host/port.

### Preconditions
- Valid env configuration for transport and network bind values.

### Expected Outcome
- MCP process serves streamable HTTP endpoint and tool list.

### Primary Runtime Call Stack

```text
[ENTRY] computer-use-mcp/src/computer_use_mcp/server.py:main()
├── computer-use-mcp/src/computer_use_mcp/config.py:load_settings(...)
├── computer-use-mcp/src/computer_use_mcp/server.py:create_server(settings, server_config)
│   └── mcp/server/fastmcp/server.py:FastMCP(... host, port ...)
└── mcp/server/fastmcp/server.py:FastMCP.run(transport="streamable-http") [IO]
```

### Branching / Fallback Paths

```text
[ERROR] invalid transport value
computer-use-mcp/src/computer_use_mcp/config.py:load_settings(...)
└── raise ConfigError -> server.py:main() maps to startup failure message
```

### Coverage Status

- Primary Path: `Covered`
- Fallback Path: `N/A`
- Error Path: `Covered`

## Use Case: UC-002 [X11 health/tool readiness]

### Goal
- Confirm display and required toolchain readiness.

### Primary Runtime Call Stack

```text
[ENTRY] computer-use-mcp/src/computer_use_mcp/server.py:x11_health_check(...) [ASYNC]
└── computer-use-mcp/src/computer_use_mcp/runner.py:run_health_check(settings)
    ├── runner.py:_check_required_tools(settings) [IO]
    ├── runner.py:_run_command(["xwininfo", "-root"], ...) [IO]
    └── runner.py:_ok_result(action="health_check", ...)
```

### Error Paths

```text
[ERROR] required binary missing
runner.py:_check_required_tools(...)
└── runner.py:_error_result(error_type="dependency")
```

```text
[ERROR] display probe fails
runner.py:_run_command(...)
└── runner.py:_error_result(error_type="execution"|"timeout")
```

### Coverage Status

- Primary Path: `Covered`
- Fallback Path: `N/A`
- Error Path: `Covered`

## Use Case: UC-003 [Screen + active window inspection]

### Primary Runtime Call Stack

```text
[ENTRY] server.py:x11_get_screen_info(...) [ASYNC]
└── runner.py:run_get_screen_info(settings)
    ├── runner.py:_run_command(["xwininfo", "-root"], ...) [IO]
    ├── runner.py:_parse_xwininfo_root(...)
    └── runner.py:_ok_result(action="get_screen_info", ...)

[ENTRY] server.py:x11_get_active_window(...) [ASYNC]
└── runner.py:run_get_active_window(settings)
    ├── runner.py:_run_command(["xdotool", "getactivewindow"], ...) [IO]
    └── runner.py:_describe_window(window_id, settings)
        ├── _run_command(["xdotool", "getwindowname", window_id], ...) [IO]
        ├── _run_command(["xdotool", "getwindowgeometry", "--shell", window_id], ...) [IO]
        └── _run_command(["xprop", "-id", window_id, "_NET_WM_PID"], ...) [IO]
```

### Error Paths

```text
[ERROR] no active window or command failure
runner.py:run_get_active_window(...)
└── _error_result(error_type="execution")
```

### Coverage Status

- Primary Path: `Covered`
- Fallback Path: `N/A`
- Error Path: `Covered`

## Use Case: UC-004 [List windows and focus target]

### Primary Runtime Call Stack

```text
[ENTRY] server.py:x11_list_windows(name_contains?, limit?) [ASYNC]
└── runner.py:run_list_windows(...)
    ├── _validate_limit(...)
    ├── _run_command(["xdotool", "search", "--name", pattern], ...) [IO]
    ├── loop window ids -> _describe_window(...) [IO]
    └── _ok_result(action="list_windows", windows=[...])

[ENTRY] server.py:x11_focus_window(window_id?, name_contains?) [ASYNC]
└── runner.py:run_focus_window(...)
    ├── _resolve_window_target(window_id?, name_contains?)
    ├── _run_command(["xdotool", "windowactivate", "--sync", window_id], ...) [IO]
    └── _describe_window(window_id, settings)
```

### Branching / Fallback Paths

```text
[FALLBACK] focus by name_contains when window_id not provided
runner.py:run_focus_window(...)
└── _resolve_window_target -> search first match
```

### Error Paths

```text
[ERROR] neither window_id nor name_contains provided
runner.py:run_focus_window(...)
└── _error_result(error_type="validation")
```

```text
[ERROR] search has no matches
runner.py:run_focus_window(...)
└── _error_result(error_type="execution")
```

### Coverage Status

- Primary Path: `Covered`
- Fallback Path: `Covered`
- Error Path: `Covered`

## Use Case: UC-005 [Pointer controls]

### Primary Runtime Call Stack

```text
[ENTRY] server.py:x11_mouse_move(...) [ASYNC]
└── runner.py:run_mouse_move(...)
    ├── _validate_coordinates(...)
    ├── _run_command(["xdotool", "mousemove"|"mousemove_relative", ...], ...) [IO]
    └── _get_mouse_location(settings) [IO]

[ENTRY] server.py:x11_mouse_click(...) [ASYNC]
└── runner.py:run_mouse_click(...)
    ├── _validate_button(...)
    ├── _run_command(["xdotool", "click", ...], ...) [IO]
    └── _get_mouse_location(settings) [IO]

[ENTRY] server.py:x11_mouse_scroll(...) [ASYNC]
└── runner.py:run_mouse_scroll(...)
    ├── map direction -> xdotool button 4/5
    └── _run_command(["xdotool", "click", "--repeat", ...], ...) [IO]

[ENTRY] server.py:x11_mouse_drag(...) [ASYNC]
└── runner.py:run_mouse_drag(...)
    ├── _run_command(["xdotool", "mousemove", ...], ...) [IO]
    ├── _run_command(["xdotool", "mousedown", button], ...) [IO]
    ├── _run_command(["xdotool", "mousemove", ...], ...) [IO]
    └── _run_command(["xdotool", "mouseup", button], ...) [IO]
```

### Branching / Fallback Paths

```text
[FALLBACK] relative movement path
run_mouse_move(...)
└── use `mousemove_relative` command form
```

### Error Paths

```text
[ERROR] invalid button/direction/coordinate input
run_mouse_* functions
└── _error_result(error_type="validation")
```

### Coverage Status

- Primary Path: `Covered`
- Fallback Path: `Covered`
- Error Path: `Covered`

## Use Case: UC-006 [Keyboard controls]

### Primary Runtime Call Stack

```text
[ENTRY] server.py:x11_type_text(text, delay_ms, clear_modifiers) [ASYNC]
└── runner.py:run_type_text(...)
    ├── _validate_text_input(...)
    └── _run_command(["xdotool", "type", ...], ...) [IO]

[ENTRY] server.py:x11_key_press(key_combo, clear_modifiers) [ASYNC]
└── runner.py:run_key_press(...)
    ├── _validate_key_combo(...)
    └── _run_command(["xdotool", "key", ...], ...) [IO]
```

### Error Paths

```text
[ERROR] text length or key combo invalid
runner.py validators
└── _error_result(error_type="validation")
```

### Coverage Status

- Primary Path: `Covered`
- Fallback Path: `N/A`
- Error Path: `Covered`

## Use Case: UC-007 [Screenshot capture]

### Primary Runtime Call Stack

```text
[ENTRY] server.py:x11_capture_screenshot(output_file_path?) [ASYNC]
└── runner.py:run_capture_screenshot(...)
    ├── _resolve_output_path(workspace_root, output_file_path) [STATE]
    ├── _run_command(["scrot", resolved_path], ...) [IO]
    ├── _run_command(["xwininfo", "-root"], ...) [IO]
    └── _ok_result(action="capture_screenshot", file_path, width, height)
```

### Branching / Fallback Paths

```text
[FALLBACK] output_file_path omitted
run_capture_screenshot(...)
└── auto-generate timestamped path under screenshot directory
```

### Error Paths

```text
[ERROR] invalid path or capture failure
run_capture_screenshot(...)
└── _error_result(error_type="validation"|"execution"|"timeout")
```

### Coverage Status

- Primary Path: `Covered`
- Fallback Path: `Covered`
- Error Path: `Covered`

## Use Case: UC-008 [Structured error responses]

### Primary Runtime Call Stack

```text
[ENTRY] any tool in server.py [ASYNC]
└── runner.py:run_* function
    ├── validation gate
    ├── command execution gate
    └── return consistent payload schema with error_type/error_message on failure
```

### Error Paths

```text
[ERROR] unexpected exception in runner
server.py tool handler
└── map to structured `error_type="execution"` and preserve message context
```

### Coverage Status

- Primary Path: `Covered`
- Fallback Path: `N/A`
- Error Path: `Covered`

## Use Case: UC-009 [MCP tests + docker validation loop]

### Primary Runtime Call Stack

```text
[ENTRY] computer-use-mcp/tests/test_server.py
└── anyio memory-stream MCP session
    ├── create_server(settings)
    ├── session.call_tool("x11_health_check", ...)
    ├── session.call_tool("x11_get_screen_info", ...)
    └── assert structured outputs

[ENTRY] docker validation scenario
└── pytest/command harness uses configured command-prefix mode
    ├── run focus/input/screenshot sequence
    └── assert command success and output artifacts
```

### Error Paths

```text
[ERROR] docker unavailable or container missing
validation scenario bootstrap
└── mark scenario blocked/skipped with explicit reason
```

### Coverage Status

- Primary Path: `Covered`
- Fallback Path: `N/A`
- Error Path: `Covered`

## Use Case: UC-010 [Design-Risk: prefix execution behavior]

### Goal
- Ensure optional command-prefix mode does not break DISPLAY propagation and command determinism.

### Expected Outcome
- Commands run with prefix include target DISPLAY context and return same structured schema as direct mode.

### Primary Runtime Call Stack

```text
[ENTRY] runner.py:_run_command(command, settings)
├── if settings.command_prefix empty -> local subprocess env DISPLAY set
└── if settings.command_prefix set -> prefixed command adds `env DISPLAY=...` in target execution chain [IO]
```

### Error Paths

```text
[ERROR] prefixed command chain fails (container missing, exec denied)
runner.py:_run_command(...)
└── _error_result(error_type="execution")
```

### Coverage Status

- Primary Path: `Covered`
- Fallback Path: `N/A`
- Error Path: `Covered`
