from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import time
from typing import Any, TypedDict

from .config import ConfigError, X11Settings

_WINDOW_ID_PATTERN = re.compile(r"^(?:0x)?[0-9a-fA-F]+$")
_PID_PATTERN = re.compile(r"=\s*(\d+)")


class X11ToolResult(TypedDict, total=False):
    ok: bool
    action: str
    command: list[str]
    display: str
    stdout: str | None
    stderr: str | None
    exit_code: int | None
    duration_ms: int | None
    error_type: str | None
    error_message: str | None
    result: dict[str, Any]


@dataclass(frozen=True, slots=True)
class _CommandResult:
    ok: bool
    command: list[str]
    stdout: str
    stderr: str
    exit_code: int | None
    duration_ms: int
    error_type: str | None
    error_message: str | None


def run_health_check(settings: X11Settings) -> X11ToolResult:
    tool_status = {tool: _is_tool_available(tool, settings) for tool in settings.required_tools}
    missing_tools = [tool for tool, available in tool_status.items() if not available]

    if missing_tools:
        return _error_result(
            action="health_check",
            settings=settings,
            command=[],
            error_type="dependency",
            error_message=f"Missing required tools: {', '.join(missing_tools)}",
            result={
                "tool_status": tool_status,
                "missing_tools": missing_tools,
                "display": settings.display,
                "display_probe_ok": False,
            },
        )

    probe = _run_command(["xwininfo", "-root"], settings=settings)
    if not probe.ok:
        return _error_result(
            action="health_check",
            settings=settings,
            command=probe.command,
            error_type=probe.error_type or "execution",
            error_message=probe.error_message or "Display probe failed.",
            stdout=probe.stdout,
            stderr=probe.stderr,
            exit_code=probe.exit_code,
            duration_ms=probe.duration_ms,
            result={
                "tool_status": tool_status,
                "missing_tools": [],
                "display": settings.display,
                "display_probe_ok": False,
            },
        )

    geometry = _parse_root_geometry(probe.stdout)
    return _ok_result(
        action="health_check",
        settings=settings,
        command=probe.command,
        stdout=probe.stdout,
        stderr=probe.stderr,
        exit_code=probe.exit_code,
        duration_ms=probe.duration_ms,
        result={
            "tool_status": tool_status,
            "missing_tools": [],
            "display": settings.display,
            "display_probe_ok": True,
            "screen": geometry,
        },
    )


def run_get_screen_info(settings: X11Settings) -> X11ToolResult:
    command_result = _run_command(["xwininfo", "-root"], settings=settings)
    if not command_result.ok:
        return _from_command_error("get_screen_info", settings, command_result)

    geometry = _parse_root_geometry(command_result.stdout)
    return _ok_result(
        action="get_screen_info",
        settings=settings,
        command=command_result.command,
        stdout=command_result.stdout,
        stderr=command_result.stderr,
        exit_code=command_result.exit_code,
        duration_ms=command_result.duration_ms,
        result=geometry,
    )


def run_get_active_window(settings: X11Settings) -> X11ToolResult:
    command_result = _run_command(["xdotool", "getactivewindow"], settings=settings)
    if not command_result.ok:
        return _from_command_error("get_active_window", settings, command_result)

    window_id = command_result.stdout.strip()
    if not window_id:
        return _error_result(
            action="get_active_window",
            settings=settings,
            command=command_result.command,
            error_type="execution",
            error_message="No active window returned by xdotool.",
            stdout=command_result.stdout,
            stderr=command_result.stderr,
            exit_code=command_result.exit_code,
            duration_ms=command_result.duration_ms,
        )

    described = _describe_window(window_id, settings)
    if not described.get("ok"):
        return described

    return _ok_result(
        action="get_active_window",
        settings=settings,
        command=command_result.command,
        stdout=command_result.stdout,
        stderr=command_result.stderr,
        exit_code=command_result.exit_code,
        duration_ms=command_result.duration_ms,
        result=described.get("result", {}),
    )


