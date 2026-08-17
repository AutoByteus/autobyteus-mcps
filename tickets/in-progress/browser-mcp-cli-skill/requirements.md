# Requirements Doc

## Status (`Draft`/`Design-ready`/`Refined`)

`Refined — approved for design on 2026-08-17`

## Goal / Problem Statement

Turn the repository's current stateful `browser-mcp` capability into task-oriented command-line tools and one agent skill, using the incomplete `autobyteus-image-audio` CLI work as a reference without copying its stateless assumptions or documentation gaps.

The intended outcome is an agent-usable browser surface that does not require the agent to start/speak MCP, manually create a Python environment, or reconstruct browser lifecycle rules. The CLI must own deterministic execution and machine contracts; the skill must own concise procedural guidance, observation/action sequencing, safety, recovery, and cleanup conventions.

## Current And Desired Behavior (Mandatory)

| Behavior ID | Current Behavior | Desired Behavior | Preserved / Unchanged Behavior | Related Requirement / Acceptance-Criteria IDs |
| --- | --- | --- | --- | --- |
| `BEH-001` | A long-lived FastMCP process exposes nine browser tools. Browser state is held in one in-memory `TabManager`; stateful calls require short process-local `tab_id` values. | Each suitable browser capability is directly invocable through a task-oriented CLI from independent shell processes, with stable tab identity across calls. | Explicit tab targeting remains mandatory; no implicit active-tab fallback is reintroduced. | `REQ-001`–`REQ-006`; `AC-001`–`AC-006` |
| `BEH-002` | `open_tab`/`attach_tab` register live Playwright pages in the MCP process; `list_tabs` shows only that process's tracked pages and metadata. | Approved CLI discovery/open/attach commands return a browser-owned tab identity that remains resolvable after the invoking process exits; listing semantics are truthful for the approved identity model. | Ambiguous attach criteria continue to fail rather than selecting arbitrarily. | `REQ-002`, `REQ-005`, `REQ-006`; `AC-001`, `AC-005`, `AC-006` |
| `BEH-003` | Navigation, page read, screenshot, DOM snapshot, and arbitrary JavaScript are implemented partly inside MCP-decorated nested functions. | One transport-neutral browser application boundary owns these operations and is used by every retained public adapter. | Core browser outcomes, explicit timeouts/wait modes, DOM selectors, script results, and artifact creation remain available unless explicitly changed below. | `REQ-001`, `REQ-006`; `AC-002`, `AC-006`, `AC-009` |
| `BEH-004` | Normal tool success returns MCP structured content; errors are translated by FastMCP. There is no browser CLI stdout/stderr/exit contract. | Every non-help CLI invocation emits one versioned JSON result or error envelope on stdout, keeps diagnostics on stderr, and exits with a stable documented category. | Help remains human-readable. | `REQ-003`, `REQ-004`; `AC-003`, `AC-004` |
| `BEH-005` | No verified browser CLI agent skill exists. The image/audio project has a skill-facing CLI but no tracked/installed image-audio `SKILL.md` was found. | One version-controlled browser skill bundle triggers on browser-automation tasks, carries its agent-facing launcher as a bundled script, and teaches preflight, discovery/opening, explicit-ID operations, observe/act/verify loops, output parsing, recovery, confirmation, and cleanup. | The skill delegates execution and validation to the CLI; it does not duplicate browser implementation logic. | `REQ-009`, `REQ-010`; `AC-010`, `AC-011` |
| `BEH-006` | Screenshot paths may be arbitrary absolute paths, URL validation is broad, and `close_browser=true` can reach a global Chrome-kill path. | File, URL, destructive lifecycle, and arbitrary-script behavior follow explicit enforceable CLI/core policy; normal skill guidance cannot accidentally terminate the whole browser. | Explicitly requested page/tab close remains available. | `REQ-007`, `REQ-008`; `AC-007`, `AC-008` |
| `BEH-007` | The current MCP server supports stdio and streamable HTTP; its README-recommended `scripts/browser_mcp_stdio.sh` launches stdio, and streamable HTTP currently defaults to unauthenticated `0.0.0.0`. | Retain MCP as a thin adapter, rename/update the stdio launcher with the project, and make streamable HTTP default to loopback. An explicitly configured non-loopback host remains possible but must warn that the server provides no built-in authentication. | Both MCP transports remain available; no compatibility wrapper, duplicated legacy business path, or new remote-auth system is introduced. | `REQ-011`; `AC-012` |
| `BEH-008` | No browser CLI wrapper exists. Running browser MCP currently requires server configuration/launch, while existing agent skills demonstrate bundled `scripts/` resolved relative to the directory containing the active `SKILL.md`. | Once an agent platform has loaded the complete browser skill folder, the skill tells the agent to set `SKILL_DIR` to the absolute directory containing that `SKILL.md` and invoke `bash "$SKILL_DIR/scripts/autobyteus-browser" health-check`; the launcher self-resolves the skill/runtime root and automatically creates/synchronizes the locked `uv` environment on first use. | No vendor-specific home variable, human PATH registration, CLI symlink, repository-path knowledge, or manual Python setup is required. | `REQ-003`, `REQ-007`, `REQ-010`; `AC-003`, `AC-004` |

