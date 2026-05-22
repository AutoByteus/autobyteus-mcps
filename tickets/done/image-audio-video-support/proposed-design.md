# Proposed Design Document

## Design Version

- Current Version: `v1`

## Revision History

| Version | Trigger | Summary Of Changes | Related Review Round |
| --- | --- | --- | --- |
| v1 | Initial draft | Add video generation/model listing to the existing image/audio MCP package without renaming the package. | 1 |

## Artifact Basis

- Investigation Notes: `tickets/in-progress/image-audio-video-support/investigation-notes.md`
- Requirements: `tickets/in-progress/image-audio-video-support/requirements.md`
- Requirements Status: `Design-ready`
- Shared Design Principles: `software-engineering-workflow-skill/shared/design-principles.md`
- Common Design Practices: `software-engineering-workflow-skill/shared/common-design-practices.md`

## Summary

Extend the existing `autobyteus-image-audio` package with video as a peer multimedia modality. The public identity stays stable; the new discoverable surface is the explicit MCP tools `generate_video` and `list_video_models`, plus CLI commands `generate-video` and `list-video-models`.

The governing design keeps the existing spine intact:

```text
MCP/CLI facade -> image_audio_mcp.services -> Autobyteus multimedia factory/client -> local downloaded output
```

No new package, import path, wrapper, or compatibility layer is introduced.

## Goal / Intended Change

Add video model discovery and video generation with text/image/audio/video inputs, backed by `autobyteus==1.4.4`, while preserving existing image, edit, speech, coordinate, model listing, and health-check behavior.

## Legacy Removal Policy

- Policy: `No backward compatibility; remove legacy code paths.`
- In-scope removal/decommission: none. This is an additive peer capability, not a replacement of an old video flow.
- Explicit rejection: do not add a renamed package alias or compatibility wrapper such as `autobyteus-multimedia`; stable existing identity remains the one canonical identity.

## Requirements And Use Cases

| Requirement ID | Description | Acceptance Criteria ID(s) | Acceptance Criteria Summary | Use Case IDs |
| --- | --- | --- | --- | --- |
| R-001 | Keep package identity unchanged; add video through explicit names. | AC-002, AC-010 | Stable identity, clear public tool inventory/docs. | UC-001, UC-002, UC-003, UC-004 |
| R-002 | Use `autobyteus==1.4.4`. | AC-001 | Dependency and frozen lock updated. | UC-001, UC-002, UC-003, UC-004 |
| R-003 | Expose `list_video_models`. | AC-004, AC-007 | Video model metadata through service/MCP/CLI. | UC-003 |
| R-004 | Expose `generate_video`. | AC-002, AC-003, AC-005, AC-011 | MCP video generation tool. | UC-001, UC-002 |
| R-005 | Accept prompt/output/media/config arguments. | AC-003, AC-005, AC-006 | Schema and CLI parsing include all video inputs. | UC-001, UC-002, UC-004 |
| R-006 | Resolve default video model env. | AC-004, AC-005, AC-008 | `DEFAULT_VIDEO_GENERATION_MODEL` or `gemini-omni-app-rpa`. | UC-001, UC-002, UC-003, UC-004 |
| R-007 | Reuse service path/media/download/cleanup patterns. | AC-005 | Safe file and cleanup behavior. | UC-001, UC-002, UC-004 |
| R-008 | Add CLI video commands. | AC-006, AC-007 | JSON-envelope CLI UX. | UC-004 |
| R-009 | Add video default to health check. | AC-008 | Health default includes video. | UC-003 |
| R-010 | Preserve existing behavior. | AC-002, AC-009 | Regression tests pass. | UC-005 |
| R-011 | Update docs. | AC-010 | README/DESIGN/root docs updated. | UC-005 |
| R-012 | Add tests. | AC-001 through AC-011 | Local and optional remote validation. | UC-001 through UC-005 |

## Current-State Read

