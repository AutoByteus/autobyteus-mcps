import asyncio
from dataclasses import dataclass
from datetime import datetime

from brui_core.ui_integrator import UIIntegrator
from browser_mcp.types import TabListEntry


def create_integrator() -> UIIntegrator:
    return UIIntegrator()


async def prepare_integrator() -> UIIntegrator:
    integrator = create_integrator()
    await integrator.initialize()
    return integrator


@dataclass(slots=True)
class BrowserTab:
    tab_id: str
    integrator: UIIntegrator
    created_at: datetime
    last_url: str | None = None
    title_cache: str | None = None
    attach_state: str = "attached"
    attached_by: str = "open_tab"


class TabManager:
    def __init__(self) -> None:
        self._tabs: dict[str, BrowserTab] = {}
        self._lock = asyncio.Lock()
        self._next_tab_number = 1

    async def open_tab(self) -> BrowserTab:
        integrator = await prepare_integrator()
        async with self._lock:
            tab_id = self._allocate_tab_id()
            tab = BrowserTab(
                tab_id=tab_id,
                integrator=integrator,
                created_at=datetime.utcnow(),
                attach_state="attached",
                attached_by="open_tab",
            )
            self._tabs[tab_id] = tab
        return tab

    async def attach_existing_tab(self, url_contains: str | None = None, title_contains: str | None = None) -> BrowserTab:
        url_match = (url_contains or "").strip()
        title_match = (title_contains or "").strip()
        if not url_match and not title_match:
            raise ValueError("Provide at least one matcher: url_contains or title_contains.")

        integrator = await prepare_integrator()
        context = integrator.context
        temporary_page = integrator.page

        if not context:
            await integrator.close(close_page=True, close_context=False, close_browser=False)
            raise RuntimeError("Playwright context not initialized")

        candidates = [page for page in context.pages if page is not temporary_page and not page.is_closed()]
        matches: list[tuple[object, str | None]] = []
        for page in candidates:
            page_url = getattr(page, "url", "") or ""
            if url_match and url_match.lower() not in page_url.lower():
                continue

            page_title: str | None = None
            if title_match:
                try:
                    page_title = await page.title()
                except Exception:
                    page_title = None
                if not page_title or title_match.lower() not in page_title.lower():
                    continue
            matches.append((page, page_title))

        if len(matches) != 1:
            await integrator.close(close_page=True, close_context=False, close_browser=False)
            if not matches:
                raise ValueError("No page matched attach criteria.")
            raise ValueError("Multiple pages matched attach criteria. Provide a more specific matcher.")

        matched_page, matched_title = matches[0]
        if temporary_page and temporary_page is not matched_page and not temporary_page.is_closed():
            await temporary_page.close()

        integrator.page = matched_page

        async with self._lock:
            tab_id = self._allocate_tab_id()
            tab = BrowserTab(
                tab_id=tab_id,
                integrator=integrator,
                created_at=datetime.utcnow(),
                last_url=(matched_page.url or None),
                title_cache=matched_title,
                attach_state="attached",
                attached_by="attach_tab",
            )
            self._tabs[tab_id] = tab
        return tab

    async def close_tab(
        self,
        tab_id: str,
        close_browser: bool = False,
    ) -> tuple[str, bool]:
        async with self._lock:
            tab = self._tabs.pop(tab_id, None)
            if not tab:
                raise ValueError(
                    f"Unknown tab_id: {tab_id}. "
                    "Attach or open a tab first via attach_tab or open_tab, then retry."
                )

        await tab.integrator.close(close_browser=close_browser)
        return tab_id, True

    def get_tab(self, tab_id: str) -> BrowserTab | None:
        return self._tabs.get(tab_id)

    async def list_tabs(self) -> list[TabListEntry]:
        async with self._lock:
            tabs = sorted(self._tabs.values(), key=lambda tab: int(tab.tab_id))

        result: list[TabListEntry] = []
        for tab in tabs:
            page = tab.integrator.page
            url = tab.last_url or (page.url if page else "")
            title = tab.title_cache
            if page and not page.is_closed():
                try:
                    title = await page.title()
                except Exception:
                    pass
            result.append(
                TabListEntry(
                    tab_id=tab.tab_id,
                    attach_state=tab.attach_state,
                    attached_by=tab.attached_by,
                    url=url or "",
                    title=title,
                    created_at=f"{tab.created_at.isoformat()}Z",
                )
            )
        return result

    def _allocate_tab_id(self) -> str:
        # Numeric tab IDs capped at 6 digits for human-readable handles.
        max_tab_number = 999999
        start = self._next_tab_number

        while True:
            candidate = str(self._next_tab_number)
            self._next_tab_number += 1
            if self._next_tab_number > max_tab_number:
                self._next_tab_number = 1

            if candidate not in self._tabs:
                return candidate
            if self._next_tab_number == start:
                raise RuntimeError("No available tab IDs. Close tabs and retry.")


async def get_tab_or_raise(tab_manager: TabManager, tab_id: str) -> BrowserTab:
    tab = tab_manager.get_tab(tab_id)
    if not tab:
        raise ValueError(f"Unknown tab_id: {tab_id}")
    return tab
