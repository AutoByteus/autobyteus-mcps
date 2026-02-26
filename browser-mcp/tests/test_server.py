from __future__ import annotations

import anyio
from pathlib import Path
import pytest

from mcp.client.session import ClientSession
from mcp.shared.message import SessionMessage

import browser_mcp.server as browser_server
import browser_mcp.tabs as browser_tabs


async def _run_with_session(server, client_callable):
    client_to_server_send, server_read_stream = anyio.create_memory_object_stream[SessionMessage | Exception](0)
    server_to_client_send, client_read_stream = anyio.create_memory_object_stream[SessionMessage](0)

    async def server_task():
        await server._mcp_server.run(  # type: ignore[attr-defined]
            server_read_stream,
            server_to_client_send,
            server._mcp_server.create_initialization_options(),  # type: ignore[attr-defined]
            raise_exceptions=True,
        )

    async with anyio.create_task_group() as tg:
        tg.start_soon(server_task)
        async with ClientSession(client_read_stream, client_to_server_send) as session:
            await session.initialize()
            await client_callable(session)
        await client_to_server_send.aclose()
        await server_to_client_send.aclose()
        tg.cancel_scope.cancel()


class FakeResponse:
    def __init__(self, ok: bool = True, status: int = 200) -> None:
        self.ok = ok
        self.status = status


class FakeLocator:
    def __init__(self) -> None:
        self.actions: list[tuple[str, object | None]] = []

    async def wait_for(self, **_kwargs):
        return None

    async def click(self):
        self.actions.append(("click", None))

    async def type(self, text: str):
        self.actions.append(("type", text))

    async def fill(self, text: str):
        self.actions.append(("fill", text))

    async def select_option(self, value: str):
        self.actions.append(("select", value))

    async def check(self):
        self.actions.append(("check", None))

    async def uncheck(self):
        self.actions.append(("uncheck", None))

    async def hover(self):
        self.actions.append(("hover", None))

    async def dblclick(self):
        self.actions.append(("double_click", None))


class FakePage:
    def __init__(self, url: str = "about:blank", title: str = "Untitled") -> None:
        self.url = url
        self._title = title
        self._content = "<html><body><h1>Test</h1><script>bad()</script></body></html>"
        self._closed = False
        self.locators: list[FakeLocator] = []
        self.last_script: str | None = None
        self.last_arg: object | None = None

    async def goto(self, url: str, **_kwargs):
        self.url = url
        if "example.com" in url:
            self._title = "Example Domain"
        return FakeResponse()

    async def content(self):
        return self._content

    async def title(self) -> str:
        return self._title

    async def close(self):
        self._closed = True

    def is_closed(self) -> bool:
        return self._closed

    async def evaluate(self, script: str, arg: object | None = None):
        self.last_script = script
        self.last_arg = arg
        if isinstance(arg, dict) and arg.get("schemaVersion") == "autobyteus-dom-snapshot-v1":
            return {
                "schema_version": "autobyteus-dom-snapshot-v1",
                "total_candidates": 3,
                "returned_elements": 2,
                "truncated": False,
                "elements": [
                    {
                        "element_id": "e1",
                        "tag_name": "button",
                        "dom_id": "submit",
                        "css_selector": "#submit",
                        "role": "button",
                        "name": "Submit",
                        "text": "Submit",
                        "href": None,
                        "value": None,
                        "bounding_box": {"x": 10, "y": 20, "width": 100, "height": 30},
                    },
                    {
                        "element_id": "e2",
                        "tag_name": "a",
                        "dom_id": None,
                        "css_selector": "a:nth-of-type(1)",
                        "role": None,
                        "name": None,
                        "text": "Learn more",
                        "href": "https://example.com/docs",
                        "value": None,
                        "bounding_box": {"x": 10, "y": 60, "width": 90, "height": 20},
                    },
                ],
            }
        return {"script": script, "arg": arg}

    async def screenshot(self, path: str, **_kwargs):
        Path(path).write_bytes(b"fake")

    def locator(self, _selector: str):
        locator = FakeLocator()
        self.locators.append(locator)
        return locator


class FakeContext:
    def __init__(self, pages: list[FakePage]) -> None:
        self.pages = pages


