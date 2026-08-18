# Architecture Review Revision Record

The current `design-review-report.md` is authoritative. This record preserves the concise architecture-review history.

## Revision Index

| Revision ID | Review Round / Trigger | Related Solution Revision IDs | Prior Decision | Current Decision | Affected Finding IDs |
| --- | --- | --- | --- | --- | --- |
| `ARCH-REV-001` | Round 1 / initial solution package review | `SR-001` | N/A | `Fail` | `DR-001`, `DR-002`, `DR-003`, `DR-004` |
| `ARCH-REV-002` | Round 2 / `SR-002` correction re-review | `SR-002` | `Fail` | `Fail` | `DR-001`, `DR-002`, `DR-003`, `DR-004` |
| `ARCH-REV-003` | Round 3 / `SR-003` final coherence re-review | `SR-003` | `Fail` | `Pass` | `DR-004` |
| `ARCH-REV-004` | Round 4 / `SR-004` runtime-resource contract re-entry | `SR-004` | `Pass` | `Fail` | `DR-005` |
| `ARCH-REV-005` | Round 5 / `SR-005` package-coherence re-review | `SR-005` | `Fail` | `Pass` | `DR-005` |
| `ARCH-REV-006` | Round 6 / `SR-006` capability-vocabulary re-entry | `SR-006` | `Pass` | `Pass` | None |
| `ARCH-REV-007` | Round 7 / cumulative `SR-008` direct-argument and owned-runtime re-entry | `SR-007`, `SR-008` | `Pass` | `Fail` | `DR-006` |
| `ARCH-REV-008` | Round 8 / `SR-009` atomic Chrome-establishment re-review | `SR-009` | `Fail` | `Pass` | `DR-006` |

## Revision Entries

### ARCH-REV-001 — Initial portable browser CLI and skill architecture baseline

- Canonical design review report: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/design-review-report.md`
- Review round and trigger: Round 1; initial architecture handoff from `solution_designer`.
- Triggering role, report path, and finding IDs: `solution_designer`; no prior design-review report; findings `DR-001`–`DR-004` established here.
- Relevant solution revision IDs: `SR-001`
- Prior authoritative decision: `N/A`
- Current authoritative decision: `Fail`
- What changed in the review result or what baseline was established: Established that the project-as-skill packaging, loader-relative `SKILL_DIR` contract, `BrowserApplication`/`BrowserRuntime` split, CDP target identity, clean alias/global-close removal, artifact policy, and thin-adapter dependency direction are sound. Recorded blockers in the launcher failure lifecycle, retained MCP operational/launcher disposition, and artifact currentness.

#### Prior Finding Resolution

None.

- New or remaining finding IDs: `DR-001`, `DR-002`, `DR-003`, `DR-004`
- Material classification changes: N/A — initial baseline.
- Recommended recipient: `solution_designer`
- Remaining risks or uncertainty: Experimental CDP target-info compatibility, same-tab cross-client ordering, brui auto-launch behavior, rename breadth, and Bash-only first-release boundary remain nonblocking validation risks after the current findings are resolved.

### ARCH-REV-002 — Technical blockers resolved; one stale scenario map remains

- Canonical design review report: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/design-review-report.md`
- Review round and trigger: Round 2; `SR-002` re-review after `ARCH-REV-001`.
- Triggering role, report path, and finding IDs: `solution_designer`; `solution-revision-record.md` / `SR-002`; prior findings `DR-001`–`DR-004`.
- Relevant solution revision IDs: `SR-002`
- Prior authoritative decision: `Fail`
- Current authoritative decision: `Fail`
- What changed in the review result or what baseline was established: Verified the launcher readiness/captured-stdout handoff, retained MCP loopback/non-loopback operational policy, clean stdio-wrapper rename/removal, and refreshed supplement/investigation state. The design is technically coherent. One stale optional-removal phrase remains in the requirements acceptance-scenario map, so the cumulative package is not yet ready for implementation.

#### Prior Finding Resolution

| Finding ID | Prior Status | Current Status | Related Revision References | Verification Evidence |
| --- | --- | --- | --- | --- |
| `DR-001` | Open | Resolved | `SR-002` | `design-spec.md` `DS-003`, `DS-006`, readiness ownership/interface/files, pseudocode, machine contract, sequence, and tests specify one no-ready bootstrap envelope or one ready CLI output/status. |
| `DR-002` | Open | Resolved | `SR-002` | `design-spec.md` `DS-008`, `mcp/config.py`, operational/security contract, loopback default, explicit non-loopback warning, no-auth boundary, and validation matrix are complete and proportionate. |
| `DR-003` | Open | Resolved | `SR-002` | `scripts/autobyteus-browser-mcp` is present in facade/file/folder/change/removal mappings; the old path is explicitly removed without forwarding and active docs/config are updated. |
| `DR-004` | Open | Remains Open | `SR-002` | Supplement and investigation text are corrected, but `requirements.md` line 193 still describes `AC-012` as retained parity **or clean removal**, contradicting the now-fixed retained-MCP requirement and acceptance criterion. |

