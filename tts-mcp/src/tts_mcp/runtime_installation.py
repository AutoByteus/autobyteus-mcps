from __future__ import annotations

from pathlib import Path
import os
import shutil
import subprocess
import sys

from .config import BackendName, ConfigError, TtsSettings
from .platform import HostInfo, detect_host
from .runtime_paths import resolve_runtime_root, resolve_runtime_script_path
from .routing_policy import ManagedKokoroProfile, ResolvedKokoroRequest, resolve_kokoro_request


def prepare_startup_runtime(settings: TtsSettings) -> list[str]:
    if not settings.auto_install_runtime:
        return []

    notes: list[str] = []
    root_dir = resolve_runtime_root()
    host = detect_host()

    mlx_bin_dir = root_dir / ".venv-mlx" / "bin"
    llama_bin_dir = root_dir / ".tools" / "llama-current"

    if host.is_macos_arm64 and settings.default_backend in {"auto", "mlx_audio"}:
        _prepend_path(mlx_bin_dir)
        if shutil.which(settings.mlx_command) is None:
            _run_install_script(resolve_runtime_script_path("install_mlx_audio_macos.sh"))
            _prepend_path(mlx_bin_dir)
            notes.append("Installed MLX runtime automatically.")

    if settings.default_backend == "xtts":
        if (
            shutil.which(settings.xtts_command) is None
            or not _python_command_has_module(settings.xtts_command, "TTS")
        ):
            _run_install_script(resolve_runtime_script_path("install_xtts_runtime.sh"))
            notes.append("Installed XTTS runtime automatically.")

    if settings.default_backend == "chatterbox":
        if (
            shutil.which(settings.chatterbox_command) is None
            or not _python_command_has_module(settings.chatterbox_command, "chatterbox")
        ):
            _run_install_script(resolve_runtime_script_path("install_chatterbox_runtime.sh"))
            notes.append("Installed Chatterbox runtime automatically.")

    linux_target_runtime = _linux_runtime_target(settings)

    if host.is_linux and linux_target_runtime == "llama_cpp":
        _prepend_path(llama_bin_dir)
        if shutil.which(settings.llama_command) is None:
            _run_install_script(resolve_runtime_script_path("install_llama_tts_linux.sh"))
            _prepend_path(llama_bin_dir)
            notes.append("Installed llama-tts runtime automatically.")

    if _host_supports_kokoro_install(host) and linux_target_runtime == "kokoro_onnx":
        default_request = resolve_kokoro_request(
            settings=settings,
            language_code=None,
            requested_voice=None,
        )
        if default_request.uses_explicit_assets:
            _ensure_explicit_kokoro_python_runtime(
                kokoro_request=default_request,
                auto_install_enabled=True,
            )
        elif _kokoro_managed_install_required(default_request):
            _install_managed_kokoro_profile(default_request.managed_profile, host)
            notes.append("Installed Kokoro ONNX runtime automatically.")

    if host.is_macos_arm64 and settings.auto_install_llama_on_macos:
        _prepend_path(llama_bin_dir)
        if shutil.which(settings.llama_command) is None:
            _run_install_script(resolve_runtime_script_path("install_llama_tts_macos.sh"))
            _prepend_path(llama_bin_dir)
            notes.append("Installed optional macOS llama-tts runtime automatically.")

    return notes


def ensure_request_runtime_ready(
    settings: TtsSettings,
    backend: BackendName,
    kokoro_request: ResolvedKokoroRequest | None = None,
) -> None:
    if backend != "kokoro_onnx":
        return
    if kokoro_request is None:
        raise RuntimeError("Kokoro request resolution is required before runtime readiness checks.")

    if kokoro_request.auto_install_allowed and settings.auto_install_runtime:
        host = detect_host()
        if not _host_supports_kokoro_install(host):
            raise RuntimeError(
                "kokoro_onnx auto-install currently supports Linux and Intel macOS hosts."
            )
        if _kokoro_managed_install_required(kokoro_request):
            _install_managed_kokoro_profile(kokoro_request.managed_profile, host)
        return

    _ensure_explicit_kokoro_python_runtime(
        kokoro_request=kokoro_request,
        auto_install_enabled=settings.auto_install_runtime and kokoro_request.uses_explicit_assets,
    )
    _validate_kokoro_assets_present(kokoro_request)


def _linux_runtime_target(settings: TtsSettings) -> str | None:
    if settings.default_backend == "llama_cpp":
        return "llama_cpp"
    if settings.default_backend == "kokoro_onnx":
        return "kokoro_onnx"
    if settings.default_backend == "auto":
        return settings.linux_runtime
    return None


def _host_supports_kokoro_install(host: HostInfo) -> bool:
    return host.is_linux or _is_macos_intel(host.system, host.machine)


def _is_macos_intel(system: str, machine: str) -> bool:
    return system.lower() == "darwin" and machine in {"x86_64", "amd64"}


