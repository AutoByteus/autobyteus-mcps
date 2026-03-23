from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import types

import pytest

from tts_mcp.config import load_settings
from tts_mcp.platform import BackendSelection, HostInfo
import tts_mcp.backend_contracts as backend_contracts
import tts_mcp.execution_support as execution_support
import tts_mcp.kokoro_runtime as kokoro_runtime
import tts_mcp.runner as runner


_MIN_VALID_WAV_BYTES = b"RIFF" + (b"\x00" * 60)


@pytest.fixture(autouse=True)
def _mock_runtime_version_check(monkeypatch) -> None:
    monkeypatch.setattr(
        runner,
        "check_backend_runtime_version",
        lambda **_: {
            "status": "latest",
            "local_version": "1.0.0",
            "latest_version": "1.0.0",
            "message": "runtime is up to date",
        },
    )


def _mlx_host() -> HostInfo:
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


class _FakeNumpyArray:
    def __init__(self, values: list[float]) -> None:
        self._values = values

    def __mul__(self, factor: float) -> "_FakeNumpyArray":
        return _FakeNumpyArray([value * factor for value in self._values])

    __rmul__ = __mul__

    def astype(self, _dtype) -> "_FakeNumpyArray":
        return self

    def tobytes(self) -> bytes:
        return b"\x00\x00" * len(self._values)


def _install_fake_numpy(monkeypatch) -> None:
    fake_numpy = types.SimpleNamespace(
        float32="float32",
        int16="int16",
        asarray=lambda values, dtype=None: _FakeNumpyArray(list(values)),
        clip=lambda values, _lo, _hi: values,
    )
    monkeypatch.setitem(sys.modules, "numpy", fake_numpy)


def test_run_speak_mlx_success(monkeypatch, tmp_path: Path) -> None:
    settings = load_settings({"TTS_MCP_OUTPUT_DIR": str(tmp_path)})

    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="mlx_audio", command=settings.mlx_command, host=_mlx_host()),
    )

    output_file = tmp_path / "mlx.wav"

    def fake_run(command, **kwargs):
        assert command[0] == settings.mlx_command
        assert "--model" in command
        assert command[command.index("--lang_code") + 1] == "a"
        prefix = command[command.index("--file_prefix") + 1]
        Path(f"{prefix}.wav").write_bytes(_MIN_VALID_WAV_BYTES)
        return subprocess.CompletedProcess(command, 0, "ok", "")

    monkeypatch.setattr(execution_support.subprocess, "run", fake_run)

    result = runner.run_speak(
        settings=settings,
        text="Hello from MLX",
        output_path=str(output_file),
        play=False,
    )

    assert result["ok"] is True
    assert result["backend"] == "mlx_audio"
    assert result["output_path"] == str(output_file)
    assert result["warnings"] == []


def test_run_speak_mlx_german_auto_selects_german_model_and_language(monkeypatch, tmp_path: Path) -> None:
    settings = load_settings(
        {
            "TTS_MCP_OUTPUT_DIR": str(tmp_path),
            "MLX_TTS_DEFAULT_LANG_CODE": "de-DE",
        }
    )

    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="mlx_audio", command=settings.mlx_command, host=_mlx_host()),
    )

    output_file = tmp_path / "mlx_de.wav"

    def fake_run(command, **kwargs):
        assert command[0] == settings.mlx_command
        assert command[command.index("--model") + 1] == "mlx-community/3b-de-ft-research_release-bf16"
        assert command[command.index("--lang_code") + 1] == "de"
        prefix = command[command.index("--file_prefix") + 1]
        Path(f"{prefix}.wav").write_bytes(_MIN_VALID_WAV_BYTES)
        return subprocess.CompletedProcess(command, 0, "ok", "")

    monkeypatch.setattr(execution_support.subprocess, "run", fake_run)

    result = runner.run_speak(
        settings=settings,
        text="Hallo aus MLX",
        output_path=str(output_file),
        play=False,
    )

    assert result["ok"] is True
    assert result["backend"] == "mlx_audio"


def test_run_speak_returns_busy_when_global_lock_not_available(monkeypatch, tmp_path: Path) -> None:
    settings = load_settings({"TTS_MCP_OUTPUT_DIR": str(tmp_path)})

    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="mlx_audio", command=settings.mlx_command, host=_mlx_host()),
    )
    monkeypatch.setattr(execution_support, "acquire_global_generation_lock", lambda **_: None)

    result = runner.run_speak(
        settings=settings,
        text="Hello from MLX",
        output_path=str(tmp_path / "busy.wav"),
        play=False,
    )

    assert result["ok"] is False
    assert result["error_type"] == "busy"


