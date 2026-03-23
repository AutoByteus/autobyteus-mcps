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
  local root_dir venv_dir python_bin

  root_dir="${TTS_MCP_ROOT_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
  venv_dir="$root_dir/.venv-xtts"
  python_bin="$(resolve_python_bin)"

  if [ ! -d "$venv_dir" ]; then
    echo "Creating XTTS virtual environment at $venv_dir"
    "$python_bin" -m venv "$venv_dir"
  fi

  echo "Installing latest XTTS runtime into $venv_dir"
  "$venv_dir/bin/python" -m pip install --upgrade pip setuptools wheel
  "$venv_dir/bin/pip" install --upgrade "torch" "torchaudio" "transformers<5" "coqui-tts[codec]"

  echo
  echo "coqui-tts version:"
  "$venv_dir/bin/python" - <<'PY'
import importlib.metadata as m
print(m.version("coqui-tts"))
PY

  echo
  echo "XTTS runtime command:"
  echo "  $venv_dir/bin/python"
  echo
  echo "Set this in MCP env:"
  echo "  XTTS_TTS_COMMAND=\"$venv_dir/bin/python\""
  echo "  XTTS_MODEL_NAME=\"tts_models/multilingual/multi-dataset/xtts_v2\""
  echo "  XTTS_DEFAULT_SPEAKER_WAV=\"/ABS/PATH/reference.wav\"  # recommended for voice cloning"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
