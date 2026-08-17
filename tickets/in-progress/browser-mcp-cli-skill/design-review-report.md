# Design Review Report

## Review Round Meta

- Upstream Requirements Doc: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/requirements.md`
- Upstream Investigation Notes: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/investigation-notes.md`
- Reviewed Design Spec: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/design-spec.md`
- Supplemental Task Artifacts Reviewed: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/cli-conversion-analysis.md`
- Solution Revision Record Reviewed: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/solution-revision-record.md`
- Relevant Solution Revision IDs: `SR-001`, `SR-002`, `SR-003`
- Architecture Review Revision Record: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/architecture-review-revision-record.md`
- Current Architecture Review Revision ID: `ARCH-REV-003`
- Current Review Round: `3`
- Trigger: Re-review of `SR-003` after the remaining `ARCH-REV-002` package-coherence finding `DR-004`.
- Prior Review Round Reviewed: Round 2 / `ARCH-REV-002` / `Fail`
- Latest Authoritative Round: `3`
- Current-State Evidence Basis: Current requirements, investigation notes, design spec, conversion supplement, `SR-003`, prior review artifacts, and the same base-code/source/probe evidence confirmed in round 1 at commit `9643f1459246c9f003196afc146a7f783eda6208`.

## Upstream Behavior And Production-Path Basis Confirmation

- Overall Basis Status (`Confirmed`/`Contradicted`/`Blocked`): `Confirmed`
- Approved requirements / intended behavior understood: Yes. The project remains one relocatable skill/runtime bundle with a loader-relative launcher, one authoritative browser application boundary, daemon-free target identity, task JSON CLI, and retained thin MCP.
- Relevant existing behavior and evidence confirmed: Yes. The current stdout-sensitive MCP wrapper, streamable-HTTP default bind, browser ownership, tool inventory, file policy, and CDP target continuity evidence remain applicable.
- Approved change, preserved behavior, and outside scope understood: Yes. `SR-002` adds a launcher readiness handoff, loopback HTTP default, explicit non-loopback warning, and clean MCP wrapper rename without adding auth/TLS/proxy machinery or a compatibility path. `SR-003` aligns the final `AC-012` scenario-intent row without changing approved behavior or architecture.
- Remaining material ambiguity, if any: None.

| Behavior ID | Kind | Design Alignment With Approved Intent (`Pass`/`Fail`) | Approved Trigger / Contract And Current-State Evidence (`Pass`/`Fail`/`Unclear`) | Target Outcome / Path / Spine Coherence (`Pass`/`Fail`/`Unclear`) | Status (`Confirmed`/`Needs Correction`/`Unclear`) | Required Action |
| --- | --- | --- | --- | --- | --- | --- |
| `BEH-001` | Contract | Pass | Pass | Pass | Confirmed | None |
| `BEH-002` | User / Contract | Pass | Pass | Pass | Confirmed | None |
| `BEH-003` | Contract | Pass | Pass | Pass | Confirmed | None |
| `BEH-004` | Contract | Pass | Pass | Pass | Confirmed | None; `DR-001` is resolved. |
| `BEH-005` | User | Pass | Pass | Pass | Confirmed | None |
| `BEH-006` | User / Operational | Pass | Pass | Pass | Confirmed | None |
| `BEH-007` | Operational | Pass | Pass | Pass | Confirmed | None; `DR-002`, `DR-003`, and `DR-004` are resolved. |
| `BEH-008` | Operational / Contract | Pass | Pass | Pass | Confirmed | None; `DR-001` is resolved. |

## Supplemental Artifact Coherence Verdict

| Artifact | Purpose And Scope Are Clear? (`Pass`/`Fail`) | Linked To Relevant Core Artifacts? (`Pass`/`Fail`) | Internally Complete? (`Pass`/`Fail`) | Consistent With Related Core Artifacts? (`Pass`/`Fail`) | Status And Approval Applicability Are Clear? (`Pass`/`Fail`) | Required Action |
| --- | --- | --- | --- | --- | --- | --- |
| `cli-conversion-analysis.md` | Pass | Pass | Pass | Pass | Pass | None. The renamed root, resolved listing/ownership/output/script/MCP decisions, readiness handoff, and true residual risks are current. |

The investigation notes are current for round 3 and contain the canonical supplement inventory. `SR-003` replaces the final stale `AC-012` scenario-intent row with the mandatory retained-MCP validation scope, so `DR-004` is resolved across the cumulative package.

## Task Design Health Assessment Verdict

