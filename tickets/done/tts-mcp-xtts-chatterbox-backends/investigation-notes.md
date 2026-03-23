# Investigation Notes

## Scope Triage

- Proposed scope: `Medium`
- Current re-entry scope: `Medium`
- Reasoning:
  - The original backend expansion is implemented, but Stage 8 exposed a file-ownership design failure rather than a behavioral gap.
  - The re-entry work does not change requirements, but it does change how the runtime orchestration is partitioned across source files.
  - The fix touches the primary execution spine (`server -> runner -> backend execution`) plus shared runtime support concerns, so a full architecture refresh is required before more code edits.

## Sources Consulted

### Local Repository

- `tickets/done/tts-mcp-xtts-chatterbox-backends/workflow-state.md`
- `tickets/done/tts-mcp-xtts-chatterbox-backends/code-review.md`
- `tickets/done/tts-mcp-xtts-chatterbox-backends/proposed-design.md`
- `tickets/done/tts-mcp-xtts-chatterbox-backends/future-state-runtime-call-stack.md`
- `tickets/done/tts-mcp-xtts-chatterbox-backends/future-state-runtime-call-stack-review.md`
- `tts-mcp/src/tts_mcp/server.py`
- `tts-mcp/src/tts_mcp/config.py`
- `tts-mcp/src/tts_mcp/platform.py`
- `tts-mcp/src/tts_mcp/runtime_bootstrap.py`
- `tts-mcp/src/tts_mcp/runner.py`
- `tts-mcp/src/tts_mcp/version_check.py`

### Workflow References

- `software-engineering-workflow-skill/shared/design-principles.md`
- `software-engineering-workflow-skill/stages/01-investigation/investigation-guide.md`
- `software-engineering-workflow-skill/stages/03-design/proposed-design-template.md`
- `software-engineering-workflow-skill/stages/05-future-state-runtime-call-stack-review/future-state-runtime-call-stack-review-template.md`

## Current Entrypoints And Boundaries

- MCP entrypoint:
  - `tts_mcp.server.speak(...)`
  - Owns only the public MCP tool boundary and forwards to the runner.
- Runtime orchestration entrypoint:
  - `tts_mcp.runner.run_speak(...)`
  - Owns request validation, backend selection sequencing, generation/playback sequencing, and result shaping.
- Backend-selection boundary:
  - `tts_mcp.platform.select_backend(...)`
  - Owns explicit backend resolution and `auto` policy.
- Runtime freshness boundary:
  - `tts_mcp.version_check.check_backend_runtime_version(...)`
  - Owns version validation policy.
- Runtime bootstrap boundary:
  - `tts_mcp.runtime_bootstrap.bootstrap_runtime(...)`
  - Owns install/setup flow before `speak`.

## Stage 8 Re-Entry Trigger

- Trigger stage: `8`
- Classification: `Design Impact`
- Recorded blocker:
  - `tts-mcp/src/tts_mcp/runner.py` is `1040` effective non-empty lines.
  - The current diff for `runner.py` is `222` changed lines.
  - The file mixes multiple distinct concerns that no longer share one natural owner.

## Current-State Read After The Review Failure