def test_run_speak_deletes_auto_output_by_default(monkeypatch, tmp_path: Path) -> None:
    settings = load_settings({"TTS_MCP_OUTPUT_DIR": str(tmp_path)})

    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="mlx_audio", command=settings.mlx_command, host=_mlx_host()),
    )

    def fake_run(command, **kwargs):
        prefix = command[command.index("--file_prefix") + 1]
        Path(f"{prefix}.wav").write_bytes(_MIN_VALID_WAV_BYTES)
        return subprocess.CompletedProcess(command, 0, "ok", "")

    monkeypatch.setattr(execution_support.subprocess, "run", fake_run)

    result = runner.run_speak(
        settings=settings,
        text="Hello from MLX",
        play=False,
    )

    assert result["ok"] is True
    assert result["output_path"] is not None
    assert not Path(result["output_path"]).exists()


def test_run_speak_keeps_explicit_output_path(monkeypatch, tmp_path: Path) -> None:
    settings = load_settings({"TTS_MCP_OUTPUT_DIR": str(tmp_path)})

    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="mlx_audio", command=settings.mlx_command, host=_mlx_host()),
    )

    output_file = tmp_path / "explicit.wav"

    def fake_run(command, **kwargs):
        prefix = command[command.index("--file_prefix") + 1]
        Path(f"{prefix}.wav").write_bytes(_MIN_VALID_WAV_BYTES)
        return subprocess.CompletedProcess(command, 0, "ok", "")

    monkeypatch.setattr(execution_support.subprocess, "run", fake_run)

    result = runner.run_speak(
        settings=settings,
        text="Hello from MLX",
        output_path=str(output_file),
        play=False,
    )

    assert result["ok"] is True
    assert output_file.exists()


def test_run_speak_keeps_auto_output_when_cleanup_disabled(monkeypatch, tmp_path: Path) -> None:
    settings = load_settings(
        {
            "TTS_MCP_OUTPUT_DIR": str(tmp_path),
            "TTS_MCP_DELETE_AUTO_OUTPUT": "false",
        }
    )

    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="mlx_audio", command=settings.mlx_command, host=_mlx_host()),
    )

    def fake_run(command, **kwargs):
        prefix = command[command.index("--file_prefix") + 1]
        Path(f"{prefix}.wav").write_bytes(_MIN_VALID_WAV_BYTES)
        return subprocess.CompletedProcess(command, 0, "ok", "")

    monkeypatch.setattr(execution_support.subprocess, "run", fake_run)

    result = runner.run_speak(
        settings=settings,
        text="Hello from MLX",
        play=False,
    )

    assert result["ok"] is True
    assert result["output_path"] is not None
    assert Path(result["output_path"]).exists()


def test_resolve_mlx_subprocess_env_forced_offline_true() -> None:
    settings = load_settings({"TTS_MCP_HF_HUB_OFFLINE_MODE": "true"})
    assert backend_contracts.resolve_mlx_subprocess_env(settings) == {"HF_HUB_OFFLINE": "1"}


def test_resolve_mlx_subprocess_env_forced_offline_false() -> None:
    settings = load_settings({"TTS_MCP_HF_HUB_OFFLINE_MODE": "false"})
    assert backend_contracts.resolve_mlx_subprocess_env(settings) is None