## Investigation Findings

1. The browser CLI is feasible, but browser state is the central design constraint. A one-process-per-command copy of the current code would lose all `TabManager` state.
2. A real isolated Chrome/Playwright probe proved that the Chrome CDP target ID for a live page remains stable after one Playwright connection closes and a new Playwright runtime reconnects. This supports a daemon-free CLI using browser-owned IDs.
3. The current `UIIntegrator.initialize()` always creates a new page, so existing tool code cannot simply be imported by a CLI. A connection/resolution boundary must attach to the current Chrome context without creating stray pages.
4. Current execution policy is fragmented across `TabManager` and MCP tool modules. The task exposes a boundary/ownership issue and requires refactoring before adding the CLI.
5. The image/audio reference provides useful wrapper, task-command, shared-service, JSON-output, packaging, and validation patterns. It is not a completed skill example, and its canonical design documentation has drifted from current CLI behavior.
6. `run_script` is the only general interaction primitive. First-class click/type/fill commands are not current MCP behavior and are not silently added by this conversion scope.
7. The user explicitly prioritized the shell command experience and confirmed that first invocation must prepare the `uv` project environment behind the CLI/wrapper. The skill should issue ordinary Bash/shell commands and must not expose environment setup as agent work.

Detailed evidence, the command disposition, and the conversion heuristic are in `cli-conversion-analysis.md`.

## Relevant Supplemental Task Artifacts

| Artifact Path | Type / Purpose | Related Requirement IDs | Related Acceptance-Criteria IDs | Status / Approval | Relationship To Requirements |
| --- | --- | --- | --- | --- | --- |
| `tickets/in-progress/browser-mcp-cli-skill/cli-conversion-analysis.md` | Evidence and decision analysis: current architecture, CDP identity probe, tool disposition, reference lessons, industry heuristic, and approved choices | `REQ-001`–`REQ-012` | `AC-001`–`AC-012` | Approved as requirements-basis supplement on 2026-08-17 | Clarifies why a CLI is feasible, why a mechanical conversion is unsafe, and which material decisions govern design. |

## Design Health Assessment (Mandatory)

- Change posture (`Feature`/`Bug Fix`/`Behavior Change`/`Refactor`/`Cleanup`/`Performance`/`Larger Requirement`): `Larger Requirement`
- Initial design issue signal (`Yes`/`No`/`Unclear`): `Yes`
- Root cause classification (`Local Implementation Defect`/`Missing Invariant`/`Boundary Or Ownership Issue`/`Duplicated Policy Or Coordination`/`File Placement Or Responsibility Drift`/`Shared Structure Looseness`/`Legacy Or Compatibility Pressure`/`No Design Issue Found`/`Unclear`): `Boundary Or Ownership Issue` (with secondary file-responsibility drift)
- Refactor posture (`Likely Needed`/`Likely Not Needed`/`Deferred`/`Unclear`): `Likely Needed`
- Evidence basis: Browser operations and policy are partly owned by MCP-decorated nested functions; the MCP `Context` appears in navigation; server import changes CWD; the in-memory short-ID owner cannot survive a CLI process boundary; `UIIntegrator.initialize()` creates a page even when a command needs only to resolve an existing page.
- Requirement or scope impact: Extract one transport-neutral browser application boundary and replace process-local identity semantics if the recommended daemon-free CLI is approved. Do not add a second copy of each tool body or make the CLI an MCP/JSON-RPC wrapper.

## Recommendations

