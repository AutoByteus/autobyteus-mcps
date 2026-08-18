# API/E2E Revision Record

The current `api-e2e-coverage-investigation.md` and `api-e2e-execution-coverage-report.md` are authoritative. This record preserves the concise chronological validation history.

## Revision Index

| Revision ID | Triggering Role / Report / Round | Related Upstream Revision IDs | Prior Result / Confidence | Current Result / Confidence |
| --- | --- | --- | --- | --- |
| `API-REV-001` | `code_reviewer` / `code-review-report.md` / API/E2E round 1 after `CRR-003` | `SR-001`–`SR-003`; `ARCH-REV-003`; `IR-001`–`IR-003`; `CRR-001`–`CRR-003` | `N/A` | `Pass / 97%` |
| `API-REV-002` | `code_reviewer` / `api-e2e-test-review-report.md` / API/E2E round 2 after `CRR-004` | `SR-001`–`SR-003`; `ARCH-REV-003`; `IR-001`–`IR-003`; `CRR-001`–`CRR-004` | `Pass / 97%` | `Pass / 97%` |
| `API-REV-003` | `code_reviewer` / `code-review-report.md` / API/E2E round 3 after `CRR-006` | `SR-001`–`SR-005`; `ARCH-REV-003`–`ARCH-REV-005`; `IR-001`–`IR-004`; `CRR-001`–`CRR-006`; `DR-001` | `Pass / 97%` | `Pass / 97%` |
| `API-REV-004` | `code_reviewer` / `code-review-report.md` / resumed API/E2E round 4 after `CRR-009` | `SR-007`–`SR-009`; `ARCH-REV-008`; `IR-006`; `CRR-009` | `Pass / 97%` (`API-REV-003`; later contract superseded/held) | `Pass / 97%` |

## Revision Entries

### API-REV-001 — Real Chrome, packaged transports, and fresh-agent baseline

- Triggering role, report path, and round: `code_reviewer`; `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/code-review-report.md`; first API/E2E round after passing `CRR-003`.
- Triggering finding or scenario IDs: No open code finding; validation scenarios `AE2E-REPO-001`, `AE2E-CLI-001`–`004`, `AE2E-LAUNCH-001`, `AE2E-MCP-001`/`002`, `AE2E-SKILL-001`, `AE2E-PLATFORM-001`, and `AE2E-AGENT-001`–`003`.
- Related solution, architecture-review, implementation, code-review, or delivery revision IDs: `SR-001`, `SR-002`, `SR-003`; `ARCH-REV-003`; `IR-001`, `IR-002`, `IR-003`; `CRR-001`, `CRR-002`, `CRR-003`; delivery `N/A`.
- Why this baseline or coverage/execution revision was recorded: Establish the first authoritative API/E2E result after required coverage investigation and direct execution of the previously unproven browser, process, transport, platform, and skill-agent boundaries.
- Coverage decisions or durable test paths changed: Added opt-in `tests/integration/` coverage for real CLI/Chrome, launcher black-box, and live MCP stdio/HTTP; registered pytest markers in `pyproject.toml`; removed nothing. The already-deleted old numeric-ID suites remain correctly replaced rather than restored.
- Scenarios added, changed, removed, or rechecked: Added the thirteen scenario IDs above; rechecked all 64 valid unit/adapter tests and package/shell/skill checks; no scenario removed.
- Commands, environment, fixture, or broader-validation delta: Added isolated Chrome 151 with temporary profile/port, deterministic loopback site, independent production CLI processes, production MCP clients/processes, relocated first-run bundle, Ubuntu 24.04 Bash matrix, and one fresh ephemeral Codex agent constrained to `SKILL.md`/CLI help.

#### Prior Failure Resolution

None. No prior completed API/E2E result exists.

- Canonical artifacts and sections updated: Complete `api-e2e-coverage-investigation.md`; created `api-e2e-execution-coverage-report.md`; created this revision record; retained JUnit/log/fresh-agent evidence under the canonical ticket evidence directory.
- Prior result and confidence: `N/A`
- Current result and confidence: `Pass / 97%`
- New or remaining failure IDs: `None`
- Recommended recipient: `code_reviewer` for proportional review of changed durable coverage.
- Remaining risks, blocked evidence, or untested scope: Future Chrome/CDP versions, Linux Chrome engine, other agent vendors, and intentionally concurrent same-tab callers are bounded breadth risks. No critical acceptance criterion is unproven and no validation is blocked.


