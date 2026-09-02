# Implementation Revision Record

The current code and `implementation-handoff.md` are authoritative. This record preserves implementation-round traceability only.

## Revision Index

| Revision ID | Triggering Role / Report / Round | Finding IDs | Classification | Related Revision IDs | Result |
| --- | --- | --- | --- | --- | --- |
| `IR-001` | `architecture_reviewer` / `design-review-report.md` / initial implementation after `ARCH-REV-003` | `N/A` | `Initial Baseline` | `SR-001`–`SR-003`, `ARCH-REV-003`; `CRR-*`/`API-REV-*`/`DR-*`: `N/A` | Approved design implemented; implementation-scoped checks pass; ready for code review |
| `IR-002` | `code_reviewer` / `code-review-report.md` / source review round 1 | `CR-001`, `CR-002` | `Local Fix` | `SR-001`–`SR-003`, `ARCH-REV-003`, `CRR-001`; `API-REV-*`/`DR-*`: `N/A` | Strict finite JSON and atomic no-clobber artifact contracts implemented; ready for source re-review |
| `IR-003` | `code_reviewer` / `code-review-report.md` / source re-review round 2 | `CR-001` | `Local Fix` | `SR-001`–`SR-003`, `ARCH-REV-003`, `CRR-001`, `CRR-002`; `API-REV-*`/`DR-*`: `N/A` | Strict JSON serialization made UTF-8-sink-safe; ready for source re-review |
| `IR-004` | `architecture_reviewer` / `design-review-report.md` / SR-004 re-entry after `ARCH-REV-005` | `N/A` (`DR-005` resolved upstream) | `Approved Re-entry Delta` | `SR-004`, `SR-005`; `ARCH-REV-004`, `ARCH-REV-005`; prior `CRR-003`, `CRR-005`, `API-REV-002`, delivery `DR-001` | Runtime-advertised skill-locator contract implemented; ready for source review |
| `IR-005` | `architecture_reviewer` / `design-review-report.md` / SR-006 re-entry after `ARCH-REV-006` | `N/A` | `Approved Re-entry Delta` | `SR-006`, `ARCH-REV-006`; prior `CRR-006`, `CRR-007`, `API-REV-003`, `DR-002` | Generic browser-automation identity/package rename implemented; ready for source review |
| `IR-006` | `architecture_reviewer` / `design-review-report.md` / cumulative SR-009 re-entry after `ARCH-REV-008` | `DR-006` / `PREM-004` (resolved upstream) | `Approved Re-entry Delta` | `SR-007`–`SR-009`, `ARCH-REV-007`, `ARCH-REV-008`; prior `CRR-008`, `API-REV-003`, `DR-002` | Direct argument procedure and owned atomic browser runtime implemented; ready for source review |

## Revision Entries

### IR-001 — Portable browser CLI and skill-bundle implementation baseline

