from __future__ import annotations

import pytest

from tts_mcp.config import ConfigError, load_settings
from tts_mcp.platform import HostInfo
from tts_mcp.routing_policy import resolve_kokoro_request
import tts_mcp.runtime_installation as runtime_installation


def _mac_host() -> HostInfo:
    return HostInfo(
        system="Darwin",
        machine="arm64",
        is_macos_arm64=True,
        is_linux=False,
        has_nvidia=False,
    )


def _linux_host() -> HostInfo:
    return HostInfo(
        system="Linux",
        machine="x86_64",
        is_macos_arm64=False,
        is_linux=True,
        has_nvidia=True,
    )


def _mac_intel_host() -> HostInfo:
    return HostInfo(
        system="Darwin",
        machine="x86_64",
        is_macos_arm64=False,
        is_linux=False,
        has_nvidia=False,
    )


def test_prepare_startup_runtime_installs_mlx_on_macos_when_missing(monkeypatch) -> None:
    settings = load_settings({})
    monkeypatch.setattr(runtime_installation, "detect_host", lambda: _mac_host())
    monkeypatch.setattr(runtime_installation.shutil, "which", lambda *_: None)

    scripts_called: list[str] = []
    monkeypatch.setattr(
        runtime_installation,
        "_run_install_script",
        lambda path: scripts_called.append(path.name),
    )

    notes = runtime_installation.prepare_startup_runtime(settings)

    assert "install_mlx_audio_macos.sh" in scripts_called
    assert notes


def test_prepare_startup_runtime_skips_mlx_install_when_runtime_exists(monkeypatch) -> None:
    settings = load_settings({})
    monkeypatch.setattr(runtime_installation, "detect_host", lambda: _mac_host())
    monkeypatch.setattr(
        runtime_installation.shutil,
        "which",
        lambda *_: "/Users/normy/autobyteus_org/autobyteus_mcps/tts-mcp/.venv-mlx/bin/mlx_audio.tts.generate",
    )

    scripts_called: list[str] = []
    monkeypatch.setattr(
        runtime_installation,
        "_run_install_script",
        lambda path: scripts_called.append(path.name),
    )

    notes = runtime_installation.prepare_startup_runtime(settings)

    assert scripts_called == []
    assert notes == []


def test_prepare_startup_runtime_ignores_latest_enforcement_flag(monkeypatch) -> None:
    settings = load_settings({"TTS_MCP_ENFORCE_LATEST": "false"})
    monkeypatch.setattr(runtime_installation, "detect_host", lambda: _mac_host())
    monkeypatch.setattr(
        runtime_installation.shutil,
        "which",
        lambda *_: "/Users/normy/autobyteus_org/autobyteus_mcps/tts-mcp/.venv-mlx/bin/mlx_audio.tts.generate",
    )

    scripts_called: list[str] = []
    monkeypatch.setattr(
        runtime_installation,
        "_run_install_script",
        lambda path: scripts_called.append(path.name),
    )

    notes = runtime_installation.prepare_startup_runtime(settings)

    assert scripts_called == []
    assert notes == []


def test_prepare_startup_runtime_installs_kokoro_on_linux_by_default(monkeypatch) -> None:
    settings = load_settings({})
    monkeypatch.setattr(runtime_installation, "detect_host", lambda: _linux_host())
    monkeypatch.setattr(runtime_installation, "_kokoro_managed_install_required", lambda *_: True)

    scripts_called: list[str] = []
    monkeypatch.setattr(
        runtime_installation,
        "_run_install_script",
        lambda path: scripts_called.append(path.name),
    )

    notes = runtime_installation.prepare_startup_runtime(settings)

    assert "install_kokoro_onnx_linux.sh" in scripts_called
    assert notes


def test_prepare_startup_runtime_installs_kokoro_on_macos_intel_by_default(monkeypatch) -> None:
    settings = load_settings({})
    monkeypatch.setattr(runtime_installation, "detect_host", lambda: _mac_intel_host())
    monkeypatch.setattr(runtime_installation, "_kokoro_managed_install_required", lambda *_: True)

    scripts_called: list[str] = []
    monkeypatch.setattr(
        runtime_installation,
        "_run_install_script",
        lambda path: scripts_called.append(path.name),
    )

    notes = runtime_installation.prepare_startup_runtime(settings)

    assert "install_kokoro_onnx_macos.sh" in scripts_called
    assert notes


