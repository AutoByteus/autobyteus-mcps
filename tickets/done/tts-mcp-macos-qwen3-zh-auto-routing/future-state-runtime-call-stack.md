# Future-State Runtime Call Stack

## Call Stack Version

- Current Version: `v3`
- Design Basis: `proposed-design.md v3`

## Scope

Model the future-state execution for `tts-mcp` after the Kokoro design-impact re-entry that adds:

- one executable startup owner
- one routing-policy owner
- one path-semantics owner
- one runtime-installation/readiness owner
- explicit Kokoro asset-pin metadata

The user-facing behavior remains:

- public `speak(text, output_path=None, play=True, language_code=None)`
- Apple Silicon MLX routing for English, German, and Chinese
- explicit MLX override preservation
- Kokoro Chinese support on Linux / Intel Mac without hidden install/profile drift

## Spine Summary

- Startup spine:
  - `app_runtime.run_server -> load_settings -> runtime_installation.prepare_startup_runtime -> server.create_server -> FastMCP.run`
- Public request spine:
  - `server.speak -> routing_policy.canonicalize_public_language -> runner.run_speak`
- Runtime routing spine:
  - `runner.run_speak -> platform.select_backend -> routing_policy.resolve_<backend>_request`
- Runtime readiness spine:
  - `resolved request -> runtime_installation.ensure_request_runtime_ready`
- Execution spine:
  - `ready request -> backend command/runtime execution -> output validation -> playback confirmation`

## Use Case 1: Executable server startup

### Preconditions

- The process starts through the executable entrypoint.
- Runtime auto-install may be enabled.

### Call Stack

1. Executable entrypoint calls `tts_mcp.app_runtime.run_server()`.
2. `app_runtime.run_server()` loads `TtsSettings` and `ServerConfig`.
3. `app_runtime.run_server()` calls `runtime_installation.prepare_startup_runtime(settings)`.
4. `runtime_installation.prepare_startup_runtime(...)`:
   - ensures runtime package/binary availability for the configured default backend
   - installs the default managed Kokoro profile only when that startup behavior is applicable
   - skips managed Kokoro asset install entirely when the operator pinned explicit custom Kokoro asset paths
5. `app_runtime.run_server()` logs runtime-preparation notes.
6. `app_runtime.run_server()` constructs the server through `server.create_server(...)`.
7. `server.create_server(...)` builds the MCP tool surface only.
8. `app_runtime.run_server()` runs the FastMCP server.

### Ownership Rule Captured

- Startup remains separate from the public boundary.
- Startup preparation does not try to predict every future per-call language request.

## Use Case 2: Apple Silicon caller requests Chinese

### Preconditions

- Host is Apple Silicon macOS.
- Backend is `auto` or `mlx_audio`.
- Caller invokes `speak(..., language_code="zh")`.
- No explicit MLX preset/model override is configured.

### Call Stack

1. `server.speak(...)` canonicalizes public language through `routing_policy.canonicalize_public_language(...)`.
2. `runner.run_speak(...)` validates text/speed and resolves output path.
3. `platform.select_backend(...)` resolves Apple Silicon `auto` to `mlx_audio`.
4. `routing_policy.resolve_mlx_request(...)` computes:
   - effective language `zh`
   - effective model `qwen_base_hq`
   - explicit-override status `false`
5. `runtime_installation.ensure_request_runtime_ready(...)` performs no extra work for MLX.
6. `backend_commands.build_mlx_command(...)` consumes the resolved request.
7. Execution proceeds unchanged.

## Use Case 3: Linux clean install, English defaults, later first Chinese Kokoro request

### Preconditions

- Host is Linux.
- Backend resolves to `kokoro_onnx`.
- Startup uses default English Kokoro settings.
- A later caller invokes `speak(..., language_code="zh")`.
- Kokoro asset paths were not explicitly pinned.

### Call Stack

