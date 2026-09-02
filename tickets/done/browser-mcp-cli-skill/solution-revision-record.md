# Solution Revision Record

The current `requirements.md`, `investigation-notes.md`, `design-spec.md`, and `cli-conversion-analysis.md` are authoritative. This record indexes completed solution rounds and does not replace them.

## Revision Index

| Revision ID | Triggering Role / Report / Round | Finding IDs | Classification | Result |
| --- | --- | --- | --- | --- |
| `SR-001` | solution_designer initial architecture handoff | N/A | `Initial Baseline` | Requirements refined and approved; portable CLI+skill/shared-core design ready for architecture review |
| `SR-002` | architecture_reviewer / `design-review-report.md` / round 1 (`ARCH-REV-001`) | `DR-001`–`DR-004` | `Design Impact` | Launcher failure ownership, MCP operational surfaces, and artifact coherence corrected; ready for architecture re-review |
| `SR-003` | architecture_reviewer / `design-review-report.md` / round 2 (`ARCH-REV-002`) | `DR-004` | `Design Impact` | Final AC-012 scenario-intent wording aligned to the mandatory retained-MCP decision; ready for architecture re-review |
| `SR-004` | user correction plus AutoByteus workspace runtime investigation | `N/A` | `Requirement / Design Impact` | Agent-facing resource discovery changed from assumed `SKILL_DIR` to runtime-advertised `SKILL.md` locator plus bundle-relative paths; ready for architecture re-review |
| `SR-005` | architecture_reviewer / `design-review-report.md` / round 4 (`ARCH-REV-004`) | `DR-005` | `Design Impact` | Current approval, candidate-state, and reviewer-routing metadata aligned to SR-004; ready for architecture re-review |
| `SR-006` | user correction routed by api_e2e_engineer after `API-REV-003` / `CRR-007` | `N/A` | `Requirement / Design Impact` | Agent/CLI/MCP public vocabulary changed from product-branded to capability-oriented generic naming; ready for architecture re-review |
| `SR-007` | user correction routed by code_reviewer after `CRR-008`; API/E2E coverage investigation hold | `N/A` | `Requirement / Design Impact` | Normal CLI usage changed to direct argument-isomorphic mapping; file/stdin modes remain optional rather than complexity-preferred; ready for architecture re-review |
| `SR-008` | explicit user runtime-ownership approval; SR-007 architecture review halted without result | `N/A` | `Requirement / Design Impact` | Cumulative direct-argument contract plus focused package-owned Chrome/Playwright runtime; external `brui-core` dependency removed by design; ready for architecture review |
| `SR-009` | architecture_reviewer / `design-review-report.md` / round 7 (`ARCH-REV-007`) | `DR-006`, `PREM-004` | `Design Impact` | Per-port establishment gate now spans authoritative probe through pending launch connect/context promote-or-abort; ready for architecture re-review |

## Revision Entries

### SR-001 — Portable browser CLI and cross-agent skill baseline

- Triggering role, report path, and round: `solution_designer`; initial solution round; no prior review report.
- Triggering finding IDs: `N/A`
- Prior authoritative result: `N/A`
- Current authoritative result: Approved requirements and conversion analysis define a vendor-neutral, zero-human-install skill bundle; the design specifies a daemon-free CDP target identity, one shared browser application boundary, task-oriented JSON CLI, and retained thin MCP adapter.
- Why this baseline or revision entry is recorded: Establish the first complete solution package before architecture review and capture the user-critical correction from PATH/Codex-specific invocation to loader-supplied skill-root invocation.
- Resolution: Make the complete renamed browser project the skill folder; `SKILL.md` directs the agent to derive `SKILL_DIR` from its own loaded location; the bundled self-locating launcher runs frozen uv; CLI and MCP share `BrowserApplication`; Chrome owns cross-process tab state through opaque target IDs.
- Approved behavior or requirement IDs affected: `BEH-001`–`BEH-008`; `REQ-001`–`REQ-012`; `AC-001`–`AC-012`.
- Canonical artifacts and sections updated:
  - `requirements.md`: status, portable invocation, resolved decisions, acceptance criteria, approval record.
  - `investigation-notes.md`: user approvals, bundled-resource evidence, open-risk contraction, design-ready routing.
  - `design-spec.md`: complete initial target architecture, command/envelope contract, files, removals, sequencing, risks.
  - `cli-conversion-analysis.md`: approved skill-root command experience and resolved material decisions.
