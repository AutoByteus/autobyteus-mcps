# Design Spec

## Current-State Read

The current `browser-mcp/` package is a long-lived FastMCP server, not a reusable browser capability package. A supported request flows from an MCP tool registered as a nested function through a process-local `TabManager`, then through `UIIntegrator` and Playwright to Chrome over CDP. `TabManager` owns short numeric IDs mapped to live `UIIntegrator`/`Page` objects. That ownership is coherent only while one MCP process remains alive.

Architecture-level inspection confirmed four coupled pressures that must be corrected in this change:

1. Application behavior is split across MCP-decorated functions, `TabManager`, `utils.py`, and `cleaning.py`; `navigate_to` also depends directly on MCP `Context`.
2. `UIIntegrator.initialize()` always creates a page, so it cannot be used as the connection boundary for list/read/resolve operations without producing stray tabs.
3. The process-local short ID map cannot survive an ordinary one-command CLI process. The approved browser-owned CDP target ID replaces it; an isolated Chrome probe already proved continuity across complete Playwright reconnects.
4. The project identity and layout are MCP-centric even though the target capability is one portable agent skill plus CLI with MCP retained only as a secondary adapter. The README-recommended `scripts/browser_mcp_stdio.sh` is a supported operational entry tied to the old root/module, and streamable HTTP currently defaults to unauthenticated `0.0.0.0`.

The target must preserve explicit tab selection, deterministic unique attach matching, navigation/read/screenshot/DOM/script outcomes, the existing Chrome/CDP runtime, and retained MCP transports. It must remove implicit/process-local state assumptions, global Chrome termination, unrestricted output paths, permissive enum handling, server-import CWD mutation, and duplicated adapter business logic. Full evidence and current production paths are recorded in `investigation-notes.md`; the approved tool disposition and shell experience are in `cli-conversion-analysis.md`.

## Intended Change

Rename the browser capability root from `browser-mcp/` to `autobyteus-browser/` and make that directory the complete, relocatable skill bundle and Python project. Place a vendor-neutral `SKILL.md` at its root and a self-locating Bash launcher at `scripts/autobyteus-browser`. The skill tells any agent to derive `SKILL_DIR` from the actual directory containing the loaded `SKILL.md`; it never assumes `$CODEX_HOME`, another vendor home, `$PATH`, a fixed checkout, or a separately installed CLI.

Extract one `BrowserApplication` boundary. Both the new CLI and retained MCP tools call that boundary. `BrowserApplication` owns command sequencing and delegates browser connection/target resolution to `BrowserRuntime`, policy to explicit URL/artifact/input policy components, and page transformations to focused owned modules. Chrome remains the durable tab-state owner, and opaque CDP target IDs are the only public tab identity.

Each CLI call is a short-lived process: launcher bootstrap -> CLI readiness handshake -> application call -> Chrome operation -> one versioned JSON stdout envelope -> connection cleanup. The first launcher call uses the bundle's `uv.lock` through `uv run --frozen`, so dependency/environment preparation is automatic and requires no human CLI installation. The launcher captures uv/CLI stdout and checks a private CLI-ready marker: if Python never reaches the CLI, it discards/redirects any captured pre-CLI text and emits one bootstrap envelope; if readiness is marked, it forwards the CLI's output and exit status exactly once.

Retained MCP remains separately launchable. Rename `scripts/browser_mcp_stdio.sh` to `scripts/autobyteus-browser-mcp`, update it to the new project/namespace and frozen uv execution, and remove the old path. Streamable HTTP changes its default bind from `0.0.0.0` to `127.0.0.1`; an explicitly configured non-loopback host is still honored but produces a prominent no-auth exposure warning. This is a secure-default/no-broadening refactor, not a new remote-auth system.

## Relevant Behavior And Production-Path Map (Mandatory)

| Behavior ID | Kind (`User`/`System`/`Operational`/`Contract`) | Approved Requirement / Intent And Acceptance-Criteria IDs | Approved Trigger Or Governing Contract | Relevant Existing Behavior And Evidence Reference | Approved Change Or Preserved Outcome | Target Production Path / Lifecycle And Spine ID(s) |
| --- | --- | --- | --- | --- | --- | --- |
| `BEH-001` | Contract | `REQ-001`–`REQ-006`; `AC-001`–`AC-006` | Agent shell command or retained MCP tool call | Current FastMCP -> `TabManager` -> live `Page`; investigation `BEH-001` | Replace server-held tab objects with one shared application boundary and browser-owned IDs; retain explicit targeting | Skill/CLI or MCP adapter -> `BrowserApplication` -> `BrowserRuntime` -> Chrome; `DS-001`, `DS-002`, `DS-005` |
| `BEH-002` | User / Contract | `REQ-002`, `REQ-005`, `REQ-006`; `AC-001`, `AC-005`, `AC-006` | `open-tab`, `attach-tab`, `list-tabs` or MCP equivalents | Current tracked-map semantics; investigation `BEH-002` | List all addressable pages in the first configured context; unique matching returns an opaque CDP target ID; remove unreconstructable metadata | Adapter -> application discovery/open -> runtime target resolver -> result; `DS-001`, `DS-002`, `DS-005` |
| `BEH-003` | Contract | `REQ-001`, `REQ-006`; `AC-002`, `AC-006`, `AC-009` | Navigate/read/screenshot/snapshot/script against explicit ID | Logic is mixed into `tools/*.py`; investigation `BEH-003` | Move all operation behavior behind `BrowserApplication`; adapters only parse/translate | Adapter -> application operation -> resolved page -> operation result; `DS-001`, `DS-002` |
| `BEH-004` | Contract | `REQ-003`, `REQ-004`; `AC-003`, `AC-004` | Non-help CLI invocation | No current CLI output contract; investigation `BEH-008` | Exactly one schema-v1 JSON value on stdout, diagnostics on stderr, stable exit category, including pre-CLI frozen-uv failure | Launcher readiness gate or CLI -> exactly one stdout/exit; `DS-001`, `DS-006` |
| `BEH-005` | User | `REQ-009`, `REQ-010`; `AC-010`, `AC-011` | A coding agent activates the browser skill | No current browser skill; investigation `BEH-008` | Portable skill resolves its own folder, teaches preflight and explicit-ID observe/act/verify workflow, and invokes only bundled launcher | Agent skill loader -> `SKILL.md` -> launcher -> CLI -> JSON -> next command; `DS-003`, `DS-004` |
| `BEH-006` | User / Operational | `REQ-007`, `REQ-008`; `AC-007`, `AC-008` | URL, output, script, or close operation | Arbitrary absolute outputs and global Chrome kill reachable; investigation `BEH-004`, `BEH-006` | Enforce http/https navigation, bounded inputs, workspace-contained artifacts, explicit overwrite, single-target close, and advanced-script confirmation | Application -> policy/runtime -> one page/artifact; `DS-001`, `DS-005` |
| `BEH-007` | Operational | `REQ-011`; `AC-012` | Existing stdio wrapper or streamable-HTTP MCP entry | FastMCP owns logic/state; tracked wrapper names old root/module; HTTP defaults to unauthenticated `0.0.0.0`; investigation `BEH-001` and source log | Retain thin transports, rename/update stdio wrapper, default HTTP to loopback, warn on explicit non-loopback, remove old identity/business/launcher paths | MCP wrapper or HTTP config -> MCP composition -> thin tool -> application -> runtime; `DS-002`, `DS-008` |
| `BEH-008` | Operational / Contract | `REQ-003`, `REQ-007`, `REQ-010`; `AC-003`, `AC-004` | First or later shell invocation from any task CWD | No browser CLI launcher; image/audio demonstrates wrapper-owned uv | `SKILL_DIR` comes from active `SKILL.md`; launcher self-resolves, captures workspace, finds uv, gates on CLI readiness, and emits or forwards exactly one outcome | Skill -> launcher -> captured uv -> readiness branch -> bootstrap JSON or CLI output; `DS-003`, `DS-006` |

## Relevant Supplemental Task Artifacts

| Artifact Path | Purpose | Related Requirement / Acceptance-Criteria IDs (When Applicable) | Relationship To This Design | Status / Approval Applicability |
| --- | --- | --- | --- | --- |
| `tickets/in-progress/browser-mcp-cli-skill/cli-conversion-analysis.md` | Feasibility evidence, CDP identity probe, current tool disposition, CLI/skill principles, and resolved choices | `REQ-001`–`REQ-012`; `AC-001`–`AC-012` | Establishes why the design uses browser-owned IDs, no daemon, task commands, one shared core, and a skill-bundled launcher | Approved requirements-basis supplement, 2026-08-17 |

## Task Design Health Assessment (Mandatory)