def test_resolve_mlx_subprocess_env_auto_uses_cache(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    cache_dir = (
        tmp_path
        / ".cache"
        / "huggingface"
        / "hub"
        / "models--mlx-community--Kokoro-82M-bf16"
        / "snapshots"
        / "1234"
    )
    cache_dir.mkdir(parents=True, exist_ok=True)
    backend_contracts.is_hf_model_cached.cache_clear()

    settings = load_settings({"TTS_MCP_HF_HUB_OFFLINE_MODE": "auto"})
    assert backend_contracts.resolve_mlx_subprocess_env(settings) == {"HF_HUB_OFFLINE": "1"}
    backend_contracts.is_hf_model_cached.cache_clear()


def test_resolve_mlx_language_code_maps_common_german_aliases() -> None:
    assert backend_contracts.resolve_mlx_language_code(
        "mlx-community/3b-de-ft-research_release-bf16",
        "de-DE",
        "en",
    ) == "de"
    assert backend_contracts.resolve_mlx_language_code(
        "mlx-community/3b-de-ft-research_release-bf16",
        "deutsch",
        "en",
    ) == "de"


def test_resolve_mlx_subprocess_env_auto_without_cache(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    backend_contracts.is_hf_model_cached.cache_clear()

    settings = load_settings({"TTS_MCP_HF_HUB_OFFLINE_MODE": "auto"})
    assert backend_contracts.resolve_mlx_subprocess_env(settings) is None
    backend_contracts.is_hf_model_cached.cache_clear()


def test_run_speak_mlx_marks_played_only_when_confirmed(monkeypatch, tmp_path: Path) -> None:
    settings = load_settings({"TTS_MCP_OUTPUT_DIR": str(tmp_path)})

    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="mlx_audio", command=settings.mlx_command, host=_mlx_host()),
    )

    output_file = tmp_path / "mlx_play.wav"

    def fake_run(command, **kwargs):
        prefix = command[command.index("--file_prefix") + 1]
        Path(f"{prefix}.wav").write_bytes(_MIN_VALID_WAV_BYTES)
        return subprocess.CompletedProcess(command, 0, "Starting audio stream...", "")

    monkeypatch.setattr(execution_support.subprocess, "run", fake_run)

    result = runner.run_speak(
        settings=settings,
        text="Hello from MLX",
        output_path=str(output_file),
        play=True,
    )

    assert result["ok"] is True
    assert result["played"] is True
    assert result["warnings"] == []


def test_run_speak_mlx_warns_when_playback_not_confirmed(monkeypatch, tmp_path: Path) -> None:
    settings = load_settings({"TTS_MCP_OUTPUT_DIR": str(tmp_path)})

    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="mlx_audio", command=settings.mlx_command, host=_mlx_host()),
    )

    output_file = tmp_path / "mlx_no_play_marker.wav"

    def fake_run(command, **kwargs):
        prefix = command[command.index("--file_prefix") + 1]
        Path(f"{prefix}.wav").write_bytes(_MIN_VALID_WAV_BYTES)
        return subprocess.CompletedProcess(command, 0, "ok", "")

    monkeypatch.setattr(execution_support.subprocess, "run", fake_run)

    result = runner.run_speak(
        settings=settings,
        text="Hello from MLX",
        output_path=str(output_file),
        play=True,
    )

    assert result["ok"] is True
    assert result["played"] is False
    assert result["warnings"]


def test_run_speak_requires_instruct_for_voicedesign(monkeypatch) -> None:
    settings = load_settings(
        {"TTS_MCP_MLX_MODEL_PRESET": "qwen_voicedesign_hq", "MLX_TTS_MODEL": "mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16"}
    )
    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="mlx_audio", command=settings.mlx_command, host=_mlx_host()),
    )

    result = runner.run_speak(
        settings=settings,
        text="Hello",
        instruct=None,
    )

    assert result["ok"] is False
    assert result["error_type"] == "validation"


def test_run_speak_uses_default_instruct_for_voicedesign(monkeypatch, tmp_path: Path) -> None:
    settings = load_settings(
        {
            "TTS_MCP_OUTPUT_DIR": str(tmp_path),
            "TTS_MCP_MLX_MODEL_PRESET": "qwen_voicedesign_hq",
            "MLX_TTS_MODEL": "mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16",
            "MLX_TTS_DEFAULT_INSTRUCT": "A warm calm narrator voice",
        }
    )
    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="mlx_audio", command=settings.mlx_command, host=_mlx_host()),
    )

    output_file = tmp_path / "vd.wav"

    def fake_run(command, **kwargs):
        if command[1:] == ["-h"]:
            return subprocess.CompletedProcess(command, 0, "--instruct", "")
        assert "--instruct" in command
        prefix = command[command.index("--file_prefix") + 1]
        Path(f"{prefix}.wav").write_bytes(_MIN_VALID_WAV_BYTES)
        return subprocess.CompletedProcess(command, 0, "ok", "")

    monkeypatch.setattr(execution_support.subprocess, "run", fake_run)

    result = runner.run_speak(
        settings=settings,
        text="Hello",
        output_path=str(output_file),
        play=False,
    )

    assert result["ok"] is True


