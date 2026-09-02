# API/E2E Coverage Investigation

## Investigation Meta

- Requirements Doc: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/requirements.md`
- Investigation Notes: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/investigation-notes.md`
- Design Spec: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/design-spec.md`
- Supplemental Task Artifact: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/cli-conversion-analysis.md`
- Solution Revision Record: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/solution-revision-record.md`
- Design Review Report: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/design-review-report.md`
- Architecture Review Revision Record: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/architecture-review-revision-record.md`
- Implementation Handoff: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/implementation-handoff.md`
- Implementation Revision Record: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/implementation-revision-record.md`
- Code Review Report: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/code-review-report.md`
- Code Review Revision Record: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/code-review-revision-record.md`
- Prior Delivery Revision Record: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/delivery-revision-record.md`
- API/E2E Revision Record: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/api-e2e-revision-record.md`
- Current API/E2E Revision ID: `API-REV-004` (reserved until this round produces a completed result)
- Current Investigation Round: `4` (resumed and refreshed after the prior SR-006 hold)
- Trigger: `code_reviewer` source review `CRR-009` / Pass for `IR-006`, implementing approved cumulative `SR-007`–`SR-009` after `ARCH-REV-008`.
- Prior Completed API/E2E Result: `API-REV-003` / `Pass / 97%`; it remains truthful history for the superseded branded runtime and is not current SR-009 proof.
- Latest Authoritative Investigation: `Round 4 SR-009 execution-ready investigation. This refresh supersedes the held SR-006 plan before current-source execution or API/E2E-owned durable coverage edits.`

## Current Requirement And Design Basis

The current capability is the generic, relocatable `browser-automation/` bundle. A runtime advertises an exact readable locator ending `browser-automation/SKILL.md`; the agent reads that exact file, resolves only its sibling `scripts/browser`, invokes the resolved path with Bash from the unrelated task workspace, and relies on no persistent shell state, path scan, vendor home, install placeholder, PATH registration, Python, or direct uv invocation. Public identity is `browser-automation` / **Browser Automation** / `$browser-automation`; active package, namespace, CLI, MCP, environment, readiness, and DOM schema identities remain generic.

`SR-007` / `BEH-010` / `REQ-014` / `AC-014` correct the normal `run-script` procedure. The former MCP operation `run_script(tab_id, script, arg)` maps argument-isomorphically to `run-script --tab-id ... --script '<JavaScript>' --arg-json '<JSON>'`. File/stdin/arg-file modes remain optional only for already-file-backed input or a concrete transport limit; script complexity, length, or multiline form is not a reason to redirect normal agent use.

`SR-008`–`SR-009` / `BEH-011` / `REQ-015` / `AC-015` replace the external runtime wrapper with package-owned `browser_automation.runtime`. Every supported CLI/MCP browser operation acquires the secure per-port advisory establishment gate before its authoritative readiness probe. A truly pre-existing endpoint is classified `DURABLE_EXISTING` and releases the gate without abort authority. A product-owned launch remains `PENDING_OWNED`, holding the gate and exact process-group authority through Playwright CDP connection and first-context validation. Success clears abort authority before unlock (`promote`); timeout, failure, or cancellation completes exact owned-group cleanup before unlock (`abort`). A concurrent second caller must remain before probe/connect until the first owner promotes or aborts, then make a gated current-state decision.

All preserved behavior remains required: browser-owned opaque CDP target continuity across short-lived processes; one application authority behind CLI and retained MCP stdio/HTTP; strict JSON and stable exits; atomic workspace artifacts; explicit tab ownership; exact-locator launcher/bootstrap; frozen uv; loopback MCP default and explicit non-loopback warning; complete old identity/runtime/dependency removal. Persisted-data disposition remains `Not Affected`: page/profile state is Chrome-owned and directly readable.

`CRR-009` independently passed source review at `9.5/10` (`94.9/100`) with no open findings. Reviewer evidence includes the focused runtime/argument/skill-contract matrix (`53`), full Chrome-free suite (`101 passed / 7 skipped`), frozen lock, compile, Bash/ShellCheck, skill validation, generic package/help probes, and dependency/import/removal scans. It intentionally does not claim real Chrome, live MCP, Linux runtime behavior, a practical cross-process PREM-004 interleaving, or current fresh-agent execution.

## Changed Behavior Summary

| Behavior / Boundary | Current Change | Coverage Consequence |
| --- | --- | --- |
| `BEH-001`–`BEH-006` / CLI/application/browser/artifact behavior | Preserved through owned runtime | Rerun independent generic CLI processes, real target continuity/effects, strict outputs/errors, PNG/JPEG/artifacts, rollback, and ownership survival. |
| `BEH-007` / retained MCP | Preserved on owned runtime | Execute production stdio and streamable HTTP with real browser effects, generic identity/logging, loopback default, invalid config, and non-loopback warning. |
| `BEH-008`–`BEH-009` / portable generic capability | Preserved | Rerun launcher/bootstrap/relocation/Linux/package/removal scans and replace superseded fresh-agent evidence. |
| `BEH-010` / direct operation arguments | Added procedural contract | Prove direct inline `--script` plus structured inline `--arg-json` through unit mapping, production CLI, and fresh-agent observe/act/verify. |
| `BEH-011` / self-contained atomic runtime | Added runtime/process boundary | Prove durable-existing attach, product-owned launch from unavailable endpoint, later-process persistence, exact owned-group failure cleanup without unrelated-Chrome termination, and gated two-caller sequencing. |
| `brui-core`, old runtime wrapper, manager/UI/clipboard/singleton/global-kill/download no-op | Removed | Prove absence from source, dependency graph, lock, built packages, entrypoints, and active docs/tests; never add compatibility coverage. |

## Changed Surface And Boundary Classification

| Surface / Boundary | Affected? | Repository Evidence | Material Remaining Risk | Selected Direct Evidence |
| --- | --- | --- | --- | --- |
| Domain / application | Preserved | Unit/application tests and CRR-009 | Real CDP effects through packaged CLI | Real Chrome CLI matrix |
| API / transport | Yes | CLI/MCP adapter and config units | Real stdout/process, MCP stdio/HTTP sessions | Production launchers and MCP clients |
| Browser integration | Yes | Mocked runtime/session units | Real Playwright attach/launch/target continuity | Isolated Chrome, separate processes |
| Process / lifecycle | Yes, critical | Deterministic gate/process/session units | OS locks/groups, actual readiness/promotion window, later-process durability | Product-owned launch, failure-group probe, practical interleaving |
| Packaging / bootstrap / identity | Yes | Contract tests and reviewer package probes | Clean relocated/frozen/Linux/fresh-agent execution | Host package matrix, Ubuntu launcher matrix, fresh agent |
| Artifacts / filesystem | Preserved | Policy/application units | Real PNG/JPEG bytes, CWD/workspace publication | Existing real integration plus fresh-agent artifact |
| Persisted browser state | No migration | Browser-owned IDs by design | State continuity after owned launch/client exit | Later independent CLI processes |
| Authentication / session ownership | Bounded | Explicit tab rules | User-owned attached tab survival | Pre-seeded isolated user tab |
| Desktop / frontend | No | N/A | N/A | None |
| Distributed / queue | No | N/A | Only local multi-process gate is in scope | Local independent-process interleaving |

## Project Execution Discovery

- Assigned worktree: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill`
- Active project root: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/browser-automation`
- Stack: Bash launchers; Python `>=3.11`; uv frozen lock; Playwright; FastMCP/MCP; Chrome/Chromium CDP; POSIX advisory locks/process groups for supported macOS/Linux.
- Authority: repository `README.md`; project `README.md`; `SKILL.md`; `pyproject.toml`/`uv.lock`; `scripts/browser`; `scripts/browser-mcp`; integration fixtures; approved requirements/design; CRR-009.
- Supported real-test opt-in: `BROWSER_AUTOMATION_REAL_TESTS=1`.
- Runtime configuration: isolated `CHROME_REMOTE_DEBUGGING_PORT`, `CHROME_USER_DATA_DIR`, `CHROME_PROFILE_DIRECTORY`, `CHROME_LOG_PATH`, `BROWSER_AUTOMATION_CHROME_BIN`, and `BROWSER_AUTOMATION_WORKSPACE`; no account or secret.
- MCP configuration remains `BROWSER_MCP_*`; loopback is default and non-loopback is warning-only by approved policy.
- Chrome executable: local Google Chrome 151 on macOS. API/E2E will use unique ports/profiles and an executable wrapper only where a headless product-owned launch needs deterministic PID/group evidence; the wrapper `exec`s the real Chrome in the production-created session/group.
- No active `brui-core` dependency. Frozen install and the actual `browser` / `browser-mcp-server` entrypoints are authoritative.
- Git remote refresh/rebase is out of API/E2E scope and remains delivery-owned.

| Component | Start / Execution | Readiness | Ownership / Cleanup |
| --- | --- | --- | --- |
| Durable-existing Chrome | Test fixture starts real headless Chrome on owned port/profile | `/json/version` | Fixture-owned group; terminate only that group |
| Product-owned Chrome | Production `scripts/browser health-check` starts absent endpoint using configured real executable wrapper | CLI success plus `/json/version` | Must outlive CLI; record exact exec-preserved PGID; terminate that group only after evidence |
| Failure endpoint | Test-owned executable group exposes syntactically valid version metadata but unusable WebSocket | Probe succeeds, Playwright connection fails | Product must reap exact group before returning; unrelated real Chrome remains reachable |
| Local site | `ThreadingHTTPServer` on owned loopback port | HTTP GET | Shutdown/join owned server |
| CLI | Exact locator -> sibling `scripts/browser`, unrelated CWD | One strict JSON stdout value | Process exits; close task tabs only |
| MCP | `scripts/browser-mcp` via SDK clients | initialize/list_tools or TCP ready | Close/terminate only owned MCP processes; inspect logs |
| Linux probe | Docker `ubuntu:24.04`, copied launcher/runtime-focused fakes | Structured output and lock sequencing | `--rm`; isolated temp |
| Fresh agent | Ephemeral `codex exec` with exact locator and task only | Transcript plus browser/artifact postconditions | Verify user tab/Chrome; close task tab; remove owned temp |

## Existing Durable Coverage Inventory And Validity

| Path / Scenario | Current Intent | Decision | Action |
| --- | --- | --- | --- |
| `tests/unit/test_runtime.py` | Owned config/executable/probe/gate/group/session lifecycle; deterministic PREM-004 abort and promote interleavings | `Still Valid` (implementation-added/updated; reviewed CRR-009) | Retain; rerun focused and full. |
| `tests/unit/test_cli_and_mcp.py` | Direct/file/stdin/arg-file mapping, strict CLI envelopes/readiness, MCP config | `Still Valid` (implementation-updated; reviewed CRR-009) | Retain; rerun. |
| Other `tests/unit/test_*.py` | Application/policy/codec/MCP adapter behaviors | `Still Valid` | Retain; rerun full. |
| `tests/integration/test_skill_contract.py` | Exact locator/sibling launcher, direct-argument norm, generic package/runtime/removal contract | `Still Valid` (implementation-updated; reviewed CRR-009) | Run focused first. |
| `tests/integration/test_cli_real_chrome.py` (4 existing) | Durable-existing real Chrome, cross-process IDs/effects, direct script/arg, PNG/JPEG, safety/rollback/ownership | `Updated / Still Valid` | The one stale `localhost` rendering expectation was replaced with authoritative owned-runtime `127.0.0.1`; focused, integration, and full real-enabled reruns pass. |
| `tests/integration/test_launcher_black_box.py` | Readiness/bootstrap/relocation and failure envelopes | `Still Valid` | Rerun. It does not prove successful production-owned Chrome durability. |
| `tests/integration/test_mcp_transports_real.py` | Live stdio/HTTP and config/warning/log behavior | `Still Valid` | Rerun with owned isolated Chrome. |
| `conftest.py`, `support.py`, `pyproject.toml` | Marker/environment/process helpers | `Needs Update` only as narrowly required for safe product-owned real-Chrome setup/cleanup | Prefer local helper in the new test; avoid broad fixture changes. |
| API-REV-003 Linux/fresh-agent evidence | Superseded branded locator/runtime and pre-SR-007 procedure | `Replace` | Overwrite canonical current evidence after successful SR-009 runs; preserve revision history. |

## Coverage Gap Decisions

| Gap | Decision | Rationale / Planned Evidence |
| --- | --- | --- |
| Real production-owned launch from unavailable endpoint and later independent-process persistence | `Add Durable Coverage — Completed` | Added an isolated `real_chrome` test using production CLI and a PID-recording wrapper that `exec`s real Chrome; exact group, later-process target/read/health use, persistence, and scoped cleanup pass. |
| Failed initial connection exact-group cleanup plus unrelated Chrome survival | `Use Temporary Executable Probe Only — Completed` | Production CLI spawned an unusable-CDP group; it was dead before the strict failure envelope returned, while a separately owned real Chrome remained alive/reachable. |
| Practical PREM-004 pending-owner interleaving | `Use Temporary Executable Probe Only — Completed` | A real product-owned Chrome reached readiness with abort authority; a separate production CLI waiter remained blocked/empty until promotion, then connected. Durable units retain both abort/promotion branches. |
| Current fresh-agent direct-argument and exact-locator journey | `Use Temporary Executable Probe Only — Completed` | Fresh Codex execution passed exact read/sibling resolution/task-CWD/direct-argument/recovery/artifact/ownership postconditions. |
| Linux launcher and gate behavior | `Use Temporary Executable Probe Only — Completed` | Ubuntu 22.04 aarch64 executed 31 runtime and two launcher nodes: `33 passed / 1 deselected`. |

## Durable Coverage Changes

- Added: `browser-automation/tests/integration/test_runtime_real_chrome.py`, one focused production-owned real-Chrome lifecycle test with local safe helpers.
- Updated: `browser-automation/tests/integration/test_cli_real_chrome.py`, only the stale removed-wrapper `localhost` rendering expectation to current owned-runtime `127.0.0.1`.
- Remove: none.
- Review routing consequence: any such repository-resident test edit requires proportional `code_reviewer` re-review before delivery.

## Repository And Broader Execution Plan

| Order | Command / Scenario | Boundary | Planned Evidence |
| --- | --- | --- | --- |
| 1 | Focused runtime, direct-argument, skill-contract, and new owned-lifecycle nodes | `REQ-014`/`REQ-015` narrow regression | Pass: `54`; new lifecycle `1`; stale assertion rerun `1` |
| 2 | Default full pytest with JUnit | Chrome-free regression and exact skip policy | Pass: `101 passed / 8 skipped` |
| 3 | Real-enabled integration suite with JUnit | Real Chrome CLI/launcher/MCP plus owned launch | Pass: `13` |
| 4 | Real-enabled full project with JUnit | Whole current-source regression | Pass: `109` |
| 5 | Frozen lock, compile, collection, Bash/ShellCheck, skill validator, package/entrypoint/help, active old-identity/runtime/dependency/removal and diff scans | Package/static/current identity | Pass: `static-and-package-checks.log` |
| 6 | Practical process-boundary PREM-004 plus failure exact-group/unrelated-Chrome probes | OS gate/group lifecycle realism | Pass: `owned-runtime-process-boundary.log` / `.json` |
| 7 | Generic Ubuntu launcher/gate matrix | Supported Linux Bash behavior | Pass: `33 passed / 1 deselected` |
| 8 | Fresh exact-locator agent journey using direct `--script`/`--arg-json` from unrelated CWD | User/agent executable contract | Pass: 21 commands/20 launcher calls; all postconditions true |

First current real-integration execution result: `12 passed / 1 failed`. The failure is an API/E2E-owned stale coverage assertion, not a product defect: `health-check` correctly returned the current fixed-loopback endpoint `http://127.0.0.1:<port>`, while the preserved test expected the removed wrapper's `http://localhost:<port>` rendering. `BrowserRuntimeConfig`, SR-009, and the loopback contract make `127.0.0.1` authoritative. The investigation is updated before editing that durable assertion; the whole real suite will be rerun after the local fix. The same command also exposed an evidence-harness path issue: a relative JUnit destination was interpreted under uv's project working directory. The misplaced API-owned output will be removed and all reruns use absolute evidence paths; this is not a product classification.

