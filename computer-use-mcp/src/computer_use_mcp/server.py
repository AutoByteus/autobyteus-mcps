from __future__ import annotations

from mcp.server.fastmcp import Context, FastMCP

from .config import ConfigError, ServerConfig, X11Settings, load_settings
from .runner import (
    X11ToolResult,
    run_capture_screenshot,
    run_focus_window,
    run_get_active_window,
    run_get_screen_info,
    run_health_check,
    run_key_press,
    run_list_windows,
    run_mouse_click,
    run_mouse_drag,
    run_mouse_move,
    run_mouse_scroll,
    run_type_text,
)


def create_server(
    settings: X11Settings | None = None,
    server_config: ServerConfig | None = None,
) -> FastMCP:
    resolved_settings = settings or load_settings()
    resolved_server_config = server_config or ServerConfig.from_env()

    server = FastMCP(
        name=resolved_server_config.name,
        instructions=resolved_server_config.instructions,
        host=resolved_settings.host,
        port=resolved_settings.port,
    )

    @server.tool(
        name="x11_health_check",
        title="X11 MCP health check",
        description="Check display readiness and required X11 command availability.",
        structured_output=True,
    )
    async def x11_health_check(*, context: Context | None = None) -> X11ToolResult:
        if context is not None:
            await context.report_progress(0, 1, "Checking X11 health")
        result = run_health_check(resolved_settings)
        if context is not None:
            await context.report_progress(1, 1, "X11 health check complete")
        return result

    @server.tool(
        name="x11_get_screen_info",
        title="Get root screen geometry",
        description="Return root X11 screen geometry metadata.",
        structured_output=True,
    )
    async def x11_get_screen_info(*, context: Context | None = None) -> X11ToolResult:
        if context is not None:
            await context.report_progress(0, 1, "Fetching screen info")
        result = run_get_screen_info(resolved_settings)
        if context is not None:
            await context.report_progress(1, 1, "Screen info collected")
        return result

    @server.tool(
        name="x11_get_active_window",
        title="Get active window",
        description="Return metadata for currently focused X11 window.",
        structured_output=True,
    )
    async def x11_get_active_window(*, context: Context | None = None) -> X11ToolResult:
        if context is not None:
            await context.report_progress(0, 1, "Fetching active window")
        result = run_get_active_window(resolved_settings)
        if context is not None:
            await context.report_progress(1, 1, "Active window collected")
        return result

    @server.tool(
        name="x11_list_windows",
        title="List windows",
        description="List X11 windows optionally filtered by name pattern.",
        structured_output=True,
    )
    async def x11_list_windows(
        name_contains: str | None = None,
        limit: int | None = None,
        *,
        context: Context | None = None,
    ) -> X11ToolResult:
        if context is not None:
            await context.report_progress(0, 1, "Listing windows")
        result = run_list_windows(resolved_settings, name_contains=name_contains, limit=limit)
        if context is not None:
            await context.report_progress(1, 1, "Window listing complete")
        return result

    @server.tool(
        name="x11_focus_window",
        title="Focus window",
        description="Focus an X11 window by explicit id or by name matcher.",
        structured_output=True,
    )
    async def x11_focus_window(
        window_id: str | None = None,
        name_contains: str | None = None,
        *,
        context: Context | None = None,
    ) -> X11ToolResult:
        if context is not None:
            await context.report_progress(0, 1, "Focusing window")
        result = run_focus_window(resolved_settings, window_id=window_id, name_contains=name_contains)
        if context is not None:
            await context.report_progress(1, 1, "Window focus complete")
        return result

    @server.tool(
        name="x11_mouse_move",
        title="Move mouse",
        description="Move pointer to absolute coordinates or by relative offsets.",
        structured_output=True,
    )
    async def x11_mouse_move(
        x: int,
        y: int,
        relative: bool = False,
        *,
        context: Context | None = None,
    ) -> X11ToolResult:
        if context is not None:
            await context.report_progress(0, 1, "Moving mouse")
        result = run_mouse_move(resolved_settings, x=x, y=y, relative=relative)
        if context is not None:
            await context.report_progress(1, 1, "Mouse move complete")
        return result

    @server.tool(
        name="x11_mouse_click",
        title="Mouse click",
        description="Perform mouse click actions with configurable repeat and delay.",
        structured_output=True,
    )
    async def x11_mouse_click(
        button: int = 1,
        repeat: int = 1,
        delay_ms: int = 40,
        *,
        context: Context | None = None,
    ) -> X11ToolResult:
        if context is not None:
            await context.report_progress(0, 1, "Clicking mouse")
        result = run_mouse_click(resolved_settings, button=button, repeat=repeat, delay_ms=delay_ms)
        if context is not None:
            await context.report_progress(1, 1, "Mouse click complete")
        return result

    @server.tool(
        name="x11_mouse_scroll",
        title="Mouse scroll",
        description="Scroll up or down by issuing wheel clicks.",
        structured_output=True,
    )
    async def x11_mouse_scroll(
        direction: str,
        amount: int = 1,
        *,
        context: Context | None = None,
    ) -> X11ToolResult:
        if context is not None:
            await context.report_progress(0, 1, "Scrolling mouse")
        result = run_mouse_scroll(resolved_settings, direction=direction, amount=amount)
        if context is not None:
            await context.report_progress(1, 1, "Mouse scroll complete")
        return result

    @server.tool(
        name="x11_mouse_drag",
        title="Mouse drag",
        description="Drag pointer from start coordinates to end coordinates.",
        structured_output=True,
    )
    async def x11_mouse_drag(
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        button: int = 1,
        *,
        context: Context | None = None,
    ) -> X11ToolResult:
        if context is not None:
            await context.report_progress(0, 1, "Dragging mouse")
        result = run_mouse_drag(
            resolved_settings,
            start_x=start_x,
            start_y=start_y,
            end_x=end_x,
            end_y=end_y,
            button=button,
        )
        if context is not None:
            await context.report_progress(1, 1, "Mouse drag complete")
        return result

    @server.tool(
        name="x11_type_text",
        title="Type text",
        description="Type text into the currently focused window.",
        structured_output=True,
    )
    async def x11_type_text(
        text: str,
        delay_ms: int = 12,
        clear_modifiers: bool = True,
        *,
        context: Context | None = None,
    ) -> X11ToolResult:
        if context is not None:
            await context.report_progress(0, 1, "Typing text")
        result = run_type_text(
            resolved_settings,
            text=text,
            delay_ms=delay_ms,
            clear_modifiers=clear_modifiers,
        )
        if context is not None:
            await context.report_progress(1, 1, "Text typing complete")
        return result

    @server.tool(
        name="x11_key_press",
        title="Press key combo",
        description="Send key combo/hotkey to currently focused window.",
        structured_output=True,
    )
    async def x11_key_press(
        key_combo: str,
        clear_modifiers: bool = True,
        *,
        context: Context | None = None,
    ) -> X11ToolResult:
        if context is not None:
            await context.report_progress(0, 1, "Pressing key combo")
        result = run_key_press(resolved_settings, key_combo=key_combo, clear_modifiers=clear_modifiers)
        if context is not None:
            await context.report_progress(1, 1, "Key combo complete")
        return result

    @server.tool(
        name="x11_capture_screenshot",
        title="Capture screenshot",
        description="Capture full-screen screenshot to requested or generated png path.",
        structured_output=True,
    )
    async def x11_capture_screenshot(
        output_file_path: str | None = None,
        *,
        context: Context | None = None,
    ) -> X11ToolResult:
        if context is not None:
            await context.report_progress(0, 1, "Capturing screenshot")
        result = run_capture_screenshot(resolved_settings, output_file_path=output_file_path)
        if context is not None:
            await context.report_progress(1, 1, "Screenshot capture complete")
        return result

    return server


def main() -> None:
    try:
        settings = load_settings()
    except ConfigError as exc:
        raise SystemExit(f"Invalid X11 MCP configuration: {exc}") from exc

    server = create_server(settings=settings)
    server.run(transport=settings.transport)


if __name__ == "__main__":
    main()