- Change posture: `Larger Requirement`
- Current design issue found: `Yes`
- Root cause classification: `Boundary Or Ownership Issue`, with secondary `File Placement Or Responsibility Drift`
- Refactor needed now: `Yes`
- Evidence: MCP nested functions own browser behavior; `TabManager` owns nonportable live objects and aliases; `Context` appears in navigation; server import changes CWD; `UIIntegrator.initialize()` always creates a page; safety policy is distributed; the root/package names describe a transport rather than the resulting capability.
- Design response: Introduce a transport-neutral `BrowserApplication`, a separate runtime/target-resolution owner, explicit contracts/policy, two thin adapters, and a project-root skill bundle. Rename the product root/package namespace so MCP becomes an adapter rather than the product owner.
- Refactor rationale: Adding a CLI beside current tool bodies would either duplicate every operation or force shell commands through MCP. Both preserve the ownership defect and fail the portable skill requirement.
- Intentional deferrals and residual risk: CDP target discovery APIs are experimental at protocol level; real-browser regression tests and the frozen dependency graph mitigate but do not eliminate upstream Chrome/Playwright change risk. Native Windows shell support is deferred; the first release targets Bash-capable macOS/Linux agents. Same-tab commands from independent agents must be sequenced by those agents; explicit target IDs prevent cross-tab ambiguity but cannot define the business ordering of intentionally concurrent actions.

## Terminology

- **Skill root / `SKILL_DIR`**: the absolute directory containing the `SKILL.md` activated by the current agent's skill loader. In target source this is `autobyteus-browser/`.
- **Launcher**: `scripts/autobyteus-browser`, a thin Bash bootstrap facade bundled with the skill.
- **CLI-ready marker**: a launcher-created private temporary file whose path is passed only through an internal environment variable. The CLI writes a fixed readiness token before parsing or emitting output; absence proves that frozen uv/environment/import startup failed before the CLI owned stdout.
- **MCP stdio launcher**: `scripts/autobyteus-browser-mcp`, the renamed supported wrapper for GUI/stdin MCP clients; it is not used by the skill CLI.
- **Canonical tab ID**: an opaque Chrome DevTools Protocol target ID returned by the current configured browser endpoint. It has meaning only while that target exists in that browser.
- **Browser application boundary**: the transport-neutral command owner used by CLI and MCP.
- **Workspace root**: the caller task directory captured before `uv --directory`, or an explicitly supplied valid `AUTOBYTEUS_AGENT_WORKSPACE`; all CLI-created/read artifact paths are confined to it.

## Legacy Removal Policy (Mandatory)

- Policy: `No backward compatibility; remove legacy code paths.`
- Remove the process-local numeric tab registry and do not translate old numeric IDs.
- Remove `close_browser` from MCP and do not expose it in CLI/skill.
- Remove adapter-owned operation implementations after their behavior is moved to `BrowserApplication`.
- Remove import-time workspace `chdir` and use explicit workspace policy.
- Rename the MCP-centric project/package layout cleanly; do not keep forwarding Python modules or a duplicate `browser-mcp/` directory.
- Preserve the `browser-mcp-server` console entry only because MCP is an approved retained adapter, not as a wrapper around removed source paths.
- Rename/update `scripts/browser_mcp_stdio.sh` to `scripts/autobyteus-browser-mcp`; remove the old path and update active README/config references without a forwarding script.

## Persisted Data / State Transition Decision (Mandatory When Persisted Data May Be Affected)

- Stored subject, location, representative shape, and approximate volume: Chrome profile cookies/local storage remain in the configured browser profile; screenshot/result artifacts are files under the agent workspace. Current short tab IDs and live pages exist only in MCP process memory.
- Relevant code-model, serialization, semantic, or physical-store change: Public tab identity changes from process-local numeric aliases to live Chrome target IDs. No Chrome profile or repository data schema changes.
- Normal reader/writer behavior and representative evidence: Chrome/Playwright continue to read/write the same profile and page state. The reconnect probe resolved the same live page by target ID without transforming browser data.
- Required semantics and invariants under direct use: Preserve authenticated browser state, do not delete/replace the profile, do not terminate Chrome, and do not overwrite artifacts without explicit permission.
- Physical-store, privacy/security, disposal/rebuild, and operational constraints: Target IDs are ephemeral references, not stored credentials. Any runtime cache/lock material is disposable and must not be treated as canonical tab state.
- Decision: `Not Affected`
- Decision rationale: Existing persistent data is consumed directly by unchanged Chrome/Playwright mechanisms. Rewriting profile data or migrating old process-local aliases would add corruption/compatibility risk without benefit; old aliases cease to exist with their process.
- Acceptance criteria or design constraints supported: `AC-001`, `AC-005`, `AC-007`, `AC-008`, `AC-009`.

### Migration Plan

N/A — no persisted-data migration is required.

## Data-Flow Spine Inventory

| Spine ID | Scope | Related Behavior ID(s) | Start | End | Governing Owner | Why It Matters |
| --- | --- | --- | --- | --- | --- | --- |
| `DS-001` | Primary End-to-End | `BEH-001`–`BEH-006` | Agent shell CLI arguments | JSON result/error and page/artifact effect | `BrowserApplication` | Main task-command execution path |
| `DS-002` | Primary End-to-End | `BEH-001`–`BEH-003`, `BEH-006`, `BEH-007` | MCP client tool request | MCP structured result/error and page/artifact effect | `BrowserApplication` | Retained MCP path must use the same behavior owner |
| `DS-003` | Primary End-to-End | `BEH-005`, `BEH-008` | Agent skill activation | First executable browser command | `SKILL.md` for procedure; launcher for bootstrap only | Proves cross-agent portable resource discovery and zero human install |
| `DS-004` | Return-Event | `BEH-004`, `BEH-005` | CLI command outcome | Agent's retained `tab_id`, recovery, or next command | CLI envelope contract | Enables observe/act/verify composition without MCP |
| `DS-005` | Bounded Local | `BEH-001`–`BEH-003`, `BEH-006` | Browser operation enters runtime | Playwright disconnected without closing Chrome | `BrowserRuntime` | Connection, first-context selection, target resolution, and cleanup are lifecycle-critical |
| `DS-006` | Bounded Local | `BEH-004`, `BEH-008` | Launcher invocation | Exactly one bootstrap envelope or exactly one forwarded CLI output | `scripts/autobyteus-browser` | Makes first-run uv preparation, readiness ownership, and stdout isolation deterministic |
| `DS-007` | Return-Event | `BEH-006` | Content-heavy application result | Workspace artifact metadata in adapter result | `ArtifactPolicy` under `BrowserApplication` | Prevents token-heavy results and unsafe file writes when output mode is requested |
| `DS-008` | Primary End-to-End | `BEH-007` | MCP operator/client launch configuration | Bound stdio or HTTP FastMCP adapter | MCP composition/configuration | Preserves the supported MCP entry while making launcher rename and HTTP exposure explicit |

## Primary Execution Spine(s)

`DS-001: Agent Bash Tool -> Skill-Bundled Launcher -> CLI Adapter -> BrowserApplication -> BrowserRuntime -> Playwright/CDP -> Chrome Page / Workspace Artifact -> CLI Envelope`

`DS-002: MCP Client -> FastMCP Tool Adapter -> BrowserApplication -> BrowserRuntime -> Playwright/CDP -> Chrome Page / Workspace Artifact -> MCP Structured Result`

`DS-003: Agent Skill Loader -> SKILL.md -> Agent Resolves SKILL_DIR -> scripts/autobyteus-browser -> Frozen uv Runtime -> CLI Help/Health Command`

`DS-008: MCP Client/Operator -> scripts/autobyteus-browser-mcp (stdio) or RuntimeConfig (HTTP) -> FastMCP Server -> Thin Tool -> BrowserApplication`

## Spine Narratives (Mandatory)

| Spine ID | Short Narrative | Main Domain Subject Nodes | Governing Owner | Key Off-Spine Concerns |
| --- | --- | --- | --- | --- |
| `DS-001` | The launcher prepares the bundle runtime, the CLI parses one task command, and `BrowserApplication` validates and performs it through a short browser session before the CLI serializes one envelope. | launcher, CLI, browser application, browser runtime, Chrome page | `BrowserApplication` | contracts, error mapping, workspace policy, DOM cleaning/snapshot |
| `DS-002` | A FastMCP tool maps typed arguments to the same application method, optionally reports adapter-specific progress, and translates the canonical result back to MCP. | MCP tool, browser application, browser runtime, Chrome page | `BrowserApplication` | FastMCP schema and error translation |
| `DS-003` | The active skill names its own root convention; the agent sets `SKILL_DIR` from the loader-provided source location and runs the bundled script, which independently self-locates, captures uv stdout, and gates the outcome on a CLI-ready marker. | skill instructions, launcher, uv, CLI | `SKILL.md` owns procedure; launcher owns pre-CLI bootstrap | optional vendor metadata, missing-uv/startup error |
| `DS-004` | The CLI returns a stable JSON success/error value; the agent retains target IDs, interprets retryability, and chooses the next observe/act/verify step. | envelope, agent workflow | CLI contract | stderr diagnostics, exit code |
| `DS-005` | Runtime serializes in-process access, ensures/attaches to Chrome, selects the configured first context without creating a page, enumerates and resolves opaque target IDs, then disconnects Playwright without closing the page/context/browser. | runtime, context, target resolver, page | `BrowserRuntime` | brui launch/configuration, CDP target-info adapter |
| `DS-006` | The launcher captures caller CWD, finds uv, validates root files, creates private stdout/ready temporary files, and runs quiet frozen uv without `exec`. A CLI that starts writes readiness before output; the launcher forwards its captured stdout/exit once. If readiness is absent, captured uv stdout is redirected to stderr and the launcher emits one fixed bootstrap JSON with exit `3`. | launcher, uv, CLI readiness marker | launcher before readiness; CLI after readiness | PATH probing, caller workspace export, secure temporary cleanup |
| `DS-007` | When requested, application content is serialized by command-specific rules and written only through `ArtifactPolicy`; the returned result contains resolved path/media type/byte count rather than duplicating content. | application result, artifact policy, file, result metadata | `BrowserApplication` | overwrite and path containment |
| `DS-008` | Stdio clients use the renamed self-locating MCP wrapper, while streamable-HTTP operators use validated `RuntimeConfig`. Default HTTP binding is loopback; explicit non-loopback binding logs a no-auth warning. Both compose the same thin MCP tools over `BrowserApplication`. | MCP launcher/config, FastMCP server, tools | MCP composition/configuration | log routing, host/port validation, exposure warning |

