from __future__ import annotations

import pytest

from autobyteus_browser.runtime import BrowserRuntime, BrowserSession


class FakeCdpSession:
    def __init__(self, target_id: str) -> None:
        self.target_id = target_id
        self.detached = False

    async def send(self, method: str):
        assert method == "Target.getTargetInfo"
        return {"targetInfo": {"targetId": self.target_id}}

    async def detach(self) -> None:
        self.detached = True


class FakePage:
    url = "https://example.com"

    def is_closed(self) -> bool:
        return False

    async def title(self) -> str:
        return "Example"


class FakeContext:
    def __init__(self) -> None:
        self.pages = [FakePage()]
        self.cdp_session: FakeCdpSession | None = None

    async def new_cdp_session(self, _page: FakePage) -> FakeCdpSession:
        self.cdp_session = FakeCdpSession("opaque-target-id")
        return self.cdp_session


@pytest.mark.anyio
async def test_browser_session_uses_public_cdp_target_info_and_detaches() -> None:
    context = FakeContext()
    session = BrowserSession(browser=object(), context=context)
    summary = await session.summarize_page(context.pages[0])
    assert summary == {
        "tab_id": "opaque-target-id",
        "url": "https://example.com",
        "title": "Example",
    }
    assert context.cdp_session is not None and context.cdp_session.detached


@pytest.mark.anyio
async def test_runtime_disconnects_client_without_browser_close() -> None:
    context = FakeContext()

    class FakeBrowser:
        contexts = [context]

        async def close(self) -> None:
            raise AssertionError("Runtime must not close the remote browser")

    class FakePlaywright:
        stopped = False

        async def stop(self) -> None:
            self.stopped = True

    class FakeManager:
        def __init__(self) -> None:
            self.browser = FakeBrowser()
            self.playwright = FakePlaywright()

        async def ensure_browser_launched(self) -> None:
            return None

        async def connect_browser(self) -> FakeBrowser:
            return self.browser

    manager = FakeManager()
    playwright = manager.playwright
    runtime = BrowserRuntime(manager_factory=lambda: manager)
    async with runtime.session() as session:
        assert session.context is context

    assert playwright.stopped
    assert manager.browser is None
    assert manager.playwright is None
