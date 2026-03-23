from __future__ import annotations

from pathlib import Path

import pytest

from tts_mcp.config import load_settings
from tts_mcp.runner import run_speak

from real_smoke_support import (
    RUN_REAL_LANGUAGE_SMOKE,
    RUN_SLOW_REAL_LANGUAGE_SMOKE,
    assert_valid_wav,
    resolve_chatterbox_command,
)


@pytest.mark.skipif(
    not RUN_REAL_LANGUAGE_SMOKE or not RUN_SLOW_REAL_LANGUAGE_SMOKE,
    reason="Set TTS_MCP_RUN_REAL_LANGUAGE_SMOKE=1 and TTS_MCP_RUN_SLOW_REAL_LANGUAGE_SMOKE=1 to run Chatterbox smoke tests.",
)
def test_real_chatterbox_smoke_german(tmp_path: Path) -> None:
    chatterbox_command = resolve_chatterbox_command()
    if chatterbox_command is None:
        pytest.skip(
            "Missing Chatterbox Python command. Run scripts/install_chatterbox_runtime.sh or set CHATTERBOX_TTS_COMMAND."
        )

    settings = load_settings(
        {
            "TTS_MCP_BACKEND": "chatterbox",
            "TTS_MCP_OUTPUT_DIR": str(tmp_path),
            "TTS_MCP_TIMEOUT_SECONDS": "2400",
            "TTS_MCP_AUTO_INSTALL_RUNTIME": "false",
            "TTS_MCP_ENFORCE_LATEST": "false",
            "CHATTERBOX_TTS_COMMAND": chatterbox_command,
            "CHATTERBOX_DEFAULT_LANGUAGE_CODE": "de",
            "CHATTERBOX_DEVICE": "auto",
        }
    )

    output_file = tmp_path / "german_chatterbox.wav"
    result = run_speak(
        settings=settings,
        text="Guten Tag. Dies ist ein Chatterbox Integrationstest fuer TTS MCP.",
        output_path=str(output_file),
        play=False,
        preferred_backend="chatterbox",
    )

    assert result["ok"] is True, result
    assert result["backend"] == "chatterbox"
    assert_valid_wav(output_file)
