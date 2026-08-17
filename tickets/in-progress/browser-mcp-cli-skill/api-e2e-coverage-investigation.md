# API/E2E Coverage Investigation

## Investigation Meta

- Requirements Doc: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/requirements.md`
- Investigation Notes: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/investigation-notes.md`
- Design Spec: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/design-spec.md`
- Supplemental Task Artifacts: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/cli-conversion-analysis.md`
- Solution Revision Record: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/solution-revision-record.md`
- Design Review Report: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/design-review-report.md`
- Architecture Review Revision Record: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/architecture-review-revision-record.md`
- Implementation Handoff: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/implementation-handoff.md`
- Implementation Revision Record: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/implementation-revision-record.md`
- Code Review Report: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/code-review-report.md`
- Code Review Revision Record: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/code-review-revision-record.md`
- Delivery Revision Record (delivery re-entry only): `N/A`
- Relevant Delivery Revision IDs: `N/A`
- API/E2E Revision Record: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/api-e2e-revision-record.md`
- Current API/E2E Revision ID: `API-REV-002`
- Current Investigation Round: `2`
- Trigger: `code_reviewer` proportional API/E2E test-code review round 1 / `CRR-004` / `Fail / Local Fix`, findings `TR-001`–`TR-003`. The implementation source remains `Pass` at `CRR-003`, and the successful product/runtime evidence at `API-REV-001` remains valid.
- Prior Investigation Reviewed: Round 1 canonical investigation and completed `API-REV-001` (`Pass / 97%`), plus `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/api-e2e-test-review-report.md` at `CRR-004`.
- Latest Authoritative Investigation: `Round 2 completed investigation, updated before durable corrections and again with final rerun evidence`

## Current Requirement And Design Basis

The approved change replaces the process-local numeric-tab MCP product with one relocatable `autobyteus-browser/` skill/runtime bundle. A self-locating Bash launcher invokes a task-oriented CLI through frozen `uv`; CLI and retained MCP adapters delegate to one transport-neutral `BrowserApplication`; `BrowserRuntime` reconnects to the first Chrome context and uses browser-owned CDP target IDs across short-lived processes. Every non-help CLI invocation must emit exactly one strict schema-v1 JSON stdout value with stable exit categories. The shared core must enforce HTTP(S), bounded inputs, workspace-contained artifacts, explicit overwrite, single-tab close, and no global Chrome shutdown.

Critical executable proof is explicitly required by `REQ-012` and `AC-001`, `AC-004`, `AC-005`, `AC-008`, `AC-009`, `AC-011`, and `AC-012`: real isolated Chrome target continuity across independent processes; truthful list/attach/open/operate/close behavior; no stray page or global shutdown; artifacts and browser-operation edge cases; zero-human first-run/relocation launcher behavior; retained MCP over live stdio and streamable HTTP; and fresh-agent skill workflows. `CRR-003` confirms the source is ready but does not claim any of that runtime evidence.

The approved persisted-data outcome is `Not Affected`. Chrome profile/site data remains Chrome-owned and is read directly; numeric IDs were memory-only and must not be migrated or protected by compatibility coverage.

## Changed Behavior Summary

| Behavior ID / Boundary | Change Type | Upstream Evidence | Coverage Consequence |
| --- | --- | --- | --- |
| `BEH-001` / CLI process boundary | Changed | `REQ-001`–`REQ-006`, `AC-001`–`AC-006`, `DS-001` | Durable real-Chrome coverage must prove one target ID works from separate launcher/CLI processes without a daemon or active-tab fallback. |
| `BEH-002` / browser-owned discovery | Changed | `REQ-002`, `REQ-005`, `AC-001`, `AC-005` | Real multiple-page list/unique attach/ambiguous attach/external close/stale-ID coverage is required. |
| `BEH-003` / shared application boundary | Changed | `REQ-001`, `AC-002`, `AC-006`, `DS-001`/`DS-002` | Existing unit delegation remains relevant; live CLI and MCP transport scenarios must exercise the same real browser effects. |
| `BEH-004` / stdout, stderr, exit contract | Added | `REQ-003`, `REQ-004`, `AC-003`, `AC-004`, `DS-004`/`DS-006` | Black-box launcher/CLI tests must parse exactly one JSON value for success and each error category, including pre-readiness bootstrap failure. |
| `BEH-005` / portable agent skill | Added | `REQ-009`, `REQ-010`, `AC-010`, `AC-011` | Structural validation is necessary but insufficient; a clean independent agent process must follow only `SKILL.md` plus CLI help through the three required workflows. |
| `BEH-006` / browser and artifact safety | Changed | `REQ-007`, `REQ-008`, `AC-007`–`AC-009` | Real effects must prove output bytes, confinement, timeout rollback, unrelated-tab survival, and absence of any browser-global close. |
| `BEH-007` / retained MCP | Changed / Preserved | `REQ-011`, `AC-012`, `DS-002`/`DS-008` | The new launcher, nine-tool inventory, shared-core effects, loopback HTTP, explicit remote warning, invalid config, and both live transports need executable proof. |
| `BEH-008` / launcher bootstrap | Added | `REQ-003`, `REQ-007`, `REQ-010`, `AC-003`, `AC-004` | Relocated clean-bundle first invocation, unrelated CWD, missing files/uv, pre-CLI failure, help, and ready CLI failure require black-box coverage on macOS and a Linux Bash probe. |
| Numeric aliases, `browser_mcp` compatibility namespace, old wrapper, `close_browser` | Removed | Legacy Removal Policy, `AC-008`, `AC-012` | No compatibility-only coverage is valid. Removal/source scans remain appropriate; no old numeric assertions may be restored. |

