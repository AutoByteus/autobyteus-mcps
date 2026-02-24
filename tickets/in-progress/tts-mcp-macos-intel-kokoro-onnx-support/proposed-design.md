# Proposed Design Document

## Design Version

- Current Version: `v1`

## Revision History

| Version | Trigger | Summary Of Changes | Related Review Round |
| --- | --- | --- | --- |
| v1 | Initial draft | Add Intel macOS Kokoro support path across platform selection, bootstrap, installer routing, and playback fallback | 1 |

## Artifact Basis

- Investigation Notes: `tickets/in-progress/tts-mcp-macos-intel-kokoro-onnx-support/investigation-notes.md`
- Requirements: `tickets/in-progress/tts-mcp-macos-intel-kokoro-onnx-support/requirements.md`
- Requirements Status: `Design-ready`

## Summary

`tts-mcp` will treat Intel macOS as a first-class Kokoro ONNX CPU host. Auto backend selection will route Intel macOS to `kokoro_onnx`, runtime bootstrap will install Kokoro runtime/assets when missing, and install scripts will provide a macOS Intel Kokoro path. Existing Apple Silicon MLX auto route and Linux runtime policy remain unchanged.

## Goals

- Deliver working Kokoro runtime path on macOS Intel.
- Preserve current behavior on Apple Silicon and Linux.
- Keep tool/API contract unchanged.
- Keep implementation clean with no compatibility shims.

## Legacy Removal Policy (Mandatory)

- Policy: `No backward compatibility; remove legacy code paths.`
- Required action: replace Linux-only Kokoro assumptions with explicit platform-aware routing in current code paths.

## Requirements And Use Cases

| Requirement | Description | Acceptance Criteria | Use Case IDs |
| --- | --- | --- | --- |
| R-001 | Auto-select Kokoro on Intel macOS | Auto route works on Darwin x86_64 | UC-001 |
| R-002 | Explicit Kokoro backend accepted on Intel macOS | `TTS_MCP_BACKEND=kokoro_onnx` works on Darwin x86_64 | UC-002 |
| R-003 | Auto bootstrap supports Intel macOS Kokoro install | missing runtime/assets trigger correct installer | UC-003 |
| R-004 | Installer supports Intel macOS asset download | script installs package + model assets | UC-004 |
| R-005 | Playback fallback works in macOS context | `auto` can use `afplay` when needed | UC-005 |

## Codebase Understanding Snapshot (Pre-Design Mandatory)

| Area | Findings | Evidence (files/functions) | Open Unknowns |
| --- | --- | --- | --- |
| Entrypoints / Boundaries | `FastMCP` tool calls `run_speak` with settings from env | `src/tts_mcp/server.py:create_server` | None |
| Current Naming Conventions | Platform routing in `platform.py`; runtime install in `runtime_bootstrap.py`; scripts in `scripts/` | `src/tts_mcp/platform.py`, `src/tts_mcp/runtime_bootstrap.py`, `scripts/*` | None |
| Impacted Modules / Responsibilities | backend selection, runtime bootstrap, install dispatch, playback command selection | `select_backend`, `bootstrap_runtime`, `install_tts_runtime.sh`, `_build_linux_play_command` | None |
| Data / Persistence / External IO | Kokoro assets written under `.tools/**`; runtime installs via pip + network downloads | `install_kokoro_onnx_linux.sh`, `runtime_bootstrap.py` | None |

## Current State (As-Is)

- Intel macOS is unsupported for Kokoro in platform routing.
- Kokoro auto bootstrap/install path is Linux-only.
- Playback auto list excludes `afplay`.

## Target State (To-Be)

- Intel macOS (`Darwin x86_64`) auto routes to Kokoro ONNX.
- Explicit `kokoro_onnx` backend is valid on Intel macOS.
- Runtime bootstrap installs Kokoro on Intel macOS when required.
- Install dispatcher routes Intel macOS Kokoro requests to a dedicated script.
- Playback auto list includes `afplay` fallback.

## Change Inventory (Delta)

| Change ID | Change Type (`Add`/`Modify`/`Rename/Move`/`Remove`) | Current Path | Target Path | Rationale | Impacted Areas | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| C-001 | Modify | `src/tts_mcp/platform.py` | `src/tts_mcp/platform.py` | Allow Intel macOS Kokoro route | Backend selection | Preserve Apple Silicon/Linx behavior |
| C-002 | Modify | `src/tts_mcp/runtime_bootstrap.py` | `src/tts_mcp/runtime_bootstrap.py` | Add Intel macOS Kokoro bootstrap path | Runtime install orchestration | Reuse existing profile logic |
| C-003 | Add | N/A | `scripts/install_kokoro_onnx_macos.sh` | Provide install/runtime script for Intel macOS | Installer tooling | Keep arg semantics aligned with Linux script |
| C-004 | Modify | `scripts/install_tts_runtime.sh` | `scripts/install_tts_runtime.sh` | Route Intel macOS Kokoro installs | Installer dispatch | Keep arm64 MLX path unchanged |
| C-005 | Modify | `src/tts_mcp/runner.py` | `src/tts_mcp/runner.py` | Add `afplay` fallback in auto playback | Kokoro playback path | No MCP API change |
| C-006 | Modify | `tests/test_platform.py`, `tests/test_runtime_bootstrap.py` | same | Lock new behavior in tests | QA coverage | Keep existing coverage |
| C-007 | Modify | `README.md` | `README.md` | Document Intel macOS support and install path | User docs | Include config guidance |

## Architecture Overview