def test_prepare_startup_runtime_installs_kokoro_zh_profile_when_default_language_is_zh(
    monkeypatch,
) -> None:
    settings = load_settings({"KOKORO_TTS_DEFAULT_LANG_CODE": "zh"})
    monkeypatch.setattr(runtime_installation, "detect_host", lambda: _linux_host())
    monkeypatch.setattr(runtime_installation, "_kokoro_managed_install_required", lambda *_: True)

    profile_seen: list[str | None] = []
    monkeypatch.setattr(
        runtime_installation,
        "_run_install_script",
        lambda path: profile_seen.append(runtime_installation.os.environ.get("KOKORO_TTS_PROFILE")),
    )

    notes = runtime_installation.prepare_startup_runtime(settings)

    assert profile_seen == ["zh_v1_1"]
    assert runtime_installation.os.environ.get("KOKORO_TTS_PROFILE") is None
    assert notes


def test_prepare_startup_runtime_uses_package_only_install_for_explicit_kokoro_assets(
    monkeypatch,
) -> None:
    settings = load_settings(
        {
            "KOKORO_TTS_MODEL_PATH": ".tools/kokoro-current/kokoro-v1.0.int8.onnx",
            "KOKORO_TTS_VOICES_PATH": ".tools/kokoro-current/voices-v1.0.bin",
        }
    )
    monkeypatch.setattr(runtime_installation, "detect_host", lambda: _linux_host())
    monkeypatch.setattr(
        runtime_installation,
        "_python_module_available",
        lambda module: False if module == "kokoro_onnx" else True,
    )

    packages_installed: list[list[str]] = []
    scripts_called: list[str] = []
    monkeypatch.setattr(
        runtime_installation,
        "_install_python_packages",
        lambda packages: packages_installed.append(packages),
    )
    monkeypatch.setattr(
        runtime_installation,
        "_run_install_script",
        lambda path: scripts_called.append(path.name),
    )

    notes = runtime_installation.prepare_startup_runtime(settings)

    assert packages_installed == [["kokoro-onnx"]]
    assert scripts_called == []
    assert notes == []


def test_prepare_startup_runtime_installs_llama_on_linux_when_selected(monkeypatch) -> None:
    settings = load_settings({"TTS_MCP_LINUX_RUNTIME": "llama_cpp"})
    monkeypatch.setattr(runtime_installation, "detect_host", lambda: _linux_host())
    monkeypatch.setattr(runtime_installation.shutil, "which", lambda *_: None)

    scripts_called: list[str] = []
    monkeypatch.setattr(
        runtime_installation,
        "_run_install_script",
        lambda path: scripts_called.append(path.name),
    )

    notes = runtime_installation.prepare_startup_runtime(settings)

    assert "install_llama_tts_linux.sh" in scripts_called
    assert notes


def test_prepare_startup_runtime_skips_kokoro_install_when_ready(monkeypatch) -> None:
    settings = load_settings({"TTS_MCP_LINUX_RUNTIME": "kokoro_onnx"})
    monkeypatch.setattr(runtime_installation, "detect_host", lambda: _linux_host())
    monkeypatch.setattr(runtime_installation, "_kokoro_managed_install_required", lambda *_: False)

    scripts_called: list[str] = []
    monkeypatch.setattr(
        runtime_installation,
        "_run_install_script",
        lambda path: scripts_called.append(path.name),
    )

    notes = runtime_installation.prepare_startup_runtime(settings)

    assert scripts_called == []
    assert notes == []