## Changed Surface And Boundary Classification

| Surface / Boundary | Affected? | Actual Changed Boundary | Repository Evidence Available | Material Risk Not Exercised By That Evidence | Candidate Broader Validation Mode |
| --- | --- | --- | --- | --- | --- |
| Domain / backend logic | Yes | Browser application, runtime, content transforms, errors, policy | 64 unit/adapter tests | Real Playwright/CDP pages, timeout effects, output bytes | Real Chrome CLI lifecycle |
| API / transport / contract | Yes | CLI envelope and retained MCP stdio/HTTP | CLI and in-memory MCP unit tests | Real subprocess stdout/exit, stdio JSON-RPC, HTTP session/bind/logging | CLI plus live MCP clients |
| Frontend component / state | No | No repository frontend | N/A | N/A | None |
| Browser integration / user journey | Yes | Chrome first-context page discovery and operations | Fake page/session unit tests only | CDP target identity, browser DOM/evaluate/screenshot, page survival | Isolated Chrome and local deterministic web fixture |
| Authentication / session / permissions | Yes, bounded | Existing attached/user page ownership and profile preservation | Skill prose and fake attached page | Real attached tab is inspected without automatic close; profile is not mutated/deleted | Isolated user-owned tab fixture |
| Desktop renderer / web-equivalent UI | No | No wrapped desktop UI | N/A | N/A | None |
| Desktop shell / Electron-specific integration | No | No Electron/native shell | N/A | N/A | None |
| Process / lifecycle | Yes | Frozen launcher, short-lived Playwright clients, external Chrome owner | Mock disconnect and implementation probes | Independent processes, first run, signal/temp cleanup, no stray pages/global shutdown | CLI/launcher/lifecycle; Linux container shell probe |
| Persisted-data transition | Yes, assessed as not affected | Existing Chrome profile/site state is directly usable | Design/implementation checks and prior feasibility probe | Real process reconnect must preserve page and browser state | Isolated temporary Chrome profile |
| Worker / queue / distributed coordination | No | No worker/queue | N/A | Same-tab races are client sequencing, not a queue contract | Serialize tested workflow; residual external race noted |
| External integration | Yes | Chrome/Chromium, Playwright/CDP, `brui_core`, host `uv` | Locked versions and mocks | Browser/version/platform compatibility and auto-connect lifecycle | Chrome 151 on macOS; Linux Bash launcher probe |

## Project Execution Discovery