### API-REV-002 — Durable JPEG, truthful selection, and owned-temp rework

- Triggering role, report path, and round: `code_reviewer`; `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/api-e2e-test-review-report.md`; second API/E2E round after proportional test-code review `CRR-004` returned `Fail / Local Fix`.
- Triggering finding or scenario IDs: `TR-001`, `TR-002`, `TR-003`; rechecked `AE2E-CLI-002`, `AE2E-LAUNCH-001`, `AE2E-MCP-002`, `AE2E-CONFIG-001`, plus the complete default/integration/full suites.
- Related solution, architecture-review, implementation, code-review, or delivery revision IDs: `SR-001`, `SR-002`, `SR-003`; `ARCH-REV-003`; `IR-001`, `IR-002`, `IR-003`; `CRR-001`–`CRR-004`; delivery `N/A`.
- Why this baseline or coverage/execution revision was recorded: Preserve the completed result after correcting the three bounded durable-test findings and refreshing every affected/default/real-enabled execution artifact. `CRR-004` did not reclassify the passing implementation source or `API-REV-001` runtime evidence as a product failure.
- Coverage decisions or durable test paths changed: Updated `tests/integration/test_cli_real_chrome.py` with production-CLI JPEG and format/extension proof; updated `test_launcher_black_box.py` with test-owned `TMPDIR`, default execution for non-live cases, and a deterministic non-CDP endpoint; updated `test_mcp_transports_real.py` so only live transports require Chrome and invalid config has no live-Chrome fixture. No product source, pytest configuration, test path, or coverage path was added/removed.
- Scenarios added, changed, removed, or rechecked: Changed/rechecked `AE2E-CLI-002`, `AE2E-LAUNCH-001`, `AE2E-MCP-002`, and `AE2E-CONFIG-001`; rechecked all ten integration scenarios and all 74 project tests; no scenario removed.
- Commands, environment, fixture, or broader-validation delta: Four affected nodes passed in `12.67s`; default execution is now `67 passed, 7 skipped`; integration is `10 passed in 36.94s`; full real-enabled execution is `74 passed in 36.73s`. Marker collection proves seven real-Chrome and three Chrome-free integration scenarios. No additional Linux/fresh-agent run was required because the rework changes only durable tests/reports; the successful `API-REV-001` evidence remains applicable.

#### Prior Failure Resolution

| Finding ID | Prior Status | Current Status | Related Revision References | Verification Evidence |
| --- | --- | --- | --- | --- |
| `TR-001` | Open at `CRR-004` | Resolved locally; pending proportional re-review | `API-REV-002`, `AE2E-CLI-002` | `.jpeg` production-CLI success returns `image/jpeg`, truthful byte count, SOI/EOI bytes; `.png` with `--format jpeg` returns `INVALID_ARGUMENT` and publishes no artifact; affected/integration/full suites pass. |
| `TR-002` | Open at `CRR-004` | Resolved locally; pending proportional re-review | `API-REV-002`, `AE2E-CONFIG-001`, `AE2E-LAUNCH-001`, `AE2E-MCP-002` | Collection lists seven `real_chrome` and three Chrome-free integrations; default run executes the latter (`67 passed, 7 skipped`); invalid MCP config has no Chrome fixture; all real-enabled tests pass. |
| `TR-003` | Open at `CRR-004` | Resolved locally; pending proportional re-review | `API-REV-002`, `AE2E-LAUNCH-001` | Every readiness/missing-bundle branch receives a created test-owned `TMPDIR` and immediately asserts it is empty; affected/default/integration/full suites pass. |

- Canonical artifacts and sections updated: Refreshed `api-e2e-coverage-investigation.md`, `api-e2e-execution-coverage-report.md`, this revision record, all three JUnit/log suites, static/package evidence, and new focused `affected-rework-pytest.log`.
- Prior result and confidence: `Pass / 97%` at `API-REV-001`; separate proportional test review `Fail / Local Fix` at `CRR-004`.
- Current result and confidence: `Pass / 97%`
- New or remaining failure IDs: `None` in API/E2E execution; `TR-001`–`TR-003` await reviewer confirmation.
- Recommended recipient: `code_reviewer` for proportional re-review of the three updated durable test files before delivery.
- Remaining risks, blocked evidence, or untested scope: Future Chrome/CDP versions, Linux Chrome engine, other agent vendors, and intentionally concurrent same-tab callers remain bounded breadth risks. No critical acceptance criterion is unproven and no validation is blocked.