def test_kokoro_assets_available_uses_zh_defaults_when_language_is_zh(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("TTS_MCP_ROOT_DIR", str(tmp_path))
    zh_dir = tmp_path / ".tools" / "kokoro-v1.1-zh"
    zh_dir.mkdir(parents=True)
    (zh_dir / "kokoro-v1.1-zh.onnx").write_bytes(b"onnx")
    (zh_dir / "voices-v1.1-zh.bin").write_bytes(b"voices")
    (zh_dir / "config.json").write_text("{}", encoding="utf-8")

    settings = load_settings({"KOKORO_TTS_DEFAULT_LANG_CODE": "zh"})
    request = resolve_kokoro_request(
        settings=settings,
        language_code=None,
        requested_voice=None,
    )
    assert runtime_installation._kokoro_assets_available(request) is True


def test_prepare_startup_runtime_disabled_noop(monkeypatch) -> None:
    settings = load_settings({"TTS_MCP_AUTO_INSTALL_RUNTIME": "false"})
    monkeypatch.setattr(runtime_installation, "detect_host", lambda: _mac_host())

    scripts_called: list[str] = []
    monkeypatch.setattr(
        runtime_installation,
        "_run_install_script",
        lambda path: scripts_called.append(path.name),
    )

    notes = runtime_installation.prepare_startup_runtime(settings)

    assert scripts_called == []
    assert notes == []


def test_prepare_startup_runtime_installs_xtts_when_selected_and_missing(monkeypatch) -> None:
    settings = load_settings({"TTS_MCP_BACKEND": "xtts"})
    monkeypatch.setattr(runtime_installation, "detect_host", lambda: _mac_host())
    monkeypatch.setattr(runtime_installation.shutil, "which", lambda *_: None)

    scripts_called: list[str] = []
    monkeypatch.setattr(
        runtime_installation,
        "_run_install_script",
        lambda path: scripts_called.append(path.name),
    )

    notes = runtime_installation.prepare_startup_runtime(settings)

    assert "install_xtts_runtime.sh" in scripts_called
    assert notes


def test_prepare_startup_runtime_installs_chatterbox_when_selected_and_missing(monkeypatch) -> None:
    settings = load_settings({"TTS_MCP_BACKEND": "chatterbox"})
    monkeypatch.setattr(runtime_installation, "detect_host", lambda: _linux_host())
    monkeypatch.setattr(runtime_installation.shutil, "which", lambda *_: None)

    scripts_called: list[str] = []
    monkeypatch.setattr(
        runtime_installation,
        "_run_install_script",
        lambda path: scripts_called.append(path.name),
    )

    notes = runtime_installation.prepare_startup_runtime(settings)

    assert "install_chatterbox_runtime.sh" in scripts_called
    assert notes


def test_ensure_request_runtime_ready_installs_missing_managed_kokoro_profile(monkeypatch) -> None:
    settings = load_settings({})
    request = resolve_kokoro_request(
        settings=settings,
        language_code="zh",
        requested_voice=None,
    )
    monkeypatch.setattr(runtime_installation, "detect_host", lambda: _linux_host())
    monkeypatch.setattr(runtime_installation, "_kokoro_managed_install_required", lambda *_: True)

    profile_seen: list[str | None] = []
    monkeypatch.setattr(
        runtime_installation,
        "_run_install_script",
        lambda path: profile_seen.append(runtime_installation.os.environ.get("KOKORO_TTS_PROFILE")),
    )

    runtime_installation.ensure_request_runtime_ready(
        settings=settings,
        backend="kokoro_onnx",
        kokoro_request=request,
    )

    assert profile_seen == ["zh_v1_1"]


def test_ensure_request_runtime_ready_explicit_assets_raise_config_when_missing(monkeypatch) -> None:
    settings = load_settings(
        {
            "KOKORO_TTS_MODEL_PATH": ".tools/custom/model.onnx",
            "KOKORO_TTS_VOICES_PATH": ".tools/custom/voices.bin",
        }
    )
    request = resolve_kokoro_request(
        settings=settings,
        language_code="zh",
        requested_voice=None,
    )
    monkeypatch.setattr(runtime_installation, "_python_module_available", lambda *_: True)

    with pytest.raises(ConfigError, match="Configured Kokoro asset file not found"):
        runtime_installation.ensure_request_runtime_ready(
            settings=settings,
            backend="kokoro_onnx",
            kokoro_request=request,
        )
