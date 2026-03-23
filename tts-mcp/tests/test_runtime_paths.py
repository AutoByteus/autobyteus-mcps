from __future__ import annotations

from pathlib import Path

import tts_mcp.runtime_paths as runtime_paths


def test_resolve_runtime_root_prefers_env_override(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("TTS_MCP_ROOT_DIR", str(tmp_path / "custom-root"))

    assert runtime_paths.resolve_runtime_root() == (tmp_path / "custom-root").resolve(strict=False)


def test_resolve_runtime_root_falls_back_to_home_dot_tts_mcp(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv("TTS_MCP_ROOT_DIR", raising=False)
    monkeypatch.setattr(runtime_paths, "detect_source_root", lambda: None)
    monkeypatch.setattr(runtime_paths.Path, "home", staticmethod(lambda: tmp_path))

    assert runtime_paths.resolve_runtime_root() == (tmp_path / ".tts-mcp").resolve(strict=False)


def test_resolve_runtime_script_path_uses_packaged_asset_when_no_source_root(monkeypatch) -> None:
    monkeypatch.setattr(runtime_paths, "detect_source_root", lambda: None)

    resolved = runtime_paths.resolve_runtime_script_path("xtts_generate.py")

    assert resolved.name == "xtts_generate.py"
    assert resolved.exists()
