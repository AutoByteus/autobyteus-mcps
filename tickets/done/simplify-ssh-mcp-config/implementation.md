# Implementation - Simplify SSH MCP Configuration

## Scope Classification

- Classification: `Medium`
- Reasoning: config contract, runner command construction, tests, and docs change together.
- Workflow Depth: `Medium` -> proposed design -> future-state runtime call stack -> two-round review `Go Confirmed` -> implementation baseline -> execution.

## Upstream Artifacts

- Workflow state: `tickets/done/simplify-ssh-mcp-config/workflow-state.md`
- Investigation notes: `tickets/done/simplify-ssh-mcp-config/investigation-notes.md`
- Requirements: `tickets/done/simplify-ssh-mcp-config/requirements.md` (`Design-ready`)
- Proposed design: `tickets/done/simplify-ssh-mcp-config/proposed-design.md` (`v1`)
- Runtime call stacks: `tickets/done/simplify-ssh-mcp-config/future-state-runtime-call-stack.md` (`v1`)
- Future-state runtime call stack review: `tickets/done/simplify-ssh-mcp-config/future-state-runtime-call-stack-review.md` (`Go Confirmed`, Round 2)

## Document Status

- Current Status: `In Execution`
- Notes: Source edits are permitted because `workflow-state.md` is Stage 6 with `Code Edit Permission = Unlocked` and Stage 5 `Go Confirmed`.

## Plan Baseline (Freeze Until Replanning)

### Preconditions

- `requirements.md` is at least `Design-ready`: `Yes`
- Acceptance criteria use stable IDs (`AC-*`) with measurable expected outcomes: `Yes`
- `workflow-state.md` is current and Stage 5 review-gate evidence is recorded: `Yes`
- Runtime call stack review artifact exists and is current: `Yes`
- All in-scope use cases reviewed: `Yes`
- No unresolved blocking findings: `Yes`
- Future-state runtime call stack review has `Go Confirmed`: `Yes`
- Missing-use-case discovery sweeps completed for the final two clean rounds: `Yes`
- No newly discovered use cases in final two clean rounds: `Yes`

### Solution Sketch

- Use Cases In Scope: UC-001..UC-009.
- Spine Inventory In Scope: DS-001..DS-005.
- Primary Owners / Main Domain Subjects: `ssh_mcp.config` (env/target/auth contract), `ssh_mcp.runner` (OpenSSH argv/env/session lifecycle), `ssh_mcp.server` (MCP tool surface), tests/docs.
- Requirement Coverage Guarantee: REQ-001..REQ-008 all map to at least one use case and Stage 7 scenario intent.
- Design-Risk Use Cases: UC-007/UC-009 guard internal auth argv ownership and legacy removal in docs/tests.
- Target Architecture Shape: keep existing coherent files; remove legacy fields; add first-class key path; centralize auth argv in runner-local helper.
- New Owners/Boundary Interfaces To Introduce: none; add local runner auth argv helper only.
- API/Behavior Delta: `SSH_MCP_PRIVATE_KEY_FILE` added; non-empty `SSH_MCP_BASE_ARGS`/`SSH_MCP_ALLOWED_HOSTS` unsupported; `SSH_MCP_DEFAULT_HOST` pins target if set.
- Key Assumptions: one MCP server config per normal SSH target; host-key verification remains OpenSSH default.
- Known Risks: removing raw args can inconvenience power users; accepted under no-legacy simplification policy.

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

### Principles

- Bottom-up: config settings/validation first, runner command builder second, tests/docs last.
- Test-driven: update focused config/runner/server tests before or alongside source modifications.
- No backward-compatibility shims or legacy branches.
- Remove obsolete fields/helpers/tests/docs for `base_args` and `allowed_hosts`.
- Preserve authoritative boundaries: env in config, argv/session in runner, MCP schema in server.
- Keep touched files within source-file size guardrails; test files exempt from hard source size gate.

### Spine-Led Dependency And Sequencing Map

