from mcp.server.fastmcp import FastMCP

from browser_mcp.tabs import TabManager
from browser_mcp.types import AttachTabResult


def register(server: FastMCP, tab_manager: TabManager) -> None:
    @server.tool(
        name="attach_tab",
        title="Attach tab",
        description="Attach an existing browser tab from the current CDP context.",
        structured_output=True,
    )
    async def attach_tab(
        url_contains: str | None = None,
        title_contains: str | None = None,
    ) -> AttachTabResult:
        tab = await tab_manager.attach_existing_tab(
            url_contains=url_contains,
            title_contains=title_contains,
        )

        page = tab.integrator.page
        title: str | None = tab.title_cache
        if page and not page.is_closed():
            try:
                title = await page.title()
            except Exception:
                pass

        return AttachTabResult(
            tab_id=tab.tab_id,
            attach_state=tab.attach_state,
            attached_by=tab.attached_by,
            url=page.url if page else (tab.last_url or ""),
            title=title,
            attached=True,
        )
