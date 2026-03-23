from __future__ import annotations

from pathlib import Path

import pytest

from tts_mcp.config import load_settings
from tts_mcp.runner import run_speak

from real_smoke_support import (
    IS_APPLE_SILICON_MAC,
    RUN_REAL_LANGUAGE_SMOKE,
    assert_valid_wav,
    resolve_mlx_command,
)


@pytest.mark.skipif(
    not RUN_REAL_LANGUAGE_SMOKE,
    reason="Set TTS_MCP_RUN_REAL_LANGUAGE_SMOKE=1 to run real language smoke tests.",
)
@pytest.mark.skipif(
    not IS_APPLE_SILICON_MAC,
    reason="Real MLX smoke tests require Apple Silicon macOS.",
)
def test_real_mlx_smoke_english(tmp_path: Path) -> None:
    mlx_command = resolve_mlx_command()
    if mlx_command is None:
        pytest.skip(
            "Missing MLX audio command. Run scripts/install_mlx_audio_macos.sh or set MLX_TTS_COMMAND."
        )

    settings = load_settings(
        {
            "TTS_MCP_BACKEND": "mlx_audio",
            "TTS_MCP_OUTPUT_DIR": str(tmp_path),
            "TTS_MCP_TIMEOUT_SECONDS": "1200",
            "TTS_MCP_ENFORCE_LATEST": "false",
            "TTS_MCP_AUTO_INSTALL_RUNTIME": "false",
            "MLX_TTS_COMMAND": mlx_command,
            "MLX_TTS_DEFAULT_LANG_CODE": "en",
        }
    )

    output_file = tmp_path / "english_mlx.wav"
    result = run_speak(
        settings=settings,
        text="This is an English integration smoke test for TTS MCP.",
        output_path=str(output_file),
        play=False,
    )

    assert result["ok"] is True, result
    assert result["backend"] == "mlx_audio"
    assert result["command"][result["command"].index("--model") + 1] == "mlx-community/Kokoro-82M-bf16"
    assert result["command"][result["command"].index("--lang_code") + 1] == "a"
    assert_valid_wav(output_file)


@pytest.mark.skipif(
    not RUN_REAL_LANGUAGE_SMOKE,
    reason="Set TTS_MCP_RUN_REAL_LANGUAGE_SMOKE=1 to run real language smoke tests.",
)
@pytest.mark.skipif(
    not IS_APPLE_SILICON_MAC,
    reason="Real MLX smoke tests require Apple Silicon macOS.",
)
def test_real_mlx_smoke_german(tmp_path: Path) -> None:
    mlx_command = resolve_mlx_command()
    if mlx_command is None:
        pytest.skip(
            "Missing MLX audio command. Run scripts/install_mlx_audio_macos.sh or set MLX_TTS_COMMAND."
        )

    settings = load_settings(
        {
            "TTS_MCP_BACKEND": "mlx_audio",
            "TTS_MCP_OUTPUT_DIR": str(tmp_path),
            "TTS_MCP_TIMEOUT_SECONDS": "1200",
            "TTS_MCP_ENFORCE_LATEST": "false",
            "TTS_MCP_AUTO_INSTALL_RUNTIME": "false",
            "MLX_TTS_COMMAND": mlx_command,
            "MLX_TTS_DEFAULT_LANG_CODE": "de",
        }
    )

    output_file = tmp_path / "german_mlx.wav"
    result = run_speak(
        settings=settings,
        text="Guten Tag. Dies ist ein deutscher Integrationstest fuer TTS MCP.",
        output_path=str(output_file),
        play=False,
    )

    assert result["ok"] is True, result
    assert result["backend"] == "mlx_audio"
    assert result["command"][result["command"].index("--model") + 1] == (
        "mlx-community/3b-de-ft-research_release-bf16"
    )
    assert result["command"][result["command"].index("--lang_code") + 1] == "de"
    assert_valid_wav(output_file)
