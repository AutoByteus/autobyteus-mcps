# Requirements Document

## Document Status

- Status: `Approved`
- Current solution revision ID: SR-002
- Package identifier: `video-audio-cli-skill`
- Request / ticket: convert `video-audio-mcp` to a CLI + agent skill, learning from `browser-automation`
- Requirements owner: Solution Designer
- Date: 2026-09-29
- Approval state and reference: Approved by the user in conversation on 2026-09-29 (message "approved") in reply to the request to approve "with your recommendations" or list changes; no changes were listed, so DEC-001..DEC-005 are resolved to their recommendations.
- Exact approved requirements baseline / solution revision: SR-001 content (REQ-001..016, AC-001..013, BEH-001..007, SCN-001..005) as approved in SR-002
- Behavior-defining supplements: none (conversion convention is `docs/mcp-to-cli-mapping.md`, already repository policy)

## Problem And Desired Outcome

- Problem: `video-audio-mcp` is reachable only as an MCP server. Agents cannot drive it from Bash with a self-provisioning command, and it has no skill; failures are unstructured strings; the code cannot be reused without FastMCP.
- Affected actors: AutoByteus agents; developers running ffmpeg edits; existing MCP clients.
- User-stated rationale (2026-09-29): agents can already use Bash well, so a skill + CLI avoids loading 32 MCP tool schemas into the LLM context; the skill is loaded only when needed.
- Desired outcome: the same media-editing capabilities available as (a) a task-oriented CLI launched through a self-locating script, with one strict JSON envelope per invocation, and (b) a `SKILL.md` telling an agent how to use it; the MCP server remains a thin adapter over the same shared core, following the `browser-automation` model.
- Observable success: a fresh agent reads `SKILL.md`, runs `health-check`, performs each operation via `<subcommand> --<option>` invocations, gets parseable JSON with stable error codes, and the produced media matches what the MCP tool produced for the same inputs.

## Relevant Current And Desired Behavior

| Behavior ID | Kind | Related Scenario IDs | Current Behavior | Desired Behavior | Preserved Behavior | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| BEH-001 | Contract | SCN-001, SCN-005 | 32 MCP tools on stdio | Every tool also a CLI subcommand; MCP tool names, argument names/types/defaults and media results unchanged | MCP surface and launch path keep working | notes BEH-001 |
| BEH-002 | Contract | SCN-002 | Paths: absolute anywhere, relative vs `AUTOBYTEUS_AGENT_WORKSPACE`/cwd | CLI path policy per DEC-003 (recommended: relative paths resolve against the caller workspace; outputs confined to it; inputs may be absolute) | MCP path behavior unchanged | notes BEH-002 |
| BEH-003 | Contract | SCN-003 | Errors as strings | CLI returns structured error `code/message/retryable` and exit category; ffmpeg stderr surfaced in `details` | MCP keeps returning the same textual results | notes BEH-003 |
| BEH-004 | Contract | SCN-002 | Outputs silently overwritten | CLI refuses to replace an existing output unless `--overwrite` (DEC-003) | MCP keeps overwrite-by-default | notes BEH-004 |
| BEH-005 | System | SCN-001 | Fallbacks, concat normalization | Identical media processing behavior through both surfaces | Fallback + normalization semantics | notes BEH-005 |
| BEH-006 | Operational | SCN-004 | System ffmpeg required, no preflight | CLI `health-check` reports ffmpeg/ffprobe availability and versions; launcher provisions the Python env via `uv run --frozen` with no manual setup | Same system prerequisite (ffmpeg) | notes BEH-006 |
| BEH-007 | Contract | SCN-001 | Structured args as dict/list | Strict JSON options (`--font-style-json`, `--text-elements-json`, `--broll-clips-json`, `--video-paths-json`, `--audio-paths-json`) | Same accepted content | notes BEH-007 |

## Stakeholders, Actors, And Outcomes

| Actor | Goal | Required Outcome | Constraint |
| --- | --- | --- | --- |
| Agent (skill user) | Edit media from Bash | Discoverable subcommands, JSON results, recoverable errors, no env setup | Only knows the advertised `SKILL.md` location |
| Existing MCP client | Keep using tools | No behavior change | Launch command keeps working (or documented equal replacement per DEC-001/DEC-002) |
| Maintainer | One implementation | CLI and MCP share one core; convention doc satisfied | No duplicate ffmpeg logic |