## Spine Actors / Main-Line Nodes

| Node | Role On Spine | Concrete Ownership |
| --- | --- | --- |
| `SKILL.md` | Procedural entry | Triggering, skill-root resolution instruction, command sequencing, safe interaction/recovery/cleanup guidance |
| `scripts/autobyteus-browser` | Thin bootstrap facade | Self-location, caller-workspace capture, uv discovery, temporary stdout/readiness gate, frozen execution, fixed pre-CLI failure envelope |
| `autobyteus_browser.cli` | CLI adapter | Readiness marking, argument schema, input-source decoding, application invocation, envelope serialization, stderr/exit mapping |
| `BrowserApplication` | Governing domain-control owner | Command validation/sequencing, operation semantics, cleanup-on-failure, result creation, artifact delegation |
| `BrowserRuntime` | Runtime lifecycle owner | Browser launch/connect/disconnect, first-context selection, target discovery/resolution, no-stray-page invariant |
| Chrome page | External durable live subject | Browser-owned tab state and target identity across client processes |
| FastMCP tools | Thin retained adapter | MCP schema, result/error translation, optional progress only |
| MCP composition/configuration | Retained operational entry | Stdio wrapper, validated transport/host/port, loopback default, non-loopback no-auth warning |

## Ownership Map

- `BrowserApplication` is the only authoritative public Python boundary for browser operations. It owns `health_check`, `list_tabs`, `attach_tab`, `open_tab`, `close_tab`, `navigate`, `read_page`, `screenshot`, `dom_snapshot`, and `run_script`.
- `BrowserRuntime` owns how those operations acquire a context/page and how CDP target IDs are obtained. It does not own command validation, artifact semantics, or adapter output.
- `ArtifactPolicy` owns workspace containment, parent creation, overwrite rules, input-file resolution, and returned resolved paths. It serves `BrowserApplication`; adapters may not resolve files themselves.
- CLI and MCP are thin public facades. They may translate syntax/transport and errors but may not call Playwright, `BrowserRuntime`, cleaning, snapshot JavaScript, or artifact internals directly.
- The skill is procedural guidance. It may compose CLI commands and interpret envelopes, but it may not invoke Python modules directly or recreate browser logic in shell snippets.

## Thin Entry Facades / Public Wrappers

| Facade / Entry Wrapper | Governing Owner Behind It | Why It Exists | Must Not Secretly Own |
| --- | --- | --- | --- |
| `SKILL.md` | CLI contract / `BrowserApplication` | Teaches agent workflow and safety | Browser implementation, target lookup, output parsing code |
| `scripts/autobyteus-browser` | CLI adapter | Portable bootstrap, automatic uv environment, and readiness-based single-output handoff | Command parsing, browser policy, Python business logic |
| `autobyteus_browser.cli` | `BrowserApplication` | Shell syntax and JSON/exit contract | Playwright lifecycle or duplicate validation rules |
| `autobyteus_browser.mcp.tools.*` | `BrowserApplication` | Retained MCP schemas/translations | Tab state, page operations, artifact policy |
| `browser-mcp-server` console entry | MCP server composition | Preserve the approved MCP adapter surface | Legacy `browser_mcp` imports or numeric-ID compatibility |
| `scripts/autobyteus-browser-mcp` | MCP server composition | Self-locating GUI/stdin-safe frozen MCP launch with protocol stdout reserved | CLI envelopes, browser business logic, old namespace fallback |

## Removal / Decommission Plan (Mandatory)

| Item To Remove / Decommission | Why It Becomes Unnecessary | Replaced By Which Owner / File / Structure | Scope | Notes |
| --- | --- | --- | --- | --- |
| `browser-mcp/` root name | Product is no longer MCP-only and must be a named portable skill bundle | `autobyteus-browser/` skill/project root | In This Change | Update root README and all active docs/config examples |
| `src/browser_mcp/` namespace | MCP-centric namespace misstates ownership | `src/autobyteus_browser/` with `mcp/` subpackage | In This Change | No forwarding package |
| `tabs.py`, `BrowserTab`, `TabManager`, numeric allocator | Process-local live-object registry cannot support independent CLI calls | `runtime.py` target resolver using CDP target IDs | In This Change | No persisted alias map or daemon |
| Tool-local `_read_page`, `_screenshot`, `_dom_snapshot`, script normalization and navigation logic | Duplicates/owns application behavior inside MCP | `BrowserApplication` plus focused owned modules | In This Change | Tool files become pure adapters |
| `close_browser` MCP input and `stop_browser` reachability | Can kill unrelated Chrome processes | Explicit `close_tab(tab_id)` only | In This Change | No hidden advanced flag |
| `server.initialize_workspace()` import side effect | Mutates global process CWD and conflates transport/workspace policy | Explicit workspace configuration and `ArtifactPolicy` | In This Change | Server import becomes side-effect-free |
| `types.py` mixed transport types | Needs canonical cross-adapter contracts and stable errors | `contracts.py`, `errors.py` | In This Change | Tight command-specific models |
| Permissive `utils.is_valid_url` and unrestricted `resolve_output_path` | Insufficient safety invariant | `policy.py` | In This Change | Delete obsolete functions/file if empty |
| Old package metadata `browser-mcp-server` as project identity | Capability now has skill/CLI primary surface | Project `autobyteus-browser`; keep MCP console entry | In This Change | MCP command remains as adapter entry only |
| `scripts/browser_mcp_stdio.sh` and old README/config path | Wrapper resolves/imports the removed root/namespace | Rename and update as `scripts/autobyteus-browser-mcp` | In This Change | No forwarding script; keep stdio protocol stdout reserved |
| Streamable-HTTP default host `0.0.0.0` | Unauthenticated all-interface default is broader than needed for a local agent capability | `mcp/config.py` loopback default plus explicit non-loopback warning | In This Change | Explicit operator host remains supported; no auth subsystem added |

## Return Or Event Spine(s)

`DS-004: BrowserApplication Result / BrowserError -> CLI Envelope Encoder -> JSON stdout + Stable Exit Category -> Agent Parses -> Retain tab_id / Retry / Refine Input / Stop`

`DS-007: Large Content Result -> Command Serializer -> ArtifactPolicy -> Workspace File -> Artifact Metadata -> CLI or MCP Result`

No server-push event or streaming replacement is required. MCP navigation progress remains adapter-local and optional; CLI progress/diagnostics use stderr only.

## Bounded Local / Internal Spines

### `DS-005` — browser operation lifecycle

Parent owner: `BrowserRuntime`

`Acquire in-process operation lock -> Ensure browser available -> Connect over CDP -> Select first configured context -> Discover/resolve page target -> Yield runtime session -> Detach CDP sessions -> Disconnect Playwright client -> Release lock`

The runtime must never call `context.new_page()` except when `BrowserApplication.open_tab()` explicitly requests it, and cleanup must never call `stop_browser()` or close a context.

### `DS-006` — launcher bootstrap

Parent owner: `scripts/autobyteus-browser`

`Capture caller PWD -> Resolve SCRIPT_DIR with BASH_SOURCE -> Resolve SKILL_DIR parent -> Validate pyproject/uv.lock -> Locate uv/UV_BIN -> Create stdout + ready temp files/trap -> Export workspace and ready-file path -> Run uv --quiet --directory SKILL_DIR run --frozen autobyteus-browser args with stdout captured -> Inspect ready marker -> Forward CLI output/status OR emit bootstrap envelope/exit 3 -> Remove temp files`

The CLI's console entry writes the fixed readiness token before parsing/help/output. If writing readiness fails, it emits nothing and exits `3`, allowing the launcher to own the bootstrap envelope. Once readiness exists, the CLI owns its normal output contract and the launcher never adds a second envelope. Captured uv stdout from a no-readiness failure is diagnostic and is redirected to stderr before the fixed bootstrap JSON is printed.

### `DS-008` — retained MCP launch and exposure