def test_run_speak_llama_playback_warning_when_no_player(monkeypatch, tmp_path: Path) -> None:
    settings = load_settings({"TTS_MCP_OUTPUT_DIR": str(tmp_path)})

    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="llama_cpp", command=settings.llama_command, host=_linux_host()),
    )
    monkeypatch.setattr(execution_support, "build_linux_play_command", lambda **_: None)

    output_file = tmp_path / "llama.wav"

    def fake_run(command, **kwargs):
        assert command[0] == settings.llama_command
        output_file.write_bytes(_MIN_VALID_WAV_BYTES)
        return subprocess.CompletedProcess(command, 0, "done", "")

    monkeypatch.setattr(execution_support.subprocess, "run", fake_run)

    result = runner.run_speak(
        settings=settings,
        text="Hello from llama",
        output_path=str(output_file),
        play=True,
    )

    assert result["ok"] is True
    assert result["backend"] == "llama_cpp"
    assert result["played"] is False
    assert result["warnings"]


def test_run_speak_llama_treats_ffplay_stderr_failure_as_not_played(
    monkeypatch,
    tmp_path: Path,
) -> None:
    settings = load_settings({"TTS_MCP_OUTPUT_DIR": str(tmp_path)})
    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="llama_cpp", command=settings.llama_command, host=_linux_host()),
    )

    output_file = tmp_path / "llama_ffplay_false_positive.wav"
    playback_command = ["ffplay", "-nodisp", "-autoexit", str(output_file)]
    monkeypatch.setattr(execution_support, "build_linux_play_command", lambda **_: playback_command)

    def fake_run(command, **kwargs):
        if command[0] == settings.llama_command:
            output_file.write_bytes(_MIN_VALID_WAV_BYTES)
            return subprocess.CompletedProcess(command, 0, "done", "")
        if command[0] == "ffplay":
            return subprocess.CompletedProcess(
                command,
                0,
                "",
                "audio open failed\nFailed to open file",
            )
        raise AssertionError(f"Unexpected command: {command}")

    monkeypatch.setattr(execution_support.subprocess, "run", fake_run)

    result = runner.run_speak(
        settings=settings,
        text="Hello from llama",
        output_path=str(output_file),
        play=True,
    )

    assert result["ok"] is True
    assert result["played"] is False
    assert result["warnings"]


def test_run_speak_llama_accepts_ffplay_success_without_failure_markers(
    monkeypatch,
    tmp_path: Path,
) -> None:
    settings = load_settings({"TTS_MCP_OUTPUT_DIR": str(tmp_path)})
    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="llama_cpp", command=settings.llama_command, host=_linux_host()),
    )

    output_file = tmp_path / "llama_ffplay_ok.wav"
    playback_command = ["ffplay", "-nodisp", "-autoexit", str(output_file)]
    monkeypatch.setattr(execution_support, "build_linux_play_command", lambda **_: playback_command)

    def fake_run(command, **kwargs):
        if command[0] == settings.llama_command:
            output_file.write_bytes(_MIN_VALID_WAV_BYTES)
            return subprocess.CompletedProcess(command, 0, "done", "")
        if command[0] == "ffplay":
            return subprocess.CompletedProcess(command, 0, "", "")
        raise AssertionError(f"Unexpected command: {command}")

    monkeypatch.setattr(execution_support.subprocess, "run", fake_run)

    result = runner.run_speak(
        settings=settings,
        text="Hello from llama",
        output_path=str(output_file),
        play=True,
    )

    assert result["ok"] is True
    assert result["played"] is True
    assert result["warnings"] == []


def test_run_speak_rejects_instruct_on_llama(monkeypatch) -> None:
    settings = load_settings({})
    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="llama_cpp", command=settings.llama_command, host=_linux_host()),
    )

    result = runner.run_speak(
        settings=settings,
        text="Hello",
        instruct="style",
    )

    assert result["ok"] is False
    assert result["error_type"] == "validation"


def test_run_speak_kokoro_success(monkeypatch, tmp_path: Path) -> None:
    settings = load_settings({"TTS_MCP_OUTPUT_DIR": str(tmp_path)})
    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="kokoro_onnx", command="kokoro_onnx", host=_linux_host()),
    )

    output_file = tmp_path / "kokoro.wav"

    def fake_kokoro(**kwargs):
        output_file.write_bytes(_MIN_VALID_WAV_BYTES)
        return {
            "stdout": "kokoro generated",
            "stderr": None,
            "exit_code": 0,
            "error_type": None,
            "error_message": None,
        }

    monkeypatch.setattr(kokoro_runtime, "run_kokoro_generation", fake_kokoro)

    result = runner.run_speak(
        settings=settings,
        text="Hello from Kokoro",
        output_path=str(output_file),
        play=False,
    )

    assert result["ok"] is True
    assert result["backend"] == "kokoro_onnx"
    assert output_file.exists()