def run_list_windows(
    settings: X11Settings,
    name_contains: str | None = None,
    limit: int | None = None,
) -> X11ToolResult:
    try:
        resolved_limit = _resolve_window_limit(settings, limit)
    except ConfigError as exc:
        return _validation_error("list_windows", settings, str(exc))
    pattern = (name_contains or ".").strip() or "."

    search_result = _run_command(
        ["xdotool", "search", "--name", pattern],
        settings=settings,
        accepted_exit_codes={0, 1},
    )
    if not search_result.ok:
        return _from_command_error("list_windows", settings, search_result)

    if search_result.exit_code == 1 or not search_result.stdout.strip():
        return _ok_result(
            action="list_windows",
            settings=settings,
            command=search_result.command,
            stdout=search_result.stdout,
            stderr=search_result.stderr,
            exit_code=search_result.exit_code,
            duration_ms=search_result.duration_ms,
            result={"windows": [], "count": 0, "pattern": pattern},
        )

    windows: list[dict[str, Any]] = []
    for raw_window_id in search_result.stdout.splitlines():
        window_id = raw_window_id.strip()
        if not window_id:
            continue
        described = _describe_window(window_id, settings)
        if not described.get("ok"):
            return described
        windows.append(described.get("result", {}))
        if len(windows) >= resolved_limit:
            break

    return _ok_result(
        action="list_windows",
        settings=settings,
        command=search_result.command,
        stdout=search_result.stdout,
        stderr=search_result.stderr,
        exit_code=search_result.exit_code,
        duration_ms=search_result.duration_ms,
        result={"windows": windows, "count": len(windows), "pattern": pattern},
    )


def run_focus_window(
    settings: X11Settings,
    window_id: str | None = None,
    name_contains: str | None = None,
) -> X11ToolResult:
    target_window_id: str
    if window_id:
        try:
            target_window_id = _normalize_window_id(window_id)
        except ConfigError as exc:
            return _validation_error("focus_window", settings, str(exc))
    else:
        if not name_contains or not name_contains.strip():
            return _validation_error(
                "focus_window",
                settings,
                "Either window_id or name_contains is required.",
            )
        candidates = run_list_windows(settings=settings, name_contains=name_contains, limit=1)
        if not candidates.get("ok"):
            return candidates
        windows = candidates.get("result", {}).get("windows", [])
        if not windows:
            return _error_result(
                action="focus_window",
                settings=settings,
                command=[],
                error_type="execution",
                error_message=f"No window matched name_contains='{name_contains}'.",
            )
        target_window_id = str(windows[0].get("window_id"))

    # `windowactivate --sync` can hang in containerized X11 sessions without full EWMH support.
    focus_result = _run_command(["xdotool", "windowactivate", target_window_id], settings=settings)
    if not focus_result.ok:
        return _from_command_error("focus_window", settings, focus_result)

    described = _describe_window(target_window_id, settings)
    if not described.get("ok"):
        return described

    return _ok_result(
        action="focus_window",
        settings=settings,
        command=focus_result.command,
        stdout=focus_result.stdout,
        stderr=focus_result.stderr,
        exit_code=focus_result.exit_code,
        duration_ms=focus_result.duration_ms,
        result=described.get("result", {}),
    )


def run_mouse_move(settings: X11Settings, x: int, y: int, relative: bool = False) -> X11ToolResult:
    if not isinstance(x, int) or not isinstance(y, int):
        return _validation_error("mouse_move", settings, "x and y must be integers.")
    if not relative and (x < 0 or y < 0):
        return _validation_error("mouse_move", settings, "Absolute x and y must be >= 0.")

    command = ["xdotool", "mousemove_relative", "--", str(x), str(y)] if relative else [
        "xdotool",
        "mousemove",
        str(x),
        str(y),
    ]
    move_result = _run_command(command, settings=settings)
    if not move_result.ok:
        return _from_command_error("mouse_move", settings, move_result)

    location = _get_mouse_location(settings)
    if not location.get("ok"):
        return location

    return _ok_result(
        action="mouse_move",
        settings=settings,
        command=move_result.command,
        stdout=move_result.stdout,
        stderr=move_result.stderr,
        exit_code=move_result.exit_code,
        duration_ms=move_result.duration_ms,
        result={
            "x": x,
            "y": y,
            "relative": relative,
            "location": location.get("result", {}),
        },
    )