1. Approve browser-owned CDP target IDs as canonical tab identity so each CLI invocation can connect, act, disconnect, and exit without a daemon.
2. Keep the MCP for the first CLI+skill release, but make it a thin adapter over the same core and use the same canonical identity; consider MCP removal only after real CLI+skill use is validated.
3. Make the complete browser capability project directory itself the portable skill root (the design may rename the current MCP-centric `browser-mcp/` path): add `SKILL.md` at that root, bundle `scripts/autobyteus-browser`, and keep `uv run --frozen` plus environment preparation behind the launcher.
4. Make `SKILL.md` set `SKILL_DIR` from the absolute path supplied by whichever agent skill loader activated it; do not use `$CODEX_HOME`, any other vendor-specific home variable, a PATH-installed command, or a checkout-specific hardcoded path.
5. Remove `close_browser` from the initial CLI/skill-facing surface, restrict screenshot output paths, define URL schemes, and use stable error codes rather than Python exception names.
6. Keep first-class click/type/fill outside this conversion unless the user explicitly expands product scope; teach selector-based interaction through existing `dom_snapshot` + `run_script` capabilities.

## Scope Classification (`Small`/`Medium`/`Large`)

`Large`

Rationale: public identity/listing behavior changes, shared-core extraction, two possible adapters, packaging/wrapper work, one new skill, enforceable safety policy, real Chrome lifecycle validation, and cross-process tab continuity coverage.

## In-Scope Use Cases

| Use Case ID | Use Case |
| --- | --- |
| `UC-001` | From any working directory, an agent invokes a wrapper-owned health/preflight command without manually preparing a Python environment. |
| `UC-002` | The agent lists existing Chrome tabs or uniquely matches an existing tab and receives a stable explicit `tab_id`. |
| `UC-003` | The agent opens a tab, receives its `tab_id`, and uses that same ID from later independent CLI processes. |
| `UC-004` | The agent navigates, reads cleaned page content, captures DOM structure, runs JavaScript with structured input, and saves a screenshot against one explicit tab. |
| `UC-005` | The agent detects and recovers from missing Chrome/CDP, stale/closed tab IDs, ambiguous attach matches, invalid inputs, timeouts, and browser-operation failures using structured errors. |
| `UC-006` | The agent follows one skill to run an observe → act → verify browser workflow and closes only tabs it owns unless instructed otherwise. |
| `UC-007` | Retained public adapters, if any, use the same authoritative browser core and do not duplicate state/policy. |

## Out of Scope

- A generic framework that converts every MCP in the repository into a CLI.
- First-class click/type/fill/select commands not present in the current public browser MCP.
- Firefox/WebKit support; current `brui_core` and the approved identity mechanism are Chromium/CDP-specific.
- Cloud-hosted browser orchestration or multi-user remote service authentication.
- Automatic handling of captchas, MFA, purchases, messages, account changes, or other external side effects without normal agent confirmation policy.
- Modifying the image/audio CLI or retroactively creating its missing skill.
- Persisting or migrating the current process-local short numeric tab IDs.

## Functional Requirements