| Order | Spine ID | Owner | Task / File | Depends On | Why This Order |
| --- | --- | --- | --- | --- | --- |
| 1 | DS-004 | `ssh_mcp.config` | Update settings/env/target/auth validation | Stage 5 Go | Runner depends on settings shape. |
| 2 | DS-005 | `ssh_mcp.runner` | Update OpenSSH auth argv/session commands | C-001/C-002/C-003 | Runtime depends on new settings. |
| 3 | DS-001..DS-003 | Tests | Update config/runner/server/E2E tests | Source changes | Durable proof for behavior. |
| 4 | DS-004/DS-005 | Docs | Update README/runtime docs | Final behavior | Public docs must match code. |

### File Placement Plan

| Item | Current Path | Target Path | Owning Concern / Platform | Action | Verification |
| --- | --- | --- | --- | --- | --- |
| Config | `ssh-mcp/src/ssh_mcp/config.py` | same | SSH MCP config | Keep/Modify | `tests/test_config.py` |
| Runner | `ssh-mcp/src/ssh_mcp/runner.py` | same | SSH runtime | Keep/Modify | `tests/test_runner.py`, E2E static/runtime |
| MCP server | `ssh-mcp/src/ssh_mcp/server.py` | same | MCP tool surface | Keep | `tests/test_server.py` |
| Tests/docs | existing | same | Validation/docs | Keep/Modify | pytest + grep/review |

### Implementation Work Table

| Change ID | Spine ID(s) | Owner | Concern | Current Path | Target Path | Action | Depends On | Implementation Status | Unit Test File | Unit Test Status | Integration Test File | Integration Test Status | Stage 8 Review Status | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C-001 | DS-004 | Config | First-class private key field/env | `config.py` | same | Modify | none | Completed | `tests/test_config.py` | Passed | N/A | N/A | Planned | AC-001/AC-002 |
| C-002 | DS-004 | Config | Remove base args/allowlist support | `config.py` | same | Remove/Modify | C-001 | Completed | `tests/test_config.py` | Passed | N/A | N/A | Planned | AC-004/AC-005 |
| C-003 | DS-004/DS-001 | Config | Default-host pinning | `config.py` | same | Modify | C-002 | Completed | `tests/test_config.py` | Passed | `tests/test_server.py` | Passed | Planned | AC-006/AC-009 |
| C-004 | DS-005/DS-001..DS-003 | Runner | Internal auth argv/env | `runner.py` | same | Modify | C-001..C-003 | Completed | `tests/test_runner.py` | Passed | `tests/test_e2e_docker.py` | Passed | Planned | AC-007/AC-008/AC-010 |
| C-005 | All | Validation | Update tests | `ssh-mcp/tests/*` | same | Modify | C-001..C-004 | Completed | multiple | Passed | Docker E2E | Passed | Planned | AC-009/AC-010 |
| C-006 | DS-004/DS-005 | Docs | Update README/runtime docs | docs | same | Modify | C-001..C-005 | Completed | N/A | N/A | docs grep | Passed | Planned | AC-011/AC-012 |

### Requirement, Spine, And Design Traceability

| Requirement | Acceptance Criteria ID(s) | Spine ID(s) | Design Section | Use Case / Call Stack | Planned Task ID(s) | Stage 6 Verification | Stage 7 Scenario ID(s) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REQ-001 | AC-001, AC-007 | DS-004, DS-005 | Data Models, Change Inventory | UC-003/UC-007 | C-001, C-004 | config/runner tests | SC-001, SC-005 |
| REQ-002 | AC-002, AC-003, AC-008 | DS-004, DS-005 | Error Handling, Auth invariant | UC-001/UC-002/UC-004/UC-007 | C-001, C-004 | config/runner tests | SC-002, SC-006 |
| REQ-003 | AC-006 | DS-004, DS-001 | Target resolution | UC-006 | C-003 | config tests | SC-004 |
| REQ-004 | AC-004, AC-005 | DS-004 | Removal Plan | UC-005 | C-002 | config tests + grep | SC-003 |
| REQ-005 | AC-009 | DS-001..DS-003 | Runtime guardrails | UC-008 | C-004/C-005 | runner/server tests | SC-007 |
| REQ-006 | AC-006 | DS-004 | Default-host pinning | UC-006 | C-003 | config tests | SC-004 |
| REQ-007 | AC-007, AC-008 | DS-005 | Runner auth argv | UC-003/UC-007/UC-008 | C-004 | runner tests | SC-005/SC-006 |
| REQ-008 | AC-010, AC-011, AC-012 | all | Docs/tests | UC-009 | C-005/C-006 | test/docs review | SC-008/SC-009 |

