"""TTS MCP package."""

from .config import ServerConfig, TtsSettings


def create_server(
    settings: TtsSettings | None = None,
    server_config: ServerConfig | None = None,
):
    from .server import create_server as _create_server

    return _create_server(settings=settings, server_config=server_config)


def main() -> None:
    from .app_runtime import main as _main

    _main()

__all__ = ["create_server", "main"]