| Requirement ID | Requirement |
| --- | --- |
| `REQ-001` | Provide one transport-neutral browser application boundary that owns connection lifecycle, tab resolution, operation validation, navigation/read/snapshot/script/screenshot execution, result models, and cleanup. CLI and any retained MCP adapter must call this boundary rather than each other or its internals. |
| `REQ-002` | Support deterministic tab-scoped behavior across independent CLI processes. Recommended baseline: make the live browser's CDP target ID the canonical `tab_id`; do not add an implicit active-tab fallback or serialize Playwright objects/process-local IDs. |
| `REQ-003` | Provide a task-oriented `autobyteus-browser` CLI with explicit kebab-case commands for every approved disposition in the analysis; do not make a generic MCP `call-tool` or JSON-RPC client the normal interface. |
| `REQ-004` | For every non-help invocation, emit exactly one versioned JSON value on stdout. Success contains the command and result; failure contains a stable error code, message, retryability, and applicable details. Diagnostics/progress go only to stderr. Exit categories are stable and documented. |
| `REQ-005` | Discovery, open, attach, list, target resolution, stale-target behavior, and close ownership must be deterministic under concurrent/multiple-tab workflows. Ambiguous attach criteria fail clearly. |
| `REQ-006` | Cover current public capabilities: open, attach, close one tab, list, navigate, read page, screenshot, DOM snapshot, and run script. Preserve explicit wait/timeout and structured result behavior where applicable; explicitly document approved behavior changes. |
| `REQ-007` | Add health/preflight behavior that distinguishes wrapper/runtime dependency failure, invalid configuration, unavailable Chrome/CDP endpoint, and successful connection without creating a stray page. |
| `REQ-008` | Enforce safety in the shared core: approved URL schemes; bounded/validated timeouts and enum values; workspace-safe screenshot/output paths; explicit single-tab close; and no normal CLI/skill path that globally kills Chrome. Arbitrary JavaScript remains an advanced explicit capability and must not bypass user confirmation for consequential actions in skill guidance. |
| `REQ-009` | Create exactly one concise, vendor-neutral skill at the browser project root with valid `SKILL.md` frontmatter; optional agent-vendor metadata may supplement but must not govern the workflow. The skill must contain trigger guidance, portable skill-root resolution, preflight, command discovery, explicit-ID lifecycle, observe/act/verify sequencing, structured output interpretation, error recovery, an advanced-script boundary, side-effect confirmation, and ownership-aware cleanup. It must not reimplement CLI logic. |
| `REQ-010` | Provide reproducible, zero-human-install packaging and invocation. Treat the complete browser capability project directory as the skill bundle and place its agent-facing launcher at `scripts/autobyteus-browser`. `SKILL.md` must instruct the agent to set `SKILL_DIR` to the absolute directory containing the loaded `SKILL.md`, as exposed by that agent's skill loader, then invoke `bash "$SKILL_DIR/scripts/autobyteus-browser" ...`. The launcher resolves the same project/skill root relative to itself, captures the caller's workspace before `uv --directory`, and internally uses `uv run --frozen`; first invocation creates/synchronizes the locked environment. The launcher and CLI must use a private readiness handshake so a frozen-uv/environment/import failure before CLI startup produces exactly one launcher-owned bootstrap JSON envelope, while a started CLI's exactly-one output is forwarded without a second launcher envelope. Neither human nor agent may install/register a CLI, change `$PATH`, use `$CODEX_HOME` or another vendor-specific skill-home variable, guess a checkout, run `uv sync`, activate `.venv`, run `pip install`, or locate the project interpreter. Missing bundled files or host `uv` must produce a clear bootstrap failure without instructing the human to install the CLI. The project package is the single authoritative runtime used by the skill CLI and retained MCP; do not copy browser business logic into `scripts/` or another skill-only runtime. |
| `REQ-011` | Retain MCP only as a thin adapter over the shared browser application boundary. Rename the tracked stdio launcher to `scripts/autobyteus-browser-mcp`, update it for the renamed root/namespace and frozen uv execution, remove `scripts/browser_mcp_stdio.sh`, and update README/config examples without a compatibility wrapper. Preserve stdio and streamable HTTP, but change the HTTP default bind from `0.0.0.0` to `127.0.0.1`; validate host/port configuration and emit a prominent stderr/log warning when an operator explicitly selects a non-loopback host because no built-in authentication is added in this scope. Do not keep parallel legacy business logic or a CLI-over-MCP protocol wrapper. |
| `REQ-012` | Validate parser/envelope/service behavior locally, verify public adapter inventory, and run real isolated Chrome tests proving independent-process target continuity, listing/attach/open/operate/close behavior, artifact creation, stale-target errors, and no stray-page/global-browser shutdown. Forward-test the agent-provisioned skill bundle on representative workflows after implementation. |

## Acceptance Criteria