### API-REV-003 — Exact advertised-skill locator and task-CWD agent proof

- Triggering role, report path, and round: `code_reviewer`; `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/code-review-report.md`; third API/E2E round after `CRR-006` passed `IR-004` and requested current durable/fresh-agent proof for `SR-004`/`SR-005`.
- Triggering finding or scenario IDs: No open source-review finding; new `AE2E-SKILL-CONTRACT-001` and `AE2E-AGENT-004`, plus re-executed `AE2E-REPO-001`, `AE2E-CLI-001`–`004`, `AE2E-LAUNCH-001`, `AE2E-MCP-001`/`002`, `AE2E-SKILL-001`, and `AE2E-AGENT-001`–`003` through the corrected initiating path.
- Related solution, architecture-review, implementation, code-review, API/E2E-test-review, or delivery revision IDs: `SR-001`–`SR-005`; `ARCH-REV-003`–`ARCH-REV-005`; `IR-001`–`IR-004`; `CRR-001`–`CRR-006`, including proportional test-code Pass at `CRR-005`; `API-REV-001`, `API-REV-002`; `DR-001`.
- Why this coverage/execution revision was recorded: Delivery re-entry changed the supported public resource-discovery procedure after the prior API/E2E result. The pre-SR-004 agent transcript was explicitly superseded, so current durable assertions and a replacement independent-agent execution were required even though launcher/Python/MCP source was unchanged.
- Coverage decisions or durable test paths changed: Added only `autobyteus-browser/tests/integration/test_skill_contract.py`. It asserts that every launcher mention is the one relative `scripts/autobyteus-browser` value, that resolution begins at the exact advertised/read file and preserves the task CWD, and that the skill exposes no public locator variable, persistent-state prerequisite, vendor home, PATH registration, bundle `cd`, absolute install path, or scan/guess fallback. No existing test or product source was updated/removed by API/E2E.
- Scenarios added, changed, removed, or rechecked: Added `AE2E-SKILL-CONTRACT-001` and `AE2E-AGENT-004`; rechecked all prior repository scenarios and agent workflows through the new initiating path; removed none. The old agent transcript was replaced as evidence, not retained as current proof.
- Commands, environment, fixture, or broader-validation delta: Focused contract `1 passed`; default `68 passed, 7 skipped`; real integration `11 passed`; full real-enabled project `75 passed`; frozen/static/package/skill checks passed. A fresh ephemeral Codex agent received only the exact advertised skill locator plus task request, worked from an unrelated temporary CWD, issued 25 direct absolute sibling-launcher commands across 26 independent shell executions, exercised real Chrome workflows/recovery, produced a caller-relative PNG, preserved the user-owned tab, closed task tabs, and left Chrome alive for harness verification.

#### Prior Failure Resolution

None. `API-REV-002` and its proportional review at `CRR-005` were Pass with no unresolved failure. The initial focused-test occurrence-count assertion and first temporary-harness relative-artifact verifier were API/E2E-local corrections made before the completed round-3 result; final focused/default/real/agent reruns all pass.

- Canonical artifacts and sections updated: Refreshed `api-e2e-coverage-investigation.md`; replaced the latest state in `api-e2e-execution-coverage-report.md`; appended this entry; refreshed default/integration/full/static logs and JUnit; added focused contract log, exact locator prompt, and independent locator verification; replaced the canonical fresh-agent events/stderr/final result.
- Prior result and confidence: `Pass / 97%` at `API-REV-002`; proportional test-code Pass at `CRR-005`; delivery baseline `DR-001` was verification-ready before the instruction re-entry.
- Current result and confidence: `Pass / 97%`
- New or remaining failure IDs: `None`
- Recommended recipient: `code_reviewer` for proportional review of `test_skill_contract.py`; delivery must wait for that review.
- Remaining risks, blocked evidence, or untested scope: Future Chrome/CDP versions, Linux Chrome engine, other agent vendors, and intentionally concurrent same-tab callers remain bounded breadth risks. No critical acceptance criterion is unproven and no validation is blocked.