| Area | Findings | Evidence | Open Unknowns |
| --- | --- | --- | --- |
| Entrypoints / Current Spine | The main execution spine is still clear at a high level: `server.speak -> runner.run_speak -> backend generation -> playback/result`. The failure is not about the public API; it is about too much support structure being absorbed into the runner. | `tts-mcp/src/tts_mcp/server.py`, `tts-mcp/src/tts_mcp/runner.py` | None |
| Current Ownership Boundaries | `runner.py` now owns five different categories of work: request/result orchestration, command-backend argument construction, backend language/env/error policy, Kokoro in-process synthesis, and generic subprocess/output/playback helpers. | `tts-mcp/src/tts_mcp/runner.py` | None |
| Current Coupling / Fragmentation Problems | The file is not fragmented into many tiny helpers; instead it is overloaded into one mixed-concern coordinator. This weakens ownership clarity even though behavior still works. | `tts-mcp/src/tts_mcp/runner.py` | None |
| Existing Constraints / Compatibility Facts | The MCP `speak` API must remain minimal. `auto` backend behavior must stay unchanged. German Orpheus MLX remains the preferred German-quality path. XTTS and Chatterbox remain explicit optional backends. | `requirements.md`, `server.py`, earlier ticket notes | None |
| Relevant Files / Components | `config.py`, `platform.py`, `runtime_bootstrap.py`, and `version_check.py` already have coherent ownership and do not need a new subsystem. The redesign target is the runner area only. | `tts-mcp/src/tts_mcp/*.py`, `code-review.md` | None |

## Ownership Failure Breakdown

### Concern 1: Runtime orchestration

- Current owner: `runner.py`
- Should stay in `runner.py`
- Concrete ownership:
  - validate `text`, `speed`, and `instruct`
  - sequence backend selection, version checks, generation, playback, cleanup, and result shaping

### Concern 2: Command-backend launch contracts

- Current owner: `runner.py`
- Should move to a dedicated file
- Concrete ownership:
  - MLX / llama / XTTS / Chatterbox command construction
  - per-backend command argument shape
  - command-only validation tied to those launch contracts

### Concern 3: Backend runtime policy

- Current owner: `runner.py`
- Should move to a dedicated file
- Concrete ownership:
  - language-code normalization by backend family
  - XTTS TOS env forwarding
  - MLX offline-cache env forwarding
  - XTTS failure classification and MLX playback confirmation markers

### Concern 4: Kokoro in-process synthesis

- Current owner: `runner.py`
- Should move to a dedicated file
- Concrete ownership:
  - Kokoro runtime loading
  - Chinese phonemization branch
  - model/voice/vocab-path resolution
  - WAV write for in-process synthesis

### Concern 5: Generic execution and playback support

- Current owner: `runner.py`
- Should move to a dedicated file
- Concrete ownership:
  - output-path resolution
  - output signature comparison
  - subprocess execution
  - global generation lock
  - Linux playback command selection

## Likely File Placement Concerns

- Keep the package layout flat under `tts-mcp/src/tts_mcp/`.
- Do not introduce a new subpackage just to split one overloaded file; that would be structural overreaction for a medium-scope package.
- Preferred new ownership split:
  - `runner.py`
    - orchestration entrypoint and `SpeakResult`
  - `backend_commands.py`
    - command builders for MLX / llama / XTTS / Chatterbox
  - `backend_contracts.py`
    - backend language/env/failure/playback policy
  - `kokoro_runtime.py`
    - in-process Kokoro synthesis and related bounded local runtime flow
  - `execution_support.py`
    - output path, signatures, subprocess execution, locks, and playback command helpers

## Constraints

- No requirements change is needed; this is not a requirement gap.
- The public MCP `speak` signature should remain unchanged.
- `server.py`, `config.py`, `platform.py`, `runtime_bootstrap.py`, and `version_check.py` should keep their current ownership boundaries.
- The redesign should remove overloaded helper placement from `runner.py`, not re-wrap it with empty indirection.
- Each changed source file in the refactor path should stay below the workflow hard limits:
  - `<=500` effective non-empty lines
  - avoid new source-file diffs above the `>220` delta gate where possible

## Design Implications

- The redesign target is a thinner `runner.py`, not a new orchestration subsystem.
- The primary spine should remain:
  - `server.speak -> runner.run_speak -> backend execution owner -> execution support -> result`
- Support branches should become explicit:
  - `platform` and `version_check` serve `runner`
  - `backend_contracts` serves `backend_commands` and `kokoro_runtime`
  - `execution_support` serves `runner`
- The Stage 3 redesign must name which helpers are removed from `runner.py` and which new owners replace them.
