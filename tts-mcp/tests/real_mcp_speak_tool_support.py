from __future__ import annotations

import os
import platform


RUN_REAL_MCP_SPEAK = os.getenv("TTS_MCP_RUN_REAL_MCP_SPEAK") == "1"
IS_APPLE_SILICON_MAC = (
    platform.system() == "Darwin"
    and platform.machine().strip().lower() in {"arm64", "aarch64"}
)