| Assessment Area | Result (`Pass`/`Fail`) | Evidence | Required Action |
| --- | --- | --- | --- |
| Assessment is present for the current task posture | Pass | Requirements and design classify the large change. | None |
| Root-cause classification is explicit and evidence-backed | Pass | MCP-owned operation bodies, process-local identity, import-time CWD mutation, page-creating initialization, and transport-centric placement support the classification. | None |
| Refactor needed now / no refactor needed / deferred decision is explicit | Pass | `Refactor needed now: Yes`. | None |
| Refactor decision is supported by the concrete design sections or residual-risk rationale | Pass | Application/runtime/policy/content boundaries, adapter files, launch spines, removals, and sequence are concrete. | None |

## Spine Inventory Verdict

| Spine ID | Scope | Spine Is Readable? (`Pass`/`Fail`) | Narrative Is Clear? (`Pass`/`Fail`) | Facade Vs Governing Owner Is Clear? (`Pass`/`Fail`/`N/A`) | Main Domain Subject Naming Is Clear? (`Pass`/`Fail`) | Ownership Is Clear? (`Pass`/`Fail`) | Off-Spine Concerns Stay Off Main Line? (`Pass`/`Fail`) | Verdict (`Pass`/`Fail`) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `DS-001` | CLI primary end-to-end | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| `DS-002` | MCP operation end-to-end | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| `DS-003` | Skill activation/bootstrap | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| `DS-004` | CLI return | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| `DS-005` | Browser runtime lifecycle | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| `DS-006` | Launcher bootstrap | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| `DS-007` | Artifact return | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| `DS-008` | Retained MCP launch/exposure | Pass | Pass | Pass | Pass | Pass | Pass | Pass |

## Boundary Encapsulation Verdict