- Assigned task worktree / workspace: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill`
- Project type and runtime stack: Git worktree; Bash launchers; Python `>=3.11`; `uv`; Playwright 1.55; `brui-core` 2.0; FastMCP/MCP 1.28.1; Chrome/Chromium CDP.
- Conflicting, missing, or unclear project instructions: The project README documents only the unit command and defers real-browser setup details to Chrome/CDP configuration. `brui_core` auto-launch hard-codes Linux `/usr/bin/google-chrome`; therefore API/E2E will own an isolated Chrome process directly on macOS and point the application at its open port so `brui_core` connects rather than auto-launches. No `AGENTS.md`, contribution guide, Compose file, or repository browser-E2E runner exists.
- Required environment variables or secrets available: `N/A`; no account or secret is required. All browser state and pages will use a temporary profile and deterministic loopback HTTP fixture.

| Instruction / Configuration Path | Authority / Purpose | Commands, Setup, Or Constraints Learned |
| --- | --- | --- |
| `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/README.md` | Repository project inventory | `autobyteus-browser/` is the current capability root. |
| `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/autobyteus-browser/README.md` | Project execution contract | Unit command is `uv run --frozen --extra test python -m pytest tests/unit`; launcher must be skill-root relative; Chrome/CDP is supported; use non-default profile on Chrome 136+; retained MCP entry and env names are documented. |
| `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/autobyteus-browser/SKILL.md` | Agent-facing workflow authority | Preflight, explicit IDs, observe/act/verify, structured recovery, side-effect confirmation, ownership-aware cleanup, and no direct uv/Python invocation. |
| `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/autobyteus-browser/pyproject.toml` | Package/test config | Frozen project, `pytest`, console entries, current unit-only testpaths. Durable real integration coverage must be opt-in/marked to avoid requiring Chrome in the default suite. |
| `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/autobyteus-browser/.env.test` | Historical real-test setting | Only `CHROME_USER_DATA_DIR=./.chrome-profile`; it is unsafe for concurrent worktree runs and will not be reused. API/E2E uses a unique temporary profile/port. |
| `autobyteus-browser/scripts/autobyteus-browser` | Production CLI launcher | Captures caller PWD, self-resolves, checks bundle/uv, captures stdout, uses private ready marker, and owns one bootstrap envelope before readiness. |
| `autobyteus-browser/scripts/autobyteus-browser-mcp` | Production MCP stdio/HTTP launcher | Self-resolves, reserves stdout for protocol, sends diagnostics to a unique log directory, and executes the frozen MCP console entry. |
| Installed `brui_core.browser.browser_launcher` / `browser_manager` | Actual external lifecycle | Endpoint is `localhost:$CHROME_REMOTE_DEBUGGING_PORT`; an already-open port prevents auto-launch; connection uses first context; normal runtime cleanup must stop only Playwright. |

| Component / Dependency | Working Directory | Start / Setup Command | Runtime / Resource Notes | Readiness Check | Stop / Cleanup Method |
| --- | --- | --- | --- | --- | --- |
| Isolated Chrome 151.0.7922.138 | Temporary API/E2E workspace | `/Applications/Google Chrome.app/... --headless=new --remote-debugging-port=<free> --user-data-dir=<temp> ...` | API/E2E-owned process group, profile, and port only | Poll `http://127.0.0.1:<port>/json/version` | Terminate owned process group; wait/kill only if needed; remove profile |
| Deterministic web fixture | Temporary API/E2E workspace | Python loopback `ThreadingHTTPServer`/fixture | Serves action page, unique attach pages, and delayed route; no internet/account | HTTP GET to fixture root | Server shutdown and temporary directory removal |
| Skill CLI | Arbitrary unrelated caller CWD | `bash "$SKILL_DIR/scripts/autobyteus-browser" <command>` with unique Chrome port/workspace | One process per command, frozen uv, exact stdout/exit capture | Parse one JSON stdout value | Process exits per command; close only test-owned tabs |
| MCP stdio | Browser project / client harness | Production `scripts/autobyteus-browser-mcp` through MCP `stdio_client` | Unique MCP log dir; same isolated Chrome/workspace | MCP initialize + `list_tools` | Close client/stdio process; verify exit and logs |
| MCP HTTP | Browser project / client harness | Production MCP launcher with `streamable-http`, free port, default or explicit host | Short-lived loopback server; optional brief explicit `0.0.0.0` warning probe | Poll TCP then MCP initialize over `/mcp` | Terminate only owned server; wait; inspect log |
| Linux Bash probe | Repository mount in local Docker `ubuntu:24.04` | `docker run --rm ... bash <copied launcher>` with fake/no uv cases | No browser, network, or repository writes; validates Bash/readiness contract | Container exit/stdout/stderr | `--rm`; no persistent container |
| Fresh agent | Unrelated CWD / captured transcript | New ephemeral `codex exec` process constrained to the loaded `SKILL.md` and CLI help | Uses same isolated Chrome/local page; no source/tests/README context | Agent completes required journeys and emits final transcript | Verify user tab remains; close only agent-opened tabs; process exits |

| Data / Fixture / Identity Need | Existing Project Mechanism Or Creation Method | Environment / Data-Safety Notes | Cleanup / Retention |
| --- | --- | --- | --- |
| Chrome profile/site data | Unique temporary `--user-data-dir` | Never touches the user's profile/session | Remove after owned Chrome exits |
| Unrelated/user-owned tab | Seed one local fixture tab before health/agent execution | Distinct URL/title token; must remain open throughout task-owned close operations | Close during final fixture teardown only |
| Duplicate attach tabs | Seed two fixture URLs/titles sharing a unique matcher | No external side effects | Close during test/fixture teardown |
| Artifacts | Unique temporary caller workspace | Workspace-relative output only; assert magic bytes/JSON/text and collision semantics | Remove after evidence copied into report/log package as needed |
| MCP process state | Unique ports/log dirs | No shared bind or log path | Stop owned process; remove temp logs after retaining evidence summaries |

## Persisted Data Transition Coverage Basis

- Approved decision: `Not Affected`
- Design-spec and implementation-handoff references: `design-spec.md` -> `Persisted Data / State Transition Decision`; `implementation-handoff.md` -> `Persisted Data Transition Check`.
- Representative existing-data setup and required behavior: A seeded page in an isolated Chrome profile remains available across independent Playwright/CLI connections; no profile transformation or alias migration occurs.
- Evidence planned for the approved direct-use outcome: The same browser-owned target is listed and operated on from later processes; attached/unrelated pages survive CLI cleanup; Chrome remains reachable after connection teardown and task-owned tab close.
- Migration-specific completion/recovery scenarios: `N/A`
- Upstream ambiguity or reroute required: `No`

## Existing Durable Coverage Inventory