## Scope Guardrail (Mandatory)

### In-Scope Use Cases
- UC-001: run any current media operation from the CLI with argument-isomorphic options.
- UC-002: preflight with `health-check` (ffmpeg/ffprobe/runtime).
- UC-003: agent discovers usage through `SKILL.md` and `--help`.
- UC-004: existing MCP clients continue to use the same tools via a thin adapter over the shared core.
- UC-005: recover from failures using stable error codes.

### Out Of Scope
- New editing capabilities, new ffmpeg features, or changing what any operation produces.
- Removing or renaming MCP tools/arguments; changing MCP result strings.
- Daemon/session/streaming features, GUI, Windows-native support, remote/HTTP MCP transports (not present today).
- Converting other MCP projects; changes to `browser-automation` beyond reading it.
- Installing ffmpeg for users (document only).

### Non-Goals
- A generic `call-tool`/payload CLI (rejected by `docs/mcp-to-cli-mapping.md`).
- Collapsing the convenience `set_*` / `convert_*_format` wrapper tools (11 + 2, corrected count) into fewer subcommands (each stays a direct subcommand; see DEC-004).

### Preserved Behavior Boundary
BEH-001 (MCP contract), BEH-004 and BEH-002 for the MCP surface, BEH-005 for both surfaces; REQ-004, REQ-011, AC-006, AC-009.

### Review Authority
Findings must cite an approved REQ/AC/BEH ID. New policies (e.g., extra security models, new tools) are Requirement Gaps needing user approval.

## Requirements

| ID | Requirement | Behavior | Priority | Rationale |
| --- | --- | --- | --- | --- |
| REQ-001 | Provide one relocatable bundle containing `SKILL.md`, agent metadata, a `scripts/` launcher, locked Python project, source, tests and README, mirroring `browser-automation` | BEH-006 | Must | Repository convention |
| REQ-002 | Every currently registered MCP tool has an explicit disposition; recommended: each is a direct kebab-case subcommand (`trim_video`→`trim-video`, `health_check`→`health-check`) | BEH-001 | Must | `docs/mcp-to-cli-mapping.md` checklist |
| REQ-003 | Options map 1:1 from argument names (`--output-video-path`), required/optional, types, defaults, enums and bounds preserved; booleans defaulting true (`reencode`) use a reviewed `--reencode/--no-reencode` pair; structured/list values use strict JSON `--*-json` options | BEH-001, BEH-007 | Must | Argument-isomorphic rule |
| REQ-004 | The MCP server remains available with identical tool names, argument schemas and string results for the same inputs, launched through a documented working command | BEH-001 | Must | Compatibility |
| REQ-005 | CLI and MCP delegate to one transport-neutral core; ffmpeg logic exists once and no longer requires FastMCP to import | BEH-001, BEH-005 | Must | Convention; maintainability |
| REQ-006 | Every non-help invocation prints exactly one strict JSON envelope (`schema_version "1"`, `ok`, `command`, `result`/`error{code,message,retryable,details?}`) on stdout; diagnostics on stderr; exit codes 0 success, 2 usage/validation/path policy, 3 bootstrap/config/missing ffmpeg, 4 input not found/unreadable media, 5 ffmpeg/operation failure | BEH-003 | Must | Browser precedent |
| REQ-007 | Success results include the produced artifact path(s) and, where the MCP returned a value (`get_media_duration`), that value as structured data | BEH-003 | Must | Agent usability |
| REQ-008 | ffmpeg failures surface as structured errors including a bounded excerpt of ffmpeg stderr; fallback attempts are reported | BEH-003, BEH-005 | Must | Recoverability |
| REQ-009 | Launcher `scripts/<cli>` self-locates the bundle, captures caller cwd as the workspace, finds `uv`, runs `uv run --frozen`, and yields a canned bootstrap-failure envelope (exit 3) if the runtime cannot start; no manual `uv sync`/venv step by the agent | BEH-006 | Must | Browser + image-audio precedent |
| REQ-010 | `health-check` reports ffmpeg and ffprobe presence/versions and returns a structured error when missing | BEH-006 | Must | Host lacks ffmpeg today |
| REQ-011 | Media processing results (fallbacks, concat normalization, subtitle wrapping, trim modes) are unchanged for both surfaces | BEH-005 | Must | Preserved behavior |
| REQ-012 | Path and overwrite policy for the CLI per DEC-003 (recommended default: relative paths resolve against the caller workspace; output paths must stay inside it; input paths may be absolute or workspace-relative; existing outputs require `--overwrite`) | BEH-002, BEH-004 | Must | Safety, browser precedent |
| REQ-013 | `SKILL.md` follows the browser skill model: front matter with when/when-not use, exact-locator launcher resolution, workflow, per-operation guidance, output/recovery code table, safety notes, plus `agents/openai.yaml` | BEH-006 | Must | Agent discoverability |
| REQ-014 | `--help` for the CLI and each subcommand documents options, defaults and examples | BEH-001 | Must | Discoverability |
| REQ-015 | Validation: unit tests (parser/policy/envelope), process-level launcher tests (quoting, invalid JSON, missing option, defaults, exit codes), real-ffmpeg tests per capability family through CLI and MCP with parity checks, and a skill-contract test; existing media tests preserved or re-homed | All | Must | Convention checklist |
| REQ-016 | Documentation updates: bundle README (CLI, skill, MCP adapter, prerequisites incl. ffmpeg), repository README entry; obsolete README claims corrected | BEH-006 | Should | Docs sync |