| Area | Findings | Evidence | Open Unknowns |
| --- | --- | --- | --- |
| Entrypoints / Current Spine | MCP and CLI are thin facades over `image_audio_mcp.services`. | `server.py:create_server`, `cli.py:_dispatch`, `services.py` | None |
| Current Ownership Boundaries | `services.py` owns provider calls, path safety, media normalization, output download, and cleanup. | `services.generate_image`, `services.edit_image`, `services.generate_speech` | None |
| Current Coupling / Fragmentation | Model-list metadata serialization is duplicated between image and audio; adding video would make it triplicate. | `services.list_audio_models`, `services.list_image_models` | Whether to extract a private serializer now |
| Existing Constraints | Repo wrapper uses `uv --frozen`; dependency lock must be updated. | `cli/autobyteus-image-audio`, `uv.lock` | None |
| Relevant Files | Package docs, service/server/CLI, tests, dependency files. | Investigation notes source log | None |

## Current State (As-Is)

```text
MCP generate_image/edit_image/generate_speech/list_* -> server.py -> services.py -> Image/Audio factories -> download output
CLI generate-image/edit-image/generate-speech/list-* -> cli.py -> services.py -> Image/Audio factories -> download output
```

There is no video model listing, video default model, video generation service, video MCP tool, or video CLI command.

## Data-Flow Spine Inventory

| Spine ID | Scope | Start | End | Owning Node / Governing Owner | Why It Matters |
| --- | --- | --- | --- | --- | --- |
| DS-001 | Primary End-to-End | MCP client calls `generate_video` | Local video file path returned | `image_audio_mcp.services.generate_video` | Main MCP user flow for prompt-only and media-conditioned video generation. |
| DS-002 | Primary End-to-End | CLI user calls `generate-video` | JSON envelope with local video file path | `image_audio_mcp.cli` delegates to `services.generate_video` | Agent/user command-line flow must stay ergonomic and consistent. |
| DS-003 | Bounded Local | Model/default discovery request | Model/default metadata returned | `image_audio_mcp.services` | Ensures video model discovery and health defaults use one metadata/default owner. |
| DS-004 | Bounded Local | Existing image/audio/grounding request | Existing output shape returned | Existing service functions | Regression spine proving the video addition does not disturb current capabilities. |

## Primary Execution / Data-Flow Spines

```text
DS-001: MCP client -> server.generate_video tool -> services.generate_video -> VideoClientFactory -> video client -> download_file_from_url -> local file path
DS-002: CLI user -> cli.generate-video parser -> cli._dispatch -> services.generate_video -> VideoClientFactory -> video client -> download_file_from_url -> JSON envelope
DS-003: MCP/CLI health/list request -> server/cli facade -> services health/list -> VideoClientFactory/VideoModel/default env -> metadata
DS-004: Existing MCP/CLI request -> unchanged facade names -> existing service function -> existing Autobyteus image/audio/LLM path
```

## Spine Actors / Main-Line Nodes

| Node | Role In Spine | What It Advances |
| --- | --- | --- |
| MCP facade (`server.py`) | Public MCP tool schema and registration | Stable tool names and typed arguments. |
| CLI facade (`cli.py`) | Task-oriented shell UX and JSON envelope | Repeatable media/config flags, error/success envelopes. |
| Service boundary (`services.py`) | Authoritative runtime owner | Path safety, default model selection, factory construction, provider invocation, download, cleanup. |
| Autobyteus video factory/client | External multimedia provider boundary | Model resolution, remote discovery, video endpoint execution. |
| File/download utilities | Existing off-spine IO concern | Local output persistence under safe path rules. |

## Spine Narratives

