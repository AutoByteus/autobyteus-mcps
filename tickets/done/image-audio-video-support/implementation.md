# Implementation

## Scope Classification

- Classification: `Medium`
- Reasoning: additive video support crosses dependency pins, service runtime, MCP schema, CLI command surface, docs, local tests, and optional remote integration.
- Workflow Depth: proposed design -> future-state runtime call stack -> two-round future-state review -> implementation baseline -> source execution.

## Upstream Artifacts

- Workflow state: `tickets/in-progress/image-audio-video-support/workflow-state.md`
- Investigation notes: `tickets/in-progress/image-audio-video-support/investigation-notes.md`
- Requirements: `tickets/in-progress/image-audio-video-support/requirements.md`
  - Current Status: `Design-ready`
- Proposed design: `tickets/in-progress/image-audio-video-support/proposed-design.md`
- Runtime call stacks: `tickets/in-progress/image-audio-video-support/future-state-runtime-call-stack.md`
- Future-state runtime call stack review: `tickets/in-progress/image-audio-video-support/future-state-runtime-call-stack-review.md`

## Document Status

- Current Status: `Ready For Implementation`
- Notes: baseline finalized after Stage 5 `Go Confirmed`; source edits may start only after `workflow-state.md` unlocks code edits.

## Plan Baseline

### Preconditions

- `requirements.md` is at least `Design-ready`: `Yes`
- Acceptance criteria use stable IDs with measurable expected outcomes: `Yes`
- `workflow-state.md` is current and Stage 5 review-gate evidence is recorded: `Yes`
- Runtime call stack review artifact exists and is current: `Yes`
- All in-scope use cases reviewed: `Yes`
- No unresolved blocking findings: `Yes`
- Future-state runtime call stack review has `Go Confirmed`: `Yes`
- Missing-use-case discovery sweeps completed for final two clean rounds: `Yes`
- No newly discovered use cases in final two clean rounds: `Yes`

### Solution Sketch

- Use Cases In Scope: UC-001 through UC-005.
- Spine Inventory In Scope: DS-001 MCP video generation, DS-002 CLI video generation, DS-003 model/default discovery, DS-004 regression.
- Primary Owners / Main Domain Subjects: `server.py` MCP facade, `cli.py` CLI facade, `services.py` runtime service boundary, Autobyteus `VideoClientFactory`.
- Requirement Coverage Guarantee: every requirement maps to at least one use case and at least one acceptance criterion.
- Design-Risk Use Cases: no package rename, no exposed `session_id`, no generic media selector, no direct VideoClientFactory usage in facades.
- Target Architecture Shape: MCP/CLI facades delegate to `services.py`; services owns model resolution, media/path normalization, video client lifecycle, output download, and cleanup.
- New Owners/Boundary Interfaces To Introduce: no new file-level owner; add peer video functions to existing owners.
- Primary file/task set: see Implementation Work Table.
- API/Behavior Delta: add `list_video_models`, `generate_video`, `list-video-models`, `generate-video`, and health default `default_video_generation_model`.
- Key Assumptions: `autobyteus==1.4.4` is available and contains video multimedia APIs.
- Known Risks: live remote video generation can fail due backend browser/login/rate-limit state; local tests must isolate implementation behavior.

### Runtime Call Stack Review Gate Summary

| Round | Review Result | Findings Requiring Persisted Updates | New Use Cases Discovered | Persisted Updates Completed | Classification | Required Re-Entry Path | Round State | Clean Streak After Round |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Pass | No | No | N/A | N/A | N/A | Candidate Go | 1 |
| 2 | Pass | No | No | N/A | N/A | N/A | Go Confirmed | 2 |

### Go / No-Go Decision

- Decision: `Go`
- Evidence:
  - Final review round: `2`
  - Clean streak at final round: `2`
  - Final review gate line: `Implementation can start: Yes`

### Spine-Led Dependency And Sequencing Map

| Order | Spine ID | Owner | Task / File | Depends On | Why This Order |
| --- | --- | --- | --- | --- | --- |
| 1 | DS-001 through DS-003 | Package runtime | dependency pins/lock | N/A | Video imports require `autobyteus==1.4.4`. |
| 2 | DS-001, DS-003 | `services.py` | service video model/default/generation support | 1 | Facades depend on service functions. |
| 3 | DS-001, DS-003 | `server.py` | MCP video tools | 2 | MCP surface delegates to services. |
| 4 | DS-002, DS-003 | `cli.py` | CLI video commands | 2 | CLI surface delegates to services. |
| 5 | all | Tests | local and optional remote tests | 2-4 | Validate behavior after public surfaces exist. |
| 6 | all | Docs | README/DESIGN/root docs | 2-5 | Docs should describe final behavior. |