### Stage 7 Planned Coverage Mapping

| Acceptance Criteria ID | Requirement ID | Spine ID(s) | Expected Outcome | Stage 7 Scenario ID(s) | Test Level | Initial Status |
| --- | --- | --- | --- | --- | --- | --- |
| AC-001 | REQ-001 | DS-004 | private-key env parsed/path expanded | SC-001 | API/unit executable | Planned |
| AC-002 | REQ-001/REQ-002 | DS-004 | conflicting auth rejected | SC-002 | API/unit executable | Planned |
| AC-003 | REQ-002 | DS-004 | password/password-file conflict rejected | SC-002 | API/unit executable | Planned |
| AC-004 | REQ-004 | DS-004 | base args unsupported | SC-003 | API/unit executable | Planned |
| AC-005 | REQ-004 | DS-004 | allowed hosts unsupported | SC-003 | API/unit executable | Planned |
| AC-006 | REQ-003/REQ-006 | DS-004/DS-001 | default-host pinning | SC-004 | API/unit executable | Planned |
| AC-007 | REQ-001/REQ-007 | DS-005 | key auth argv internal | SC-005 | API/unit executable | Planned |
| AC-008 | REQ-002/REQ-007 | DS-005 | password askpass argv/env | SC-006 | API/unit executable | Planned |
| AC-009 | REQ-005 | DS-001..DS-003 | server lifecycle tests pass | SC-007 | MCP integration | Planned |
| AC-010 | REQ-008 | DS-001..DS-003 | Docker E2E fixture uses key field | SC-008 | E2E/static optional runtime | Planned |
| AC-011 | REQ-008 | DS-004 | README simple examples | SC-009 | Docs executable grep | Planned |
| AC-012 | REQ-008 | DS-004 | runtime docs no removed env support | SC-009 | Docs executable grep | Planned |

### Design Delta Traceability

| Change ID | Planned Task ID(s) | Includes Remove/Rename Work | Verification |
| --- | --- | --- | --- |
| C-001 | C-001 | No | Config tests + Stage 7 SC-001 |
| C-002 | C-002 | Yes | Config tests + grep SC-003/SC-009 |
| C-003 | C-003 | No | Config tests SC-004 |
| C-004 | C-004 | No | Runner tests SC-005/SC-006 |
| C-005 | C-005 | Yes old expectations | Full tests SC-007/SC-008 |
| C-006 | C-006 | Yes old docs | Docs grep SC-009 |

### Decommission / Rename Execution Tasks

| Task ID | Item | Action | Cleanup Steps | Risk Notes |
| --- | --- | --- | --- | --- |
| T-DEL-001 | `SshSettings.base_args` / `SSH_MCP_BASE_ARGS` | Remove | Delete field/usages/tests/docs; reject stale env. | Runner command expectations change. |
| T-DEL-002 | `SshSettings.allowed_hosts` / `SSH_MCP_ALLOWED_HOSTS` | Remove | Delete field/parser/usages/tests/docs; default-host pin. | Explicit-host behavior must stay clear. |
| T-DEL-003 | E2E raw key base args | Remove | Use `private_key_file` and normal known_hosts setup. | Docker E2E may be environment-gated. |

### Step-By-Step Plan

1. Update config tests and source for private key, auth conflicts, unsupported env keys, and default-host pinning.
2. Update runner tests and source for internal auth argv, health check, open/exec/close command construction.
3. Update server/E2E tests for new `SshSettings` shape and first-class private key.
4. Update README/runtime docs; remove supported mentions of old env variables.
5. Run targeted and full `ssh-mcp` test suite; run docs grep; optionally run Docker E2E if enabled/available.
6. Update implementation tracking and transition to Stage 7.

