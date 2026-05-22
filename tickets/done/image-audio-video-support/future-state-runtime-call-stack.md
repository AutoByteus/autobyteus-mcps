# Future-State Runtime Call Stacks

## Design Basis

- Scope Classification: `Medium`
- Call Stack Version: `v1`
- Requirements: `tickets/in-progress/image-audio-video-support/requirements.md` (`Design-ready`)
- Source Artifact: `tickets/in-progress/image-audio-video-support/proposed-design.md`
- Source Design Version: `v1`
- Referenced Sections:
  - `Data-Flow Spine Inventory`
  - `Ownership Map`
  - `Derived Interface Boundary Mapping`

## Future-State Modeling Rule

This document models the target (`to-be`) behavior after video support is implemented. It is not a trace of current code.

## Use Case Index

| use_case_id | Spine ID(s) | Spine Scope | Governing Owner | Source Type | Requirement ID(s) | Design-Risk Objective | Use Case Name | Coverage Target |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| UC-001 | DS-001 | Primary End-to-End | `services.generate_video` | Requirement | R-004, R-005, R-006, R-007 | N/A | MCP prompt-only video generation | Primary/Error |
| UC-002 | DS-001 | Primary End-to-End | `services.generate_video` | Requirement | R-004, R-005, R-007 | N/A | MCP video generation with media inputs | Primary/Error |
| UC-003 | DS-003 | Bounded Local | `services.py` | Requirement | R-003, R-006, R-009 | N/A | Video model/default discovery | Primary/Error |
| UC-004 | DS-002, DS-003 | Primary End-to-End / Bounded Local | `cli.py` and `services.py` | Requirement | R-005, R-008 | N/A | CLI video generation and listing | Primary/Error |
| UC-005 | DS-004 | Bounded Local | Existing service functions | Requirement | R-010, R-011, R-012 | N/A | Existing capability regression | Primary/Error |

## Transition Notes

- No migration/dual-path behavior is modeled.
- No project rename alias is modeled.
- `autobyteus==1.4.4` is assumed available after dependency update.

## Use Case: UC-001 MCP Prompt-Only Video Generation

### Spine Context

- Spine ID(s): DS-001
- Spine Scope: Primary End-to-End
- Governing Owner: `image_audio_mcp.services.generate_video`
- Why This Use Case Matters: it is the main MCP video generation path.

### Goal

Generate a video from prompt text and save it to a safe local output path.

### Preconditions

- MCP server is created through `image_audio_mcp.server:create_server`.
- `DEFAULT_VIDEO_GENERATION_MODEL` may be set; otherwise default is `gemini-omni-app-rpa`.
- Autobyteus video factory can resolve the configured model.

### Expected Outcome

`generate_video` returns a structured payload with a local `file_path` and the resolved model identifier.

### Primary Runtime Call Stack

```text
[ENTRY] image_audio_mcp/server.py:create_server(...)
└── image_audio_mcp/server.py:generate_video(prompt, output_file_path, input_images=None, input_audios=None, input_videos=None, generation_config=None)
    └── [ASYNC] image_audio_mcp/services.py:generate_video(prompt, output_file_path, input_images=None, input_audios=None, input_videos=None, generation_config=None)
        ├── image_audio_mcp/services.py:_get_workspace_root()
        ├── image_audio_mcp/services.py:_resolve_output_path(output_file_path, workspace_root)
        ├── image_audio_mcp/services.py:_normalize_media_sources(None, workspace_root) # images
        ├── image_audio_mcp/services.py:_normalize_media_sources(None, workspace_root) # audios
        ├── image_audio_mcp/services.py:_normalize_media_sources(None, workspace_root) # videos
        ├── image_audio_mcp/services.py:_get_default_video_model()
        ├── autobyteus.multimedia.video.video_client_factory.py:VideoClientFactory.create_video_client(model_id)
        ├── [ASYNC] autobyteus.multimedia.video.base_video_client.py:generate_video(prompt, input_image_urls=None, input_audio_urls=None, input_video_urls=None, generation_config=generation_config)
        │   └── [IO] Autobyteus video provider/RPA LLM server generates video and returns video_urls
        ├── [IO] autobyteus.utils.download_utils.py:download_file_from_url(response.video_urls[0], resolved_output)
        ├── image_audio_mcp/services.py:return {"file_path": str(resolved_output), "model": model_id}
        └── [ASYNC] image_audio_mcp/services.py:_safe_cleanup(client)
```

