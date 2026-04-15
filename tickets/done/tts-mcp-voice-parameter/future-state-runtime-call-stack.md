# Future-State Runtime Call Stack

## Use Case

Public MCP caller provides `text`, optional `language`, optional `voice`, and optional `temperature` to `speak`. English/Kokoro behavior stays unchanged. Chinese requests on Apple Silicon MLX routes must remain speaker-capable and become deterministic by default:

- `language="zh", voice="Vivian"` must route to a Qwen CustomVoice model that actually supports named speakers
- `language="zh"` with omitted `voice` must still resolve to a deterministic Chinese speaker instead of backend drift
- omitted MLX `temperature` must resolve to deterministic `0.0`
- explicit MLX `temperature` must override that default when the caller intentionally opts into sampling

## Call Stack

1. MCP client calls public tool `speak` in `tts-mcp/src/tts_mcp/server.py`.
2. `speak` publishes schema metadata that includes `language`, `voice`, and `temperature`.
3. `speak` canonicalizes the public `language` hint exactly as today.
4. `speak` builds `run_kwargs` with required inputs plus optional internal `language_code`, optional public `voice`, and optional public `temperature` when provided.
5. `runner.run_speak` selects the backend.
6. On Apple Silicon MLX routes, `runner.run_speak` passes both `language_code` and the requested `voice` into `routing_policy.resolve_mlx_request`, while separately resolving the effective temperature from the explicit override or the MCP-owned default.
7. `routing_policy.resolve_mlx_request` chooses the MLX model variant:
   - English default remains `mlx-community/Kokoro-82M-bf16`
   - Chinese auto-route chooses a speaker-capable Qwen CustomVoice model
   - explicit MLX pins remain authoritative, but incompatible named-speaker requests are detected
8. `routing_policy.resolve_mlx_request` also computes the effective MLX voice:
   - if the caller supplied a Chinese named `voice`, preserve it
   - if the caller omitted `voice` on the Chinese auto-route, inject a deterministic default Chinese speaker
   - if the selected MLX model does not support predefined speakers and a named Chinese `voice` is requested, return a clear error path instead of silent drift
9. `backend_commands.build_mlx_command` builds the MLX CLI command using the resolved model id, resolved language code, resolved effective voice, and resolved effective temperature.
10. The MLX subprocess now receives an explicit `--voice <speaker>` for both:
   - Chinese named-voice calls
   - Chinese no-voice calls on the deterministic default route
11. The MLX subprocess also receives an explicit `--temperature <value>`:
   - omitted-temperature MLX calls receive `--temperature 0.0`
   - explicit MLX overrides preserve the caller's requested value
12. Existing backend-specific behavior remains authoritative:
   - English/Kokoro route can use Kokoro voices such as `af_heart`
   - Chinese speaker examples shown in the public schema match the actual installed CustomVoice runtime, for example `vivian`, `eric`, and `serena`
   - XTTS and Chatterbox reject named voices
   - non-MLX routes do not silently invent temperature behavior
13. MCP tool tests that need an in-process server session use `tts-mcp/tests/mcp_session_test_support.py` as the shared session bootstrap owner.
14. MLX/language tests that need fake runtime/numpy support use `tts-mcp/tests/mlx_language_test_support.py` as the shared owner.
15. `speak` returns the same structured success/failure result shape as today.

## Expected Outcome

- Agents can keep calling the public `speak(language, voice)` API without learning lower-layer model details.
- Agents can keep calling the public `speak(language, voice, temperature)` API without learning lower-layer model details.
- Chinese named voices become truthful because the route selects a speaker-capable model.
- Chinese omitted-voice calls become deterministic because MCP injects a default speaker instead of relying on backend drift.
- MLX omitted-temperature calls become deterministic because MCP injects a default `temperature=0.0` instead of relying on runtime sampling defaults.
- Incompatible pinned-model + named-voice combinations fail clearly instead of silently pretending to honor the request.