- Supplemental artifacts updated, added, or removed: Updated `cli-conversion-analysis.md`; no supplement removed.
- Downstream and architecture-review impact: Architecture reviewer should verify the whole-project-as-skill packaging, project/namespace rename, BrowserApplication/BrowserRuntime ownership split, target-ID lifecycle, adapter thinness, launcher stdout/bootstrap contract, and workspace safety before implementation.
- Next recipient or routing: `architecture_reviewer`.
- Remaining gaps or risks: Experimental CDP target-info compatibility; Bash-capable macOS/Linux first-release boundary; deliberate same-tab concurrency ordering; broad rename/removal completeness; browser-manager auto-launch behavior.

### SR-002 — Bootstrap and retained MCP operational completion

- Triggering role, report path, and round: `architecture_reviewer`; `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/design-review-report.md`; round 1 / `ARCH-REV-001`.
- Triggering finding IDs: `DR-001`, `DR-002`, `DR-003`, `DR-004`.
- Prior authoritative result: `Fail / Design Impact` for SR-001; core architecture passed but four technical/package-coherence findings blocked implementation.
- Current authoritative result: All four findings are addressed in the canonical package; SR-002 is ready for architecture re-review and remains blocked from implementation until that review passes.
- Why this baseline or revision entry is recorded: Preserve the exact round-1 design corrections and distinguish them from the approved SR-001 behavior/architecture baseline.
- Resolution:
  - `DR-001`: Replace unconditional CLI-launcher `exec` with captured stdout plus a private CLI-ready temporary-file handshake. Before readiness, launcher owns one fixed bootstrap envelope/exit `3`; after readiness, it forwards the CLI output/status exactly once, including nonzero CLI errors.
  - `DR-002`: Change retained streamable-HTTP default bind from unauthenticated `0.0.0.0` to `127.0.0.1`; validate configuration and warn once for explicit non-loopback hosts without adding an out-of-scope auth subsystem.
  - `DR-003`: Cleanly rename/update the tracked `scripts/browser_mcp_stdio.sh` to `scripts/autobyteus-browser-mcp`, update README/config and new namespace/root references, and remove the old path without forwarding compatibility.
  - `DR-004`: Refresh the supplement's renamed skill root/resolved decisions/true risks and the investigation notes' stage/status/reviewer routing text.
- Approved behavior or requirement IDs affected: `BEH-004`, `BEH-007`, `BEH-008`; `REQ-004`, `REQ-007`, `REQ-010`, `REQ-011`; `AC-003`, `AC-004`, `AC-012`. No business-intent change.
- Canonical artifacts and sections updated:
  - `requirements.md`: resolved retained-MCP behavior, launcher readiness guarantee, stdio wrapper rename, loopback/non-loopback acceptance criteria.
  - `design-spec.md`: `DS-003`, `DS-006`, new `DS-008`; readiness ownership/boundaries/example/contract/tests; MCP config/exposure section; stdio launcher file/removal/sequence/docs mapping.
  - `cli-conversion-analysis.md`: renamed `autobyteus-browser/` bundle, readiness handshake, all previously stale resolved decisions, residual evidence needs.
  - `investigation-notes.md`: current review status, architecture-review evidence, stdio launcher disposition, true residual risks, round-2 routing.
- Supplemental artifacts updated, added, or removed: Updated `cli-conversion-analysis.md`; architecture review artifacts retained as review evidence.
- Downstream and architecture-review impact: Architecture reviewer should verify closure of `DR-001`–`DR-004`. Implementation remains prohibited until a Pass review.
- Next recipient or routing: `architecture_reviewer` for round-2 re-review with the cumulative package and both round-1 review artifacts.
- Remaining gaps or risks: CDP protocol/version risk; browser auto-launch behavior; same-tab external races; Bash/macOS/Linux temporary-file behavior; explicit remote MCP bind remains operator-protected; broad rename/reference removal completeness.

### SR-003 — Retained MCP scenario-intent alignment