- New or remaining finding IDs: `DR-004`
- Material classification changes: None. The remaining issue is the same cross-artifact coherence finding, not a new requirement decision.
- Recommended recipient: `solution_designer`
- Remaining risks or uncertainty: CDP compatibility, same-tab external races, brui auto-launch behavior, readiness behavior on supported shells, non-loopback operator protection, and broad rename cleanup remain implementation-validation risks after `DR-004` closes.

### ARCH-REV-003 — Final package coherence resolved; design passes

- Canonical design review report: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/design-review-report.md`
- Review round and trigger: Round 3; `SR-003` re-review after the remaining `ARCH-REV-002` finding.
- Triggering role, report path, and finding IDs: `solution_designer`; `solution-revision-record.md` / `SR-003`; prior finding `DR-004`.
- Relevant solution revision IDs: `SR-001`, `SR-002`, `SR-003`
- Prior authoritative decision: `Fail`
- Current authoritative decision: `Pass`
- What changed in the review result or what baseline was established: Verified that the `AC-012` scenario-intent row now mandates retained-MCP validation through the shared core for stdio and streamable HTTP, the renamed launcher and old-path absence, loopback default, explicit non-loopback warning, host/port validation, and no-broadening checks. This closes the final cross-artifact contradiction without changing approved behavior or architecture.

#### Prior Finding Resolution

| Finding ID | Prior Status | Current Status | Related Revision References | Verification Evidence |
| --- | --- | --- | --- | --- |
| `DR-004` | Remains Open | Resolved | `SR-003` | `requirements.md` line 193 now expresses only the retained-MCP `AC-012` scenario and matches the normative acceptance criterion and the shared-core/MCP design. Searches of the current package find no superseded retained-or-remove alternative. |

- New or remaining finding IDs: None.
- Material classification changes: The prior `Design Impact` blocker is resolved; no failure classification applies to the passing result.
- Recommended recipient: `implementation_engineer`
- Remaining risks or uncertainty: Experimental CDP target-info compatibility, same-tab external races, `brui_core` auto-launch behavior, supported-shell readiness behavior, explicit non-loopback operator protection, and broad rename/reference cleanup remain implementation-validation risks.

### ARCH-REV-004 — Corrected resource boundary passes technically; package state needs one refresh

- Canonical design review report: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/design-review-report.md`
- Review round and trigger: Round 4; `SR-004` architecture re-entry after the user's correction to the public agent skill-resource model invalidated the verification-ready candidate's `SKILL_DIR` example.
- Triggering role, report path, and finding IDs: `solution_designer`; `solution-revision-record.md` / `SR-004`; no prior open finding; new finding `DR-005`.
- Relevant solution revision IDs: `SR-001`, `SR-002`, `SR-003`, `SR-004`
- Prior authoritative decision: `Pass`
- Current authoritative decision: `Fail`
- What changed in the review result or what baseline was established: Direct AutoByteus source inspection confirms the exact-path native catalog, whole-root Codex/Claude projection, relative-resource invariant, and administrative-only `SkillLoader`. The corrected `SKILL.md` contract and narrow existing-candidate re-entry plan pass structurally and do not reopen the browser core. The cumulative package nevertheless retains contradictory 2026-08-17-only approval metadata, a no-implementation statement, and obsolete `SR-002` routing, so implementation re-entry is not yet authorized.

#### Prior Finding Resolution

None. `DR-001`–`DR-004` remain resolved; `DR-005` is new in this round.

- New or remaining finding IDs: `DR-005`
- Material classification changes: The prior passing result changes to `Fail / Design Impact` because `SR-004` introduced a new approved contract and re-entry state that was not propagated consistently through current package metadata.
- Recommended recipient: `solution_designer`
- Remaining risks or uncertainty: After `DR-005` closes, the explicit `SR-004` implementation, durable coverage, fresh-agent/API-E2E, proportional code-review, and delivery refresh remain required. Experimental CDP compatibility, same-tab races, `brui_core` auto-launch, supported-shell readiness, explicit non-loopback operator protection, and broad reference cleanup remain bounded validation risks.

### ARCH-REV-005 — SR-004 package state aligned; re-entry design passes

