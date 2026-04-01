from __future__ import annotations

import sys

from .config import ServerConfig, TtsSettings, load_settings
from .runtime_installation import prepare_startup_runtime
from .server import create_server


def run_server(
    settings: TtsSettings | None = None,
    server_config: ServerConfig | None = None,
) -> None:
    resolved_settings = settings or load_settings()
    resolved_server_config = server_config or ServerConfig.from_env()
    startup_notes = prepare_startup_runtime(resolved_settings)
    for note in startup_notes:
        print(f"[tts-mcp] {note}", file=sys.stderr)

    server = create_server(
        settings=resolved_settings,
        server_config=resolved_server_config,
    )
    server.run()


def main() -> None:
    run_server()