### Branching / Fallback Paths

```text
[ERROR] if response.video_urls is empty
image_audio_mcp/services.py:generate_video(...)
└── raise ValueError("Video generation returned no video URLs.")
```

```text
[ERROR] if model cannot be resolved
VideoClientFactory.create_video_client(model_id)
└── raise ValueError(...) # propagated through MCP error handling
```

### State And Data Transformations

- MCP arguments -> service arguments.
- `output_file_path` -> workspace-safe `Path`.
- configured/default model env -> `model_id`.
- first returned `video_url` -> downloaded local file.

### Observability And Debug Points

- Existing provider/client logging from Autobyteus video client.
- Service exceptions preserve provider/path failure messages.

### Design Smells / Gaps

- Any legacy/backward-compatibility branch present? `No`
- Any tight coupling or cyclic cross-subsystem dependency introduced? `No`
- Any naming-to-responsibility drift detected? `No`

### Coverage Status

- Primary Path: `Covered`
- Fallback Path: `N/A`
- Error Path: `Covered`

## Use Case: UC-002 MCP Video Generation With Media Inputs

### Spine Context

- Spine ID(s): DS-001
- Spine Scope: Primary End-to-End
- Governing Owner: `image_audio_mcp.services.generate_video`
- Why This Use Case Matters: proves image, audio, and video references are accepted and passed to the video client in their explicit subject lists.

### Goal

Generate a video using optional image, audio, and video references as conditioning inputs.

### Preconditions

- Input references are URLs, data URIs, or safe local paths under the configured workspace/allowed roots.

### Expected Outcome

The video client receives normalized `input_image_urls`, `input_audio_urls`, and `input_video_urls`; the generated output is downloaded locally.

### Primary Runtime Call Stack

```text
[ENTRY] image_audio_mcp/server.py:generate_video(prompt, output_file_path, input_images=[...], input_audios=[...], input_videos=[...], generation_config={...})
└── [ASYNC] image_audio_mcp/services.py:generate_video(...)
    ├── image_audio_mcp/services.py:_get_workspace_root()
    ├── image_audio_mcp/services.py:_resolve_output_path(output_file_path, workspace_root)
    ├── image_audio_mcp/services.py:_normalize_media_sources(input_images, workspace_root)
    │   └── image_audio_mcp/services.py:_normalize_media_source(each_image, workspace_root)
    ├── image_audio_mcp/services.py:_normalize_media_sources(input_audios, workspace_root)
    │   └── image_audio_mcp/services.py:_normalize_media_source(each_audio, workspace_root)
    ├── image_audio_mcp/services.py:_normalize_media_sources(input_videos, workspace_root)
    │   └── image_audio_mcp/services.py:_normalize_media_source(each_video, workspace_root)
    ├── image_audio_mcp/services.py:_get_default_video_model()
    ├── autobyteus.multimedia.video.video_client_factory.py:VideoClientFactory.create_video_client(model_id)
    ├── [ASYNC] video_client.generate_video(
    │       prompt=prompt,
    │       input_image_urls=normalized_images,
    │       input_audio_urls=normalized_audios,
    │       input_video_urls=normalized_videos,
    │       generation_config=generation_config,
    │   )
    ├── [IO] download_file_from_url(response.video_urls[0], resolved_output)
    └── [ASYNC] _safe_cleanup(client)
```

### Branching / Fallback Paths