| Acceptance Criteria ID | Verifiable Expected Outcome |
| --- | --- |
| `AC-001` | A tab opened in process A is navigated/read or otherwise operated on successfully from process B using the returned canonical `tab_id`, with no CLI daemon and no implicit active-tab selection when the recommended identity model is approved. |
| `AC-002` | Source review shows CLI and every retained adapter call one authoritative browser application boundary; no CLI command calls MCP/JSON-RPC and no tool body is duplicated across adapters. |
| `AC-003` | Success, usage error, configuration/connectivity error, stale-tab error, and browser-operation error scenarios each produce one parseable versioned JSON stdout value, expected stderr behavior, and the documented exit category. |
| `AC-004` | With the complete skill folder available to a coding agent and no pre-existing runtime environment, the agent sets `SKILL_DIR` to the actual directory containing the loaded `SKILL.md` and successfully runs `bash "$SKILL_DIR/scripts/autobyteus-browser" health-check` from an unrelated CWD. The first call performs launcher-owned locked `uv` environment creation/synchronization, preserves the caller workspace for artifact policy, and returns the CLI result; help also works without caller-managed setup. Separate black-box cases prove that missing bundled files, missing `uv`, and frozen environment/import failure before CLI readiness each emit one bootstrap JSON value and exit `3`, whereas a started CLI success or error is forwarded exactly once with its own exit code. Structural and forward tests find no `$CODEX_HOME`, other vendor-home dependency, PATH/symlink registration, hardcoded checkout path, duplicated skill runtime, `uv sync`, virtual-environment activation, `pip install`, or direct interpreter instruction. |
| `AC-005` | Open/list/attach results expose truthful deterministic metadata. Duplicate attach matches fail, and a target closed outside the CLI yields a stable actionable stale-target error. |
| `AC-006` | Every current MCP tool has an approved disposition and corresponding durable coverage; current explicit-ID navigation/read/screenshot/DOM/script outcomes remain available. |
| `AC-007` | Screenshot/output path tests reject disallowed destinations and return resolved approved artifact paths; navigation rejects unsupported URL schemes and invalid enum/timeout inputs. |
| `AC-008` | Normal CLI help and skill guidance do not expose a global Chrome-kill operation. Closing one CLI-opened tab does not close unrelated tabs or stop Chrome. Attached/user-owned tabs are not closed automatically. |
| `AC-009` | Real Chrome execution validates DOM snapshot selectors, cleaned read modes, JavaScript result/argument serialization, screenshot file contents, navigation timeout behavior, and connection cleanup without stray pages. |
| `AC-010` | The skill passes structural validation (`quick_validate.py`) and its metadata clearly triggers for direct browser automation through the CLI while avoiding unrelated generic web research tasks. |
| `AC-011` | Forward tests show a fresh agent can use only the loaded skill bundle plus CLI help to perform at least: open→navigate→read→close; attach→inspect without closing the user tab; and DOM snapshot→script action→verification, while correctly parsing structured errors. |
| `AC-012` | Retained MCP inventory/behavior is validated over the shared core for stdio and streamable HTTP. The renamed `scripts/autobyteus-browser-mcp` works from the new project root and the old script/path is absent from active source/docs/config. Streamable HTTP defaults to `127.0.0.1`; an explicit non-loopback host is preserved with a no-auth exposure warning; host/port validation and no-broadening checks pass. |

## Constraints / Dependencies

- Current package target: Python `>=3.11`; runtime uses `brui-core`, Playwright, and Chromium CDP.
- Current `brui_core` connects to the first browser context and may launch Chrome when the configured debug endpoint is unavailable.
- Playwright documents CDP sessions as Chromium-only. Chrome DevTools Protocol target discovery/information methods used by the feasibility approach are currently marked experimental.
- The wrapper is expected to depend on `uv` and use the project lockfile.
- Large page/script results use the approved optional workspace-safe artifact-output contract; overwrite is opt-in.
- The current streamable HTTP MCP default binds to `0.0.0.0` without built-in authentication. The approved retained-adapter design changes the default to loopback, keeps explicit non-loopback configuration with a warning, and does not add a remote-auth system in this scope.

## Persisted Data Outcome (When Applicable)

- Stored subject / location: Existing Chrome profile/cookies/local storage and user-created screenshot artifacts. Current MCP `TabManager`/short IDs are memory-only and are not persisted data.
- Required outcome (`Not Affected`/`Directly Usable — No Migration`/`Discard or Rebuild`/`Migration Required`/`Undetermined`): `Not Affected`
- Existing data to preserve, discard/rebuild, transform, or quarantine: Existing Chrome profile data remains owned/read by Chrome and is not transformed. Process-local tab registrations disappear naturally when the MCP process ends and are not migrated.
- Unacceptable data loss or corruption: The CLI must not delete/replace a Chrome profile, terminate unrelated Chrome sessions, or overwrite artifacts without the approved output policy.
- Relevant availability, maintenance-window, or rollout constraints: None for stored-data migration; live tabs are ephemeral external runtime state and need lifecycle validation rather than data migration.
- Related requirement and acceptance-criteria IDs: `REQ-002`, `REQ-005`, `REQ-008`, `REQ-012`; `AC-001`, `AC-005`, `AC-008`, `AC-009`

## Assumptions