## Acceptance Criteria

| ID | Reqs | Trigger | Expected Outcome | Alternate/Failure | Verification |
| --- | --- | --- | --- | --- | --- |
| AC-001 | REQ-002, REQ-003 | Compare registered MCP tools/schemas with CLI subcommands/options | Every tool has a subcommand; every argument has an option with matching required/default/type; disposition table has no gaps | Any tool omitted must carry a documented reason | Automated parity test from live `list_tools` |
| AC-002 | REQ-009 | From an unrelated cwd, run launcher `health-check` on fresh checkout | JSON success (or structured `FFMPEG_MISSING` exit 3) with no manual setup | Broken uv → bootstrap envelope, exit 3 | Black-box test |
| AC-003 | REQ-006 | Run success, usage error, missing input, ffmpeg failure | Exactly one JSON envelope on stdout with correct code/exit category | Help output exempt | Process tests |
| AC-004 | REQ-003, BEH-007 | Invoke `add-subtitles --font-style-json`, `add-text-overlay --text-elements-json`, `concatenate-videos --video-paths-json`, multiline/quoted values | Values arrive intact; invalid JSON rejected exit 2 | `NaN`/non-JSON rejected | Process `argv` tests |
| AC-005 | REQ-003 | Omit optional args; `trim-video` without flags | Defaults match MCP (`reencode` true; `--no-reencode` selects copy) | | Unit + real tests |
| AC-006 | REQ-004, REQ-011 | Call each tool family via in-memory/real MCP and via CLI with same inputs | Equivalent media outputs (duration/streams/dimensions within tolerance); MCP returns same strings as before | | Parity tests |
| AC-007 | REQ-012 | Output path outside workspace; existing output without `--overwrite`; input absolute | Rejected exit 2 with `ARTIFACT_PATH_REJECTED`/`ARTIFACT_EXISTS`; absolute inputs accepted; with `--overwrite` succeeds | MCP behavior unchanged | Policy + process tests |
| AC-008 | REQ-010 | Run `health-check` with ffmpeg absent | exit 3, code `FFMPEG_MISSING` | with ffmpeg: versions reported | Test with PATH override |
| AC-009 | REQ-005 | Import the core without `mcp` installed / grep for ffmpeg calls | No FastMCP import in core; one implementation per operation | | Import test + review |
| AC-010 | REQ-013 | Fresh-agent walkthrough using only `SKILL.md` | Agent resolves launcher, runs health-check, performs trim + concat + extract audio, parses results, recovers from a deliberate error | | Skill-contract test + manual scenario |
| AC-011 | REQ-014 | `--help` and `<cmd> --help` | Full option list, defaults, examples; no generic call-tool form | | Help tests |
| AC-012 | REQ-015 | Run full suite on a host with ffmpeg | All tests pass; tests needing ffmpeg skip with clear reason when absent | | CI/local run |
| AC-013 | REQ-016 | Review docs | READMEs describe CLI, skill, MCP adapter, ffmpeg prerequisite accurately | | Docs review |