| Path / Scenario | Current Assertion Or Intent | Related Requirement / Acceptance Criteria / Design | Validity Decision | Evidence | Action |
| --- | --- | --- | --- | --- | --- |
| `tests/unit/test_json_codec.py` | Strict finite JSON and UTF-8-sink-safe surrogate round trips | `REQ-004`, `AC-003`, `CR-001` | Still Valid | `CRR-003`; source inspection | Retain and rerun. |
| `tests/unit/test_policy.py` | URL/timeout policy, workspace containment, no-clobber publication, strict JSON artifacts | `REQ-008`, `AC-007`, `CR-002` | Still Valid | Source/assertion inspection | Retain and rerun. |
| `tests/unit/test_application.py` | Shared fake runtime workflow, attach ambiguity/stale, script JSON, screenshot publication | `REQ-001`, `REQ-005`–`REQ-008`, `AC-002`, `AC-003`, `AC-005`–`AC-007` | Still Valid | Uses current application boundary and opaque IDs | Retain as fast behavior coverage; do not treat mocks as browser proof. |
| `tests/unit/test_runtime.py` | Public CDP method usage and Playwright-only disconnect | `REQ-001`, `REQ-002`, `AC-001`, `AC-008` | Still Valid | Assertion matches approved runtime lifecycle | Retain; add real lifecycle replacement coverage. |
| `tests/unit/test_cli_and_mcp.py` | CLI envelopes/readiness, MCP config/default/warning, strict stdout | `REQ-003`, `REQ-004`, `REQ-010`, `REQ-011`; `AC-003`, `AC-004`, `AC-012` | Still Valid | Current adapters and config | Retain; add black-box launcher/live transport coverage. |
| `tests/unit/test_mcp_adapter.py` | In-memory nine-tool MCP inventory/delegation | `REQ-001`, `REQ-006`, `REQ-011`; `AC-002`, `AC-006`, `AC-012` | Still Valid | Exercises real MCP protocol in memory over fake application | Retain; add live process transports and real browser effects. |
| Deleted `browser-mcp/tests/test_integration_real.py` real scenarios | Long-lived MCP + numeric registry + unrestricted absolute paths; also real navigate/read/snapshot/script/screenshot workflows | Old behavior plus current `AC-005`, `AC-006`, `AC-009` intent | Replace | Numeric IDs, `attach_state`/`attached_by`, absolute outputs, and one-process manager are obsolete, but the real browser operations remain required | Keep deletion; replace with current opt-in integration coverage using isolated Chrome, launcher processes, workspace artifacts, and opaque IDs. |
| Deleted `browser-mcp/tests/test_server.py` fake server scenarios | Old MCP tool bodies/process registry | Superseded by `REQ-001`, `AC-002`, `AC-006` | Replace | Current unit files already cover application/policy/runtime/CLI/MCP separation | Existing current unit suite is the replacement; no restoration. |
| `SKILL.md` quick validation performed only in handoff/review | Frontmatter/skill structure | `REQ-009`, `AC-010` | Needs Update | No repository-resident command test asserts current skill through the declared validator | Run authoritative validator each execution; black-box forward validation is added separately. |
| `tests/integration/` added at `API-REV-001`, corrected at `API-REV-002` | Real CLI/Chrome, launcher, MCP transport, fixture, and selection coverage | `REQ-012`, `AC-001`, `AC-004`, `AC-005`, `AC-008`, `AC-009`, `AC-012` | Still Valid after Update | `CRR-004` findings `TR-001`–`TR-003` are locally resolved; focused/default/integration/full executions pass | Retain the corrected suite; send the three updated test files for proportional re-review. |

## Stale Or Obsolete Coverage Decisions

| Path / Scenario | Obsolete Assertion | Why It Is Obsolete | Upstream Evidence | Replacement Coverage | No-Replacement Rationale |
| --- | --- | --- | --- | --- | --- |
| Deleted `browser-mcp/tests/test_integration_real.py` | Short numeric IDs, tracked-only list, `attach_state`/`attached_by`, one long-lived manager, absolute screenshot path | Approved browser-owned ID, all first-context pages, tight metadata, independent processes, and workspace policy intentionally replace them | `REQ-002`, `REQ-005`, `REQ-008`, Legacy Removal Policy; `AC-001`, `AC-005`, `AC-007` | `AE2E-CLI-001`–`AE2E-CLI-006` in new real-Chrome integration suite | N/A |
| Deleted `browser-mcp/tests/test_server.py` | Old MCP-owned tool logic and `close_browser` behavior | MCP is now thin and global close is prohibited | `REQ-001`, `REQ-008`, `REQ-011`; `AC-002`, `AC-008`, `AC-012` | Current unit application/MCP suites plus `AE2E-MCP-001`/`002` | N/A |

## Durable Coverage To Add

