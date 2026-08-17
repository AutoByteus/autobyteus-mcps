from mcp.server.fastmcp import FastMCP

from autobyteus_browser.application import BrowserApplication
from autobyteus_browser.contracts import ReadPageResult


def register(server: FastMCP, application: BrowserApplication) -> None:
    from autobyteus_browser.mcp.tools import invoke

    @server.tool(name="read_page", title="Read page", description="Read page content inline or into a workspace artifact.", structured_output=True)
    async def read_page(
        tab_id: str,
        cleaning_mode: str = "thorough",
        output_file: str | None = None,
        overwrite: bool = False,
    ) -> ReadPageResult:
        return await invoke(
            application.read_page(
                tab_id=tab_id,
                cleaning_mode=cleaning_mode,
                output_file=output_file,
                overwrite=overwrite,
            )
        )
