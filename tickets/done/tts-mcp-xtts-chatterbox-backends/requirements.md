Status: Design-ready

# Requirements

## User Intent

Add XTTS-v2 and Chatterbox support to `tts-mcp` so the MCP can use those newer or more widely used multilingual TTS stacks without removing the existing MLX Audio, Kokoro ONNX, or llama.cpp backends.

## Draft Requirements

- `speak` remains the MCP tool surface for text-to-speech generation.
- Add explicit backend support for:
  - XTTS-v2
  - Chatterbox Multilingual
- Do not change current `auto` backend-routing behavior as part of this task.
- Preserve existing MLX Audio, Kokoro ONNX, and llama.cpp behavior unless XTTS or Chatterbox is explicitly selected.
- Support configuration-driven runtime selection for XTTS and Chatterbox, including any required command or Python runtime path configuration.
- Chatterbox integration targets the multilingual model path, not the English-only Turbo variant.
- Generated output handling for XTTS and Chatterbox must match current `speak` expectations:
  - explicit `output_path` support,
  - `.wav` output,
  - `play` behavior consistent with existing backends,
  - structured success/failure results consistent with existing runner behavior.
- Runtime setup for XTTS and Chatterbox must avoid breaking the existing lightweight default `tts-mcp` installation path for current backends.
- Add validation coverage for backend selection, config parsing, and runner execution behavior for the new backends.
- Update `tts-mcp` documentation for install, configuration, and runtime constraints.

## Acceptance Criteria

- With `TTS_MCP_BACKEND=xtts`, `tts-mcp` selects XTTS explicitly and reaches the XTTS execution path through `speak`.
- With `TTS_MCP_BACKEND=chatterbox`, `tts-mcp` selects Chatterbox explicitly and reaches the Chatterbox execution path through `speak`.
- Existing `auto`, `mlx_audio`, `kokoro_onnx`, and `llama_cpp` behavior remains unchanged unless explicitly configured otherwise.
- Unit and integration tests cover the new backend-selection and runner command-building behavior.
- Runtime bootstrap/version-check behavior for XTTS and Chatterbox is either implemented or explicitly documented as intentionally unsupported with clear user-facing rationale.
- `tts-mcp/README.md` documents how to install and configure XTTS and Chatterbox support.
- Real local execution is validated on the current Apple Silicon host for any backend whose runtime is feasible in this environment; if a backend is infeasible, the ticket must record the precise blocker and compensating validation evidence.

## Constraints

- Existing backend names and semantics must remain backward-compatible for current users.
- `auto` must remain opinionated around MLX/Kokoro/llama and not silently switch to XTTS or Chatterbox.
- Chatterbox-Turbo is out of scope for multilingual/German support in this ticket.

## Remaining Design Questions

- Whether XTTS should be integrated through the Coqui Python API, the `tts` CLI, or a repo-local wrapper.
- Which host/runtime combinations are officially in scope for real local execution validation during this ticket.