| Spine ID | Short Narrative | Main Domain Subject Nodes | Governing Owner | Key Off-Spine Concerns |
| --- | --- | --- | --- | --- |
| DS-001 | The MCP client supplies a prompt/output path and optional media lists. The server validates/schema-shapes the tool call, then delegates to `services.generate_video`, which resolves paths/default model, calls the Autobyteus video client, downloads the first video URL, cleans up, and returns the saved file path. | MCP tool, service operation, video client, output file | `services.generate_video` | Safe path resolution, media source normalization, download, cleanup. |
| DS-002 | The CLI parses ergonomic flags into service-shaped values, delegates to the same service operation as MCP, then wraps the result in the existing JSON envelope. | CLI command, service operation, output envelope | `cli._dispatch` plus `services.generate_video` | Config parsing, repeated media flags, usage-error mapping. |
| DS-003 | Discovery calls use service functions to initialize factories and serialize model/default metadata; health reads default env values. | Service model listing/default logic | `services.py` | Private model metadata serializer. |
| DS-004 | Existing commands/tools keep their current facade names and service functions. | Existing service functions | Existing owners | Regression tests only; no new compatibility path. |

## Ownership Map

| Node / Owner | Owns | Must Not Own | Notes |
| --- | --- | --- | --- |
| `server.py` | MCP names, schemas, descriptions, tool registration | Provider construction, path normalization, downloads | Add `generate_video` and `list_video_models` only. |
| `cli.py` | Argument parsing, CLI command names, JSON envelopes | Provider construction, download logic | Add repeatable audio/video input flags and dispatch. |
| `services.py` | Runtime behavior, model defaults, safe paths, factory/client lifecycle, model metadata serialization | MCP-specific context or CLI output formatting | Add video peer functions here. |
| `VideoClientFactory` / video client | Video model resolution and provider execution | MCP/CLI schema concerns | Consumed through Autobyteus public multimedia API. |

## Off-Spine Concerns Around The Spine

| Off-Spine Concern | Serves Which Owner | Responsibility | Must Stay Off Main Line? |
| --- | --- | --- | --- |
| Model metadata serialization | `services.py` model listing functions | Convert Image/Audio/Video model objects to public dict shape. | Yes |
| Media source normalization | `services.generate_video` | Reuse URL/data URI/local safe-path handling for images/audios/videos. | Yes |
| Config parsing | `cli.py` | Convert `--config key=value` into nested generation_config dict. | Yes |
| Remote integration gating | `tests/test_integration.py` | Keep slow/quota tests opt-in. | Yes |

## Existing Capability / Subsystem Reuse Check

| Need / Concern | Existing Capability Area / Subsystem | Decision | Why | If New, Why Existing Areas Are Not Right |
| --- | --- | --- | --- | --- |
| MCP video tool | `image_audio_mcp.server` | Extend | Same public MCP facade owns current tools. | N/A |
| CLI video command | `image_audio_mcp.cli` | Extend | Same CLI facade owns task-oriented commands. | N/A |
| Video runtime | `image_audio_mcp.services` | Extend | Existing authoritative runtime boundary. | N/A |
| Model metadata serialization | `services.py` private helpers | Extend | Existing listing functions already own this shape. | N/A |
| Video backend | `autobyteus.multimedia.video` | Reuse | Latest Autobyteus release owns video model/client behavior. | N/A |

## Subsystem / Capability-Area Allocation

| Subsystem / Capability Area | Owns Which Concerns | Related Spine ID(s) | Governing Owner(s) Served | Decision | Notes |
| --- | --- | --- | --- | --- | --- |
| `autobyteus-image-audio` package | MCP/CLI multimedia generation surfaces | DS-001 through DS-004 | MCP and CLI users | Extend | No rename. |
| `image_audio_mcp.services` | Runtime provider/path/output behavior | DS-001, DS-003, DS-004 | Service boundary | Extend | Add video as peer modality. |
| `image_audio_mcp.cli` | Shell UX | DS-002, DS-004 | CLI boundary | Extend | Add video commands and flags. |
| Package tests | Local/remote verification | DS-001 through DS-004 | Validation gate | Extend | Keep opt-in remote video. |

## Ownership-Driven Dependency Rules

- Allowed dependency directions:
  - `server.py` -> `services.py`
  - `cli.py` -> `services.py`
  - `services.py` -> Autobyteus multimedia factories/clients and utilities
  - tests -> public service/server/CLI surfaces
