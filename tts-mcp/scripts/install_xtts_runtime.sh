#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${TTS_MCP_ROOT_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
exec bash "$ROOT_DIR/src/tts_mcp/runtime_assets/install_xtts_runtime.sh" "$@"
