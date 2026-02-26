from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any

import pytest

from computer_use_mcp.config import X11Settings
import computer_use_mcp.runner as runner


ROOT_GEOMETRY = """
xwininfo: Window id: 0x519 (the root window) (has no name)

  Width: 1920
  Height: 1080
  Absolute upper-left X: 0
  Absolute upper-left Y: 0
""".strip()


def _settings(tmp_path: Path, *, command_prefix: tuple[str, ...] = tuple(), display: str = ":99") -> X11Settings:
    return X11Settings(
        display=display,
        timeout_seconds=5,
        command_prefix=command_prefix,
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


def test_run_get_screen_info_direct_sets_display_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    settings = _settings(tmp_path, display=":55")

    def fake_run(command: list[str], **kwargs: Any):
        assert command == ["xwininfo", "-root"]
        assert kwargs["env"]["DISPLAY"] == ":55"
        return subprocess.CompletedProcess(command, 0, stdout=ROOT_GEOMETRY, stderr="")

    monkeypatch.setattr(runner.subprocess, "run", fake_run)

    result = runner.run_get_screen_info(settings)

    assert result["ok"] is True
    assert result["result"]["width"] == 1920
    assert result["result"]["height"] == 1080


def test_run_get_screen_info_prefix_includes_env_display(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    settings = _settings(tmp_path, command_prefix=("docker", "exec", "llm-server-0"), display=":66")

    def fake_run(command: list[str], **kwargs: Any):
        assert command[:5] == ["docker", "exec", "llm-server-0", "env", "DISPLAY=:66"]
        assert command[-2:] == ["xwininfo", "-root"]
        return subprocess.CompletedProcess(command, 0, stdout=ROOT_GEOMETRY, stderr="")

    monkeypatch.setattr(runner.subprocess, "run", fake_run)

    result = runner.run_get_screen_info(settings)

    assert result["ok"] is True


def test_run_mouse_click_validation_error(tmp_path: Path):
    settings = _settings(tmp_path)

    result = runner.run_mouse_click(settings, button=0)

    assert result["ok"] is False
    assert result["error_type"] == "validation"


def test_run_mouse_move_absolute_uses_non_sync_command(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    settings = _settings(tmp_path)

    calls: list[list[str]] = []

    def fake_run(command: list[str], **kwargs: Any):
        calls.append(command)
        if command == ["xdotool", "mousemove", "20", "30"]:
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")
        if command == ["xdotool", "getmouselocation", "--shell"]:
            return subprocess.CompletedProcess(command, 0, stdout="X=20\nY=30\nSCREEN=0\nWINDOW=123\n", stderr="")
        raise AssertionError(f"Unexpected command: {command}")

    monkeypatch.setattr(runner.subprocess, "run", fake_run)

    result = runner.run_mouse_move(settings, x=20, y=30)

    assert result["ok"] is True
    assert calls[0] == ["xdotool", "mousemove", "20", "30"]


def test_run_mouse_drag_uses_non_sync_move_steps(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    settings = _settings(tmp_path)

    calls: list[list[str]] = []

    def fake_run(command: list[str], **kwargs: Any):
        calls.append(command)
        if command == ["xdotool", "mousemove", "5", "6"]:
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")
        if command == ["xdotool", "mousedown", "1"]:
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")
        if command == ["xdotool", "mousemove", "7", "8"]:
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")
        if command == ["xdotool", "mouseup", "1"]:
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")
        if command == ["xdotool", "getmouselocation", "--shell"]:
            return subprocess.CompletedProcess(command, 0, stdout="X=7\nY=8\nSCREEN=0\nWINDOW=123\n", stderr="")
        raise AssertionError(f"Unexpected command: {command}")

    monkeypatch.setattr(runner.subprocess, "run", fake_run)

    result = runner.run_mouse_drag(settings, start_x=5, start_y=6, end_x=7, end_y=8, button=1)

    assert result["ok"] is True
    assert calls[0] == ["xdotool", "mousemove", "5", "6"]
    assert calls[2] == ["xdotool", "mousemove", "7", "8"]


def test_run_list_windows_empty_when_search_exit_one(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    settings = _settings(tmp_path)

    def fake_run(command: list[str], **kwargs: Any):
        assert command == ["xdotool", "search", "--name", "."]
        return subprocess.CompletedProcess(command, 1, stdout="", stderr="")

    monkeypatch.setattr(runner.subprocess, "run", fake_run)

    result = runner.run_list_windows(settings)

    assert result["ok"] is True
    assert result["result"]["windows"] == []


def test_run_focus_window_by_id_uses_non_sync_activate(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    settings = _settings(tmp_path)

    def fake_run(command: list[str], **kwargs: Any):
        assert command == ["xdotool", "windowactivate", "123"]
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    monkeypatch.setattr(
        runner,
        "_describe_window",
        lambda window_id, _settings: {"ok": True, "result": {"window_id": window_id, "name": "Chrome"}},
    )

    result = runner.run_focus_window(settings, window_id="123")

    assert result["ok"] is True
    assert result["result"]["window_id"] == "123"


def test_run_focus_window_by_name_uses_resolved_window(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    settings = _settings(tmp_path)

    def fake_run(command: list[str], **kwargs: Any):
        assert command == ["xdotool", "windowactivate", "321"]
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    monkeypatch.setattr(
        runner,
        "run_list_windows",
        lambda settings, name_contains=None, limit=None: {
            "ok": True,
            "result": {"windows": [{"window_id": "321", "name": "Chrome"}], "count": 1},
        },
    )
    monkeypatch.setattr(
        runner,
        "_describe_window",
        lambda window_id, _settings: {"ok": True, "result": {"window_id": window_id, "name": "Chrome"}},
    )

    result = runner.run_focus_window(settings, name_contains="Chrome")

    assert result["ok"] is True
    assert result["result"]["window_id"] == "321"


def test_run_capture_screenshot_creates_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    settings = _settings(tmp_path)

    def fake_run(command: list[str], **kwargs: Any):
        if command and command[0] == "scrot":
            output = Path(command[-1])
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b"png-data")
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")
        if command == ["xwininfo", "-root"]:
            return subprocess.CompletedProcess(command, 0, stdout=ROOT_GEOMETRY, stderr="")
        raise AssertionError(f"Unexpected command: {command}")

    monkeypatch.setattr(runner.subprocess, "run", fake_run)

    result = runner.run_capture_screenshot(settings, output_file_path="capture.png")

    assert result["ok"] is True
    assert result["result"]["file_exists"] is True
    assert result["result"]["file_path"].endswith("capture.png")
    assert result["result"]["width"] == 1920
