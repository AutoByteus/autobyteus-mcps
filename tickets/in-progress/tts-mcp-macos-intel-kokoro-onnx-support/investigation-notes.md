# Investigation Notes

## Ticket

- Name: `tts-mcp-macos-intel-kokoro-onnx-support`
- Date: `2026-02-24`

## Sources Consulted

- Local files:
  - `tts-mcp/README.md`
  - `tts-mcp/src/tts_mcp/platform.py`
  - `tts-mcp/src/tts_mcp/runtime_bootstrap.py`
  - `tts-mcp/src/tts_mcp/runner.py`
  - `tts-mcp/scripts/install_tts_runtime.sh`
  - `tts-mcp/scripts/install_kokoro_onnx_linux.sh`
  - `tts-mcp/tests/test_platform.py`
  - `tts-mcp/tests/test_runtime_bootstrap.py`
- Runtime validation commands:
  - `uv pip install --python .venv/bin/python --upgrade kokoro-onnx`
  - direct Kokoro generation check on host

## Current Host Facts

- Host OS/arch: `Darwin x86_64` (Intel Mac)
- Existing `tts-mcp` behavior:
  - `platform.select_backend()` rejects `kokoro_onnx` unless host is Linux.
  - `install_tts_runtime.sh` supports only macOS `arm64` for MLX and Linux for Kokoro/Llama.
  - Auto runtime bootstrap installs Kokoro only on Linux.

## Key Findings

1. **Runtime capability exists on Intel macOS today.**
   - `kokoro-onnx` and `onnxruntime` install successfully in `tts-mcp/.venv`.
   - A real WAV was generated successfully at:
     - `tts-mcp/outputs/intel-mac-kokoro-test.wav`
2. **Blocker is policy/code gating, not runtime feasibility.**
   - Backend selection and installer routing currently enforce Linux-only for Kokoro.
3. **Playback behavior is nearly portable already.**
   - `ffplay` exists on this machine.
   - macOS-native `afplay` exists and should be a fallback when `ffplay` is missing.

## Constraints

- Preserve existing default behavior:
  - Apple Silicon macOS auto -> `mlx_audio`
  - Linux auto -> runtime policy (`kokoro_onnx`/`llama_cpp`)
- No backward-compat wrappers; implement cleanly in current flow.
- Keep MCP API surface stable (`speak` contract unchanged).

## Unknowns / Risks

- `kokoro-onnx` upstream package behavior can change across releases.
- Mandarin profile dependencies (`misaki-fork[zh]`) on Intel macOS should be treated as best effort with clear install-time errors.

## Implications For Requirements/Design

- Add first-class Intel macOS routing for Kokoro in platform selection.
- Add a dedicated Intel macOS Kokoro installer script and route `install_tts_runtime.sh` to it.
- Extend runtime bootstrap to auto-install Kokoro on Intel macOS when selected.
- Update docs and tests to lock behavior.
