# Architecture Review Revision Record

The current `design-review-report.md` is authoritative. This record preserves the concise architecture-review history.

## Revision Index

| Revision ID | Review Round / Trigger | Related Solution Revision IDs | Prior Decision | Current Decision | Affected Finding IDs |
| --- | --- | --- | --- | --- | --- |
| `ARCH-REV-001` | Round 1 / initial solution package review | `SR-001` | N/A | `Fail` | `DR-001`, `DR-002`, `DR-003`, `DR-004` |
| `ARCH-REV-002` | Round 2 / `SR-002` correction re-review | `SR-002` | `Fail` | `Fail` | `DR-001`, `DR-002`, `DR-003`, `DR-004` |
| `ARCH-REV-003` | Round 3 / `SR-003` final coherence re-review | `SR-003` | `Fail` | `Pass` | `DR-004` |

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