- Keep single platform-selection gateway (`platform.select_backend`).
- Keep single bootstrap gateway (`runtime_bootstrap.bootstrap_runtime`).
- Add one dedicated macOS Intel installer script; avoid branching complexity inside Linux script.

## File And Module Breakdown

| File/Module | Change Type | Concern / Responsibility | Public APIs | Inputs/Outputs | Dependencies |
| --- | --- | --- | --- | --- | --- |
| `src/tts_mcp/platform.py` | Modify | Host-to-backend policy | `detect_host`, `select_backend` | settings+host -> backend selection | `config`, `platform`, `subprocess` |
| `src/tts_mcp/runtime_bootstrap.py` | Modify | Runtime auto-install orchestration | `bootstrap_runtime` | settings -> script execution | filesystem, install scripts |
| `scripts/install_kokoro_onnx_macos.sh` | Add | Intel macOS Kokoro runtime/assets install | shell entrypoint | args/env -> installed runtime/assets | Python/pip/network |
| `scripts/install_tts_runtime.sh` | Modify | Cross-platform installer dispatch | shell entrypoint | args/env -> calls platform installer | platform uname checks |
| `src/tts_mcp/runner.py` | Modify | Speak execution + playback routing | `run_speak` internals | generated wav -> playback command | subprocess/player binaries |

## Layer-Appropriate Separation Of Concerns Check

- Non-UI scope: responsibilities stay module-local and clear.
- Integration scope: installer script encapsulates macOS Intel Kokoro installation concern.

## Naming Decisions (Natural And Implementation-Friendly)

| Item Type (`File`/`Module`/`API`) | Current Name | Proposed Name | Reason | Notes |
| --- | --- | --- | --- | --- |
| File | N/A | `install_kokoro_onnx_macos.sh` | explicit platform/runtime intent | mirrors Linux naming pattern |
| API | `_build_linux_play_command` | keep name unchanged (internal) | avoid broad refactor scope | behavior expanded to include `afplay` in `auto` mode |

## Naming Drift Check (Mandatory)

| Item | Current Responsibility | Does Name Still Match? (`Yes`/`No`) | Corrective Action (`Rename`/`Split`/`Move`/`N/A`) | Mapped Change ID |
| --- | --- | --- | --- | --- |
| `platform.select_backend` | policy routing across hosts | Yes | N/A | C-001 |
| `runtime_bootstrap.bootstrap_runtime` | install orchestration by host/runtime | Yes | N/A | C-002 |
| `_build_linux_play_command` | chooses local playback command for generated audio | Partially | N/A (scope-limited) | C-005 |

## Dependency Flow And Cross-Reference Risk

| Module/File | Upstream Dependencies | Downstream Dependents | Cross-Reference Risk | Mitigation / Boundary Strategy |
| --- | --- | --- | --- | --- |
| `platform.py` | env settings + host info | `runner.py` | Low | pure decision logic |
| `runtime_bootstrap.py` | host detection + scripts | `server.py` | Low | keep script selection helper local |
| `install_tts_runtime.sh` | uname/runtime args | users/bootstrap | Low | explicit per-platform branches |

## Decommission / Cleanup Plan

| Item To Remove/Rename | Cleanup Actions | Legacy Removal Notes | Verification |
| --- | --- | --- | --- |
| Linux-only Kokoro assumption in route/bootstrap | Replace with platform-aware conditions | no compatibility branch retained | unit tests + manual smoke |

## Error Handling And Edge Cases

- Unsupported host remains explicit failure with clear message.
- Intel macOS with `--linux-runtime llama_cpp` returns unsupported runtime message.
- Missing model assets triggers installer path or explicit runtime error.

## Use-Case Coverage Matrix (Design Gate)

| use_case_id | Requirement | Use Case | Primary Path Covered (`Yes`/`No`) | Fallback Path Covered (`Yes`/`No`/`N/A`) | Error Path Covered (`Yes`/`No`/`N/A`) | Runtime Call Stack Section |
| --- | --- | --- | --- | --- | --- | --- |
| UC-001 | R-001 | Auto backend route on Intel macOS | Yes | N/A | Yes | UC-001 |
| UC-002 | R-002 | Explicit Kokoro backend on Intel macOS | Yes | N/A | Yes | UC-002 |
| UC-003 | R-003 | Auto bootstrap install on Intel macOS | Yes | Yes | Yes | UC-003 |
| UC-004 | R-004 | Manual installer route for Intel macOS | Yes | Yes | Yes | UC-004 |
| UC-005 | R-005 | Playback command selection with fallback | Yes | Yes | Yes | UC-005 |

## Change Traceability To Implementation Plan

| Change ID | Implementation Plan Task(s) | Verification (Unit/Integration/E2E/Manual) | Status |
| --- | --- | --- | --- |
| C-001 | T-001 | unit tests (`test_platform.py`) | Planned |
| C-002 | T-002 | unit tests (`test_runtime_bootstrap.py`) | Planned |
| C-003 | T-003 | manual script smoke + bootstrap path test | Planned |
| C-004 | T-004 | manual script dispatch checks | Planned |
| C-005 | T-005 | unit tests (runner path) + manual playback check | Planned |
| C-006 | T-006 | pytest | Planned |
| C-007 | T-007 | README consistency review | Planned |

## Design Feedback Loop Notes (From Review/Implementation)

| Date | Trigger (Review/File/Test/Blocker) | Classification (`Local Fix`/`Design Impact`/`Requirement Gap`) | Design Smell | Requirements Updated? | Design Update Applied | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-02-24 | initial design | N/A | None | No | v1 created | Open |

## Open Questions

- None blocking for implementation.
