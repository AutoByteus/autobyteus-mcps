# Code Review - Simplify SSH MCP Configuration

## Review Meta

- Ticket: `simplify-ssh-mcp-config`
- Review Round: `1`
- Trigger Stage: `7`
- Prior Review Round Reviewed: `None`
- Latest Authoritative Round: `1`
- Workflow state source: `tickets/done/simplify-ssh-mcp-config/workflow-state.md`
- Investigation notes reviewed as context: `tickets/done/simplify-ssh-mcp-config/investigation-notes.md`
- Earlier design artifact(s) reviewed as context: `tickets/done/simplify-ssh-mcp-config/proposed-design.md` (`v2`), `future-state-runtime-call-stack-review.md` (`Go Confirmed` Round 4)
- Runtime call stack artifact: `tickets/done/simplify-ssh-mcp-config/future-state-runtime-call-stack.md` (`v2`)
- Shared Design Principles: `software-engineering-workflow-skill/shared/design-principles.md` and `code-reviewer/design-principles.md`
- Code Review Principles: `software-engineering-workflow-skill/stages/08-code-review/code-review-principles.md`

Round rules applied:
- One canonical Stage 8 file: `code-review.md`.
- No prior Stage 8 findings exist.
- Earlier design artifacts are context only; review authority is the current code plus shared design/review principles.

## Scope

- Source files reviewed:
  - `ssh-mcp/src/ssh_mcp/config.py`
  - `ssh-mcp/src/ssh_mcp/runner.py`
  - `ssh-mcp/src/ssh_mcp/server.py`
  - `ssh-mcp/src/ssh_mcp/types.py`
  - `ssh-mcp/src/ssh_mcp/session.py`
  - `ssh-mcp/src/ssh_mcp/execution.py`
- Test files reviewed:
  - `ssh-mcp/tests/test_config.py`
  - `ssh-mcp/tests/test_runner.py`
  - `ssh-mcp/tests/test_server.py`
  - `ssh-mcp/tests/test_e2e_docker.py`
- Directly impacted docs checked as context for legacy/public-contract drift:
  - `ssh-mcp/README.md`
  - `ssh-mcp/docs/runtime-flow.md`
- Why these files: they carry the env contract change, auth command policy, runtime split, MCP server import boundary, unit/integration coverage, and Docker E2E lifecycle proof.

## Commands And Evidence Reviewed

```bash
git status --short --branch
git diff --check
for f in ssh-mcp/src/ssh_mcp/config.py ssh-mcp/src/ssh_mcp/runner.py ssh-mcp/src/ssh_mcp/server.py ssh-mcp/src/ssh_mcp/types.py ssh-mcp/src/ssh_mcp/session.py ssh-mcp/src/ssh_mcp/execution.py; do rg -n "\\S" "$f" | wc -l; done
git diff --numstat -- ssh-mcp/src/ssh_mcp/config.py ssh-mcp/src/ssh_mcp/runner.py ssh-mcp/src/ssh_mcp/server.py
uv --directory ssh-mcp run --frozen python -m compileall -q src
uv --directory ssh-mcp run --frozen --extra test pytest tests/test_config.py tests/test_runner.py tests/test_server.py
SSH_MCP_RUN_DOCKER_E2E=1 uv --directory ssh-mcp run --frozen --extra test pytest tests/test_e2e_docker.py
rg -n "base_args|allowed_hosts" ssh-mcp/src ssh-mcp/tests
rg -n "SSH_MCP_BASE_ARGS|SSH_MCP_ALLOWED_HOSTS" ssh-mcp/README.md ssh-mcp/docs/runtime-flow.md
```

Results:
- `git diff --check`: no whitespace/errors.
- `compileall`: passed.
- Unit/integration MCP tests: `34 passed in 0.51s`.
- Docker E2E tests: `6 passed in 17.50s`.
- Lowercase source/test legacy-symbol scan: no matches for `base_args|allowed_hosts`.
- Docs supported-controls scan: no matches for `SSH_MCP_BASE_ARGS|SSH_MCP_ALLOWED_HOSTS` in README/runtime docs.
- Source/tests still intentionally mention removed env names only in the fail-fast unsupported-setting map/tests; this is rejection behavior, not compatibility support.

## Prior Findings Resolution Check