## Relevant Scenarios And Journeys

| ID | Kind | Actor | Goal | Trigger | Start | Steps | Outcome | Alternate/Error | Validity | Evidence | Reqs/ACs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SCN-001 | User | Agent | Edit media | Skill → launcher subcommand | Workspace with input media | health-check → run e.g. `trim-video`, `concatenate-videos` → parse JSON | Output file in workspace, artifact path in result | Error envelope with code | Supported Normal Scenario | User request; browser skill flow | REQ-002/003/006/007, AC-001/003/004/005 |
| SCN-002 | User | Agent | Avoid clobbering / escaping workspace | Re-run with existing output or outside path | Existing file | Command rejected; retry with `--overwrite` or valid path | Safe outcome | | Supported Normal Scenario | browser policy precedent (DEC-003 pending) | REQ-012, AC-007 |
| SCN-003 | User | Agent | Recover from bad input | Missing file / bad ffmpeg args | | Read `error.code`, adjust, retry | Actionable error with ffmpeg excerpt | | Supported Normal Scenario | browser recovery table | REQ-006/008, AC-003 |
| SCN-004 | Operational | Agent/host | Preflight | `health-check` | Host with/without ffmpeg | Report or fail structurally | Clear prerequisite state | | Supported Normal Scenario | ffmpeg absent on this host | REQ-009/010, AC-002/008 |
| SCN-005 | Contract | MCP client | Keep working | stdio launch | Existing config | Same tools/results | No regression | | Supported Normal Scenario | README client configs | REQ-004/011, AC-006 |

## UI, Interaction, And Experience Requirements

- Applicable: No. Linked prototype/UI-UX fields: `N/A — not applicable`.

## Quality And Non-Functional Requirements

| ID | Reqs | Area | Requirement | Verification |
| --- | --- | --- | --- | --- |
| QR-001 | REQ-006 | Operability | stdout contains only the JSON envelope for non-help calls, even when ffmpeg is noisy | Process test |
| QR-002 | REQ-012 | Security | Argument values are never shell-interpolated; ffmpeg invoked with argument arrays; workspace confinement per DEC-003 | Review + tests |
| QR-003 | REQ-004 | Compatibility | MCP tool list and schemas identical before/after | Snapshot test |
| QR-004 | REQ-009 | Portability | macOS and Linux with Bash + uv + ffmpeg; Windows native out of scope | Docs |

## Data Continuity And Acceptable Loss

- Persisted data affected: No. Only user media files, written explicitly by commands.

## External Contracts And Dependencies

| Contract | Constraint | Authority | Risk |
| --- | --- | --- | --- |
| System `ffmpeg`/`ffprobe` | Must be on PATH | Existing README | Absent on this dev host (RISK-002) |
| `uv` | Launcher needs it | browser/image-audio precedent | |
| `docs/mcp-to-cli-mapping.md` | Governs mapping | Repo policy | |

## Supplemental Artifacts

None yet. Investigation evidence: `investigation-notes.md`.

## Assumptions

| ID | Assumption | Why | Validation | Status |
| --- | --- | --- | --- | --- |
| ASM-001 | AutoByteus agents set the shell cwd to the task workspace and read the skill by exact path (as for browser-automation) | Locator rules | Skill-contract test | Open |
| ASM-002 | ffmpeg can be installed on a validation host | Real tests | Install ffmpeg (apt available) at validation | Open |

## Open Decisions And Questions

