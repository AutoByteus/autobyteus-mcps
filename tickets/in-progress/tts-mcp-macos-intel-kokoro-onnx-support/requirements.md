# Requirements

## Status

- `Design-ready`

## Goal / Problem Statement

Enable `tts-mcp` to support Kokoro ONNX CPU runtime on Intel macOS (`Darwin x86_64`) with a working install/bootstrap path, while preserving existing Apple Silicon and Linux behavior.

## In-Scope Use Cases

- `UC-001`: Auto backend selection on Intel macOS routes to `kokoro_onnx`.
- `UC-002`: Explicit `TTS_MCP_BACKEND=kokoro_onnx` is accepted on Intel macOS.
- `UC-003`: Runtime bootstrap auto-installs Kokoro runtime/assets on Intel macOS when missing.
- `UC-004`: Manual installer script supports Intel macOS Kokoro runtime + model asset download.
- `UC-005`: `speak` with Kokoro on Intel macOS can generate WAV and attempt playback using available local players.

## Acceptance Criteria

- Platform selection logic supports Intel macOS Kokoro path without breaking existing Linux/Apple Silicon routes.
- `scripts/install_tts_runtime.sh` can route Intel macOS to a Kokoro installer path.
- A new or refactored Kokoro installer path supports Intel macOS and downloads required model assets.
- Runtime bootstrap invokes the correct installer for Intel macOS when Kokoro runtime/assets are missing.
- Playback command selection includes a valid macOS fallback (`afplay`) when `ffplay` is unavailable.
- Tests are updated to validate new platform/bootstrap behavior.
- README documents Intel macOS support and install/config guidance.

## Constraints / Dependencies

- Depends on `kokoro-onnx` + `onnxruntime` availability on Intel macOS Python env.
- Depends on network access for model downloads (GitHub release assets).
- Keep `speak` API unchanged.

## Assumptions

- Intel macOS users prefer CPU inference and accept slower latency vs MLX on Apple Silicon.
- Existing Linux installer logic is reusable for model/profile selection semantics.

## Open Questions / Risks

- Whether Kokoro package/model compatibility changes for future releases.
- Whether all users have `ffplay`; fallback to `afplay` must be available for robust playback.

## Scope Classification

- Final classification: `Medium`
- Rationale: cross-cutting behavior touches platform selection, runtime bootstrap, install scripts, playback routing, docs, and tests.