### File Placement Plan

| Item | Current Path | Target Path | Owning Concern / Platform | Action | Verification |
| --- | --- | --- | --- | --- | --- |
| dependency pins | package dependency files | same | package runtime | Keep/Modify | `uv --frozen` works. |
| video service support | `src/image_audio_mcp/services.py` | same | runtime service | Keep/Modify | service tests. |
| MCP video tools | `src/image_audio_mcp/server.py` | same | MCP facade | Keep/Modify | in-memory MCP tests. |
| CLI video commands | `src/image_audio_mcp/cli.py` | same | CLI facade | Keep/Modify | CLI tests. |
| tests | package `tests/` | same | package validation | Keep/Modify | pytest. |
| docs | package/root docs | same | user docs | Keep/Modify | docs sync review. |

### Implementation Work Table

| Change ID | Spine ID(s) | Owner | Concern | Current Path | Target Path | Action | Depends On | Implementation Status | Unit Test File | Unit Test Status | Integration Test File | Integration Test Status | Stage 8 Review Status | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T-001 | DS-001 through DS-003 | Package runtime | dependency update | dependency files | same | Modify | N/A | Completed | N/A | N/A | N/A | N/A | Planned | `autobyteus==1.4.4`; lock updated. |
| T-002 | DS-001, DS-003 | `services.py` | video default/model list/generation | `services.py` | same | Modify | T-001 | Completed | `tests/test_services_local.py` | Passed | N/A | N/A | Planned | Added private model metadata serializer. |
| T-003 | DS-001, DS-003 | `server.py` | MCP video tools/schema | `server.py` | same | Modify | T-002 | Completed | `tests/test_server_local.py` | Passed | N/A | N/A | Planned | No `session_id`. |
| T-004 | DS-002, DS-003 | `cli.py` | CLI video commands | `cli.py` | same | Modify | T-002 | Completed | `tests/test_cli_local.py` | Passed | N/A | N/A | Planned | Repeatable image/audio/video flags. |
| T-005 | all | Tests | local + optional remote coverage | `tests/*.py` | same | Modify | T-002 through T-004 | Completed | package tests | Passed | `tests/test_integration.py` | Passed | Planned | Remote video skips by default. |
| T-006 | all | Docs | user-facing docs | READMEs/DESIGN | same | Modify | T-002 through T-005 | Completed | N/A | N/A | N/A | N/A | Planned | Describes multimedia scope without rename. |

### Requirement, Spine, And Design Traceability

| Requirement | Acceptance Criteria ID(s) | Spine ID(s) | Design Section | Use Case / Call Stack | Planned Task ID(s) | Stage 6 Verification | Stage 7 Scenario ID(s) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R-001 | AC-002, AC-010 | DS-001 through DS-004 | Naming Decisions | UC-001 through UC-005 | T-003, T-004, T-006 | Unit + docs | AV-002, AV-010 |
| R-002 | AC-001 | DS-001 through DS-003 | Change Inventory | UC-001 through UC-004 | T-001 | Frozen command | AV-001 |
| R-003 | AC-004, AC-007 | DS-003 | Interface Boundary Mapping | UC-003 | T-002, T-003, T-004 | Unit | AV-004, AV-007 |
| R-004 | AC-002, AC-003, AC-005, AC-011 | DS-001 | Interface Boundary Mapping | UC-001, UC-002 | T-002, T-003, T-005 | Unit + optional integration | AV-002, AV-003, AV-005, AV-011 |
| R-005 | AC-003, AC-005, AC-006 | DS-001, DS-002 | Interface Boundary Mapping | UC-001, UC-002, UC-004 | T-002, T-003, T-004 | Unit | AV-003, AV-005, AV-006 |
| R-006 | AC-004, AC-005, AC-008 | DS-003 | Naming Decisions | UC-001 through UC-004 | T-002, T-003 | Unit | AV-004, AV-005, AV-008 |
| R-007 | AC-005 | DS-001 | Off-Spine Concerns | UC-001, UC-002, UC-004 | T-002 | Unit | AV-005 |
| R-008 | AC-006, AC-007 | DS-002, DS-003 | CLI spine | UC-004 | T-004 | Unit | AV-006, AV-007 |
| R-009 | AC-008 | DS-003 | Discovery spine | UC-003 | T-002, T-003 | Unit | AV-008 |
| R-010 | AC-002, AC-009 | DS-004 | Regression spine | UC-005 | T-005 | Unit | AV-009 |
| R-011 | AC-010 | DS-004 | Docs | UC-005 | T-006 | Docs review | AV-010 |
| R-012 | AC-001 through AC-011 | all | Validation | UC-001 through UC-005 | T-005 | Unit + optional integration | AV-001 through AV-011 |

