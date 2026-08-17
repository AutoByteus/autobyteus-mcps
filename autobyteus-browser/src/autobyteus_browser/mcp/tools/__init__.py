"""Register the complete retained browser MCP tool inventory."""

from __future__ import annotations

from collections.abc import Awaitable
from typing import Any, TypeVar

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from autobyteus_browser.application import BrowserApplication
from autobyteus_browser.errors import BrowserError
from autobyteus_browser.json_codec import StrictJsonError, dumps_strict
from autobyteus_browser.mcp.tools.attach_tab import register as register_attach_tab
from autobyteus_browser.mcp.tools.close_tab import register as register_close_tab
from autobyteus_browser.mcp.tools.dom_snapshot import register as register_dom_snapshot
from autobyteus_browser.mcp.tools.list_tabs import register as register_list_tabs
from autobyteus_browser.mcp.tools.navigate_to import register as register_navigate_to
from autobyteus_browser.mcp.tools.open_tab import register as register_open_tab
from autobyteus_browser.mcp.tools.read_page import register as register_read_page
from autobyteus_browser.mcp.tools.run_script import register as register_run_script
from autobyteus_browser.mcp.tools.screenshot import register as register_screenshot

T = TypeVar("T")


async def invoke(operation: Awaitable[T]) -> T:
    try:
        return await operation
    except BrowserError as exc:
        try:
            suffix = f" details={dumps_strict(exc.details)}" if exc.details else ""
        except StrictJsonError:
            suffix = ""
        raise ToolError(f"{exc.code}: {exc.message}{suffix}") from exc


def register_tools(server: FastMCP, application: BrowserApplication) -> None:
    register_open_tab(server, application)
    register_attach_tab(server, application)
    register_close_tab(server, application)
    register_list_tabs(server, application)
    register_navigate_to(server, application)
    register_read_page(server, application)
    register_screenshot(server, application)
    register_dom_snapshot(server, application)
    register_run_script(server, application)