- Canonical design review report: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/design-review-report.md`
- Review round and trigger: Round 5; `SR-005` re-review after `ARCH-REV-004` finding `DR-005`.
- Triggering role, report path, and finding IDs: `solution_designer`; `solution-revision-record.md` / `SR-005`; prior finding `DR-005`.
- Relevant solution revision IDs: `SR-001`, `SR-002`, `SR-003`, `SR-004`, `SR-005`
- Prior authoritative decision: `Fail`
- Current authoritative decision: `Pass`
- What changed in the review result or what baseline was established: Verified that requirements, investigation, design, and supplement now identify both approval dates, the checkpointed existing candidate, the still-pending `SR-004` delta, and the correct `SR-005`/`ARCH-REV-004` reviewer route. Historical revision/source-log facts remain intact. The technically accepted runtime-locator contract and narrow candidate re-entry plan are unchanged and ready for implementation.

#### Prior Finding Resolution

| Finding ID | Prior Status | Current Status | Related Revision References | Verification Evidence |
| --- | --- | --- | --- | --- |
| `DR-005` | Open | Resolved | `SR-005` | `requirements.md` status/supplement/assumption text now covers the 2026-08-17 and 2026-08-18 approvals; `investigation-notes.md` distinguishes the checkpointed candidate from its pending delta, updates supplement applicability, records `ARCH-REV-004`, and routes `SR-005`; `design-spec.md` and `cli-conversion-analysis.md` carry the same current status. The obsolete active phrases no longer occur. |

- New or remaining finding IDs: None.
- Material classification changes: The prior `Design Impact` blocker is resolved; no failure classification applies to the passing result.
- Recommended recipient: `implementation_engineer`
- Remaining risks or uncertainty: The explicit `SR-004` skill/prose and durable coverage change, fresh-agent/API-E2E refresh, proportional code review, and delivery refresh remain required before finalization. Experimental CDP compatibility, same-tab races, `brui_core` auto-launch, supported-shell readiness, explicit non-loopback operator protection, and stale-reference cleanup remain bounded validation risks.

### ARCH-REV-006 — Generic browser-automation boundary and atomic re-entry pass

- Canonical design review report: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/design-review-report.md`
- Review round and trigger: Round 6; `SR-006` architecture re-entry after the user's approved correction replaced product-branded capability vocabulary with generic browser-automation vocabulary. The correction was routed after successful `API-REV-003` and `CRR-007` verification of the now-superseded branded contract.
- Triggering role, report path, and finding IDs: `solution_designer`; `solution-revision-record.md` / `SR-006`; no prior open finding and no new finding.
- Relevant solution revision IDs: `SR-001`, `SR-002`, `SR-003`, `SR-004`, `SR-005`, `SR-006`
- Prior authoritative decision: `Pass`
- Current authoritative decision: `Pass`
- What changed in the review result or what baseline was established: Verified the exact generic set—`browser-automation`, **Browser Automation**, `$browser-automation`, `scripts/browser`, CLI `browser`, `scripts/browser-mcp`, retained `browser-mcp-server`, distribution/namespace `browser-automation` / `browser_automation`, `BROWSER_AUTOMATION_*`, `browser-cli-ready-v1`, and `browser-dom-snapshot-v1`. The package maps supported catalog/locator, help/error/debug/result, MCP, package, documentation, and coverage paths to those names; confines provenance to author/origin ownership metadata, immutable history/evidence, and runtime-owned path ancestors; and removes the branded candidate without aliases, fallback reads, scans, or forwarding paths. The checkpointed `BrowserApplication`/`BrowserRuntime`, locator-relative invocation, readiness bootstrap, JSON, target-ID, artifact/lifecycle safety, and MCP exposure design remain unchanged. The atomic rename plus downstream revalidation is ready for implementation.

#### Prior Finding Resolution

None. `DR-001`–`DR-005` remain resolved; `SR-006` is a new approved requirement/design re-entry rather than recurrence of a prior finding.

- New or remaining finding IDs: None.
- Material classification changes: None. The prior `Pass` remains `Pass`; `SR-006` adds an approved cross-surface naming requirement and implementation re-entry, not a new architecture defect.
- Recommended recipient: `implementation_engineer`
- Remaining risks or uncertainty: The broad root/distribution/namespace/protocol rename requires exact active-surface removal scans, regenerated lock/package identity, and complete unit/launcher/MCP/real-Chrome/fresh-agent regression. Prior functional evidence remains truthful history but is not final `SR-006` evidence. CDP compatibility, same-tab races, `brui_core` auto-launch, supported-shell readiness, and explicitly selected unauthenticated non-loopback MCP binds remain bounded unchanged risks.

### ARCH-REV-007 — Cumulative direct-argument contract passes; launch-promotion race blocks owned runtime