- Triggering role, report path, and round: `architecture_reviewer`; `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/design-review-report.md`; round 2 / `ARCH-REV-002`.
- Triggering finding IDs: remaining package-coherence item under `DR-004`.
- Prior authoritative result: `Fail / Design Impact` for SR-002 because the acceptance-criteria scenario-intent table retained an obsolete MCP-retention-or-removal alternative; `DR-001`–`DR-003` and the other `DR-004` corrections were verified resolved.
- Current authoritative result: The last stale scenario-intent row is aligned to mandatory retained MCP; SR-003 is ready for architecture re-review and remains blocked from implementation until that review passes.
- Why this revision entry is recorded: The normative behavior and acceptance criterion already required retained MCP, but the validation-intent summary still allowed clean MCP removal and therefore made the package internally contradictory.
- Resolution: Replace only the `AC-012` scenario-intent row with retained-MCP validation covering the shared core and both transports, the renamed stdio launcher and absence of its old path, loopback default, explicit non-loopback no-auth exposure warning, host/port validation, and no-broadening checks.
- Approved behavior or requirement IDs affected: `BEH-007`; `REQ-011`; `AC-012`. No business-intent or architecture change.
- Canonical artifacts and sections updated:
  - `requirements.md`: `Acceptance Criteria -> Scenario Intent` row for `AC-012` only.
  - `solution-revision-record.md`: added `SR-003`.
- Supplemental artifacts updated, added, or removed: None.
- Downstream and architecture-review impact: Architecture reviewer should verify final package coherence for `AC-012`. Implementation remains prohibited until a Pass review.
- Next recipient or routing: `architecture_reviewer` for round-3 re-review with the cumulative package and review artifacts.
- Remaining gaps or risks: Existing implementation-validation risks recorded in SR-002 remain; no unresolved design gap is known.

### SR-004 — Runtime-advertised skill locator and relative-resource contract

- Triggering role, report path, and round: User correction on 2026-08-18, followed by direct investigation of `/Users/normy/autobyteus_org/autobyteus-workspace-superrepo`; no downstream report.
- Triggering finding IDs: `N/A`.
- Prior authoritative result: SR-003 had corrected the last ARCH-REV-002 coherence row and was awaiting architecture re-review, but the agent-facing design still assumed that a skill loader supplied or enabled an agent-visible `SKILL_DIR` value.
- Current authoritative result: The canonical package now requires `SKILL.md` to contain only bundle-relative references. The agent reads the exact runtime-advertised `SKILL.md`, resolves `scripts/autobyteus-browser` from that file's containing directory, and invokes the resulting launcher path without relying on a populated variable or persistent shell state. The existing verification-ready candidate uses the superseded public `SKILL_DIR` example, so finalization is blocked pending architecture re-review and downstream source/coverage/delivery re-entry.
- Why this revision entry is recorded: The user clarified that skills are ordinarily read with general file tools from a path advertised in runtime context, not actively loaded through an agent API. AutoByteus source confirmed this for the native runtime and confirmed equivalent whole-package provider projections for Codex and Claude.
- Resolution:
  - Native AutoByteus: rely on the catalog's exact absolute `SKILL.md` path and its existing relative-reference rule.
  - Codex: preserve the provider-discovered or `.codex/skills/<name>` whole-directory projection; never embed the source/materialized path in the skill.
  - Claude: preserve the `.claude/skills/<name>` whole-directory projection and provider discovery; never embed the source/materialized path in the skill.
  - All runtimes: `SKILL.md` names `scripts/autobyteus-browser` only; the agent resolves it from `dirname(advertised SKILL.md)`, retains the task workspace as shell CWD, and invokes the resolved path. `SKILL_DIR` is neither populated nor required.
- Approved behavior or requirement IDs affected: `BEH-005`, `BEH-008`; `REQ-009`, `REQ-010`, `REQ-012`; `AC-004`, `AC-010`, `AC-011`. Browser CLI/core/MCP behavior is unchanged.
- Canonical artifacts and sections updated:
  - `requirements.md`: behavior map, investigation findings, recommendation, `REQ-010`, `AC-004`, `AC-011`, dependency, scenario intent, and approval record.
  - `investigation-notes.md`: current status, user correction, exact AutoByteus native/Codex/Claude runtime evidence, cross-runtime conclusion, and superseded reference interpretation.
  - `design-spec.md`: intended change, terminology, verified runtime projection contract, DS-003, ownership/dependency examples, file responsibilities, risk, and implementation guidance.
  - `cli-conversion-analysis.md`: shell command experience, resource discovery, verified runtime projection table, and resolved packaging decision.
