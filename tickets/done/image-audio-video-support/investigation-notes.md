# Investigation Notes

## Investigation Status

- Current Status: `Current`
- Scope Triage: `Medium`
- Triage Rationale: the change is additive but crosses the package dependency lock, service layer, MCP tool schema, CLI command surface, README/DESIGN docs, local tests, and optional real-provider integration tests.
- Investigation Goal: determine how to add video generation to the existing `autobyteus-image-audio` MCP/CLI package using the latest `autobyteus` library while deciding whether a package rename is warranted.
- Primary Questions To Resolve:
  - Should this package be renamed now that it will expose video generation?
  - Which current layer owns provider calls, path normalization, model defaults, and result downloads?
  - What video API surface does the latest `autobyteus` library provide?
  - Which files and tests need to change without breaking existing image/audio/grounding behavior?

## Source Log

| Date | Source Type | Exact Source / Query / Command | Why Consulted | Relevant Findings | Follow-Up Needed |
| --- | --- | --- | --- | --- | --- |
| 2026-05-22 | Command | `git fetch origin --prune --tags` before ticket worktree creation | Ensure bootstrap uses latest tracked base | `origin/main` advanced to `9b73e58`; ticket branch/worktree created from that commit | No |
| 2026-05-22 | Code | `autobyteus-image-audio/src/image_audio_mcp/server.py` | Inspect MCP entrypoint and public tool registration | `create_server()` is a thin FastMCP facade. It registers `health_check`, model listing, image generation/edit, speech, and coordinate tools, then delegates to `services`. No video tool is present. Server identity/env names are `autobyteus-image-audio` and `IMAGE_AUDIO_MCP_*`. | Yes |
| 2026-05-22 | Code | `autobyteus-image-audio/src/image_audio_mcp/services.py` | Inspect authoritative runtime boundary | Service layer owns workspace resolution, safe path handling, media normalization, default model env vars, provider client creation, result download, and cleanup. It imports image/audio factories only and has no video default, model listing, or generation path. | Yes |
| 2026-05-22 | Code | `autobyteus-image-audio/src/image_audio_mcp/cli.py` | Inspect CLI command surface and parsing patterns | CLI dispatch is task-oriented and delegates only to `services`. It has list-image/list-audio, generate-image, edit-image, generate-speech, and find-target-coordinates. It already has reusable helpers for output paths, image input flags, and repeatable `--config key=value`. | Yes |
| 2026-05-22 | Code | `cli/autobyteus-image-audio` | Check wrapper contract and rename blast radius | Repo wrapper hard-codes project directory `autobyteus-image-audio` and console script `autobyteus-image-audio`. Renaming would require wrapper migration and likely aliases. | No |
| 2026-05-22 | Code | `autobyteus-image-audio/pyproject.toml`, `requirements.txt`, `uv.lock` | Confirm dependency and package identity | Project name and scripts are `autobyteus-image-audio`; dependency is locked to `autobyteus==1.4.3` in all dependency sources. Video support requires bumping to `1.4.4`. | Yes |
| 2026-05-22 | Doc | `README.md` | Inspect workspace project naming and potential name collisions | Root README lists `autobyteus-image-audio` as internal image/TTS/UI-coordinate MCP and separately lists `video-audio-mcp` as an FFmpeg editing MCP. | Yes |
| 2026-05-22 | Doc | `autobyteus-image-audio/README.md` | Inspect user-facing docs and MCP config | README title/content says Image + Audio, lists only existing tools, documents `IMAGE_AUDIO_MCP_*` env vars, and includes Cursor/Claude config using `autobyteus-image-audio-server`. It already mentions Autobyteus remote credentials. | Yes |
| 2026-05-22 | Doc | `autobyteus-image-audio/DESIGN.md` | Inspect intended architecture and public contracts | Design says CLI and MCP are thin public surfaces sharing one authoritative implementation in `image_audio_mcp.services`. Public capability table currently lacks video. | Yes |
| 2026-05-22 | Code | `autobyteus-image-audio/tests/test_server_local.py` | Inspect MCP local coverage | Local MCP tests assert exact public tool set and only include dummy image model listing. Tool list must be updated and video model/tool tests added. | Yes |
| 2026-05-22 | Code | `autobyteus-image-audio/tests/test_services_local.py` | Inspect service coverage style | Existing tests use fake image/audio clients and fake downloads to verify safe paths, model env vars, output download, and cleanup. Video should follow the same pattern. | Yes |
| 2026-05-22 | Code | `autobyteus-image-audio/tests/test_cli_local.py` | Inspect CLI coverage style | Existing tests validate dispatch, JSON envelopes, repeatable flags, `--config` parsing, speaker mapping, and help text. Video CLI command should have comparable parsing/dispatch coverage. | Yes |
| 2026-05-22 | Code | `autobyteus-image-audio/tests/test_integration.py` | Inspect real-provider validation gate | Remote tests are opt-in with `RUN_REMOTE_IMAGE_AUDIO_TESTS=1` and currently validate only image and speech through MCP. Video should be added as an optional remote test path, likely gated by `DEFAULT_VIDEO_GENERATION_MODEL` to avoid accidental quota use. | Yes |
| 2026-05-22 | Code | `../autobyteus/autobyteus/multimedia/video/video_client_factory.py` | Verify latest Autobyteus video factory API | `VideoClientFactory` registers default `gemini-omni-app-rpa`, discovers remote models, resolves exact or unique unqualified identifiers, and creates video clients. | Yes |
| 2026-05-22 | Code | `../autobyteus/autobyteus/multimedia/video/api/autobyteus_video_client.py` | Verify video client method contract | `generate_video(prompt, input_image_urls=None, input_audio_urls=None, input_video_urls=None, generation_config=None)` returns `VideoGenerationResponse(video_urls=...)`. Session IDs are internal to the client. | Yes |
| 2026-05-22 | Code | `../autobyteus/autobyteus/tools/multimedia/video_tools.py` | Compare LLM tool schema and defaults | `GenerateVideoTool` uses `DEFAULT_VIDEO_GENERATION_MODEL`, default `gemini-omni-app-rpa`, accepts prompt/output and optional image/audio/video inputs, downloads the first returned video. The MCP can reuse the lower-level factory pattern rather than invoking this tool. | Yes |
| 2026-05-22 | Doc | `../autobyteus/docs/multimedia_tools.md` | Verify user-facing Autobyteus video naming/config | Documents `generate_video`, default model `gemini-omni-app-rpa`, env var `DEFAULT_VIDEO_GENERATION_MODEL`, media inputs, and host-qualified remote model identifiers. | Yes |
| 2026-05-22 | Command | `find . -maxdepth 4 -type f \( -iname '*release*' -o -iname '*publish*' -o -name '*.yml' -o -name '*.yaml' \)` | Look for package release workflow | No active release/publish workflow found in this repo; prior image-audio CLI ticket recorded no release/publication required. | No |

