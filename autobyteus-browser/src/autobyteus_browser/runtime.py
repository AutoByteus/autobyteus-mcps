"""Short-lived Chrome/CDP connection and target-resolution boundary."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from brui_core.browser.browser_launcher import get_browser_config
from brui_core.browser.browser_manager import BrowserManager

from autobyteus_browser.contracts import TabSummary
from autobyteus_browser.errors import BrowserError, browser_unavailable, tab_not_found

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class BrowserSession:
    """One connected first-context view owned by BrowserRuntime."""

    browser: Any
    context: Any

    async def target_id_for_page(self, page: Any) -> str:
        cdp_session = await self.context.new_cdp_session(page)
        try:
            response = await cdp_session.send("Target.getTargetInfo")
        finally:
            await cdp_session.detach()
        target_info = response.get("targetInfo") if isinstance(response, dict) else None
        target_id = target_info.get("targetId") if isinstance(target_info, dict) else None
        if not isinstance(target_id, str) or not target_id:
            raise BrowserError(
                "BROWSER_OPERATION_FAILED",
                "Chrome did not provide an addressable target identifier for the page.",
                retryable=True,
                exit_status=5,
            )
        return target_id

    async def summarize_page(self, page: Any) -> TabSummary:
        target_id = await self.target_id_for_page(page)
        try:
            title = await page.title()
        except Exception:
            title = None
        return {"tab_id": target_id, "url": page.url or "", "title": title}

    async def list_tabs(self) -> list[TabSummary]:
        tabs: list[TabSummary] = []
        for page in list(self.context.pages):
            if page.is_closed():
                continue
            try:
                tabs.append(await self.summarize_page(page))
            except Exception as exc:
                if page.is_closed():
                    logger.debug("A page closed while browser targets were being listed: %s", exc)
                    continue
                raise BrowserError(
                    "BROWSER_OPERATION_FAILED",
                    "Chrome target metadata could not be read for an addressable page.",
                    retryable=True,
                    exit_status=5,
                ) from exc
        return tabs

    async def resolve_page(self, tab_id: str) -> Any:
        for page in list(self.context.pages):
            if page.is_closed():
                continue
            try:
                candidate_id = await self.target_id_for_page(page)
            except Exception:
                continue
            if candidate_id == tab_id:
                return page
        raise tab_not_found(tab_id)


class BrowserRuntime:
    """Own connection, first-context selection, target lookup, and disconnect."""

    def __init__(self, manager_factory: Callable[[], Any] = BrowserManager) -> None:
        self._manager_factory = manager_factory
        self._operation_lock = asyncio.Lock()

    @property
    def endpoint(self) -> str:
        try:
            config = get_browser_config()
            port = config["browser"].get("remote_debugging_port", 9222)
        except Exception:
            port = 9222
        return f"http://localhost:{port}"

    @asynccontextmanager
    async def session(self) -> AsyncIterator[BrowserSession]:
        async with self._operation_lock:
            manager = self._manager_factory()
            try:
                await manager.ensure_browser_launched()
                browser = await manager.connect_browser()
                if not browser.contexts:
                    raise browser_unavailable("Chrome exposed no browser context at the configured CDP endpoint.")
                context = browser.contexts[0]
            except BrowserError:
                await self._disconnect(manager)
                raise
            except Exception as exc:
                await self._disconnect(manager)
                logger.error("Unable to connect to Chrome over CDP: %s", exc)
                raise browser_unavailable() from exc

            try:
                yield BrowserSession(browser=browser, context=context)
            finally:
                await self._disconnect(manager)

    async def _disconnect(self, manager: Any) -> None:
        """Stop only the Playwright client; never close Chrome, its context, or pages."""

        playwright = getattr(manager, "playwright", None)
        manager.browser = None
        manager.playwright = None
        if playwright is None:
            return
        try:
            await playwright.stop()
        except Exception as exc:
            logger.warning("Failed to cleanly disconnect the Playwright client: %s", exc)
