# Docs Sync

## Scope

- Ticket: `image-audio-video-support`
- Trigger Stage: `9`
- Workflow state source: `tickets/in-progress/image-audio-video-support/workflow-state.md`

## Why Docs Were Updated

- Summary: video generation is now a durable capability of the existing `autobyteus-image-audio` MCP/CLI package.
- Why this matters: future users need to discover `generate_video`, `list_video_models`, `generate-video`, `list-video-models`, `DEFAULT_VIDEO_GENERATION_MODEL`, and the stable no-rename package identity from long-lived project docs rather than from ticket artifacts.

## Long-Lived Docs Reviewed

| Doc Path | Why It Was Reviewed | Result | Notes |
| --- | --- | --- | --- |
| `README.md` | Root project catalog needs accurate package summary. | Updated | Description now mentions image/video generation and TTS. |
| `autobyteus-image-audio/README.md` | Primary user-facing MCP/CLI docs. | Updated | Added video tools, CLI examples, env var, path/media notes, MCP config env. |
| `autobyteus-image-audio/DESIGN.md` | Durable architecture/runtime design doc. | Updated | Added video capability, service contracts, runtime simulations, validation posture. |
| `autobyteus-image-audio/runtime_callstack_simulation` | Existing runtime reference was stale and server-owned. | Updated | Rewritten to reflect service-boundary flows and video case. |
| `autobyteus-image-audio/pyproject.toml` | Package metadata is user-visible. | Updated | Description now includes video. |
| `autobyteus-image-audio/requirements.txt` / `uv.lock` | Dependency truth for runtime. | Updated | Autobyteus pin moved to `1.4.4`. |

## Docs Updated

| Doc Path | Type Of Update | What Was Added / Changed | Why |
| --- | --- | --- | --- |
| `README.md` | Project catalog | `autobyteus-image-audio` summary includes video generation. | Root overview must be accurate. |
| `autobyteus-image-audio/README.md` | User guide | Added video CLI commands, MCP tools, env var, stable identity explanation, media path behavior, MCP config default. | Users need discoverable video docs without project rename. |
| `autobyteus-image-audio/DESIGN.md` | Architecture/runtime | Added video service contract, model catalog, runtime simulations, validation posture. | Future maintainers need the current runtime shape. |
| `autobyteus-image-audio/runtime_callstack_simulation` | Runtime reference | Updated image/audio paths to use `services.py`; added `generate_video`. | Prior simulation was stale after the existing service-boundary architecture and lacked video. |
| `autobyteus-image-audio/pyproject.toml` | Package metadata | Description includes image, audio, and video generation. | Published/install metadata should not be image/audio-only. |

## Durable Design / Runtime Knowledge Promoted

| Topic | What Future Readers Need To Understand | Source Ticket Artifact(s) | Target Long-Lived Doc |
| --- | --- | --- | --- |
| Stable package identity | Do not rename; video is exposed through tool/command names. | `requirements.md`, `proposed-design.md` | `autobyteus-image-audio/README.md` |
| Video MCP/CLI surfaces | `generate_video`, `list_video_models`, `generate-video`, `list-video-models`. | `requirements.md`, `api-e2e-testing.md` | `README.md`, package `README.md`, `DESIGN.md` |
| Runtime owner | `services.py` owns model defaults, media normalization, client lifecycle, download, cleanup. | `proposed-design.md`, call stack docs | `DESIGN.md`, `runtime_callstack_simulation` |
| Configuration | `DEFAULT_VIDEO_GENERATION_MODEL`, default `gemini-omni-app-rpa`. | `requirements.md` | package `README.md`, MCP config example |

## Removed / Replaced Components Recorded

| Old Component / Path / Concept | What Replaced It | Where The New Truth Is Documented |
| --- | --- | --- |
| Image/audio-only package description | Stable package with image, audio, and video capabilities | root README, package README, pyproject description |
| Runtime simulation showing server-owned path helpers | Service-boundary runtime simulation | `runtime_callstack_simulation` and `DESIGN.md` |
| Duplicated model metadata serialization concept | Private service-owned model metadata serializer | `DESIGN.md` and implementation |

## Final Result

- Result: `Updated`
- Blocked classification: `N/A`
- Required return path or unblock condition: `N/A`
- Follow-up needed: none for docs sync.

## Verification

- `rg` found no stale `1.4.3`, `image and audio generation`, image/audio-only public-tools wording, or missing video env/tool docs in reviewed long-lived docs.
- `uv lock --check` passed.
- `git diff --check` passed.
