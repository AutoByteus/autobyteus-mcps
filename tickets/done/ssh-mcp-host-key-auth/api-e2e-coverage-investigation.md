# API/E2E Coverage Investigation — SSH MCP Seamless Multi-Auth Sessions

## Investigation Meta

- Requirements: `requirements.md`
- Investigation notes: `investigation-notes.md`
- Design: `design-spec.md`
- Solution revision: `solution-revision-record.md`
- Implementation handoff: `implementation-handoff.md`
- Implementation revision: `implementation-revision-record.md`
- Code review: `code-review-report.md`
- Code review revision: `code-review-revision-record.md`
- API/E2E revision: created after completed execution
- Current round: `1`
- Trigger: Code review `CRR-001` passed

## Current Requirement And Design Basis

The changed boundary is the real OpenSSH lifecycle behind MCP tools. Critical proof must cover both fixed-host configurations: LAN password/askpass and droplet private key. First-use host-key handling must be non-interactive, changed keys must fail, and sessions must open, execute, close, and clean up.

## Changed Behavior Summary

| Behavior / Boundary | Change | Coverage Consequence |
| --- | --- | --- |
| BEH-001 health | Preserved | Existing server/runner tests remain valid; local-only meaning documented. |
| BEH-002 LAN password | Changed | Add first-use durable E2E and live LAN MCP smoke. |
| BEH-003 droplet key | Preserved plus shared host-key flag | Existing key E2E plus live droplet MCP smoke. |
| BEH-004 failures | Changed diagnostics/prompt bound | Unit timeout-output test and changed-key live probe. |

## Changed Surface And Boundary Classification

| Surface | Affected | Evidence / Risk / Mode |
| --- | --- | --- |
| Backend logic | Yes | Runner/execution source and unit tests; direct source invocation. |
| API/transport/contract | Yes | In-memory MCP server/client lifecycle and structured results. |
| Authentication/session | Yes | Real LAN password and droplet private-key sessions. |
| Process/lifecycle | Yes | Control master open/exec/close and cleanup. |
| External integration | Yes | Real SSH daemons at configured LAN/droplet targets. |
| Frontend/browser/desktop/persisted data | No | Not applicable. |

## Project Execution Discovery

- Worktree: `/Users/normy/autobyteus-org/autobyteus-mcps-worktrees/ssh-mcp-host-key-auth`
- Runtime: Python 3.13.14, `uv`, OpenSSH 10.2p1, MCP Python SDK.
- Primary instructions: `ssh-mcp/README.md`, `ssh-mcp/pyproject.toml`, `ssh-mcp/tests/test_e2e_docker.py`.
- Required secrets/config available: Yes through local MCP config; values were never recorded in artifacts/output.
- Docker CLI available; Docker daemon unavailable (`docker info` exit 1), so Docker E2E is blocked in this environment.

## Existing Durable Coverage Inventory

| Path / Scenario | Decision | Action |
| --- | --- | --- |
| `tests/test_config.py` | Still Valid | Run unchanged. |
| `tests/test_runner.py` | Needs Update | Assert shared accept-new policy and one password prompt. |
| `tests/test_server.py` | Still Valid | MCP delegation contract remains unchanged. |
| `tests/test_e2e_docker.py` key/password/password-file lifecycle | Still Valid | Run when Docker is available. |
| `tests/test_e2e_docker.py` first-use password lifecycle | Add Durable Coverage | New isolated known-hosts scenario added by implementation. |
| `tests/test_execution.py` timeout bytes | Add Durable Coverage | New focused regression added by implementation. |

## Durable Coverage To Add / Update

| Scenario ID | Behavior / AC | Path | Decision |
| --- | --- | --- | --- |
| SC-API-001 | BEH-002 / AC-001, AC-003 | `test_e2e_docker.py` first-use password | Added; proves no host-key prompt loop. |
| SC-API-002 | BEH-004 / AC-005 | `test_execution.py` timeout bytes | Added; proves diagnostics preserved. |
| SC-API-003 | BEH-002/003 / AC-003/004/006 | Temporary real MCP protocol smoke | Temporary only; direct live proof for current configured endpoints. |
| SC-API-004 | BEH-004 / AC-002 | Temporary changed-key probe | Temporary only; OpenSSH rejects mismatched key quickly. |

