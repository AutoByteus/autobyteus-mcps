from __future__ import annotations

from pathlib import Path

import anyio
import pytest

from mcp.client.session import ClientSession
from mcp.shared.message import SessionMessage

from computer_use_mcp.config import ServerConfig, X11Settings
import computer_use_mcp.server as server_module


@pytest.fixture
def anyio_backend():
    return "asyncio"


def _settings(tmp_path: Path) -> X11Settings:
    return X11Settings(
        display=":99",
        timeout_seconds=5,
        command_prefix=tuple(),
        required_tools=("xdotool", "xwininfo", "xprop", "scrot"),
        workspace_root=str(tmp_path),
        screenshot_dir=str((tmp_path / "shots").resolve()),
        max_text_chars=2000,
        max_key_combo_chars=256,
        max_windows=50,
        transport="stdio",
        host="127.0.0.1",
        port=8000,
    )


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


def _assert_contains(payload: dict, expected_subset: dict) -> None:
    for key, value in expected_subset.items():
        assert payload.get(key) == value


@pytest.mark.anyio
async def test_health_tool_delegates_runner(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    expected = {
        "ok": True,
        "action": "health_check",
        "display": ":99",
        "command": ["xwininfo", "-root"],
        "result": {"tool_status": {"xdotool": True}, "missing_tools": []},
    }
    monkeypatch.setattr(server_module, "run_health_check", lambda _settings: expected)

    server = server_module.create_server(
        settings=_settings(tmp_path),
        server_config=ServerConfig(name="x11-test"),
    )

    async def run_client(session: ClientSession):
        result = await session.call_tool("x11_health_check", {})
        assert not result.isError
        assert result.structuredContent is not None
        _assert_contains(result.structuredContent, expected)

    await _run_with_session(server, run_client)


@pytest.mark.anyio
async def test_list_windows_tool_delegates_runner(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    expected = {
        "ok": True,
        "action": "list_windows",
        "display": ":99",
        "command": ["xdotool", "search", "--name", "Chrome"],
        "result": {"windows": [{"window_id": "123", "name": "Chrome"}], "count": 1},
    }

    def fake_list(settings, name_contains=None, limit=None):
        assert settings.display == ":99"
        assert name_contains == "Chrome"
        assert limit == 1
        return expected

    monkeypatch.setattr(server_module, "run_list_windows", fake_list)

    server = server_module.create_server(
        settings=_settings(tmp_path),
        server_config=ServerConfig(name="x11-test"),
    )

    async def run_client(session: ClientSession):
        result = await session.call_tool("x11_list_windows", {"name_contains": "Chrome", "limit": 1})
        assert not result.isError
        assert result.structuredContent is not None
        _assert_contains(result.structuredContent, expected)

    await _run_with_session(server, run_client)


@pytest.mark.anyio
async def test_capture_screenshot_tool_delegates_runner(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    expected = {
        "ok": True,
        "action": "capture_screenshot",
        "display": ":99",
        "command": ["scrot", "/tmp/capture.png"],
        "result": {
            "file_path": "/tmp/capture.png",
            "file_exists": True,
            "width": 1920,
            "height": 1080,
        },
    }

    def fake_capture(settings, output_file_path=None):
        assert settings.display == ":99"
        assert output_file_path == "capture.png"
        return expected

    monkeypatch.setattr(server_module, "run_capture_screenshot", fake_capture)

    server = server_module.create_server(
        settings=_settings(tmp_path),
        server_config=ServerConfig(name="x11-test"),
    )

    async def run_client(session: ClientSession):
        result = await session.call_tool("x11_capture_screenshot", {"output_file_path": "capture.png"})
        assert not result.isError
        assert result.structuredContent is not None
        _assert_contains(result.structuredContent, expected)

    await _run_with_session(server, run_client)