### Stage 7 Planned Coverage Mapping

| Acceptance Criteria ID | Requirement ID | Spine ID(s) | Expected Outcome | Stage 7 Scenario ID(s) | Test Level | Initial Status |
| --- | --- | --- | --- | --- | --- | --- |
| AC-001 | R-002 | DS-001 through DS-003 | Frozen runtime uses `autobyteus==1.4.4`. | AV-001 | API | Planned |
| AC-002 | R-001/R-004/R-010 | DS-001/DS-004 | MCP tool inventory is additive and exact. | AV-002 | API | Planned |
| AC-003 | R-004/R-005 | DS-001 | MCP schema includes video fields and excludes `session_id`. | AV-003 | API | Planned |
| AC-004 | R-003/R-006 | DS-003 | Video models list shape is correct. | AV-004 | API | Planned |
| AC-005 | R-004/R-007 | DS-001 | Service video generation saves file and cleans up. | AV-005 | API | Planned |
| AC-006 | R-008 | DS-002 | CLI `generate-video` parses/dispatches. | AV-006 | API | Planned |
| AC-007 | R-003/R-008 | DS-003 | CLI `list-video-models` dispatches. | AV-007 | API | Planned |
| AC-008 | R-009 | DS-003 | Health includes video default. | AV-008 | API | Planned |
| AC-009 | R-010 | DS-004 | Existing tests pass. | AV-009 | API | Planned |
| AC-010 | R-011 | DS-004 | Docs synced. | AV-010 | API | Planned |
| AC-011 | R-004/R-012 | DS-001 | Optional remote MCP video test exists and skips by default. | AV-011 | E2E | Planned |

### Design Delta Traceability

| Change ID (Design) | Planned Task ID(s) | Includes Remove/Rename Work | Verification |
| --- | --- | --- | --- |
| C-001 through C-003 | T-001 | No | Frozen `uv`/pytest |
| C-004 | T-002 | Duplicate serialization decommission | service tests |
| C-005 | T-003 | No | server tests |
| C-006 | T-004 | No | CLI tests |
| C-007 | T-005 | No | pytest/integration skip |
| C-008 | T-006 | No project rename; docs update only | docs sync |

### Decommission / Rename Execution Tasks

| Task ID | Item | Action | Cleanup Steps | Risk Notes |
| --- | --- | --- | --- | --- |
| T-DEL-001 | Project rename idea | Remove from implementation path | Do not add alias package/scripts/env vars. | Stable package name remains. |
| T-DEL-002 | Triplicate model metadata serialization | Remove duplication risk | Add private metadata serializer in `services.py` and use for image/audio/video list functions. | Must preserve existing output shape. |

### Step-By-Step Plan

1. Update dependency pins/lock to `autobyteus==1.4.4`.
2. Implement service video default, model list, generation, and metadata serializer.
3. Implement MCP video model/generation tools.
4. Implement CLI video commands and flags.
5. Add/update local and optional remote tests.
6. Update docs.
7. Run local validation and update execution tracking.

### Backward-Compat And Decoupling Guardrails

- Backward-compatibility mechanisms introduced: `None`
- Legacy code retained for old behavior: `No`
- Dead/obsolete code or unused helpers/tests/flags/adapters left in scope: `No`
- Shared data structures remain tight: `Yes`
- Shared design/common-practice rules reapplied during implementation: `Yes`
- Authoritative Boundary Rule preserved: `Yes`
- Decoupling impact assessment completed: `Yes`
- New tight coupling or cyclic dependency introduced: `No`
- Changed source implementation files kept within proactive size-pressure guardrails: `Yes`

### Code Review Gate Plan

- Gate artifact path: `tickets/in-progress/image-audio-video-support/code-review.md`
- Source scope: `services.py`, `server.py`, `cli.py`; dependency/doc/test files reviewed for appropriate concerns.
- Line-count measurement command: `rg -n "\S" <file-path> | wc -l`
- Changed-line delta command: `git diff --numstat origin/main...HEAD -- <file-path>`
- Expected hotspot: `services.py` size growth. If source file exceeds 500 effective non-empty lines or source delta exceeds 220 lines with ownership pressure, split/refactor or classify upstream design impact.

| File | Current Line Count | Adds/Expands Functionality | Ownership/SoC Risk | Required Action | Expected Review Classification if not addressed |
| --- | --- | --- | --- | --- | --- |
| `services.py` | TBD during Stage 8 | Yes | Medium | Keep concise; extract only private serializer; avoid new unrelated helpers. | Design Impact if mixed concerns grow. |
| `server.py` | TBD during Stage 8 | Yes | Low | Keep facade thin. | Local Fix if schema issue only; Design Impact if runtime leaks in. |
| `cli.py` | TBD during Stage 8 | Yes | Low | Keep dispatch/parsing only. | Local Fix if parsing issue only; Design Impact if provider logic leaks in. |

