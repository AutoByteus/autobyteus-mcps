from __future__ import annotations

from pathlib import Path

import pytest

from computer_use_mcp.config import ConfigError, load_settings


def test_load_settings_defaults(tmp_path: Path):
    settings = load_settings({"AUTOBYTEUS_AGENT_WORKSPACE": str(tmp_path)})

    assert settings.transport == "streamable-http"
    assert settings.host == "0.0.0.0"
    assert settings.port == 8765
    assert settings.display == ":99"
    assert settings.timeout_seconds == 10
    assert settings.required_tools == ("xdotool", "xwininfo", "xprop", "scrot")
    assert settings.workspace_root == str(tmp_path.resolve())
    assert settings.screenshot_dir == str((tmp_path / "artifacts/screenshots").resolve())


def test_load_settings_with_prefix_and_custom_transport(tmp_path: Path):
    settings = load_settings(
        {
            "AUTOBYTEUS_AGENT_WORKSPACE": str(tmp_path),
            "X11_MCP_TRANSPORT": "stdio",
            "X11_MCP_COMMAND_PREFIX": "docker exec llm-server-0",
            "X11_MCP_DISPLAY": ":77",
            "X11_MCP_PORT": "9123",
        }
    )

    assert settings.transport == "stdio"
    assert settings.command_prefix == ("docker", "exec", "llm-server-0")
    assert settings.display == ":77"
    assert settings.port == 9123


def test_invalid_transport_raises(tmp_path: Path):
    with pytest.raises(ConfigError, match="X11_MCP_TRANSPORT"):
        load_settings(
            {
                "AUTOBYTEUS_AGENT_WORKSPACE": str(tmp_path),
                "X11_MCP_TRANSPORT": "http-only",
            }
        )


def test_invalid_required_tool_name_raises(tmp_path: Path):
    with pytest.raises(ConfigError, match="invalid tool name"):
        load_settings(
            {
                "AUTOBYTEUS_AGENT_WORKSPACE": str(tmp_path),
                "X11_MCP_REQUIRED_TOOLS": "xdotool, bad tool",
            }
        )