### Backward-Compat And Decoupling Guardrails

- Backward-compatibility mechanisms introduced: `None`
- Legacy code retained for old behavior: `No`
- Dead/obsolete code or unused helpers/tests/flags/adapters left in scope: `No`; reference scan completed.
- Shared data structures remain tight: `Yes`
- Shared design-principles guidance reapplied during implementation: `Yes`
- Authoritative Boundary Rule preserved: `Yes`
- Decoupling impact assessment completed: `Yes`
- New tight coupling or cyclic dependency introduced: `No`
- Changed source implementation files kept within proactive size-pressure guardrails: `Yes`; final effective line counts: config 303, runner 422, session 89, execution 186, types 22, server 175.

### Code Review Gate Plan (Stage 8)

- Gate artifact path: `tickets/done/simplify-ssh-mcp-config/code-review.md`
- Scope: changed source files, tests, docs evidence relevant to behavior.
- Line-count measurement:
  - `rg -n "\\S" ssh-mcp/src/ssh_mcp/config.py ssh-mcp/src/ssh_mcp/runner.py ssh-mcp/src/ssh_mcp/server.py | wc -l`
  - `git diff --numstat origin/main...HEAD -- ssh-mcp/src/ssh_mcp/config.py ssh-mcp/src/ssh_mcp/runner.py ssh-mcp/src/ssh_mcp/server.py`
- `>500` hard-limit policy: any changed source implementation file over 500 effective non-empty lines fails review by default and triggers design-impact split/refactor.
- `>220` changed-line delta gate: record design-impact assessment for any changed source file over 220 changed lines.

| File | Current Line Count | Adds/Expands Functionality | Ownership/SoC Risk | Required Action | Expected Review Classification if not addressed |
| --- | --- | --- | --- | --- | --- |
| `config.py` | 303 | Yes | Low | Keep concise; remove old helpers. | Design Impact if legacy fields remain. |
| `runner.py` | 422 | Yes | Low | Split completed; auth builder local and cohesive. | Design Impact if raw args path remains. |
| `server.py` | 175 | No | Low | Imports shared result type only. | Local Fix if tests only need shape update. |

### Test Strategy

- Unit tests: `ssh-mcp/tests/test_config.py`, `ssh-mcp/tests/test_runner.py`.
- Integration tests: `ssh-mcp/tests/test_server.py` MCP client/server delegation.
- Optional E2E: `SSH_MCP_RUN_DOCKER_E2E=1 uv --directory ssh-mcp run --frozen --extra test pytest tests/test_e2e_docker.py` if Docker environment supports it.
- Stage 7 handoff notes:
  - canonical artifact path: `tickets/done/simplify-ssh-mcp-config/api-e2e-testing.md`
  - expected acceptance criteria count: 12
  - expected scenario count: 9
  - known environment constraints: Docker E2E is optional/gated by `SSH_MCP_RUN_DOCKER_E2E=1` and Docker availability.

### Cross-Reference Exception Protocol

No cross-reference exceptions planned.

### Design Feedback Loop

| Smell/Issue | Evidence | Design Section To Update | Action | Status |
| --- | --- | --- | --- | --- |
| None | N/A | N/A | N/A | Current |

## Execution Tracking

### Kickoff Preconditions Checklist

- Workflow state is current: `Yes`
- `workflow-state.md` shows `Current Stage = 6` and `Code Edit Permission = Unlocked` before source edits: `Yes`
- Scope classification confirmed: `Medium`
- Investigation notes are current: `Yes`
- Requirements status is `Design-ready` or `Refined`: `Yes`
- Future-state runtime call stack review final gate is `Implementation can start: Yes`: `Yes`
- Future-state runtime call stack review reached `Go Confirmed`: `Yes`
- No unresolved blocking findings: `Yes`

### Progress Log

- 2026-08-18: Stage 6 implementation baseline created; source edits unlocked by workflow-state T-006.

### Scope Change Log

| Date | Previous Scope | New Scope | Trigger | Required Action |
| --- | --- | --- | --- | --- |
| N/A | N/A | N/A | N/A | N/A |