### Test Strategy

- Unit/local tests:
  - service fake video client/download path
  - video model list dummy model
  - MCP public tool inventory and video schema
  - CLI `generate-video` and `list-video-models`
  - existing regression suite
- Integration tests:
  - existing opt-in remote tests retained
  - add optional remote `generate_video` test gated by env and default skip
- Stage 7 handoff:
  - canonical artifact path: `tickets/in-progress/image-audio-video-support/api-e2e-testing.md`
  - expected acceptance criteria count: 11
  - known environment constraints: live video requires configured Autobyteus server and may be slow/rate-limited.

### Cross-Reference Exception Protocol

| File | Cross-Reference With | Why Unavoidable | Temporary Strategy | Unblock Condition | Design Follow-Up Status | Owner |
| --- | --- | --- | --- | --- | --- | --- |
| N/A | N/A | N/A | N/A | N/A | Not Needed | N/A |

### Design Feedback Loop

| Smell/Issue | Evidence | Design Section To Update | Action | Status |
| --- | --- | --- | --- | --- |
| None | N/A | N/A | N/A | N/A |

## Execution Tracking

### Kickoff Preconditions Checklist

- Workflow state is current: `Yes`
- `workflow-state.md` shows `Current Stage = 6`: `Yes`
- `workflow-state.md` shows `Code Edit Permission = Unlocked` before source edits: `Yes`
- Scope classification confirmed: `Medium`
- Investigation notes are current: `Yes`
- Requirements status is `Design-ready` or `Refined`: `Yes`
- Future-state runtime call stack review final gate is `Implementation can start: Yes`: `Yes`
- Future-state runtime call stack review reached `Go Confirmed`: `Yes`
- No unresolved blocking findings: `Yes`

### Progress Log

- 2026-05-22: Implementation baseline created after Stage 5 `Go Confirmed`.
- 2026-05-22: Implemented video service, MCP, CLI, tests, dependency update, lockfile update, and docs.
- 2026-05-22: `uv --directory autobyteus-image-audio run --frozen --extra test pytest` passed with `25 passed, 3 skipped`.
- 2026-05-22: Wrapper health check from `/tmp` passed and reported `default_video_generation_model`.
- 2026-05-22: `uv --directory autobyteus-image-audio run --frozen autobyteus-image-audio list-video-models` passed and returned discovered video model metadata.

### Scope Change Log

| Date | Previous Scope | New Scope | Trigger | Required Action |
| --- | --- | --- | --- | --- |
| N/A | N/A | N/A | N/A | N/A |

### Implementation Work Updates

| Change ID | Last Failure Classification | Last Failure Investigation Required | Cross-Reference Smell | Design Follow-Up | Requirement Follow-Up | Last Verified | Verification Command | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T-001 | N/A | No | None | Not Needed | Not Needed | 2026-05-22 | `uv lock --upgrade-package autobyteus`; frozen pytest | Dependency updated to `1.4.4`. |
| T-002 | N/A | No | None | Not Needed | Not Needed | 2026-05-22 | `uv --directory autobyteus-image-audio run --frozen --extra test pytest` | Service tests passed. |
| T-003 | N/A | No | None | Not Needed | Not Needed | 2026-05-22 | `uv --directory autobyteus-image-audio run --frozen --extra test pytest` | MCP tests passed. |
| T-004 | N/A | No | None | Not Needed | Not Needed | 2026-05-22 | `uv --directory autobyteus-image-audio run --frozen --extra test pytest`; `autobyteus-image-audio list-video-models` | CLI tests and smoke passed. |
| T-005 | N/A | No | None | Not Needed | Not Needed | 2026-05-22 | `uv --directory autobyteus-image-audio run --frozen --extra test pytest` | Optional remote tests skipped by default. |
| T-006 | N/A | No | None | Not Needed | Not Needed | 2026-05-22 | `git diff --check` | Docs updated. |

### Downstream Stage Status Pointers

| Stage | Canonical Artifact | Current Status | Last Updated | Notes |
| --- | --- | --- | --- | --- |
| 7 API/E2E + Executable Validation | `tickets/in-progress/image-audio-video-support/api-e2e-testing.md` | Not Started | N/A | Starts after Stage 6 implementation/local verification. |
| 8 Code Review | `tickets/in-progress/image-audio-video-support/code-review.md` | Not Started | N/A | Starts after Stage 7 pass. |
| 9 Docs Sync | `tickets/in-progress/image-audio-video-support/docs-sync.md` | Not Started | N/A | Starts after Stage 8 pass. |

### Completion Gate

- Stage 6 implementation execution complete: `Yes`
