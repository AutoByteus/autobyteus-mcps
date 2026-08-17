# API/E2E Revision Record

The current `api-e2e-coverage-investigation.md` and `api-e2e-execution-coverage-report.md` are authoritative. This record preserves the concise chronological validation history.

## Revision Index

| Revision ID | Triggering Role / Report / Round | Related Upstream Revision IDs | Prior Result / Confidence | Current Result / Confidence |
| --- | --- | --- | --- | --- |
| `API-REV-001` | `code_reviewer` / `code-review-report.md` / API/E2E round 1 after `CRR-003` | `SR-001`–`SR-003`; `ARCH-REV-003`; `IR-001`–`IR-003`; `CRR-001`–`CRR-003` | `N/A` | `Pass / 97%` |
| `API-REV-002` | `code_reviewer` / `api-e2e-test-review-report.md` / API/E2E round 2 after `CRR-004` | `SR-001`–`SR-003`; `ARCH-REV-003`; `IR-001`–`IR-003`; `CRR-001`–`CRR-004` | `Pass / 97%` | `Pass / 97%` |

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