- Authoritative public entrypoints versus internal owned sub-layers:
  - Public MCP entrypoint: `create_server()`
  - Public CLI entrypoint: `image_audio_mcp.cli:main`
  - Runtime authority: `image_audio_mcp.services`
- Authoritative Boundary Rule:
  - MCP/CLI code must not instantiate `VideoClientFactory` directly; it calls `services`.
  - Tests may monkeypatch service dependencies for local validation.
- Forbidden shortcuts:
  - No direct remote HTTP calls from MCP/CLI.
  - No exposed `session_id` parameter.
  - No project rename aliases or dual server identities for this ticket.
- Temporary exceptions and removal plan:
  - None.

## Architecture Direction Decision

- Chosen direction: extend existing package, service boundary, MCP facade, and CLI facade with video peer capability.
- Rationale:
  - Complexity: smallest coherent change; no migration.
  - Testability: service/server/CLI local tests follow existing patterns.
  - Operability: `uv --frozen` wrapper stays stable after lock update.
  - Evolution cost: future video models remain inside Autobyteus `VideoClientFactory`.
- Data-flow spine clarity assessment: `Yes`
- Spine inventory completeness assessment: `Yes`
- Ownership clarity assessment: `Yes`
- Off-spine concern clarity assessment: `Yes`
- Authoritative Boundary Rule assessment: `Yes`
- File placement within the owning subsystem assessment: `Yes`
- Outcome: `Add`

## Ownership And Structure Checks

| Check | Result | Evidence | Decision |
| --- | --- | --- | --- |
| Repeated coordination policy across callers exists and needs a clearer owner | Yes | MCP and CLI both need video runtime; existing service owner handles this. | Keep service boundary authoritative. |
| Responsibility overload exists in one file or one optional module grouping | No | `services.py` already owns multimedia runtime; video is a peer. | Keep flat layout. |
| Proposed indirection owns real policy, translation, or boundary concern | Yes | Private model metadata serializer avoids triplicate list serialization. | Add private helper in `services.py`. |
| Every off-spine concern has a clear owner on the spine | Yes | Config parsing in CLI, model/path/download in services. | Keep. |
| Authoritative Boundary Rule is preserved | Yes | Facades only call services. | Keep. |
| Existing capability area/subsystem was reused or extended where it naturally fits | Yes | Existing package and Autobyteus multimedia video reused. | Extend/reuse. |
| Repeated structures were extracted into reusable owned files where needed | Partially | Model serialization can be a private function, not a new file. | Extract private function. |
| Current structure can remain unchanged without spine/ownership degradation | Yes | New video surface maps naturally to existing files. | Keep layout. |

## Change Inventory

| Change ID | Change Type | Current Path | Target Path | Rationale | Impacted Areas | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| C-001 | Modify | `autobyteus-image-audio/pyproject.toml` | same | Bump dependency to `autobyteus==1.4.4`. | Dependency | Keep package name/version unless release policy says otherwise. |
| C-002 | Modify | `autobyteus-image-audio/requirements.txt` | same | Keep alternate dependency source aligned. | Dependency |  |
| C-003 | Modify | `autobyteus-image-audio/uv.lock` | same | Preserve `uv --frozen` wrapper. | Runtime |  |
| C-004 | Modify | `src/image_audio_mcp/services.py` | same | Add video default/model listing/generation and private model serializer. | Runtime | Governing owner. |
| C-005 | Modify | `src/image_audio_mcp/server.py` | same | Add MCP `list_video_models` and `generate_video`; update instructions. | MCP | No rename. |
| C-006 | Modify | `src/image_audio_mcp/cli.py` | same | Add CLI video commands and input flags. | CLI | No raw MCP mode. |
| C-007 | Modify | package tests | same | Add local service/server/CLI/integration coverage. | Tests | Optional remote video gated. |
| C-008 | Modify | package/root docs | same | Document video support and stable identity. | Docs | README/DESIGN/root README. |

## Removal / Decommission Plan