- The user wants analysis and reviewed design before implementation.
- The first practical target remains Chrome/Chromium over a local CDP endpoint, matching the existing browser MCP.
- Agents can retain and pass an explicit long target identifier in structured output.
- One skill should be reusable across supported agent requests and should discover detailed option syntax from CLI help rather than embedding every flag.
- The resolved choices are approved through the explicit 2026-08-17 user direction recorded below.

## Resolved Material Decisions / Remaining Questions

1. Retain MCP for the first release only as a thin adapter over the same browser application boundary used by the CLI; remove process-local identity and duplicated tool business logic.
2. Use browser-owned CDP target IDs across independent CLI/MCP calls; do not add a daemon or preserve short numeric aliases.
3. First release supports Bash-capable macOS/Linux coding-agent environments and the existing Chrome/Chromium-over-CDP runtime; other shells/platforms are follow-up validation targets.
4. `list-tabs` lists every addressable page in the first configured Chrome context; the context endpoint/configuration is the isolation boundary for this release.
5. `read-page`, `dom-snapshot`, and `run-script` support optional workspace-safe output files; existing files are rejected unless explicit overwrite is requested.
6. `run-script` is retained but appears only in a clearly marked advanced skill workflow and remains subject to normal confirmation for consequential external side effects.
7. The retained streamable-HTTP MCP default becomes loopback-only (`127.0.0.1`); explicit non-loopback configuration is operator opt-in and warns that no built-in authentication exists.
8. The tracked MCP stdio launcher is retained by capability but cleanly renamed to `scripts/autobyteus-browser-mcp`; the old script/path is removed rather than forwarded.

No material requirement question remains open for initial design. Platform/CDP protocol compatibility and concurrent-client behavior remain implementation-validation risks, not unresolved product intent.

## Requirement-To-Use-Case Coverage

| Requirement ID | Covered Use Case IDs |
| --- | --- |
| `REQ-001` | `UC-003`, `UC-004`, `UC-007` |
| `REQ-002` | `UC-002`, `UC-003`, `UC-004` |
| `REQ-003`, `REQ-004` | `UC-001`–`UC-005` |
| `REQ-005`, `REQ-006` | `UC-002`–`UC-006` |
| `REQ-007` | `UC-001`, `UC-005` |
| `REQ-008` | `UC-004`–`UC-006` |
| `REQ-009` | `UC-006` |
| `REQ-010` | `UC-001`, `UC-006` |
| `REQ-011` | `UC-007` |
| `REQ-012` | `UC-001`–`UC-007` |

## Acceptance-Criteria-To-Scenario Intent

| Acceptance Criteria ID | Intended Validation Scenario |
| --- | --- |
| `AC-001` | Two independent CLI subprocesses operate on one isolated Chrome tab by returned ID. |
| `AC-002` | Architecture/source dependency inspection and adapter delegation tests. |
| `AC-003` | Black-box stdout/stderr/exit matrix with JSON parsing. |
| `AC-004` | Clean/unrelated-CWD first-run wrapper and command-help tests. |
| `AC-005` | Real/fake multi-tab discovery, duplicate matching, external close, and stale resolution. |
| `AC-006` | Tool-disposition coverage matrix against current MCP registry. |
| `AC-007` | Path traversal/absolute path, URL scheme, enum, and boundary-value tests. |
| `AC-008` | Isolated Chrome with unrelated tab remains alive after command/skill cleanup. |
| `AC-009` | Real Chrome end-to-end operation matrix. |
| `AC-010` | Skill validator plus metadata/trigger inspection. |
| `AC-011` | Fresh-agent skill forward tests using only the agent-provisioned skill bundle and CLI help. |
| `AC-012` | Retained-MCP validation over the shared core for stdio and streamable HTTP, including the renamed `scripts/autobyteus-browser-mcp`, absence of the old launcher/path, the loopback default, the explicit non-loopback no-auth exposure warning, host/port validation, and no-broadening checks. |

## Approval Status

`Approved for design.` On 2026-08-17 the user approved continuing without further clarification after confirming the critical portability contract: the complete skill must tell any coding agent how to derive the directory containing its loaded `SKILL.md`, invoke the bundled launcher from that directory, avoid `$CODEX_HOME` and all vendor-specific installation assumptions, require no human CLI setup, and let the launcher own first-call locked `uv` environment preparation. The recommended task-command surface, daemon-free CDP target identity, retained thin MCP adapter, first-context listing, workspace-safe optional large-output files, and advanced-script treatment are adopted as the refined baseline.