## Post-Repository Confidence And Broader-Validation Decision

- Pre-execution confidence: `80%`.
- Post-repository confidence: `96%` after the current 109-test/static/package/Linux repository matrix.
- Final confidence after broader validation: `97%`; no category below `90%` and no critical criterion missing.
- Broader validation: `Required and completed successfully`.
- Selected modes: real Chrome/process lifecycle, live CLI/MCP, practical cross-process probes, Linux Bash container, and fresh agent.
- Evidence gain: direct practical PREM-004, exact failure-group/unrelated-Chrome, and fresh-agent proof closed the remaining material mock/cognition gaps.
- Desktop decision: no desktop app exists. Browser validation is the actual capability boundary; native Windows and non-Chromium engines remain out of first-release scope.

## Live Fixture And Safety Plan

- Allocate unique loopback ports, profiles, workspaces, logs, lock roots, and site state.
- Never touch or terminate a user browser. Any real Chrome called “unrelated” is separately API/E2E-created with its own recorded process group and must survive the tested failure cleanup before being explicitly torn down by the harness.
- For product-owned launches, a test-owned executable wrapper records its own PID then `exec`s the selected real Chrome with headless/safe flags. `start_new_session=True` in product source makes that PID the exact owned group leader; teardown targets only that recorded group after persistence assertions.
- Seed a deterministic user-owned tab, keep opaque browser target IDs unchanged across processes, close only task-created tabs, and assert the user-owned target survives.
- Keep all artifacts under an isolated caller workspace; assert PNG/JPEG signatures and metadata.
- Capture commands, environment names (not secrets), process/target observations, logs, and cleanup results. Confirm no owned processes remain.