Parent owner: MCP composition/configuration (`mcp/config.py`, `mcp/server.py`, `scripts/autobyteus-browser-mcp`)

`Stdio: MCP client -> renamed self-locating wrapper -> uv --quiet --directory PROJECT run --frozen browser-mcp-server -> FastMCP stdio`

`HTTP: Operator env -> McpRuntimeConfig validation -> loopback/non-loopback exposure assessment -> FastMCP streamable-http bind`

The current unauthenticated all-interface default is not copied. The established `BROWSER_MCP_HOST` configuration defaults to `127.0.0.1` for streamable HTTP. `localhost`, `127.0.0.0/8`, and `::1` are loopback. If an operator explicitly supplies a non-loopback host such as `0.0.0.0`, configuration accepts it to retain the explicit deployment capability but logs a prominent warning to stderr/server log that the MCP adapter has no built-in authentication and must be protected by a trusted network or external boundary. The refactor adds no authentication, TLS, reverse proxy, or multi-user remote orchestration; those remain outside requirements.

Validation must prove: default streamable HTTP binds loopback; explicit host/port values are passed unchanged after validation; invalid/empty host and invalid port fail before server start; the non-loopback warning appears once; stdio remains unaffected by host settings; and no source/config path silently restores `0.0.0.0` as default.

## Off-Spine Concerns Around The Spine

| Off-Spine Concern | Related Spine ID(s) | Serves Which Owner | Responsibility | Why It Exists | Risk If Misplaced On Main Line |
| --- | --- | --- | --- | --- | --- |
| Canonical contracts | `DS-001`, `DS-002`, `DS-004` | `BrowserApplication` and adapters | Tight tab/result/artifact structures | Prevent transport-specific shape drift | Adapters invent incompatible results |
| Error taxonomy | `DS-001`, `DS-002`, `DS-004`, `DS-006` | Application/adapters | Stable codes, retryability, exit category | Agent recovery requires stable semantics | Exception class names become public API |
| URL/input policy | `DS-001`, `DS-002` | `BrowserApplication` | http/https, enums, bounds, opaque-ID validation | Safety must hold below adapters | MCP and CLI diverge |
| Artifact policy | `DS-001`, `DS-002`, `DS-007` | `BrowserApplication` | Workspace containment, input/output resolution, overwrite | Prevent arbitrary filesystem mutation | Path logic leaks into parsers/tool files |
| HTML cleaning | `DS-001`, `DS-002` | `BrowserApplication.read_page` | raw/text/thorough transform | Existing reusable capability | Application grows transformation internals |
| DOM snapshot program | `DS-001`, `DS-002` | `BrowserApplication.dom_snapshot` | Page-side element capture and result normalization | Large specialized code is reusable | Transport files carry domain script |
| Script normalization/input decoding | `DS-001`, `DS-002` | Application/CLI respectively | Canonical expression execution; safe CLI file/stdin/arg decoding | Avoid fragile shell quoting without leaking files into core | Application becomes shell-aware or adapters diverge |
| Envelope serialization | `DS-001`, `DS-004`, `DS-006` | CLI | Exactly one JSON stdout value | Agent-machine contract | Browser core becomes CLI-specific |
| MCP translation/progress | `DS-002` | MCP adapter | FastMCP schema/errors/progress | Retained transport concern | MCP Context leaks into core |
| MCP launch/configuration | `DS-002`, `DS-008` | MCP composition | Stdio wrapper, transport/host/port validation, loopback default, exposure warning | Retained operational surface must survive rename safely | Launch/security behavior becomes implicit or stale |
| Optional agent metadata | `DS-003` | Skill loader | UI display metadata only | Supports vendors without changing skill contract | Vendor path/runtime assumptions enter `SKILL.md` |

## Ownership Boundaries

1. **Agent procedure -> launcher:** `SKILL.md` may name `$SKILL_DIR/scripts/autobyteus-browser`; it must not name a vendor home or a Python module command. The loader-provided location is the only external path premise.
2. **Launcher -> CLI:** launcher owns environment/bootstrap until the private ready marker is written and captures uv stdout during that interval. After readiness, the CLI owns syntax and machine output; the launcher forwards captured output/status exactly once without interpretation.
3. **Adapter -> application:** both adapters depend only on `BrowserApplication` and canonical contracts/errors. Neither adapter receives `BrowserRuntime` or Playwright objects.
4. **Application -> runtime:** application requests browser operations through a runtime session and opaque target resolver. It never reads `BrowserManager` singleton fields directly.
5. **Application -> policy:** file/URL/input rules are called by application before effects. Adapter-only validation may improve messages but never substitutes for these invariants.
6. **Runtime -> external browser:** connection close means client disconnect only. Page close occurs only for explicit target close or cleanup of a newly created page whose open/navigation failed.
7. **MCP launch/configuration -> MCP adapter:** the stdio wrapper and `McpRuntimeConfig` own process launch/bind decisions only. They compose the retained FastMCP adapter and may not reach application/runtime internals. HTTP default is loopback; explicit non-loopback selection is warned, not silently broadened.

## Boundary Encapsulation Map

| Authoritative Boundary | Internal Owned Mechanism(s) It Encapsulates | Upstream Callers That Must Use The Boundary | Forbidden Bypass Shape | If Boundary API Is Too Thin, Fix By |
| --- | --- | --- | --- | --- |
| `BrowserApplication` | runtime, policies, cleaning, snapshot/script normalization, result construction | CLI, MCP tools, tests of public behavior | adapter -> runtime/page/policy directly | Add a command-specific application method or explicit parameter |
| `BrowserRuntime.session()` | brui manager, Playwright lifecycle, context selection, CDP target info | `BrowserApplication` | application -> `UIIntegrator` or `BrowserManager` fields | Extend session/target APIs |
| `ArtifactPolicy` | root resolution, containment, parent creation, overwrite/read checks | `BrowserApplication` | CLI/MCP -> `Path.resolve` and write | Add explicit input/output resolution method |
| CLI envelope encoder | Ready marking, JSON stdout and exit mapping | CLI main and launcher readiness gate | application prints or logger writes stdout | Add error/result encoder cases |
| Skill launcher | uv discovery, self-root resolution, captured stdout/readiness gate | `SKILL.md` workflows | skill runs `uv`, `.venv/python`, or module directly; launcher unconditionally `exec`s uv | Add launcher behavior/help, not skill shell setup |
| MCP composition/configuration | stdio wrapper, `RuntimeConfig`, warning/log policy | MCP clients/operators | tool modules parse env/bind sockets or old wrapper imports old namespace | Extend `mcp/config.py`/server composition |

## Dependency Rules

Allowed direction:

`SKILL.md -> launcher -> CLI adapter -> BrowserApplication -> {BrowserRuntime, policy, cleaning, DOM/script components} -> brui/Playwright/Chrome`

`MCP stdio wrapper or HTTP RuntimeConfig -> MCP server/tools -> BrowserApplication -> same owned components`

`CLI/MCP adapters -> contracts/errors`

Forbidden shortcuts:

- `SKILL.md -> uv`, `.venv`, `python -m`, MCP protocol, or repository-root CLI wrapper.
- CLI/MCP tool -> Playwright, `BrowserRuntime`, `UIIntegrator`, `BrowserManager`, output path resolver, DOM JavaScript, or HTML cleaner.
- Runtime -> CLI/MCP types or output serialization.
- Application -> FastMCP `Context`, argparse, stdout/stderr, or skill paths.
- `scripts/` -> copied Python browser logic.
- CLI launcher -> unconditional `exec uv` or a second envelope after CLI readiness.
- MCP stdio launcher -> old root/module compatibility path; MCP config -> implicit all-interface default.
- Any path -> `stop_browser()` or a global Chrome kill.
- Any old `browser_mcp` compatibility namespace or numeric-ID fallback.

## Interface Boundary Mapping

| Interface / API / Query / Command / Method | Subject Owned | Responsibility | Accepted Identity Shape(s) | Notes |
| --- | --- | --- | --- | --- |
| `BrowserApplication.health_check()` | browser runtime | Connect without creating page; report endpoint/context/page count | none | May launch browser using existing brui behavior; failure is classified |
| `list_tabs()` | current browser context | Enumerate addressable page metadata | none | All pages in first configured context |
| `attach_tab(url_contains, title_contains)` | existing page discovery | Return exactly one matched page ID/metadata | at least one nonempty matcher | Zero/multiple match are distinct stable errors |
| `open_tab(url, wait_until, timeout_ms)` | new page | Create optionally navigate; return ID | no ID input | Close newly opened page on failed initialization/navigation |
| `close_tab(tab_id)` | one live page | Resolve then close exactly one page | opaque CDP target ID | Never context/browser close |
| `navigate(tab_id, url, wait_until, timeout_ms)` | one live page | Navigate and return response metadata | opaque CDP target ID | http/https only |
| `read_page(tab_id, cleaning_mode, output)` | one live page | Read/clean inline or artifact result | opaque CDP target ID | enum values `raw`, `text`, or `thorough` |
| `screenshot(tab_id, output_file, full_page, format, overwrite)` | one live page/artifact | Capture workspace-contained png/jpeg | opaque target ID + relative path | extension/format consistency |
| `dom_snapshot(tab_id, options, output)` | one live page | Structured visible element snapshot inline/artifact | opaque CDP target ID | element IDs snapshot-local |
| `run_script(tab_id, script, arg, output)` | one live page | Evaluate normalized script and return serializable result | opaque CDP target ID | core accepts script/arg values, not files/stdin |
| `BrowserRuntime.resolve_page(tab_id)` | live Chrome target | Find page by target ID | opaque nonempty bounded string | Uses public Playwright CDP session, no private attributes |
| `ArtifactPolicy.resolve_output(relative_path, overwrite)` | workspace file | Validate containment/existence and prepare parent | relative workspace path | Returns resolved absolute path |
| CLI readiness handshake | launcher/CLI stdout ownership | Prove whether Python CLI started before choosing bootstrap vs forwarded output | launcher-created temporary file path via private env | No public CLI flag; cleaned on every launcher exit |
| `McpRuntimeConfig.from_env()` | retained MCP process | Parse transport/host/port and assess exposure | `stdio` or `streamable-http`, validated host, port 1..65535 | HTTP default `127.0.0.1`; explicit non-loopback logs no-auth warning |

