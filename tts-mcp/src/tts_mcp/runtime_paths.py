from __future__ import annotations

from importlib import resources
import os
from pathlib import Path


_RUNTIME_ROOT_ENV = "TTS_MCP_ROOT_DIR"
_DEFAULT_RUNTIME_ROOT_DIRNAME = ".tts-mcp"


def detect_source_root() -> Path | None:
    candidate = Path(__file__).resolve().parents[2]
    if not (candidate / "pyproject.toml").exists():
        return None
    if not (candidate / "src" / "tts_mcp").is_dir():
        return None
    if not (candidate / "scripts").is_dir():
        return None
    return candidate


def resolve_runtime_root() -> Path:
    configured = os.getenv(_RUNTIME_ROOT_ENV)
    if configured:
        return Path(configured).expanduser().resolve(strict=False)

    source_root = detect_source_root()
    if source_root is not None:
        return source_root

    return (Path.home() / _DEFAULT_RUNTIME_ROOT_DIRNAME).resolve(strict=False)


def resolve_runtime_script_path(script_name: str) -> Path:
    source_root = detect_source_root()
    if source_root is not None:
        candidate = source_root / "scripts" / script_name
        if candidate.exists():
            return candidate

    asset = resources.files("tts_mcp.runtime_assets").joinpath(script_name)
    return Path(str(asset))


def resolve_runtime_command_path(value: str) -> str:
    candidate = Path(value).expanduser()
    if candidate.is_absolute():
        return str(candidate)
    if len(candidate.parts) <= 1 and not value.startswith("."):
        return value
    return str((resolve_runtime_root() / candidate).resolve(strict=False))


def resolve_runtime_file_path(value: str | None) -> str | None:
    if value is None:
        return None
    candidate = Path(value).expanduser()
    if candidate.is_absolute():
        return str(candidate.resolve(strict=False))
    return str((resolve_runtime_root() / candidate).resolve(strict=False))