| Scenario ID | Behavior / Boundary | Requirement / Acceptance Criteria / Design Evidence | Planned Artifact / Path | Why Durable Coverage Is Needed |
| --- | --- | --- | --- | --- |
| `AE2E-CLI-001` | Clean isolated Chrome; health creates no page; process A open and process B list/navigate/read by same ID | `REQ-002`, `REQ-007`, `REQ-012`; `AC-001`, `AC-004`, `AC-008` | `tests/integration/test_cli_real_chrome.py` | Core product claim and prior mock gap. |
| `AE2E-CLI-002` | Real read modes, DOM selectors, script arg/result/action verification, screenshot PNG/JPEG/artifact metadata | `REQ-006`, `REQ-008`, `REQ-012`; `AC-006`, `AC-007`, `AC-009` | `tests/integration/test_cli_real_chrome.py` | Replaces meaningful parts of deleted real-browser coverage through current public CLI. |
| `AE2E-CLI-003` | Unique attach, duplicate ambiguity, external close stale error, unrelated tab survival | `REQ-005`, `REQ-008`; `AC-005`, `AC-008` | `tests/integration/test_cli_real_chrome.py` | Real ownership/discovery/lifecycle semantics are not proven by fakes. |
| `AE2E-CLI-004` | Failed/slow open navigation rolls back only the new page and leaves Chrome/user page alive | `REQ-005`, `REQ-008`, `REQ-012`; `AC-008`, `AC-009` | `tests/integration/test_cli_real_chrome.py` | Lifecycle and recovery effect needs direct proof. |
| `AE2E-LAUNCH-001` | Relocated no-`.venv` first invocation from unrelated CWD, help, ready error, pre-ready failure, missing bundle, temp cleanup | `REQ-010`; `AC-003`, `AC-004`, `DS-006` | `tests/integration/test_launcher_black_box.py` | Launcher contract is public and shell behavior should not remain an ad hoc probe. |
| `AE2E-MCP-001` | Production stdio launcher, nine live tools, real shared-core operation/error | `REQ-011`, `REQ-012`; `AC-006`, `AC-012` | `tests/integration/test_mcp_transports_real.py` | In-memory transport does not prove the executable wrapper or stdout isolation. |
| `AE2E-MCP-002` | Live streamable HTTP initialization/tool operation, loopback default, explicit non-loopback warning, invalid config | `REQ-011`; `AC-012`, `DS-008` | `tests/integration/test_mcp_transports_real.py` | Actual process/bind/log behavior is material. |
| `AE2E-SUPPORT-001` | Deterministic local site and isolated Chrome lifecycle | `REQ-012`; `AC-001`, `AC-005`, `AC-008`, `AC-009` | `tests/integration/conftest.py`, `tests/integration/support.py` | Makes the durable integration coverage isolated, reproducible, and cleanup-owned. |

## Durable Coverage Updated In Round 2

| Scenario ID | Existing Path / Scenario | Required Update | Requirement / Acceptance Criteria / Design Evidence | Notes |
| --- | --- | --- | --- | --- |
| `AE2E-CLI-002` / `TR-001` | `tests/integration/test_cli_real_chrome.py::test_real_content_dom_script_screenshot_and_workspace_artifacts` | Added production-launcher `--format jpeg` proof using a `.jpeg` workspace artifact; asserts a successful envelope, `image/jpeg`, truthful byte metadata, JPEG signature/trailer, and a rejected format/extension mismatch with no artifact publication. | `REQ-006`, `REQ-008`, `REQ-012`; `AC-006`, `AC-007`, `AC-009`; reviewed design screenshot invariant | Closes the gap between the investigation's promised PNG/JPEG coverage and durable assertions without changing product code. |
| `AE2E-CONFIG-001` / `TR-002` | `tests/integration/test_launcher_black_box.py`, `tests/integration/test_mcp_transports_real.py` | Kept `integration` at file scope; applies `real_chrome` only to the relocated clean-bundle test and two live MCP transport tests. Removed `live_chrome` from invalid pre-start MCP configuration validation. | `REQ-010`, `REQ-011`, `REQ-012`; `AC-003`, `AC-004`, `AC-012` | Default pytest executes the three external-Chrome-free integration scenarios and skips only seven scenarios that actually require a local browser. |
| `AE2E-LAUNCH-001` / `TR-003` | `tests/integration/test_launcher_black_box.py::test_launcher_readiness_branches_and_missing_bundle_are_exactly_once` | Creates a `tmp_path`-owned `TMPDIR`, passes it to every launcher branch, and asserts only that owned namespace is empty after each branch. | `REQ-010`; `AC-003`, `AC-004`; `DS-006` | Removes dependence on unrelated or concurrent process-global temp files while retaining exact launcher cleanup proof. |
| `AE2E-CONFIG-001` | `autobyteus-browser/pyproject.toml` pytest config | Retain registered `integration` and accurately defined `real_chrome` markers | Reviewed design `tests/integration`; `REQ-012` | Marker definitions remain valid; test-level usage is corrected under `TR-002`. |

## Durable Coverage To Remove

None in round 2. The obsolete old suites were removed by implementation, their approved replacements were added at `API-REV-001`, and no legacy assertion or path was revived.

## Repository Coverage Execution Plan And Results

Round 2 first ran the four directly affected checks (one `TR-001` browser scenario plus the three Chrome-free `TR-002`/`TR-003` cases), then the default suite without real-Chrome opt-in, the complete integration suite with opt-in, and the full real-enabled project suite. Marker collection proves seven `real_chrome` scenarios and three Chrome-free integration scenarios. Default execution is now `67 passed, 7 skipped`; real-enabled totals remain `74 passed`. Git/diff inspection confirms that the rework changes only three durable integration test files and reports/evidence, so successful Linux launcher and fresh-agent evidence from `API-REV-001` remains directly applicable and was not rerun.

