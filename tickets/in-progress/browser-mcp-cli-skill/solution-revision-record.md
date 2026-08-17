# Solution Revision Record

The current `requirements.md`, `investigation-notes.md`, `design-spec.md`, and `cli-conversion-analysis.md` are authoritative. This record indexes completed solution rounds and does not replace them.

## Revision Index

| Revision ID | Triggering Role / Report / Round | Finding IDs | Classification | Result |
| --- | --- | --- | --- | --- |
| `SR-001` | solution_designer initial architecture handoff | N/A | `Initial Baseline` | Requirements refined and approved; portable CLI+skill/shared-core design ready for architecture review |
| `SR-002` | architecture_reviewer / `design-review-report.md` / round 1 (`ARCH-REV-001`) | `DR-001`–`DR-004` | `Design Impact` | Launcher failure ownership, MCP operational surfaces, and artifact coherence corrected; ready for architecture re-review |
| `SR-003` | architecture_reviewer / `design-review-report.md` / round 2 (`ARCH-REV-002`) | `DR-004` | `Design Impact` | Final AC-012 scenario-intent wording aligned to the mandatory retained-MCP decision; ready for architecture re-review |

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