| ID | Question | Options / Evidence | Recommendation | Owner | Status |
| --- | --- | --- | --- | --- | --- |
| DEC-001 | Keep the MCP server as a retained thin adapter? | (a) retain like browser-automation; (b) remove like `browser-mcp` was | (a) retain — zero-risk for existing clients. Note: user's context-cost rationale applies to agents using the skill; a retained adapter costs agents nothing unless it is configured | User | Resolved 2026-09-29: user approved recommendation |
| DEC-002 | Rename directory/bundle (`video-audio-mcp` → e.g. `video-audio-editing`) with CLI name `video-audio`? Browser precedent renamed `browser-mcp`→`browser-automation`. Rename also breaks documented client paths | (a) rename; (b) keep dir, add skill/CLI inside | (a) rename to `video-audio-editing`, CLI `video-audio`, note README migration path | User | Resolved 2026-09-29: user approved recommendation |
| DEC-003 | CLI path/overwrite policy stricter than MCP (workspace-confined outputs, `--overwrite`, absolute inputs allowed)? | (a) as recommended; (b) mirror MCP exactly (absolute anywhere, always overwrite) | (a) for CLI only; MCP unchanged | User | Resolved 2026-09-29: user approved recommendation |
| DEC-004 | Keep all 9 convenience set_* wrappers as subcommands, or drop redundant ones from the CLI (still in MCP)? | (a) keep all (isomorphic, no judgement); (b) drop | (a) | User | Resolved 2026-09-29: user approved recommendation |
| DEC-005 | Fix pre-existing packaging quirks (pytest as runtime dependency, Python ≥3.13 floor, README badge "3.8+")? | (a) fix (move pytest to test extra, keep/relax floor only if verified); (b) leave | (a) minimal fixes | User | Resolved 2026-09-29: user approved recommendation |

## Traceability

| Req | Use Cases | Behaviors | ACs | Scenarios |
| --- | --- | --- | --- | --- |
| REQ-001 | UC-003 | BEH-006 | AC-002, AC-010 | SCN-001, SCN-004 |
| REQ-002 | UC-001 | BEH-001 | AC-001 | SCN-001 |
| REQ-003 | UC-001 | BEH-001, BEH-007 | AC-001, AC-004, AC-005 | SCN-001 |
| REQ-004 | UC-004 | BEH-001 | AC-006 | SCN-005 |
| REQ-005 | UC-001, UC-004 | BEH-001, BEH-005 | AC-009 | SCN-001, SCN-005 |
| REQ-006 | UC-005 | BEH-003 | AC-003 | SCN-001, SCN-003 |
| REQ-007 | UC-001 | BEH-003 | AC-003 | SCN-001 |
| REQ-008 | UC-005 | BEH-003, BEH-005 | AC-003 | SCN-003 |
| REQ-009 | UC-002 | BEH-006 | AC-002 | SCN-004 |
| REQ-010 | UC-002 | BEH-006 | AC-002, AC-008 | SCN-004 |
| REQ-011 | UC-001, UC-004 | BEH-005 | AC-006 | SCN-005 |
| REQ-012 | UC-001 | BEH-002, BEH-004 | AC-007 | SCN-002 |
| REQ-013 | UC-003 | BEH-006 | AC-010 | SCN-001 |
| REQ-014 | UC-003 | BEH-001 | AC-011 | SCN-001 |
| REQ-015 | all | all | AC-012 | all |
| REQ-016 | UC-003 | BEH-006 | AC-013 | — |

## Architecture Phase Input

- Scenarios to map: SCN-001..SCN-005.
- Constraints to preserve: MCP contract (QR-003), single core (REQ-005), convention doc.
- Deferred to design: package layout, module split, how the MCP adapter renders legacy strings from typed results, tool-schema derivation, launcher details, test layout.
- Facts to verify: exact `list_tools` schemas; whether existing tests pass with ffmpeg; Python floor.
- Risks: string-vs-structured error mapping for 81 error sites; fallback reporting.

## Readiness Check

### Content Ready For Approval
- Current behavior evidence-backed: Yes
- Desired and preserved behavior explicit: Yes
- Scope and non-goals clear: Yes
- Requirements/ACs testable and traceable: Yes
- Scenarios covered: Yes
- Prototype/supplements: N/A
- Assumptions and open decisions visible: Yes
- Content ready for user approval: Yes
- Remaining content blocker: none (DEC-001..005 carry recommendations)

### Approved Basis Ready For Design
- User approval received: Yes (2026-09-29, see Document Status)
- Exact approval basis recorded: Yes (SR-002)
- Ready for architecture design: Yes
- Remaining blocker: none