- Supplemental artifacts updated, added, or removed: Updated `cli-conversion-analysis.md`; no supplement added or removed.
- Downstream and architecture-review impact: Architecture reviewer should re-review the complete skill-resource boundary and the explicit SR-004 candidate delta. On Pass, implementation must update `SKILL.md`/project README and durable contract coverage; fresh-agent/API-E2E evidence and code review must be refreshed proportionately, and delivery must replace stale verification guidance before finalization.
- Next recipient or routing: `architecture_reviewer` with the cumulative package and existing review artifacts.
- Remaining gaps or risks: Non-AutoByteus frameworks must expose a readable `SKILL.md` locator and ordinary shell/file access; absence of that capability is unsupported rather than recoverable through path guessing. All prior browser/CDP/bootstrap/MCP implementation-validation risks remain.

### SR-005 — SR-004 package-state and approval coherence

- Triggering role, report path, and round: `architecture_reviewer`; `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/design-review-report.md`; round 4 / `ARCH-REV-004`.
- Triggering finding IDs: `DR-005`.
- Prior authoritative result: `Fail / Design Impact` for SR-004 because current metadata across the canonical package still described 2026-08-17-only approval, no implementation, and obsolete SR-002/ARCH-REV-001 routing even though a verification-ready candidate and the approved 2026-08-18 correction were recorded elsewhere.
- Current authoritative result: Current approval applicability, existing-candidate state, and reviewer routing are aligned across the four canonical artifacts. SR-005 is ready for architecture re-review; implementation re-entry and finalization remain blocked until that review passes.
- Why this revision entry is recorded: Prevent downstream readers from applying the correct SR-004 technical design through an obsolete approval or lifecycle state.
- Resolution: Refresh only current status and approval-applicability text, identify the checkpointed candidate and its still-unimplemented SR-004 delta, and route the cumulative SR-004/SR-005 package against ARCH-REV-004/DR-005. Preserve historical revision and source-log facts.
- Approved behavior or requirement IDs affected: `BEH-005`, `BEH-008`; `REQ-009`, `REQ-010`, `REQ-012`; `AC-004`, `AC-010`, `AC-011`. No behavior or technical-design change.
- Canonical artifacts and sections updated:
  - `requirements.md`: document status, supplement approval applicability, and approval-basis assumption.
  - `investigation-notes.md`: current status/scope, request-context candidate state, supplement approval applicability, ARCH-REV-004 source entry, and reviewer routing.
  - `design-spec.md`: supplement approval applicability and pending candidate re-entry state.
  - `cli-conversion-analysis.md`: current approved-baseline and candidate re-entry status.
  - `solution-revision-record.md`: added `SR-005`.
- Supplemental artifacts updated, added, or removed: Updated `cli-conversion-analysis.md`; no supplement added or removed.
- Downstream and architecture-review impact: Architecture reviewer should verify only closure of `DR-005` and continued package coherence. The technically accepted SR-004 resource contract and browser core design are unchanged. Implementation re-entry remains prohibited until a Pass review.
- Next recipient or routing: `architecture_reviewer` for round-5 re-review with the cumulative package and all still-relevant downstream evidence.
- Remaining gaps or risks: The explicit SR-004 source, durable contract coverage, fresh-agent/API-E2E, proportional code-review, and delivery refresh remain pending after architecture Pass. Prior CDP, concurrency, bootstrap, MCP exposure, and rename-validation risks are unchanged.

### SR-006 — Capability-oriented browser automation identity

- Triggering role, report path, and round: User correction confirmed through `api_e2e_engineer` after successful `API-REV-003` and `CRR-007`; requirement/design re-entry, not an API/E2E local fix.
- Triggering finding IDs: `N/A` — authoritative user vocabulary correction.
- Prior authoritative result: `ARCH-REV-005` passed SR-005; IR-004, CRR-006, API-REV-003, and CRR-007 then passed exact advertised-file-relative execution using the now-superseded branded resource/name. The candidate was verification-ready for that prior contract but not finalized.
- Current authoritative result: The requirements basis and target design now make browser automation entirely capability-oriented across skill, locator segment, launcher, CLI, MCP, package/protocol identifiers, active docs, and tests. The branded candidate is blocked from implementation re-entry/finalization until SR-006 passes architecture review.
- Why this revision entry is recorded: The user explicitly explained that AutoByteus is product/platform provenance with no useful meaning to an LLM. A copy-only skill edit would leave contradictory and agent-visible branding in runtime paths, help/errors/results, MCP metadata/logs, package internals, docs, and coverage.
- Resolution:
  - Skill/catalog/folder/server identity: `browser-automation`; human title **Browser Automation**; generic capability description; metadata token `$browser-automation`.
  - Agent launcher and CLI: `scripts/browser`; CLI console/prog/error identity `browser`; preserve exact locator-relative resolution, task CWD, frozen bootstrap, readiness ownership, and JSON/exit contracts.
  - MCP: `scripts/browser-mcp`, generic server instructions/errors/warnings/cache/log, existing generic `browser-mcp-server`, unchanged transports/shared core/exposure policy.
  - Package/protocol: distribution `browser-automation`, namespace `browser_automation`, `BROWSER_AUTOMATION_*` workspace/debug/readiness identifiers, `browser-cli-ready-v1`, `browser-dom-snapshot-v1`.
  - Boundary: AutoByteus remains only in genuine package-author/root-repository-origin metadata and immutable historical tickets/review/revision/evidence. Runtime-owned locator ancestors are outside package control, but the capability-controlled segment ends `browser-automation/SKILL.md`.
  - Clean removal: no old bundle/skill ID, launcher, MCP wrapper, console/import/env/schema/default-prompt alias, forwarding path, or fallback scan.