## Current Behavior / Codebase Findings

### Entrypoints And Boundaries

- Primary entrypoints:
  - MCP: `image_audio_mcp.server:create_server()`
  - MCP process launch: `image_audio_mcp.server:main`
  - CLI: `image_audio_mcp.cli:main`
  - Repo wrapper: `cli/autobyteus-image-audio`
- Execution boundaries:
  - MCP client -> `server.py` FastMCP tool -> `services.py` -> Autobyteus multimedia client -> download output file.
  - User/agent shell -> repo wrapper -> `uv --directory ... run --frozen autobyteus-image-audio ...` -> `cli.py` -> `services.py`.
- Owning subsystem / package:
  - `autobyteus-image-audio` is the owning package for generation/listing/coordinate tools.
  - `video-audio-mcp` is a separate FFmpeg editing package and should not be conflated with Autobyteus video generation.
- Folder / file placement observations:
  - New video support should stay inside `autobyteus-image-audio/src/image_audio_mcp/services.py`, `server.py`, and `cli.py`, matching existing image/audio placement.
  - Tests should stay in the existing package-local `tests/` files unless they become too large; no new subsystem folder is needed.

### Relevant Files / Symbols

| Path | Symbol / Area | Current Responsibility | Finding / Observation | Ownership / Placement Implication |
| --- | --- | --- | --- | --- |
| `autobyteus-image-audio/src/image_audio_mcp/server.py` | `DEFAULT_SERVER_NAME`, `ServerConfig`, `create_server` | MCP identity and public tool registration | Keeps the package name and env vars image/audio-specific; no video model/tool registration exists. | Add video tools here; keep identity stable unless a separate migration is planned. |
| `autobyteus-image-audio/src/image_audio_mcp/services.py` | service functions | Authoritative provider/path/download/cleanup logic | Has reusable media normalization and cleanup; only imports `ImageClientFactory`, `ImageModel`, `AudioClientFactory`, `AudioModel`. | Add `VideoClientFactory`, `VideoModel`, default model, `list_video_models`, and `generate_video` here. |
| `autobyteus-image-audio/src/image_audio_mcp/cli.py` | `_dispatch`, parser helpers | Task-oriented CLI facade | Existing helpers make `generate-video` straightforward; new audio/video input helpers are needed. | Add `list-video-models` and `generate-video` command without introducing raw MCP call mode. |
| `autobyteus-image-audio/pyproject.toml` | package metadata/deps/scripts | Package name, version, dependencies, scripts | Dependency is `autobyteus==1.4.3`; package/scripts are established. | Bump dependency to `1.4.4`; do not rename in this ticket. |
| `autobyteus-image-audio/requirements.txt` | dependency pin | Alternate install source | Pins `autobyteus==1.4.3`. | Bump to `1.4.4`. |
| `autobyteus-image-audio/uv.lock` | frozen runtime lock | Wrapper uses `uv --frozen` | Lock still contains `autobyteus==1.4.3`. | Update lock to `1.4.4` so wrapper and tests run frozen. |
| `cli/autobyteus-image-audio` | repo wrapper | Path-independent CLI UX | Hard-codes package dir and console script name. | Rename would require wrapper alias/migration; keeping the name avoids breaking current callers. |
| `autobyteus-image-audio/tests/test_server_local.py` | `test_tool_list_excludes_hidden_grounding_tools` | Public MCP inventory check | Exact tool set excludes video today. | Update exact set and add video schema/list tests. |
| `autobyteus-image-audio/tests/test_services_local.py` | fake clients/downloads | Local service contract tests | Clear pattern exists for media output services. | Add fake video response/client test with image/audio/video input normalization. |
| `autobyteus-image-audio/tests/test_cli_local.py` | CLI parser/dispatch tests | CLI UX regression coverage | Clear pattern exists for repeatable inputs and config. | Add `generate-video` parsing/dispatch and help assertions. |
| `autobyteus-image-audio/tests/test_integration.py` | remote MCP tests | Opt-in real provider validation | Existing gate covers image/speech only. | Add an opt-in video test with video-specific env skip behavior. |
| `../autobyteus/autobyteus/multimedia/video/video_client_factory.py` | `VideoClientFactory`, `VideoModel` | Video model registry and client factory | Provides default `gemini-omni-app-rpa` plus remote discovery. | MCP should list and instantiate video models through this factory. |
| `../autobyteus/autobyteus/multimedia/video/api/autobyteus_video_client.py` | `AutobyteusVideoClient.generate_video` | Server-backed video execution | Takes image/audio/video URL lists and `generation_config`; returns `video_urls`; manages `session_id` internally. | MCP service should not expose session IDs. |