| Order | Command | Working Directory / Configuration | Boundary Or Scenario Proven | Result | Evidence / Output Path |
| --- | --- | --- | --- | --- | --- |
| 1 | `AUTOBYTEUS_BROWSER_REAL_TESTS=1 ... pytest -q -vv <four affected node IDs>` | `autobyteus-browser/`; isolated Chrome/profile/workspace and test-owned launcher `TMPDIR` | Direct `TR-001`–`TR-003` resolutions | Pass — `4 passed in 12.67s` | `evidence/affected-rework-pytest.log` |
| 2 | `uv run --frozen --extra test python -m pytest -o addopts= -q --junitxml=...` | No real-Chrome opt-in | Unit/adapter plus three Chrome-free integrations | Pass — `67 passed, 7 skipped in 2.93s` | `evidence/default-pytest.log`, `default-pytest-junit.xml` |
| 3 | `AUTOBYTEUS_BROWSER_REAL_TESTS=1 ... pytest -o addopts= tests/integration -q -vv --junitxml=...` | Owned Chrome/profile/ports/workspaces | Corrected complete integration suite | Pass — `10 passed in 36.94s` | `evidence/integration-pytest.log`, `integration-junit.xml` |
| 4 | `AUTOBYTEUS_BROWSER_REAL_TESTS=1 ... pytest -o addopts= -q --junitxml=...` | Same | Complete project with real coverage enabled | Pass — `74 passed`, zero failures/errors/skips, `36.73s` | `evidence/full-pytest.log`, `full-pytest-junit.xml` |
| 5 | Lock/compile/unit/default/marker collection/Bash/ShellCheck/skill/package/search/diff checks | Worktree/project | Frozen package, exact 7/3 marker selection, packaging/skill/shell/removal/whitespace integrity | Pass | `evidence/static-and-package-checks.log`; final Git checks recorded in execution report |

## Post-Repository Confidence Scorecard

Round-2 repository execution passed the complete real-enabled suite: `74 passed` (`64` unit/adapter plus `10` integration), zero failures/errors/skips in `36.73s`. The default invocation now executes the 64 unit/adapter tests plus three Chrome-free process integrations and skips only seven actual real-Chrome scenarios (`67 passed, 7 skipped`). Direct evidence now includes isolated Chrome 151, independent production launcher processes, PNG/JPEG bytes and metadata, format/extension rejection, isolated launcher temp cleanup, stale/ambiguous/timeout lifecycle, relocated first-run bootstrap, live MCP stdio/HTTP, and Chrome-free invalid config/connectivity cases. The already-successful fresh-agent and Linux Bash evidence from `API-REV-001` remains applicable because no product/runtime source changed in round 2.

| Confidence Category | Score | What Supports The Score | Remaining Uncertainty | Additional Validation That Could Improve It |
| --- | --- | --- | --- | --- |
| Requirement and acceptance-criteria proof | 98% | All `AC-001`–`AC-012` retain direct material evidence; durable CLI coverage now includes the promised PNG/JPEG branches and format/extension invariant. | None critical; additional versions are breadth only. | Future version/platform breadth only. |
| Changed-boundary execution directness | 98% | Production CLI/MCP/launcher and real Chrome were rerun; prior fresh-agent execution remains direct and applicable. | Only one locally available browser-engine/platform combination is direct. | Future multi-browser-version CI. |
| Cross-boundary integration realism and mock gap | 97% | Real Chrome/CDP, frozen uv, stdio JSON-RPC, streamable HTTP, browser effects, files, PNG/JPEG bytes, and local HTTP cross actual boundaries. | No external account/site is used, intentionally avoiding nondeterminism and credentials. | External-site breadth is not required for the approved contracts. |
| Environment, configuration, identity, and fixture fidelity | 97% | Temporary Chrome profile/port/workspace, relocated bundle, real MCP bind/logs, deterministic non-CDP endpoint, and owned launcher `TMPDIR` are used. | Linux Chrome itself was not available locally. | Future Linux browser-engine execution. |
| Failure, edge-case, lifecycle, and recovery evidence | 97% | Invalid/connectivity/stale/ambiguous/path/collision/mismatch/timeout cases, per-branch temp cleanup, rollback, user-tab survival, and prior fresh-agent recovery pass. | Deliberate same-tab multi-agent races are outside the sequencing contract. | None required in current scope. |
| User-surface, browser, and desktop-shell confidence | 98% | Real browser journeys and the prior independent fresh agent passed; no user-facing product source changed in round 2 and no desktop app applies. | Other agent vendors are not independently executed. | Vendor breadth only. |
| Durable regression coverage quality and relevance | 97% | Ten scenarios now use truthful selection (seven Chrome-required, three default), isolated temp ownership, and complete PNG/JPEG assertions. | Browser executable availability remains a prerequisite for seven opt-in scenarios. | Passing proportional re-review is the workflow gate, not an execution gap. |

