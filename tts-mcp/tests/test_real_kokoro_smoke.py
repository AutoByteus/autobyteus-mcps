from __future__ import annotations

from pathlib import Path

import pytest

from tts_mcp.config import load_settings
from tts_mcp.runner import run_speak

from real_smoke_support import (
    IS_LINUX,
    RUN_REAL_LANGUAGE_SMOKE,
    ZH_CONFIG_PATH,
    ZH_MODEL_PATH,
    ZH_VOICES_PATH,
    assert_valid_wav,
)


@pytest.mark.skipif(
    not RUN_REAL_LANGUAGE_SMOKE,
    reason="Set TTS_MCP_RUN_REAL_LANGUAGE_SMOKE=1 to run real language smoke tests.",
)
@pytest.mark.skipif(
    not IS_LINUX,
    reason="Real Kokoro smoke test currently targets Linux.",
)
def test_real_kokoro_smoke_chinese_linux(tmp_path: Path) -> None:
    if not (ZH_MODEL_PATH.exists() and ZH_VOICES_PATH.exists() and ZH_CONFIG_PATH.exists()):
        pytest.skip(
            "Missing Kokoro zh_v1.1 assets. Run scripts/install_kokoro_onnx_linux.sh --profile zh_v1_1"
        )

    settings = load_settings(
        {
            "TTS_MCP_BACKEND": "auto",
            "TTS_MCP_LINUX_RUNTIME": "kokoro_onnx",
            "TTS_MCP_OUTPUT_DIR": str(tmp_path),
            "TTS_MCP_TIMEOUT_SECONDS": "1200",
            "TTS_MCP_AUTO_INSTALL_RUNTIME": "false",
            "TTS_MCP_ENFORCE_LATEST": "false",
            "KOKORO_TTS_MODEL_PATH": str(ZH_MODEL_PATH),
            "KOKORO_TTS_VOICES_PATH": str(ZH_VOICES_PATH),
            "KOKORO_TTS_VOCAB_CONFIG_PATH": str(ZH_CONFIG_PATH),
            "KOKORO_TTS_DEFAULT_LANG_CODE": "zh",
            "KOKORO_TTS_DEFAULT_VOICE": "zf_001",
        }
    )

    output_file = tmp_path / "chinese_kokoro.wav"
    result = run_speak(
        settings=settings,
        text="你好，这是 TTS MCP 的中文集成测试。",
        output_path=str(output_file),
        play=False,
    )

    assert result["ok"] is True, result
    assert result["backend"] == "kokoro_onnx"
    assert_valid_wav(output_file)