- Triggering role, report path, and round: `architecture_reviewer`; `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/design-review-report.md`; initial implementation after the passing round recorded by `ARCH-REV-003`.
- Triggering finding IDs: `N/A` — upstream `DR-001`–`DR-004` were already resolved before implementation.
- Classification: `Initial Baseline`
- Prior authoritative result: `N/A`
- Current authoritative result: The reviewed portable `autobyteus-browser/` skill bundle, task CLI, shared browser core, safety policy, launchers, and retained thin MCP adapter are implemented. Implementation-scoped unit, package, skill, shell, bootstrap-contract, and removal checks pass. Independent real-Chrome/API/E2E coverage remains downstream-owned.
- Related solution revision IDs: `SR-001`, `SR-002`, `SR-003`
- Related architecture-review revision IDs: `ARCH-REV-003`
- Related code-review revision IDs: `N/A`
- Related API/E2E revision IDs: `N/A`
- Related delivery revision IDs: `N/A`
- Why this baseline or implementation revision is recorded: Establish the first authoritative implementation handoff after the complete reviewed solution package passed architecture review.
- Approved behavior or requirement IDs affected: `BEH-001`–`BEH-008`; `REQ-001`–`REQ-012`; implementation covers the production code and packaging portions of `AC-001`–`AC-012`, with independent executable evidence still required downstream.
- Implementation delta: Cleanly renamed the project/package, replaced process-local numeric tab tracking with public CDP target discovery, centralized browser operations in `BrowserApplication`/`BrowserRuntime`, added strict URL/input/artifact policy and stable errors, added the versioned JSON CLI and readiness-gated frozen-uv launcher, added the vendor-neutral skill, refactored MCP to thin tools with validated loopback-default configuration, renamed the MCP launcher, updated docs/lock metadata, removed global-close and legacy paths, and replaced obsolete numeric-ID unit coverage with implementation-focused shared-core/adapter checks.
- Changed files or areas: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/autobyteus-browser/`, `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/README.md`, and this task workspace's implementation artifacts.
- Local validation and result: `uv lock --check`, Python compile, `11` unit/adapter tests, skill quick validation, Bash syntax, ShellCheck, package build, unrelated-CWD relocation/help, launcher ready/no-ready/bootstrap cases, MCP-wrapper stdout isolation, source-size/whitespace inspection, and obsolete-path removal checks all passed.
- Next recipient or routing: `code_reviewer`
- Remaining limitations or risks: Real isolated Chrome cross-process continuity and browser effects, `brui_core` auto-launch behavior, platform-specific CDP compatibility, live stdio/HTTP MCP behavior, same-tab independent-client races, and fresh-agent forward workflows require downstream investigation/execution. No API/E2E sign-off is claimed.

### IR-002 — Strict JSON and atomic artifact publication local fix

- Triggering role, report path, and round: `code_reviewer`; `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/code-review-report.md`; implementation source review round `1` / `CRR-001`.
- Triggering finding IDs: `CR-001`, `CR-002`
- Classification: `Local Fix`
- Prior authoritative result: `IR-001` implementation received `Fail / Local Fix` at `CRR-001` because reachable non-finite values could escape the schema-v1 JSON boundary and `overwrite=False` could lose a concurrent artifact race.
- Current authoritative result: Strict finite JSON is enforced at CLI input, application argument/result, JSON artifact, MCP detail, and final CLI envelope boundaries. No-overwrite publication uses an atomic same-filesystem no-clobber link, while explicit overwrite alone uses replacement. Focused scalar/nested/overflow and deterministic interleaving coverage passes; the current implementation is ready for source re-review.
- Related solution revision IDs: `SR-001`, `SR-002`, `SR-003`
- Related architecture-review revision IDs: `ARCH-REV-003`
- Related code-review revision IDs: `CRR-001`
- Related API/E2E revision IDs: `N/A`
- Related delivery revision IDs: `N/A`
- Why this baseline or implementation revision is recorded: Resolve the two bounded implementation-source findings without changing the approved architecture, behavior, command surface, or stable error categories.
- Approved behavior or requirement IDs affected: `BEH-004`, `BEH-006`; `REQ-004`, `REQ-006`, `REQ-008`; `AC-003`, `AC-007`.
- Implementation delta: Added `json_codec.py` as the shared strict RFC-JSON owner; rejected named and exponent-overflow non-finite arguments as `INVALID_ARGUMENT`; rejected scalar/nested non-finite script arguments/results before browser/output effects; made artifact and final envelope encoding strict with pre-write fallback; centralized temporary publication in `ArtifactPolicy.commit_temporary`; used atomic `os.link` for no-overwrite and `os.replace` only for explicit overwrite; routed screenshots through the same commit owner; preserved the winning file and cleaned temporary siblings on collisions/failures.
- Changed files or areas: `src/autobyteus_browser/json_codec.py`, `cli.py`, `application.py`, `policy.py`, `mcp/tools/__init__.py`, and focused unit tests in `tests/unit/test_json_codec.py`, `test_policy.py`, `test_application.py`, and `test_cli_and_mcp.py`.
- Local validation and result: `48` unit/adapter tests passed, including scalar/nested `NaN`/`Infinity`/`-Infinity`, exponent overflow, strict final-envelope fallback, generic bytes/text/JSON commit interleavings, screenshot interleaving, explicit overwrite, winning-file preservation, and temporary cleanup. The unrelated-CWD bundled launcher also emitted one strict `INVALID_ARGUMENT` envelope/exit `2` for nested `NaN`. Lock, compile, skill, Bash, ShellCheck, package-build, whitespace, and owner scans passed.
- Next recipient or routing: `code_reviewer`
- Remaining limitations or risks: The original downstream real-Chrome/CDP, live MCP, cross-process lifecycle, supported-shell breadth, same-tab race, and fresh-agent forward risks remain. No API/E2E investigation or execution occurred during this local fix.

### IR-003 — UTF-8-sink-safe strict JSON completion

- Triggering role, report path, and round: `code_reviewer`; `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/code-review-report.md`; implementation source re-review round `2` / `CRR-002`.
- Triggering finding IDs: `CR-001`
- Classification: `Local Fix`
- Prior authoritative result: `IR-002` received `Fail / Local Fix` at `CRR-002`. `CR-002` was verified resolved; `CR-001` remained open because a JavaScript lone-surrogate result passed the codec but failed at a real UTF-8 stdout or artifact sink.
- Current authoritative result: Strict JSON serialization now escapes all non-ASCII code points before publication, so lone high/low surrogates have a sink-safe representation while finite-value enforcement and one-envelope ownership remain unchanged. Focused real-subprocess stdout and artifact-byte coverage passes; the implementation is ready for source re-review.
- Related solution revision IDs: `SR-001`, `SR-002`, `SR-003`
- Related architecture-review revision IDs: `ARCH-REV-003`
- Related code-review revision IDs: `CRR-001`, `CRR-002`
- Related API/E2E revision IDs: `N/A`
- Related delivery revision IDs: `N/A`
- Why this implementation revision is recorded: Complete the remaining representation half of `CR-001` at the existing shared codec owner without changing the approved behavior, command surface, or output/error categories.
- Approved behavior or requirement IDs affected: `BEH-004`, `BEH-006`; `REQ-004`, `REQ-006`; `AC-003`.
- Implementation delta: Changed `dumps_strict` to use ASCII escaping, guaranteeing that the complete serialized value is encodable by strict UTF-8 stdout and artifact sinks before publication. Added top-level/nested lone high/low surrogate coverage at codec, `BrowserApplication` inline/artifact, direct artifact-byte, and real CLI subprocess stdout boundaries.
- Changed files or areas: `src/autobyteus_browser/json_codec.py` plus focused coverage in `tests/unit/test_json_codec.py`, `test_application.py`, `test_policy.py`, and `test_cli_and_mcp.py`; current implementation artifacts were refreshed.
- Local validation and result: `64` unit/adapter tests passed. Four real subprocess cases returned exactly one strict schema-v1 envelope with exit `0` for top-level/nested lone high/low surrogate results; four artifact cases produced strict UTF-8-decodable bytes with equivalent decoded values. Lock, compile, skill, Bash, ShellCheck, package-build, whitespace, strict-owner, and removal scans passed.
- Next recipient or routing: `code_reviewer`
- Remaining limitations or risks: The original downstream real-Chrome/CDP, live MCP, cross-process lifecycle, supported-shell breadth, same-tab race, and fresh-agent forward risks remain. No API/E2E investigation or execution occurred during this local fix.

### IR-004 — Runtime-advertised skill-locator re-entry

- Triggering role, report path, and round: `architecture_reviewer`; `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/design-review-report.md`; SR-004/SR-005 re-entry round `5` / `ARCH-REV-005`.
- Triggering finding IDs: `N/A` — the user-triggered SR-004 contract correction has no code-review finding ID, and architecture finding `DR-005` was resolved by `SR-005` before implementation re-entry.
- Classification: `Approved Re-entry Delta`
- Prior authoritative result: The candidate at checkpoint `5d5ba7e018ff3c429f28e6d175b37c5cb340277c` had passed implementation source review (`CRR-003`), API/E2E (`API-REV-002`), durable-test re-review (`CRR-005`), and delivery preparation (`DR-001`), but its public skill instructions still assumed required agent-visible shell variables and an absolute-directory placeholder. SR-004 made that instruction shape obsolete and placed finalization on hold.
- Current authoritative result: `SKILL.md` now names only `scripts/autobyteus-browser`, requires resolution from the directory containing the exact runtime-advertised/read `SKILL.md`, keeps the task workspace as shell CWD, and rejects variable, vendor-home, PATH-registration, bundle-CWD, and scanning/guessing prerequisites. The project README is aligned while retaining delivery-owned runtime/support and default/real-Chrome test guidance. The bounded source/prose delta is ready for code review.
- Related solution revision IDs: `SR-004`, `SR-005` (with `SR-001`–`SR-003` preserved)
- Related architecture-review revision IDs: `ARCH-REV-004`, `ARCH-REV-005` (prior passing baseline `ARCH-REV-003` preserved)
- Related code-review revision IDs: Prior `CRR-003`, `CRR-005`; re-entry review `N/A`
- Related API/E2E revision IDs: Prior `API-REV-002`; re-entry revision `N/A`
- Related delivery revision IDs: Prior `DR-001`; re-entry revision `N/A`
- Why this implementation revision is recorded: Implement only the approved SR-004 existing-candidate delta without reopening the validated launcher internals, `BrowserApplication`/`BrowserRuntime`, CDP identity, CLI JSON/bootstrap, artifact policy, or retained MCP behavior.
- Approved behavior or requirement IDs affected: `BEH-005`, `BEH-008`; `REQ-009`, `REQ-010`, `REQ-012`; `AC-004`, `AC-010`, `AC-011`.
- Implementation delta: Replaced the public `SKILL_DIR`/`BROWSER_CLI` example and absolute-directory placeholder with an exact runtime-advertised/read file-locator procedure and semantic resolved-launcher invocations. Updated the README's agent workflow and development commands to preserve the task CWD and use `uv --directory` for human development checks. No launcher, Python source, package, MCP, or durable coverage file changed.
- Changed files or areas: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/autobyteus-browser/SKILL.md`, `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/autobyteus-browser/README.md`, and current implementation handoff/revision artifacts.
- Local validation and result: Authoritative skill `quick_validate.py` passed; a focused ephemeral SR-004 contract assertion confirmed the relative launcher reference, exact-locator/directory/task-CWD instructions, preserved README support/test sections, and absence of required variables, vendor projection paths, embedded absolute placeholders, shell assignments, scan commands, or bundle `cd`; `uv lock --check`, compileall, all `64` unit tests, unrelated-CWD launcher help, and `git diff --check` passed.
- Next recipient or routing: `code_reviewer`
- Remaining limitations or risks: Repository-resident durable skill-contract coverage remains downstream-owned and must be preceded by the refreshed API/E2E coverage investigation. That stage should add a focused Chrome-free contract assertion and rerun fresh-agent proof against the corrected instruction shape. Any durable coverage edit must return through proportional code review before delivery refresh. The prior fresh-agent transcript cannot prove IR-004 by itself.

