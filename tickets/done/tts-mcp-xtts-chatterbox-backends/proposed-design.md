# Proposed Design

## Design Version

- Current Version: `v2`

## Revision History

| Version | Trigger | Summary Of Changes | Related Review Round |
| --- | --- | --- | --- |
| v1 | Initial draft | Added XTTS and Chatterbox as explicit wrapper-backed backends without changing `auto` routing. | 1-2 |
| v2 | Stage 8 design-impact re-entry | Redefined the runner area around spine-led ownership: thin orchestration in `runner.py`, backend launch contracts moved out, Kokoro runtime moved out, and generic execution/playback support moved out. | 3-4 |

## Artifact Basis

- Investigation Notes: `tickets/done/tts-mcp-xtts-chatterbox-backends/investigation-notes.md`
- Requirements: `tickets/done/tts-mcp-xtts-chatterbox-backends/requirements.md`
- Requirements Status: `Design-ready`
- Shared Design Principles: `shared/design-principles.md`

## Summary

Keep the public MCP `speak` API unchanged and keep current `auto` routing unchanged, but refactor the `tts-mcp` runner area so one file no longer owns orchestration, backend launch policy, Kokoro synthesis, and generic execution support at the same time.

The target architecture keeps the current package flat and introduces four explicit owners around the `runner.py` orchestration spine:

- `backend_commands.py`
  - command construction for MLX / llama / XTTS / Chatterbox
- `backend_contracts.py`
  - backend language/env/failure/playback policy
- `kokoro_runtime.py`
  - Kokoro in-process synthesis and its bounded local runtime flow
- `execution_support.py`
  - output path, output signatures, subprocess execution, locks, and Linux playback helpers

## Goal / Intended Change

- Preserve the clean public MCP boundary:
  - `speak(text, output_path=None, play=True)`
- Preserve explicit XTTS and Chatterbox backend support.
- Preserve current MLX Audio, Kokoro ONNX, and llama.cpp behavior.
- Preserve current `auto` backend routing.
- Refactor the runner area so each changed source file has one concrete owner and stays under the workflow structural gates.

## Legacy Removal Policy

- Policy: `No backward compatibility; remove legacy code paths.`
- In-scope removal:
  - remove mixed-concern helper ownership from `runner.py`
  - remove runner-local copies of backend language/env/error policy
  - remove runner-local ownership of Kokoro runtime loading and synthesis
  - remove runner-local ownership of generic subprocess/output/playback helpers
- Out of scope:
  - changing the MCP tool signature
  - removing any existing backend

## Requirements And Use Cases

| Requirement ID | Description | Acceptance Criteria Summary | Use Case IDs |
| --- | --- | --- | --- |
| R-001 | `speak` remains the MCP tool surface. | Public MCP API stays minimal and unchanged. | UC-001, UC-002, UC-003, UC-004 |
| R-002 | XTTS and Chatterbox remain explicit opt-in backends. | Explicit backend selection reaches the correct execution owner. | UC-001, UC-002 |
| R-003 | Existing backend behavior remains unchanged unless explicitly selected otherwise. | `auto`, MLX, Kokoro, and llama paths remain behaviorally stable. | UC-003, UC-004 |
| R-004 | Heavy Torch runtimes stay isolated from the base MCP runtime. | XTTS and Chatterbox continue to run through wrapper scripts and dedicated virtualenvs. | UC-001, UC-002 |
| R-005 | The refactor must improve architectural quality, not only behavior. | `runner.py` stops owning unrelated support concerns and Stage 8 becomes passable. | UC-001, UC-002, UC-003, UC-004 |

## Current-State Read

| Area | Findings | Evidence | Open Unknowns |
| --- | --- | --- | --- |
| Entrypoints / Current Spine | The main runtime spine is already coherent at the API level: `server.speak -> runner.run_speak -> backend execution -> playback/result`. | `server.py`, `runner.py` | None |
| Current Ownership Boundaries | `runner.py` is overloaded: it owns orchestration, command contracts, backend policy, Kokoro synthesis, and generic execution support. | `runner.py`, `code-review.md` | None |
| Current Coupling / Fragmentation Problems | The issue is not missing layers; it is support concerns sitting inside the main-line owner instead of serving it from clear side owners. | `runner.py`, `investigation-notes.md` | None |
| Existing Constraints / Compatibility Facts | `server.py`, `config.py`, `platform.py`, `runtime_bootstrap.py`, and `version_check.py` already have natural ownership and should be reused, not replaced. | `tts_mcp/*.py` | None |
| Relevant Files / Components | The redesign target is the `runner` area only. | `runner.py` and adjacent files | None |

