#!/usr/bin/env bash
set -euo pipefail

# Stable stdio launcher for MCP clients that do not inherit an interactive
# shell PATH (for example GUI-launched coding agents on macOS/Linux).
# Keep stdout reserved for MCP JSON-RPC; write diagnostics to stderr/log only.

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
LOG_DIR="${BROWSER_MCP_LOG_DIR:-${HOME:-/tmp}/.cache/autobyteus-mcps}"
LOG_FILE="${LOG_DIR}/browser-mcp.log"
mkdir -p "$LOG_DIR"

log() {
  printf '[%s] %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$*" >> "$LOG_FILE"
}

# GUI apps often miss /usr/local/bin, Homebrew, pyenv, and uv installer paths.
export PATH="/usr/local/bin:/opt/homebrew/bin:${HOME:-}/.local/bin:${HOME:-}/.cargo/bin:${HOME:-}/.pyenv/shims:/usr/bin:/bin:/usr/sbin:/sbin:${PATH:-}"

find_uv() {
  if command -v uv >/dev/null 2>&1; then
    command -v uv
    return 0
  fi
  for candidate in \
    "${UV_BIN:-}" \
    "${HOME:-}/.local/bin/uv" \
    "${HOME:-}/.cargo/bin/uv" \
    "/usr/local/bin/uv" \
    "/opt/homebrew/bin/uv"; do
    if [ -n "$candidate" ] && [ -x "$candidate" ]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  return 1
}

if ! UV_PATH="$(find_uv)"; then
  log "ERROR: uv was not found. Install uv or set UV_BIN to its absolute path. PATH=$PATH"
  printf 'browser-mcp launcher error: uv was not found. See %s\n' "$LOG_FILE" >&2
  exit 127
fi

log "Starting browser-mcp with uv=$UV_PATH project=$PROJECT_DIR python_preference=${BROWSER_MCP_PYTHON:-uv-default}"

if [ -n "${BROWSER_MCP_PYTHON:-}" ]; then
  exec "$UV_PATH" --directory "$PROJECT_DIR" run --python "$BROWSER_MCP_PYTHON" python -m browser_mcp.server 2>> "$LOG_FILE"
fi

exec "$UV_PATH" --directory "$PROJECT_DIR" run python -m browser_mcp.server 2>> "$LOG_FILE"