- Approved behavior or requirement IDs affected: `BEH-005`, `BEH-007`, `BEH-008`, new `BEH-009`; `REQ-003`, `REQ-009`–`REQ-013`; `AC-004`, `AC-010`–`AC-013`. Browser operations, target identity, safety, output semantics, lifecycle, and MCP transport/exposure behavior remain unchanged.
- Canonical artifacts and sections updated:
  - `requirements.md`: current/desired behavior, investigation findings, recommendations, generic naming requirements and acceptance criteria, mappings, decisions, constraints, and approval status.
  - `investigation-notes.md`: current state, source log, complete naming exposure inventory, generic boundary, candidate impact, risks, and reviewer routing.
  - `design-spec.md`: intended change, behavior map, naming boundary/table, spines/facades/removals/files/contracts, clean re-entry sequence, risks, and implementation guidance.
  - `cli-conversion-analysis.md`: status, CLI/shell contract, capability naming table, resolved decisions, and follow-up evidence.
  - `solution-revision-record.md`: added `SR-006`.
- Supplemental artifacts updated, added, or removed: Updated `cli-conversion-analysis.md`; no supplement added or removed.
- Downstream and architecture-review impact: Architecture reviewer should validate the precise agent-facing boundary, internal-leakage rationale, exact generic naming set, clean removal policy, and proportional reuse of the validated browser core. On Pass, implementation performs the atomic rename; source/code review, API/E2E coverage investigation/execution, proportional coverage review, and delivery refresh must all rerun as required.
- Next recipient or routing: `architecture_reviewer` with the cumulative package and all prior downstream evidence, including API-REV-003 and CRR-007 as truthful historical evidence.
- Remaining gaps or risks: Broad active-reference removal across root/package/lock/imports/env/readiness/schema/MCP/docs/tests; runtime-owned ancestor path names outside capability control; all prior CDP, same-tab concurrency, bootstrap, and explicit non-loopback risks remain bounded and unchanged.

### SR-007 — Argument-isomorphic agent CLI contract

- Triggering role, report path, and round: Explicit user correction routed by `code_reviewer` after `CRR-008`, followed by the held API/E2E coverage investigation at `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/api-e2e-coverage-investigation.md`; requirement/design re-entry, not an API/E2E local fix.
- Triggering finding IDs: `N/A` — authoritative user command-model correction; API/E2E classification is `Requirement Gap / Design Impact` with `Proceed: No`.
- Prior authoritative result: `ARCH-REV-006` passed SR-006, `IR-005` implemented the generic capability, and `CRR-008` passed source review. The current CLI parser already accepts direct `--script`/`--arg-json` and optional file/stdin sources. However, the then-approved `SKILL.md` and design prefer file/stdin for nontrivial code, so prior source approval and provisional held runs do not prove the corrected agent procedure.
- Current authoritative result: The canonical package now defines semantic argument isomorphism as the normal CLI model. Former MCP operations map to approved task commands and supported user arguments to explicit operation-specific flags. `run_script(tab_id, script, arg)` normally becomes `run-script --tab-id ... --script '<direct JavaScript>' --arg-json '<direct structured JSON>'`. SR-007 is ready for architecture review; implementation/API-E2E/delivery remain held until it passes.
- Why this revision entry is recorded: The user's main goal is that agents invoke the CLI naturally through Bash rather than performing unnecessary input transformation. Treating complex inline code as an anti-shape contradicts that intent even though the executable capability already exists.
- Resolution:
  - Normal mapping: snake-case MCP operation -> approved kebab-case task command; each supported user argument -> one explicit operation-specific flag; no generic MCP/request envelope.
  - Scripted interaction: pass JavaScript directly through `--script` and structured `arg` directly through `--arg-json`; the coding agent owns correct Bash quoting, including nontrivial or multiline content.
  - Optional alternatives: preserve `--script-file`, `--script-stdin`, and `--arg-file` only for pre-existing sources or a concrete shell/process transport constraint. Complexity, length, multiline form, or structured content alone is not a preference trigger.
  - Preserved implementation: do not redesign `BrowserApplication`, `BrowserRuntime`, launcher/bootstrap, JSON/error, target identity, safety/lifecycle, packaging/naming, MCP transports/exposure, output artifacts, or existing parser source modes.
  - Evidence: update active skill/prose and durable contract assertions, then rerun source review and the held API/E2E investigation/execution with a fresh-agent real-Chrome direct-script/structured-argument journey.