N/A for Review Round 1.

## Source File Size And Structure Audit

This audit applies to changed source implementation files only. Test files remain in review scope but are not subject to source-size thresholds.

Measurement note: the ticket branch has not been committed yet, so tracked changed-line deltas use `git diff --numstat -- <file>`. Untracked new source files use effective non-empty line count as the addition count for the Stage 8 delta assessment.

| Source File | Effective Non-Empty Line Count | Adds/Expands Functionality (`Yes`/`No`) | `>500` Hard-Limit Check | `>220` Changed-Line Delta Gate | Scope-Appropriate SoC Check | File Placement Check | Preliminary Classification | Required Action |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- |
| `ssh-mcp/src/ssh_mcp/config.py` | 303 | Yes | Pass | Pass: 75 changed lines | Pass | Pass | N/A | Keep |
| `ssh-mcp/src/ssh_mcp/runner.py` | 422 | Yes | Pass | Pass with recorded design-impact assessment: 432 changed lines, primarily removal/extraction from prior oversized all-in-one runtime file | Pass | Pass | N/A | Keep after split |
| `ssh-mcp/src/ssh_mcp/server.py` | 175 | No | Pass | Pass: 2 changed lines | Pass | Pass | N/A | Keep |
| `ssh-mcp/src/ssh_mcp/types.py` | 22 | Yes | Pass | Pass: 22 added effective lines | Pass | Pass | N/A | Keep |
| `ssh-mcp/src/ssh_mcp/session.py` | 89 | Yes | Pass | Pass: 89 added effective lines | Pass | Pass | N/A | Keep |
| `ssh-mcp/src/ssh_mcp/execution.py` | 186 | Yes | Pass | Pass: 186 added effective lines | Pass | Pass | N/A | Keep |

### `runner.py` `>220` Changed-Line Delta Assessment

- Trigger: `runner.py` changed-line delta is `432` (59 additions, 373 deletions), above the `>220` delta gate.
- Assessment: this is not an unresolved design smell. The same size/shape pressure was already classified as `Design Impact` during Stage 6 (transition `T-007`), then resolved through re-entry artifacts (`proposed-design.md` v2, `future-state-runtime-call-stack.md` v2, review Round 4 `Go Confirmed`).
- Current state: `runner.py` is now below the hard source-size limit and owns only runtime orchestration plus OpenSSH argv/env policy. Session state moved to `session.py`, execution/result mapping moved to `execution.py`, and the shared result contract moved to `types.py`.
- Decision: gate passes; no additional design re-entry is required.

## Structural Integrity Checks