### API-REV-004 — Direct arguments and atomic owned-Chrome lifecycle proof

- Triggering role, report path, and round: `code_reviewer`; `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/code-review-report.md`; resumed API/E2E round 4 after `CRR-009` passed `IR-006` and authorized SR-009 current-source execution.
- Triggering finding or scenario IDs: No open source-review findings. Rechecked the existing matrix and added `AE2E-RUNTIME-001`–`003`, `AE2E-PLATFORM-002`, and `AE2E-AGENT-005` for product-owned launch, practical gate sequencing, exact failed-group cleanup, Linux owned-runtime behavior, and current generic direct-argument agent use.
- Related revisions: `SR-007`, `SR-008`, `SR-009`; `ARCH-REV-007`/`DR-006`/`PREM-004`, resolved at `ARCH-REV-008`; `IR-006`; `CRR-009`; prior `API-REV-001`–`003`; prior delivery history `DR-001`, `DR-002` is truthful but superseded-contract evidence.
- Why this revision was recorded: The public identity, normal script-call procedure, browser runtime ownership, dependency graph, and cross-process Chrome establishment invariant all changed after API-REV-003. Prior generic SR-006 provisional runs were held and never classified. Current direct system-boundary evidence was therefore required.
- Coverage decisions or durable test paths changed: Added `browser-automation/tests/integration/test_runtime_real_chrome.py` for product-owned real Chrome launch/promotion/later-process durability/scoped cleanup. Updated one assertion in `test_cli_real_chrome.py` from the removed wrapper's `localhost` rendering to the current fixed `127.0.0.1` owned-runtime endpoint. Removed no coverage.
- Scenarios added, changed, removed, or rechecked: Added `AE2E-RUNTIME-001`–`003`, `AE2E-PLATFORM-002`, and `AE2E-AGENT-005`; rechecked repository, skill contract, CLI, artifacts, launcher, live MCP, package/removal, and current direct-argument scenarios. No scenario or required behavior was removed.
- Commands/environment delta: focused current matrix `54 passed`; default `101 passed / 8 skipped`; real integration `13 passed`; full real-enabled `109 passed`; Ubuntu runtime/launcher `33 passed / 1 deselected`; static/frozen/package/removal checks passed. A practical multi-process owner/waiter run proved the waiter blocked through a ready-but-abortable endpoint until promotion. A separate production failure run proved exact group cleanup before return and unrelated real-Chrome survival. A fresh ephemeral Codex agent received only the exact generic skill locator/task, issued 20 sibling-launcher calls across 21 command executions, used direct `--script`/`--arg-json`, recovered from `TAB_NOT_FOUND`, created a valid PNG, preserved the user tab, and cleaned task tabs.

#### Prior Failure Resolution

No unresolved prior completed API/E2E failure applied. API-REV-003 was Pass. The subsequent SR-006 round was correctly held before API-REV-004 existed; SR-007–SR-009, ARCH-REV-008, IR-006, and CRR-009 resolved that upstream contract/design re-entry. Within this round, a stale API/E2E endpoint assertion and two temporary verifier assumptions were corrected locally before complete passing reruns; no product failure resulted.

- Canonical artifacts updated: refreshed `api-e2e-coverage-investigation.md` and `api-e2e-execution-coverage-report.md`; appended this entry; replaced current default/integration/full/static/Linux/fresh-agent evidence; added focused owned-runtime, stale-assertion, and practical process-boundary evidence.
- Prior result and confidence: `Pass / 97%` at API-REV-003; later contract superseded and round-4 execution held without a completed result.
- Current result and confidence: `Pass / 97%`.
- New or remaining failure IDs: `None`.
- Recommended recipient: `code_reviewer` for proportional review of the two changed durable integration-test paths; delivery must wait.
- Remaining risks: Linux real Chrome-engine/version breadth, other agent vendors, and intentional caller-violating same-tab races. The practical waiter run used the promotion branch; both promotion and abort waiter branches remain deterministic durable unit evidence, and exact abort was also exercised across the real process boundary. No critical criterion is blocked or unproven.