## Interface Boundary Check

| Interface | Responsibility Is Singular? | Identity Shape Is Explicit? | Ambiguous Selector Risk | Corrective Action |
| --- | --- | --- | --- | --- |
| `BrowserApplication.*` command methods | Yes | Yes | Low | Keep command-specific methods; no generic `execute(tool, payload)` |
| `attach_tab` | Yes | Yes | Medium by nature | Require one or both matchers and fail unless exactly one match |
| `resolve_page` | Yes | Yes | Low | Treat ID as opaque and return `TAB_NOT_FOUND` when absent |
| CLI `run-script` input source | Yes | Yes | Medium | Make `--script`, `--script-file`, `--script-stdin` mutually exclusive; same for JSON arg sources |
| Artifact output | Yes | Yes | Low | Relative path + explicit overwrite only |
| CLI readiness handshake | Yes | Yes | Low | Marker is presence/token only; launcher never parses CLI payload |
| MCP runtime config | Yes | Yes | Low | Keep bind policy in `mcp/config.py`; do not add auth claims |

## Main Domain Subject Naming Check

| Node / Subject | Current / Proposed Name | Name Is Natural And Self-Descriptive? | Naming Drift Risk | Corrective Action |
| --- | --- | --- | --- | --- |
| Product/skill root | `browser-mcp` -> `autobyteus-browser` | Yes after rename | Low | Remove old directory references |
| Python namespace | `browser_mcp` -> `autobyteus_browser` | Yes | Low | Place retained adapter under `mcp/` |
| Governing owner | `BrowserApplication` | Yes | Low | Do not rename to generic `Service`/`Manager` |
| Runtime owner | `BrowserRuntime` | Yes | Low | Keep target lifecycle here, not application policy |
| Tab identity | `tab_id` | Yes at public surface | Medium | Document that value is an opaque CDP target ID |
| Existing page discovery | `attach_tab` | Yes for user task language | Low | Clarify it discovers/returns ID; it does not persist registration |

## Existing Capability / Subsystem Reuse Check

| Need / Concern | Existing Capability Area / Subsystem | Decision | Why | If New, Why Existing Areas Are Not Right |
| --- | --- | --- | --- | --- |
| Chrome launch/CDP connection | `brui_core.browser.BrowserManager` | Extend through wrapper boundary | Retain validated browser configuration/launch behavior | New `BrowserRuntime` is required because `UIIntegrator` always creates a page and exposes global-stop behavior |
| HTML cleaning | `cleaning.py` | Reuse/strengthen | Transport-neutral implementation exists | Add strict enum at application/policy boundary |
| DOM snapshot | Current MCP tool script | Move/extend | Existing behavior is valuable and tested | It must leave MCP adapter ownership |
| Script normalization | Current `run_script.py` | Move/extend | Existing expression/body handling is reusable | It must become application-owned |
| CLI/envelope | Image/audio CLI pattern | Create new | Pattern informs shape but browser needs state/error/artifact semantics | No browser CLI exists |
| Launcher/uv bootstrap | Image/audio and MCP launchers | Extend pattern | Self-location/uv discovery are proven | New launcher lives in skill root and preserves caller workspace/fixed JSON |
| MCP stdio launch | `scripts/browser_mcp_stdio.sh` | Extend/rename | It is a current documented public path with useful GUI-PATH/log behavior | Rename to new capability path; no old wrapper retained |
| Agent skill path | Existing bundled-resource skills | Reuse convention | `SKILL_DIR` from directory containing active `SKILL.md` is vendor-neutral | Do not use imagegen's `$CODEX_HOME` example |

## Subsystem / Capability-Area Allocation

| Subsystem / Capability Area | Owns Which Concerns | Related Spine ID(s) | Governing Owner(s) Served | Decision | Notes |
| --- | --- | --- | --- | --- | --- |
| Portable skill bundle | `SKILL.md`, optional vendor metadata, launcher entry | `DS-003`, `DS-006` | Agent workflow / CLI | Create at renamed project root | Project itself is the bundle; no second runtime copy |
| Browser application | command orchestration, canonical results/errors | `DS-001`, `DS-002`, `DS-004`, `DS-007` | `BrowserApplication` | Create | Authoritative shared core |
| Browser runtime | browser/context/target lifecycle | `DS-001`, `DS-002`, `DS-005` | `BrowserRuntime` | Replace `TabManager` path | Chrome owns durable state |
| Browser content | cleaning, DOM snapshot, script normalization | `DS-001`, `DS-002` | `BrowserApplication` | Reuse/move | Focused owned modules |
| Policy | URL/input/artifact rules | `DS-001`, `DS-002`, `DS-007` | `BrowserApplication` | Create/replace utils | Enforced below adapters |
| CLI adapter | argparse, input files/stdin, JSON/exit | `DS-001`, `DS-004` | `BrowserApplication` | Create | No MCP calls |
| MCP adapter | FastMCP composition/tools plus launch/bind configuration | `DS-002`, `DS-008` | `BrowserApplication` and MCP composition | Refactor | Rename stdio wrapper; HTTP default loopback; explicit non-loopback warning |
| Coverage | unit/adapter/launcher/real browser/skill forward tests | all | all | Extend/reorganize | Final durable coverage decisions belong downstream |

## Draft File Responsibility Mapping

| Candidate File | Owning Subsystem | Owner / Boundary | Concrete Concern | Why This Is One File | Reuses Shared Structure? |
| --- | --- | --- | --- | --- | --- |
| `SKILL.md` | skill | procedural facade | portable path and browser workflow | one concise agent instruction source | CLI help/contracts |
| `scripts/autobyteus-browser` | skill/bootstrap | launcher | root/uv/workspace bootstrap and readiness gate | one executable facade | project lock/script |
| `application.py` | application | `BrowserApplication` | all command methods and sequencing | one coherent browser command subject | contracts/runtime/policy/content |
| `runtime.py` | runtime | `BrowserRuntime` | connection/context/target lifecycle | one lifecycle boundary | contracts/errors |
| `contracts.py` | application | canonical contracts | results/enums/artifacts | cross-adapter shared shapes | N/A |
| `errors.py` | application | error taxonomy | stable codes/retry/exit categories | one public failure vocabulary | N/A |
| `policy.py` | policy | URL/artifact/input policy | all effect-bound validation | coherent safety concern | contracts/errors |
| `content.py` / `dom.py` | browser content | transform owners | cleaning versus DOM/script program | split because HTML transformation and page programs change independently | contracts |
| `cli.py` | CLI | thin adapter | parser/decoding/envelope/main | one transport boundary | application/contracts/errors |
| `mcp/config.py`, `mcp/server.py`, `mcp/tools/*.py` | MCP | thin adapter/config | transport config/exposure, composition, and schemas | config is distinct from one-tool adapters | application/contracts/errors |
| `scripts/autobyteus-browser-mcp` | MCP/bootstrap | stdio facade | self-locating frozen stdio launch and log routing | preserves supported GUI/stdin entry cleanly | project console entry |

## Reusable Owned Structures Check

| Repeated Structure / Logic | Candidate Shared File | Owning Subsystem | Why Shared | Redundant Attributes Removed? | Overlapping Representations Removed? | Must Not Become |
| --- | --- | --- | --- | --- | --- | --- |
| Tab/result metadata | `contracts.py` | application | CLI and MCP expose same semantic result | Yes: remove `created_at`, `attached_by`, `attach_state` | Yes: one opaque `tab_id` | Generic untyped response bag |
| Stable browser failures | `errors.py` | application | Both adapters need identical codes/meaning | Yes: no exception-class API | Yes | Transport exception hierarchy |
| Artifact metadata | `contracts.py` + `policy.py` | application/policy | Three content-heavy commands and screenshot return files | Yes | Yes: one `ArtifactResult` | Optional-field kitchen sink |
| Page target lookup | `runtime.py` | runtime | Every tab-scoped command resolves the same ID | Yes: no registry aliases | Yes | Adapter-visible Playwright helper |
| Wait/timeout/enum validation | `policy.py` | policy | Open/navigate and content operations share bounds | Yes | Yes | Parser-only validation |