def run_mouse_click(
    settings: X11Settings,
    button: int = 1,
    repeat: int = 1,
    delay_ms: int = 40,
) -> X11ToolResult:
    validation_error = _validate_mouse_click_inputs(button, repeat, delay_ms)
    if validation_error is not None:
        return _validation_error("mouse_click", settings, validation_error)

    click_result = _run_command(
        ["xdotool", "click", "--repeat", str(repeat), "--delay", str(delay_ms), str(button)],
        settings=settings,
    )
    if not click_result.ok:
        return _from_command_error("mouse_click", settings, click_result)

    location = _get_mouse_location(settings)
    if not location.get("ok"):
        return location

    return _ok_result(
        action="mouse_click",
        settings=settings,
        command=click_result.command,
        stdout=click_result.stdout,
        stderr=click_result.stderr,
        exit_code=click_result.exit_code,
        duration_ms=click_result.duration_ms,
        result={"button": button, "repeat": repeat, "delay_ms": delay_ms, "location": location.get("result", {})},
    )


def run_mouse_scroll(settings: X11Settings, direction: str, amount: int = 1) -> X11ToolResult:
    direction_value = (direction or "").strip().lower()
    if direction_value not in {"up", "down"}:
        return _validation_error("mouse_scroll", settings, "direction must be 'up' or 'down'.")
    if not isinstance(amount, int) or amount <= 0:
        return _validation_error("mouse_scroll", settings, "amount must be an integer > 0.")

    button = "4" if direction_value == "up" else "5"
    scroll_result = _run_command(["xdotool", "click", "--repeat", str(amount), button], settings=settings)
    if not scroll_result.ok:
        return _from_command_error("mouse_scroll", settings, scroll_result)

    location = _get_mouse_location(settings)
    if not location.get("ok"):
        return location

    return _ok_result(
        action="mouse_scroll",
        settings=settings,
        command=scroll_result.command,
        stdout=scroll_result.stdout,
        stderr=scroll_result.stderr,
        exit_code=scroll_result.exit_code,
        duration_ms=scroll_result.duration_ms,
        result={"direction": direction_value, "amount": amount, "location": location.get("result", {})},
    )


def run_mouse_drag(
    settings: X11Settings,
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    button: int = 1,
) -> X11ToolResult:
    if any(not isinstance(value, int) for value in (start_x, start_y, end_x, end_y)):
        return _validation_error("mouse_drag", settings, "start_x/start_y/end_x/end_y must be integers.")
    if any(value < 0 for value in (start_x, start_y, end_x, end_y)):
        return _validation_error("mouse_drag", settings, "Coordinates must be >= 0.")
    if button < 1 or button > 9:
        return _validation_error("mouse_drag", settings, "button must be between 1 and 9.")

    sequence = [
        ["xdotool", "mousemove", str(start_x), str(start_y)],
        ["xdotool", "mousedown", str(button)],
        ["xdotool", "mousemove", str(end_x), str(end_y)],
        ["xdotool", "mouseup", str(button)],
    ]

    last_result: _CommandResult | None = None
    for command in sequence:
        step = _run_command(command, settings=settings)
        if not step.ok:
            return _from_command_error("mouse_drag", settings, step)
        last_result = step

    location = _get_mouse_location(settings)
    if not location.get("ok"):
        return location

    assert last_result is not None
    return _ok_result(
        action="mouse_drag",
        settings=settings,
        command=last_result.command,
        stdout=last_result.stdout,
        stderr=last_result.stderr,
        exit_code=last_result.exit_code,
        duration_ms=last_result.duration_ms,
        result={
            "start": {"x": start_x, "y": start_y},
            "end": {"x": end_x, "y": end_y},
            "button": button,
            "location": location.get("result", {}),
        },
    )


def run_type_text(
    settings: X11Settings,
    text: str,
    delay_ms: int = 12,
    clear_modifiers: bool = True,
) -> X11ToolResult:
    normalized_text = (text or "").strip()
    if not normalized_text:
        return _validation_error("type_text", settings, "text cannot be empty.")
    if len(normalized_text) > settings.max_text_chars:
        return _validation_error(
            "type_text",
            settings,
            f"text length exceeds max of {settings.max_text_chars} characters.",
        )
    if not isinstance(delay_ms, int) or delay_ms < 0:
        return _validation_error("type_text", settings, "delay_ms must be an integer >= 0.")

    command = ["xdotool", "type", "--delay", str(delay_ms)]
    if clear_modifiers:
        command.append("--clearmodifiers")
    command.extend(["--", normalized_text])

    type_result = _run_command(command, settings=settings)
    if not type_result.ok:
        return _from_command_error("type_text", settings, type_result)

    return _ok_result(
        action="type_text",
        settings=settings,
        command=type_result.command,
        stdout=type_result.stdout,
        stderr=type_result.stderr,
        exit_code=type_result.exit_code,
        duration_ms=type_result.duration_ms,
        result={
            "chars_typed": len(normalized_text),
            "delay_ms": delay_ms,
            "clear_modifiers": clear_modifiers,
        },
    )