## Data-Flow Spine Inventory

| Spine ID | Scope | Start | End | Owning Node / Governing Owner | Why It Matters |
| --- | --- | --- | --- | --- | --- |
| DS-001 | Primary End-to-End | `server.speak(...)` | `SpeakResult` returned to MCP host | `runner.run_speak(...)` | This is the main user-visible generation spine for all backends. |
| DS-002 | Primary End-to-End | `runner.run_speak(...)` | external wrapper process exits and output is validated | `backend_commands.py` + `execution_support.py` | This is the command-backend spine for MLX / llama / XTTS / Chatterbox. |
| DS-003 | Primary End-to-End | `runner.run_speak(...)` | Kokoro WAV exists and is validated | `kokoro_runtime.py` + `execution_support.py` | Kokoro remains in-process and therefore needs a distinct owner from command-backed generation. |
| DS-004 | Bounded Local | `kokoro_runtime.run_kokoro_generation(...)` | PCM WAV write completed | `kokoro_runtime.py` | The Chinese phonemization/runtime-load/model-path flow materially shapes Kokoro behavior and must be explicit. |

## Primary Execution / Data-Flow Spine(s)

- `server.speak -> runner.run_speak -> backend execution owner -> execution_support -> SpeakResult`
- `server.speak -> runner.run_speak -> kokoro_runtime.run_kokoro_generation -> execution_support -> SpeakResult`

## Spine Actors / Main-Line Nodes

| Node | Role In Spine | What It Advances |
| --- | --- | --- |
| `server.speak` | MCP boundary | Public tool invocation only |
| `runner.run_speak` | Main-line orchestrator | Validation, sequencing, result shaping |
| `backend_commands` | Command-backend launch owner | Builds launch contracts for MLX / llama / XTTS / Chatterbox |
| `kokoro_runtime` | Kokoro generation owner | In-process Kokoro synthesis path |
| `execution_support` | Shared runtime support owner | Output resolution, execution, locking, playback, signature checks |

## Spine Narratives

| Spine ID | Short Narrative | Main Domain Subject Nodes | Governing Owner | Key Support Branches |
| --- | --- | --- | --- | --- |
| DS-001 | The MCP server forwards a `speak` request to a runner that validates the request, chooses a backend, delegates generation to the correct execution owner, validates the WAV, optionally plays it, and returns a structured result. | `server.speak`, `runner.run_speak` | `runner.py` | `platform.py`, `version_check.py`, `execution_support.py` |
| DS-002 | For command-backed backends, the runner asks `backend_commands.py` to build the correct command contract and env inputs, then asks `execution_support.py` to run it and validate the produced output. | `runner.run_speak`, `backend_commands.py`, `execution_support.py` | `runner.py` | `backend_contracts.py` |
| DS-003 | For Kokoro, the runner delegates synthesis to `kokoro_runtime.py`, which owns runtime loading, language/voice selection, optional Chinese phonemization, and WAV emission before common output/playback handling resumes. | `runner.run_speak`, `kokoro_runtime.py` | `runner.py` | `backend_contracts.py`, `execution_support.py` |
| DS-004 | Inside Kokoro, a bounded local flow resolves language/profile paths, loads the runtime, optionally phonemizes Chinese text, synthesizes audio, and writes PCM WAV data. | `kokoro_runtime.py` | `kokoro_runtime.py` | none |

## Ownership Map

| Node / Owner | Owns | Must Not Own | Notes |
| --- | --- | --- | --- |
| `server.py` | MCP tool signature and host boundary | backend policy, output validation, playback | Keep unchanged |
| `runner.py` | request validation, sequencing, shared result shaping | command construction, runtime loading internals, generic subprocess helpers | This is the primary file to shrink |
| `backend_commands.py` | command argument construction for MLX / llama / XTTS / Chatterbox | subprocess execution, output validation, result shaping | Support owner for command-backed generation |
| `backend_contracts.py` | backend language normalization, env policy, failure/playback markers | main-line sequencing | Shared backend policy owner |
| `kokoro_runtime.py` | Kokoro runtime loading and synthesis | MCP orchestration, generic subprocess helpers | Separate because Kokoro is not command-backed |
| `execution_support.py` | output path/signature helpers, lock, subprocess execution, playback command selection | backend-specific launch policy | Shared runtime support owner |
| `platform.py` | backend selection and explicit/auto policy | command construction | Reuse unchanged owner |
| `version_check.py` | runtime freshness validation | generation sequencing | Reuse unchanged owner |