## Shared Structure / Data Model Tightness Check

| Shared Structure / Type / Schema | One Clear Meaning Per Field? | Redundant Attributes Removed? | Parallel / Overlapping Representation Risk | Corrective Action |
| --- | --- | --- | --- | --- |
| `TabSummary(tab_id,url,title)` | Yes | Yes | Low | Do not add process-local ownership timestamps |
| `ArtifactResult(path,media_type,bytes_written)` | Yes | Yes | Low | Inline result and artifact result are explicit variants, not nullable duplicates |
| `BrowserError(code,message,retryable,exit_category,details)` | Yes | Yes | Low | Keep stack/exception type out of stdout |
| CLI envelope | Yes | Yes | Low | Exactly one of `result` or `error` |
| DOM snapshot element | Yes | Yes | Low | Preserve selector as actionable identity; document `element_id` as snapshot-local only |

## Final File Responsibility Mapping

| File | Owning Subsystem | Owner / Boundary | Concrete Concern | Why This Is One File | Reuses Shared Structure? |
| --- | --- | --- | --- | --- | --- |
| `autobyteus-browser/SKILL.md` | portable skill | procedural facade | Trigger, `SKILL_DIR`, preflight, observe/act/verify, errors, advanced script, cleanup | Single authoritative workflow | CLI help/envelopes |
| `autobyteus-browser/agents/openai.yaml` | optional metadata | vendor metadata only | Display/default prompt | Isolated from portable contract | `SKILL.md` meaning only |
| `autobyteus-browser/scripts/autobyteus-browser` | bootstrap | launcher | Self-root, caller workspace, uv, captured stdout/ready marker, frozen run, pre-CLI bootstrap error | Shell concern only | root project files/CLI readiness protocol |
| `autobyteus-browser/scripts/autobyteus-browser-mcp` | MCP/bootstrap | stdio facade | Self-root, GUI PATH/uv discovery, frozen MCP run, log/stderr routing | Preserves current supported stdio launch under new name | MCP console entry |
| `src/autobyteus_browser/contracts.py` | application | canonical contracts | Enums and tight result/artifact types | Shared semantic shapes | N/A |
| `src/autobyteus_browser/errors.py` | application | error taxonomy | Stable codes/retry/exit metadata | Shared failure vocabulary | N/A |
| `src/autobyteus_browser/policy.py` | policy | safety owner | URL, scalar bounds, workspace input/output paths, overwrite | Effect-bound rules together | contracts/errors |
| `src/autobyteus_browser/runtime.py` | runtime | `BrowserRuntime` | Browser connect/context/target discovery/resolution/disconnect | One lifecycle owner | contracts/errors |
| `src/autobyteus_browser/application.py` | application | `BrowserApplication` | Command methods, sequencing, cleanup, result/artifact choice | One authoritative subject boundary | all core structures |
| `src/autobyteus_browser/cleaning.py` | content | HTML cleaner | raw/text/thorough transform only | Existing focused concern | cleaning enum |
| `src/autobyteus_browser/dom_snapshot.py` | content | DOM snapshot owner | Page JavaScript and response normalization | Large specialized program | DOM contracts |
| `src/autobyteus_browser/script.py` | content | script owner | Script normalization/evaluation preconditions | Distinct advanced capability | errors |
| `src/autobyteus_browser/cli.py` | CLI | adapter | Parser, file/stdin/arg JSON decoding, envelope and exit | Shell boundary | application/contracts/errors |
| `src/autobyteus_browser/mcp/config.py` | MCP | configuration | Server/transport/host/port parsing, loopback default, exposure warning classification | Keeps operational/security policy out of tools | errors/logging |
| `src/autobyteus_browser/mcp/server.py` | MCP | composition | FastMCP lifecycle, config application, warning emission, no import CWD mutation | Transport composition | application/config |
| `src/autobyteus_browser/mcp/tools/*.py` | MCP | thin tools | One MCP schema/translation each | Retains readable public inventory | application/contracts |
| `tests/...` | coverage | verification | Unit, adapter, launcher, real runtime, skill forward scenarios | Separate evidence scopes | public boundaries |

## Applied Patterns

- **Thin adapters over an authoritative application boundary:** CLI and MCP translate only.
- **External durable state with stable identity:** Chrome owns pages; CDP target IDs cross process boundaries.
- **Self-locating bundled launcher:** both skill and launcher resolve from their own bundle location, not caller CWD/PATH.
- **Readiness-gated launcher handoff:** launcher owns uv/pre-Python failure; a private marker transfers stdout ownership exactly once to CLI.
- **Resource-safe short-lived runtime:** connect, operate, disconnect without stopping Chrome.
- **Explicit artifact policy:** all file effects remain workspace-contained and overwrite-aware.
- **Observe -> act -> verify skill loop:** structured page observation precedes advanced script action and is followed by verification.

## Target Subsystem / Folder / File Mapping

| Path | Kind | Owner / Boundary | Responsibility | Why It Belongs Here | Must Not Contain |
| --- | --- | --- | --- | --- | --- |
| `autobyteus-browser/` | Folder | complete capability/skill bundle | Skill, lock, package, docs, launchers, tests | One relocatable unit | Duplicate external runtime |
| `autobyteus-browser/SKILL.md` | File | portable procedure | Agent-neutral instructions | Root location lets the whole project be the skill | Vendor-home paths |
| `autobyteus-browser/agents/openai.yaml` | File | optional vendor metadata | OpenAI UI metadata | Conventional optional metadata | Runtime/path requirements |
| `autobyteus-browser/scripts/` | Folder | entry facades | `autobyteus-browser` CLI launcher and `autobyteus-browser-mcp` stdio launcher | Executables next to skill/project | Browser business logic or old wrapper names |
| `.../scripts/autobyteus-browser` | File | CLI bootstrap | Captured uv/readiness-gated single-output handoff | Owns failures before CLI starts | Application parsing/business logic |
| `.../scripts/autobyteus-browser-mcp` | File | MCP bootstrap | GUI/stdin-safe frozen MCP launch with protocol stdout reserved | Clean successor to tracked wrapper | CLI JSON envelopes or compatibility forwarding |
| `autobyteus-browser/src/autobyteus_browser/` | Folder | shared application/runtime | Canonical capability | Product namespace, not transport namespace | FastMCP at root modules |
| `.../application.py` | File | `BrowserApplication` | Command orchestration | Authoritative core boundary | argparse/FastMCP |
| `.../runtime.py` | File | `BrowserRuntime` | Chrome/CDP lifecycle and target lookup | Main-line runtime depth | CLI/MCP serialization |
| `.../contracts.py` | File | application contracts | Tight shared shapes/enums | Reused across adapters | Generic optional bag |
| `.../errors.py` | File | error taxonomy | Stable error semantics | Reused across adapters | Tracebacks as contract |
| `.../policy.py` | File | policy | URL/input/artifact invariants | Off-spine safety owner | Transport syntax |
| `.../cleaning.py` | File | browser content | HTML transforms | Existing focused behavior | Page lifecycle |
| `.../dom_snapshot.py` | File | browser content | Snapshot program/normalization | Specialized page behavior | MCP decorators |
| `.../script.py` | File | browser content | Script normalization | Advanced capability boundary | CLI file reading |
| `.../cli.py` | File | CLI adapter | Commands/envelopes/exits | Public shell surface | Playwright calls |
| `.../mcp/` | Folder | MCP adapter | Config, server composition, and thin tools | Makes MCP structurally secondary | Core business/state |
| `.../mcp/config.py` | File | MCP configuration | Bind/port/transport validation and exposure assessment | One operational policy owner | Browser operations |
| `autobyteus-browser/tests/unit/` | Folder | coverage | Core/parser/policy/adapter unit tests | Fast deterministic feedback | Real Chrome assumptions |
| `autobyteus-browser/tests/integration/` | Folder | coverage | Launcher, real Chrome, cross-process, skill forward tests | Runtime evidence | Unmarked always-on external tests |

## Folder Boundary Check

| Path / Folder | Intended Structural Depth | Ownership Boundary Is Clear? | Mixed-Layer Or Over-Split Risk | Justification / Corrective Action |
| --- | --- | --- | --- | --- |
| `autobyteus-browser/` | Mixed Justified | Yes | Low | A skill folder intentionally contains its packaged runtime and metadata |
| `src/autobyteus_browser/` | Main-Line Domain-Control | Yes | Low | Application/runtime are primary; focused off-spine files remain nearby because package is compact |
| `src/autobyteus_browser/mcp/` | Transport | Yes | Low | All FastMCP-specific code is isolated here |
| `scripts/` | Transport/bootstrap | Yes | Low | Shell facades only |
| `tests/unit`, `tests/integration` | Mixed Justified | Yes | Low | Split by runtime dependency/evidence scope, not source mirroring |

## Concrete Examples / Shape Guidance