def test_run_speak_kokoro_missing_dependency(monkeypatch, tmp_path: Path) -> None:
    settings = load_settings({"TTS_MCP_OUTPUT_DIR": str(tmp_path)})
    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="kokoro_onnx", command="kokoro_onnx", host=_linux_host()),
    )
    monkeypatch.setattr(
        kokoro_runtime,
        "run_kokoro_generation",
        lambda **_: {
            "stdout": None,
            "stderr": None,
            "exit_code": None,
            "error_type": "dependency",
            "error_message": "kokoro-onnx package is not installed.",
        },
    )

    result = runner.run_speak(
        settings=settings,
        text="Hello",
        output_path=str(tmp_path / "kokoro_dep.wav"),
        play=False,
    )

    assert result["ok"] is False
    assert result["error_type"] == "dependency"


def test_run_speak_rejects_empty_text() -> None:
    settings = load_settings({})
    result = runner.run_speak(settings=settings, text="   ")

    assert result["ok"] is False
    assert result["error_type"] == "validation"


def test_run_speak_rejects_non_wav_output_path(monkeypatch, tmp_path: Path) -> None:
    settings = load_settings({})
    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="mlx_audio", command=settings.mlx_command, host=_mlx_host()),
    )

    result = runner.run_speak(
        settings=settings,
        text="hello",
        output_path=str(tmp_path / "audio.mp3"),
    )

    assert result["ok"] is False
    assert result["error_type"] == "validation"


def test_run_speak_fails_if_existing_output_file_not_updated(monkeypatch, tmp_path: Path) -> None:
    settings = load_settings({"TTS_MCP_OUTPUT_DIR": str(tmp_path)})
    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="mlx_audio", command=settings.mlx_command, host=_mlx_host()),
    )

    output_file = tmp_path / "stale.wav"
    output_file.write_bytes(_MIN_VALID_WAV_BYTES)

    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, "ok", "")

    monkeypatch.setattr(execution_support.subprocess, "run", fake_run)

    result = runner.run_speak(
        settings=settings,
        text="hello",
        output_path=str(output_file),
        play=False,
    )

    assert result["ok"] is False
    assert result["error_type"] == "execution"


def test_run_speak_blocks_outdated_runtime_when_enforced(monkeypatch) -> None:
    settings = load_settings({})
    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="mlx_audio", command=settings.mlx_command, host=_mlx_host()),
    )
    monkeypatch.setattr(
        runner,
        "check_backend_runtime_version",
        lambda **_: {
            "status": "outdated",
            "local_version": "0.2.10",
            "latest_version": "0.3.1",
            "message": "mlx-audio is outdated",
        },
    )

    result = runner.run_speak(settings=settings, text="hello")

    assert result["ok"] is False
    assert result["error_type"] == "dependency"


def test_run_speak_allows_outdated_runtime_when_not_enforced(monkeypatch, tmp_path: Path) -> None:
    settings = load_settings(
        {
            "TTS_MCP_ENFORCE_LATEST": "false",
            "TTS_MCP_OUTPUT_DIR": str(tmp_path),
        }
    )
    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="mlx_audio", command=settings.mlx_command, host=_mlx_host()),
    )
    version_check_calls: list[str] = []

    monkeypatch.setattr(
        runner,
        "check_backend_runtime_version",
        lambda **_: version_check_calls.append("called"),
    )

    output_file = tmp_path / "outdated_but_allowed.wav"

    def fake_run(command, **kwargs):
        prefix = command[command.index("--file_prefix") + 1]
        Path(f"{prefix}.wav").write_bytes(_MIN_VALID_WAV_BYTES)
        return subprocess.CompletedProcess(command, 0, "ok", "")

    monkeypatch.setattr(execution_support.subprocess, "run", fake_run)

    result = runner.run_speak(
        settings=settings,
        text="hello",
        output_path=str(output_file),
        play=False,
    )

    assert result["ok"] is True
    assert version_check_calls == []
    assert result["warnings"] == []


def test_run_speak_blocks_when_runtime_freshness_is_unknown_and_enforced(monkeypatch) -> None:
    settings = load_settings({})
    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="mlx_audio", command=settings.mlx_command, host=_mlx_host()),
    )
    monkeypatch.setattr(
        runner,
        "check_backend_runtime_version",
        lambda **_: {
            "status": "unknown",
            "local_version": None,
            "latest_version": "0.3.1",
            "message": "Could not fetch latest mlx-audio version from PyPI.",
        },
    )

    result = runner.run_speak(settings=settings, text="hello")

    assert result["ok"] is False
    assert result["error_type"] == "dependency"


