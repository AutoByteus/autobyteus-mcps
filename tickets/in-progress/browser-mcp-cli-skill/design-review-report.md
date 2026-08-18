# Design Review Report

## Review Round Meta

- Upstream Requirements Doc: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/requirements.md`
- Upstream Investigation Notes: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/investigation-notes.md`
- Reviewed Design Spec: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/design-spec.md`
- Supplemental Task Artifacts Reviewed: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/cli-conversion-analysis.md`
- Solution Revision Record Reviewed: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/solution-revision-record.md`
- Relevant Solution Revision IDs: `SR-001` through `SR-009`; `SR-009` is the current narrow correction to cumulative `SR-008`.
- Architecture Review Revision Record: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/architecture-review-revision-record.md`
- Current Architecture Review Revision ID: `ARCH-REV-008`
- Current Review Round: `8`
- Trigger: `SR-009` re-review after `ARCH-REV-007` returned the cumulative direct-argument/owned-runtime package solely for `DR-006` / `PREM-004`.
- Prior Review Round Reviewed: Round 7 / `ARCH-REV-007` / `Fail — Design Impact`.
- Latest Authoritative Round: `8`
- Relevant Triggering Downstream Evidence Reviewed: `IR-005`, `CRR-008`, the held `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/api-e2e-coverage-investigation.md`, current candidate source/tests, and the supplied `/Users/normy/autobyteus_org/brui_core` source/package evidence.
- Current-State Evidence Basis: Current canonical artifacts through `SR-009`; `ARCH-REV-007` and `PREM-004`; checkpointed generic candidate application/runtime/CLI source and tests; package/lock state; sibling runtime evidence; prior downstream history; and the held API/E2E reroute.

## Upstream Behavior And Production-Path Basis Confirmation

- Overall Basis Status (`Confirmed`/`Contradicted`/`Blocked`): `Confirmed`
- Approved requirements / intended behavior understood: Yes. The package preserves the generic portable skill, direct operation-specific CLI flags, exact advertised-file-relative launcher resolution, one application boundary, browser-owned target IDs, strict JSON, workspace safety, and retained thin MCP. It replaces the two-symbol `brui-core` dependency with an owned config/Chrome-establishment/Playwright-session package and now makes launch establishment atomic across supported processes.
- Relevant existing behavior and evidence confirmed: Yes. The current candidate already supplies the passing application, parser, target lookup, and client-only disconnect seams. The sibling source confirms the narrow external dependency and the unsafe/unneeded manager/UI/clipboard/singleton/global-kill breadth being removed. `PREM-004` remains a reachable two-caller lifecycle that the corrected design must address.
- Approved change, preserved behavior, and outside scope understood: Yes. `SR-009` changes only the owned runtime's per-port gate/lease lifetime. Every supported caller gates before authoritative readiness classification; a new launch remains gated through initial Playwright connection/first-context promotion or exact abort. No daemon, browser registry, PID marker, public command, new adapter responsibility, or broader browser behavior is added.
- Remaining material ambiguity, if any: None. The terminal lease states, gate order, cleanup order, caller blocking point, owner-death boundary, security properties, and deterministic validation branches are explicit.