- Overall post-repository confidence: `97%` (97.4%, rounded)
- Calculation method: Simple average of the seven applicable categories.
- Every critical acceptance criterion directly proven: `Yes`
- Any applicable category below `90%`: `No`
- Default clean-confidence target of `95%` met: `Yes`
- Material residual risks: Additional Chrome/Chromium versions, Linux Chrome engine, other agent vendors, and intentionally concurrent same-tab callers.

## Broader Validation Decision

- Decision: `Not Required` for an additional round-2 broader run; the required browser/transport/Linux/fresh-agent validation completed successfully at `API-REV-001`.
- Selected execution mode: Repository-resident real Chrome CLI/MCP/lifecycle reruns only, because those durable assertions changed.
- Specific confidence gap or residual risk addressed: `TR-001`–`TR-003` concerned durable branch completeness, test selection, and resource isolation, not a new product/user/platform boundary.
- Why the selected mode can materially improve confidence: Affected/default/real-enabled pytest executions directly verify each corrected assertion and selection behavior. Re-running unchanged fresh-agent and Linux probes would add time but no material evidence for test-only changes.
- Expected confidence after the selected validation: `97%` overall with no category below `90%`, retaining the direct prior broader evidence.
- Browser-specific decision and rationale: Real browser execution remains mandatory for the seven marked scenarios and was rerun; Chrome-free scenarios now execute without the opt-in. Generic web browsing remains irrelevant.
- If `Not Required`: Successful `API-REV-001` Linux Bash and fresh-agent evidence is carried forward explicitly; Git/diff inspection confirms no product/runtime source delta in round 2.
- If `Blocked`: `N/A`
- Execution status after decision: Completed. Four affected tests, `67 passed / 7 skipped` default execution, 10/10 integration scenarios, and 74/74 real-enabled project tests pass. The retained Linux and fresh-agent evidence remains successful and applicable.

## Desktop Application Validation Decision

- Desktop framework / shell: `N/A`
- Relevant README or development instructions: No desktop app exists.
- Web-equivalent behavior: Browser automation itself is tested directly in Chrome.
- Shell-specific or lifecycle behavior: Bash launchers are tested as process/lifecycle surfaces, not as a desktop shell.
- Chosen validation approach and why it fits the project: CLI/live MCP/Chrome per the project architecture.
- Effect on any already-running desktop application: `None`; only an API/E2E-owned headless Chrome process and profile are used.
- Behavior not directly proven and confidence consequence: Native Windows shell is intentionally out of scope; Linux browser engine coverage may remain a bounded platform residual if only the Bash launcher can be exercised in Docker.

## Live Environment And Fixture Plan

- Startup order and commands: Allocate loopback ports and temp root; start deterministic HTTP server; launch isolated Chrome with temp profile; verify CDP; seed user/duplicate tabs where needed; execute CLI; execute stdio MCP; execute HTTP MCP; execute fresh-agent scenario; tear down in reverse order.
- Environment choices that materially affect the run: `CHROME_REMOTE_DEBUGGING_PORT=<owned>`, `CHROME_USER_DATA_DIR=<owned absolute temp profile>`, `AUTOBYTEUS_AGENT_WORKSPACE=<owned temp workspace>`, `BROWSER_MCP_LOG_DIR=<owned temp logs>`. Chrome is headless on macOS ARM64; locale/timezone are not behavior inputs.
- Health / readiness checks: `/json/version`, CLI `health-check`, MCP initialization/tool list, TCP readiness for HTTP.
- Seed data / fixtures: Local page with heading, button/input and DOM action; delayed route; one unique user-owned tab; two duplicate-matcher tabs.
- Test identities, authentication, permissions, or session state: No external identity/account. The seeded user-owned tab stands in for an attached/authenticated existing page ownership boundary without credentials.
- Requirement-linked journeys or scenarios: `AE2E-CLI-001`–`004`, `AE2E-LAUNCH-001`, `AE2E-MCP-001`/`002`, plus fresh-agent journeys `AE2E-AGENT-001`–`003` and Linux shell `AE2E-PLATFORM-001`.
- Evidence to capture: Exact commands/status, JSON stdout/stderr byte counts, target/page counts, artifact paths/magic bytes, MCP structured results, bind/log warning, fresh-agent transcript, process cleanup checks.
- Owned processes and temporary state to clean up: HTTP server thread/process, Chrome process group/profile, MCP processes/ports/logs, relocated bundle/`.venv`, caller artifacts, Docker container, fresh-agent process/transcript.

## Temporary Executable Validation Plan