def run_key_press(settings: X11Settings, key_combo: str, clear_modifiers: bool = True) -> X11ToolResult:
    combo = (key_combo or "").strip()
    if not combo:
        return _validation_error("key_press", settings, "key_combo cannot be empty.")
    if "\n" in combo or "\r" in combo:
        return _validation_error("key_press", settings, "key_combo cannot contain newline characters.")
    if len(combo) > settings.max_key_combo_chars:
        return _validation_error(
            "key_press",
            settings,
            f"key_combo length exceeds max of {settings.max_key_combo_chars} characters.",
        )

    command = ["xdotool", "key"]
    if clear_modifiers:
        command.append("--clearmodifiers")
    command.append(combo)

    key_result = _run_command(command, settings=settings)
    if not key_result.ok:
        return _from_command_error("key_press", settings, key_result)

    return _ok_result(
        action="key_press",
        settings=settings,
        command=key_result.command,
        stdout=key_result.stdout,
        stderr=key_result.stderr,
        exit_code=key_result.exit_code,
        duration_ms=key_result.duration_ms,
        result={"key_combo": combo, "clear_modifiers": clear_modifiers},
    )


def run_capture_screenshot(settings: X11Settings, output_file_path: str | None = None) -> X11ToolResult:
    try:
        resolved_path = _resolve_screenshot_path(settings, output_file_path)
    except ConfigError as exc:
        return _validation_error("capture_screenshot", settings, str(exc))

    if settings.command_prefix:
        ensure_dir_result = _run_command(["mkdir", "-p", str(resolved_path.parent)], settings=settings)
        if not ensure_dir_result.ok:
            return _from_command_error("capture_screenshot", settings, ensure_dir_result)

    capture_result = _run_command(["scrot", str(resolved_path)], settings=settings)
    if not capture_result.ok:
        return _from_command_error("capture_screenshot", settings, capture_result)

    screen_result = run_get_screen_info(settings)
    if not screen_result.get("ok"):
        return screen_result

    file_exists, file_size_bytes = _probe_output_file(settings, resolved_path)

    return _ok_result(
        action="capture_screenshot",
        settings=settings,
        command=capture_result.command,
        stdout=capture_result.stdout,
        stderr=capture_result.stderr,
        exit_code=capture_result.exit_code,
        duration_ms=capture_result.duration_ms,
        result={
            "file_path": str(resolved_path),
            "file_exists": file_exists,
            "file_size_bytes": file_size_bytes,
            "width": screen_result.get("result", {}).get("width"),
            "height": screen_result.get("result", {}).get("height"),
        },
    )


def _resolve_window_limit(settings: X11Settings, limit: int | None) -> int:
    if limit is None:
        return settings.max_windows
    if not isinstance(limit, int) or limit <= 0:
        raise ConfigError("limit must be an integer > 0.")
    if limit > settings.max_windows:
        raise ConfigError(f"limit cannot exceed X11_MCP_MAX_WINDOWS ({settings.max_windows}).")
    return limit


def _normalize_window_id(raw_value: str) -> str:
    value = raw_value.strip()
    if not value:
        raise ConfigError("window_id cannot be empty.")
    if not _WINDOW_ID_PATTERN.fullmatch(value):
        raise ConfigError("window_id must be a decimal or hex integer value.")
    return str(int(value, 0))


def _describe_window(window_id: str, settings: X11Settings) -> X11ToolResult:
    normalized_window_id = _normalize_window_id(window_id)

    name_result = _run_command(["xdotool", "getwindowname", normalized_window_id], settings=settings)
    if not name_result.ok:
        return _from_command_error("describe_window", settings, name_result)

    geometry_result = _run_command(
        ["xdotool", "getwindowgeometry", "--shell", normalized_window_id],
        settings=settings,
    )
    if not geometry_result.ok:
        return _from_command_error("describe_window", settings, geometry_result)

    pid_result = _run_command(
        ["xprop", "-id", normalized_window_id, "_NET_WM_PID"],
        settings=settings,
        accepted_exit_codes={0, 1},
    )
    pid = _extract_pid(pid_result.stdout) if pid_result.ok else None

    geometry = _parse_shell_assignments(geometry_result.stdout)
    return _ok_result(
        action="describe_window",
        settings=settings,
        command=geometry_result.command,
        stdout=geometry_result.stdout,
        stderr=geometry_result.stderr,
        exit_code=geometry_result.exit_code,
        duration_ms=geometry_result.duration_ms,
        result={
            "window_id": normalized_window_id,
            "name": name_result.stdout.strip(),
            "x": _safe_int(geometry.get("X")),
            "y": _safe_int(geometry.get("Y")),
            "width": _safe_int(geometry.get("WIDTH")),
            "height": _safe_int(geometry.get("HEIGHT")),
            "screen": _safe_int(geometry.get("SCREEN")),
            "pid": pid,
        },
    )


