# Investigation Notes

## Investigation Status

- Current Status: `Current`
- Scope Triage: `Small`
- Triage Rationale: The public `language`/`voice` API is already in place, but the user reported a new Chinese speaker-stability bug that appears limited to the Apple Silicon Qwen route and may stem from the routed MLX model rather than broad architecture changes.
- Investigation Goal: Reproduce the reported Chinese speaker drift, determine whether omitted and explicit `voice` calls are both unstable, confirm which Qwen model variant actually supports named speakers in the routed path, and identify which runtime control makes repeated outputs deterministic.
- Primary Questions To Resolve:
  - Does the current Chinese auto-route land on a Qwen model that truly supports named speakers?
  - When the caller sends `voice="Vivian"` or `voice="Ethan"`, is the model actually anchoring to those speakers or ignoring the parameter?
  - If `voice` is omitted, should MCP choose a deterministic default speaker instead of relying on backend drift?
  - Does deterministic speaker stability require a sampling control such as `temperature=0`, and if so can MCP own that default?
  - Which executable validations are missing to prevent false positives around speaker stability?

## Source Log

| Date | Source Type | Exact Source / Query / Command | Why Consulted | Relevant Findings | Follow-Up Needed |
| --- | --- | --- | --- | --- | --- |
| 2026-04-15 | Code | `tts-mcp/src/tts_mcp/server.py` | Inspect current public `speak` schema | `speak` currently exposes `text`, `output_path`, `play`, and public language routing, but initially used the longer field name `language_code` and had no public `voice` field | Yes |
| 2026-04-15 | Code | `tts-mcp/src/tts_mcp/backend_commands.py` | Verify lower-layer MLX voice support | MLX command builder already accepts `voice` and appends `--voice` when set | No |
| 2026-04-15 | Code | `tts-mcp/src/tts_mcp/config.py` | Confirm configuration support | `MLX_TTS_DEFAULT_VOICE` already exists in settings | No |
| 2026-04-15 | Doc | `tts-mcp/README.md` | Check public docs and supported examples | README documents `MLX_TTS_DEFAULT_VOICE`; current tool section does not document a per-call `voice` input | Yes |
| 2026-04-15 | Command | ``/Users/normy/autobyteus_org/autobyteus_mcps/tts-mcp/.venv-mlx/bin/mlx_audio.tts.generate --help | rg -n "Voice/speaker|Qwen3-TTS|--voice"`` | Confirm installed runtime examples | Installed MLX command advertises `--voice` and example Qwen voices `Chelsie`, `Ethan`, and `Vivian` | No |
| 2026-04-15 | Code | `tts-mcp/tests/test_runner.py` | Check backend-specific constraints | XTTS rejects named `voice`; Chatterbox also rejects named `voice`; Kokoro and MLX handle voice selection differently | No |
| 2026-04-15 | Code Review | `tickets/in-progress/tts-mcp-voice-parameter/code-review.md` round 1 findings | Diagnose failed Stage 8 gate | Review found unfinished support extraction: `mcp_session_test_support.py` and `mlx_language_test_support.py` exist, but related tests still keep duplicated local helpers | Yes |
| 2026-04-15 | Command | real `run_speak(..., language_code="en", voice=...)` probe | Verify English route voice reality instead of inferring from schema text | Internal `run_speak(language_code="en")` stays on MLX Kokoro; tested `voice="af_heart"` succeeds, while `voice="Vivian"` fails on that English route | Yes |
| 2026-04-15 | Code | `tts-mcp/tests/test_real_mcp_speak_tool_english.py`, `tts-mcp/tests/test_real_mcp_speak_tool_chinese_qwen.py` | Check current Stage 7 real MCP coverage | Existing real MCP tool tests prove English route without voice and Chinese route with public `language="zh"` but initially without `voice`; explicit language+voice scenarios were missing | Yes |
| 2026-04-15 | User Requirement | user direction to rename the public field to `language` | Improve API intuition and reduce agent friction | Public field should be `language`, not `language_code`, while internal runner/routing names can remain unchanged | Yes |
| 2026-04-15 | Probe | live `tts/speak` repeated Chinese calls with omitted `voice`, `voice="Vivian"`, and `voice="Ethan"` to `/private/tmp/tts-qwen-stability/*.wav` | Reproduce the user's report through the real app-facing MCP tool | All calls returned `ok=true`, but repeated files differ in size/duration and required deeper speaker-identity investigation rather than simple WAV-exists checks | Yes |
| 2026-04-15 | Probe | Qwen base-model embedding analysis over `/private/tmp/tts-qwen-stability/*.wav` using `model.extract_speaker_embedding(...)` | Check whether repeated explicit-voice outputs cluster as the same speaker | The routed `mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16` model loads with `supported_speakers=[]`; cross-sample cosine similarity does not show clear named-speaker separation, consistent with explicit voices not being anchored by this model | Yes |
| 2026-04-15 | Web | `https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16/raw/main/config.json`, `https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16/raw/main/config.json` | Verify model metadata at the source instead of trusting CLI help text | The routed Base model has `talker_config.spk_id = {}`; the CustomVoice model exists and carries `talker_config.spk_id` entries for named speakers including `serena`, `vivian`, `uncle_fu`, `ryan`, `aiden`, `eric`, and `dylan` | Yes |
| 2026-04-15 | Doc | `mlx_audio/tts/models/qwen3_tts/README.md` in the installed runtime package | Check upstream package expectations for Qwen variants | Installed runtime docs differentiate Base, CustomVoice, and VoiceDesign variants and show named-speaker usage on the CustomVoice model, not only on the routed Base model | Yes |
| 2026-04-15 | Probe | `/Users/normy/autobyteus_org/autobyteus_mcps/tts-mcp/.venv-mlx/bin/mlx_audio.tts.generate --model mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16 --text '你好，这是 Ethan 的中文语音一致性测试。' --voice Ethan --lang_code zh ...` | Verify whether the advertised `Ethan` example actually exists on the routed CustomVoice model | The installed CustomVoice model rejects `Ethan` and reports the actual supported speakers as `serena`, `vivian`, `uncle_fu`, `ryan`, `aiden`, `ono_anna`, `sohee`, `eric`, and `dylan` | Yes |
| 2026-04-15 | Code | `tts-mcp/.venv-mlx/lib/python3.13/site-packages/mlx_audio/tts/generate.py`, `tts-mcp/.venv-mlx/lib/python3.13/site-packages/mlx_audio/tts/models/qwen3_tts/qwen3_tts.py` | Determine which runtime knobs control repeatability | The installed MLX runtime exposes `temperature`, `top_p`, and `top_k`; the Qwen sampler switches to greedy decoding when `temperature <= 0`; no seed control was found in the installed TTS runtime | Yes |
| 2026-04-15 | Probe | repeated `mlx_audio.tts.generate` with `voice=eric`, identical Chinese text, `temperature=0`, `top_p=1.0`, `top_k=0`, then `shasum -a 256` over the outputs | Verify whether greedy decoding is strong enough to remove observable run-to-run drift | Three repeated Chinese CustomVoice outputs were bit-identical under `temperature=0` | Yes |