| Scenario ID | Probe / Harness / Runtime Setup | Behavior Proven | Why This Should Not Remain As Durable Coverage |
| --- | --- | --- | --- |
| `AE2E-PLATFORM-001` | Local `ubuntu:24.04` Docker container with mounted/copied production launcher and deterministic fake/no-uv executables | Linux Bash 5 readiness branch, missing uv/files, ready success/error, stdout/stderr/exit and temp cleanup | Host/container availability is not a normal project test dependency; durable launcher tests cover the invariant, while this records one representative Linux execution. |
| `AE2E-AGENT-001` | Fresh ephemeral agent process given only loaded `SKILL.md`, CLI help, local task URL, and inherited isolated Chrome env | Open -> navigate -> read -> close with explicit ID and JSON parsing | Agent-platform execution is expensive/environment-dependent and should remain forward validation evidence, not an always-on repository test. |
| `AE2E-AGENT-002` | Same fresh agent with a pre-seeded user-owned tab | Attach -> inspect without closing user tab | Same reason; product code coverage is durable separately. |
| `AE2E-AGENT-003` | Same fresh agent and deterministic action page | DOM snapshot -> script action -> verification; deliberately parse one structured stale/invalid error | Same reason; validates skill procedural sufficiency, not a deterministic unit boundary. |

## Not Tested / Infeasible / Deferred

| Behavior / Boundary | Reason | Risk | Required Follow-Up Or Escalation |
| --- | --- | --- | --- |
| Native Windows shell/browser | Explicitly out of first-release scope | None for approved first release | Future platform expansion only |
| Additional Chrome/Chromium versions and Linux graphical Chromium | Only Chrome 151/macOS is locally available; Docker probe targets Bash, not browser engine | CDP experimental method could regress elsewhere | Record bounded residual; add CI/platform matrix when available |
| Malicious remote client/auth | Auth is explicitly out of scope; non-loopback bind is operator-protected | Remote bind remains unauthenticated by design | Verify warning/default only; do not claim auth |
| Intentional same-tab races across independent agents | Requirements assign sequencing to skill and do not define a coordinator | External actions can race if callers violate procedure | Serialize all tested workflows; record residual |

## Ambiguities Or Reroute Triggers

None identified before execution. A live failure will be classified from direct evidence and sent to `code_reviewer` for focused failure-origin review after this investigation is updated.

### Execution-Time Coverage Decision Updates

- The first full CLI integration attempt exposed two coverage-local assertions, not product defects: Chrome's `/json/close/<id>` endpoint returns plain text (`Target is closing`) rather than JSON, and Chrome 151/Playwright returns U+FFFD when JavaScript produces a lone UTF-16 surrogate. The helper was corrected to treat the close response as plain text. The extra live-surrogate equality assertion was replaced by standards-valid non-ASCII structured serialization because approved `AC-003` requires sink-safe JSON and existing unit/subprocess coverage already proves lone-surrogate values that reach Python; the conversion does not promise overriding Chrome/Playwright's pre-application string normalization.
- Live FastMCP showed that union/root output schemas are advertised and returned under the protocol-valid `structuredContent.result` property, while single TypedDict results are direct objects. The MCP integration helper now follows each tool's advertised schema rather than assuming one unapproved uniform framework representation. Browser semantics and all nine tools remained correct.
- One initial integration skip hook accidentally marked unit items when collecting the full tree. It was corrected before `API-REV-001` to inspect the `real_chrome` marker. `CRR-004` then found that file-level use of that marker was too broad. Round 2 scopes it to the seven actual Chrome scenarios; marker collection lists exactly seven marked and three Chrome-free integration items. Evidence is now `67 passed, 7 skipped` by default and `74 passed` with real execution enabled.
- `TR-001` is resolved: the production launcher writes a `.jpeg` artifact with `image/jpeg`, truthful size, JPEG SOI/EOI bytes, and rejects a JPEG request targeting `.png` without publishing a file. PNG evidence remains intact.
- `TR-002` is resolved: readiness/missing-bundle, deterministic non-CDP connectivity failure, and invalid MCP host/port execute by default. The invalid config test no longer requests `live_chrome`; the connectivity case points to the owned HTTP fixture so it cannot auto-launch platform Chrome.
- `TR-003` is resolved: every fake-uv readiness/missing-bundle branch uses one created test-owned `TMPDIR` and verifies it is empty immediately after the branch. No global temp namespace is scanned.
- No requirement, design, implementation, fixture, or environment failure remains. No pre-handoff failure reroute is required.

## Investigation Decision

- Proceed To API/E2E Execution: `Yes`
- Repository-Resident Durable Coverage Will Be Added / Updated / Removed: `Yes` — round 2 updates three existing integration test files to resolve `TR-001`–`TR-003`; no product source or durable coverage path is added/removed.
- Post-repository confidence: `97%`; every critical acceptance criterion retains direct proof and no category is below 90%.
- Broader validation decision: `Not Required` for an additional round-2 run; required `API-REV-001` browser/platform/fresh-agent evidence remains applicable, while the changed real Chrome/MCP repository scenarios were rerun.
- Reroute Required Before Validation Execution: `No`
- Recommended Recipient If Reroute Required: `N/A`
- Notes: The initial artifact was created before any round-1 durable coverage edit. It was refreshed for `CRR-004` before round-2 corrections/final execution and is now current with the passing reruns. Final confidence and outcome are recorded separately in the execution coverage report and API/E2E revision record.