## Not Tested / Infeasible / Deferred

| Boundary | Reason | Risk / Follow-up |
| --- | --- | --- |
| Native Windows | Explicitly outside first-release Bash/POSIX scope | None for approved release; future platform work |
| Linux Chrome engine and broader Chrome versions | Local real engine is Chrome 151/macOS; Linux covers launcher/gate semantics | Bounded platform/version breadth; future CI matrix |
| Other agent runtimes/vendors | Executable agent is current Codex runtime | Loader-specific breadth; contract requires exact readable locator |
| Intentional same-tab multi-agent mutation races | Requirements assign serialization to callers | Retain documented residual |
| Remote MCP authentication | Explicitly out of scope | Prove loopback default and non-loopback warning only |

## Superseded Hold Note

Round 4 originally began under SR-006 and was immediately held when the user corrected direct-argument behavior. Provisional pre-hold counts (`2`, `64`, `69/7`, `12`, `76`) were never classified as API-REV-004 and do not prove SR-009. The requirement gap is resolved by SR-007–SR-009, ARCH-REV-008, IR-006, and CRR-009. Current evidence will replace the canonical execution logs; API-REV-003 remains the latest completed history until this round finishes.

## Ambiguities Or Reroute Triggers

None currently. Reroute if direct-argument behavior contradicts SR-007, a supported caller bypasses the gate, a pending owner unlocks before terminal cleanup/promotion, a real product-owned Chrome does not persist, exact failure cleanup touches an unrelated group, or package scans reveal removed/legacy runtime surface.

## Investigation Decision

- Proceed To API/E2E Execution: `Completed`
- Repository-Resident Durable Coverage Added / Updated / Removed: `Yes — one focused real product-owned lifecycle test added; one stale endpoint assertion updated; no removals`
- Reroute Required Before Execution: `No`
- Final routing if validation passes: `code_reviewer` for proportional review of API/E2E-owned durable test changes; do not route directly to delivery.
- Notes: This investigation was refreshed before current-source execution/durable edits and then kept current when the stale assertion was discovered. Execution is complete at `Pass / 97%`; `API-REV-004` records the result.
