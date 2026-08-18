# Docs Sync Report

## Scope

- Ticket: `browser-mcp-cli-skill`
- Trigger: Delivery re-entry after the runtime-advertised skill-locator correction (`SR-004`/`SR-005`), architecture pass `ARCH-REV-005`, implementation/source pass `IR-004`/`CRR-006`, API/E2E pass `API-REV-003`, and proportional durable test-code pass `CRR-007`.
- Bootstrap base reference: `origin/main` at `9643f1459246c9f003196afc146a7f783eda6208`.
- Integrated base reference used for docs sync: Latest fetched `origin/main` at `9643f1459246c9f003196afc146a7f783eda6208`; it had not advanced and remains an ancestor of the local candidate checkpoint `5d5ba7e018ff3c429f28e6d175b37c5cb340277c`.
- Post-integration verification reference: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/evidence/delivery-docs-checks.log` (focused skill contract `1 passed`; default project `68 passed, 7 skipped`; compile, launcher help, diff, and active legacy-reference checks passed).

## Why Docs Were Updated

- Summary: The agent-facing discovery procedure now starts from the exact readable `SKILL.md` locator advertised by the runtime. The skill names only `scripts/autobyteus-browser`; the agent resolves that sibling path from the exact file, invokes it with Bash from the unchanged task workspace, and does not rely on a public locator variable, persistent shell state, vendor home, PATH registration, bundle CWD, direct Python/uv use, or path scanning/guessing.
- Why this should live in long-lived project docs: Resource discovery is the initiating public contract for every browser workflow. Keeping the superseded assumed-variable procedure would make an otherwise correct launcher and runtime inaccessible or misleading for supported agents.

## Long-Lived Docs Reviewed

| Doc Path | Why It Was Reviewed | Result (`Updated`/`No change`/`Needs follow-up`) | Notes |
| --- | --- | --- | --- |
| `README.md` | Canonical repository project inventory | `No change` | The `autobyteus-browser` project name and skill/CLI/thin-MCP description remain accurate after SR-004/SR-005. |
| `autobyteus-browser/README.md` | Canonical operator/developer contract | `Updated` | Replaces the assumed variable/loader procedure with exact advertised-file resolution, unchanged task CWD, unsupported-without-locator behavior, and `uv --directory` developer checks. Existing runtime, support, MCP, and safety documentation remains accurate. |
| `autobyteus-browser/SKILL.md` | Canonical agent procedure | `Updated` | Names exactly one relative launcher resource and defines exact-file resolution, task-CWD invocation, and prohibited discovery/setup fallbacks. |
| `autobyteus-browser/agents/openai.yaml` | Optional vendor metadata | `No change` | Remains supplementary and does not own resource discovery or runtime rules. |

## Docs Updated

| Doc Path | Type Of Update | What Changed | Why |
| --- | --- | --- | --- |
| `autobyteus-browser/README.md` | Operator/developer documentation | Documents runtime-advertised exact `SKILL.md` discovery, bundle-relative launcher resolution, task-CWD preservation, unsupported-runtime behavior, and root-safe development commands. | Aligns durable human guidance with SR-004/SR-005 and the tested production initiating path. |
| `autobyteus-browser/SKILL.md` | Agent-facing workflow | Removes public locator variables and persistent shell assumptions; requires the exact advertised/read file, its containing directory, one relative launcher reference, Bash invocation, and no guessing/scanning or alternate installation path. | Makes the initiating agent contract deterministic and portable across whole-bundle runtime projections. |

## Durable Design / Runtime Knowledge Promoted

| Topic | What Future Readers Need To Understand | Source Ticket Artifact(s) | Target Long-Lived Doc |
| --- | --- | --- | --- |
| Runtime-advertised skill locator | A supported runtime advertises an exact readable `SKILL.md`; the agent resolves `scripts/autobyteus-browser` from that exact file's directory and keeps the task workspace as CWD. | `requirements.md`, `cli-conversion-analysis.md`, `design-spec.md`, `solution-revision-record.md` (`SR-004`/`SR-005`) | `autobyteus-browser/README.md`, `autobyteus-browser/SKILL.md` |
| Rejected public prerequisites | No public locator variable, persistent shell state, vendor skill home, PATH registration, bundle `cd`, direct Python/uv, absolute installation path, or scan/guess fallback is part of the skill contract. | `design-spec.md`, `implementation-handoff.md`, `api-e2e-coverage-investigation.md` | `autobyteus-browser/README.md`, `autobyteus-browser/SKILL.md` |
| Launcher ownership | After the agent resolves the relative resource, the unchanged launcher privately self-locates, captures caller workspace, prepares frozen uv, and owns pre-CLI output readiness. | `design-spec.md`, `code-review-report.md` (`CRR-006`) | `autobyteus-browser/README.md` |
| Stable explicit tab identity | Browser-owned target IDs survive independent CLI processes while the target exists; there is no daemon, numeric alias registry, or active-tab fallback. | `requirements.md`, `design-spec.md`, `api-e2e-execution-coverage-report.md` | `autobyteus-browser/README.md`, `autobyteus-browser/SKILL.md` |
| Machine output and safe artifacts | Non-help CLI calls produce one schema-v1 JSON stdout value; artifacts remain inside the caller workspace and replacement is explicit. | `requirements.md`, `implementation-handoff.md`, `api-e2e-execution-coverage-report.md` | `autobyteus-browser/README.md`, `autobyteus-browser/SKILL.md` |
| MCP exposure boundary | HTTP defaults to loopback; explicit non-loopback use has no built-in authentication and requires external protection. | `requirements.md`, `design-spec.md`, `api-e2e-execution-coverage-report.md` | `autobyteus-browser/README.md` |
| Supported/validated baseline | Bash-capable macOS/Linux and Chrome/Chromium over CDP are first-release scope; live-browser tests are opt-in with `AUTOBYTEUS_BROWSER_REAL_TESTS=1`. | `requirements.md`, `api-e2e-execution-coverage-report.md` | `autobyteus-browser/README.md` |

## Removed / Replaced Components Recorded

| Old Component / Path / Concept | What Replaced It | Where The New Truth Is Documented |
| --- | --- | --- |
| Assumed loader-populated/public skill-directory variable | Exact runtime-advertised/read `SKILL.md` plus relative `scripts/autobyteus-browser` resolution | `autobyteus-browser/README.md`; `autobyteus-browser/SKILL.md` |
| Persistent shell locator state or bundle-discovery fallback | Resolve from the exact advertised file whenever needed; unsupported rather than scan/guess | `autobyteus-browser/SKILL.md` |
| `browser-mcp/` MCP-only project root | Relocatable `autobyteus-browser/` skill/project bundle | Root `README.md`; `autobyteus-browser/README.md` |
| `scripts/browser_mcp_stdio.sh` | `autobyteus-browser/scripts/autobyteus-browser-mcp` | `autobyteus-browser/README.md` |
| MCP-owned in-memory numeric tab aliases | Browser-owned opaque target IDs shared by CLI and MCP | `autobyteus-browser/README.md`; `autobyteus-browser/SKILL.md` |
| MCP tool bodies as business-logic owners | Shared transport-neutral `BrowserApplication` with thin CLI/MCP adapters | `autobyteus-browser/README.md` |
| Unauthenticated all-interface HTTP default | Loopback default; explicit non-loopback remains allowed with a no-auth warning | `autobyteus-browser/README.md` |
| Process/global browser-close behavior | Explicit single-tab close only | `autobyteus-browser/README.md`; `autobyteus-browser/SKILL.md` |

## No-Impact Decision (Use Only If Truly No Docs Changes Are Needed)

Not applicable; the public resource-discovery documentation changed materially.

## Delivery Continuation

- Result: `Pass`
- Next delivery action: Present `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/handoff-summary.md` for explicit user verification and keep archival, commit/push, merge, release, and cleanup on hold.
- Notes: The latest tracked base had not advanced, so no base change required integration or base-induced revalidation. Delivery re-entry nevertheless reran the focused contract and default suite (`1 passed`; `68 passed, 7 intentionally skipped`), compile, launcher help, diff, and active legacy-reference checks. `API-REV-003` remains authoritative for 11/11 real integration and 75/75 full real-enabled execution; `CRR-007` approves the added durable test.

## Blocked Or Escalated Follow-Up (Use Only If Docs Sync Cannot Complete)

- Classification: N/A
- Recommended recipient: N/A
- Why docs could not be finalized truthfully: N/A; docs sync passed.