| Boundary / Owner | Authoritative Public Entry Point Is Clear? (`Pass`/`Fail`) | Internal Owned Mechanisms Stay Internal? (`Pass`/`Fail`) | Caller Bypass Risk Is Controlled? (`Pass`/`Fail`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- |
| `BrowserApplication` | Pass | Pass | Pass | Pass | Both adapters depend only on the command boundary/contracts. |
| `BrowserRuntime.session()` | Pass | Pass | Pass | Pass | No-page connection, target resolution, and disconnect remain internal. |
| `ArtifactPolicy` | Pass | Pass | Pass | Pass | File inputs and outputs remain below both adapters. |
| `scripts/autobyteus-browser` | Pass | Pass | Pass | Pass | A private readiness token transfers stdout ownership exactly once. |
| MCP composition/configuration | Pass | Pass | Pass | Pass | Stdio launch and HTTP bind policy remain transport concerns and cannot bypass the application boundary. |

## Dependency Direction / Forbidden Shortcut Verdict

| Owner / Boundary | Allowed Dependencies Are Clear? (`Pass`/`Fail`) | Forbidden Shortcuts Are Explicit? (`Pass`/`Fail`) | Direction Is Coherent With Ownership? (`Pass`/`Fail`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- |
| Skill and CLI launcher | Pass | Pass | Pass | Pass | No vendor home, direct uv skill command, copied runtime, or unconditional `exec`. |
| CLI/MCP -> `BrowserApplication` | Pass | Pass | Pass | Pass | No adapter-to-runtime/page/policy bypass. |
| `BrowserApplication` -> runtime/policy/content | Pass | Pass | Pass | Pass | Ownership and encapsulation remain aligned. |
| MCP launch/config -> MCP adapter | Pass | Pass | Pass | Pass | Bind/launch configuration composes the adapter only. |
| Runtime -> brui/Playwright/CDP | Pass | Pass | Pass | Pass | Transport types and serializers stay out of runtime. |

## Interface Boundary Verdict

| Interface / API / Query / Command / Method | Subject Is Clear? (`Pass`/`Fail`) | Responsibility Is Singular? (`Pass`/`Fail`) | Identity Shape Is Explicit? (`Pass`/`Fail`) | Generic Boundary Risk (`Low`/`Medium`/`High`) | Verdict (`Pass`/`Fail`) |
| --- | --- | --- | --- | --- | --- |
| `BrowserApplication` command methods | Pass | Pass | Pass | Low | Pass |
| `BrowserRuntime.session()` / `resolve_page(tab_id)` | Pass | Pass | Pass | Low | Pass |
| `attach_tab(url_contains,title_contains)` | Pass | Pass | Pass | Medium | Pass |
| `ArtifactPolicy.resolve_output(...)` | Pass | Pass | Pass | Low | Pass |
| CLI readiness handshake | Pass | Pass | Pass | Low | Pass |
| `McpRuntimeConfig.from_env()` | Pass | Pass | Pass | Low | Pass |

## Existing Capability / Subsystem Reuse Verdict

| Need / Concern | Existing Capability Area Was Checked? (`Pass`/`Fail`) | Reuse / Extension Decision Is Sound? (`Pass`/`Fail`) | New Support Piece Is Justified? (`Pass`/`Fail`/`N/A`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- |
| Chrome launch/CDP connection | Pass | Pass | Pass | Pass | Reuse `BrowserManager` behind `BrowserRuntime`, not page-creating `UIIntegrator`. |
| Cleaning/DOM/script behavior | Pass | Pass | Pass | Pass | Existing logic moves under focused transport-neutral owners. |
| CLI/envelope and uv-launch patterns | Pass | Pass | Pass | Pass | Readiness adapts rather than blindly copies the stateless reference. |
| Existing MCP stdio launcher | Pass | Pass | N/A | Pass | Rename/update preserves the supported capability without a forwarding wrapper. |

## Subsystem / Capability-Area Allocation Verdict

| Subsystem / Capability Area | Ownership Allocation Is Clear? (`Pass`/`Fail`) | Reuse / Extend / Create-New Decision Is Sound? (`Pass`/`Fail`) | Supports The Right Spine Owners? (`Pass`/`Fail`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- |
| Portable skill bundle | Pass | Pass | Pass | Pass | One project is the skill and runtime. |
| Browser application/runtime/content/policy | Pass | Pass | Pass | Pass | Governing and off-spine owners are coherent. |
| CLI adapter/bootstrap | Pass | Pass | Pass | Pass | Syntax/output and pre-CLI bootstrap remain distinct. |
| MCP adapter/config/bootstrap | Pass | Pass | Pass | Pass | Tools, bind policy, composition, and stdio launcher have explicit owners. |

## Reusable Owned Structures Verdict

| Repeated Structure / Logic | Extraction Need Was Evaluated? (`Pass`/`Fail`) | Shared File Choice Is Sound? (`Pass`/`Fail`/`N/A`) | Ownership Of Shared Structure Is Clear? (`Pass`/`Fail`/`N/A`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- |
| Tab/result/artifact contracts | Pass | Pass | Pass | Pass | Tight canonical shapes serve both adapters. |
| Stable browser failures | Pass | Pass | Pass | Pass | Public codes replace exception-class contracts. |
| Target lookup | Pass | Pass | Pass | Pass | One runtime resolver replaces aliases. |
| Shared input policy | Pass | Pass | Pass | Pass | Invariants remain below adapters. |
| MCP runtime configuration | Pass | Pass | Pass | Pass | Transport/host/port/exposure assessment has one owner. |

## Shared Structure / Data Model Tightness Verdict

| Shared Structure / Type / Schema | One Clear Meaning Per Field? (`Pass`/`Fail`) | Redundant Attributes Removed? (`Pass`/`Fail`) | Overlapping Representation Risk Is Controlled? (`Pass`/`Fail`) | Shared Core Vs Specialized Variant / Composition Decision Is Sound? (`Pass`/`Fail`/`N/A`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `TabSummary` | Pass | Pass | Pass | N/A | Pass | Process-local metadata is removed. |
| `ArtifactResult` | Pass | Pass | Pass | Pass | Inline and artifact results are explicit variants. |
| `BrowserError` | Pass | Pass | Pass | N/A | Transport-neutral error semantics remain tight. |
| CLI envelope/readiness marker | Pass | Pass | Pass | Pass | The marker transfers ownership only and never duplicates/parses the payload. |
| DOM element result | Pass | Pass | Pass | N/A | Selector and snapshot-local label meanings remain distinct. |

## File Responsibility Mapping Verdict

| File | Responsibility Is Singular And Clear? (`Pass`/`Fail`) | Responsibility Matches The Intended Owner/Boundary? (`Pass`/`Fail`) | Responsibilities Were Re-Tightened After Shared-Structure Extraction? (`Pass`/`Fail`/`N/A`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- |
| `application.py`, `runtime.py` | Pass | Pass | Pass | Pass | Governing command and lifecycle responsibilities stay separate. |
| `contracts.py`, `errors.py`, `policy.py` | Pass | Pass | Pass | Pass | Shared shapes and effect policy are focused. |
| `cleaning.py`, `dom_snapshot.py`, `script.py` | Pass | Pass | Pass | Pass | Content concerns remain specialized. |
| `cli.py` | Pass | Pass | Pass | Pass | Readiness, syntax, envelope, stderr, and exit behavior are one adapter boundary. |
| `scripts/autobyteus-browser` | Pass | Pass | N/A | Pass | Self-location, frozen uv, readiness gate, and bootstrap envelope are actionable. |
| `mcp/config.py`, `mcp/server.py`, `mcp/tools/*.py` | Pass | Pass | Pass | Pass | Configuration, composition, and schemas are separated. |
| `scripts/autobyteus-browser-mcp` | Pass | Pass | N/A | Pass | Clean stdio facade successor; protocol stdout stays reserved. |

## Subsystem / Folder / File Placement Verdict

| Path / Item | Target Placement Is Clear? (`Pass`/`Fail`) | Folder Matches Owning Boundary? (`Pass`/`Fail`) | Mixed-Layer Or Over-Split Risk (`Low`/`Medium`/`High`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- |
| `autobyteus-browser/` complete bundle | Pass | Pass | Low | Pass | Whole-project skill packaging is coherent and relocatable. |
| `src/autobyteus_browser/` | Pass | Pass | Low | Pass | Capability namespace replaces the transport namespace. |
| `src/autobyteus_browser/mcp/` | Pass | Pass | Low | Pass | FastMCP config/server/tools remain secondary. |
| `scripts/` | Pass | Pass | Low | Pass | CLI and MCP launchers are both explicitly mapped. |
| `tests/unit`, `tests/integration` | Pass | Pass | Low | Pass | Evidence-scope split remains proportionate. |

## Removal / Decommission Completeness Verdict

| Item / Area | Redundant / Obsolete Piece To Remove Is Named? (`Pass`/`Fail`) | Replacement Owner / Structure Is Clear? (`Pass`/`Fail`/`N/A`) | Removal / Decommission Scope Is Explicit? (`Pass`/`Fail`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- |
| Numeric tab registry and aliases | Pass | Pass | Pass | Pass | No persisted/compatibility map. |
| Tool-owned browser logic | Pass | Pass | Pass | Pass | Moves behind `BrowserApplication`. |
| `close_browser` / global kill path | Pass | Pass | Pass | Pass | Exact removal remains required. |
| Old root/package namespace | Pass | Pass | Pass | Pass | No forwarding package/directory. |
| Import-time CWD mutation/permissive utils | Pass | Pass | Pass | Pass | Explicit workspace/policy replaces them. |
| `scripts/browser_mcp_stdio.sh` and old active references | Pass | Pass | Pass | Pass | Renamed/updated without forwarding. |
| HTTP `0.0.0.0` implicit default | Pass | Pass | Pass | Pass | Loopback becomes default; explicit operator selection remains warned. |

## Legacy / Backward-Compatibility Verdict

| Area | Compatibility Wrapper / Dual-Path / Legacy Retention Exists? (`Yes`/`No`) | Clean-Cut Removal Is Explicit? (`Pass`/`Fail`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- |
| Numeric IDs | No | Pass | Pass | Target IDs replace aliases. |
| Python namespace/root | No | Pass | Pass | No forwarding source path. |
| MCP tool business logic | No | Pass | Pass | Retained MCP delegates to the application boundary. |
| Old MCP wrapper | No | Pass | Pass | Capability is renamed/updated, not wrapped. |
| Global browser close | No | Pass | Pass | Removed rather than hidden. |

## Persisted-Data Transition Verdict (When Applicable)

| Area / Stored Subject | Approved Decision | Representative Reader / Semantic / Invariant Evidence Is Sufficient? (`Pass`/`Fail`) | Direct Use, Rebuild, Or Migration Choice Is Proportionate? (`Pass`/`Fail`) | Migration Safety Is Complete If Required? (`Pass`/`Fail`/`N/A`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Chrome profile/site data and artifact files | `Not Affected` | Pass | Pass | N/A | Pass | Chrome/Playwright readers stay unchanged; process-local IDs are not stored data. |

## Change / Refactor Safety Verdict

| Area | Sequence Is Realistic? (`Pass`/`Fail`) | Temporary Seams Are Explicit? (`Pass`/`Fail`) | Cleanup / Removal Is Explicit? (`Pass`/`Fail`) | Verdict (`Pass`/`Fail`) |
| --- | --- | --- | --- | --- |
| Namespace/root rename and shared-core extraction | Pass | Pass | Pass | Pass |
| Runtime identity/lifecycle replacement | Pass | Pass | Pass | Pass |
| CLI/skill bootstrap | Pass | Pass | Pass | Pass |
| Retained MCP refactor | Pass | Pass | Pass | Pass |

## Example Adequacy Verdict

| Topic / Area | Example Was Needed? (`Yes`/`No`) | Example Is Present And Clear? (`Pass`/`Fail`/`N/A`) | Bad / Avoided Shape Is Explained When Helpful? (`Pass`/`Fail`/`N/A`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- |
| Vendor-neutral skill invocation | Yes | Pass | Pass | Pass | Placeholder semantics remain explicit. |
| Shared application boundary | Yes | Pass | Pass | Pass | Both adapters call the same methods. |
| Target identity and safe artifacts | Yes | Pass | Pass | Pass | Good/rejected shapes are concrete. |
| Bootstrap failure after uv begins | Yes | Pass | Pass | Pass | Pseudocode shows ready/no-ready and no-double-envelope branches. |
| Retained MCP exposure | Yes | Pass | Pass | Pass | Loopback default and explicit warned remote bind are concrete. |

## Material Premise Validation (Only When Needed)

### `PREM-001` — Frozen `uv` setup or runtime preparation fails after launcher prechecks and before the Python CLI starts

- Related approved requirement or established contract: `REQ-004`, `REQ-007`, `REQ-010`; `AC-003`, `AC-004`.
- Relevant behavior ID(s): `BEH-004`, `BEH-008`.
- Initiating basis kind: `Contract`
- Independent product-supported initiating trigger or applicable governing contract: A coding agent activates the loaded browser skill and invokes the documented bundled launcher; the approved contract explicitly includes wrapper/runtime dependency failure.
- Support evidence: `SKILL.md` is the exposed surface and `bash "$SKILL_DIR/scripts/autobyteus-browser" health-check` is the supported action.
- Forward current or approved target production caller/event path that exercises the initiating basis and reaches the claimed state: `Agent -> SKILL.md -> Bash launcher -> prechecks pass -> quiet frozen uv -> environment/import fails before CLI ready marker -> launcher no-ready branch`.
- Lifecycle preconditions and material consequence at the claimed point: Python has not taken stdout ownership. Captured stdout is redirected to stderr; the launcher emits one fixed bootstrap envelope and exits `3`.
- Reachability: `Reachable`
- Review consequence / proportionate response: `Resolved by SR-002`. The readiness token, captured stdout, fixed no-ready result, forward-only ready branch, cleanup, and validation matrix close `DR-001` without a daemon or installer.

### `PREM-002` — A current MCP consumer launches the server through the documented stdio wrapper after the root/package rename

- Related approved requirement or established contract: `BEH-007`, `REQ-011`, `AC-012` retain stdio MCP while removing old paths cleanly.
- Relevant behavior ID(s): `BEH-007`.
- Initiating basis kind: `User`
- Independent product-supported initiating trigger or applicable governing contract: A user configures a GUI coding agent using the project's documented MCP wrapper and starts the browser MCP.
- Support evidence: Current `browser-mcp/README.md` exposes `scripts/browser_mcp_stdio.sh` as the supported command.
- Forward current or approved target production caller/event path that exercises the initiating basis and reaches the claimed state: `GUI MCP configuration -> renamed scripts/autobyteus-browser-mcp -> quiet frozen uv -> browser-mcp-server -> FastMCP stdio`.
- Lifecycle preconditions and material consequence at the claimed point: The root/namespace is renamed; the new wrapper points directly at the new root/entry, preserves protocol stdout, and the old path is removed.
- Reachability: `Reachable`
- Review consequence / proportionate response: `Resolved by SR-002`. The explicit file/removal/docs/coverage mapping closes `DR-003` without compatibility forwarding.

## Unresolved Approved-Behavior Or Current-State Gaps

None.

## Review Decision

`Pass` — The approved behavior basis is confirmed, `SR-002` and `SR-003` resolve `DR-001`–`DR-004`, the cumulative package is coherent, and the design is ready for implementation.

## Findings

None. `DR-001`–`DR-004` are resolved; the resolution history remains in `architecture-review-revision-record.md`.

## Classification

`N/A` — no failure classification applies to this passing review.

## Recommended Recipient

`implementation_engineer`

## Residual Risks

- CDP target discovery remains Chromium-specific and partly experimental; frozen dependencies and supported-platform real-browser tests remain required.
- Independent clients can race intentionally on one tab; the skill must serialize its own observe/act/verify workflow.
- `brui_core` auto-launch behavior, readiness temporary-file behavior, and renamed wrapper stdout isolation remain implementation-validation risks.
- Explicit non-loopback MCP binds remain unauthenticated and operator-protected; the design correctly does not invent an auth subsystem.
- The broad root/namespace rename still requires active-reference removal checks.

## Latest Authoritative Result

- Review Decision: `Pass`
- Material-Premise Gate (`Pass`/`Fail`/`Blocked`): `Pass`
- Notes: `ARCH-REV-003` is authoritative. `DR-001`–`DR-004` are resolved, no new findings remain, and the cumulative `SR-001`–`SR-003` package may proceed to implementation.