## Current Behavior / Codebase Findings

### Entrypoints And Boundaries

- Primary entrypoint: public MCP tool `speak` in `tts-mcp/src/tts_mcp/server.py`
- Execution boundary: `server.py` delegates to `runner.run_speak`, which selects backend and builds the backend command
- Owning subsystem: `tts-mcp`
- Folder / file placement observations: the public boundary is correctly centralized in `server.py`; exposing `voice` belongs there, not in backend-specific files

### Relevant Files / Symbols

| Path | Symbol / Area | Current Responsibility | Finding / Observation | Ownership / Placement Implication |
| --- | --- | --- | --- | --- |
| `tts-mcp/src/tts_mcp/server.py` | `speak` | Public MCP contract | Public field name should be concise (`language`) and expose per-call `voice`; if MCP adopts temperature control, it must also surface a truthful optional `temperature` boundary | Keep public contract ownership here |
| `tts-mcp/src/tts_mcp/backend_commands.py` | `build_mlx_command` | MLX CLI invocation | Already appends `--voice` when a voice is provided, but does not currently force a deterministic MLX temperature | Temperature propagation belongs here |
| `tts-mcp/src/tts_mcp/config.py` | `mlx_default_voice` | Env default voice support | Existing default voice can remain as fallback when per-call `voice` is omitted; there is not yet an MCP-owned default MLX temperature setting | Add a configuration owner for deterministic default temperature if the contract adopts it |
| `tts-mcp/src/tts_mcp/routing_policy.py` | `resolve_mlx_request` | Apple Silicon MLX model selection | English defaults to Kokoro MLX; Chinese auto-selects `mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16` when no explicit MLX preset/model is pinned | The current Chinese route does not choose the Qwen CustomVoice model needed for anchored named speakers |
| `tts-mcp/tests/test_runner.py` | backend behavior tests | Runner/backend invariants | Existing tests already prove XTTS rejects named voice, but after the branch split it still duplicates fake-runtime scaffolding that now belongs in `mlx_language_test_support.py` | Reuse shared support and delete duplicate local scaffolding |
| `tts-mcp/tests/mcp_session_test_support.py` | shared MCP session helper | Shared test session bootstrap | Correct new owner for `_run_with_session` | Reuse from all directly impacted MCP tool tests |
| `tts-mcp/tests/test_real_linux_kokoro_chinese.py` | real Linux Kokoro Chinese test | Real MCP tool integration coverage | Still carries its own `_run_with_session`, bypassing the new shared support owner | Move to the shared helper |
| `tts-mcp/tests/test_real_mcp_speak_tool_english.py` | real Apple Silicon English MCP tool test | Real MCP tool validation | Does not currently prove explicit English `voice` selection | Add an explicit English+voice scenario |
| `tts-mcp/tests/test_real_mcp_speak_tool_chinese_qwen.py` | real Apple Silicon Chinese MCP tool test | Real MCP tool validation | Current tests only prove valid WAV generation; they do not prove speaker stability or that explicit named voices are honored by the routed model | Add speaker-capability and stability validation |