### IR-005 — Generic browser-automation identity and package re-entry

- Triggering role, report path, and round: `architecture_reviewer`; `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/design-review-report.md`; SR-006 capability-vocabulary re-entry round `6` / `ARCH-REV-006`.
- Triggering finding IDs: `N/A` — `ARCH-REV-006` passed with no new or remaining finding; `DR-001`–`DR-005` remain resolved.
- Classification: `Approved Re-entry Delta`
- Prior authoritative result: The checkpointed candidate through `IR-004`, `CRR-006`, `API-REV-003`, `CRR-007`, and delivery `DR-002` was verification-ready under a branded active capability contract. SR-006 superseded that vocabulary while preserving the validated browser, locator, bootstrap, JSON, safety, and transport semantics.
- Current authoritative result: The complete active bundle is atomically renamed to `browser-automation` with display **Browser Automation**, token `$browser-automation`, agent launcher `scripts/browser`, CLI `browser`, MCP wrapper `scripts/browser-mcp`, retained console `browser-mcp-server`, distribution/namespace `browser-automation`/`browser_automation`, generic `BROWSER_AUTOMATION_*` identifiers, readiness `browser-cli-ready-v1`, and DOM schema `browser-dom-snapshot-v1`. Old branded active paths/identifiers are absent with no aliases, forwarding paths, fallback reads, or scans. Implementation-scoped checks pass; ready for source review.
- Related solution revision IDs: `SR-006` (preserving `SR-001`–`SR-005` history)
- Related architecture-review revision IDs: `ARCH-REV-006` (prior passing baselines preserved)
- Related code-review revision IDs: Prior `CRR-006`, `CRR-007`; SR-006 re-entry review `N/A`
- Related API/E2E revision IDs: Prior `API-REV-003`; SR-006 re-entry revision `N/A`
- Related delivery revision IDs: Prior `DR-002`; SR-006 re-entry revision `N/A`
- Why this implementation revision is recorded: Implement the user-approved generic capability identity across every active package/agent/operator/runtime/test surface as one clean rename without redesigning or weakening the already reviewed browser core.
- Approved behavior or requirement IDs affected: `BEH-004`, `BEH-005`, `BEH-007`, `BEH-008`, `BEH-009`; `REQ-003`, `REQ-009`–`REQ-013`; `AC-004`, `AC-010`–`AC-013`.
- Implementation delta: Renamed the project root, launchers, Python namespace, imports, distribution/console entry, uv lock record, skill/agent metadata, CLI identity/diagnostics/debug/readiness, workspace environment, DOM schema, MCP default name/instructions/diagnostics/cache log, root/project README references, and durable tests. Regenerated agent metadata and the lock; preserved `BrowserApplication`/`BrowserRuntime`, CDP target IDs, strict JSON, atomic artifacts, task-CWD/bootstrap ownership, MCP transports, loopback default, and non-loopback warning.
- Changed files or areas: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/browser-automation/`, `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/README.md`, and the canonical implementation handoff/revision artifacts. Historical ticket/revision/evidence content was moved with the bundle where applicable but not rewritten as failed history.
- Local validation and result: Bash syntax/executable checks, skill quick validation, regenerated OpenAI metadata, `uv lock --check`, compileall, focused `68 passed / 1 deselected`, default `69 passed / 7 skipped`, actual unrelated-CWD bundled launcher help, generic import/entrypoint and no-alias checks, generic sdist/wheel build, source-size inspection, and active old-path/identifier scans all passed.
- Next recipient or routing: `code_reviewer`
- Remaining limitations or risks: API/E2E must first refresh coverage investigation, then rerun the renamed real-Chrome, independent-process, live MCP, launcher/platform, output/removal, and fresh-agent matrix. Prior `API-REV-003` and delivery evidence remains historical evidence for the superseded branded contract and does not prove SR-006.

### IR-006 — Direct argument contract and atomic owned browser runtime

- Triggering role, report path, and round: `architecture_reviewer`; `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/design-review-report.md`; cumulative `SR-009` re-entry / `ARCH-REV-008`.
- Triggering finding IDs: `DR-006` / `PREM-004`, resolved by the reviewed `SR-009` gate-through-promote-or-abort design.
- Classification: `Approved Re-entry Delta`
- Prior authoritative result: `IR-005` and `CRR-008` passed the generic SR-006 implementation. The subsequent API/E2E investigation was held after the user corrected direct script-argument procedure and approved replacing the external runtime dependency. `ARCH-REV-007` passed the direct-argument and runtime ownership choices but found that readiness could be observed while the launch owner still had abort authority.
- Current authoritative result: Direct `--script` plus `--arg-json` is the normal skill procedure; optional file/stdin/arg-file modes remain supported. The external manager wrapper/dependency is replaced by a focused owned runtime package. Every supported caller gates before readiness classification, a new launch remains pending/gated through initial Playwright connection and first context, promotion clears abort authority before unlock, and failure/timeout/cancellation terminates and reaps only the exact owned group before unlock. Implementation-scoped checks pass; ready for source review.
- Related solution revision IDs: `SR-007`, `SR-008`, `SR-009` (preserving `SR-001`–`SR-006`)
- Related architecture-review revision IDs: `ARCH-REV-007`, `ARCH-REV-008`
- Related code-review revision IDs: Prior `CRR-008`; current re-entry review `N/A`
- Related API/E2E revision IDs: Prior `API-REV-003`; held SR-006 investigation and current re-entry execution `N/A`
- Related delivery revision IDs: Prior `DR-002`; current re-entry `N/A`
- Why this implementation revision is recorded: Implement the complete approved cumulative delta after `ARCH-REV-008`, including the direct argument-isomorphic agent procedure, removal of the external runtime mechanism, and the atomic establishment invariant that closes `DR-006`.
- Approved behavior or requirement IDs affected: `BEH-010`, `BEH-011`, with `BEH-001`–`BEH-009` preserved; `REQ-014`, `REQ-015`; `AC-014`, `AC-015`.
- Implementation delta: Updated `SKILL.md`/README and durable argument-source coverage; deleted the single-file external-manager wrapper; added `runtime/config.py`, `runtime/chrome_launcher.py`, `runtime/session.py`, and exports; removed the external distribution and regenerated the lock; added config/executable/gate/spawn/lease/cleanup/session/cancellation units and deterministic A-abort/B-fresh-decision plus A-promote/B-durable-attach interleavings; extended package/skill removal contracts and the existing real-Chrome script case to the direct `(arg) =>` form.
- Changed files or areas: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/browser-automation/SKILL.md`, `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/browser-automation/README.md`, `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/browser-automation/pyproject.toml`, `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/browser-automation/uv.lock`, `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/browser-automation/src/browser_automation/runtime/`, `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/browser-automation/tests/unit/test_runtime.py`, `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/browser-automation/tests/unit/test_cli_and_mcp.py`, `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/browser-automation/tests/integration/test_skill_contract.py`, `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/browser-automation/tests/integration/test_cli_real_chrome.py`, and the canonical implementation handoff/revision artifacts.
- Local validation and result: Skill quick validation, frozen lock check, compileall, Bash/ShellCheck, generic sdist/wheel build, installed package/entrypoint/runtime imports, source/package/lock removal scans, focused argument/runtime/skill-contract tests, and the default Chrome-free project suite all pass. The final authoritative counts and staged checks are recorded in `implementation-handoff.md`.
- Next recipient or routing: `code_reviewer`
- Remaining limitations or risks: API/E2E must refresh its held investigation after source review, then prove real durable-existing and production-owned Chrome lifecycles, independent process persistence/cleanup, unrelated Chrome survival, supported-host process/lock behavior, live MCP transports, package/removal surfaces, and a fresh agent using direct `--script`/`--arg-json`. Historical `API-REV-003`, delivery records, and the held SR-006 investigation are context only.