| Item To Remove / Decommission | Why It Becomes Unnecessary | Replaced By Which Owner / File / Structure | Scope | Notes |
| --- | --- | --- | --- | --- |
| Project rename idea | User confirmed no rename; rename would create migration burden. | Stable `autobyteus-image-audio` identity with clear video tool names. | In This Change | No alias package or wrapper added. |
| Duplicate model metadata serialization | Adding video would make duplicated image/audio list serialization triplicate. | Private `_model_metadata()` in `services.py`. | In This Change | Keep local to service owner. |

## Final File Responsibility Mapping

| File | Owning Subsystem / Capability Area | Owner / Boundary | Concrete Concern | Why This Is One File | Reuses Shared Structure? |
| --- | --- | --- | --- | --- | --- |
| `services.py` | `autobyteus-image-audio` runtime | Service boundary | Defaults, model listing, generation/edit/speech/video runtime, safe paths, downloads, cleanup. | Existing authoritative runtime file; video is peer modality. | Existing path/media helpers plus private metadata helper. |
| `server.py` | MCP facade | MCP boundary | Tool registration, names, schema annotations, descriptions. | Existing public MCP facade. | Delegates to services. |
| `cli.py` | CLI facade | CLI boundary | Command parsing, JSON envelopes, dispatch. | Existing task-oriented CLI file. | Existing config/output helpers plus new media flags. |
| `tests/test_services_local.py` | Validation | Service tests | Fake-client service behavior. | Existing local service coverage file. | Existing fake pattern. |
| `tests/test_server_local.py` | Validation | MCP tests | Tool inventory/schema/model listing. | Existing in-memory MCP coverage file. | Existing session helper. |
| `tests/test_cli_local.py` | Validation | CLI tests | Command parsing/envelope. | Existing CLI coverage file. | Existing output parser helper. |
| `tests/test_integration.py` | Validation | Remote optional tests | Real MCP/provider smoke tests. | Existing opt-in integration file. | Existing env gates. |

## Derived Implementation Mapping

| Target File | Change Type | Mapped Spine ID | Owner / Off-Spine Concern | Responsibility | Key APIs / Interfaces | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `services.py` | Modify | DS-001, DS-003 | Runtime service | Add `DEFAULT_VIDEO_MODEL`, `_get_default_video_model`, `list_video_models`, `generate_video`. | `VideoClientFactory`, `VideoModel` | Private serializer used by image/audio/video lists. |
| `server.py` | Modify | DS-001, DS-003 | MCP facade | Register `list_video_models`, `generate_video`. | FastMCP tools | Include media list args and config description. |
| `cli.py` | Modify | DS-002, DS-003 | CLI facade | Parse/dispatch `list-video-models`, `generate-video`. | argparse commands | Repeatable `--input-audio`, `--input-video`. |
| `tests/*` | Modify | all | Validation | Cover local and opt-in remote scenarios. | pytest, in-memory MCP |  |

## File Placement And Ownership Check

| File | Current Path | Target Path | Owning Concern / Platform | Path Matches Concern? | Flat-Or-Over-Split Risk | Action | Rationale |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `services.py` | existing | existing | Runtime service | Yes | Low | Keep | Adding peer modality does not justify new folder. |
| `server.py` | existing | existing | MCP facade | Yes | Low | Keep | Existing public boundary. |
| `cli.py` | existing | existing | CLI facade | Yes | Low | Keep | Existing command boundary. |
| tests | existing | existing | Package validation | Yes | Low | Keep | Existing test grouping is clear. |

## Concrete Examples / Shape Guidance

| Topic | Good Example | Bad / Avoided Shape | Why The Example Matters |
| --- | --- | --- | --- |
| MCP tool names | `generate_video`, `list_video_models` | Rename package to `autobyteus-multimedia` during this ticket | Tool names are the public discovery surface without migration. |
| Video runtime boundary | `server.generate_video -> services.generate_video -> VideoClientFactory` | `server.generate_video -> VideoClientFactory` | Preserves service authority. |
| CLI media flags | `--input-image a.png --input-audio voice.wav --input-video clip.mp4` | one ambiguous `--input-media` flag | Explicit media subjects avoid guessing. |

## Backward-Compatibility Rejection Log