## Support Structure Around The Spine

| Support Branch / Service | Serves Which Owner | Responsibility | Must Stay Off Main Line? |
| --- | --- | --- | --- |
| `platform.py` | `runner.py` | backend selection | Yes |
| `version_check.py` | `runner.py` | runtime freshness gate | Yes |
| `backend_contracts.py` | `backend_commands.py`, `kokoro_runtime.py`, `runner.py` | backend-specific normalization and failure/env policy | Yes |
| `execution_support.py` | `runner.py` | output path, subprocess, lock, playback, signature helpers | Yes |

## Existing Capability / Subsystem Reuse Check

| Need / Concern | Existing Capability Area / Subsystem | Decision | Why | If New, Why Existing Areas Are Not Right |
| --- | --- | --- | --- | --- |
| Public MCP boundary | `server.py` | Reuse | Already correct and intentionally small. |  |
| Backend selection | `platform.py` | Reuse | Already owns explicit vs `auto` backend policy. |  |
| Runtime bootstrap | `runtime_bootstrap.py` | Reuse | No architectural issue was found there. |  |
| Runtime freshness checks | `version_check.py` | Reuse | Already owns version-gating behavior. |  |
| Command-backend launch contracts | `runner.py` today | Create New owner (`backend_commands.py`) | This concern is real and separate from orchestration. | `runner.py` is overloaded; no existing file owns command contracts cleanly. |
| Backend language/env/failure policy | `runner.py` today | Create New owner (`backend_contracts.py`) | The same policy is shared across multiple backends and should not stay embedded in the orchestrator. | No current file besides `runner.py` owns backend contract normalization. |
| Kokoro in-process synthesis | `runner.py` today | Create New owner (`kokoro_runtime.py`) | Kokoro is a full in-process runtime with a bounded local spine. | It does not fit `backend_commands.py` because it is not command-backed. |
| Output/lock/playback helpers | `runner.py` today | Create New owner (`execution_support.py`) | These helpers are cross-backend runtime support. | They do not belong in `backend_commands.py` or `kokoro_runtime.py`. |

## Ownership-Driven Dependency Rules

- Allowed dependency directions:
  - `server.py -> runner.py`
  - `runner.py -> platform.py`
  - `runner.py -> version_check.py`
  - `runner.py -> backend_commands.py`
  - `runner.py -> backend_contracts.py`
  - `runner.py -> kokoro_runtime.py`
  - `runner.py -> execution_support.py`
  - `backend_commands.py -> backend_contracts.py`
  - `kokoro_runtime.py -> backend_contracts.py`
  - `kokoro_runtime.py -> execution_support.py` only for path helpers if needed
- Forbidden shortcuts:
  - `server.py` must not call command builders or runtime support directly.
  - `backend_commands.py` must not execute subprocesses directly.
  - `execution_support.py` must not own backend-specific language normalization.
  - `backend_contracts.py` must not become a second orchestrator.

## Architecture Direction Decision

- Chosen direction:
  - Split the `runner.py` support branches into explicit flat files while keeping one orchestration entrypoint.
- Rationale:
  - `complexity`: removes mixed-concern growth from the runner without inventing a new subsystem
  - `testability`: command-building, backend policy, Kokoro runtime, and execution helpers become independently testable
  - `operability`: runtime contracts stay explicit and easy to inspect
  - `evolution cost`: future backend additions no longer require growing one monolithic runner
- Data-flow spine clarity assessment: `Yes`
- Ownership clarity assessment: `Yes`
- Support structure clarity assessment: `Yes`
- File placement within the owning subsystem assessment: `Yes`
- Outcome: `Split`

## Optional Alternatives