def _get_mouse_location(settings: X11Settings) -> X11ToolResult:
    command_result = _run_command(["xdotool", "getmouselocation", "--shell"], settings=settings)
    if not command_result.ok:
        return _from_command_error("get_mouse_location", settings, command_result)

    values = _parse_shell_assignments(command_result.stdout)
    return _ok_result(
        action="get_mouse_location",
        settings=settings,
        command=command_result.command,
        stdout=command_result.stdout,
        stderr=command_result.stderr,
        exit_code=command_result.exit_code,
        duration_ms=command_result.duration_ms,
        result={
            "x": _safe_int(values.get("X")),
            "y": _safe_int(values.get("Y")),
            "screen": _safe_int(values.get("SCREEN")),
            "window_id": values.get("WINDOW"),
        },
    )


def _resolve_screenshot_path(settings: X11Settings, output_file_path: str | None) -> Path:
    if output_file_path is None or not output_file_path.strip():
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S-%f")
        path = Path(settings.screenshot_dir) / f"screenshot-{timestamp}.png"
    else:
        candidate = Path(output_file_path.strip()).expanduser()
        if candidate.is_absolute():
            path = candidate
        else:
            if settings.command_prefix:
                path = Path("/tmp/computer-use-mcp-screenshots") / candidate
            else:
                path = Path(settings.workspace_root) / candidate

    if path.suffix.lower() != ".png":
        raise ConfigError("output_file_path must use .png extension.")

    path.parent.mkdir(parents=True, exist_ok=True)
    return path.resolve()