class FakeUIIntegrator:
    shared_pages: list[FakePage] = []

    def __init__(self) -> None:
        self.page: FakePage | None = None
        self.context: FakeContext | None = None
        self.initialized = False

    @classmethod
    def add_external_page(cls, url: str, title: str) -> FakePage:
        page = FakePage(url=url, title=title)
        cls.shared_pages.append(page)
        return page

    async def initialize(self):
        page = FakePage(url="about:blank", title="New Tab")
        self.__class__.shared_pages.append(page)
        self.context = FakeContext(self.__class__.shared_pages)
        self.page = page
        self.initialized = True

    async def close(self, close_page: bool = True, **_kwargs):
        if close_page and self.page and not self.page.is_closed():
            await self.page.close()
        if self.page in self.__class__.shared_pages:
            self.__class__.shared_pages.remove(self.page)
        self.page = None
        self.context = None
        self.initialized = False


def _create_server_with_fake_ui():
    return browser_server.create_server()


@pytest.fixture(autouse=True)
def _patch_create_integrator(monkeypatch: pytest.MonkeyPatch):
    FakeUIIntegrator.shared_pages = []
    monkeypatch.setattr(browser_tabs, "create_integrator", lambda: FakeUIIntegrator())


def _error_text(result) -> str:
    return " ".join(getattr(item, "text", "") for item in (result.content or []))


def _find_tab(list_result, tab_id: str) -> dict:
    tabs = list_result.structuredContent["tabs"]
    for entry in tabs:
        if entry["tab_id"] == tab_id:
            return entry
    raise AssertionError(f"tab {tab_id} not found")


def test_runtime_config_defaults():
    config = browser_server.RuntimeConfig.from_env({})
    assert config.transport == "stdio"
    assert config.host == "0.0.0.0"
    assert config.port == 8765


def test_runtime_config_http_values():
    config = browser_server.RuntimeConfig.from_env(
        {
            "BROWSER_MCP_TRANSPORT": "streamable-http",
            "BROWSER_MCP_HOST": "127.0.0.1",
            "BROWSER_MCP_PORT": "9123",
        }
    )
    assert config.transport == "streamable-http"
    assert config.host == "127.0.0.1"
    assert config.port == 9123


def test_runtime_config_invalid_transport():
    with pytest.raises(browser_server.ConfigError, match="BROWSER_MCP_TRANSPORT"):
        browser_server.RuntimeConfig.from_env({"BROWSER_MCP_TRANSPORT": "http"})


def test_create_server_applies_runtime_host_port():
    config = browser_server.RuntimeConfig(transport="stdio", host="127.0.0.1", port=9999)
    server = browser_server.create_server(runtime_config=config)
    assert server.settings.host == "127.0.0.1"
    assert server.settings.port == 9999


def test_main_uses_configured_transport(monkeypatch: pytest.MonkeyPatch):
    captured: dict[str, str] = {}

    class FakeServer:
        def run(self, *, transport: str):
            captured["transport"] = transport

    monkeypatch.setattr(
        browser_server.RuntimeConfig,
        "from_env",
        classmethod(lambda cls, env=None: browser_server.RuntimeConfig(transport="streamable-http", host="0.0.0.0", port=8765)),
    )
    monkeypatch.setattr(browser_server, "create_server", lambda config=None, runtime_config=None: FakeServer())

    browser_server.main()

    assert captured["transport"] == "streamable-http"


def test_main_uses_stdio_transport(monkeypatch: pytest.MonkeyPatch):
    captured: dict[str, str] = {}

    class FakeServer:
        def run(self, *, transport: str):
            captured["transport"] = transport

    monkeypatch.setattr(
        browser_server.RuntimeConfig,
        "from_env",
        classmethod(lambda cls, env=None: browser_server.RuntimeConfig(transport="stdio", host="0.0.0.0", port=8765)),
    )
    monkeypatch.setattr(browser_server, "create_server", lambda config=None, runtime_config=None: FakeServer())

    browser_server.main()

    assert captured["transport"] == "stdio"