| Option | Summary | Pros | Cons | Decision | Rationale |
| --- | --- | --- | --- | --- | --- |
| A | Keep a flat package and split the runner area into four new support files. | Best fit for current package scale; avoids empty indirection. | Adds several new files. | Chosen | Fixes ownership without over-structuring the package. |
| B | Create a new `tts_mcp/runtime/` subpackage and move all runner-adjacent code there. | Strong visual separation. | Over-splits a still-small package and adds path churn without new owners. | Rejected | The problem is ownership overload, not missing folder depth. |

## Change Inventory

| Change ID | Change Type | Current Path | Target Path | Rationale | Impacted Areas |
| --- | --- | --- | --- | --- | --- |
| C-001 | Modify | `tts-mcp/src/tts_mcp/runner.py` | same | Reduce the file to orchestration and result shaping. | Main runtime spine |
| C-002 | Add | N/A | `tts-mcp/src/tts_mcp/backend_commands.py` | Own command-backed launch contracts. | MLX / llama / XTTS / Chatterbox |
| C-003 | Add | N/A | `tts-mcp/src/tts_mcp/backend_contracts.py` | Own backend normalization/env/failure/playback policy. | Shared backend policy |
| C-004 | Add | N/A | `tts-mcp/src/tts_mcp/kokoro_runtime.py` | Own Kokoro runtime loading and synthesis. | Kokoro |
| C-005 | Add | N/A | `tts-mcp/src/tts_mcp/execution_support.py` | Own output path/signature, subprocess, lock, and playback helpers. | Shared runtime support |
| C-006 | Modify | `tts-mcp/tests/test_runner.py` and related tests | same | Re-point tests to the new file owners while preserving behavior coverage. | Tests |

## Removal / Decommission Plan

| Item To Remove / Decommission | Why It Becomes Unnecessary | Replaced By Which Owner / File / Structure | Scope |
| --- | --- | --- | --- |
| `_build_mlx_command`, `_build_llama_command`, `_build_xtts_command`, `_build_chatterbox_command` inside `runner.py` | Command contracts become a separate owner. | `backend_commands.py` | In This Change |
| backend language alias dicts and language resolvers inside `runner.py` | Shared backend policy no longer belongs in the orchestrator. | `backend_contracts.py` | In This Change |
| `_resolve_mlx_subprocess_env`, `_resolve_xtts_subprocess_env`, XTTS failure classification helpers in `runner.py` | Shared backend runtime policy becomes explicit. | `backend_contracts.py` | In This Change |
| `_run_kokoro_onnx` and Kokoro runtime loaders from `runner.py` | Kokoro has its own bounded local runtime spine. | `kokoro_runtime.py` | In This Change |
| `_execute`, output helpers, lock helpers, playback command helpers in `runner.py` | Shared execution support should not live inside the orchestrator. | `execution_support.py` | In This Change |

## Final File Responsibility Mapping

| File | Owning Capability Area | Owner / Boundary | Concrete Concern | Why This Is One File |
| --- | --- | --- | --- | --- |
| `server.py` | MCP boundary | Public tool boundary | Expose `speak` only | The public API remains intentionally minimal. |
| `runner.py` | Runtime orchestration | Main-line sequencer | Validate request, choose flow, coordinate generation, shape result | One file owns one end-to-end orchestration subject. |
| `backend_commands.py` | Command-backed generation | Launch-contract owner | Build commands for MLX / llama / XTTS / Chatterbox | These backends share one kind of concern: external command launch shape. |
| `backend_contracts.py` | Shared backend policy | Normalization/policy owner | Language/env/failure/playback policy | These rules repeat across backends and deserve one owner. |
| `kokoro_runtime.py` | Kokoro runtime | In-process synthesis owner | Load Kokoro runtime, resolve profiles, synthesize WAV | Kokoro is a distinct non-command runtime. |
| `execution_support.py` | Shared runtime support | Runtime support owner | Output paths, signatures, subprocesses, locks, playback helpers | Shared support should stay off the main line. |
| `platform.py` | Backend selection | Selection owner | Explicit/auto backend resolution | Already correct. |
| `version_check.py` | Runtime freshness | Version gate owner | Backend runtime freshness checks | Already correct. |

## Derived Implementation Mapping

