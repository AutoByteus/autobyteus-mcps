from mcp.server.fastmcp import FastMCP

from autobyteus_browser.application import BrowserApplication
from autobyteus_browser.contracts import TabSummary


def register(server: FastMCP, application: BrowserApplication) -> None:
    from autobyteus_browser.mcp.tools import invoke

    @server.tool(name="open_tab", title="Open tab", description="Open a browser tab and return its opaque target ID.", structured_output=True)
    async def open_tab(
        url: str | None = None,
        wait_until: str = "domcontentloaded",
        timeout_ms: int = 60_000,
    ) -> TabSummary:
        return await invoke(application.open_tab(url=url, wait_until=wait_until, timeout_ms=timeout_ms))