### Runtime / Probe Findings

| Date | Method (`Repro`/`Trace`/`Probe`/`Script`/`Test`/`Setup`) | Exact Command / Method | Observation | Implication |
| --- | --- | --- | --- | --- |
| 2026-04-15 | Probe | Live `tts/speak` generated `/private/tmp/tts-qwen-stability/no_voice_1.wav`, `no_voice_2.wav`, `vivian_1.wav`, `vivian_2.wav`, `ethan_1.wav` with repeated Chinese text | All five calls succeeded, but repeated files vary materially in size and duration (`6.32s` to `7.52s`) | Existing Stage 7 evidence is insufficient because success + valid WAV does not prove speaker identity stability |
| 2026-04-15 | Script | Load `mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16` and inspect `model.supported_speakers` | The routed Base model reports `supported_speakers=[]` | Explicit named voices on the current Chinese route are not backed by a predefined speaker inventory |
| 2026-04-15 | Script | Speaker-embedding cosine comparison using the Qwen Base model's `extract_speaker_embedding(...)` on repeated generated WAVs | Repeated `Vivian` outputs do not clearly cluster apart from omitted-voice or `Ethan` outputs | The current routed model likely ignores or weakly conditions on the named `voice` input for this path |
| 2026-04-15 | Web | Read Hugging Face `config.json` for Base and CustomVoice variants | Base has empty `talker_config.spk_id`, while CustomVoice has nine speaker IDs including the expected Chinese speaker names | A fix should route named-speaker Chinese calls to the CustomVoice model instead of the current Base model |
| 2026-04-15 | Probe | CustomVoice speaker-list rejection output for `voice=Ethan` | The real supported speaker list on this runtime does not include `Ethan` or `Chelsie`; supported ids include `vivian` and `eric` | MCP schema examples must stop advertising unsupported Chinese names |
| 2026-04-15 | Code + Probe | Inspect Qwen sampling path and generate repeated `voice=eric` outputs with `temperature=0` | Qwen uses greedy decoding when `temperature <= 0`, and repeated outputs with the same text/voice become bit-identical under that setting | Deterministic behavior can be owned by MCP through temperature defaulting without requiring a seed feature |