def test_resolve_kokoro_language_code_maps_common_chinese_aliases() -> None:
    assert backend_contracts.resolve_kokoro_language_code("zh", "en-us") == "cmn"
    assert backend_contracts.resolve_kokoro_language_code("zh-cn", "en-us") == "cmn"
    assert backend_contracts.resolve_kokoro_language_code("zh_hans", "en-us") == "cmn"
    assert backend_contracts.resolve_kokoro_language_code("mandarin", "en-us") == "cmn"


def test_resolve_kokoro_language_code_keeps_supported_values() -> None:
    assert backend_contracts.resolve_kokoro_language_code(None, "cmn") == "cmn"
    assert backend_contracts.resolve_kokoro_language_code("en-us", "cmn") == "en-us"


def test_resolve_kokoro_runtime_config_auto_switches_to_zh_profile() -> None:
    settings = load_settings({"KOKORO_TTS_DEFAULT_LANG_CODE": "zh"})

    resolved = kokoro_runtime.resolve_kokoro_runtime_config(
        settings=settings,
        selected_language="cmn",
        requested_voice=None,
    )

    assert resolved["model_path"].endswith("kokoro-v1.1-zh.onnx")
    assert resolved["voices_path"].endswith("voices-v1.1-zh.bin")
    assert resolved["vocab_config_path"] and resolved["vocab_config_path"].endswith("config.json")
    assert resolved["selected_voice"] == "zf_001"


def test_resolve_kokoro_runtime_config_keeps_custom_default_voice_for_zh() -> None:
    settings = load_settings(
        {
            "KOKORO_TTS_DEFAULT_LANG_CODE": "zh",
            "KOKORO_TTS_DEFAULT_VOICE": "zf_008",
        }
    )

    resolved = kokoro_runtime.resolve_kokoro_runtime_config(
        settings=settings,
        selected_language="cmn",
        requested_voice=None,
    )

    assert resolved["selected_voice"] == "zf_008"


def test_run_kokoro_onnx_uses_misaki_when_vocab_configured(monkeypatch, tmp_path: Path) -> None:
    _install_fake_numpy(monkeypatch)
    settings = load_settings(
        {
            "KOKORO_TTS_VOCAB_CONFIG_PATH": str(tmp_path / "config.json"),
            "KOKORO_TTS_DEFAULT_LANG_CODE": "cmn",
            "KOKORO_TTS_DEFAULT_VOICE": "zf_001",
        }
    )
    (tmp_path / "config.json").write_text("{}", encoding="utf-8")

    captured: dict[str, object] = {}

    class _FakeKokoro:
        def create(self, **kwargs):
            captured.update(kwargs)
            return [0.0] * 24000, 24000

    monkeypatch.setattr(kokoro_runtime, "load_kokoro_runtime", lambda **_: _FakeKokoro())
    monkeypatch.setattr(
        kokoro_runtime,
        "load_misaki_zh_g2p",
        lambda **_: (lambda text: ("pʰ o n e m e s", None)),
    )

    result = kokoro_runtime.run_kokoro_generation(
        settings=settings,
        text="你好",
        output_path=tmp_path / "misaki.wav",
        voice=None,
        speed=1.0,
        language_code="cmn",
    )

    assert result["exit_code"] == 0
    assert captured["text"] == "pʰ o n e m e s"
    assert captured["is_phonemes"] is True
    assert captured["voice"] == "zf_001"


def test_run_kokoro_onnx_auto_uses_zh_defaults_from_language(monkeypatch, tmp_path: Path) -> None:
    _install_fake_numpy(monkeypatch)
    settings = load_settings({"KOKORO_TTS_DEFAULT_LANG_CODE": "zh"})
    captured: dict[str, object] = {}
    loader_inputs: dict[str, str | None] = {}

    class _FakeKokoro:
        def create(self, **kwargs):
            captured.update(kwargs)
            return [0.0] * 24000, 24000

    def fake_loader(**kwargs):
        loader_inputs["model_path"] = str(kwargs["model_path"])
        loader_inputs["voices_path"] = str(kwargs["voices_path"])
        vocab = kwargs.get("vocab_config_path")
        loader_inputs["vocab_config_path"] = str(vocab) if vocab is not None else None
        return _FakeKokoro()

    monkeypatch.setattr(kokoro_runtime, "load_kokoro_runtime", fake_loader)
    monkeypatch.setattr(
        kokoro_runtime,
        "load_misaki_zh_g2p",
        lambda **_: (lambda text: ("pʰ o n e m e s", None)),
    )

    result = kokoro_runtime.run_kokoro_generation(
        settings=settings,
        text="你好",
        output_path=tmp_path / "auto_zh.wav",
        voice=None,
        speed=1.0,
        language_code=None,
    )

    assert result["exit_code"] == 0
    assert loader_inputs["model_path"] and "kokoro-v1.1-zh.onnx" in loader_inputs["model_path"]
    assert loader_inputs["voices_path"] and "voices-v1.1-zh.bin" in loader_inputs["voices_path"]
    assert loader_inputs["vocab_config_path"] and "config.json" in loader_inputs["vocab_config_path"]
    assert captured["voice"] == "zf_001"
    assert captured["is_phonemes"] is True