| Topic | Good Example | Bad / Avoided Shape | Why The Example Matters |
| --- | --- | --- | --- |
| Portable invocation | `SKILL_DIR="<directory containing active SKILL.md>"; bash "$SKILL_DIR/scripts/autobyteus-browser" list-tabs` | `$CODEX_HOME/...`, bare `autobyteus-browser`, or `/Users/normy/...` | Works across agent vendors and bundle locations |
| Shared boundary | `CLI -> BrowserApplication.open_tab -> BrowserRuntime` and `MCP -> same method` | CLI calls MCP or copies tool body | Prevents adapter drift |
| Identity | `open-tab` returns opaque target ID used by later process | Save Playwright object or translate to short numeric alias | Browser, not a daemon, owns durable state |
| Safe output | `screenshot --output-file artifacts/page.png` resolved under caller workspace | absolute `/tmp/...` or `../../...` accepted silently | Enforces filesystem boundary |
| Advanced action | snapshot -> choose selector -> `run-script --script-file ...` -> read/snapshot verify | giant inline shell-escaped JS without observation | Skill adds procedural safety; CLI remains deterministic |
| Runtime cleanup | disconnect Playwright client after operation; close page only on explicit close | `stop_browser()` or context close | Preserves unrelated user tabs/session |
| Launcher failure ownership | No ready marker: redirect captured uv stdout to stderr, emit one fixed `bootstrap` JSON, exit `3`; ready marker: forward captured CLI stdout/status only | `exec uv ...` followed by no possible launcher recovery, or unconditional second JSON on any nonzero exit | Distinguishes reachable pre-Python failure from a valid CLI error |
| Retained MCP exposure | HTTP defaults to `127.0.0.1`; explicit `0.0.0.0` is honored with a no-auth warning | Silently retaining unauthenticated `0.0.0.0` default | Documents and tests no-broadening without inventing auth |

Example skill command sequence:

```bash
# The agent replaces the placeholder with the actual directory containing this SKILL.md.
SKILL_DIR="<absolute skill directory supplied by the active skill loader>"
BROWSER_CLI="$SKILL_DIR/scripts/autobyteus-browser"

bash "$BROWSER_CLI" health-check
bash "$BROWSER_CLI" open-tab --url "https://example.com"
# Read result.tab_id from the JSON, then:
bash "$BROWSER_CLI" read-page --tab-id "$TAB_ID" --cleaning-mode text
bash "$BROWSER_CLI" close-tab --tab-id "$TAB_ID"
```

The placeholder is instruction text, not a literal runtime path. `SKILL.md` must explicitly say to use its own loaded source directory and must not guess where an agent vendor stores skills.

Launcher/CLI handoff shape (implementation guidance, not a second public command):

```bash
READY_FILE="$(mktemp)"
STDOUT_FILE="$(mktemp)"
trap 'rm -f "$READY_FILE" "$STDOUT_FILE"' EXIT

set +e
AUTOBYTEUS_BROWSER_CLI_READY_FILE="$READY_FILE" \
  "$UV_PATH" --quiet --directory "$SKILL_DIR" run --frozen \
  autobyteus-browser "$@" >"$STDOUT_FILE"
status=$?
set -e

if grep -qx 'autobyteus-browser-cli-ready-v1' "$READY_FILE"; then
  cat "$STDOUT_FILE"
  exit "$status"
fi

# uv/import output is diagnostic because CLI never took stdout ownership.
cat "$STDOUT_FILE" >&2
printf '%s\n' '{"schema_version":"1","ok":false,"command":"bootstrap","error":{"code":"BOOTSTRAP_FAILED","message":"The bundled browser runtime could not be prepared or started.","retryable":true}}'
exit 3
```

The real launcher also performs fixed prechecks and validates secure temporary-file creation. The CLI entry writes `autobyteus-browser-cli-ready-v1` before parsing/help/output. If it cannot write that marker, it exits `3` without writing stdout, so the launcher remains the sole envelope owner. A normal CLI error may also exit nonzero, but its ready marker forces the forward-only branch and prevents a duplicate bootstrap envelope.

## Backward-Compatibility Rejection Log (Mandatory)

| Candidate Compatibility Mechanism | Why It Was Considered | Rejection Decision | Clean-Cut Replacement / Removal Plan |
| --- | --- | --- | --- |
| Preserve numeric tab aliases in MCP | Existing clients receive them | Rejected | MCP and CLI both expose target IDs; update schemas/tests/docs |
| Persist alias -> target map | Could hide identity change | Rejected | No compatibility state; use target ID directly |
| CLI calls MCP/JSON-RPC | Reuses current implementation superficially | Rejected | Extract `BrowserApplication`; both adapters call it |
| Keep old `browser_mcp` package forwarding imports | Reduces immediate import churn | Rejected | Rename package and update retained console entry directly |
| Keep `close_browser` as hidden/advanced | Existing schema includes it | Rejected | Remove; only explicit one-page close remains |
| PATH shim or vendor home fallback | Shorter command | Rejected | Skill-root-relative bundled launcher |
| Copy package into a separate skill runtime | Makes copied skill self-contained | Rejected | Entire renamed project directory is the skill bundle |
| Accept old permissive cleaning modes/absolute output paths | Avoid behavior breaks | Rejected | Strict enums and workspace policy with stable errors |
| Retain `scripts/browser_mcp_stdio.sh` as forwarding wrapper | Existing README/config may name it | Rejected | Rename/update active references to `scripts/autobyteus-browser-mcp`; delete old path |
| Retain HTTP `0.0.0.0` as implicit default | Avoid bind behavior change | Rejected | Default loopback; explicit non-loopback remains operator-selected with warning |

## Derived Layering (If Useful)

Explanatory only:

1. Portable procedure/bootstrap: `SKILL.md`, `scripts/`.
2. Public adapters: `cli.py`, `mcp/`.
3. Application control: `BrowserApplication`, contracts/errors.
4. Runtime and policy/content concerns: runtime, policy, cleaning, DOM/script.
5. External mechanisms: brui, Playwright/CDP, Chrome, filesystem.

No higher layer may skip the application boundary to call a lower layer that it owns.

## Command And Machine Contract

### Approved command surface

| Command | Required inputs | Important optional inputs | Result subject |
| --- | --- | --- | --- |
| `health-check` | none | none | connectivity/context/page count |
| `list-tabs` | none | none | all current `TabSummary` values |
| `attach-tab` | one/both matcher | `--url-contains`, `--title-contains` | unique `TabSummary` |
| `open-tab` | none | `--url`, `--wait-until`, `--timeout-ms` | opened `TabSummary` |
| `close-tab` | `--tab-id` | none | target ID + `closed=true` |
| `navigate` | `--tab-id`, `--url` | wait mode, timeout | URL/status/ok |
| `read-page` | `--tab-id` | cleaning mode, `--output-file`, `--overwrite` | inline content or artifact metadata |
| `screenshot` | `--tab-id`, `--output-file` | full-page/viewport, format, overwrite | artifact metadata |
| `dom-snapshot` | `--tab-id` | noninteractive, bounding boxes, max elements, output, overwrite | inline snapshot or artifact metadata |
| `run-script` | `--tab-id` plus exactly one script source | JSON arg source, output, overwrite | inline JSON result or artifact metadata |

`run-script` script sources are mutually exclusive: `--script`, `--script-file`, or `--script-stdin`. JSON argument sources are mutually exclusive: `--arg-json` or `--arg-file`. File inputs are resolved through workspace policy. Help remains human-readable; every other path emits one JSON value.

### Success/error envelopes

```json
{"schema_version":"1","ok":true,"command":"open-tab","result":{"tab_id":"OPAQUE_TARGET_ID","url":"https://example.com","title":"Example Domain"}}
```

```json
{"schema_version":"1","ok":false,"command":"read-page","error":{"code":"TAB_NOT_FOUND","message":"The requested tab is closed or unavailable.","retryable":true,"details":{"tab_id":"OPAQUE_TARGET_ID"}}}
```

Stable exit categories:

| Exit | Category | Representative codes |
| --- | --- | --- |
| `0` | success | N/A |
| `2` | usage/validation/policy | `INVALID_ARGUMENT`, `INVALID_URL`, `ARTIFACT_PATH_REJECTED`, `ARTIFACT_EXISTS` |
| `3` | bootstrap/config/connectivity | `BOOTSTRAP_FAILED`, `CONFIGURATION_ERROR`, `BROWSER_UNAVAILABLE` |
| `4` | discovery/target state | `TAB_NOT_FOUND`, `NO_TAB_MATCH`, `AMBIGUOUS_TAB_MATCH` |
| `5` | browser/application operation | `NAVIGATION_TIMEOUT`, `SCRIPT_FAILED`, `BROWSER_OPERATION_FAILED`, `INTERNAL_ERROR` |

