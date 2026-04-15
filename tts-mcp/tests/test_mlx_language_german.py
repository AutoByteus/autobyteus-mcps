from __future__ import annotations

from pathlib import Path
import subprocess

from mlx_language_test_support import _MIN_VALID_WAV_BYTES, _mlx_host, _mock_runtime_version_check
from tts_mcp.config import load_settings
from tts_mcp.platform import BackendSelection
import tts_mcp.execution_support as execution_support
import tts_mcp.runner as runner


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