1. Startup runs `runtime_installation.prepare_startup_runtime(settings)` and installs only the default managed profile needed at startup, typically `managed_v1_0`.
2. Later, `server.speak(...)` forwards canonical public language `zh`.
3. `runner.run_speak(...)` selects `kokoro_onnx`.
4. `routing_policy.resolve_kokoro_request(...)` returns a managed Kokoro request:
   - effective language `cmn`
   - managed profile `zh_v1_1`
   - managed zh assets/voice
   - runtime install allowed `true`
5. Before synthesis, `runtime_installation.ensure_request_runtime_ready(...)` checks whether the managed zh assets exist.
6. If missing and auto-install is enabled, it installs `zh_v1_1` on demand.
7. `kokoro_runtime.run_kokoro_generation(...)` receives a ready Kokoro request and synthesizes without install/profile fallback logic.

### Ownership Rule Captured

- Request-time runtime readiness is now owned explicitly instead of being an accidental gap between startup install and runtime routing.

## Use Case 4: Explicit Kokoro asset pins suppress managed zh auto-switching

### Preconditions

- Host resolves to `kokoro_onnx`.
- Operator explicitly sets Kokoro model/voices paths in MCP config, even if they point to the English default asset locations.
- Caller invokes `speak(..., language_code="zh")`.

### Call Stack

1. `load_settings(...)` records both the resolved Kokoro path values and the `*_explicit` metadata.
2. `routing_policy.resolve_kokoro_request(...)` sees explicit Kokoro asset pins.
3. The resolved request is marked as an explicit/custom Kokoro asset request, not a managed zh profile request.
4. `runtime_installation.ensure_request_runtime_ready(...)` does not install/switch a managed zh profile for that request.
5. Execution uses the pinned operator assets or fails clearly if they are invalid/missing.

### Ownership Rule Captured

- Explicit operator pins are authoritative because explicitness is now represented directly, not guessed from path equality.

## Use Case 5: Explicit zh asset pins with implicit missing vocab/voice defaults

### Preconditions

- Operator explicitly points Kokoro model/voices to the managed zh asset pair.
- Vocab path or default voice may be omitted.

### Call Stack

1. `load_settings(...)` records explicit model/voices pins.
2. `routing_policy.resolve_kokoro_request(...)` recognizes that the explicit pins correspond to the managed zh profile.
3. The request keeps the explicit asset authority but may derive compatible missing fields:
   - zh vocab config if omitted
   - zh default voice when the voice itself was not explicitly pinned
4. Runtime readiness skips install if the explicit managed zh assets already exist; otherwise it may surface a missing-asset/config error according to the explicit-pin contract.

## Use Case 6: XTTS / Chatterbox asset paths

### Preconditions

- Operator configures relative backend asset paths such as:
  - `XTTS_DEFAULT_SPEAKER_WAV`
  - `CHATTERBOX_AUDIO_PROMPT_PATH`

### Call Stack

1. `load_settings(...)` normalizes configured paths through the path-semantics owner.
2. `runner.run_speak(...)` forwards normalized settings into backend command building.
3. Backend command builders consume already-normalized paths only.
4. No backend builder decides its own relative-path base.

## Critical Failure Path A: First-run Chinese Qwen model download

1. Caller requests Chinese on Apple Silicon with no explicit MLX override.
2. `routing_policy.resolve_mlx_request(...)` selects Qwen.
3. `backend_contracts.resolve_mlx_subprocess_env(...)` checks cache for the resolved model.
4. If cache is missing and offline mode is `auto`, MLX downloads the model on first run.
5. Future runs reuse cache.

## Non-Regression Rules Captured In The Call Stack

- Public MCP surface remains `language_code` only.
- Apple Silicon still uses `mlx_audio` in `auto`.
- Explicit MLX overrides remain authoritative.
- Kokoro Chinese support remains available on Linux / Intel Mac.
- Startup install and first per-call Kokoro Chinese execution are now modeled as one coherent runtime spine rather than two disconnected decisions.
