from mcp.server.fastmcp import FastMCP

from autobyteus_browser.application import BrowserApplication
from autobyteus_browser.contracts import TabSummary


def register(server: FastMCP, application: BrowserApplication) -> None:
    from autobyteus_browser.mcp.tools import invoke

    @server.tool(name="attach_tab", title="Attach tab", description="Find exactly one existing tab and return its opaque target ID.", structured_output=True)
    async def attach_tab(url_contains: str | None = None, title_contains: str | None = None) -> TabSummary:
        return await invoke(application.attach_tab(url_contains=url_contains, title_contains=title_contains))