| Behavior ID | Kind | Design Alignment With Approved Intent (`Pass`/`Fail`) | Approved Trigger / Contract And Current-State Evidence (`Pass`/`Fail`/`Unclear`) | Target Outcome / Path / Spine Coherence (`Pass`/`Fail`/`Unclear`) | Status (`Confirmed`/`Needs Correction`/`Unclear`) | Required Action |
| --- | --- | --- | --- | --- | --- | --- |
| `BEH-001` | Contract | Pass | Pass | Pass | Confirmed | None |
| `BEH-002` | User / Contract | Pass | Pass | Pass | Confirmed | None |
| `BEH-003` | Contract | Pass | Pass | Pass | Confirmed | None |
| `BEH-004` | Contract | Pass | Pass | Pass | Confirmed | None; `DR-001` remains resolved. |
| `BEH-005` | User | Pass | Pass | Pass | Confirmed | None |
| `BEH-006` | User / Operational | Pass | Pass | Pass | Confirmed | None |
| `BEH-007` | Operational | Pass | Pass | Pass | Confirmed | None; retained MCP thinness/exposure remain unchanged. |
| `BEH-008` | Operational / Contract | Pass | Pass | Pass | Confirmed | None; launcher/bootstrap ownership remains unchanged. |
| `BEH-009` | User / Operational / Contract | Pass | Pass | Pass | Confirmed | None; generic vocabulary remains coherent. |
| `BEH-010` | User / Contract | Pass | Pass | Pass | Confirmed | None; direct `--script`/`--arg-json`, bounded alternate sources, and `(arg) =>` remain aligned. |
| `BEH-011` | Operational / Contract | Pass | Pass | Pass | Confirmed | None; `SR-009` closes `DR-006` through one gated establish/promote-or-abort transition. |

## Supplemental Artifact Coherence Verdict

| Artifact | Purpose And Scope Are Clear? (`Pass`/`Fail`) | Linked To Relevant Core Artifacts? (`Pass`/`Fail`) | Internally Complete? (`Pass`/`Fail`) | Consistent With Related Core Artifacts? (`Pass`/`Fail`) | Status And Approval Applicability Are Clear? (`Pass`/`Fail`) | Required Action |
| --- | --- | --- | --- | --- | --- | --- |
| `cli-conversion-analysis.md` | Pass | Pass | Pass | Pass | Pass | None. It matches `REQ-015`, `AC-015`, `DS-005`, the two availability states, terminal ordering, and the deterministic two-caller validation. |

The investigation inventory is current and maps the supplement through `REQ-001`–`REQ-015` and `AC-001`–`AC-015`. Historical `SR-008` text remains historical; current status/routing consistently identify `SR-009` and `DR-006` closure. The held API/E2E artifact remains downstream reroute history rather than completed current evidence.

## Task Design Health Assessment Verdict

| Assessment Area | Result (`Pass`/`Fail`) | Evidence | Required Action |
| --- | --- | --- | --- |
| Assessment is present for the current task posture | Pass | Requirements and design identify the cumulative larger requirement and narrow `SR-009` correction. | None |
| Root-cause classification is explicit and evidence-backed | Pass | Original transport ownership, current two-symbol dependency, and the reachable readiness-before-promotion race are evidenced. | None |
| Refactor needed now / no refactor needed / deferred decision is explicit | Pass | The full owned-runtime refactor remains required; `SR-009` changes only the establishment gate/lease transition. | None |
| Refactor decision is supported by the concrete design sections or residual-risk rationale | Pass | State table, lifecycle spine, boundaries, interface, file allocation, sequence, examples, and validation all implement the decision. | None |

## Spine Inventory Verdict

| Spine ID | Scope | Spine Is Readable? (`Pass`/`Fail`) | Narrative Is Clear? (`Pass`/`Fail`) | Facade Vs Governing Owner Is Clear? (`Pass`/`Fail`/`N/A`) | Main Domain Subject Naming Is Clear? (`Pass`/`Fail`) | Ownership Is Clear? (`Pass`/`Fail`) | Off-Spine Concerns Stay Off Main Line? (`Pass`/`Fail`) | Verdict (`Pass`/`Fail`) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `DS-001` | CLI primary end-to-end | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| `DS-002` | MCP primary end-to-end | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| `DS-003` | Skill projection/resource/bootstrap | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| `DS-004` | CLI return/agent continuation | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| `DS-005` | Owned browser runtime lifecycle | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| `DS-006` | Launcher bootstrap | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| `DS-007` | Artifact return | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| `DS-008` | Retained MCP launch/exposure | Pass | Pass | Pass | Pass | Pass | Pass | Pass |