| Candidate Compatibility Mechanism | Why It Was Considered | Rejection Decision | Replacement Clean-Cut Design |
| --- | --- | --- | --- |
| Rename project with old-name wrapper alias | Name no longer lists video. | Rejected | Keep stable project identity; add clear video tool/command names. |
| Generic `input_media` argument | Could reduce flags/fields. | Rejected | Use explicit `input_images`, `input_audios`, `input_videos` matching Autobyteus video client. |
| Expose `session_id` in MCP schema | Autobyteus client has internal session lifecycle. | Rejected | Let `AutobyteusVideoClient` own session IDs. |

## Derived Interface Boundary Mapping

| Owning File | Mapped Spine ID | Owner / Off-Spine Concern | Subject Owned | Concern / Responsibility | Interfaces / APIs / Methods | Accepted Identity Shape(s) | Inputs/Outputs | Dependencies |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `services.py` | DS-001 | Runtime service | Video generation | Execute and save video generation. | `generate_video(...)` | model via env/default; media as list of path/URL/data URI strings | dict with `file_path`, `model` | `VideoClientFactory`, file/download utils |
| `services.py` | DS-003 | Runtime service | Video models | List available video models. | `list_video_models()` | N/A | dict with `models` list | `VideoClientFactory`, `VideoModel` |
| `server.py` | DS-001 | MCP facade | MCP video tool | Public schema/registration. | `generate_video` tool | explicit named params | structured result | `services.generate_video` |
| `cli.py` | DS-002 | CLI facade | CLI video command | CLI parsing/envelope. | `generate-video` command | repeatable flags | JSON envelope | `services.generate_video` |

## Interface Boundary Check

| Interface / API / Command / Method | Subject Owned | Responsibility Is Singular? | Identity Shape Is Explicit? | Ambiguous-ID Or Generic-Selector Risk | Corrective Action |
| --- | --- | --- | --- | --- | --- |
| `services.generate_video` | Video generation | Yes | Yes | Low | None |
| MCP `generate_video` | Video generation tool | Yes | Yes | Low | None |
| CLI `generate-video` | Video generation command | Yes | Yes | Low | None |
| `services.list_video_models` | Video model listing | Yes | N/A | Low | None |

## Naming Decisions

| Item Type | Current Name | Proposed Name | Reason | Notes |
| --- | --- | --- | --- | --- |
| API/MCP tool | N/A | `generate_video` | Matches existing MCP snake_case and Autobyteus tool name. | Add. |
| API/MCP tool | N/A | `list_video_models` | Peer to `list_image_models` / `list_audio_models`. | Add. |
| CLI command | N/A | `generate-video` | Existing CLI kebab-case style. | Add. |
| CLI command | N/A | `list-video-models` | Existing CLI kebab-case style. | Add. |
| Env var | N/A | `DEFAULT_VIDEO_GENERATION_MODEL` | Matches Autobyteus video tool. | Add. |
| Package | `autobyteus-image-audio` | `autobyteus-image-audio` | Stable identity. | Keep. |

## Naming Drift Check

| Item | Current Responsibility | Does Name Still Match? | Corrective Action | Mapped Change ID |
| --- | --- | --- | --- | --- |
| `autobyteus-image-audio` package | Image, audio, coordinate, and now video generation MCP/CLI | Partially | Keep by confirmed requirement; docs describe multimedia scope. | C-008 |
| `image_audio_mcp` import path | Package implementation | Partially | Keep by confirmed requirement; no alias. | N/A |
| `IMAGE_AUDIO_MCP_*` env vars | MCP name/instructions overrides | Partially | Keep by confirmed requirement. | N/A |

## Existing-Structure Bias Check

| Candidate Area | Current-File-Layout Bias Risk | Architecture-First Alternative | Decision | Why |
| --- | --- | --- | --- | --- |
| Keep video in `services.py` | Low | Create `video_services.py` | Keep | Existing file is the runtime boundary and has reusable path/download helpers. |
| Keep package name | Medium | Rename to multimedia | Keep | User confirmed; rename would create migration without runtime benefit. |
| Keep tests in current files | Low | Split video test files | Keep | Scope is additive and current files are small enough. |

