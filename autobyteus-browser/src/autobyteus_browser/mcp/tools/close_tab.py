from mcp.server.fastmcp import FastMCP

from autobyteus_browser.application import BrowserApplication
from autobyteus_browser.contracts import CloseTabResult


def register(server: FastMCP, application: BrowserApplication) -> None:
    from autobyteus_browser.mcp.tools import invoke

    @server.tool(name="close_tab", title="Close tab", description="Close exactly one tab by opaque target ID.", structured_output=True)
    async def close_tab(tab_id: str) -> CloseTabResult:
        return await invoke(application.close_tab(tab_id=tab_id))