def _kokoro_managed_install_required(kokoro_request: ResolvedKokoroRequest) -> bool:
    if kokoro_request.managed_profile is None:
        return False
    if not _python_module_available("kokoro_onnx"):
        return True
    if kokoro_request.use_misaki_zh and not _python_module_available("misaki"):
        return True
    return not _kokoro_assets_available(kokoro_request)


def _ensure_explicit_kokoro_python_runtime(
    *,
    kokoro_request: ResolvedKokoroRequest,
    auto_install_enabled: bool,
) -> None:
    if not _python_module_available("kokoro_onnx"):
        if not auto_install_enabled:
            raise RuntimeError(
                "kokoro-onnx package is not installed. Install with: pip install --upgrade kokoro-onnx"
            )
        _install_python_packages(["kokoro-onnx"])

    if kokoro_request.use_misaki_zh and not _python_module_available("misaki"):
        if not auto_install_enabled:
            raise RuntimeError(
                "misaki-fork[zh] package is not installed for Kokoro Chinese phonemization. "
                "Install with: pip install --upgrade 'misaki-fork[zh]'"
            )
        _install_python_packages(["misaki-fork[zh]"])


def _validate_kokoro_assets_present(kokoro_request: ResolvedKokoroRequest) -> None:
    missing_paths: list[str] = []
    for maybe_path in (
        kokoro_request.model_path,
        kokoro_request.voices_path,
        kokoro_request.vocab_config_path,
    ):
        if maybe_path and not Path(maybe_path).exists():
            missing_paths.append(maybe_path)

    if not missing_paths:
        return

    joined = ", ".join(missing_paths)
    if kokoro_request.uses_explicit_assets:
        raise ConfigError(f"Configured Kokoro asset file not found: {joined}")

    profile = kokoro_request.managed_profile or "the requested managed profile"
    raise RuntimeError(
        f"Kokoro assets are missing for managed profile {profile}: {joined}. "
        "Enable TTS_MCP_AUTO_INSTALL_RUNTIME=true or run the Kokoro installer script."
    )


def _install_managed_kokoro_profile(
    profile: ManagedKokoroProfile | None,
    host: HostInfo,
) -> None:
    if profile is None:
        raise RuntimeError("Managed Kokoro install requested without a managed profile.")

    script_name = (
        "install_kokoro_onnx_linux.sh"
        if host.is_linux
        else "install_kokoro_onnx_macos.sh"
    )
    _run_install_script_with_env(
        resolve_runtime_script_path(script_name),
        {"KOKORO_TTS_PROFILE": profile},
    )


def _kokoro_assets_available(kokoro_request: ResolvedKokoroRequest) -> bool:
    model_path = Path(kokoro_request.model_path)
    voices_path = Path(kokoro_request.voices_path)
    if not (model_path.exists() and voices_path.exists()):
        return False

    if kokoro_request.vocab_config_path:
        vocab_config_path = Path(kokoro_request.vocab_config_path)
        return vocab_config_path.exists()

    return True


def _python_module_available(module_name: str) -> bool:
    completed = subprocess.run(
        [sys.executable, "-c", f"import {module_name}"],
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.returncode == 0


def _python_command_has_module(command: str, module_name: str) -> bool:
    completed = subprocess.run(
        [command, "-c", f"import {module_name}"],
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.returncode == 0


def _install_python_packages(packages: list[str]) -> None:
    env = os.environ.copy()
    env.setdefault("PYTHON_BIN", sys.executable)
    env.setdefault("TTS_MCP_ROOT_DIR", str(resolve_runtime_root()))

    if not _python_command_has_module(sys.executable, "pip"):
        subprocess.run(
            [sys.executable, "-m", "ensurepip", "--upgrade"],
            capture_output=True,
            text=True,
            check=True,
            env=env,
        )

    _run_python_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"], env)
    _run_python_command([sys.executable, "-m", "pip", "install", "--upgrade", *packages], env)


def _prepend_path(directory: Path) -> None:
    path_value = str(directory)
    current_path = os.environ.get("PATH", "")
    entries = current_path.split(":") if current_path else []
    if path_value in entries:
        return
    os.environ["PATH"] = f"{path_value}:{current_path}" if current_path else path_value


def _run_install_script(script_path: Path) -> None:
    if not script_path.exists():
        raise RuntimeError(f"Missing installer script: {script_path}")

    env = os.environ.copy()
    env.setdefault("PYTHON_BIN", sys.executable)
    env.setdefault("TTS_MCP_ROOT_DIR", str(resolve_runtime_root()))
    _run_python_command([str(script_path)], env)


def _run_install_script_with_env(script_path: Path, extra_env: dict[str, str]) -> None:
    previous: dict[str, str | None] = {
        key: os.environ.get(key)
        for key in extra_env
    }
    os.environ.update(extra_env)
    try:
        _run_install_script(script_path)
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _run_python_command(command: list[str], env: dict[str, str]) -> None:
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    if completed.returncode == 0:
        return

    output = "\n".join(
        [
            part.strip()
            for part in (completed.stdout, completed.stderr)
            if part and part.strip()
        ]
    )
    raise RuntimeError(
        f"Runtime auto-install failed via {' '.join(command)} (exit {completed.returncode}). {output}"
    )