## Constraints

- Technical constraints:
  - Voice selection is not uniformly supported across all backends.
  - The schema must not imply that every backend accepts the same named voices.
  - Stage 8 requires the new shared test-support owners to be the only owners for duplicated setup logic in the directly impacted test slice.
  - The tested English Apple Silicon path uses Kokoro-style voices rather than the Qwen names advertised by the installed runtime help for Qwen.
  - The current Chinese auto-route uses Qwen Base, and that routed model has no predefined speaker table.
- Environment constraints:
  - Dynamic runtime voice enumeration is out of scope for this change.
- Third-party / API constraints:
  - Installed MLX runtime help advertises Qwen voice examples, but that help text is not sufficient proof that the currently routed model variant supports named speakers.

## Implications

### Requirements Implications

- The public field should be `language`, not `language_code`, because the accepted values include aliases such as `english`, `mandarin`, and `zh-cn`, not only strict codes.
- The new public `voice` field should be optional and examples-based, not a strict enum.
- The branch must also finish the shared test-support extraction already started here; otherwise the code-review gate fails on ownership and cleanup quality.
- Stage 7 must explicitly cover executable English+voice and Chinese+voice tool scenarios rather than inferring that voice works from unit-level delegation tests.
- Stage 7 must now also prove speaker-capability and deterministic default behavior for the Chinese route instead of treating any valid WAV as success.

### Design Implications

- The cleanest design is to rename the public routing field to `language`, canonicalize it at the public boundary, and pass the resolved value down as the existing internal `language_code`.
- The cleanest design is to expose `voice` only at the public MCP boundary and pass it through unchanged to `run_speak`.
- Schema metadata should distinguish tested route-specific examples:
  - English/Kokoro example: `af_heart`
  - Chinese/Qwen examples: `Chelsie`, `Ethan`, `Vivian`
- The schema must still note that unsupported backends may reject named voices.
- The cleanest test-support design is to keep one owner for MCP session bootstrap and one owner for fake MLX runtime scaffolding across the touched test slice.
- For Chinese named-speaker support, the route likely needs to select Qwen CustomVoice rather than the current Qwen Base model.
- If `voice` is omitted on the Chinese named-speaker route, MCP likely needs to provide a deterministic default voice instead of relying on the backend's unconstrained default.

### Implementation / Placement Implications

- Update `server.py` to add an annotated `voice` parameter.
- Add focused MCP-boundary tests in a dedicated voice-specific test file.
- Reuse `mcp_session_test_support.py` from all directly impacted MCP-tool tests.
- Reuse `mlx_language_test_support.py` from the MLX/language tests and remove duplicate local support bodies from `test_runner.py`.
- Update README tool docs to mention the new optional `voice` input and its backend caveat.
- Add durable Stage 7 real MCP scenarios for explicit English+voice and Chinese+voice `speak` calls on Apple Silicon using the public `language` field.
- Extend routing/config so the Chinese Qwen path can select a speaker-capable model variant when named voices are requested.
- Add validation that fails if the routed Chinese model reports no supported speakers while the schema/docs claim named speaker examples.

## Re-Entry Additions

### 2026-04-15 Re-Entry Update

- Trigger: user reported that repeated Chinese `speak` calls drift between male and female voices, even in cases where agents attempted to pass a named `voice`.
- New evidence:
  - Live repeated MCP Chinese generations succeeded but produced materially different WAVs.
  - The routed `mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16` model reports `supported_speakers=[]`.
  - Hugging Face model metadata shows that named speaker IDs live on the `CustomVoice` variant, not on the current routed `Base` variant.
- Updated implications:
- The current Chinese route is not sufficient for truthful named-speaker support.
- A real fix likely needs routing/config changes plus stronger Stage 7 validation around deterministic speaker behavior.
- The current public Chinese speaker examples are not truthful for the installed CustomVoice runtime because `Ethan` and `Chelsie` are not actually supported there.
- Deterministic repeated output is available through `temperature=0`, and the installed runtime exposes no seed control, so MCP should treat temperature as the primary stability knob.
