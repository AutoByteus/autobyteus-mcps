# Requirements

## Status

- Current Status: `Design-ready`
- Ticket: `image-audio-video-support`
- Project: `autobyteus_mcps`
- Target package: `autobyteus-image-audio`
- Scope Classification: `Medium`

## Goal / Problem Statement

Add video generation support to the existing `autobyteus-image-audio` MCP/CLI package using the latest released `autobyteus` library video capability, while keeping the package identity stable. Users should discover video capability through clear public tool names and CLI commands, not through a project rename.

## Confirmed Requirement Decisions

- RD-001: Do not rename the project/package for this ticket.
- RD-002: Keep existing identity surfaces unchanged: package/folder `autobyteus-image-audio`, import path `image_audio_mcp`, console scripts `autobyteus-image-audio` and `autobyteus-image-audio-server`, repo wrapper `cli/autobyteus-image-audio`, default MCP server name `autobyteus-image-audio`, and existing `IMAGE_AUDIO_MCP_*` env vars.
- RD-003: New public MCP video tools must be named `generate_video` and `list_video_models`.
- RD-004: Existing MCP tool names must remain unchanged: `health_check`, `list_audio_models`, `list_image_models`, `generate_image`, `edit_image`, `generate_speech`, and `find_target_coordinates`.
- RD-005: The MCP schema must not expose internal Autobyteus video `session_id`; session lifecycle remains owned by the Autobyteus video client.

## Requirements

| Requirement ID | Requirement | Use Case IDs |
| --- | --- | --- |
| R-001 | Keep the existing `autobyteus-image-audio` package identity unchanged and add video capability through explicit public tool and CLI names. | UC-001, UC-002, UC-003, UC-004 |
| R-002 | Update all authoritative dependency sources for the package to use the latest video-capable `autobyteus` release, `autobyteus==1.4.4`. | UC-001, UC-002, UC-003, UC-004 |
| R-003 | Expose a video model listing service and MCP tool named `list_video_models`, analogous to `list_image_models` and `list_audio_models`. | UC-003 |
| R-004 | Expose a video generation service and MCP tool named `generate_video`. | UC-001, UC-002 |
| R-005 | `generate_video` must accept a required `prompt`, required `output_file_path`, optional `input_images`, optional `input_audios`, optional `input_videos`, and optional `generation_config`. | UC-001, UC-002, UC-004 |
| R-006 | Video generation must resolve the default model from `DEFAULT_VIDEO_GENERATION_MODEL`, falling back to `gemini-omni-app-rpa`. | UC-001, UC-002, UC-003, UC-004 |
| R-007 | Video generation must reuse existing service-layer path safety, media normalization, output download, and cleanup patterns. | UC-001, UC-002, UC-004 |
| R-008 | The CLI must expose `list-video-models` and `generate-video` commands using the existing JSON envelope, repeatable media input flags, and repeatable `--config key=value` generation settings. | UC-004 |
| R-009 | `health_check` must include `default_video_generation_model` while preserving existing status/default model fields. | UC-003 |
| R-010 | Existing image generation, image editing, speech generation, coordinate finding, model listing, health-check behavior, command names, and tool names must keep working. | UC-005 |
| R-011 | README, DESIGN, and root project listing docs must describe video generation accurately while preserving stable launch/config examples. | UC-005 |
| R-012 | Add focused local tests and optional remote integration coverage for the video MCP/CLI/service surface. | UC-001, UC-002, UC-003, UC-004, UC-005 |

## In-Scope Use Cases

| Use Case ID | Name | Description | Primary Actor / Caller |
| --- | --- | --- | --- |
| UC-001 | MCP prompt-only video generation | MCP client calls `generate_video` with prompt and output path; the package saves the generated video locally and returns the path/model. | MCP client |
| UC-002 | MCP video generation with media inputs | MCP client calls `generate_video` with optional image, audio, and/or video references; the service normalizes safe local paths/URLs/data URIs and passes them to the Autobyteus video client. | MCP client |
| UC-003 | Video model/default discovery | MCP client or CLI lists video models and checks default model status through `list_video_models` and `health_check`. | MCP client / CLI user |
| UC-004 | CLI video generation | User or agent invokes `autobyteus-image-audio generate-video` with prompt, output, repeatable media inputs, and optional config; stdout uses the existing JSON envelope. | CLI user / coding agent |
| UC-005 | Existing capability regression | Existing image/audio/grounding MCP tools and CLI commands continue to work with unchanged names and behavior. | Existing MCP/CLI users |

## Acceptance Criteria