def test_run_kokoro_onnx_returns_dependency_error_when_misaki_missing(
    monkeypatch,
    tmp_path: Path,
) -> None:
    _install_fake_numpy(monkeypatch)
    settings = load_settings(
        {
            "KOKORO_TTS_VOCAB_CONFIG_PATH": str(tmp_path / "config.json"),
            "KOKORO_TTS_DEFAULT_LANG_CODE": "cmn",
            "KOKORO_TTS_DEFAULT_VOICE": "zf_001",
        }
    )
    (tmp_path / "config.json").write_text("{}", encoding="utf-8")

    class _FakeKokoro:
        def create(self, **kwargs):
            return [0.0] * 24000, 24000

    monkeypatch.setattr(kokoro_runtime, "load_kokoro_runtime", lambda **_: _FakeKokoro())
    monkeypatch.setattr(
        kokoro_runtime,
        "load_misaki_zh_g2p",
        lambda **_: (_ for _ in ()).throw(RuntimeError("misaki missing")),
    )

    result = kokoro_runtime.run_kokoro_generation(
        settings=settings,
        text="你好",
        output_path=tmp_path / "misaki_missing.wav",
        voice=None,
        speed=1.0,
        language_code="cmn",
    )

    assert result["exit_code"] is None
    assert result["error_type"] == "dependency"
    assert "misaki missing" in (result["error_message"] or "")


def test_run_speak_xtts_success(monkeypatch, tmp_path: Path) -> None:
    settings = load_settings(
        {
            "TTS_MCP_OUTPUT_DIR": str(tmp_path),
            "XTTS_DEFAULT_LANGUAGE_CODE": "de-DE",
            "XTTS_DEFAULT_SPEAKER_WAV": str(tmp_path / "speaker.wav"),
        }
    )
    (tmp_path / "speaker.wav").write_bytes(b"fake")

    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="xtts", command=settings.xtts_command, host=_linux_host()),
    )

    output_file = tmp_path / "xtts.wav"

    def fake_run(command, **kwargs):
        assert command[0] == settings.xtts_command
        assert Path(command[1]).name == "xtts_generate.py"
        assert command[command.index("--language") + 1] == "de"
        assert command[command.index("--speaker-wav") + 1] == str(tmp_path / "speaker.wav")
        output_file.write_bytes(_MIN_VALID_WAV_BYTES)
        return subprocess.CompletedProcess(command, 0, "done", "")

    monkeypatch.setattr(execution_support.subprocess, "run", fake_run)

    result = runner.run_speak(
        settings=settings,
        text="Hallo aus XTTS",
        output_path=str(output_file),
        play=False,
    )

    assert result["ok"] is True
    assert result["backend"] == "xtts"


def test_run_speak_xtts_passes_coqui_tos_env_when_configured(monkeypatch, tmp_path: Path) -> None:
    settings = load_settings(
        {
            "TTS_MCP_OUTPUT_DIR": str(tmp_path),
            "XTTS_COQUI_TOS_AGREED": "true",
            "XTTS_DEFAULT_SPEAKER_WAV": str(tmp_path / "speaker.wav"),
        }
    )
    (tmp_path / "speaker.wav").write_bytes(b"fake")
    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="xtts", command=settings.xtts_command, host=_linux_host()),
    )

    output_file = tmp_path / "xtts_tos.wav"

    def fake_run(command, **kwargs):
        assert kwargs["env"]["COQUI_TOS_AGREED"] == "1"
        output_file.write_bytes(_MIN_VALID_WAV_BYTES)
        return subprocess.CompletedProcess(command, 0, "done", "")

    monkeypatch.setattr(execution_support.subprocess, "run", fake_run)

    result = runner.run_speak(
        settings=settings,
        text="Hallo aus XTTS",
        output_path=str(output_file),
        play=False,
    )

    assert result["ok"] is True


