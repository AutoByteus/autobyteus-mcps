from __future__ import annotations

import os
from pathlib import Path
import platform

import pytest

from mcp_session_test_support import _run_with_session
from tts_mcp.config import ServerConfig, load_settings
import tts_mcp.server as server_module


RUN_REAL_LINUX_KOKORO_CN = os.getenv("TTS_MCP_RUN_REAL_LINUX_KOKORO_CN") == "1"
IS_LINUX = platform.system() == "Linux"
ROOT_DIR = Path(__file__).resolve().parents[1]
ZH_MODEL_PATH = ROOT_DIR / ".tools" / "kokoro-v1.1-zh" / "kokoro-v1.1-zh.onnx"
ZH_VOICES_PATH = ROOT_DIR / ".tools" / "kokoro-v1.1-zh" / "voices-v1.1-zh.bin"
ZH_CONFIG_PATH = ROOT_DIR / ".tools" / "kokoro-v1.1-zh" / "config.json"


@pytest.mark.skipif(
    not RUN_REAL_LINUX_KOKORO_CN,
    reason="Set TTS_MCP_RUN_REAL_LINUX_KOKORO_CN=1 to run real Linux Kokoro Chinese integration test.",
)
@pytest.mark.skipif(
    not IS_LINUX,
    reason="Real Linux Kokoro Chinese integration test requires Linux.",
)
@pytest.mark.anyio
async def test_real_linux_kokoro_chinese_with_env_defaults(tmp_path: Path) -> None:
    if not (ZH_MODEL_PATH.exists() and ZH_VOICES_PATH.exists() and ZH_CONFIG_PATH.exists()):
        pytest.skip(
            "Missing Kokoro zh_v1.1 assets. Run scripts/install_kokoro_onnx_linux.sh --profile zh_v1_1"
        )

    settings = load_settings(
        {
            "TTS_MCP_BACKEND": "auto",
            "TTS_MCP_LINUX_RUNTIME": "kokoro_onnx",
            "TTS_MCP_OUTPUT_DIR": str(tmp_path),
            "TTS_MCP_AUTO_INSTALL_RUNTIME": "false",
            "TTS_MCP_ENFORCE_LATEST": "false",
            "KOKORO_TTS_MODEL_PATH": str(ZH_MODEL_PATH),
            "KOKORO_TTS_VOICES_PATH": str(ZH_VOICES_PATH),
            "KOKORO_TTS_VOCAB_CONFIG_PATH": str(ZH_CONFIG_PATH),
            # Intentionally use zh alias to validate normalization to cmn.
            "KOKORO_TTS_DEFAULT_LANG_CODE": "zh",
            "KOKORO_TTS_DEFAULT_VOICE": "zf_001",
        }
    )

    server = server_module.create_server(
        settings=settings,
        server_config=ServerConfig(name="tts-real-linux-kokoro-cn-test"),
    )

    async def run_client(session) -> None:
        output_path = tmp_path / "real_linux_kokoro_cn.wav"
        result = await session.call_tool(
            "speak",
            {
                "text": "你好，这是 Linux Kokoro 中文集成测试。",
                "output_path": str(output_path),
                "play": False,
            },
        )
        assert not result.isError
        payload = result.structuredContent
        assert payload["ok"] is True
        assert output_path.exists()
        assert output_path.stat().st_size > 44

    await _run_with_session(server, run_client)