`DS-005` now spans the actual ownership transition: in-process serialization -> per-port gate -> authoritative probe -> durable-existing release or pending-owned launch -> gated connect/context -> promote-before-unlock or abort-cleanup-before-unlock -> session/target work -> client-only disconnect.

## Boundary Encapsulation Verdict

| Boundary / Owner | Authoritative Public Entry Point Is Clear? (`Pass`/`Fail`) | Internal Owned Mechanisms Stay Internal? (`Pass`/`Fail`) | Caller Bypass Risk Is Controlled? (`Pass`/`Fail`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- |
| `BrowserApplication` | Pass | Pass | Pass | Pass | CLI and MCP remain above one authoritative operation boundary. |
| `BrowserRuntime.session()` | Pass | Pass | Pass | Pass | It drives pending availability through connection/context and a terminal lease transition. |
| `ChromeLauncher.ensure_available()` / `ChromeAvailability` | Pass | Pass | Pass | Pass | All callers gate before authoritative probe; only pending-owned has abort authority; no ready-path bypass remains. |
| `ArtifactPolicy` | Pass | Pass | Pass | Pass | Workspace/file effects remain application-owned. |
| `scripts/browser` | Pass | Pass | Pass | Pass | Readiness transfers stdout ownership exactly once. |
| Runtime projection -> `SKILL.md` -> launcher | Pass | Pass | Pass | Pass | Exact-locator-relative resolution remains sound. |
| MCP composition/configuration | Pass | Pass | Pass | Pass | Both transports remain thin and cannot bypass application/runtime authority. |
| Capability naming policy | Pass | Pass | Pass | Pass | Generic identifiers and provenance exclusions remain explicit. |

## Dependency Direction / Forbidden Shortcut Verdict

| Owner / Boundary | Allowed Dependencies Are Clear? (`Pass`/`Fail`) | Forbidden Shortcuts Are Explicit? (`Pass`/`Fail`) | Direction Is Coherent With Ownership? (`Pass`/`Fail`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- |
| Skill/launcher -> CLI | Pass | Pass | Pass | Pass | No MCP, vendor home, path scan, manual setup, or copied runtime. |
| CLI/MCP -> `BrowserApplication` | Pass | Pass | Pass | Pass | Adapters do not reach runtime internals. |
| `BrowserApplication` -> owned runtime/policy/content | Pass | Pass | Pass | Pass | Application uses the runtime facade. |
| Owned runtime -> Playwright/stdlib/Chrome | Pass | Pass | Pass | Pass | `brui-core`, sibling paths, manager/UI/clipboard/singleton/global kill, pre-gate probes, and early pending unlock are forbidden. |
| MCP launch/config -> MCP adapter | Pass | Pass | Pass | Pass | Bind/launch policy remains transport-owned. |
| Capability package -> active facades | Pass | Pass | Pass | Pass | The `SR-006` generic boundary stays clean. |

## Interface Boundary Verdict

| Interface / API / Query / Command / Method | Subject Is Clear? (`Pass`/`Fail`) | Responsibility Is Singular? (`Pass`/`Fail`) | Identity Shape Is Explicit? (`Pass`/`Fail`) | Generic Boundary Risk (`Low`/`Medium`/`High`) | Verdict (`Pass`/`Fail`) |
| --- | --- | --- | --- | --- | --- |
| `BrowserApplication.*` command methods | Pass | Pass | Pass | Low | Pass |
| CLI `run-script` input-source contract | Pass | Pass | Pass | Low | Pass |
| `BrowserRuntime.session()` / `BrowserSession` | Pass | Pass | Pass | Low | Pass |
| `BrowserRuntimeConfig.from_env()` | Pass | Pass | Pass | Low | Pass |
| `ChromeLauncher.ensure_available()` / `ChromeAvailability` | Pass | Pass | Pass | Low | Pass |
| `BrowserRuntime.resolve_page(tab_id)` | Pass | Pass | Pass | Low | Pass |
| `ArtifactPolicy.resolve_output(...)` | Pass | Pass | Pass | Low | Pass |
| CLI readiness handshake | Pass | Pass | Pass | Low | Pass |
| `McpRuntimeConfig.from_env()` | Pass | Pass | Pass | Low | Pass |

`DURABLE_EXISTING` and `PENDING_OWNED` now have disjoint meanings and authority. The latter carries the gate/process handle until exactly one ordered terminal transition; the former carries no kill authority.

## Existing Capability / Subsystem Reuse Verdict

| Need / Concern | Existing Capability Area Was Checked? (`Pass`/`Fail`) | Reuse / Extension Decision Is Sound? (`Pass`/`Fail`) | New Support Piece Is Justified? (`Pass`/`Fail`/`N/A`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- |
| Application/target core | Pass | Pass | N/A | Pass | Preserve the passing candidate application, target lookup, and parser. |
| Chrome config/launch/CDP connection | Pass | Pass | Pass | Pass | Focused ownership replaces two external symbols and excludes unrelated policy/transitives. |
| Cleaning/DOM/script behavior | Pass | Pass | N/A | Pass | Existing focused modules remain reusable. |
| CLI/envelope and launcher patterns | Pass | Pass | Pass | Pass | Existing readiness-gated bootstrap remains. |
| MCP stdio/HTTP adapters | Pass | Pass | N/A | Pass | Generic thin adapters and exposure policy remain. |

## Subsystem / Capability-Area Allocation Verdict

| Subsystem / Capability Area | Ownership Allocation Is Clear? (`Pass`/`Fail`) | Reuse / Extend / Create-New Decision Is Sound? (`Pass`/`Fail`) | Supports The Right Spine Owners? (`Pass`/`Fail`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- |
| Portable skill bundle | Pass | Pass | Pass | Pass | Procedure and runtime remain one relocatable bundle. |
| Browser application | Pass | Pass | Pass | Pass | Governing operation owner remains unchanged. |
| Owned browser runtime | Pass | Pass | Pass | Pass | Config, Chrome establishment, and Playwright session responsibilities are explicit and coordinated. |
| Browser content/policy | Pass | Pass | Pass | Pass | Existing off-spine owners stay focused. |
| CLI and MCP adapters | Pass | Pass | Pass | Pass | Both remain thin. |
| Coverage | Pass | Pass | Pass | Pass | Unit, deterministic interleaving, package, real runtime, and fresh-agent scopes are proportionate. |

## Reusable Owned Structures Verdict

| Repeated Structure / Logic | Extraction Need Was Evaluated? (`Pass`/`Fail`) | Shared File Choice Is Sound? (`Pass`/`Fail`/`N/A`) | Ownership Of Shared Structure Is Clear? (`Pass`/`Fail`/`N/A`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- |
| Tab/result/artifact contracts | Pass | Pass | Pass | Pass | Tight shared application shapes remain. |
| Stable errors | Pass | Pass | Pass | Pass | Both adapters retain one taxonomy. |
| Target lookup | Pass | Pass | Pass | Pass | `runtime/session.py` is the one owner. |
| Runtime config | Pass | Pass | Pass | Pass | Immutable config replaces the external mutable dictionary. |
| Chrome establishment/availability | Pass | Pass | Pass | Pass | `chrome_launcher.py` owns the gate/process lease; `session.py` supplies the success/failure signal for its terminal transition. |

## Shared Structure / Data Model Tightness Verdict

| Shared Structure / Type / Schema | One Clear Meaning Per Field? (`Pass`/`Fail`) | Redundant Attributes Removed? (`Pass`/`Fail`) | Overlapping Representation Risk Is Controlled? (`Pass`/`Fail`) | Shared Core Vs Specialized Variant / Composition Decision Is Sound? (`Pass`/`Fail`/`N/A`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `TabSummary` | Pass | Pass | Pass | N/A | Pass | Browser-owned target identity remains singular. |
| `ArtifactResult` | Pass | Pass | Pass | Pass | Pass | Inline/artifact variants remain explicit. |
| `BrowserError` | Pass | Pass | Pass | N/A | Pass | Stable transport-neutral failures remain. |
| CLI envelope/readiness marker | Pass | Pass | Pass | Pass | Pass | Payload and bootstrap ownership remain distinct. |
| `ChromeAvailability` state | Pass | Pass | Pass | Pass | Pass | Durable-existing has no abort authority; pending-owned holds gate plus exact process authority until promote or abort. |

## File Responsibility Mapping Verdict

| File | Responsibility Is Singular And Clear? (`Pass`/`Fail`) | Responsibility Matches The Intended Owner/Boundary? (`Pass`/`Fail`) | Responsibilities Were Re-Tightened After Shared-Structure Extraction? (`Pass`/`Fail`/`N/A`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- |
| `SKILL.md`, active READMEs, contract tests | Pass | Pass | N/A | Pass | Direct argument guidance is a bounded procedure/contract delta. |
| `application.py` | Pass | Pass | Pass | Pass | Application authority is unchanged. |
| `runtime/config.py` | Pass | Pass | Pass | Pass | Pure validated runtime settings. |
| `runtime/chrome_launcher.py` | Pass | Pass | Pass | Pass | Owns secure gate, authoritative probe, process launch/readiness, lease terminal transition, and exact failed-group cleanup. |
| `runtime/session.py` | Pass | Pass | Pass | Pass | Owns Playwright connection/context/targets and drives pending lease success/failure without taking process ownership. |
| `runtime/__init__.py` | Pass | Pass | N/A | Pass | Clean stable package facade. |
| `contracts.py`, `errors.py`, `policy.py` | Pass | Pass | Pass | Pass | Existing application/policy structures remain focused. |
| `cleaning.py`, `dom_snapshot.py`, `script.py` | Pass | Pass | Pass | Pass | Existing content concerns remain focused. |
| `cli.py`, `mcp/config.py`, `mcp/server.py`, `mcp/tools/*.py` | Pass | Pass | Pass | Pass | Public adapters/config remain thin. |
| `pyproject.toml`, `uv.lock` | Pass | Pass | N/A | Pass | Clean dependency removal/regeneration is explicit. |

## Subsystem / Folder / File Placement Verdict

| Path / Item | Target Placement Is Clear? (`Pass`/`Fail`) | Folder Matches Owning Boundary? (`Pass`/`Fail`) | Mixed-Layer Or Over-Split Risk (`Low`/`Medium`/`High`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- |
| `browser-automation/` complete bundle | Pass | Pass | Low | Pass | Whole-project skill packaging remains coherent. |
| `src/browser_automation/runtime/` | Pass | Pass | Low | Pass | Config, Chrome establishment, and Playwright session are meaningful distinct concerns. |
| `src/browser_automation/mcp/` | Pass | Pass | Low | Pass | FastMCP stays secondary. |
| `scripts/` | Pass | Pass | Low | Pass | Shell facades only. |
| `tests/unit`, `tests/integration` | Pass | Pass | Low | Pass | Evidence split is proportionate. |

## Removal / Decommission Completeness Verdict

| Item / Area | Redundant / Obsolete Piece To Remove Is Named? (`Pass`/`Fail`) | Replacement Owner / Structure Is Clear? (`Pass`/`Fail`/`N/A`) | Removal / Decommission Scope Is Explicit? (`Pass`/`Fail`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- |
| Numeric IDs/tool-owned operations/global close | Pass | Pass | Pass | Pass | Earlier clean removals remain explicit. |
| Old branded capability identifiers | Pass | Pass | Pass | Pass | `SR-006` clean-removal policy remains intact. |
| Complexity-preferred file/stdin guidance | Pass | Pass | Pass | Pass | Direct flags are normal; alternate sources stay optional. |
| `brui-core` metadata/lock/imports | Pass | Pass | Pass | Pass | Replaced by owned runtime modules. |
| `runtime.py` | Pass | Pass | Pass | Pass | Clean file-to-package move. |
| UI/clipboard/singleton/global-kill/unused transitives | Pass | N/A | Pass | Pass | Explicitly not copied or exposed. |
| `CHROME_DOWNLOAD_DIRECTORY` no-op | Pass | N/A | Pass | Pass | Removal and absence coverage are explicit. |

## Legacy / Backward-Compatibility Verdict

| Area | Compatibility Wrapper / Dual-Path / Legacy Retention Exists? (`Yes`/`No`) | Clean-Cut Removal Is Explicit? (`Pass`/`Fail`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- |
| Tab identity/global close | No | Pass | Pass | No alias map, daemon, or hidden global close. |
| Generic public naming | No | Pass | Pass | No branded launcher/import/env/schema fallback. |
| Direct input procedure | No | Pass | Pass | Optional sources are current alternatives, not compatibility routes. |
| Browser runtime dependency | No | Pass | Pass | No `brui_core` compatibility namespace, sibling path, or whole-library vendoring. |

## Persisted-Data Transition Verdict (When Applicable)

| Area / Stored Subject | Approved Decision | Representative Reader / Semantic / Invariant Evidence Is Sufficient? (`Pass`/`Fail`) | Direct Use, Rebuild, Or Migration Choice Is Proportionate? (`Pass`/`Fail`) | Migration Safety Is Complete If Required? (`Pass`/`Fail`/`N/A`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Chrome profile/cookies/local storage and workspace artifacts | `Not Affected` | Pass | Pass | N/A | Pass | Chrome and current artifact policy remain the readers/writers. |
| Process-local numeric aliases | `Not Affected` | Pass | Pass | N/A | Pass | Ephemeral and intentionally not migrated. |
| Per-port gate file | `Not Affected` / disposable coordination | Pass | Pass | N/A | Pass | Empty file presence is not state; no PID/browser registry is stored. |

## Change / Refactor Safety Verdict

| Area | Sequence Is Realistic? (`Pass`/`Fail`) | Temporary Seams Are Explicit? (`Pass`/`Fail`) | Cleanup / Removal Is Explicit? (`Pass`/`Fail`) | Verdict (`Pass`/`Fail`) |
| --- | --- | --- | --- | --- |
| Direct argument guidance/coverage delta | Pass | Pass | Pass | Pass |
| Runtime file-to-package/dependency replacement | Pass | Pass | Pass | Pass |
| Gate -> probe -> pending connect/context -> promote/abort | Pass | Pass | Pass | Pass |
| Code review -> held API/E2E -> delivery re-entry | Pass | Pass | Pass | Pass |

The corrected sequence specifies gate acquisition/timeout/cancellation, descriptor inheritance, authoritative probe placement, terminal ordering, exact process-group cleanup/reap, and fresh decisions by waiting callers.

## Example Adequacy Verdict

| Topic / Area | Example Was Needed? (`Yes`/`No`) | Example Is Present And Clear? (`Pass`/`Fail`/`N/A`) | Bad / Avoided Shape Is Explained When Helpful? (`Pass`/`Fail`/`N/A`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- |
| Direct `run-script` mapping | Yes | Pass | Pass | Pass | `(arg) => ...` plus `--arg-json` matches current normalization. |
| Locator-relative launcher | Yes | Pass | Pass | Pass | Placeholder remains design notation only. |
| Launcher readiness handoff | Yes | Pass | Pass | Pass | Pseudocode distinguishes bootstrap and CLI-owned output. |
| Owned runtime establishment | Yes | Pass | Pass | Pass | The A/B abort and promotion branches show B blocked before probe/classify/connect and a fresh post-terminal decision. |
| MCP exposure | Yes | Pass | Pass | Pass | Loopback default and non-loopback warning remain clear. |

## Material Premise Validation (Only When Needed)

### `PREM-004` — A second supported client can observe a newly ready endpoint before the launching client's initial connection is promoted

- Related approved requirement or established contract: `REQ-001`, `REQ-005`, `REQ-007`, `REQ-012`, `REQ-015`; `AC-001`, `AC-003`, `AC-008`, `AC-015`.
- Relevant behavior ID(s): `BEH-001`, `BEH-005`, `BEH-011`.
- Initiating basis kind: `System` / `Contract`
- Independent product-supported initiating trigger or applicable governing contract: Two independent supported CLI/MCP calls begin against the same valid configured loopback port while no CDP endpoint exists. Cross-process establishment and initial Playwright connection failure are explicit contracts.
- Support evidence: Independent CLI processes and retained MCP share one endpoint. `REQ-015`/`AC-015` require cross-process coordination, connection/context failure handling, successful-launch persistence, and unrelated-browser survival.
- Forward current or approved target production caller/event path that exercises the initiating basis and reaches the claimed state: Caller A acquires the gate, observes unavailable, launches, reaches `/json/version`, and remains pending before Playwright promotion. Caller B starts and waits before its probe. A then either aborts exact cleanup before unlock, after which B performs a fresh gated decision, or promotes/clears abort authority before unlock, after which B observes durable Chrome and attaches without kill authority.
- Lifecycle preconditions and material consequence at the claimed point: In `SR-008`, B could attach while A remained abort-capable and then lose Chrome. In `SR-009`, B cannot probe, classify, or connect during that interval, so no supported client can share still-abortable Chrome.
- Reachability: `Reachable`
- Review consequence / proportionate response: `Resolved by SR-009`. The existing per-port gate now spans the complete abortable establishment transition; deterministic abort and promotion interleavings verify the exact consequence without adding a daemon or registry.

Earlier `PREM-001` through `PREM-003` remain confirmed by unchanged launcher, MCP-wrapper, and skill-locator contracts and drive no new finding.

## Unresolved Approved-Behavior Or Current-State Gaps

None.

## Review Decision

`Pass` — `SR-009` closes `DR-006` by making Chrome establishment atomic through the only interval in which an owned process group remains abortable. The cumulative direct-argument and self-contained-runtime design is ready for implementation.

## Findings

None. `DR-006` is resolved; `DR-001` through `DR-005` remain resolved.

## Classification

`N/A` — no failure classification applies to this passing review.

## Recommended Recipient

`implementation_engineer`

## Residual Risks

- CDP target-info behavior remains Chromium-specific and partly experimental; frozen dependencies and real supported-platform regression remain required.
- Gate file permissions/no-follow creation, nonblocking async retry, descriptor inheritance, timeout/cancellation cleanup, executable discovery, readiness validation, and POSIX process-group/reap semantics remain implementation-validation risks covered by `AC-015`.
- An uncatchable owner death before Chrome becomes ready may leave an orphan attempt; the approved gate has no stale ownership and a later caller decides from current endpoint reality. No unsupported recovery registry should be added.
- Independent clients can still intentionally race page operations after establishment; the skill must serialize its own observe/act/verify loop.
- Direct argv remains bounded by Bash quoting and host argument limits; alternate sources stay exceptional rather than complexity-preferred.
- `brui-core`/unused-transitive removal and the generic naming boundary require source/package/lock/output scans plus regenerated frozen metadata.
- The held API/E2E investigation remains reroute history only; current runtime, direct-argument, and fresh-agent evidence must follow implementation and source review.
- Explicit non-loopback MCP remains unauthenticated and operator-protected; no auth subsystem should be added.

## Latest Authoritative Result

- Review Decision: `Pass`
- Material-Premise Gate (`Pass`/`Fail`/`Blocked`): `Pass`
- Notes: `ARCH-REV-008` is authoritative for `SR-009`. `DR-006` is resolved and no new finding exists. Route the cumulative package to `implementation_engineer`; the subsequent source review, held API/E2E, and delivery re-entry remain required before finalization.
