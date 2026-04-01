from __future__ import annotations

from tts_mcp.config import ServerConfig, load_settings
import tts_mcp.app_runtime as app_runtime


def test_run_server_bootstraps_before_running_server(monkeypatch, capsys) -> None:
    settings = load_settings({"TTS_MCP_AUTO_INSTALL_RUNTIME": "false"})
    server_config = ServerConfig(name="tts-runtime-test")
    events: list[str] = []

    class _FakeServer:
        def run(self) -> None:
            events.append("run")

    monkeypatch.setattr(
        app_runtime,
        "prepare_startup_runtime",
        lambda passed_settings: (
            events.append(f"bootstrap:{passed_settings.default_backend}") or ["runtime ready"]
        ),
    )
    monkeypatch.setattr(
        app_runtime,
        "create_server",
        lambda *, settings, server_config: (
            events.append(f"create:{settings.default_backend}:{server_config.name}") or _FakeServer()
        ),
    )

    app_runtime.run_server(settings=settings, server_config=server_config)

    captured = capsys.readouterr()
    assert events == [
        "bootstrap:auto",
        "create:auto:tts-runtime-test",
        "run",
    ]
    assert "[tts-mcp] runtime ready" in captured.err