## Runtime / Probe Findings

| Date | Method | Exact Command / Method | Observation | Implication |
| --- | --- | --- | --- | --- |
| 2026-05-22 | Code search | `rg -n "class VideoModel|VideoClientFactory|GenerateVideoTool|def generate_video|input_audio|input_video" ../autobyteus -S` | Latest sibling Autobyteus source contains complete video model factory, client, tool, tests, and docs. | The MCP can depend on released `autobyteus==1.4.4` and follow existing image/audio service patterns. |
| 2026-05-22 | Dependency inspection | `rg -n 'name = "autobyteus"|version = "1\.4\.' autobyteus-image-audio/uv.lock -C 2` | Lockfile and metadata still resolve Autobyteus `1.4.3`. | `uv.lock` must be updated or wrapper validation with `--frozen` will not use video-capable library. |
| 2026-05-22 | Release-path search | `find . -maxdepth 4 -type f \( -iname '*release*' -o -iname '*publish*' -o -name '*.yml' -o -name '*.yaml' \)` | No active release workflow found; prior ticket says no package release/publication was required. | Stage 10 likely records no release/publication unless implementation reveals a new package-publishing convention. |

## External Code / Dependency Findings

- Upstream/local dependency examined:
  - sibling project `../autobyteus` at latest local/released source after the video support ticket.
- Version / release:
  - `autobyteus==1.4.4` is the needed dependency version for `VideoClientFactory`, `VideoModel`, and `GenerateVideoTool`.
- Relevant behavior, contract, or constraint learned:
  - Default video model/env: `DEFAULT_VIDEO_GENERATION_MODEL`, default `gemini-omni-app-rpa`.
  - Video client API: `generate_video(prompt, input_image_urls, input_audio_urls, input_video_urls, generation_config)`.
  - Result shape: first generated URL is in `response.video_urls`.
  - Remote model identifiers may be host-qualified, e.g. `<model-name>@<host:port>`, and unqualified names resolve only if unique.
  - `session_id` exists inside `AutobyteusVideoClient`; it should not be part of the MCP tool schema.
- Confidence and freshness:
  - High; inspected local source and docs from the release completed earlier on 2026-05-22.

## Reproduction / Environment Setup

- No browser or provider runtime was required for Stage 1 analysis.
- No source code probes or temporary product code edits were needed.
- Ticket bootstrap worktree:
  - `/home/ryan-ai/SSD/autobyteus_org_workspace/autobyteus_mcps-image-audio-video-support`
- Ticket branch:
  - `codex/image-audio-video-support`

## Rename Analysis

Recommendation: do **not** rename the package, import path, console scripts, wrapper, or default MCP server name in this ticket.