```text
[ERROR] if a local input path is missing
image_audio_mcp/services.py:_normalize_media_source(value, workspace_root)
└── raise FileNotFoundError(f"Input file not found: {resolved}")
```

```text
[ERROR] if provider rejects media/config
video_client.generate_video(...)
└── provider exception propagates through service and MCP response handling
```

### State And Data Transformations

- Local paths -> absolute safe paths.
- URL/data URI inputs -> unchanged.
- Three explicit media lists remain separate; no generic media list is introduced.

### Design Smells / Gaps

- Any legacy/backward-compatibility branch present? `No`
- Any tight coupling or cyclic cross-subsystem dependency introduced? `No`
- Any naming-to-responsibility drift detected? `No`

### Coverage Status

- Primary Path: `Covered`
- Fallback Path: `N/A`
- Error Path: `Covered`

## Use Case: UC-003 Video Model/Default Discovery

### Spine Context

- Spine ID(s): DS-003
- Spine Scope: Bounded Local
- Governing Owner: `image_audio_mcp.services`
- Why This Use Case Matters: model listing and health defaults must expose video support consistently.

### Goal

List video model metadata and report the configured default video model in health status.

### Preconditions

- Autobyteus video factory is importable from `autobyteus==1.4.4`.

### Expected Outcome

`list_video_models` returns model metadata with the same shape as image/audio model lists; `health_check` includes `default_video_generation_model`.

### Primary Runtime Call Stack

```text
[ENTRY] image_audio_mcp/server.py:list_video_models()
└── [ASYNC] image_audio_mcp/services.py:list_video_models()
    ├── autobyteus.multimedia.video.video_client_factory.py:VideoClientFactory.ensure_initialized()
    ├── autobyteus.multimedia.video.video_model.py:VideoModel.__iter__()
    ├── image_audio_mcp/services.py:_model_metadata(model) for each model
    └── return {"models": models}
```

```text
[ENTRY] image_audio_mcp/server.py:health_check()
└── [ASYNC] image_audio_mcp/services.py:health_check()
    ├── image_audio_mcp/services.py:_get_default_image_generation_model()
    ├── image_audio_mcp/services.py:_get_default_image_edit_model()
    ├── image_audio_mcp/services.py:_get_default_speech_model()
    ├── image_audio_mcp/services.py:_get_default_video_model()
    ├── image_audio_mcp/services.py:_get_default_grounding_model()
    └── return default model payload
```

### Branching / Fallback Paths

```text
[ERROR] if remote discovery fails internally
VideoClientFactory.ensure_initialized()
└── Autobyteus provider/factory behavior determines whether discovery failure is logged or raised
```

### State And Data Transformations

- Model object -> metadata dict:
  - `model_identifier`
  - `name`
  - `value`
  - `provider`
  - `runtime`
  - `parameter_schema`
  - `default_config`

### Design Smells / Gaps

- Any legacy/backward-compatibility branch present? `No`
- Any tight coupling or cyclic cross-subsystem dependency introduced? `No`
- Any naming-to-responsibility drift detected? `No`

### Coverage Status

- Primary Path: `Covered`
- Fallback Path: `N/A`
- Error Path: `Covered`

## Use Case: UC-004 CLI Video Generation And Listing

### Spine Context

- Spine ID(s): DS-002, DS-003
- Spine Scope: Primary End-to-End / Bounded Local
- Governing Owner: `image_audio_mcp.cli` and `image_audio_mcp.services`
- Why This Use Case Matters: the repo wrapper and CLI are used by agents and should support video without raw MCP JSON.

### Goal

Expose video generation and model listing through task-oriented CLI commands.

### Preconditions

- User invokes `cli/autobyteus-image-audio` or the package console script.

### Expected Outcome

CLI prints `{"ok":true,"command":"generate-video","result":...}` or `{"ok":true,"command":"list-video-models","result":...}` on success.

### Primary Runtime Call Stack