| Check | Result | Evidence | Required Action |
| --- | --- | --- | --- |
| Data-flow spine inventory clarity and preservation under shared principles | Pass | Tool flow is traceable as `server -> runner -> config/session/execution -> OpenSSH -> structured result`; `runner.py` remains the lifecycle spine owner. | None |
| Ownership boundary preservation and clarity | Pass | `config.py` owns env/target/auth validation; `runner.py` owns command policy and lifecycle orchestration; `session.py` owns session map/control paths; `execution.py` owns subprocess/result mapping. | None |
| Off-spine concern clarity | Pass | Askpass is runner-owned, password-file reading is config-owned, timeout/output mapping is execution-owned, capacity/expiry is session-owned. | None |
| Existing capability/subsystem reuse check | Pass | Existing `config`, `runner`, and `server` boundaries are reused; new files are created only for real extracted runtime owners. | None |
| Reusable owned structures check | Pass | `SshToolResult` is extracted once to `types.py` instead of duplicated or imported from an internal runtime owner. | None |
| Shared-structure/data-model tightness check | Pass | `SshSettings` has one field per current env concept; removed fields are gone; auth sources are mutually exclusive; `SshToolResult` remains broad because it is the single tool structured-output contract. | None |
| Repeated coordination ownership check | Pass | Auth argv policy is centralized in `_build_auth_args` and reused by open/exec/close builders. | None |
| Empty indirection check | Pass | `types.py`, `session.py`, and `execution.py` own concrete type/state/execution concerns; `create_session_manager` preserves the runner boundary for server without exposing session internals. | None |
| Scope-appropriate separation of concerns and file responsibility clarity | Pass | The package stays flat but each file has a coherent owner; no nested package would materially improve readability for this small MCP package. | None |
| Ownership-driven dependency check | Pass | Dependencies follow `server -> runner/types`, `runner -> config/session/execution/types`, `execution -> types`, `session -> config` only for `ConfigError`; no cycles observed. | None |
| Authoritative Boundary Rule check | Pass | `server.py` does not bypass runner to call session/execution internals; it imports only runner lifecycle functions and the shared result type. | None |
| File placement check | Pass | All runtime files remain under `ssh_mcp`, the owning package for this MCP; test files remain under `ssh-mcp/tests`. | None |
| Flat-vs-over-split layout judgment | Pass | Four runtime source files (`runner`, `config`, `session`, `execution`) plus `types` are enough to expose owners without over-fragmenting. | None |
| Interface/API/query/command/service-method boundary clarity | Pass | Public MCP tools remain explicit lifecycle commands; env contract uses destination + one auth source; `ExecutionSpec` has an explicit complete command/result identity. | None |
| Naming quality and naming-to-responsibility alignment check | Pass | `private_key_file`, `SessionManager`, `ExecutionSpec`, `error_result`, and `resolve_target` describe their responsibilities directly. | None |
| No unjustified duplication of code / repeated structures in changed scope | Pass | Result construction is centralized in `execution.error_result`; auth args centralized in runner; session capacity messages occur only in the session owner. | None |
| Patch-on-patch complexity control | Pass | No compatibility fallback branch was layered on top of the old raw args/allowlist model; old fields and helpers were removed. | None |
| Dead/obsolete code cleanup completeness in changed scope | Pass | `base_args`, `allowed_hosts`, `_parse_allowed_hosts`, `_parse_csv`, and in-runner duplicate execution/session structures were removed from supported code paths. | None |
| Test quality is acceptable for the changed behavior | Pass | Unit tests cover env parsing, auth conflicts, default-host pinning, command construction, askpass, private-key command args, server delegation, and Docker E2E lifecycle. | None |
| Test maintainability is acceptable for the changed behavior | Pass | Helpers are localized and scenario names describe behavior; Docker setup is explicit and gated by env. | None |
| Validation evidence sufficiency for the changed flow | Pass | Fast suite, compile check, Docker E2E, legacy scans, and size checks all passed. | None |
| No backward-compatibility mechanisms | Pass | Removed env vars fail fast when non-empty; there is no dual parsing, no raw-args passthrough, and no allowlist fallback behavior. | None |
| No legacy code retention for old behavior | Pass | Old public raw-args/allowlist model is not documented as supported and no lowercase legacy fields/helpers remain. | None |

## Review Scorecard

- Overall score (`/10`): `9.5 / 10`
- Overall score (`/100`): `95 / 100`
- Score calculation note: simple average across the ten categories for trend visibility only; the Stage 8 gate still depends on each category being `>= 9.0` and all mandatory checks passing.

