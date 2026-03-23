from __future__ import annotations

from pathlib import Path
import os

import pytest

from tts_mcp.config import load_settings
from tts_mcp.runner import run_speak

from real_smoke_support import (
    DEFAULT_GERMAN_SPEAKER_WAV,
    RUN_REAL_LANGUAGE_SMOKE,
    RUN_SLOW_REAL_LANGUAGE_SMOKE,
    assert_valid_wav,
    resolve_xtts_command,
)


@pytest.mark.skipif(
    not RUN_REAL_LANGUAGE_SMOKE or not RUN_SLOW_REAL_LANGUAGE_SMOKE,
    reason="Set TTS_MCP_RUN_REAL_LANGUAGE_SMOKE=1 and TTS_MCP_RUN_SLOW_REAL_LANGUAGE_SMOKE=1 to run XTTS smoke tests.",
)
def test_real_xtts_smoke_german(tmp_path: Path) -> None:
    xtts_command = resolve_xtts_command()
    if xtts_command is None:
        pytest.skip(
            "Missing XTTS Python command. Run scripts/install_xtts_runtime.sh or set XTTS_TTS_COMMAND."
        )
    tos_accepted = (
        os.getenv("XTTS_COQUI_TOS_AGREED") == "true"
        or os.getenv("COQUI_TOS_AGREED") == "1"
    )
    if not tos_accepted:
        pytest.skip(
            "XTTS requires explicit Coqui terms acceptance. Set XTTS_COQUI_TOS_AGREED=true "
            "for MCP config after reviewing the license terms."
        )
    if not DEFAULT_GERMAN_SPEAKER_WAV.exists():
        pytest.skip(f"Missing XTTS speaker prompt WAV: {DEFAULT_GERMAN_SPEAKER_WAV}")

    settings = load_settings(
        {
            "TTS_MCP_BACKEND": "xtts",
            "TTS_MCP_OUTPUT_DIR": str(tmp_path),
            "TTS_MCP_TIMEOUT_SECONDS": "2400",
            "TTS_MCP_AUTO_INSTALL_RUNTIME": "false",
            "TTS_MCP_ENFORCE_LATEST": "false",
            "XTTS_TTS_COMMAND": xtts_command,
            "XTTS_DEFAULT_LANGUAGE_CODE": "de",
            "XTTS_DEFAULT_SPEAKER_WAV": str(DEFAULT_GERMAN_SPEAKER_WAV),
            "XTTS_DEVICE": "cpu",
            "XTTS_COQUI_TOS_AGREED": "true",
        }
    )

    output_file = tmp_path / "german_xtts.wav"
    result = run_speak(
        settings=settings,
        text="Guten Tag. Dies ist ein XTTS Integrationstest fuer TTS MCP.",
        output_path=str(output_file),
        play=False,
        preferred_backend="xtts",
    )

    assert result["ok"] is True, result
    assert result["backend"] == "xtts"
    assert_valid_wav(output_file)
