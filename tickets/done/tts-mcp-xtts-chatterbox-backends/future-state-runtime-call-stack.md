# Future-State Runtime Call Stack

## Call Stack Version

- Current Version: `v2`
- Design Basis: `proposed-design.md v2`

## Scope

Model the refactored future-state execution for `tts-mcp` after the `runner.py` ownership split:

- XTTS explicit backend
- Chatterbox explicit backend
- existing `auto` MLX / llama command-backed behavior
- existing Kokoro in-process behavior

The public MCP tool remains:

- `speak(text, output_path=None, play=True)`

## Spine Summary

- Main orchestration spine:
  - `server.speak -> runner.run_speak -> backend execution owner -> execution_support -> SpeakResult`
- Command-backed branch:
  - `runner.run_speak -> backend_commands -> execution_support.execute_command`
- Kokoro branch:
  - `runner.run_speak -> kokoro_runtime.run_kokoro_generation -> execution_support`
- Bounded local Kokoro runtime spine:
  - `kokoro_runtime -> runtime config -> runtime load -> optional misaki zh -> PCM WAV write`

## Use Case 1: XTTS explicit backend generates German speech

### Preconditions

- MCP config sets `TTS_MCP_BACKEND=xtts`.
- XTTS wrapper runtime is installed and available.
- XTTS config includes:
  - default or explicit language code
  - a usable speaker WAV reference

### Call Stack

1. MCP host starts `tts_mcp.server`.
2. `tts_mcp.config.load_settings(...)` loads XTTS-related settings.
3. `tts_mcp.runtime_bootstrap.bootstrap_runtime(settings)` ensures the XTTS wrapper runtime exists.
4. User calls `speak(text=..., output_path=..., play=...)`.
5. `tts_mcp.server.speak(...)` forwards to `tts_mcp.runner.run_speak(...)`.
6. `runner.run_speak(...)` validates request text, speed, and public-call inputs.
7. `tts_mcp.platform.select_backend(...)` resolves explicit backend `xtts`.
8. `tts_mcp.execution_support.resolve_output_path(...)` resolves the WAV output target.
9. `tts_mcp.version_check.check_backend_runtime_version(...)` validates XTTS runtime freshness when enabled.
10. `tts_mcp.backend_commands.build_xtts_command(...)` builds the XTTS wrapper command.
11. `tts_mcp.backend_contracts.resolve_xtts_subprocess_env(...)` decides whether `COQUI_TOS_AGREED=1` must be forwarded.
12. `tts_mcp.execution_support.acquire_global_generation_lock(...)` guards concurrent generation.
13. `tts_mcp.execution_support.execute_command(...)` runs the XTTS wrapper command.
14. The XTTS wrapper loads XTTS-v2 in the XTTS virtualenv and writes a WAV.
15. `tts_mcp.execution_support.output_signature(...)` confirms a new non-empty WAV was produced.
16. If generation fails, `tts_mcp.backend_contracts.classify_generation_failure(...)` translates XTTS-specific failures such as first-run TOS rejection.
17. If `play=true`, `tts_mcp.execution_support.build_linux_play_command(...)` and `execute_command(...)` handle playback.
18. `runner.run_speak(...)` returns a structured `SpeakResult`.

## Use Case 2: Chatterbox explicit backend generates German speech

### Preconditions

- MCP config sets `TTS_MCP_BACKEND=chatterbox`.
- Chatterbox wrapper runtime is installed and available.
- Chatterbox config includes a default or explicit language code.

### Call Stack

1. MCP host starts `tts_mcp.server`.
2. `tts_mcp.config.load_settings(...)` loads Chatterbox settings.
3. `tts_mcp.runtime_bootstrap.bootstrap_runtime(settings)` ensures the Chatterbox runtime exists.
4. User calls `speak(...)`.
5. `tts_mcp.server.speak(...)` calls `tts_mcp.runner.run_speak(...)`.
6. `runner.run_speak(...)` validates inputs and resolves the output path through `execution_support`.
7. `tts_mcp.platform.select_backend(...)` resolves explicit backend `chatterbox`.
8. `tts_mcp.version_check.check_backend_runtime_version(...)` validates runtime freshness when enabled.
9. `tts_mcp.backend_commands.build_chatterbox_command(...)` builds the Chatterbox wrapper command.
10. `tts_mcp.backend_contracts.resolve_chatterbox_language_code(...)` provides the normalized language ID used by the command builder.
11. `tts_mcp.execution_support.acquire_global_generation_lock(...)` guards generation.
12. `tts_mcp.execution_support.execute_command(...)` runs the Chatterbox wrapper command.
13. The Chatterbox wrapper loads `ChatterboxMultilingualTTS` in its dedicated virtualenv and writes a WAV.
14. `tts_mcp.execution_support.output_signature(...)` confirms a new non-empty WAV was produced.
15. If `play=true`, `execution_support` owns playback execution and confirmation.
16. `runner.run_speak(...)` returns a structured `SpeakResult`.

