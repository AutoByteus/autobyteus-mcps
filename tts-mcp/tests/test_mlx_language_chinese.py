from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

from tts_mcp.config import ServerConfig, load_settings
from tts_mcp.platform import BackendSelection
import tts_mcp.execution_support as execution_support
import tts_mcp.routing_policy as routing_policy
import tts_mcp.runner as runner
import tts_mcp.server as server_module

from mcp_session_test_support import _run_with_session
from mlx_language_test_support import _MIN_VALID_WAV_BYTES, _mlx_host, _mock_runtime_version_check


@pytest.mark.anyio
async def test_speak_tool_canonicalizes_chinese_language_before_delegating(monkeypatch):
    runner_result = {
        "ok": True,
        "backend": "mlx_audio",
        "platform": "Darwin",
        "machine": "arm64",
        "command": ["mlx_audio.tts.generate", "--text", "hi"],
        "output_path": "/tmp/out.wav",
        "played": True,
        "playback_command": None,
        "warnings": [],
        "stdout": "ok",
        "stderr": None,
        "exit_code": 0,
        "error_type": None,
        "error_message": None,
    }
    captured: dict[str, object] = {}

    def fake_run_speak(**kwargs):
        captured.update(kwargs)
        return runner_result

    monkeypatch.setattr(server_module, "run_speak", fake_run_speak)

    server = server_module.create_server(
        settings=load_settings({"TTS_MCP_AUTO_INSTALL_RUNTIME": "false"}),
        server_config=ServerConfig(name="tts-test"),
    )

    async def run_client(session) -> None:
        result = await session.call_tool("speak", {"text": "hello", "language": "zh-cn"})
        assert not result.isError
        assert result.structuredContent == {"ok": True}
        assert captured["language_code"] == "zh"

    await _run_with_session(server, run_client)


def test_run_speak_mlx_chinese_auto_selects_qwen_model_and_language(monkeypatch, tmp_path: Path) -> None:
    settings = load_settings({"TTS_MCP_OUTPUT_DIR": str(tmp_path)})

    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="mlx_audio", command=settings.mlx_command, host=_mlx_host()),
    )

    output_file = tmp_path / "mlx_zh.wav"

    def fake_run(command, **kwargs):
        assert command[0] == settings.mlx_command
        assert command[command.index("--model") + 1] == "mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16"
        assert command[command.index("--lang_code") + 1] == "zh"
        assert command[command.index("--temperature") + 1] == "0.0"
        assert command[command.index("--voice") + 1] == "Vivian"
        prefix = command[command.index("--file_prefix") + 1]
        Path(f"{prefix}.wav").write_bytes(_MIN_VALID_WAV_BYTES)
        return subprocess.CompletedProcess(command, 0, "ok", "")

    monkeypatch.setattr(execution_support.subprocess, "run", fake_run)

    result = runner.run_speak(
        settings=settings,
        text="你好，来自 MLX。",
        output_path=str(output_file),
        play=False,
        language_code="zh",
    )

    assert result["ok"] is True
    assert result["backend"] == "mlx_audio"


def test_run_speak_mlx_chinese_honors_explicit_temperature_override(monkeypatch, tmp_path: Path) -> None:
    settings = load_settings({"TTS_MCP_OUTPUT_DIR": str(tmp_path)})

    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="mlx_audio", command=settings.mlx_command, host=_mlx_host()),
    )

    output_file = tmp_path / "mlx_zh_temperature.wav"

    def fake_run(command, **kwargs):
        assert command[command.index("--temperature") + 1] == "0.4"
        prefix = command[command.index("--file_prefix") + 1]
        Path(f"{prefix}.wav").write_bytes(_MIN_VALID_WAV_BYTES)
        return subprocess.CompletedProcess(command, 0, "ok", "")

    monkeypatch.setattr(execution_support.subprocess, "run", fake_run)

    result = runner.run_speak(
        settings=settings,
        text="你好，来自 MLX。",
        output_path=str(output_file),
        play=False,
        language_code="zh",
        temperature=0.4,
    )

    assert result["ok"] is True