def test_main_invalid_runtime_config_exits(monkeypatch: pytest.MonkeyPatch):
    def _raise_config_error(cls, env=None):
        raise browser_server.ConfigError("bad transport")

    monkeypatch.setattr(browser_server.RuntimeConfig, "from_env", classmethod(_raise_config_error))

    with pytest.raises(SystemExit, match="Invalid browser MCP configuration"):
        browser_server.main()


@pytest.mark.anyio
async def test_list_tabs_empty():
    server = _create_server_with_fake_ui()

    async def run_client(session: ClientSession) -> None:
        result = await session.call_tool("list_tabs", {})
        assert not result.isError
        structured = result.structuredContent
        assert structured is not None
        assert structured["tabs"] == []

    await _run_with_session(server, run_client)


@pytest.mark.anyio
async def test_open_and_close_tab():
    server = _create_server_with_fake_ui()

    async def run_client(session: ClientSession) -> None:
        opened = await session.call_tool("open_tab", {"url": "https://example.com"})
        assert not opened.isError
        tab_id = opened.structuredContent["tab_id"]
        assert tab_id.isdigit()
        assert 1 <= len(tab_id) <= 6
        assert opened.structuredContent["url"] == "https://example.com"

        listed = await session.call_tool("list_tabs", {})
        listed_entry = _find_tab(listed, tab_id)
        assert listed_entry["attach_state"] == "attached"
        assert listed_entry["attached_by"] == "open_tab"

        closed = await session.call_tool("close_tab", {"tab_id": tab_id})
        assert closed.structuredContent["closed"] is True
        assert closed.structuredContent["tab_id"] == tab_id

        listed_after = await session.call_tool("list_tabs", {})
        assert listed_after.structuredContent["tabs"] == []

    await _run_with_session(server, run_client)


@pytest.mark.anyio
async def test_attach_tab_and_detach_close():
    server = _create_server_with_fake_ui()

    async def run_client(session: ClientSession) -> None:
        external = FakeUIIntegrator.add_external_page(
            url="https://chat.openai.com/c/abc-123",
            title="ChatGPT",
        )

        attached = await session.call_tool("attach_tab", {"url_contains": "chat.openai.com/c/abc-123"})
        assert not attached.isError
        structured = attached.structuredContent
        assert structured["attach_state"] == "attached"
        assert structured["attached_by"] == "attach_tab"
        assert structured["attached"] is True
        tab_id = structured["tab_id"]

        listed = await session.call_tool("list_tabs", {})
        listed_entry = _find_tab(listed, tab_id)
        assert listed_entry["attached_by"] == "attach_tab"
        assert listed_entry["title"] == "ChatGPT"

        closed = await session.call_tool("close_tab", {"tab_id": tab_id})
        assert not closed.isError
        assert closed.structuredContent["closed"] is True
        assert external.is_closed()

    await _run_with_session(server, run_client)


@pytest.mark.anyio
async def test_attach_tab_requires_matcher():
    server = _create_server_with_fake_ui()

    async def run_client(session: ClientSession) -> None:
        result = await session.call_tool("attach_tab", {})
        assert result.isError
        assert "matcher" in _error_text(result).lower()

    await _run_with_session(server, run_client)


@pytest.mark.anyio
async def test_attach_tab_fails_without_match():
    server = _create_server_with_fake_ui()

    async def run_client(session: ClientSession) -> None:
        result = await session.call_tool("attach_tab", {"url_contains": "does-not-exist"})
        assert result.isError
        assert "no page matched" in _error_text(result).lower()

    await _run_with_session(server, run_client)


@pytest.mark.anyio
async def test_close_tab_requires_tab_id():
    server = _create_server_with_fake_ui()

    async def run_client(session: ClientSession) -> None:
        result = await session.call_tool("close_tab", {})
        assert result.isError
        assert "tab_id" in _error_text(result)

    await _run_with_session(server, run_client)


@pytest.mark.anyio
async def test_close_tab_unknown_tab_id_returns_actionable_error():
    server = _create_server_with_fake_ui()

    async def run_client(session: ClientSession) -> None:
        result = await session.call_tool("close_tab", {"tab_id": "999999"})
        assert result.isError
        text = _error_text(result).lower()
        assert "unknown tab_id" in text
        assert "attach_tab" in text
        assert "open_tab" in text

    await _run_with_session(server, run_client)