- Canonical design review report: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/design-review-report.md`
- Review round and trigger: Round 7; cumulative `SR-008` architecture re-entry after the `SR-007` review was halted without a result and the user approved replacing the small external `brui_core` dependency with a focused package-owned browser runtime.
- Triggering role, report path, and finding IDs: `solution_designer`; `solution-revision-record.md` / `SR-008`; new finding `DR-006`.
- Relevant solution revision IDs: `SR-001` through `SR-008`; `SR-008` is current and preserves the `SR-007` direct-argument correction.
- Prior authoritative decision: `Pass` (`ARCH-REV-006` for `SR-006`; no `ARCH-REV-007` result previously existed for the halted `SR-007` review).
- Current authoritative decision: `Fail`
- What changed in the review result or what baseline was established: Verified that the normal operation-specific flag mapping, direct `--script` plus `--arg-json`, optional-only file/stdin/arg-file sources, and `(arg) =>` example are coherent with the current parser/normalizer. Also verified the focused config/Chrome-launch/Playwright-session allocation, clean `brui-core`/unused-transitive removal, no-vendoring/sibling policy, exact process-group cleanup intent, and proportional validation plan. The owned-runtime design is blocked by one lifecycle gap: endpoint readiness becomes visible before the launching client completes initial connection/context promotion, so a concurrent caller can attach through the pre-existing/no-op path while the first caller still retains abort authority over that Chrome group.

#### Prior Finding Resolution

None. `DR-001`–`DR-005` remain resolved. `DR-006` is new and does not reopen those earlier findings.

- New or remaining finding IDs: `DR-006`
- Material classification changes: The latest decision changes from `Pass` to `Fail / Design Impact` because the new `SR-008` runtime lifecycle does not make cross-process launch ownership atomic through promotion/abort. `SR-007` itself passes within the cumulative review.
- Recommended recipient: `solution_designer`
- Remaining risks or uncertainty: After `DR-006` closes, executable discovery, CDP readiness validation, POSIX process-group behavior, per-port lock security, real existing/owned Chrome journeys, direct-argv fresh-agent execution, frozen dependency removal, and full source/API-E2E/delivery re-entry remain required. The held API/E2E investigation and prior `ARCH-REV-006`/`IR-005`/`CRR-008` evidence remain truthful history, not final `SR-008` proof.

### ARCH-REV-008 — Atomic Chrome establishment closes DR-006; cumulative design passes

- Canonical design review report: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/design-review-report.md`
- Review round and trigger: Round 8; `SR-009` re-review after `ARCH-REV-007/DR-006/PREM-004` returned the cumulative `SR-008` design solely for the readiness-before-promotion ownership gap.
- Triggering role, report path, and finding IDs: `solution_designer`; `solution-revision-record.md` / `SR-009`; prior finding `DR-006`.
- Relevant solution revision IDs: `SR-001` through `SR-009`; `SR-009` is the current correction and preserves all other `SR-008` decisions.
- Prior authoritative decision: `Fail / Design Impact`
- Current authoritative decision: `Pass`
- What changed in the review result or what baseline was established: Verified that every supported caller now acquires the same per-port establishment gate before authoritative readiness classification. A ready endpoint under an otherwise-unheld gate returns `DURABLE_EXISTING` with no abort authority. An unavailable endpoint returns `PENDING_OWNED` while retaining the gate and exact process-group authority through Playwright connection/first-context success. `promote()` clears abort authority before unlock; `abort()` terminates/reaps only the exact group before unlock. Waiting callers cannot probe/classify/connect while a live owner remains abort-capable and make a fresh decision only after the terminal transition. The design also makes acquisition async/cancellable, prevents child descriptor inheritance, keeps lock-file presence non-semantic, and requires deterministic abort/promotion interleavings. Direct arguments, module allocation, clean dependency removal, no-vendoring, generic naming, locator/bootstrap, application/adapters, and all earlier findings remain unchanged and passing.

#### Prior Finding Resolution

| Finding ID | Prior Status | Current Status | Related Revision References | Verification Evidence |
| --- | --- | --- | --- | --- |
| `DR-006` | Open | Resolved | `SR-009`, `ARCH-REV-007`, `PREM-004` | `requirements.md` `BEH-011`/`REQ-015`/`AC-015`; `design-spec.md` owned-runtime state table, `DS-005`, boundaries, interface, sequence, A/B interleaving example, and implementation guidance; `cli-conversion-analysis.md` runtime ownership/atomic establishment decision and evidence plan all require gate-before-probe and gate-through-promote-or-abort. |

- New or remaining finding IDs: None. `DR-001`–`DR-005` remain resolved.
- Material classification changes: The prior `Design Impact` blocker is resolved; no failure classification applies to this passing result.
- Recommended recipient: `implementation_engineer`
- Remaining risks or uncertainty: Implementation must prove secure/no-follow owner-only gate creation, async retry/cancellation, non-inherited descriptors, exact process-group cleanup/reap, deterministic `PREM-004` interleavings, executable/CDP behavior, real durable-existing and owned-launch journeys, direct-argument fresh-agent use, frozen dependency removal, and complete source/API-E2E/delivery re-entry. These are explicit validation risks rather than remaining design gaps.
