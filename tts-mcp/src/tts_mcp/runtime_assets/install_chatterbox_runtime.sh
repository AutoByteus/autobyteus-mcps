#!/usr/bin/env bash
set -euo pipefail

resolve_python_bin() {
  local candidate

  if [ -n "${PYTHON_BIN:-}" ]; then
    if command -v "$PYTHON_BIN" >/dev/null 2>&1 && python_is_supported "$PYTHON_BIN"; then
      printf '%s\n' "$PYTHON_BIN"
      return 0
    fi
    echo "Python 3.10+ not found or unsupported: $PYTHON_BIN" >&2
    return 1
  fi

  for candidate in python3.13 python3.12 python3.11 python3.10 python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 && python_is_supported "$candidate"; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done

  echo "Python 3.10+ not found. Install python3.10+ or set PYTHON_BIN." >&2
  return 1
}

python_is_supported() {
  "$1" - <<'PY' >/dev/null 2>&1
import sys
raise SystemExit(0 if sys.version_info >= (3, 10) else 1)
PY
}

main() {
  local root_dir venv_dir python_bin local_checkout install_target

  root_dir="${TTS_MCP_ROOT_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
  venv_dir="$root_dir/.venv-chatterbox"
  local_checkout="$root_dir/../chatterbox"
  python_bin="$(resolve_python_bin)"

  if [ ! -d "$venv_dir" ]; then
    echo "Creating Chatterbox virtual environment at $venv_dir"
    "$python_bin" -m venv "$venv_dir"
  fi

  "$venv_dir/bin/python" -m pip install --upgrade pip setuptools wheel

  if [ -d "$local_checkout" ]; then
    install_target="$local_checkout"
    echo "Installing Chatterbox runtime from local checkout: $install_target"
  else
    install_target="chatterbox-tts"
    echo "Installing Chatterbox runtime from PyPI"
  fi

  "$venv_dir/bin/pip" install --upgrade "$install_target"

  echo
  echo "chatterbox-tts version:"
  "$venv_dir/bin/python" - <<'PY'
import importlib.metadata as m
print(m.version("chatterbox-tts"))
PY

  echo
  echo "Chatterbox runtime command:"
  echo "  $venv_dir/bin/python"
  echo
  echo "Set this in MCP env:"
  echo "  CHATTERBOX_TTS_COMMAND=\"$venv_dir/bin/python\""
  echo "  CHATTERBOX_DEFAULT_LANGUAGE_CODE=\"de\""
  echo "  CHATTERBOX_AUDIO_PROMPT_PATH=\"/ABS/PATH/reference.wav\"  # optional voice cloning prompt"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