Launcher pre-Python errors use command `bootstrap` and fixed strings so shell values never need JSON interpolation. The launcher captures stdout while uv runs and uses `AUTOBYTEUS_BROWSER_CLI_READY_FILE` as a private ownership handshake. No marker means uv/environment/import failed before CLI startup: captured stdout becomes stderr diagnostic, the launcher emits one `BOOTSTRAP_FAILED` envelope, and exits `3`. A valid marker means the CLI started: the launcher prints only the captured CLI stdout and exits with the CLI status, including when that status is nonzero. It never maps “nonzero” alone to bootstrap failure.

The ready-file path is launcher-created with secure temporary-file semantics, never accepted as a public CLI argument, and removed by an exit trap. CLI readiness is written before help/parser/application output. If readiness cannot be written, the CLI emits no stdout and exits `3`, leaving the launcher as sole owner. Python logging is configured to stderr. Tracebacks never appear in stdout and are emitted to stderr only when an explicit debug mode is active.

### Retained MCP operational/security contract

- Console entry: keep `browser-mcp-server`, repointed directly to `autobyteus_browser.mcp.server:main`.
- Stdio wrapper: rename `scripts/browser_mcp_stdio.sh` to `scripts/autobyteus-browser-mcp`; self-resolve the new root, use quiet frozen uv, keep JSON-RPC stdout untouched, and route bootstrap diagnostics to stderr/log. Remove the old script and every active README/config reference.
- Transport owner: `autobyteus_browser.mcp.config.McpRuntimeConfig` parses `BROWSER_MCP_TRANSPORT`, `BROWSER_MCP_HOST`, and `BROWSER_MCP_PORT` before server construction.
- HTTP default: `127.0.0.1`, not `0.0.0.0`.
- Explicit remote bind: a configured non-loopback host is accepted, but `server.main` logs one prominent warning that the server has no built-in authentication and requires a trusted/external protection boundary.
- Auth scope: no authentication/TLS/proxy implementation or multi-user remote-service promise is added.

## Change / Refactor Sequence

1. Rename `browser-mcp/` to `autobyteus-browser/`, rename the distribution/namespace to `autobyteus-browser` / `autobyteus_browser`, and update imports/test discovery without adding forwarding modules.
2. Define canonical contracts and stable browser errors first; encode approved target/list/result semantics and exit categories.
3. Implement `BrowserRuntime` with no-page connection, first-context selection, CDP target-ID discovery/resolution, in-process lifecycle locking, and disconnect-without-browser-close cleanup.
4. Implement strict URL/input/artifact policy, then move/strengthen cleaning, DOM snapshot, and script normalization into transport-neutral files.
5. Implement `BrowserApplication` command methods over runtime/policy/content owners. Cover new-page rollback on failed `open_tab` and exact single-page close.
6. Add CLI parser/input-source handling/envelope mapping, readiness marking, and the `autobyteus-browser` console entry. Validate one-JSON stdout behavior and marker-write failure before launcher work.
7. Add root `SKILL.md`, optional `agents/openai.yaml`, and self-locating `scripts/autobyteus-browser`; capture caller workspace and uv stdout, implement the private ready-file branch, and validate missing-uv, frozen-setup/import failure, CLI success, CLI validation failure, help, relocation, and unrelated-CWD cases without double output.
8. Refactor MCP config/server/tools into the `mcp/` subpackage and thin delegation over one application instance. Move transport/host/port parsing to `mcp/config.py`, default HTTP to loopback, warn on explicit non-loopback, and remove process-local ID state/`close_browser` from schemas.
9. Rename/update `scripts/browser_mcp_stdio.sh` to `scripts/autobyteus-browser-mcp`; point it at the new root/console entry with quiet frozen uv, preserve protocol-stdout/log behavior, and remove the old path without a forwarding wrapper.
10. Remove obsolete `tabs.py`, old tool logic, old namespace/directory, permissive utils, import-time CWD mutation, and old launcher references. Regenerate lock/package metadata as required.
11. Update project/root README and active examples to lead with portable skill/CLI use, name the new MCP wrapper, document loopback default/non-loopback warning, and describe retained MCP separately.
12. Run unit/adapter/launcher tests, isolated real Chrome cross-process tests, retained MCP parity for stdio/HTTP config, skill validation, and fresh-agent forward scenarios. Durable coverage ownership/edits remain subject to downstream coverage investigation and code review.

No temporary dual runtime or compatibility shim may remain after a step is complete. A short implementation-only seam may exist within an uncommitted refactor, but the delivered state has one namespace, one application boundary, and one identity model.

## Key Tradeoffs

- **Whole project as skill bundle:** Larger than a prose-only skill, but it is the only simple way to make the skill relocatable and executable without copying runtime code or relying on a vendor install path.
- **CDP target IDs:** Longer and Chromium-specific, but remove daemon/state-management complexity and are stable across independent clients in the validated probe.
- **Retained MCP:** Preserves an existing transport while increasing adapter/test surface. Thin delegation prevents it from remaining the architecture owner.
- **Loopback HTTP default:** Changes the old all-interface default, but prevents the refactor from silently preserving an unauthenticated broad exposure. Explicit non-loopback deployment remains available with an honest warning rather than an out-of-scope auth implementation.
- **Readiness-gated stdout capture:** Adds two temporary files and delays stdout until command completion, but preserves exactly-one machine output across both uv startup and CLI-owned failures without parsing CLI JSON in Bash.
- **First Chrome context:** Matches current brui behavior and keeps command identity simple. Multi-context selection is deferred rather than guessed.
- **Strict workspace outputs:** Restricts arbitrary absolute paths, but gives agents a reliable safety boundary and explicit artifact paths.
- **Advanced generic script instead of new click/fill commands:** Preserves current capability and scope, but requires stronger skill guidance and shell-safe file/stdin inputs.

## Risks

1. `Target.getTargetInfo`/target discovery behavior is Chromium/CDP-specific and partly experimental; lock versions and run real regression coverage.
2. Browser manager behavior may launch Chrome when absent. Health/open tests must distinguish successful automatic launch from configuration/launch failure without killing an existing browser.
3. Multiple independent clients can intentionally race on the same tab. The skill must keep one tab's observe/action sequence serial; explicit IDs prevent wrong-tab fallback but cannot infer desired ordering.
4. `uv --directory` changes execution context. The launcher must capture/export caller workspace first, and tests must verify output confinement from unrelated CWDs.
5. uv can fail after launcher prechecks but before Python imports. The readiness/captured-stdout protocol is mandatory; any unconditional `exec` reopens `DR-001`.
6. Renaming the package/root is broad. Search-based removal checks must cover README, console scripts (including the old MCP wrapper), tests, active configs, and imports; no old forwarding path may remain.
7. Explicit non-loopback MCP binds remain unauthenticated. Documentation/log warnings prevent accidental exposure, but operators must supply any external protection; remote auth remains outside scope.
8. Large script results may not be JSON serializable. Application/adapter must classify this as a stable script/result serialization error and recommend artifact-safe or simplified output.
9. Skill-loader source paths differ across vendors. The instruction must define `SKILL_DIR` semantically as the directory containing the active `SKILL.md`, not prescribe how a vendor stores it.

## Guidance For Implementation

- Treat `SKILL_DIR="<absolute path to this skill>"` as an agent substitution instruction, never a literal default or environment dependency.
- Keep `SKILL.md` concise and workflow-oriented. Put detailed flags in CLI `--help`; do not duplicate the parser reference in prose.
- The CLI launcher must use `BASH_SOURCE[0]`, `pwd -P`, quoted variables, secure temporary files, an exit trap, `uv --quiet --directory "$SKILL_DIR" run --frozen`, captured stdout, and the ready marker. It must not unconditionally `exec` uv, `cd` the caller shell, parse CLI JSON, or emit uv diagnostics to stdout.
- Capture `CALLER_WORKSPACE="$PWD"` before uv and export `AUTOBYTEUS_AGENT_WORKSPACE` only when the caller has not explicitly set it.
- Write the ready marker before CLI help/parser/application output. If marker write fails, emit no CLI stdout; let the launcher produce the bootstrap envelope. Test nonzero CLI errors separately from pre-CLI uv failures to prove no double envelope.
- Use public Playwright APIs plus page-bound CDP sessions; do not depend on private `_impl_obj` target identifiers.
- Treat target IDs as opaque strings. Do not truncate or derive human aliases.
- `BrowserRuntime` cleanup disconnects its client only. Never call `stop_browser`, close a browser context, or close unrelated pages.
- On `open_tab` failure after page creation, close only that new page before disconnecting.
- Application methods must enforce policy even when called directly by MCP/tests; CLI parser validation is an ergonomics layer, not the invariant owner.
- Make artifact write operations atomic where practical (temporary sibling + replace only when overwrite is allowed) and return resolved path, media type, and byte count.
- Ensure bootstrap, CLI, application, and MCP errors are tested separately so transport mapping does not leak into the core.
- Keep `scripts/autobyteus-browser-mcp` distinct from the skill CLI launcher: it reserves stdout for MCP JSON-RPC, may use `exec`, and routes launch errors to stderr/log rather than a CLI envelope.
- Default streamable HTTP to `127.0.0.1`; warn exactly once for explicit non-loopback hosts and never imply that the retained adapter authenticates clients.
- Do not create `implementation-handoff.md` during solution/design work.