| Target File | Change Type | Mapped Spine ID | Owner / Support Branch | Responsibility | Key APIs / Interfaces |
| --- | --- | --- | --- | --- | --- |
| `tts-mcp/src/tts_mcp/runner.py` | Modify | DS-001 | Main-line owner | `run_speak(...)`, `SpeakResult`, result shaping | `run_speak`, `_error_result` |
| `tts-mcp/src/tts_mcp/backend_commands.py` | Add | DS-002 | Support branch | Build command lines for command-backed backends | `build_mlx_command`, `build_llama_command`, `build_xtts_command`, `build_chatterbox_command` |
| `tts-mcp/src/tts_mcp/backend_contracts.py` | Add | DS-002, DS-003 | Support branch | Normalize language codes, env overrides, failure markers | `resolve_*_language_code`, `resolve_*_subprocess_env`, `classify_generation_failure` |
| `tts-mcp/src/tts_mcp/kokoro_runtime.py` | Add | DS-003, DS-004 | Main generation owner for Kokoro | In-process Kokoro generation | `run_kokoro_generation` |
| `tts-mcp/src/tts_mcp/execution_support.py` | Add | DS-001, DS-002, DS-003 | Support branch | Path, execution, locking, playback helpers | `resolve_output_path`, `execute_command`, `output_signature`, `build_linux_play_command`, lock helpers |

## File Placement And Ownership Check

| File | Current Path | Target Path | Path Matches Concern? | Flat-Or-Over-Split Risk | Action | Rationale |
| --- | --- | --- | --- | --- | --- | --- |
| `runner.py` | `tts-mcp/src/tts_mcp/runner.py` | same | Yes after split | Low | Split | Keep the public internal entrypoint stable but reduce responsibility. |
| `backend_commands.py` | N/A | `tts-mcp/src/tts_mcp/backend_commands.py` | Yes | Low | Add | Flat placement is clearer than a new subfolder for one concern. |
| `backend_contracts.py` | N/A | `tts-mcp/src/tts_mcp/backend_contracts.py` | Yes | Low | Add | Shared policy is package-level support, not a new subsystem. |
| `kokoro_runtime.py` | N/A | `tts-mcp/src/tts_mcp/kokoro_runtime.py` | Yes | Low | Add | Distinct runtime owner with clear name. |
| `execution_support.py` | N/A | `tts-mcp/src/tts_mcp/execution_support.py` | Yes | Low | Add | Cross-backend runtime support stays readable in the flat package. |

## Concrete Examples / Shape Guidance

| Topic | Good Example | Bad / Avoided Shape | Why The Example Matters |
| --- | --- | --- | --- |
| Main orchestration shape | `server.speak -> runner.run_speak -> backend owner -> execution support -> SpeakResult` | `server.speak -> runner.py` silently owns command building, env policy, Kokoro synthesis, locks, and playback itself | It shows the desired support branches around the spine instead of keeping everything in one file. |

## Backward-Compatibility Rejection Log

| Candidate Compatibility Mechanism | Why It Was Considered | Rejection Decision | Replacement Clean-Cut Design |
| --- | --- | --- | --- |
| Keep the current monolithic `runner.py` and only move a few lines to satisfy the line gate | Smallest diff | Rejected | Split by actual ownership so Stage 8 passes for architectural reasons, not cosmetic reasons. |
| Add a second orchestration facade while keeping the old runner helpers underneath | Could preserve old helper names | Rejected | Move the real owners out and keep only one orchestration entrypoint. |

## Naming Decisions

| Item Type | Current Name | Proposed Name | Reason |
| --- | --- | --- | --- |
| File | N/A | `backend_commands.py` | Directly names the command-backed concern it owns. |
| File | N/A | `backend_contracts.py` | Signals that this file owns backend-normalization and runtime contract policy. |
| File | N/A | `kokoro_runtime.py` | Says clearly that the file owns the Kokoro runtime path. |
| File | N/A | `execution_support.py` | Says clearly that the file is shared runtime support, not orchestration. |

## Existing-Structure Bias Check

| Candidate Area | Current-File-Layout Bias Risk | Architecture-First Alternative | Decision | Why |
| --- | --- | --- | --- | --- |
| `runner.py` | High | Keep only orchestration there and move support owners out. | Change | The Stage 8 finding showed that preserving the existing file as the owner was the architectural mistake. |
| Package folder depth | Medium | Add a new subpackage for runtime concerns. | Keep flat package | A new folder would add path churn without creating clearer owners than flat package-level files. |