- Approved behavior or requirement IDs affected: new `BEH-010`, `REQ-014`, `AC-014`; refined `REQ-003`, `REQ-006`, `REQ-009`, `REQ-012`, and `AC-011`. Prior `BEH-001`–`BEH-009`, `REQ-001`–`REQ-013`, and `AC-001`–`AC-013` remain preserved except for the explicit procedural refinement.
- Canonical artifacts and sections updated:
  - `requirements.md`: SR-007 status, `BEH-010`, findings/recommendations, `REQ-014`, `AC-014`, direct fresh-agent scenario, mappings, decisions, constraints, and approval basis.
  - `investigation-notes.md`: current generic candidate state, downstream correction/coverage hold evidence, direct-vs-alternate input boundary, affected surfaces, risks, and reviewer routing.
  - `design-spec.md`: current-state conflict, intended direct mapping, behavior/spine/boundary updates, examples/command contract, narrow re-entry sequence, tradeoffs, risks, and implementation guidance.
  - `cli-conversion-analysis.md`: status, `run_script` disposition, contract principles, full argument-mapping table, direct Bash example, resolved decision, and follow-up evidence.
  - `solution-revision-record.md`: added `SR-007`.
- Supplemental artifacts updated, added, or removed: Updated `cli-conversion-analysis.md`; no supplement added or removed. Included the refreshed `api-e2e-coverage-investigation.md` as the downstream reroute artifact without treating it as a completed execution result.
- Downstream and architecture-review impact: Architecture reviewer should validate the semantic isomorphism definition, direct `--script`/`--arg-json` normal form, bounded alternate-source rule, documented exceptions, and proportionate no-core-redesign sequence. On Pass, implementation updates only affected active skill/prose/help-if-needed and durable contract expectations; code review repeats before API/E2E resumes. Any later API/E2E durable coverage edit returns through code review before delivery.
- Next recipient or routing: `architecture_reviewer` with the cumulative package, including `ARCH-REV-006`, `IR-005`, `CRR-008`, and the held coverage-investigation reroute as truthful stage evidence.
- Remaining gaps or risks: Direct argv has host length limits and Bash quoting semantics, but no current product defect is known. Fresh-agent coverage must prove nontrivial direct JavaScript plus structured JSON without converting optional escape hatches into a default. Prior CDP, concurrency, bootstrap, MCP exposure, and generic naming risks remain bounded and unchanged.

### SR-008 — Self-contained owned browser runtime