## Repository Coverage Execution Plan And Results

| Order | Command | Result | Evidence |
| --- | --- | --- | --- |
| 1 | `uv run --frozen --extra test pytest tests/test_config.py tests/test_runner.py tests/test_execution.py tests/test_server.py` | Pass | 35 passed. |
| 2 | `uv run --frozen --extra test pytest` | Pass | 35 passed, 7 skipped (Docker-gated). |
| 3 | `uv run --frozen python -m compileall -q src` | Pass | Compileall passed. |
| 4 | Docker E2E with `SSH_MCP_RUN_DOCKER_E2E=1` | Blocked | Docker daemon unavailable. |
| 5 | Temporary in-memory MCP protocol + real LAN/droplet SSH | Pass | Both opened, ran `whoami`, and closed successfully. |
| 6 | Temporary changed-key real SSH probe | Pass | Mismatched key rejected in 594 ms; no session registered. |

## Confidence Scorecard Before Broader Validation

| Category | Score | Support | Remaining Uncertainty |
| --- | ---: | --- | --- |
| Requirements/AC proof | 92% | Unit + direct real MCP smokes cover core paths. | Docker fixture path unavailable here. |
| Changed-boundary directness | 98% | Patched source runner and MCP protocol exercised. | Current installed tool process not restarted from branch. |
| Cross-boundary realism | 95% | Real LAN and droplet SSH targets used. | Docker E2E skipped. |
| Environment/config fidelity | 96% | Actual MCP config values loaded, secrets redacted. | Launcher-specific restart not exercised. |
| Failure/lifecycle evidence | 95% | Changed-key rejection, timeout normalization, open/exec/close. | Wrong-password live path not exercised to avoid repeated auth attempts. |
| User/browser/desktop | N/A | Backend-only MCP change. | None. |
| Durable coverage quality | 94% | Focused tests and isolated first-use fixture added. | Docker execution unavailable. |

- Overall post-repository confidence: 95%
- Calculation: simple average across applicable categories.
- All critical AC directly proven: Yes through combined unit + live probes; Docker fixture execution remains blocked.
- Applicable category below 90%: No.
- Default target met: Yes, with explicit Docker limitation.

## Broader Validation Decision

- Decision: `Required` and completed through `CLI`/`Lifecycle`/`Live API`-equivalent MCP protocol mode.
- Gap addressed: actual configured external endpoints and separate auth sources.
- Why selected mode: this is not a browser task; real MCP protocol calls plus real SSH targets exercise the changed boundary more directly than mocks.
- Browser: Not applicable.
- Docker: Blocked after safe setup; daemon unavailable. Existing repository Docker coverage remains durable and will run in CI/another host.

## Temporary Executable Validation Plan

| Scenario | Probe | Result / Cleanup |
| --- | --- | --- |
| SC-API-003 | In-memory MCP client/server with actual LAN and droplet settings, wrapper-isolated known-hosts, open -> whoami -> close. | Pass; temporary wrapper/session dirs cleaned by OS temp lifecycle. |
| SC-API-004 | Real OpenSSH with deliberately mismatched known_hosts entry against LAN target. | Pass; rejected quickly, session count 0. |

## Not Tested / Infeasible / Deferred

| Boundary | Reason | Risk / Follow-up |
| --- | --- | --- |
| Dockerized OpenSSH E2E execution | Docker daemon unavailable. | Run `SSH_MCP_RUN_DOCKER_E2E=1 uv ... pytest tests/test_e2e_docker.py` when daemon is available. |
| Current already-running MCP server after branch change | Running connector is not restarted automatically from worktree. | Restart/reinstall MCP before user verification. |

## Investigation Decision

- Proceed to API/E2E execution: Yes; completed.
- Durable coverage changed: Yes, `test_runner.py`, `test_execution.py`, `test_e2e_docker.py`.
- Reroute required: No.
- Notes: Both real configured MCP endpoints pass against the patched source; code review may now perform proportional test-code review.