## Use Case 3: Existing command-backed MLX / llama behavior remains stable

### Preconditions

- MCP config sets `TTS_MCP_BACKEND=auto`, `mlx_audio`, or `llama_cpp`.

### Call Stack

1. MCP host starts `tts_mcp.server`.
2. `tts_mcp.config.load_settings(...)` loads existing backend settings as today.
3. `tts_mcp.runtime_bootstrap.bootstrap_runtime(settings)` behaves exactly as current logic for MLX / Kokoro / llama targets.
4. User calls `speak(...)`.
5. `server.speak(...)` forwards to `runner.run_speak(...)`.
6. `platform.select_backend(...)` resolves `auto` or the explicit existing backend.
7. For MLX / llama:
   - `backend_commands.py` builds the command contract
   - `backend_contracts.py` normalizes language/env policy as needed
   - `execution_support.py` executes and validates output
8. For MLX playback confirmation:
   - `backend_contracts.py` owns the MLX-specific playback marker interpretation
9. `runner.run_speak(...)` returns the same style of structured result as before.

## Use Case 4: Existing Kokoro in-process behavior remains stable

### Preconditions

- MCP config sets `TTS_MCP_BACKEND=kokoro_onnx`, or `auto` resolves to Kokoro.

### Call Stack

1. MCP host starts `tts_mcp.server`.
2. `tts_mcp.config.load_settings(...)` loads Kokoro settings.
3. User calls `speak(...)`.
4. `server.speak(...)` forwards to `runner.run_speak(...)`.
5. `platform.select_backend(...)` resolves `kokoro_onnx`.
6. `execution_support.resolve_output_path(...)` resolves the output path.
7. `execution_support.acquire_global_generation_lock(...)` guards generation.
8. `kokoro_runtime.run_kokoro_generation(...)` owns synthesis.
9. Inside `kokoro_runtime.run_kokoro_generation(...)`:
   - normalize Kokoro language via `backend_contracts.resolve_kokoro_language_code(...)`
   - resolve runtime config and selected voice
   - load Kokoro runtime/model paths
   - if Chinese profile requires phonemization, load Misaki and phonemize text
   - synthesize samples
   - write PCM WAV output
10. `execution_support.output_signature(...)` confirms a new non-empty WAV was produced.
11. If `play=true`, `execution_support` owns playback execution.
12. `runner.run_speak(...)` returns a structured `SpeakResult`.

## Bounded Local Spine: Kokoro runtime flow

- Parent owner:
  - `tts_mcp.kokoro_runtime`
- Start:
  - `run_kokoro_generation(...)`
- End:
  - PCM WAV written to disk
- Arrow chain:
  - `run_kokoro_generation -> resolve runtime config -> load runtime -> optional zh g2p -> synthesize -> write wav`
- Why explicit:
  - The Chinese phonemization branch and runtime-profile resolution are not generic helpers; they are real Kokoro-specific sequencing owned by the Kokoro runtime file.

## Critical Failure Path A: XTTS terms not accepted yet

1. User selects backend `xtts`.
2. `backend_commands.py` builds the XTTS wrapper command normally.
3. XTTS runtime fails during first model download because Coqui terms were not accepted.
4. `execution_support.execute_command(...)` returns stderr/stdout and exit information.
5. `backend_contracts.classify_generation_failure(...)` recognizes the XTTS TOS markers and returns an actionable validation error.
6. `runner.run_speak(...)` returns the structured failure without guessing or silently bypassing the prompt.

## Critical Failure Path B: Chatterbox runtime missing or invalid

1. User selects backend `chatterbox`.
2. Runtime bootstrap is disabled or the Chatterbox wrapper/runtime is missing.
3. `backend_commands.py` still builds the command contract, but `execution_support.execute_command(...)` fails with `FileNotFoundError`, or the wrapper exits with a runtime/config error.
4. `runner.run_speak(...)` returns a dependency or execution failure with wrapper output preserved.

## Critical Failure Path C: Output file not refreshed

1. Any backend exits zero but does not create or update the requested WAV.
2. `execution_support.output_signature(...)` compares pre/post signatures.
3. `runner.run_speak(...)` returns an execution failure that the output was missing or unchanged.

## Non-Regression Rules Captured In The Call Stack

- `server.py` remains the only public MCP boundary.
- `runner.py` remains the only orchestration owner.
- XTTS and Chatterbox remain explicit opt-in backends.
- `auto` routing is unchanged.
- Kokoro remains the only in-process synthesis backend.
- Execution helpers stay off the main line and do not absorb backend policy.