- Triggering role, report path, and round: Explicit user approval on 2026-08-18 after asking whether the very small sibling `brui_core` code should live inside browser automation; cumulative requirement/design re-entry while SR-007 architecture review was still running.
- Triggering finding IDs: `N/A` — authoritative user ownership/evolution decision. Architecture reviewer halted SR-007 and issued no result for that basis; the next numbered review, `ARCH-REV-007`, later reviewed SR-008.
- Prior authoritative result: `ARCH-REV-006`, `IR-005`, and `CRR-008` passed the generic SR-006 candidate. SR-007 had made the direct-argument solution package ready for review, but no architecture result existed when the user approved runtime independence. The candidate still imports `BrowserManager` and `get_browser_config` from `brui-core>=2.0.0`.
- Current authoritative result: SR-008 is one cumulative architecture-review basis. It preserves SR-007's direct `--script`/`--arg-json` normal form and adds a focused owned `browser_automation.runtime` config/Chrome-launch/Playwright-session package. The separate library remains untouched; implementation and all held downstream stages remain blocked until architecture Pass.
- Why this revision entry is recorded: Browser automation's complete skill bundle cannot evolve or relocate independently while its narrow runtime seam depends on a separately released library that contributes unused UI/clipboard/transitives, singleton lifecycle, Linux-specific launch assumptions, and global-kill behavior. Only two external symbols are used, so a narrow owned rewrite is proportionate and avoids vendoring a generic library.
- Resolution:
  - Keep `BrowserApplication`, CLI/MCP adapters, explicit CDP target IDs, JSON/artifact/safety contracts, exact locator/bootstrap, generic naming, and retained MCP transport/exposure unchanged.
  - Preserve the SR-007 semantic argument mapping. Use an implementation-compatible `(arg) => ({..., label: arg.label})` example; do not teach complexity-based file/stdin indirection. No script-normalizer expansion is required.
  - Replace `src/browser_automation/runtime.py` with `runtime/{__init__,config,chrome_launcher,session}.py`. Config owns fixed-loopback validated port/profile/user-data/log plus generic executable selection; launcher owns probe/secure per-port lock/double-check/process-group spawn/readiness/exact failed-attempt cleanup; session owns direct Playwright/CDP connection, first context, targets, and client-only disconnect.
  - Attach to a ready endpoint without launch. Never terminate pre-existing/unrelated Chrome. Terminate only the process group created by a failed current attempt. After readiness and successful initial connection, leave the launched Chrome running as external durable state for later CLI processes.
  - Remove `brui-core` from `pyproject.toml`/`uv.lock`, active imports, and now-unused transitives. Do not vendor `brui_core`, expose manager/UI/clipboard/singleton/global-kill compatibility APIs, modify the sibling repository, or create an editable/path/submodule dependency. Remove unused `CHROME_DOWNLOAD_DIRECTORY` rather than preserving a parsed no-op.
  - Prefer independent reimplementation. If any sibling source is copied, verify the declared MIT terms and attribution first because the inspected checkout has no root `LICENSE` file.
- Approved behavior or requirement IDs affected: new `BEH-011`, `REQ-015`, `AC-015`; preserves SR-007 `BEH-010`, `REQ-014`, `AC-014` and all earlier contracts.
- Canonical artifacts and sections updated:
  - `requirements.md`: cumulative SR-008 status, behavior/finding/recommendation, owned-runtime requirement and acceptance criterion, constraints, mappings, decisions, and approval record.
  - `investigation-notes.md`: user approval, sibling/candidate source evidence, current dependency/lifecycle impact, risks, architecture halt/observations, and SR-008 routing.
  - `design-spec.md`: cumulative intended change/behavior map, owned runtime contract, config and launch ownership, spines/boundaries/dependencies/removals/file map, implementation-compatible direct example, refactor sequence, tradeoffs, risks, and implementation guidance.
  - `cli-conversion-analysis.md`: cumulative status/ranges, implementation-compatible direct example, runtime ownership evidence/decision table, resolved choice, and evidence plan.
  - `solution-revision-record.md`: added `SR-008`.
- Supplemental artifacts updated, added, or removed: Updated `cli-conversion-analysis.md`; no supplement added or removed. The held `api-e2e-coverage-investigation.md` remains a required reroute artifact and is not rewritten as completed SR-008 evidence.
- Downstream and architecture-review impact: Architecture reviewer should review the cumulative direct-argument procedure plus owned-runtime boundary, lifecycle ownership, clean dependency removal, no-vendoring decision, and validation scope. On Pass, implementation updates source/package/lock/docs/tests; code review repeats before API/E2E refreshes its investigation and executes both real runtime modes plus fresh-agent direct arguments. Durable API/E2E coverage edits return through code review before delivery.
- Next recipient or routing: `architecture_reviewer` with all current canonical artifacts, the supplemental analysis, prior review/downstream history, held coverage reroute, current candidate source/tests, and inspected sibling runtime evidence.
- Remaining gaps or risks: macOS/Linux executable discovery and process-group semantics; cross-process absent-endpoint races; Chrome/CDP version behavior; successful-launch persistence without an owned daemon; direct argv shell/length mechanics; and licensing verification if implementation copies rather than independently rewrites source. All have explicit design boundaries and planned evidence; no material requirement question remains open.

