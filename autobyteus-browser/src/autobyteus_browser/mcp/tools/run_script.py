from typing import Any

from mcp.server.fastmcp import FastMCP

from autobyteus_browser.application import BrowserApplication
from autobyteus_browser.contracts import RunScriptResult


def register(server: FastMCP, application: BrowserApplication) -> None:
    from autobyteus_browser.mcp.tools import invoke

    @server.tool(name="run_script", title="Run script", description="Advanced: evaluate JavaScript in one explicit tab.", structured_output=True)
    async def run_script(
        tab_id: str,
        script: str,
        arg: Any | None = None,
        output_file: str | None = None,
        overwrite: bool = False,
    ) -> RunScriptResult:
        return await invoke(
            application.run_script(
                tab_id=tab_id,
                script=script,
                arg=arg,
                output_file=output_file,
                overwrite=overwrite,
            )
        )