def _run_command(
    command: list[str],
    *,
    settings: X11Settings,
    accepted_exit_codes: set[int] | None = None,
) -> _CommandResult:
    accepted_codes = accepted_exit_codes or {0}

    if settings.command_prefix:
        final_command = [*settings.command_prefix, "env", f"DISPLAY={settings.display}", *command]
        env = os.environ.copy()
    else:
        final_command = list(command)
        env = os.environ.copy()
        env["DISPLAY"] = settings.display

    start = time.monotonic()
    try:
        completed = subprocess.run(
            final_command,
            capture_output=True,
            text=True,
            timeout=settings.timeout_seconds,
            env=env,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        duration_ms = int((time.monotonic() - start) * 1000)
        return _CommandResult(
            ok=False,
            command=final_command,
            stdout=(exc.stdout or "") if isinstance(exc.stdout, str) else "",
            stderr=(exc.stderr or "") if isinstance(exc.stderr, str) else "",
            exit_code=None,
            duration_ms=duration_ms,
            error_type="timeout",
            error_message=f"Command timed out after {settings.timeout_seconds}s.",
        )
    except OSError as exc:
        duration_ms = int((time.monotonic() - start) * 1000)
        return _CommandResult(
            ok=False,
            command=final_command,
            stdout="",
            stderr=str(exc),
            exit_code=None,
            duration_ms=duration_ms,
            error_type="dependency",
            error_message=str(exc),
        )

    duration_ms = int((time.monotonic() - start) * 1000)
    success = completed.returncode in accepted_codes
    if success:
        return _CommandResult(
            ok=True,
            command=final_command,
            stdout=completed.stdout,
            stderr=completed.stderr,
            exit_code=completed.returncode,
            duration_ms=duration_ms,
            error_type=None,
            error_message=None,
        )

    return _CommandResult(
        ok=False,
        command=final_command,
        stdout=completed.stdout,
        stderr=completed.stderr,
        exit_code=completed.returncode,
        duration_ms=duration_ms,
        error_type="execution",
        error_message=(completed.stderr or completed.stdout or "Command failed.").strip(),
    )


def _is_tool_available(tool: str, settings: X11Settings) -> bool:
    if settings.command_prefix:
        probe = _run_command(["sh", "-lc", f"command -v {tool}"], settings=settings, accepted_exit_codes={0, 1})
        return probe.exit_code == 0
    return shutil.which(tool) is not None


def _parse_shell_assignments(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def _parse_root_geometry(output: str) -> dict[str, Any]:
    root_window_id = None
    width = None
    height = None
    absolute_x = None
    absolute_y = None

    for line in output.splitlines():
        match_window = re.search(r"Window id:\s*(0x[0-9a-fA-F]+)", line)
        if match_window:
            root_window_id = match_window.group(1)
            break

    for line in output.splitlines():
        stripped = line.strip()
        if stripped.startswith("Width:"):
            width = _safe_int(stripped.split(":", 1)[1])
        elif stripped.startswith("Height:"):
            height = _safe_int(stripped.split(":", 1)[1])
        elif stripped.startswith("Absolute upper-left X:"):
            absolute_x = _safe_int(stripped.split(":", 1)[1])
        elif stripped.startswith("Absolute upper-left Y:"):
            absolute_y = _safe_int(stripped.split(":", 1)[1])

    return {
        "root_window_id": root_window_id,
        "width": width,
        "height": height,
        "absolute_x": absolute_x,
        "absolute_y": absolute_y,
    }


def _extract_pid(text: str) -> int | None:
    match = _PID_PATTERN.search(text)
    if not match:
        return None
    return _safe_int(match.group(1))


def _probe_output_file(settings: X11Settings, path: Path) -> tuple[bool, int | None]:
    if settings.command_prefix:
        quoted = shlex.quote(str(path))
        probe = _run_command(
            ["sh", "-lc", f"test -f {quoted} && wc -c < {quoted}"],
            settings=settings,
            accepted_exit_codes={0, 1},
        )
        if probe.exit_code != 0:
            return False, None
        return True, _safe_int((probe.stdout or "").strip())

    if not path.exists():
        return False, None
    return True, path.stat().st_size


def _validate_mouse_click_inputs(button: int, repeat: int, delay_ms: int) -> str | None:
    if not isinstance(button, int) or button < 1 or button > 9:
        return "button must be an integer between 1 and 9."
    if not isinstance(repeat, int) or repeat <= 0:
        return "repeat must be an integer > 0."
    if not isinstance(delay_ms, int) or delay_ms < 0:
        return "delay_ms must be an integer >= 0."
    return None


def _safe_int(raw_value: str | None) -> int | None:
    if raw_value is None:
        return None
    try:
        return int(str(raw_value).strip())
    except ValueError:
        return None


def _from_command_error(action: str, settings: X11Settings, command_result: _CommandResult) -> X11ToolResult:
    return _error_result(
        action=action,
        settings=settings,
        command=command_result.command,
        error_type=command_result.error_type or "execution",
        error_message=command_result.error_message or "Command failed.",
        stdout=command_result.stdout,
        stderr=command_result.stderr,
        exit_code=command_result.exit_code,
        duration_ms=command_result.duration_ms,
    )


def _validation_error(action: str, settings: X11Settings, message: str) -> X11ToolResult:
    return _error_result(
        action=action,
        settings=settings,
        command=[],
        error_type="validation",
        error_message=message,
    )


def _ok_result(
    *,
    action: str,
    settings: X11Settings,
    command: list[str],
    result: dict[str, Any],
    stdout: str | None,
    stderr: str | None,
    exit_code: int | None,
    duration_ms: int | None,
) -> X11ToolResult:
    return X11ToolResult(
        ok=True,
        action=action,
        command=command,
        display=settings.display,
        stdout=stdout,
        stderr=stderr,
        exit_code=exit_code,
        duration_ms=duration_ms,
        error_type=None,
        error_message=None,
        result=result,
    )


def _error_result(
    *,
    action: str,
    settings: X11Settings,
    command: list[str],
    error_type: str,
    error_message: str,
    result: dict[str, Any] | None = None,
    stdout: str | None = None,
    stderr: str | None = None,
    exit_code: int | None = None,
    duration_ms: int | None = None,
) -> X11ToolResult:
    return X11ToolResult(
        ok=False,
        action=action,
        command=command,
        display=settings.display,
        stdout=stdout,
        stderr=stderr,
        exit_code=exit_code,
        duration_ms=duration_ms,
        error_type=error_type,
        error_message=error_message,
        result=result or {},
    )