def test_run_speak_xtts_reports_terms_acceptance_requirement(monkeypatch, tmp_path: Path) -> None:
    settings = load_settings(
        {
            "TTS_MCP_OUTPUT_DIR": str(tmp_path),
            "XTTS_DEFAULT_SPEAKER_WAV": str(tmp_path / "speaker.wav"),
        }
    )
    (tmp_path / "speaker.wav").write_bytes(b"fake")
    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="xtts", command=settings.xtts_command, host=_linux_host()),
    )

    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(
            command,
            1,
            ' > You must confirm the following:\n | > "Otherwise, I agree to the terms of the non-commercial CPML: https://coqui.ai/cpml" - [y/n]',
            "",
        )

    monkeypatch.setattr(execution_support.subprocess, "run", fake_run)

    result = runner.run_speak(
        settings=settings,
        text="Hallo aus XTTS",
        output_path=str(tmp_path / "xtts_terms.wav"),
        play=False,
    )

    assert result["ok"] is False
    assert result["error_type"] == "validation"
    assert "XTTS_COQUI_TOS_AGREED=true" in (result["error_message"] or "")


def test_run_speak_xtts_requires_default_speaker_wav(monkeypatch, tmp_path: Path) -> None:
    settings = load_settings({"TTS_MCP_OUTPUT_DIR": str(tmp_path)})
    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="xtts", command=settings.xtts_command, host=_linux_host()),
    )

    result = runner.run_speak(
        settings=settings,
        text="Hallo aus XTTS",
        output_path=str(tmp_path / "xtts_missing_speaker.wav"),
        play=False,
    )

    assert result["ok"] is False
    assert result["error_type"] == "config"
    assert "XTTS_DEFAULT_SPEAKER_WAV" in (result["error_message"] or "")


def test_run_speak_xtts_requires_existing_default_speaker_wav(monkeypatch, tmp_path: Path) -> None:
    settings = load_settings(
        {
            "TTS_MCP_OUTPUT_DIR": str(tmp_path),
            "XTTS_DEFAULT_SPEAKER_WAV": str(tmp_path / "missing.wav"),
        }
    )
    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="xtts", command=settings.xtts_command, host=_linux_host()),
    )

    result = runner.run_speak(
        settings=settings,
        text="Hallo aus XTTS",
        output_path=str(tmp_path / "xtts_missing_speaker.wav"),
        play=False,
    )

    assert result["ok"] is False
    assert result["error_type"] == "config"
    assert "not found" in (result["error_message"] or "")


def test_run_speak_chatterbox_success(monkeypatch, tmp_path: Path) -> None:
    settings = load_settings(
        {
            "TTS_MCP_OUTPUT_DIR": str(tmp_path),
            "CHATTERBOX_DEFAULT_LANGUAGE_CODE": "de-DE",
            "CHATTERBOX_AUDIO_PROMPT_PATH": str(tmp_path / "prompt.wav"),
        }
    )
    (tmp_path / "prompt.wav").write_bytes(b"fake")

    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(
            backend="chatterbox",
            command=settings.chatterbox_command,
            host=_mlx_host(),
        ),
    )

    output_file = tmp_path / "chatterbox.wav"

    def fake_run(command, **kwargs):
        assert command[0] == settings.chatterbox_command
        assert Path(command[1]).name == "chatterbox_generate.py"
        assert command[command.index("--language") + 1] == "de"
        assert command[command.index("--audio-prompt-path") + 1] == str(tmp_path / "prompt.wav")
        output_file.write_bytes(_MIN_VALID_WAV_BYTES)
        return subprocess.CompletedProcess(command, 0, "done", "")

    monkeypatch.setattr(execution_support.subprocess, "run", fake_run)

    result = runner.run_speak(
        settings=settings,
        text="Hallo aus Chatterbox",
        output_path=str(output_file),
        play=False,
    )

    assert result["ok"] is True
    assert result["backend"] == "chatterbox"


def test_run_speak_rejects_named_voice_on_xtts(monkeypatch) -> None:
    settings = load_settings({})
    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="xtts", command=settings.xtts_command, host=_linux_host()),
    )

    result = runner.run_speak(
        settings=settings,
        text="Hello",
        play=False,
        voice="speaker-a",
    )

    assert result["ok"] is False
    assert result["error_type"] == "config"