| Priority | Category | Score | Why This Score | What Is Weak / Holding It Down | What Should Improve |
| --- | --- | ---: | --- | --- | --- |
| `1` | `Data-Flow Spine Inventory and Clarity` | 9.5 | The runtime path is clear from MCP tool entrypoint through runner orchestration into config/session/execution and back as structured output. | The code relies on ticket/runtime docs to name spines; source itself is intentionally lean. | Keep runtime docs synchronized so future maintainers see the same spine map. |
| `2` | `Ownership Clarity and Boundary Encapsulation` | 9.5 | Extracted owners are concrete, and `server.py` does not bypass the runner boundary. | `session.py` imports `ConfigError` from config, a small shared error coupling accepted for this package. | If error taxonomy grows, consider a tiny package-level errors module; not needed now. |
| `3` | `API / Interface / Query / Command Clarity` | 9.5 | Public MCP tools are explicit lifecycle commands; env config is host/user/optional-port plus one auth source; removed knobs produce actionable errors. | `SSH_MCP_HEALTH_CHECK_ARGS` remains shell-split advanced config by design. | Keep advanced controls documented as optional and avoid promoting them into normal setup. |
| `4` | `Separation of Concerns and File Placement` | 9.5 | `config`, `runner`, `session`, `execution`, and `types` each own a coherent concern under the correct package. | Flat package means files sit side by side rather than in a runtime subpackage. | Keep flat layout unless more runtime owners are added. |
| `5` | `Shared-Structure / Data-Model Tightness and Reusable Owned Structures` | 9.0 | `SshSettings` is tight and mutually exclusive for auth; `SshToolResult` is centralized. | `SshToolResult` necessarily contains nullable fields for multiple tool actions, so it is broad. | If tool outputs diverge later, split into action-specific result variants instead of widening this type. |
| `6` | `Naming Quality and Local Readability` | 9.5 | Names are direct and unsurprising: `private_key_file`, `resolve_target`, `SessionRecord`, `ExecutionSpec`, `execute`. | Minor helper names remain private and implementation-oriented. | Keep names action/owner-oriented as behavior expands. |
| `7` | `Validation Strength` | 10.0 | Unit/integration suite, server tests, Docker-backed real OpenSSH E2E, compile check, legacy scans, and size gates all passed. | None material. | Continue running Docker E2E for auth/session changes. |
| `8` | `Runtime Correctness Under Edge Cases` | 9.5 | Handles missing command, timeout, non-zero SSH exit, output truncation, auth conflicts, default-host override rejection, expired/missing sessions, and password not in argv. | Private-key existence/permissions are delegated to OpenSSH rather than prevalidated. | Keep delegating SSH-native validation unless requirements demand custom preflight. |
| `9` | `No Backward-Compatibility / No Legacy Retention` | 9.5 | Old env vars are not supported; non-empty stale use fails fast; no raw-args or allowlist behavior remains. | Removed env names still appear in rejection messages/tests, intentionally. | Keep removed env mentions limited to fail-fast diagnostics. |
| `10` | `Cleanup Completeness` | 9.5 | Obsolete fields/parsers and in-runner duplicated session/execution/result code are removed; docs no longer list removed settings as supported. | Runtime docs need Stage 9 synchronization to describe the new split fully. | Complete Stage 9 docs sync before handoff. |

## Findings

None.

## Round History

| Round | Trigger | Prior Unresolved Findings Rechecked | New Findings Found | Gate Decision | Latest Authoritative | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Stage 7 pass | N/A | No | Pass | Yes | Mandatory structural checks, line-count gates, validation evidence, and no-legacy checks passed. |

## Re-Entry Declaration

N/A. Stage 8 passes and no re-entry is required.

## Gate Decision

- Latest authoritative review round: `1`
- Decision: `Pass`
- Implementation can proceed to `Stage 9`: `Yes`
- Mandatory pass checks:
  - Review scorecard is recorded with rationale, weakness, and required-improvement notes for all ten categories in canonical priority order: `Pass`
  - No scorecard category is below `9.0`: `Pass`
  - All changed source files have effective non-empty line count `<=500`: `Pass`
  - Required `>220` changed-line delta-gate assessments are recorded for all applicable changed source files: `Pass`
  - Data-flow spine inventory clarity and preservation under shared principles: `Pass`
  - Ownership boundary preservation: `Pass`
  - Support/off-spine structure clarity: `Pass`
  - Existing capability/subsystem reuse check: `Pass`
  - Reusable owned structures check: `Pass`
  - Shared-structure/data-model tightness check: `Pass`
  - Repeated coordination ownership check: `Pass`
  - Empty indirection check: `Pass`
  - Scope-appropriate separation of concerns and file responsibility clarity: `Pass`
  - Ownership-driven dependency check: `Pass`
  - Authoritative Boundary Rule check: `Pass`
  - File placement check: `Pass`
  - Flat-vs-over-split layout judgment: `Pass`
  - Interface/API/query/command/service-method boundary clarity: `Pass`
  - Naming quality and naming-to-responsibility alignment check: `Pass`
  - No unjustified duplication of code / repeated structures in changed scope: `Pass`
  - Patch-on-patch complexity control: `Pass`
  - Dead/obsolete code cleanup completeness in changed scope: `Pass`
  - Test quality is acceptable for the changed behavior: `Pass`
  - Test maintainability is acceptable for the changed behavior: `Pass`
  - Validation evidence sufficiency: `Pass`
  - No backward-compatibility mechanisms: `Pass`
  - No legacy code retention: `Pass`
- Notes: Code edits remain locked. Proceed to Stage 9 docs sync.