@pytest.mark.anyio
async def test_navigate_to_requires_tab_id():
    server = _create_server_with_fake_ui()

    async def run_client(session: ClientSession) -> None:
        result = await session.call_tool("navigate_to", {"url": "https://example.com"})
        assert result.isError
        assert "tab_id" in _error_text(result)

    await _run_with_session(server, run_client)


@pytest.mark.anyio
async def test_read_page_requires_tab_id():
    server = _create_server_with_fake_ui()

    async def run_client(session: ClientSession) -> None:
        result = await session.call_tool("read_page", {"cleaning_mode": "text"})
        assert result.isError
        assert "tab_id" in _error_text(result)

    await _run_with_session(server, run_client)


@pytest.mark.anyio
async def test_read_page_with_explicit_tab_id():
    server = _create_server_with_fake_ui()

    async def run_client(session: ClientSession) -> None:
        opened = await session.call_tool("open_tab", {"url": "https://example.com"})
        tab_id = opened.structuredContent["tab_id"]

        result = await session.call_tool("read_page", {"tab_id": tab_id, "cleaning_mode": "text"})
        assert not result.isError
        structured = result.structuredContent
        assert structured["url"] == "https://example.com"
        assert "Test" in structured["content"]
        assert structured["tab_id"] == tab_id

    await _run_with_session(server, run_client)


@pytest.mark.anyio
async def test_screenshot_with_explicit_tab_id(tmp_path):
    server = _create_server_with_fake_ui()
    output_path = tmp_path / "shot.png"

    async def run_client(session: ClientSession) -> None:
        opened = await session.call_tool("open_tab", {"url": "https://example.com"})
        tab_id = opened.structuredContent["tab_id"]

        result = await session.call_tool(
            "screenshot",
            {"tab_id": tab_id, "file_path": str(output_path)},
        )
        assert not result.isError
        assert Path(result.structuredContent["file_path"]).is_file()
        assert result.structuredContent["tab_id"] == tab_id

    await _run_with_session(server, run_client)


@pytest.mark.anyio
async def test_dom_snapshot():
    server = _create_server_with_fake_ui()

    async def run_client(session: ClientSession) -> None:
        opened = await session.call_tool("open_tab", {"url": "https://example.com"})
        tab_id = opened.structuredContent["tab_id"]

        result = await session.call_tool(
            "dom_snapshot",
            {"tab_id": tab_id, "include_bounding_boxes": True, "max_elements": 50},
        )
        assert not result.isError
        structured = result.structuredContent
        assert structured is not None
        assert structured["url"] == "https://example.com"
        assert structured["total_candidates"] == 3
        assert structured["returned_elements"] == 2
        assert len(structured["elements"]) == 2
        assert structured["elements"][0]["element_id"] == "e1"
        assert structured["elements"][0]["css_selector"] == "#submit"
        assert structured["tab_id"] == tab_id

    await _run_with_session(server, run_client)


@pytest.mark.anyio
async def test_run_script_with_explicit_tab_id():
    server = _create_server_with_fake_ui()

    async def run_client(session: ClientSession) -> None:
        opened = await session.call_tool("open_tab", {"url": "https://example.com"})
        tab_id = opened.structuredContent["tab_id"]

        result = await session.call_tool(
            "run_script",
            {
                "tab_id": tab_id,
                "script": "return 1 + 1;",
                "arg": {"x": 1},
            },
        )
        assert not result.isError
        structured = result.structuredContent
        assert "return 1 + 1;" in structured["result"]["script"]
        assert structured["result"]["arg"] == {"x": 1}
        assert structured["tab_id"] == tab_id

    await _run_with_session(server, run_client)


@pytest.mark.anyio
async def test_run_script_requires_tab_id():
    server = _create_server_with_fake_ui()

    async def run_client(session: ClientSession) -> None:
        result = await session.call_tool(
            "run_script",
            {
                "script": "return 1 + 1;",
                "arg": {"x": 1},
            },
        )
        assert result.isError
        assert "tab_id" in _error_text(result)

    await _run_with_session(server, run_client)