```text
[ENTRY] cli/autobyteus-image-audio generate-video ...
└── [IO] uv --directory autobyteus-image-audio run --frozen autobyteus-image-audio generate-video ...
    └── image_audio_mcp/cli.py:main(argv)
        └── image_audio_mcp/cli.py:run(argv)
            ├── image_audio_mcp/cli.py:build_parser()
            ├── argparse:parse_args(argv)
            ├── image_audio_mcp/cli.py:_load_generation_config(args)
            ├── [ASYNC] image_audio_mcp/cli.py:_dispatch(args)
            │   └── [ASYNC] image_audio_mcp/services.py:generate_video(
            │       prompt=args.prompt,
            │       output_file_path=args.output_file_path,
            │       input_images=args.input_images,
            │       input_audios=args.input_audios,
            │       input_videos=args.input_videos,
            │       generation_config=config,
            │   )
            └── image_audio_mcp/cli.py:_emit_success("generate-video", result)
```

```text
[ENTRY] cli/autobyteus-image-audio list-video-models
└── image_audio_mcp/cli.py:_dispatch(args)
    └── [ASYNC] image_audio_mcp/services.py:list_video_models()
```

### Branching / Fallback Paths

```text
[ERROR] invalid --config syntax
image_audio_mcp/cli.py:_parse_config_item(item)
└── raise CliUsageError(...)
    └── image_audio_mcp/cli.py:_emit_failure(command, "UsageError", ...)
```

```text
[ERROR] provider/path failure
image_audio_mcp/services.py:generate_video(...)
└── exception propagates to image_audio_mcp/cli.py:run(...)
    └── _emit_failure(command, type(exc).__name__, str(exc))
```

### State And Data Transformations

- Kebab-case CLI command -> service function dispatch.
- Repeatable `--input-image` -> `args.input_images: list[str]`.
- Repeatable `--input-audio` -> `args.input_audios: list[str]`.
- Repeatable `--input-video` -> `args.input_videos: list[str]`.
- Repeatable `--config key=value` -> nested `generation_config`.

### Design Smells / Gaps

- Any legacy/backward-compatibility branch present? `No`
- Any tight coupling or cyclic cross-subsystem dependency introduced? `No`
- Any naming-to-responsibility drift detected? `No`

### Coverage Status

- Primary Path: `Covered`
- Fallback Path: `N/A`
- Error Path: `Covered`

## Use Case: UC-005 Existing Capability Regression

### Spine Context

- Spine ID(s): DS-004
- Spine Scope: Bounded Local
- Governing Owner: Existing service functions and facades
- Why This Use Case Matters: video is separate but must not break current image/audio/grounding workflows.

### Goal

Existing public tools/commands and behavior continue to work.

### Preconditions

- Existing tests and tool names remain in the package.

### Expected Outcome

Local test suite passes with existing image/audio/grounding tests updated only for additive tool inventory/default field expectations.

### Primary Runtime Call Stack

```text
[ENTRY] MCP/CLI existing command or tool
├── image_audio_mcp/server.py or image_audio_mcp/cli.py existing facade function/dispatch
├── [ASYNC] image_audio_mcp/services.py:generate_image/edit_image/generate_speech/find_target_coordinates/list_image_models/list_audio_models/health_check
└── existing output shape returned
```

### Branching / Fallback Paths

```text
[ERROR] existing provider/path/config failures
existing service function
└── existing exception behavior remains unchanged
```

### State And Data Transformations

- Existing image/audio/coordinate input and output shapes remain unchanged.
- `health_check` gains only additive `default_video_generation_model`.
- Public tool inventory gains only additive `list_video_models` and `generate_video`.

### Design Smells / Gaps

- Any legacy/backward-compatibility branch present? `No`
- Any tight coupling or cyclic cross-subsystem dependency introduced? `No`
- Any naming-to-responsibility drift detected? `No`

### Coverage Status

- Primary Path: `Covered`
- Fallback Path: `N/A`
- Error Path: `Covered`
