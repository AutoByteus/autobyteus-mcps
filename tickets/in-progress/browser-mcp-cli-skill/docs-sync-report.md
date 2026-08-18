# Docs Sync Report

## Scope

- Ticket: `browser-mcp-cli-skill`
- Trigger: Delivery re-entry for cumulative `SR-009` after architecture pass `ARCH-REV-008`, implementation/source pass `IR-006`/`CRR-009`, API/E2E pass `API-REV-004`, and proportional durable test-code pass `CRR-010`.
- Bootstrap base reference: `origin/main` at `9643f1459246c9f003196afc146a7f783eda6208`.
- Integrated base reference used for docs sync: Latest fetched `origin/main` at `7d0ff82191d045402f8ec84405a56fccba1c969a`, integrated by merge into the ticket branch at `3c29f8b2e50edfe73b168be347774429ee2c86e7` after candidate safety checkpoint `7fa3d72c39d244fe44c701045486081ec09426b0`.
- Post-integration verification reference: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/evidence/delivery-docs-checks.log` (focused current matrix `54 passed`; default project `101 passed, 8 skipped`; compile, launcher help, diff, and active removed-identity/dependency checks passed).

## Why Docs Were Updated

- Summary: The final public capability is now the generic `browser-automation` bundle with `scripts/browser`, distribution/namespace `browser-automation` / `browser_automation`, and generic runtime variables. Agent script calls map directly to operation-specific `--script` and `--arg-json` flags. The former external browser-manager dependency is replaced by a production-owned runtime that gates establishment by debug port, attaches to a durable loopback CDP endpoint or launches one exact Chrome process group, promotes only after initial Playwright/context validation, and aborts only its exact pending group before unlock.
- Why this should live in long-lived project docs: These are the active product identity, invocation, configuration, process-ownership, concurrency, cleanup, security, and maintenance contracts. They must not be reconstructed from superseded branded delivery records or ticket-only architecture evidence.

## Long-Lived Docs Reviewed

| Doc Path | Why It Was Reviewed | Result (`Updated`/`No change`/`Needs follow-up`) | Notes |
| --- | --- | --- | --- |
| `README.md` | Canonical repository project inventory | `Updated` | Active project entry is `browser-automation`; the superseded branded project name is removed. |
| `browser-automation/README.md` | Canonical operator/developer/runtime contract | `Updated` | Documents generic skill/CLI/MCP identities, exact-locator invocation, direct script arguments, workspace policy, owned runtime lifecycle/configuration, support boundary, and current test commands. |
| `browser-automation/SKILL.md` | Canonical agent procedure and safety guidance | `Updated` | Names only `scripts/browser`, preserves exact advertised-file/task-CWD discovery, and makes direct `--script`/`--arg-json` the normal former-MCP mapping. |
| `browser-automation/agents/openai.yaml` | Optional vendor metadata | `Updated` | Uses generic display name, skill invocation, and prompt while remaining supplementary to `SKILL.md`. |
| Active old project/docs paths | Removal and no-alias verification | `Updated` | `autobyteus-browser/` active docs/source are removed; no compatibility launcher or active branded identity remains. |

## Docs Updated

| Doc Path | Type Of Update | What Changed | Why |
| --- | --- | --- | --- |
| `README.md` | Repository inventory | Replaces the branded browser project row with `browser-automation`. | Keeps repository navigation aligned with the final generic public identity. |
| `browser-automation/README.md` | Operator/developer/runtime documentation | Records the exact skill locator and `scripts/browser`, direct argument mapping, JSON/exit/artifact contracts, shared application, owned Chrome establishment/promotion/abort lifecycle, MCP exposure, configuration, and executable checks. | Makes the reviewed SR-009 runtime and operational boundaries durable. |
| `browser-automation/SKILL.md` | Agent-facing workflow | Uses the generic skill/launcher and direct operation flags while preserving preflight, explicit IDs, observe/act/verify, recovery, confirmation, and ownership-aware cleanup. | Agents need the current supported procedure without branded aliases or unnecessary input indirection. |
| `browser-automation/agents/openai.yaml` | Optional provider metadata | Renames display/prompt references to Browser Automation / `$browser-automation`. | Keeps optional metadata aligned without making it authoritative. |

## Durable Design / Runtime Knowledge Promoted

| Topic | What Future Readers Need To Understand | Source Ticket Artifact(s) | Target Long-Lived Doc |
| --- | --- | --- | --- |
| Generic bundle identity | The active bundle is `browser-automation`; the skill is `browser-automation`; the agent launcher is `scripts/browser`; MCP uses `scripts/browser-mcp`; package/namespace are `browser-automation` / `browser_automation`. | `requirements.md`, `cli-conversion-analysis.md`, `design-spec.md`, `solution-revision-record.md` | Root `README.md`; `browser-automation/README.md`; `browser-automation/SKILL.md` |
| Exact advertised skill locator | Resolve `scripts/browser` from the exact runtime-advertised/read `SKILL.md`, invoke with Bash from the unchanged task workspace, and do not scan/guess or require persistent public locator state. | `requirements.md`, `design-spec.md`, `api-e2e-execution-coverage-report.md` | `browser-automation/README.md`; `browser-automation/SKILL.md` |
| Argument-isomorphic script use | Normal `run_script(tab_id, script, arg)` mapping is `run-script --tab-id ... --script ... --arg-json ...`; file/stdin modes are optional only for pre-existing sources or concrete transport constraints. | `requirements.md` (`REQ-014`/`AC-014`), `design-spec.md`, `implementation-handoff.md` | `browser-automation/README.md`; `browser-automation/SKILL.md` |
| Owned Chrome establishment | One per-port gate precedes the authoritative probe. A new launch remains pending and exact-group-owned through Playwright connection/first-context validation; promotion clears abort authority before unlock, while failure/cancellation completes exact group cleanup before unlock. | `design-spec.md` (`SR-008`/`SR-009`), `implementation-handoff.md`, `api-e2e-execution-coverage-report.md` (`AC-015`) | `browser-automation/README.md` |
| Durable Chrome and explicit tab identity | Pre-existing or successfully promoted Chrome survives individual CLI clients; browser-owned target IDs work across independent processes; client disconnect does not globally terminate Chrome. | `requirements.md`, `api-e2e-execution-coverage-report.md` | `browser-automation/README.md`; `browser-automation/SKILL.md` |
| Runtime configuration and discovery | Endpoint is fixed loopback with configured port; profile/log/executable configuration is explicit; common macOS/Linux executables are discovered deterministically; the runtime never enumerates or globally kills browsers. | `implementation-handoff.md`, `code-review-report.md`, `api-e2e-execution-coverage-report.md` | `browser-automation/README.md` |
| MCP exposure boundary | MCP remains a thin adapter; HTTP defaults to loopback, and explicit non-loopback operation has no built-in authentication and requires external protection. | `requirements.md`, `design-spec.md`, `api-e2e-execution-coverage-report.md` | `browser-automation/README.md` |

## Removed / Replaced Components Recorded

| Old Component / Path / Concept | What Replaced It | Where The New Truth Is Documented |
| --- | --- | --- |
| `autobyteus-browser/`, branded skill/CLI/namespace/environment/readiness/schema identities | Generic `browser-automation/`, `browser-automation`, `browser`, `browser_automation`, and `BROWSER_AUTOMATION_*` identities | Root `README.md`; `browser-automation/README.md`; `browser-automation/SKILL.md` |
| `scripts/autobyteus-browser` and `scripts/autobyteus-browser-mcp` | `scripts/browser` and `scripts/browser-mcp` | `browser-automation/README.md`; `browser-automation/SKILL.md` |
| External `brui-core` runtime/wrapper | Owned `browser_automation.runtime` configuration, launcher/establishment, and session modules | `browser-automation/README.md` |
| Complexity-based preference for script files/stdin | Direct `--script` and `--arg-json` normal form; alternate sources only for an existing source or concrete transport limit | `browser-automation/README.md`; `browser-automation/SKILL.md` |
| Process-local numeric tab aliases / implicit active tab | Browser-owned opaque target IDs supplied explicitly across processes | `browser-automation/README.md`; `browser-automation/SKILL.md` |
| Global or enumerated browser termination | Exact pending owned-process-group abort only; promoted/pre-existing Chrome persists | `browser-automation/README.md`; `browser-automation/SKILL.md` |
| Unauthenticated all-interface MCP default | Loopback default; explicit non-loopback remains opt-in with a no-auth warning | `browser-automation/README.md` |

## No-Impact Decision (Use Only If Truly No Docs Changes Are Needed)

Not applicable; the active identity, normal script procedure, dependency/runtime ownership, configuration, and lifecycle documentation changed materially in the cumulative SR-009 candidate. Delivery reviewed that final integrated documentation and found no additional long-lived content correction necessary after the base merge.

## Delivery Continuation

- Result: `Pass`
- Next delivery action: Present `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/handoff-summary.md` for explicit user verification and keep archival, final commit/push, target update/merge/push, release, and cleanup on hold.
- Notes: The tracked remote base advanced by three SSH-only commits and was merged without conflict before delivery assertions. Delivery reran the current real-enabled focused matrix (`54 passed`) and default project suite (`101 passed, 8 intentionally skipped`) plus compile, launcher help, diff, and active removal scans. `API-REV-004` remains authoritative for 13/13 real integrations, 109/109 full real-enabled project tests, Linux `33 passed / 1 deselected`, process-boundary/fresh-agent/cleanup evidence, and 97% confidence; `CRR-010` approves both durable coverage changes.

## Blocked Or Escalated Follow-Up (Use Only If Docs Sync Cannot Complete)

- Classification: N/A
- Recommended recipient: N/A
- Why docs could not be finalized truthfully: N/A; docs sync passed.
