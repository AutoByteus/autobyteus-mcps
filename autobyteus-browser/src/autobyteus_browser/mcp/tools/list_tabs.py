from mcp.server.fastmcp import FastMCP

from autobyteus_browser.application import BrowserApplication
from autobyteus_browser.contracts import ListTabsResult


def register(server: FastMCP, application: BrowserApplication) -> None:
    from autobyteus_browser.mcp.tools import invoke

    @server.tool(name="list_tabs", title="List tabs", description="List all addressable tabs in the configured Chrome context.", structured_output=True)
    async def list_tabs() -> ListTabsResult:
        return await invoke(application.list_tabs())