## Anti-Hack Check

| Candidate Change | Shortcut/Hack Risk | Proper Structural Fix | Decision | Notes |
| --- | --- | --- | --- | --- |
| Direct `VideoClientFactory` use in `server.py` | High | Route through `services.py`. | Reject shortcut | Preserves boundary. |
| Hard-code remote host/model in MCP tool | High | Use env/default factory resolution. | Reject shortcut | Keeps config model consistent. |
| Shell out to existing Autobyteus `GenerateVideoTool` | Medium | Use factory/client service pattern directly. | Reject shortcut | Avoids mixing agent tool lifecycle into MCP service. |

## Dependency Flow And Cross-Reference Risk

| Dependency Boundary | Upstream Dependencies | Downstream Dependents | Cross-Reference Risk | Mitigation / Boundary Strategy |
| --- | --- | --- | --- | --- |
| MCP -> service | `server.py` imports `services` | MCP clients | Low | Keep one-way dependency. |
| CLI -> service | `cli.py` imports `services` | CLI users/wrapper | Low | Keep one-way dependency. |
| Service -> Autobyteus video | `services.py` imports video factory/model | Runtime provider | Medium | Limit to service layer; test with fake client. |
| Tests -> internals | tests monkeypatch factories | Validation only | Low | Keep monkeypatching scoped to local tests. |

## Decommission / Cleanup Plan

| Item To Remove/Rename | Cleanup Actions | Legacy Removal Notes | Verification |
| --- | --- | --- | --- |
| None | N/A | No old video implementation exists. | Review verifies no rename aliases or compatibility wrappers added. |

## Error Handling And Edge Cases

- No video URLs returned: raise `ValueError("Video generation returned no video URLs.")`.
- Missing local media file: existing `_normalize_media_source` raises `FileNotFoundError`.
- Video client creation/model resolution failure: propagate Autobyteus error through existing CLI/MCP error handling.
- Remote backend browser/session failure: treated as provider/runtime error; optional integration test evidence should distinguish this from implementation failure.
- Cleanup failure: reuse `_safe_cleanup` warning behavior.

## Use-Case Coverage Matrix

| use_case_id | Requirement | Use Case | Primary Path Covered | Fallback Path Covered | Error Path Covered | Runtime Call Stack Section |
| --- | --- | --- | --- | --- | --- | --- |
| UC-001 | R-004/R-005/R-006/R-007 | MCP prompt-only video generation | Yes | N/A | Yes | Future stack UC-001 |
| UC-002 | R-004/R-005/R-007 | MCP media-input video generation | Yes | N/A | Yes | Future stack UC-002 |
| UC-003 | R-003/R-006/R-009 | Video model/default discovery | Yes | N/A | Yes | Future stack UC-003 |
| UC-004 | R-008 | CLI video generation/listing | Yes | N/A | Yes | Future stack UC-004 |
| UC-005 | R-010/R-011/R-012 | Existing capability regression | Yes | N/A | Yes | Future stack UC-005 |

## Migration / Rollout

1. Update dependency pins/lock.
2. Add video service functions and model metadata serializer.
3. Add MCP tools and CLI commands.
4. Add local tests and optional remote integration test.
5. Update docs.
6. Run frozen local validation.

## Change Traceability To Implementation

| Change ID | Implementation Task(s) | Verification | Status |
| --- | --- | --- | --- |
| C-001 through C-003 | Dependency and lock update | `uv --frozen` commands, pytest | Planned |
| C-004 | Service video support | service local tests | Planned |
| C-005 | MCP video support | server local tests | Planned |
| C-006 | CLI video support | CLI local tests | Planned |
| C-007 | Test coverage | pytest/local and optional remote | Planned |
| C-008 | Docs | docs sync review | Planned |

## Open Questions

- Whether optional remote video integration should be executed in this ticket depends on available server state and quota. The test should exist and skip by default regardless.