Reasons:

- Existing public identity is encoded in several user-facing contracts: package name `autobyteus-image-audio`, import path `image_audio_mcp`, console scripts `autobyteus-image-audio` and `autobyteus-image-audio-server`, repo wrapper `cli/autobyteus-image-audio`, MCP config examples, and `IMAGE_AUDIO_MCP_*` env vars.
- The prior CLI ticket intentionally established the wrapper and task-oriented CLI contract. Renaming would turn an additive feature into a migration.
- A separate `video-audio-mcp` already exists for FFmpeg editing. Renaming this package to a video/audio-oriented name could create ambiguity between generation and editing packages.
- Video generation fits the same runtime category as the existing image/speech generation surfaces: Autobyteus multimedia model invocation plus local file output.
- The safest user-facing update is to keep the stable name and update descriptions/docs to say the package now exposes image, audio, and video generation capabilities. A future dedicated rename could be designed with aliases if product naming becomes important.

Optional future-compatible improvement:

- Consider accepting new alias env vars such as `AUTOBYTEUS_MULTIMEDIA_MCP_NAME` / `AUTOBYTEUS_MULTIMEDIA_MCP_INSTRUCTIONS` only if requirements explicitly want a naming refresh. The default should still preserve `IMAGE_AUDIO_MCP_*` to avoid breaking existing configs.

## Constraints

- `uv --frozen` is part of the wrapper contract; dependency and lockfile updates must remain consistent.
- Existing image/audio/grounding behavior must remain unchanged except for docs/tool inventory additions.
- The MCP server should not bypass `image_audio_mcp.services`; the service layer remains the authoritative owner for provider calls, safe paths, output downloads, and cleanup.
- The MCP video schema should not expose Autobyteus client internals such as video `session_id`.
- Real video generation can be slow and quota/rate-limit sensitive. Remote integration coverage should stay opt-in.
- The user explicitly prefers no backward-compatibility burden in source implementation in general, but this analysis finds that renaming is not needed to implement the feature. Keeping the existing package name is stability of the existing product identity, not a legacy branch in code behavior.

## Unknowns / Open Questions

- Unknown: whether the repository has an unpublished external package distribution convention not visible in the files.
  - Why it matters: it affects Stage 10 release/publication.
  - Planned follow-up: re-check project docs and git tags during Stage 10; current evidence says no release is required.
- Unknown: whether live video integration should be run during this MCP ticket or left as optional due quota.
  - Why it matters: video generation can be slow/rate-limited, but we already have a working Docker endpoint from the Autobyteus ticket.
  - Planned follow-up: Stage 7 should include local executable tests; optional remote MCP video test can be run when credentials/server are available.

## Implications

### Requirements Implications

- Requirements should explicitly call this an additive video-generation feature inside the existing package identity.
- Requirements should define the MCP tool schema as:
  - `generate_video(prompt, output_file_path, input_images=None, input_audios=None, input_videos=None, generation_config=None)`
  - `list_video_models()`
- Requirements should include `health_check` returning `default_video_generation_model`.
- Requirements should require dependency bump from `autobyteus==1.4.3` to `autobyteus==1.4.4` in all authoritative dependency files.

### Design Implications

- For a `Medium` scope ticket, create a proposed design rather than only a small solution sketch.
- Keep the spine:
  - MCP/CLI facade -> `image_audio_mcp.services` -> `VideoClientFactory` -> video client -> `download_file_from_url`.
- Add video as a peer to image/audio, not as a special case inside image or speech code.
- Prefer list inputs on the MCP/service surface because existing MCP `generate_image` already uses `Optional[List[str]]`; the CLI can expose repeatable `--input-image`, `--input-audio`, and `--input-video` flags.

### Implementation / Placement Implications

- Expected source/doc changes:
  - `autobyteus-image-audio/pyproject.toml`
  - `autobyteus-image-audio/requirements.txt`
  - `autobyteus-image-audio/uv.lock`
  - `autobyteus-image-audio/src/image_audio_mcp/services.py`
  - `autobyteus-image-audio/src/image_audio_mcp/server.py`
  - `autobyteus-image-audio/src/image_audio_mcp/cli.py`
  - `autobyteus-image-audio/tests/test_services_local.py`
  - `autobyteus-image-audio/tests/test_server_local.py`
  - `autobyteus-image-audio/tests/test_cli_local.py`
  - `autobyteus-image-audio/tests/test_integration.py`
  - `autobyteus-image-audio/README.md`
  - `autobyteus-image-audio/DESIGN.md`
  - root `README.md`
- No source implementation should begin until Stage 5 is complete and Stage 6 unlocks code edits.

## Re-Entry Additions

Append new dated evidence here when later stages reopen investigation.