def test_resolve_mlx_request_auto_selects_qwen_for_chinese() -> None:
    settings = load_settings({})

    resolved = routing_policy.resolve_mlx_request(settings=settings, language_code="zh")

    assert resolved.model_id == "mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16"
    assert resolved.language_code == "zh"
    assert resolved.effective_voice == "Vivian"
    assert resolved.supports_named_speakers is True
    assert resolved.auto_model_selection_applied is True


def test_resolve_mlx_request_keeps_explicit_mlx_model_for_chinese() -> None:
    settings = load_settings(
        {
            "TTS_MCP_MLX_MODEL_PRESET": "kokoro_fast",
            "MLX_TTS_MODEL": "mlx-community/Kokoro-82M-bf16",
        }
    )

    resolved = routing_policy.resolve_mlx_request(settings=settings, language_code="zh")

    assert resolved.model_id == "mlx-community/Kokoro-82M-bf16"
    assert resolved.language_code == "zh"
    assert resolved.effective_voice is None
    assert resolved.supports_named_speakers is False
    assert resolved.auto_model_selection_applied is False


def test_resolve_mlx_request_rejects_named_voice_on_explicit_base_model() -> None:
    settings = load_settings(
        {
            "TTS_MCP_MLX_MODEL_PRESET": "qwen_base_hq",
            "MLX_TTS_MODEL": "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16",
        }
    )

    with pytest.raises(ValueError, match="does not support named speakers"):
        routing_policy.resolve_mlx_request(
            settings=settings,
            language_code="zh",
            requested_voice="Vivian",
        )


def test_run_speak_returns_config_error_for_named_voice_on_explicit_base_model(
    monkeypatch, tmp_path: Path
) -> None:
    settings = load_settings(
        {
            "TTS_MCP_OUTPUT_DIR": str(tmp_path),
            "TTS_MCP_MLX_MODEL_PRESET": "qwen_base_hq",
            "MLX_TTS_MODEL": "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16",
        }
    )

    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="mlx_audio", command=settings.mlx_command, host=_mlx_host()),
    )

    result = runner.run_speak(
        settings=settings,
        text="你好，来自 MLX。",
        output_path=str(tmp_path / "mlx_zh_fail.wav"),
        play=False,
        language_code="zh",
        voice="Vivian",
    )

    assert result["ok"] is False
    assert result["error_type"] == "config"
    assert "does not support named speakers" in (result["error_message"] or "")


@pytest.mark.anyio
async def test_speak_tool_returns_clear_error_for_named_voice_on_explicit_base_model(
    monkeypatch, tmp_path: Path
) -> None:
    settings = load_settings(
        {
            "TTS_MCP_OUTPUT_DIR": str(tmp_path),
            "TTS_MCP_AUTO_INSTALL_RUNTIME": "false",
            "TTS_MCP_ENFORCE_LATEST": "false",
            "TTS_MCP_MLX_MODEL_PRESET": "qwen_base_hq",
            "MLX_TTS_MODEL": "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16",
        }
    )

    monkeypatch.setattr(
        runner,
        "select_backend",
        lambda **_: BackendSelection(backend="mlx_audio", command=settings.mlx_command, host=_mlx_host()),
    )

    server = server_module.create_server(
        settings=settings,
        server_config=ServerConfig(name="tts-test"),
    )

    async def run_client(session) -> None:
        result = await session.call_tool(
            "speak",
            {
                "text": "你好，这是中文语音角色测试。",
                "language": "zh",
                "voice": "Vivian",
                "play": False,
            },
        )
        assert not result.isError
        assert result.structuredContent["ok"] is False
        assert "does not support named speakers" in result.structuredContent["reason"]

    await _run_with_session(server, run_client)