| Acceptance Criteria ID | Acceptance Criteria | Requirement IDs | Validation Intent |
| --- | --- | --- | --- |
| AC-001 | `pyproject.toml`, `requirements.txt`, and `uv.lock` all resolve `autobyteus==1.4.4`; `uv --directory autobyteus-image-audio run --frozen ...` remains usable. | R-002 | Dependency/frozen-runtime check |
| AC-002 | MCP `list_tools` returns existing public tools plus exactly `list_video_models` and `generate_video`; hidden grounding internals remain unexposed. | R-001, R-003, R-004, R-010 | In-memory MCP local test |
| AC-003 | MCP `generate_video` schema exposes `prompt`, `output_file_path`, `input_images`, `input_audios`, `input_videos`, and `generation_config`, and does not expose `session_id`. | R-004, R-005, RD-005 | In-memory MCP schema test |
| AC-004 | `services.list_video_models()` initializes `VideoClientFactory` and returns video model metadata including model identifier, name, value, provider, runtime, parameter schema, and default config. | R-003, R-006 | Local service/MCP test with dummy model |
| AC-005 | `services.generate_video()` resolves `DEFAULT_VIDEO_GENERATION_MODEL`, normalizes image/audio/video inputs through the workspace-safe media path rules, calls `VideoClientFactory.create_video_client`, downloads the first returned video URL to the resolved output path, returns `file_path` and `model`, and cleans up the client. | R-004, R-005, R-006, R-007 | Local service test with fake video client/download |
| AC-006 | CLI `generate-video` parses repeatable `--input-image`, `--input-audio`, `--input-video`, repeatable `--config key=value`, and `--output-file-path`, delegates to `services.generate_video`, and prints the standard JSON success/failure envelope. | R-008 | Local CLI test |
| AC-007 | CLI `list-video-models` delegates to `services.list_video_models` and uses the standard JSON success envelope. | R-003, R-008 | Local CLI test |
| AC-008 | `health_check()` includes `default_video_generation_model` and keeps existing default model fields. | R-006, R-009, R-010 | Local service/MCP test |
| AC-009 | Existing local tests for image, edit, speech, coordinate finding, config parsing, speaker/voice mapping, and public tool inventory continue to pass after the video addition. | R-010, R-012 | Local pytest suite |
| AC-010 | Docs list `generate_video`, `list_video_models`, `DEFAULT_VIDEO_GENERATION_MODEL`, media input behavior, and the no-rename/stable launch path in the relevant package/root docs. | R-001, R-006, R-011 | Docs sync review |
| AC-011 | Optional remote integration test can exercise MCP `generate_video` against configured Autobyteus RPA LLM server credentials/host/model without running by default. | R-004, R-012 | Opt-in integration test gated by env |

## Requirement-To-Use-Case Coverage

| Requirement ID | Covered By Use Case IDs |
| --- | --- |
| R-001 | UC-001, UC-002, UC-003, UC-004 |
| R-002 | UC-001, UC-002, UC-003, UC-004 |
| R-003 | UC-003 |
| R-004 | UC-001, UC-002 |
| R-005 | UC-001, UC-002, UC-004 |
| R-006 | UC-001, UC-002, UC-003, UC-004 |
| R-007 | UC-001, UC-002, UC-004 |
| R-008 | UC-004 |
| R-009 | UC-003 |
| R-010 | UC-005 |
| R-011 | UC-005 |
| R-012 | UC-001, UC-002, UC-003, UC-004, UC-005 |

## Acceptance-Criteria-To-Scenario Intent

| Acceptance Criteria ID | Scenario Intent |
| --- | --- |
| AC-001 | Frozen dependency/runtime scenario |
| AC-002 | MCP public inventory regression scenario |
| AC-003 | MCP schema clarity and no-internal-session scenario |
| AC-004 | Video model discovery scenario |
| AC-005 | Video generation service primary path with all media input classes |
| AC-006 | CLI video generation parsing/dispatch scenario |
| AC-007 | CLI video model listing scenario |
| AC-008 | Health/default model scenario |
| AC-009 | Existing capability regression scenario |
| AC-010 | User-facing docs discoverability scenario |
| AC-011 | Optional real endpoint MCP video generation scenario |

## Constraints / Dependencies

- Dependency: `autobyteus==1.4.4` must be available to the package runtime.
- Runtime: video generation defaults to `gemini-omni-app-rpa` via Autobyteus RPA LLM server-backed video support.
- Environment: remote video generation requires `AUTOBYTEUS_API_KEY`, `AUTOBYTEUS_LLM_SERVER_HOSTS`, and an available logged-in/healthy backend browser state when using the RPA server.
- Test policy: real remote video generation remains opt-in because it is slow and quota/rate-limit sensitive.
- Architecture: MCP and CLI facades must continue to delegate provider/path/output work to `image_audio_mcp.services`.
- No project rename is in scope.

## Assumptions

- The latest required Autobyteus release is `1.4.4`, based on the sibling project release completed earlier on 2026-05-22.
- Keeping the project name stable is acceptable because the MCP and CLI tool names clearly communicate the new capability.
- The current flat `src/image_audio_mcp` layout remains appropriate for this additive peer modality.

## Open Questions / Risks

- OQ-001: Whether this repo has an external package publishing convention outside the visible files. Current evidence indicates no release/publication step is required for this package.
- Risk-001: Live video generation may fail for environment/browser-state reasons even if the MCP implementation is correct. Stage 7 should distinguish implementation failures from remote backend state failures.
