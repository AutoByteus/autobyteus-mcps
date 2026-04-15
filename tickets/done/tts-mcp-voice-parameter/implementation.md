# Implementation

## Scope

Small fix to make MLX-backed speech deterministic by default and keep Chinese voice guidance truthful. The public `speak(language, voice)` API remains concise, but it now also needs an optional `temperature` override while defaulting omitted MLX temperature to `0.0`.

## Design Basis

- Keep the public MCP API concise:
  - public field remains `language`
  - public field `voice` remains optional
  - add public field `temperature` as an optional MLX sampling override
- Keep the English/Kokoro route unchanged.
- Change the Chinese MLX routing behavior:
  - when the route is Chinese and MCP is choosing the MLX model automatically, choose the Qwen `CustomVoice` model variant instead of the current Qwen `Base` model
  - when the route is Chinese and the caller omits `voice`, inject a deterministic default Chinese speaker instead of relying on backend drift
  - when the route is Chinese and the caller provides a named `voice`, require a speaker-capable model
- Add deterministic MLX sampling ownership:
  - when the caller omits `temperature`, use an MCP-owned MLX default of `0.0`
  - when the caller provides `temperature`, pass it through to the MLX command path
- Add a hard compatibility check:
  - if the selected/pinned MLX model does not expose predefined speakers and the caller asks for a named Chinese `voice`, return a clear validation/config error instead of silently generating audio on an incompatible model
- Keep lower-layer naming internal:
  - internal runner/routing APIs may continue to use `language_code`
- Keep schema/docs honest:
  - continue to show curated Chinese speaker examples, but only from the actual supported CustomVoice runtime set such as `vivian`, `eric`, and `serena`
  - clarify that named Chinese speakers are tied to the speaker-capable Qwen route, not every Qwen model variant

## Concrete Implementation Shape

- `tts-mcp/src/tts_mcp/config.py`
  - add a Qwen `CustomVoice` MLX preset/model id
  - add a deterministic Chinese default voice constant for the MLX CustomVoice route
  - add an MLX default temperature setting with a deterministic default of `0.0`
- `tts-mcp/src/tts_mcp/routing_policy.py`
  - extend MLX request resolution so Chinese auto-routing can choose the CustomVoice model
  - compute the effective Chinese default voice when `voice` is omitted on the auto-routed Chinese path
  - expose enough routing result data to validate whether the selected model supports predefined speakers
- `tts-mcp/src/tts_mcp/runner.py`
  - pass requested `voice` into MLX request resolution
  - accept optional public `temperature` and pass it toward the MLX command path
  - fail clearly when a named Chinese `voice` is requested against an incompatible pinned model
- `tts-mcp/src/tts_mcp/backend_commands.py`
  - build the MLX command from the resolved effective voice so Chinese no-voice calls still emit a deterministic `--voice <default>`
  - emit `--temperature <value>` for MLX using the explicit override or deterministic default
- `tts-mcp/src/tts_mcp/server.py`
  - expose public `temperature` with truthful MLX-specific wording
  - replace unsupported Chinese speaker examples such as `Ethan` with actual supported examples from the installed CustomVoice runtime

## Files Expected To Change

- `tts-mcp/src/tts_mcp/config.py`
- `tts-mcp/src/tts_mcp/routing_policy.py`
- `tts-mcp/src/tts_mcp/runner.py`
- `tts-mcp/src/tts_mcp/backend_commands.py`
- `tts-mcp/src/tts_mcp/server.py`
- `tts-mcp/tests/test_config.py`
- `tts-mcp/tests/test_speak_temperature.py`
- `tts-mcp/tests/test_runner.py`
- `tts-mcp/tests/test_mlx_language_chinese.py`
- `tts-mcp/tests/test_mlx_language_english.py`
- `tts-mcp/tests/test_speak_voice.py`
- `tts-mcp/tests/test_real_mcp_speak_tool_chinese_qwen.py`
- `tts-mcp/README.md`
- `tickets/in-progress/tts-mcp-voice-parameter/api-e2e-testing.md`

## Validation Plan

- Focused unit/integration regression:
  - `cd tts-mcp && uv run --extra test python -m pytest -q tests/test_config.py tests/test_server.py tests/test_speak_voice.py tests/test_mlx_language_chinese.py tests/test_mlx_language_english.py tests/test_runner.py`
- New behavior checks:
  - Chinese auto-route uses the speaker-capable CustomVoice model
  - Chinese no-voice path emits a deterministic default voice
  - MLX routes emit deterministic default `--temperature 0.0` when the caller omits `temperature`
  - explicit MLX `temperature` overrides are forwarded to the command path
  - Chinese named-voice requests fail against incompatible pinned Qwen Base model selections
- Real MCP validation:
  - `TTS_MCP_RUN_REAL_MCP_SPEAK=1 uv run --extra test python -m pytest -q tests/test_real_mcp_speak_tool_chinese_qwen.py tests/test_real_mcp_speak_tool_english.py`
  - direct repeated-output probe using the installed MLX runtime with `temperature=0` to confirm stable repeated output for a supported Chinese speaker id
