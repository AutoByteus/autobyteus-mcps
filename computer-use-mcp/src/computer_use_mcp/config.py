from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
import shlex
from typing import Literal, Mapping

DEFAULT_SERVER_NAME = "computer-use-mcp"
DEFAULT_INSTRUCTIONS = (
    "Expose deterministic X11 computer-use tools for Linux desktop control. "
    "Use health/screen/window tools before pointer or keyboard actions."
)

_ALLOWED_TRANSPORTS = {"stdio", "sse", "streamable-http"}
_TOOL_NAME_PATTERN = re.compile(r"^[A-Za-z0-9._+-]+$")


class ConfigError(ValueError):
    """Raised when computer-use MCP configuration is invalid."""


@dataclass(frozen=True, slots=True)
class X11Settings:
    display: str
    timeout_seconds: int
    command_prefix: tuple[str, ...]
    required_tools: tuple[str, ...]
    workspace_root: str
    screenshot_dir: str
    max_text_chars: int
    max_key_combo_chars: int
    max_windows: int
    transport: Literal["stdio", "sse", "streamable-http"]
    host: str
    port: int


@dataclass(frozen=True, slots=True)
class ServerConfig:
    name: str = DEFAULT_SERVER_NAME
    instructions: str = DEFAULT_INSTRUCTIONS

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "ServerConfig":
        actual_env = env if env is not None else os.environ
        return cls(
            name=actual_env.get("X11_MCP_NAME", DEFAULT_SERVER_NAME),
            instructions=actual_env.get("X11_MCP_INSTRUCTIONS", DEFAULT_INSTRUCTIONS),
        )


def load_settings(env: Mapping[str, str] | None = None) -> X11Settings:
    actual_env = env if env is not None else os.environ

    display = _require_non_empty(actual_env, "X11_MCP_DISPLAY", default=":99")
    timeout_seconds = _parse_positive_int(actual_env.get("X11_MCP_TIMEOUT_SECONDS", "10"), "X11_MCP_TIMEOUT_SECONDS")
    command_prefix = tuple(_parse_shell_args(actual_env.get("X11_MCP_COMMAND_PREFIX", "")))

    required_tools_raw = actual_env.get("X11_MCP_REQUIRED_TOOLS", "xdotool,xwininfo,xprop,scrot")
    required_tools = tuple(_parse_required_tools(required_tools_raw))
    if not required_tools:
        raise ConfigError("X11_MCP_REQUIRED_TOOLS cannot be empty.")

    workspace_root = _resolve_workspace_root(actual_env.get("AUTOBYTEUS_AGENT_WORKSPACE"))
    screenshot_dir = _resolve_screenshot_dir(actual_env.get("X11_MCP_SCREENSHOT_DIR", "artifacts/screenshots"), workspace_root)

    max_text_chars = _parse_positive_int(actual_env.get("X11_MCP_MAX_TEXT_CHARS", "2000"), "X11_MCP_MAX_TEXT_CHARS")
    max_key_combo_chars = _parse_positive_int(
        actual_env.get("X11_MCP_MAX_KEY_COMBO_CHARS", "256"),
        "X11_MCP_MAX_KEY_COMBO_CHARS",
    )
    max_windows = _parse_positive_int(actual_env.get("X11_MCP_MAX_WINDOWS", "50"), "X11_MCP_MAX_WINDOWS")

    transport = _parse_transport(actual_env.get("X11_MCP_TRANSPORT", "streamable-http"))
    host = _require_non_empty(actual_env, "X11_MCP_HOST", default="0.0.0.0")
    port = _parse_port(actual_env.get("X11_MCP_PORT", "8765"), "X11_MCP_PORT")

    return X11Settings(
        display=display,
        timeout_seconds=timeout_seconds,
        command_prefix=command_prefix,
        required_tools=required_tools,
        workspace_root=workspace_root,
        screenshot_dir=screenshot_dir,
        max_text_chars=max_text_chars,
        max_key_combo_chars=max_key_combo_chars,
        max_windows=max_windows,
        transport=transport,
        host=host,
        port=port,
    )


def _parse_transport(raw_value: str | None) -> Literal["stdio", "sse", "streamable-http"]:
    value = (raw_value or "").strip().lower()
    if value not in _ALLOWED_TRANSPORTS:
        allowed = ", ".join(sorted(_ALLOWED_TRANSPORTS))
        raise ConfigError(f"X11_MCP_TRANSPORT must be one of: {allowed}.")
    return value  # type: ignore[return-value]


def _parse_required_tools(raw_value: str) -> list[str]:
    tools: list[str] = []
    for token in raw_value.split(","):
        tool = token.strip()
        if not tool:
            continue
        if not _TOOL_NAME_PATTERN.fullmatch(tool):
            raise ConfigError(
                f"X11_MCP_REQUIRED_TOOLS contains invalid tool name '{tool}'. "
                "Allowed characters: letters, digits, dot, underscore, plus, hyphen."
            )
        tools.append(tool)
    return tools


def _resolve_workspace_root(raw_workspace: str | None) -> str:
    if raw_workspace and raw_workspace.strip():
        return str(Path(raw_workspace.strip()).expanduser().resolve())
    return str(Path.cwd().resolve())


def _resolve_screenshot_dir(raw_dir: str | None, workspace_root: str) -> str:
    if raw_dir is None or not raw_dir.strip():
        raise ConfigError("X11_MCP_SCREENSHOT_DIR must be non-empty.")
    candidate = Path(raw_dir.strip()).expanduser()
    if not candidate.is_absolute():
        candidate = Path(workspace_root) / candidate
    return str(candidate.resolve())


def _require_non_empty(env: Mapping[str, str], key: str, default: str | None = None) -> str:
    raw_value = env.get(key, default or "")
    value = raw_value.strip()
    if not value:
        raise ConfigError(f"{key} must be non-empty.")
    if "\n" in value or "\r" in value:
        raise ConfigError(f"{key} cannot contain newline characters.")
    return value


def _parse_shell_args(raw_value: str) -> list[str]:
    text = raw_value.strip()
    if not text:
        return []
    try:
        parts = shlex.split(text)
    except ValueError as exc:
        raise ConfigError(f"X11_MCP_COMMAND_PREFIX is invalid shell syntax: {exc}") from exc
    for item in parts:
        if "\n" in item or "\r" in item:
            raise ConfigError("X11_MCP_COMMAND_PREFIX cannot contain newline characters.")
    return parts


def _parse_positive_int(raw_value: str | None, key: str) -> int:
    if raw_value is None:
        raise ConfigError(f"{key} is required.")
    try:
        value = int(raw_value.strip())
    except ValueError as exc:
        raise ConfigError(f"{key} must be an integer.") from exc
    if value <= 0:
        raise ConfigError(f"{key} must be > 0.")
    return value


def _parse_port(raw_value: str | None, key: str) -> int:
    value = _parse_positive_int(raw_value, key)
    if value > 65535:
        raise ConfigError(f"{key} must be <= 65535.")
    return value
