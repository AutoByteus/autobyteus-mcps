import logging
import os
from dataclasses import dataclass
from typing import Literal, Mapping

from mcp.server.fastmcp import FastMCP

from browser_mcp.tabs import TabManager
from browser_mcp.tools import register_tools

DEFAULT_SERVER_NAME = "browser-mcp"
DEFAULT_INSTRUCTIONS = (
    "Expose browser automation tools backed by brui_core/Playwright. "
    "Use open_tab or attach_tab to obtain a tab_id, then run stateful tools with that tab_id."
)
_ALLOWED_TRANSPORTS = {"stdio", "streamable-http"}

logger = logging.getLogger(__name__)


def initialize_workspace() -> None:
    workspace_path = os.environ.get("AUTOBYTEUS_AGENT_WORKSPACE")
    if workspace_path:
        logger.info("AUTOBYTEUS_AGENT_WORKSPACE found: '%s'", workspace_path)
        if os.path.isdir(workspace_path):
            try:
                os.chdir(workspace_path)
                logger.info("Successfully changed CWD to: %s", os.getcwd())
            except Exception as exc:
                logger.error("Failed to change CWD to '%s': %s", workspace_path, exc, exc_info=True)
        else:
            logger.warning(
                "Workspace path '%s' does not exist or is not a directory. CWD not changed.",
                workspace_path,
            )
    else:
        logger.info("AUTOBYTEUS_AGENT_WORKSPACE not set. Using default CWD.")


initialize_workspace()


class ConfigError(ValueError):
    """Raised when browser MCP runtime configuration is invalid."""


@dataclass(slots=True)
class ServerConfig:
    name: str = DEFAULT_SERVER_NAME
    instructions: str = DEFAULT_INSTRUCTIONS

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "ServerConfig":
        actual_env = env if env is not None else os.environ
        name = actual_env.get("BROWSER_MCP_NAME", DEFAULT_SERVER_NAME)
        instructions = actual_env.get("BROWSER_MCP_INSTRUCTIONS", DEFAULT_INSTRUCTIONS)
        return cls(name=name, instructions=instructions)


@dataclass(slots=True)
class RuntimeConfig:
    transport: Literal["stdio", "streamable-http"] = "stdio"
    host: str = "0.0.0.0"
    port: int = 8765

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "RuntimeConfig":
        actual_env = env if env is not None else os.environ
        transport = _parse_transport(actual_env.get("BROWSER_MCP_TRANSPORT", "stdio"))
        host = _require_non_empty(actual_env, "BROWSER_MCP_HOST", default="0.0.0.0")
        port = _parse_port(actual_env.get("BROWSER_MCP_PORT", "8765"), "BROWSER_MCP_PORT")
        return cls(transport=transport, host=host, port=port)


def create_server(
    config: ServerConfig | None = None,
    runtime_config: RuntimeConfig | None = None,
) -> FastMCP:
    cfg = config or ServerConfig.from_env()
    runtime = runtime_config or RuntimeConfig.from_env()
    server = FastMCP(
        name=cfg.name,
        instructions=cfg.instructions,
        host=runtime.host,
        port=runtime.port,
    )
    tab_manager = TabManager()
    register_tools(server, tab_manager)
    return server


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    try:
        runtime = RuntimeConfig.from_env()
    except ConfigError as exc:
        raise SystemExit(f"Invalid browser MCP configuration: {exc}") from exc

    server = create_server(runtime_config=runtime)
    server.run(transport=runtime.transport)


def _parse_transport(raw_value: str | None) -> Literal["stdio", "streamable-http"]:
    value = (raw_value or "").strip().lower()
    if value not in _ALLOWED_TRANSPORTS:
        allowed = ", ".join(sorted(_ALLOWED_TRANSPORTS))
        raise ConfigError(f"BROWSER_MCP_TRANSPORT must be one of: {allowed}.")
    return value  # type: ignore[return-value]


def _parse_port(raw_value: str | None, key: str) -> int:
    if raw_value is None:
        raise ConfigError(f"{key} is required.")
    try:
        value = int(raw_value.strip())
    except ValueError as exc:
        raise ConfigError(f"{key} must be an integer.") from exc
    if value <= 0 or value > 65535:
        raise ConfigError(f"{key} must be in range 1..65535.")
    return value


def _require_non_empty(env: Mapping[str, str], key: str, default: str | None = None) -> str:
    raw_value = env.get(key, default or "")
    value = raw_value.strip()
    if not value:
        raise ConfigError(f"{key} must be non-empty.")
    if "\n" in value or "\r" in value:
        raise ConfigError(f"{key} cannot contain newline characters.")
    return value


if __name__ == "__main__":
    main()
