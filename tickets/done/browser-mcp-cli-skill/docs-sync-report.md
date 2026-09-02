# Docs Sync Report

## Scope

- Ticket: `browser-mcp-cli-skill`
- Trigger: User-requested durable best-practice guide after current cumulative `SR-009` passed `ARCH-REV-008`, `IR-006`/`CRR-009`, `API-REV-004`, and `CRR-010`. This is a delivery-owned documentation revision; product source and test code are unchanged.
- Bootstrap base reference: `origin/main` at `9643f1459246c9f003196afc146a7f783eda6208`.
- Integrated base reference used for docs sync: Latest fetched `origin/main` at `8eb45df64416f51db524bba995c291721081f51b`, integrated by merge into the ticket branch at `72ffa7de0bcf1673f668a80b6be8fc95a489aadd` after protecting the prior DR-003 state at `99500c4bedd6a79fd9bbadf501982a322dc2bfe6`.
- Post-integration verification reference: `/Users/normy/autobyteus_org/autobyteus_mcps/tickets/done/browser-mcp-cli-skill/evidence/delivery-docs-checks.log` (focused current matrix `54 passed`; default project `101 passed, 8 skipped`; compile, launcher help, guide contract/link validation, diff, and active removed-identity/dependency checks passed).

## Why Docs Were Updated

- Summary: Added the repository-wide guide `docs/mcp-to-cli-mapping.md`, titled **Argument-Isomorphic MCP-to-CLI Mapping**, and linked it from the root and Browser Automation READMEs. The guide makes direct MCP-argument-to-CLI-option mapping the reusable default, defines CLI/argv terminology, preserves schema semantics, documents scalar/strict-JSON/boolean handling, requires direct argv for normal agent use, rejects a generic payload normal form, separates the JSON output envelope, and uses the reviewed Browser Automation `run_script` and `attach_tab` mappings as concrete examples. The existing generic identity, direct-argument skill, and production-owned runtime docs remain current.
- Why this should live in long-lived project docs: The mapping rule is a cross-project engineering convention for future MCP-to-CLI work, not a ticket-only browser decision. A repository guide makes the rule discoverable and reusable while the Browser Automation links and examples keep it grounded in a reviewed implementation.

## Long-Lived Docs Reviewed

| Doc Path | Why It Was Reviewed | Result (`Updated`/`No change`/`Needs follow-up`) | Notes |
| --- | --- | --- | --- |
| `docs/mcp-to-cli-mapping.md` | Repository-wide future-conversion convention requested by the user | `Updated` | New durable guide covers terminology, invariant-preserving name/value mapping, strict JSON, direct argv, optional source alternatives, quoting, output separation, anti-patterns, examples, and review tests. |
| `README.md` | Canonical repository inventory and engineering-guide discovery | `Updated` | Existing `browser-automation` entry remains accurate; a new Engineering Guides section links the mapping guide. |
| `browser-automation/README.md` | Canonical operator/developer/runtime contract and concrete reference | `Updated` | Links the repository guide; existing generic identity, direct arguments, workspace policy, owned runtime, support, MCP, and test documentation remains accurate. |
| `browser-automation/SKILL.md` | Canonical agent procedure and concrete behavior basis | `No change` | Already implements the documented direct `--script`/`--arg-json` normal path and exact-locator contract. |
| `browser-automation/agents/openai.yaml` | Optional vendor metadata | `No change` | Remains aligned and supplementary. |
| Active old project/docs paths | Removal and no-alias verification | `No change` | Active branded identity and external runtime references remain absent. |

## Docs Updated

| Doc Path | Type Of Update | What Changed | Why |
| --- | --- | --- | --- |
| `docs/mcp-to-cli-mapping.md` | Repository engineering guide | Adds the reusable argument-isomorphic mapping rule, precise terminology, invariant checklist, shell quoting, strict JSON, direct argv policy, canonical browser examples, rejected generic wrappers, and validation checklist. | Gives future MCP-to-CLI conversions a durable approved default. |
| `README.md` | Guide discovery | Adds an Engineering Guides link to the new repository convention. | Makes the cross-project practice findable from the repository entrypoint. |
| `browser-automation/README.md` | Concrete-reference cross-link | Links the reusable guide from the implementation that established the reviewed practice. | Connects generic guidance to the current production example without duplicating the full guide. |

## Durable Design / Runtime Knowledge Promoted

| Topic | What Future Readers Need To Understand | Source Ticket Artifact(s) | Target Long-Lived Doc |
| --- | --- | --- | --- |
| Repository conversion convention | Prefer argument-isomorphic/direct MCP-argument-to-CLI-option mapping: tool to subcommand, argument name to named option, scalar value directly, structured value as strict JSON, direct argv normally, and no generic payload layer. | User request; `requirements.md` (`REQ-014`), `design-spec.md`, `cli-conversion-analysis.md` | `docs/mcp-to-cli-mapping.md` |
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

Not applicable; the user explicitly requested a new durable cross-project guide, and root/project README links were required to make it discoverable.

## Delivery Continuation

- Result: `Pass`
- Next delivery action: None. User verification and repository finalization completed; no release or deployment applies.
- Notes: Before this documentation edit, a fresh remote check found four additional SSH-only base commits. Delivery protected DR-003 at `99500c4`, merged `origin/main@8eb45df` without conflict at `72ffa7d`, then reran the focused matrix (`54 passed`) and default suite (`101 passed, 8 intentionally skipped`) plus compile, launcher help, guide contract/link validation, diff, and active removal scans. `API-REV-004`/`CRR-010` remain authoritative and unchanged. Finalization merged at `596d07c`; post-merge focused/default, compile, launcher-help, guide/link, and diff checks passed; cleanup completed.

## Blocked Or Escalated Follow-Up (Use Only If Docs Sync Cannot Complete)

- Classification: N/A
- Recommended recipient: N/A
- Why docs could not be finalized truthfully: N/A; docs sync passed.