### SR-009 — Atomic cross-process Chrome establishment

- Triggering role, report path, and round: `architecture_reviewer`; `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/design-review-report.md`; round 7 / `ARCH-REV-007` reviewing cumulative SR-008.
- Triggering finding IDs: `DR-006`; material-premise record `PREM-004`.
- Prior authoritative result: `Fail / Design Impact`. All direct argument-isomorphic, owned-runtime allocation, clean `brui-core` removal, no-vendoring, file-placement, and proportional validation decisions passed. `DS-005` failed because `/json/version` could become visible before the launch owner completed Playwright connection/first-context promotion, allowing a second supported caller to attach while the first still retained abort authority.
- Current authoritative result: The per-port establishment gate is now mandatory before every supported caller's authoritative readiness probe. A new owner retains the gate after readiness through initial connection/context and ends it only through ordered promote or exact abort. SR-009 is ready for architecture re-review; implementation and held downstream stages remain blocked until Pass.
- Why this revision entry is recorded: `PREM-004` proves a complete supported two-caller path, not a speculative race. Without atomic establishment, caller A's legitimate initial-connect failure cleanup could kill Chrome already used by caller B, contradicting successful-launch persistence and no-unrelated/pre-existing-termination contracts.
- Resolution:
  - `ChromeLauncher.ensure_available()` acquires the owner-only per-port advisory gate before authoritative probe; no ready-path fast return bypasses it.
  - Ready under an otherwise-unheld gate returns `DURABLE_EXISTING`, releases immediately, and grants no abort authority. This preserves attach-first for truly pre-existing or no-longer-abortable Chrome.
  - Unavailable starts one group and returns `PENDING_OWNED` while retaining gate, process handle, and exact abort authority after `/json/version` readiness.
  - `BrowserRuntime` connects Playwright and obtains first context while pending. `promote()` clears abort authority before unlock. Failure/timeout/cancellation calls `abort()`, which terminates/reaps only the exact group before unlock. Waiting callers then make a fresh gated decision.
  - Kernel `flock` release after owner death is sufficient because a dead owner cannot later abort. Lock-file existence stores no state; no daemon, marker, PID file, or persistent browser registry is added.
  - `AC-015` adds deterministic readiness-before-promotion two-caller interleavings: B must remain before probe/classify/connect while A is pending; cover both A-abort/B-fresh-decision and A-promote/B-durable-attach branches.
- Approved behavior or requirement IDs affected: refined `BEH-011`, `REQ-015`, and `AC-015`; explicitly reinforces `REQ-001`, `REQ-005`, `REQ-007`, `REQ-012`, `AC-001`, and `AC-008`. No product behavior or public command change.
- Canonical artifacts and sections updated:
  - `requirements.md`: SR-009 status, finding/recommendation, atomic establishment invariant in `BEH-011`/`REQ-015`/`AC-015`, constraint, decision, and approval record.
  - `investigation-notes.md`: ARCH-REV-007/PREM-004 evidence, candidate-impact lifecycle rows, risks, and current reviewer routing.
  - `design-spec.md`: intended change, behavior map, terminology, `ChromeAvailability` state contract, `DS-005`, ownership/boundary/dependency/interface/file mappings, interleaving example, sequence, tradeoff, risks, and implementation guidance.
  - `cli-conversion-analysis.md`: current status, runtime lifecycle/decision, and deterministic evidence expectations.
  - `solution-revision-record.md`: added `SR-009` and clarified the SR-007-vs-ARCH-REV-007 numbering history.
- Supplemental artifacts updated, added, or removed: Updated `cli-conversion-analysis.md`; no supplement added or removed. Architecture review artifacts now carry authoritative `ARCH-REV-007/DR-006/PREM-004` evidence.
- Downstream and architecture-review impact: Architecture reviewer should verify only that `DR-006` is closed without reopening `DR-001`–`DR-005` or the other passing SR-008 areas. On Pass, implementation executes the full cumulative direct-argument/owned-runtime delta; source review and held API/E2E/delivery re-entry remain required.
- Next recipient or routing: `architecture_reviewer` for SR-009 re-review with the cumulative package and `ARCH-REV-007` artifacts.
- Remaining gaps or risks: advisory-lock security/timeout/cancellation behavior, POSIX exact-group cleanup, executable discovery, CDP compatibility, and deterministic scheduling hooks remain implementation-validation risks already mapped to `AC-015`; no design or requirement gap remains known.