### Implementation Work Updates

| Change ID | Last Failure Classification | Last Failure Investigation Required | Cross-Reference Smell | Design Follow-Up | Requirement Follow-Up | Last Verified | Verification Command | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C-001..C-010 | N/A | No | None | Completed in v2 | Not Needed | 2026-08-18 | `uv --directory ssh-mcp run --frozen --extra test pytest`; `SSH_MCP_RUN_DOCKER_E2E=1 uv --directory ssh-mcp run --frozen --extra test pytest tests/test_e2e_docker.py` | Stage 6 source/tests/docs complete. |

### Downstream Stage Status Pointers

| Stage | Canonical Artifact | Current Status | Last Updated | Notes |
| --- | --- | --- | --- | --- |
| 7 API/E2E + Executable Validation | `tickets/done/simplify-ssh-mcp-config/api-e2e-testing.md` | `Ready to start` | 2026-08-18 | Stage 6 tests passed; detailed Stage 7 artifact pending. |
| 8 Code Review | `tickets/done/simplify-ssh-mcp-config/code-review.md` | `Not Started` | 2026-08-18 | Planned after Stage 7. |
| 9 Docs Sync | `tickets/done/simplify-ssh-mcp-config/docs-sync.md` | `Not Started` | 2026-08-18 | Planned after Stage 8. |

### Blocked Items

| Change ID | Blocked By | Unblock Condition | Owner/Next Action |
| --- | --- | --- | --- |
| N/A | N/A | N/A | N/A |

### Design Feedback Loop Log

| Date | Trigger File(s) | Smell Description | Design Section Updated | Update Status | Notes |
| --- | --- | --- | --- | --- | --- |
| N/A | N/A | N/A | N/A | N/A | N/A |

### Remove/Rename/Legacy Cleanup Verification Log

| Date | Change ID | Item | Verification Performed | Result | Notes |
| --- | --- | --- | --- | --- | --- |
| 2026-08-18 | C-002 | `base_args`/`allowed_hosts` support | `rg -n "base_args|allowed_hosts" ssh-mcp/src ssh-mcp/tests`; docs grep for removed env names; full pytest | Passed | No source/test legacy fields remain; docs do not list removed env names. |

### Completion Gate

- Implementation Status: `Completed`
- Required unit/integration tests: `Passed`
- No backward-compatibility shims or legacy old-behavior branches remain in scope: `Passed`
- Dead code/obsolete helpers removed: `Passed`
- Ownership-dependency checks show no new unjustified tight coupling/cycles: `Passed`
- Touched files have correct placement: `Passed`
- Changed source implementation files have Stage 8 size-pressure handling recorded: `Passed`; runner split resolved >500 issue; runner changed-line delta >220 is documented as Design Impact already handled by v2 split.

### Stage 6 Re-entry Event

- 2026-08-18: Design Impact found during Stage 6 size-pressure check. Changed `ssh-mcp/src/ssh_mcp/runner.py` has 717 effective non-empty lines, exceeding the workflow hard limit of 500 for changed source implementation files. Source edits are paused and locked; upstream artifacts must be updated to split runtime/session/execution ownership before implementation resumes.


### Stage 6 Completion Evidence

- 2026-08-18: Source implementation completed. Added `ssh_mcp.types`, `ssh_mcp.session`, and `ssh_mcp.execution`; slimmed `ssh_mcp.runner`; updated config, tests, README, and runtime docs.
- Unit/integration: `uv --directory ssh-mcp run --frozen --extra test pytest` -> `34 passed, 6 skipped in 0.56s`.
- Docker E2E: `SSH_MCP_RUN_DOCKER_E2E=1 uv --directory ssh-mcp run --frozen --extra test pytest tests/test_e2e_docker.py` -> `6 passed in 28.75s`.
- Source line counts: `config.py` 303, `runner.py` 422, `session.py` 89, `execution.py` 186, `types.py` 22, `server.py` 175 effective non-empty lines.
- Legacy scan: no `base_args`/`allowed_hosts` source/test fields remain; docs contain no supported mentions of removed env settings.
