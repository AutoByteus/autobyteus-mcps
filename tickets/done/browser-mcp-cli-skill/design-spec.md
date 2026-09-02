# Design Spec

## Current-State Read

The original `browser-mcp/` baseline was a long-lived FastMCP server, not a reusable browser capability package. A supported request flowed from an MCP tool registered as a nested function through a process-local `TabManager`, then through `UIIntegrator` and Playwright to Chrome over CDP. `TabManager` owned short numeric IDs mapped to live `UIIntegrator`/`Page` objects. That ownership was coherent only while one MCP process remained alive.

Architecture-level inspection established five coupled original pressures that SR-001 through SR-006 corrected and that remain preserved invariants; items 6 and 7 plus the readiness-to-promotion lifecycle correction form the cumulative SR-009 re-entry:

1. Application behavior is split across MCP-decorated functions, `TabManager`, `utils.py`, and `cleaning.py`; `navigate_to` also depends directly on MCP `Context`.
2. `UIIntegrator.initialize()` always creates a page, so it cannot be used as the connection boundary for list/read/resolve operations without producing stray tabs.
3. The process-local short ID map cannot survive an ordinary one-command CLI process. The approved browser-owned CDP target ID replaces it; an isolated Chrome probe already proved continuity across complete Playwright reconnects.
4. The project identity and layout are MCP-centric even though the target capability is one portable agent skill plus CLI with MCP retained only as a secondary adapter. The README-recommended `scripts/browser_mcp_stdio.sh` is a supported operational entry tied to the old root/module, and streamable HTTP currently defaults to unauthenticated `0.0.0.0`.
5. The checkpointed candidate solved the browser ownership/runtime problem and later solved exact-locator-relative invocation, but exposes AutoByteus product provenance through the skill/catalog/folder, launcher, CLI help/errors/protocol identifiers, MCP identity/logs, package namespace/distribution, README, and tests. The user has explicitly rejected that vocabulary for the agent-facing capability.
6. The generic SR-006 candidate has since passed `ARCH-REV-006`, `IR-005`, and `CRR-008`. Its parser already accepts direct `--script`/`--arg-json` and optional file/stdin sources, but `SKILL.md` prefers file/stdin for nontrivial JavaScript and this design calls large inline shell-escaped JavaScript an anti-shape. The user has explicitly corrected that procedural contract: direct former-MCP arguments are the normal CLI form regardless of code complexity.
7. The current `BrowserRuntime` still imports `BrowserManager` and `get_browser_config` from external `brui-core>=2.0.0`. Direct inspection of `/Users/normy/autobyteus_org/brui_core` shows only those two symbols are used here; the 608-line library also carries unused UI integration, clipboard, Pillow/pyperclip, singleton lifecycle, global Chrome-kill, and Linux-specific launch behavior. The user explicitly approved making browser automation independent so this runtime can evolve within the complete skill bundle.

The current generic candidate preserves explicit tab selection, deterministic unique attach matching, navigation/read/screenshot/DOM/script outcomes, the Chrome/CDP runtime, and retained MCP transports. It has removed implicit/process-local state assumptions, global Chrome termination from supported public paths, unrestricted output paths, permissive enum handling, server-import CWD mutation, and duplicated adapter business logic. SR-009 must preserve all of those outcomes while carrying forward the direct-argument correction, replacing the external runtime mechanism dependency, and making that owned runtime's cross-process establishment atomic through promote/abort. Full evidence and production-path history are recorded in `investigation-notes.md`; the approved tool disposition, shell experience, runtime-ownership decision, and `DR-006` correction are in `cli-conversion-analysis.md`.

## Intended Change

Preserve the implemented complete capability root `browser-automation/`, matching skill/frontmatter/catalog ID, as the relocatable skill bundle and Python project. Keep **Browser Automation** as heading/display name, a generic capability description, `$browser-automation` in optional agent metadata, the self-locating launcher at `scripts/browser`, and CLI program/help identity `browser`. `SKILL.md` continues to name only that bundle-relative resource. The agent resolves it from the directory containing the exact runtime-advertised/read `SKILL.md` and invokes the resolved path; no framework-populated variable, vendor home, PATH entry, embedded checkout, or separately installed CLI is assumed.

Keep the implemented single `BrowserApplication` boundary called by both CLI and retained MCP. `BrowserApplication` owns command sequencing and delegates browser connection/target resolution to `BrowserRuntime`, policy to explicit URL/artifact/input policy components, and page transformations to focused owned modules. Chrome remains the durable tab-state owner, and opaque CDP target IDs remain the only public tab identity.

Each CLI call is a short-lived process: launcher bootstrap -> CLI readiness handshake -> application call -> Chrome operation -> one versioned JSON stdout envelope -> connection cleanup. The first launcher call uses the bundle's `uv.lock` through `uv run --frozen`, so dependency/environment preparation is automatic and requires no human CLI installation. The launcher captures uv/CLI stdout and checks a private CLI-ready marker: if Python never reaches the CLI, it discards/redirects any captured pre-CLI text and emits one bootstrap envelope; if readiness is marked, it forwards the CLI's output and exit status exactly once.

Retained MCP remains separately launchable through generic `scripts/browser-mcp`, default server name `browser-automation`, generic instructions/warnings/logs, and the generic `browser-mcp-server` console entry. Preserve project distribution/namespace `browser-automation` / `browser_automation` and generic capability-owned workspace/debug/readiness/schema identifiers so supported help/errors/debug/results cannot leak the old product term. Streamable HTTP retains the validated loopback default and explicit non-loopback no-auth warning. Every prior active branded identifier remains absent without aliases or fallback reads.

Make ordinary CLI use semantically argument-isomorphic with retained MCP calls: map a snake-case function name to its approved kebab-case task command and each supported user argument to one explicit operation-specific flag. Most flags are the kebab-case argument spelling; documented CLI vocabulary such as MCP `file_path` to `--output-file`, boolean switches, CLI-only artifact extensions, transport-injected context, and deliberately removed global close behavior are explicit exceptions. For `run_script`, the agent normally passes JavaScript directly through `--script` and the structured `arg` value directly through `--arg-json`, using normal Bash quoting even for nontrivial or multiline content. Keep `--script-file`, `--script-stdin`, and `--arg-file` as optional alternate input sources only when content already resides there or an actual shell/process constraint prevents faithful argv transport. Do not teach indirection merely because code is complex. No browser-core, application-boundary, or parser-capability redesign is required.

Replace the external browser-management dependency with a focused owned package at `src/browser_automation/runtime/`. `config.py` validates supported `CHROME_*` settings; `chrome_launcher.py` owns the secure per-port establishment gate, authoritative loopback probe, optional Chrome process-group launch, readiness wait, and exact owned-failure cleanup; `session.py` owns direct `async_playwright()` startup, `connect_over_cdp`, first-context selection, target IDs, and client-only disconnect. Every supported caller acquires the gate before its authoritative readiness decision. A newly launched owner retains that same exclusive gate after `/json/version` becomes ready until Playwright connection and first-context validation either promote the launch irreversibly or abort exact owned cleanup. A caller cannot classify or attach to the endpoint through this runtime while another caller retains abort authority. Remove the old `runtime.py`, `brui-core` metadata/lock entry, imports, and unused transitive UI/clipboard dependencies. Do not create a vendored `brui_core` namespace or reference the sibling checkout. Once promoted, Chrome remains the external durable state owner for later short-lived commands.

## Relevant Behavior And Production-Path Map (Mandatory)

| Behavior ID | Kind (`User`/`System`/`Operational`/`Contract`) | Approved Requirement / Intent And Acceptance-Criteria IDs | Approved Trigger Or Governing Contract | Relevant Existing Behavior And Evidence Reference | Approved Change Or Preserved Outcome | Target Production Path / Lifecycle And Spine ID(s) |
| --- | --- | --- | --- | --- | --- | --- |
| `BEH-001` | Contract | `REQ-001`–`REQ-006`; `AC-001`–`AC-006` | Agent shell command or retained MCP tool call | Current FastMCP -> `TabManager` -> live `Page`; investigation `BEH-001` | Replace server-held tab objects with one shared application boundary and browser-owned IDs; retain explicit targeting | Skill/CLI or MCP adapter -> `BrowserApplication` -> `BrowserRuntime` -> Chrome; `DS-001`, `DS-002`, `DS-005` |
| `BEH-002` | User / Contract | `REQ-002`, `REQ-005`, `REQ-006`; `AC-001`, `AC-005`, `AC-006` | `open-tab`, `attach-tab`, `list-tabs` or MCP equivalents | Current tracked-map semantics; investigation `BEH-002` | List all addressable pages in the first configured context; unique matching returns an opaque CDP target ID; remove unreconstructable metadata | Adapter -> application discovery/open -> runtime target resolver -> result; `DS-001`, `DS-002`, `DS-005` |
| `BEH-003` | Contract | `REQ-001`, `REQ-006`; `AC-002`, `AC-006`, `AC-009` | Navigate/read/screenshot/snapshot/script against explicit ID | Logic is mixed into `tools/*.py`; investigation `BEH-003` | Move all operation behavior behind `BrowserApplication`; adapters only parse/translate | Adapter -> application operation -> resolved page -> operation result; `DS-001`, `DS-002` |
| `BEH-004` | Contract | `REQ-003`, `REQ-004`; `AC-003`, `AC-004` | Non-help CLI invocation | No current CLI output contract; investigation `BEH-008` | Exactly one schema-v1 JSON value on stdout, diagnostics on stderr, stable exit category, including pre-CLI frozen-uv failure | Launcher readiness gate or CLI -> exactly one stdout/exit; `DS-001`, `DS-006` |
| `BEH-005` | User | `REQ-009`, `REQ-010`, `REQ-013`; `AC-010`, `AC-011`, `AC-013` | A coding agent receives `browser-automation/SKILL.md` through the runtime and reads it on demand | Original absence plus branded candidate exposure; investigation source log and naming table | Generic skill metadata names only `scripts/browser`, teaches preflight and explicit-ID observe/act/verify, and invokes the resolved launcher | Runtime projection -> agent reads generic advertised skill -> relative resolution -> launcher -> CLI -> JSON -> next command; `DS-003`, `DS-004` |
| `BEH-006` | User / Operational | `REQ-007`, `REQ-008`; `AC-007`, `AC-008` | URL, output, script, or close operation | Arbitrary absolute outputs and global Chrome kill reachable; investigation `BEH-004`, `BEH-006` | Enforce http/https navigation, bounded inputs, workspace-contained artifacts, explicit overwrite, single-target close, and advanced-script confirmation | Application -> policy/runtime -> one page/artifact; `DS-001`, `DS-005` |
| `BEH-007` | Operational | `REQ-011`, `REQ-013`; `AC-012`, `AC-013` | Stdio wrapper or streamable-HTTP MCP entry | Original MCP-centric state and branded candidate wrapper/server metadata; investigation source log/naming table | Retain thin transports through generic wrapper/server/logs, loopback default, explicit non-loopback warning, and shared application core; remove all old identities | MCP wrapper or HTTP config -> MCP composition -> thin tool -> application -> runtime; `DS-002`, `DS-008` |
| `BEH-008` | Operational / Contract | `REQ-003`, `REQ-007`, `REQ-010`, `REQ-013`; `AC-003`, `AC-004`, `AC-013` | First or later shell invocation from any task CWD | Candidate proves locator-relative readiness-gated launch but uses branded resource/protocol names | Agent resolves `scripts/browser` from `browser-automation/SKILL.md`; generic launcher self-resolves, captures workspace, finds uv, gates readiness, and emits/forwards one outcome | Advertised generic `SKILL.md` -> agent path composition -> launcher -> captured uv -> readiness branch -> bootstrap JSON or CLI output; `DS-003`, `DS-006` |
| `BEH-009` | User / Operational / Contract | `REQ-009`–`REQ-013`; `AC-004`, `AC-010`–`AC-013` | Skill catalog/read, CLI launch/help/result/error/debug, MCP discovery/launch/log, or active documentation | SR-006 generic boundary is implemented and passed CRR-008; investigation preserves the pre-rename inventory | Preserve one capability-oriented vocabulary (`browser-automation`, **Browser Automation**, `scripts/browser`, `browser`, `scripts/browser-mcp`, `browser_automation`) with generic internal protocol/config names and provenance confined to ownership/history | Skill path `DS-003`; CLI `DS-001`/`DS-006`; MCP `DS-002`/`DS-008`; no compatibility path |
| `BEH-010` | User / Contract | `REQ-003`, `REQ-006`, `REQ-009`, `REQ-012`, `REQ-014`; `AC-006`, `AC-009`, `AC-011`, `AC-014` | Agent translates a former MCP capability call into a shell command, especially `run_script(tab_id, script, arg)` | Generic candidate parser supports every input source, but active skill/design prefers file/stdin for complex script text | Direct flags are normal: `run-script --tab-id ... --script '<JavaScript>' --arg-json '<JSON>'`; file/stdin/arg-file remain optional sources only for pre-existing input or a real transport constraint | Runtime-advertised skill -> direct CLI argv -> CLI decoder -> same `BrowserApplication.run_script`; `DS-001`, `DS-003`, `DS-004` |
| `BEH-011` | Operational / Contract | `REQ-001`, `REQ-005`, `REQ-007`, `REQ-010`, `REQ-012`, `REQ-015`; `AC-001`, `AC-002`, `AC-004`, `AC-008`, `AC-009`, `AC-015` | Any CLI/MCP operation needs Chrome/CDP runtime, including concurrent callers at an initially unavailable endpoint | Candidate wraps two external `brui_core` symbols; SR-008's owned design exposed readiness before promotion, so a second caller could attach while the launch owner still had abort authority (`ARCH-REV-007/PREM-004`) | Owned runtime calls Playwright/Chrome directly; every caller gates before authoritative probe; owned launch stays gated through connect/context promote-or-abort; no caller treats still-abortable Chrome as durable; remove external dependency/namespace | Adapter -> `BrowserApplication` -> owned `BrowserRuntime` -> atomic establishment gate/lease -> Playwright/CDP/Chrome; `DS-001`, `DS-002`, `DS-005` |

## Relevant Supplemental Task Artifacts

| Artifact Path | Purpose | Related Requirement / Acceptance-Criteria IDs (When Applicable) | Relationship To This Design | Status / Approval Applicability |
| --- | --- | --- | --- | --- |
| `tickets/in-progress/browser-mcp-cli-skill/cli-conversion-analysis.md` | Feasibility evidence, CDP identity probe, tool disposition, CLI/skill/naming/argument/runtime-ownership/atomic-establishment principles, and resolved choices | `REQ-001`–`REQ-015`; `AC-001`–`AC-015` | Establishes browser-owned IDs, task commands, shared core, relative launcher, generic naming, direct argument mapping, owned browser runtime, and cross-process promotion/abort gate | Initial baseline approved 2026-08-17; locator, capability-vocabulary, argument-isomorphic, and owned-runtime corrections approved 2026-08-18; SR-009 resolves ARCH-REV-007/DR-006 and awaits re-review |

## Task Design Health Assessment (Mandatory)

- Change posture: `Larger Requirement`
- Current design issue found: `Yes`
- Root cause classification: `Boundary Or Ownership Issue`, with secondary `File Placement Or Responsibility Drift`
- Refactor needed now: `Yes`
- Evidence: MCP nested functions own browser behavior; `TabManager` owns nonportable live objects and aliases; `Context` appears in navigation; server import changes CWD; `UIIntegrator.initialize()` always creates a page; safety policy is distributed; the root/package names describe a transport rather than the resulting capability.
- Design response: Introduce a transport-neutral `BrowserApplication`, a separate runtime/target-resolution owner, explicit contracts/policy, two thin adapters, and a project-root skill bundle. Rename the product root/package namespace so MCP becomes an adapter rather than the product owner.
- Refactor rationale: Adding a CLI beside current tool bodies would either duplicate every operation or force shell commands through MCP. Both preserve the ownership defect and fail the portable skill requirement.
- Intentional deferrals and residual risk: CDP target discovery APIs are experimental at protocol level; real-browser regression tests and the frozen dependency graph mitigate but do not eliminate upstream Chrome/Playwright change risk. Native Windows shell support is deferred; the first release targets Bash-capable macOS/Linux agents. Same-tab commands from independent agents must be sequenced by those agents; explicit target IDs prevent cross-tab ambiguity but cannot define the business ordering of intentionally concurrent actions.
- SR-009 design assessment: `ARCH-REV-007` passed `BrowserApplication`, CLI/MCP spines, target identity, direct arguments, owned module allocation, dependency removal, and validation scope. `DR-006` exposed one boundary defect inside `DS-005`: readiness was visible before launch abort authority ended. Retain the per-port establishment gate across readiness and initial connect/context promote-or-abort; require every supported caller to gate before authoritative probe. No new daemon, registry, adapter responsibility, or public behavior is introduced.

## Terminology

- **Runtime-advertised `SKILL.md` locator**: the exact absolute entry-point path presented to the agent through a system-prompt catalog (native AutoByteus) or provider-specific skill projection (Codex/Claude and comparable runtimes). It is model-visible resource context, not a shell variable or an agent-facing load operation.
- **Skill resource path**: a bundle-relative path written in `SKILL.md`, such as `scripts/browser`, which the agent resolves from the directory containing the runtime-advertised `SKILL.md` before shell execution.
- **Launcher**: `scripts/browser`, a thin Bash bootstrap facade bundled with the skill.
- **CLI-ready marker**: a launcher-created private temporary file whose path is passed only through an internal environment variable. The CLI writes a fixed readiness token before parsing or emitting output; absence proves that frozen uv/environment/import startup failed before the CLI owned stdout.
- **MCP stdio launcher**: `scripts/browser-mcp`, the renamed supported wrapper for GUI/stdin MCP clients; it is not used by the skill CLI.
- **Canonical tab ID**: an opaque Chrome DevTools Protocol target ID returned by the current configured browser endpoint. It has meaning only while that target exists in that browser.
- **Browser application boundary**: the transport-neutral command owner used by CLI and MCP.
- **Workspace root**: the caller task directory captured before `uv --directory`, or an explicitly supplied valid `BROWSER_AUTOMATION_WORKSPACE`; all CLI-created/read artifact paths are confined to it.
- **Agent-facing surface**: every capability-owned name/path/content an LLM can receive through catalog metadata, the advertised skill segment, skill/agent metadata, command/help, stdout/stderr/debug, JSON/schema/results, configuration errors, MCP metadata/warnings/logs, or active examples. Active distribution/namespace/protocol identifiers are included because supported failure/debug paths can reveal them.
- **Ownership-only provenance**: explicit repository/project origin or package-author metadata, plus immutable historical tickets/revision/evidence. It may retain AutoByteus but must not feed active skill cognition, invocation, runtime output, or compatibility behavior.
- **Argument-isomorphic CLI mapping**: a semantic mapping in which an MCP function becomes its approved kebab-case task command and each supported user argument becomes one explicit operation-specific flag, without a generic request envelope or mandatory file materialization.
- **Direct argument source**: an argv value supplied with the operation flag itself, notably `--script '<JavaScript>'` and `--arg-json '<JSON>'` for `run-script`.
- **Optional input-source escape hatch**: `--script-file`, `--script-stdin`, or `--arg-file`, used when input already exists in that source or a concrete shell/process limitation prevents faithful direct argv transport; length, multiline form, or complexity alone does not make it preferred.
- **Owned browser runtime**: the `browser_automation.runtime` package that contains all capability-required configuration, Chrome availability/launch, Playwright connection, target resolution, and client-disconnect behavior. It is shared application infrastructure, not part of the MCP adapter.
- **Pre-existing browser**: a Chrome/Chromium process already exposing the configured loopback CDP endpoint before the current runtime invocation. The capability never owns or terminates it.
- **Owned launch attempt**: a Chrome process group started by the current runtime because the authoritative gated probe found the endpoint unavailable. The runtime may terminate that exact group only while its establishment lease remains pending; after promotion, Chrome is deliberately left running for future independent commands.
- **Per-port establishment gate**: the owner-only `fcntl.flock` coordination boundary every supported process acquires before its authoritative readiness probe. A new launch retains it through promote/abort; the empty lock file carries no browser state.
- **Authoritative readiness classification**: the endpoint probe performed only while holding the establishment gate. A ready endpoint under a newly acquired otherwise-unheld gate is durable/no-longer-abortable for this runtime; an unavailable endpoint may create one pending owned launch.
- **Abort authority**: the pending launch lease's exclusive right to terminate only its own process group. It cannot coexist with another supported caller's durable classification; `promote()` clears it before gate release and `abort()` completes cleanup before gate release.

## Capability-Oriented Naming Boundary

| Surface | Required Generic Identity | Removal / Leakage Rule |
| --- | --- | --- |
| Skill/catalog/folder/locator segment | `browser-automation`; locator ends `browser-automation/SKILL.md` | Remove candidate skill ID/folder; runtime-owned ancestor names are outside the capability contract |
| Human/trigger metadata | **Browser Automation** and generic Chrome/Chromium capability description | No product term in `SKILL.md` or `agents/openai.yaml`; avoid generic web-lookup triggering |
| Agent invocation metadata | `$browser-automation`; sole relative resource `scripts/browser` | No alternate/default prompt token, bare PATH command instruction, or branded resource |
| CLI | console/prog `browser`; stderr prefix `browser:` | Help, bootstrap diagnostics, unexpected-error/debug output, and examples remain generic |
| CLI private/config protocol | `BROWSER_AUTOMATION_WORKSPACE`, `BROWSER_AUTOMATION_CLI_READY_FILE`, `BROWSER_AUTOMATION_DEBUG`, token `browser-cli-ready-v1`, generic `browser-cli.*` temp names | No read fallback for branded env names/tokens; behavior and exit/envelope semantics unchanged |
| Browser result schema | outer CLI `schema_version: "1"` unchanged; DOM snapshot schema `browser-dom-snapshot-v1` | No product term in agent-consumed JSON/artifacts |
| MCP | wrapper `scripts/browser-mcp`; console `browser-mcp-server`; default server `browser-automation`; generic instructions/errors/warnings; cache `$HOME/.cache/browser-automation/browser-mcp.log`; existing `BROWSER_MCP_*` config | Remove both prior wrappers, server identity, log/cache path, startup text; tools remain generic |
| Python package | distribution `browser-automation`; namespace `browser_automation` | No import package, distribution/lock record, or console alias for candidate names; prevents uv/debug traceback leakage |
| Active docs/tests | generic root/project README, configs, examples, test constants/fixtures/titles/temp paths; `BROWSER_AUTOMATION_REAL_TESTS` and `BROWSER_AUTOMATION_TEST_CHROME_BIN` | Old token/path absence is asserted separately from functional behavior |
| Allowed provenance | `pyproject.toml` author and root repository README Origin value; immutable historical ticket/review/revision/evidence content | Never consulted as runtime fallback and excluded explicitly—not implicitly—from active-surface scans |

Target skill metadata is concrete:

- Frontmatter `name`: `browser-automation`
- Heading and `agents/openai.yaml` display: `Browser Automation`
- Frontmatter description: `Operate a local Chrome/Chromium session through the bundled browser CLI for explicit-tab navigation, authenticated-page inspection, DOM observation, JavaScript interaction, screenshots, and multi-step browser workflows. Use when an agent must act in or inspect a live browser, especially existing signed-in tabs. Do not use for generic web research or ordinary URL lookup when a non-browser web tool is sufficient.`
- Agent short description: `Automate explicit tabs in a live Chrome session`
- Agent default prompt: `Use $browser-automation to inspect and operate the relevant Chrome tab safely.`

## Owned Browser Runtime Contract

The owned runtime is deliberately narrower than `brui_core`. It supports the browser capability's actual lifecycle and no generic UI/clipboard/process-management API.

| Module / Mechanism | Owned Responsibility | Explicit Non-Responsibility |
| --- | --- | --- |
| `runtime/config.py` / `BrowserRuntimeConfig` | Parse and validate the fixed local endpoint and launch settings below; provide immutable values to launcher/session | MCP bind config, CLI workspace/artifacts, mutable global dict, silent invalid-value fallback |
| `runtime/chrome_launcher.py` / `ChromeLauncher`, `ChromeAvailability` | Acquire the per-port establishment gate before authoritative probe; classify durable ready endpoint or start one owned group; retain gate/abort authority for pending launch; promote or abort atomically | Ungated readiness classification, enumerating/killing arbitrary Chrome, closing a promoted browser, page/context operations |
| `runtime/session.py` / `BrowserRuntime`, `BrowserSession` | Drive pending availability through Playwright connect and first-context success before promotion; abort on initial failure/cancellation; resolve targets; stop Playwright client only | Releasing a pending gate, public process ownership, command policy, adapter serialization |
| `runtime/__init__.py` | Re-export stable `BrowserRuntime`, `BrowserSession`, and testable config/launcher seams | Compatibility exports under `brui_core` or legacy manager APIs |

Runtime configuration is explicit:

| Setting | Default / Validation | Use / Decision |
| --- | --- | --- |
| Endpoint host | Fixed `127.0.0.1` | Browser automation remains local; no remote browser-host surface is added |
| `CHROME_REMOTE_DEBUGGING_PORT` | `9222`; integer `1..65535` | Probe, launch argument, and `connect_over_cdp`; invalid value is `CONFIGURATION_ERROR`, never silent fallback |
| `CHROME_USER_DATA_DIR` | Optional path | Passed only when launching. Chrome 136+ may require a non-default value; existing-endpoint attachment does not reinterpret profile ownership |
| `CHROME_PROFILE_DIRECTORY` | `Profile 1` | Passed only when launching to preserve current profile-selection behavior |
| `CHROME_LOG_PATH` | Platform temporary directory + `browser-automation-chrome.log` | Chrome child stdout/stderr only; parent directories are created safely; no `brui` filename |
| `BROWSER_AUTOMATION_CHROME_BIN` | Optional executable file; otherwise common macOS app and Linux PATH candidates | Generic explicit override plus deterministic supported-platform discovery |
| `CHROME_DOWNLOAD_DIRECTORY` | Removed | Candidate `BrowserRuntime` never consumes the external config value; retaining a parsed no-op would misstate ownership |

Launch coordination uses a secure advisory lock in a private platform-temporary directory keyed by debug port (Bash-capable macOS/Linux is the approved platform boundary). The private directory/file use owner-only permissions and no-follow/create-safe open semantics; `fcntl.flock` supplies kernel ownership. The gate descriptor is explicitly non-inheritable, and Chrome spawns with `close_fds=True`, so the child cannot retain the parent's lock after promote/abort. Acquisition uses nonblocking lock attempts plus async retry under the bounded runtime-establishment deadline so a retained MCP event loop is not blocked. Gate-wait timeout produces retryable `BROWSER_UNAVAILABLE` without probing or acquiring process authority. Cancellation while waiting closes only the caller's descriptor and performs no endpoint probe. The file contains no durable browser identity and may remain as empty coordination material. **Every supported caller acquires this establishment gate before its authoritative probe of `http://127.0.0.1:<port>/json/version`.** No ready-path fast return may bypass the gate. The existing in-process async operation lock prevents same-process tasks from competing on POSIX per-process lock semantics.

Under the gate, `ChromeLauncher.ensure_available()` has exactly two outcomes:

| Authoritative gated observation | Returned `ChromeAvailability` state | Gate / abort authority |
| --- | --- | --- |
| Endpoint already ready | `DURABLE_EXISTING` | Caller did not launch it and has no abort authority. Release the gate before returning; later Playwright connection is attach-first and may fail normally without process cleanup. |
| Endpoint unavailable | `PENDING_OWNED` after executable selection, one process-group spawn, and `/json/version` readiness | Retain the exclusive gate plus private `Popen`/process-group handle. No other supported caller can probe/classify/attach until this lease promotes or aborts. |

For `PENDING_OWNED`, `BrowserRuntime` starts Playwright, calls `connect_over_cdp`, and obtains the first context while the lease still holds the gate. Success calls `promote()`, which first irreversibly clears/discards abort authority and then releases the gate; only then may a waiting caller acquire, observe ready Chrome, and return `DURABLE_EXISTING`. Connection failure, missing first context, timeout, or cancellation calls `abort()` from a `finally`-safe lease boundary. Abort sends bounded `SIGTERM` and, if needed, `SIGKILL` to only the exact owned process group, reaps the owned parent, then releases the gate. A waiting caller subsequently acquires the gate and performs a new authoritative probe; it never inherits the prior classification.

If an owner process crashes, the kernel releases its advisory lock. That dead process can no longer exercise abort authority; a later holder may therefore classify a still-ready orphaned Chrome endpoint as durable. No marker, PID file, daemon, persisted state, or global registry is needed. A lock file's existence alone never means ownership. No process handle, PID, lease state, or gate status enters public JSON.

The child starts with `start_new_session=True`, making its POSIX process-group ID equal to the spawned PID. On early exit or readiness timeout, the same pending lease aborts before unlocking. If an exact owned group is gone but an independently created endpoint is present, the runtime must not kill that replacement; the next gate holder probes and classifies current reality.

Executable resolution is deterministic: validate an explicit executable file from `BROWSER_AUTOMATION_CHROME_BIN`; otherwise try common macOS Google Chrome/Chromium application executables, then Linux `google-chrome`, `google-chrome-stable`, `chromium`, and `chromium-browser` via `shutil.which` plus the currently supported fixed Google Chrome paths. Spawn arguments preserve `--no-first-run`, the configured `--remote-debugging-port`, `--profile-directory`, and optional `--user-data-dir`; stdout/stderr append to the validated generic log path.

The implementation should be a focused independent rewrite against these owned contracts. If any source is copied from the sibling library instead, implementation must first verify the declared MIT terms and retain required attribution in ownership metadata; this must not reintroduce product provenance into agent-facing skill/CLI/MCP vocabulary.

## Verified Agent-Runtime Skill Projection Contract

The target skill is authored once against a relative-resource invariant; it does not branch on agent vendor:

| Runtime evidence | How `SKILL.md` is exposed | Relevant path | Design consequence |
| --- | --- | --- | --- |
| AutoByteus native (`appendConfiguredSkillsCatalog`) | System prompt lists the exact absolute `SKILL.md` path; agent reads it with ordinary file/shell tools. | Canonical configured skill root | Resolve launcher from `dirname(advertised SKILL.md)`; no injected body or shell variable. |
| AutoByteus Codex backend (`CodexWorkspaceSkillMaterializer`) | Existing provider-discoverable skill is reused; otherwise complete root is symlinked for provider discovery. | `<workspace>/.codex/skills/<name>/SKILL.md` | Relative scripts/assets remain usable through the directory symlink; no `.codex` path appears in the skill. |
| AutoByteus Claude backend (`ClaudeWorkspaceSkillMaterializer`) | Complete root is symlinked for provider discovery with project/local setting sources enabled. | `<workspace>/.claude/skills/<name>/SKILL.md` | Relative scripts/assets remain usable through the directory symlink; no `.claude` path appears in the skill. |

`SkillLoader` in the server is an administrative parser, not an agent-facing loading action. The agent-facing path is ordinary on-demand reading plus resource resolution relative to the `SKILL.md` actually advertised/read. Skill packaging makes the capability-controlled path end `browser-automation/SKILL.md`; provider/workspace ancestors remain runtime-owned. The agent invokes the resolved launcher without changing away from its task workspace.

## Legacy Removal Policy (Mandatory)

- Policy: `No backward compatibility; remove legacy code paths.`
- Remove the process-local numeric tab registry and do not translate old numeric IDs.
- Remove `close_browser` from MCP and do not expose it in CLI/skill.
- Remove adapter-owned operation implementations after their behavior is moved to `BrowserApplication`.
- Remove import-time workspace `chdir` and use explicit workspace policy.
- Rename the MCP-centric project/package layout cleanly; do not keep forwarding Python modules or a duplicate `browser-mcp/` directory.
- Preserve the `browser-mcp-server` console entry only because MCP is an approved retained adapter, not as a wrapper around removed source paths.
- Rename/update `scripts/browser_mcp_stdio.sh` to `scripts/browser-mcp`; remove the old path and update active README/config references without a forwarding script.
- Remove candidate `autobyteus-browser/`, `scripts/autobyteus-browser`, `scripts/autobyteus-browser-mcp`, `autobyteus-browser` console/distribution, `autobyteus_browser` imports, `AUTOBYTEUS_*` capability variables, branded readiness/temp/schema identifiers, branded MCP server/logs, and catalog/default-prompt tokens. Do not add aliases, fallback environment reads, forwarding packages/scripts, or path scans.
- Remove `brui-core` from package metadata/lock, remove active `brui_core`/manager imports, and delete the old `runtime.py` after the focused `runtime/` package owns its behavior. Do not vendor a compatibility namespace, reference the sibling checkout, or copy unrelated UI/clipboard/singleton/global-kill code.

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
| `DS-001` | Primary End-to-End | `BEH-001`–`BEH-006`, `BEH-009`–`BEH-011` | Agent shell CLI arguments | JSON result/error and page/artifact effect | `BrowserApplication` | Main task-command path uses generic vocabulary, direct arguments, and the owned runtime |
| `DS-002` | Primary End-to-End | `BEH-001`–`BEH-003`, `BEH-006`, `BEH-007`, `BEH-009`, `BEH-011` | MCP client tool request | MCP structured result/error and page/artifact effect | `BrowserApplication` | Retained MCP path uses the same owned runtime and generic server metadata |
| `DS-003` | Primary End-to-End | `BEH-005`, `BEH-008`, `BEH-009`, `BEH-010` | `browser-automation` skill activation | First executable browser command | `SKILL.md` for procedure; launcher for bootstrap only | Proves portable generic resource discovery, direct CLI use, and zero human install |
| `DS-004` | Return-Event | `BEH-004`, `BEH-005`, `BEH-010` | CLI command outcome | Agent's retained `tab_id`, recovery, or next command | CLI envelope contract | Enables direct-argument observe/act/verify composition without MCP |
| `DS-005` | Bounded Local | `BEH-001`–`BEH-003`, `BEH-006`, `BEH-011` | Browser operation enters owned runtime | Atomic establishment completes, then Playwright disconnects without closing Chrome | `BrowserRuntime` | Every caller's gated classification plus pending launch connect/context promote-or-abort prevents readiness from becoming shared while still abortable |
| `DS-006` | Bounded Local | `BEH-004`, `BEH-008`, `BEH-009` | `scripts/browser` invocation | Exactly one bootstrap envelope or exactly one forwarded CLI output | `scripts/browser` | Makes generic first-run uv preparation, readiness ownership, and stdout isolation deterministic |
| `DS-007` | Return-Event | `BEH-006` | Content-heavy application result | Workspace artifact metadata in adapter result | `ArtifactPolicy` under `BrowserApplication` | Prevents token-heavy results and unsafe file writes when output mode is requested |
| `DS-008` | Primary End-to-End | `BEH-007`, `BEH-009` | MCP operator/client launch configuration | Bound stdio or HTTP FastMCP adapter | MCP composition/configuration | Preserves the MCP entry with generic identity while retaining exposure policy |

## Primary Execution Spine(s)

`DS-001: Agent Bash Tool -> Skill-Bundled Launcher -> CLI Adapter -> BrowserApplication -> BrowserRuntime -> Playwright/CDP -> Chrome Page / Workspace Artifact -> CLI Envelope`

`DS-002: MCP Client -> FastMCP Tool Adapter -> BrowserApplication -> BrowserRuntime -> Playwright/CDP -> Chrome Page / Workspace Artifact -> MCP Structured Result`

`DS-003: Runtime Advertises browser-automation/SKILL.md -> Agent Reads Generic Skill -> Agent Resolves Relative scripts/browser -> Bash Invokes Resolved Launcher -> Frozen uv Runtime -> browser Help/Health Command`

`DS-008: MCP Client/Operator -> scripts/browser-mcp (stdio) or RuntimeConfig (HTTP) -> FastMCP Server -> Thin Tool -> BrowserApplication`

## Spine Narratives (Mandatory)

| Spine ID | Short Narrative | Main Domain Subject Nodes | Governing Owner | Key Off-Spine Concerns |
| --- | --- | --- | --- | --- |
| `DS-001` | `scripts/browser` prepares the bundle, the `browser` CLI parses one task command whose former MCP arguments arrive as explicit flags, and `BrowserApplication` performs it before one generic schema-v1 envelope is serialized. | launcher, CLI, browser application, browser runtime, Chrome page | `BrowserApplication` | contracts, input-source decoding, error mapping, workspace policy, DOM cleaning/snapshot |
| `DS-002` | A generically identified FastMCP tool/server maps typed arguments to the same application method and translates the canonical result back to MCP. | MCP tool, browser application, browser runtime, Chrome page | `BrowserApplication` | FastMCP schema and error translation |
| `DS-003` | The runtime advertises `browser-automation/SKILL.md`; the agent reads its generic metadata/body, resolves `scripts/browser` from that directory, and runs the resulting path. The skill maps operation arguments directly to CLI flags, while the bundled script self-locates, captures uv stdout, and gates the outcome on a generic CLI-ready marker. | runtime-advertised locator, skill instructions, agent path/argument resolution, launcher, uv, CLI | Runtime projection owns locator disclosure; `SKILL.md` owns relative procedure/direct use; launcher owns pre-CLI bootstrap | optional vendor metadata, absent locator, missing-uv/startup error |
| `DS-004` | The CLI returns a stable JSON success/error value; the agent retains target IDs, interprets retryability, and chooses the next observe/act/verify step. A scripted action normally supplies direct `--script` and `--arg-json` values. | envelope, agent workflow | CLI contract | Bash quoting, stderr diagnostics, exit code |
| `DS-005` | Owned runtime validates config, acquires the per-port establishment gate before authoritative probe, and either releases a durable-existing classification or retains the gate across one owned launch's readiness and initial Playwright connect/first-context promote-or-abort. After atomic establishment it resolves opaque targets and disconnects the Playwright client without closing page/context/browser. | runtime config, establishment gate, availability lease, Chrome launcher, Playwright session, context, target resolver, page | `BrowserRuntime` | executable selection, gate acquisition, launch readiness, exact owned-process abort, CDP target-info adapter |
| `DS-006` | The generic launcher captures caller CWD, finds uv, validates root files, creates generic private stdout/ready temporary files, and runs quiet frozen uv without `exec`. A started CLI writes readiness before output; the launcher forwards stdout/exit once. Without readiness it redirects captured uv output to stderr and emits one bootstrap JSON/exit `3`. | launcher, uv, CLI readiness marker | launcher before readiness; CLI after readiness | PATH probing, caller workspace export, secure temporary cleanup |
| `DS-007` | When requested, application content is serialized by command-specific rules and written only through `ArtifactPolicy`; the returned result contains resolved path/media type/byte count rather than duplicating content. | application result, artifact policy, file, result metadata | `BrowserApplication` | overwrite and path containment |
| `DS-008` | Stdio clients use `scripts/browser-mcp`; streamable-HTTP operators use validated `RuntimeConfig`. Default server metadata/logging is generic. HTTP binding remains loopback by default and explicit non-loopback logs the no-auth warning. Both compose the same thin tools over `BrowserApplication`. | MCP launcher/config, FastMCP server, tools | MCP composition/configuration | log routing, host/port validation, exposure warning |

## Spine Actors / Main-Line Nodes

| Node | Role On Spine | Concrete Ownership |
| --- | --- | --- |
| `browser-automation/SKILL.md` | Procedural entry | Generic capability triggering, relative-resource resolution, command sequencing, safe interaction/recovery/cleanup guidance |
| `scripts/browser` | Thin bootstrap facade | Self-location, caller-workspace capture, uv discovery, temporary stdout/readiness gate, frozen execution, fixed pre-CLI failure envelope |
| `browser_automation.cli` | CLI adapter | Readiness marking, argument schema, input-source decoding, application invocation, envelope serialization, stderr/exit mapping |
| `BrowserApplication` | Governing domain-control owner | Command validation/sequencing, operation semantics, cleanup-on-failure, result creation, artifact delegation |
| `browser_automation.runtime` / `BrowserRuntime` | Runtime lifecycle owner | Validated config, endpoint readiness, optional launch, direct Playwright connect/disconnect, first-context target discovery/resolution, no-stray-page and no-global-kill invariants |
| Chrome page | External durable live subject | Browser-owned tab state and target identity across client processes |
| FastMCP tools | Thin retained adapter | MCP schema, result/error translation, optional progress only |
| MCP composition/configuration | Retained operational entry | Stdio wrapper, validated transport/host/port, loopback default, non-loopback no-auth warning |

## Ownership Map

- `BrowserApplication` is the only authoritative public Python boundary for browser operations. It owns `health_check`, `list_tabs`, `attach_tab`, `open_tab`, `close_tab`, `navigate`, `read_page`, `screenshot`, `dom_snapshot`, and `run_script`.
- `BrowserRuntime` owns how those operations validate runtime config, attach or optionally launch, acquire a context/page, obtain CDP target IDs, and disconnect the client. It does not own command policy, artifact semantics, or adapter output.
- `ChromeLauncher` is an internal mechanism under `BrowserRuntime`. It probes loopback CDP first, selects an executable, starts at most one attempt per invocation, waits for readiness, and can terminate only the exact process object it started when that attempt fails. It exposes no global process enumeration/kill API.
- `ArtifactPolicy` owns workspace containment, parent creation, overwrite rules, input-file resolution, and returned resolved paths. It serves `BrowserApplication`; adapters may not resolve files themselves.
- CLI and MCP are thin public facades. They may translate syntax/transport and errors but may not call Playwright, `BrowserRuntime`, cleaning, snapshot JavaScript, or artifact internals directly.
- The skill is procedural guidance. It composes direct CLI commands and interprets envelopes, but it may not invoke Python modules directly, recreate browser logic in shell snippets, or route complex values through files/stdin by default when the matching direct flag can faithfully carry them.
- Capability naming is cross-surface policy owned by the project/skill package, not by individual adapters. Each facade derives its assigned generic identifier from this design; no facade may invent provenance-bearing public text.

## Thin Entry Facades / Public Wrappers

| Facade / Entry Wrapper | Governing Owner Behind It | Why It Exists | Must Not Secretly Own |
| --- | --- | --- | --- |
| `browser-automation/SKILL.md` | CLI contract / `BrowserApplication` | Teaches generic agent workflow and safety | Browser implementation, target lookup, output parsing code, product provenance |
| `scripts/browser` | CLI adapter | Portable bootstrap, automatic uv environment, and readiness-based single-output handoff | Command parsing, browser policy, Python business logic |
| `browser_automation.cli` | `BrowserApplication` | Shell syntax and JSON/exit contract | Playwright lifecycle or duplicate validation rules |
| `browser_automation.mcp.tools.*` | `BrowserApplication` | Retained MCP schemas/translations | Tab state, page operations, artifact policy |
| `browser-mcp-server` console entry | MCP server composition | Preserve the approved MCP adapter surface | Legacy `browser_mcp` imports or numeric-ID compatibility |
| `scripts/browser-mcp` | MCP server composition | Self-locating GUI/stdin-safe frozen MCP launch with protocol stdout reserved | CLI envelopes, browser business logic, old namespace fallback |

## Removal / Decommission Plan (Mandatory)

| Item To Remove / Decommission | Why It Becomes Unnecessary | Replaced By Which Owner / File / Structure | Scope | Notes |
| --- | --- | --- | --- | --- |
| `browser-mcp/` root name | Product is no longer MCP-only and must be a named portable skill bundle | `browser-automation/` skill/project root | In This Change | Update root README and all active docs/config examples |
| `src/browser_mcp/` namespace | MCP-centric namespace misstates ownership | `src/browser_automation/` with `mcp/` subpackage | In This Change | No forwarding package |
| `tabs.py`, `BrowserTab`, `TabManager`, numeric allocator | Process-local live-object registry cannot support independent CLI calls | Owned runtime session target resolver using CDP target IDs | In This Change | No persisted alias map or daemon |
| Tool-local `_read_page`, `_screenshot`, `_dom_snapshot`, script normalization and navigation logic | Duplicates/owns application behavior inside MCP | `BrowserApplication` plus focused owned modules | In This Change | Tool files become pure adapters |
| `close_browser` MCP input and `stop_browser` reachability | Can kill unrelated Chrome processes | Explicit `close_tab(tab_id)` only | In This Change | No hidden advanced flag |
| `server.initialize_workspace()` import side effect | Mutates global process CWD and conflates transport/workspace policy | Explicit workspace configuration and `ArtifactPolicy` | In This Change | Server import becomes side-effect-free |
| `types.py` mixed transport types | Needs canonical cross-adapter contracts and stable errors | `contracts.py`, `errors.py` | In This Change | Tight command-specific models |
| Permissive `utils.is_valid_url` and unrestricted `resolve_output_path` | Insufficient safety invariant | `policy.py` | In This Change | Delete obsolete functions/file if empty |
| Old package metadata `browser-mcp-server` as project identity | Capability now has skill/CLI primary surface | Distribution `browser-automation`, console `browser`; keep generic MCP console entry | In This Change | MCP command remains as adapter entry only |
| `scripts/browser_mcp_stdio.sh` and old README/config path | Wrapper resolves/imports the removed root/namespace | Rename and update as `scripts/browser-mcp` | In This Change | No forwarding script; keep stdio protocol stdout reserved |
| Streamable-HTTP default host `0.0.0.0` | Unauthenticated all-interface default is broader than needed for a local agent capability | `mcp/config.py` loopback default plus explicit non-loopback warning | In This Change | Explicit operator host remains supported; no auth subsystem added |
| Candidate `autobyteus-browser/` bundle/skill/catalog segment | Product provenance is not capability vocabulary and the folder must match the skill name | `browser-automation/` | SR-006 | Remove old directory; no symlink/alternate skill ID |
| Candidate `scripts/autobyteus-browser` and `autobyteus-browser` console/prog | Branded agent invocation/help/diagnostics | `scripts/browser` and `browser` console/prog | SR-006 | No forwarding launcher/console alias |
| Candidate `scripts/autobyteus-browser-mcp`, branded server metadata/logs | MCP-using agents/operators can see the product term | `scripts/browser-mcp`, server `browser-automation`, generic messages/cache/log | SR-006 | No alternate server identity or old log path |
| Candidate `autobyteus_browser`, distribution/lock, `AUTOBYTEUS_*` capability variables, readiness/temp tokens, DOM schema | Supported uv/debug/error/result paths can leak the old term | `browser_automation`, `browser-automation`, `BROWSER_AUTOMATION_*`, `browser-cli-ready-v1`, `browser-dom-snapshot-v1` | SR-006 | Rename imports/tests/lock atomically; no fallback env reads/import package |
| Branded active README/examples/tests/default prompt | Keeps obsolete cognitive/invocation vocabulary alive | Generic active docs, `$browser-automation`, and generic contract tests | SR-006 | Historical tickets/reports/evidence remain immutable context |
| `brui-core` project/lock dependency and `brui_core` imports | Only two symbols are used; separate release/namespace pulls unused UI/clipboard/transitives and policy-conflicting singleton/global-kill behavior into the self-scoped runtime | `src/browser_automation/runtime/{config,chrome_launcher,session}.py` using direct Playwright/stdlib mechanisms | SR-008 | Remove dependency/lock/imports; no sibling editable/path dependency or compatibility namespace |
| `src/browser_automation/runtime.py` external-manager wrapper | One file conflates target sessions with an external lifecycle abstraction that the capability now owns | Focused `runtime/` package; `__init__.py` exports stable `BrowserRuntime`/`BrowserSession` imports | SR-008 | Clean file-to-package move; update imports/tests; no parallel module |
| Unused `UIIntegrator`, clipboard, singleton, Pillow/pyperclip, process enumeration, `kill_all_chrome_processes`, and `stop_browser` code | Not required by browser automation and some behavior violates the no-global-kill invariant | No replacement; only required runtime mechanisms are independently owned | SR-008 | Do not copy/vend these files or expose compatibility APIs |

## Return Or Event Spine(s)

`DS-004: BrowserApplication Result / BrowserError -> CLI Envelope Encoder -> JSON stdout + Stable Exit Category -> Agent Parses -> Retain tab_id / Retry / Refine Input / Stop`

`DS-007: Large Content Result -> Command Serializer -> ArtifactPolicy -> Workspace File -> Artifact Metadata -> CLI or MCP Result`

No server-push event or streaming replacement is required. MCP navigation progress remains adapter-local and optional; CLI progress/diagnostics use stderr only.

## Bounded Local / Internal Spines

### `DS-005` — browser operation lifecycle

Parent owner: `BrowserRuntime`

`Acquire in-process operation lock -> Load/validate owned runtime config -> Acquire cross-process per-port establishment gate -> Authoritatively probe configured loopback CDP endpoint -> [ready: classify DURABLE_EXISTING + release gate] OR [unavailable: select executable + start one owned process group + wait for /json/version while retaining gate + return PENDING_OWNED] -> Start Playwright directly -> Connect over CDP -> Select first configured context -> [pending success: clear abort authority + promote + release gate] OR [pending failure/cancellation: terminate/reap exact group + abort + release gate] -> Discover/resolve page target -> Yield session -> Detach page CDP sessions -> Stop Playwright client only -> Release in-process lock`

The cross-process invariant is: **no supported caller can perform the authoritative probe or attach classification while a live owner retains abort authority.** A ready `DURABLE_EXISTING` result is possible only after acquiring an otherwise-unheld gate, which proves that no cooperating owner is still pending. `PENDING_OWNED` keeps the gate through connection and first-context validation. Promotion removes abort authority before unlock; abort completes exact cleanup before unlock. Lock-file presence is not a state signal, and kernel lock release after owner death is sufficient because the dead owner cannot later abort.

The runtime must never call `context.new_page()` except when `BrowserApplication.open_tab()` explicitly requests it. It has no global process-kill API. A durable-existing endpoint is never terminated. A process from the current launch attempt is terminated only while its gated lease is pending and readiness or initial connection/context establishment fails; after promotion it remains alive for later CLI processes. Normal cleanup never calls browser/context close.

### `DS-006` — launcher bootstrap

Parent owner: `scripts/browser`

`Capture caller PWD -> Resolve SCRIPT_DIR with BASH_SOURCE -> Resolve PROJECT_ROOT parent -> Validate pyproject/uv.lock -> Locate uv/UV_BIN -> Create stdout + ready temp files/trap -> Export workspace and ready-file path -> Run uv --quiet --directory PROJECT_ROOT run --frozen browser args with stdout captured -> Inspect browser-cli-ready-v1 -> Forward CLI output/status OR emit bootstrap envelope/exit 3 -> Remove temp files`

The CLI's console entry writes the fixed readiness token before parsing/help/output. If writing readiness fails, it emits nothing and exits `3`, allowing the launcher to own the bootstrap envelope. Once readiness exists, the CLI owns its normal output contract and the launcher never adds a second envelope. Captured uv stdout from a no-readiness failure is diagnostic and is redirected to stderr before the fixed bootstrap JSON is printed.

### `DS-008` — retained MCP launch and exposure

Parent owner: MCP composition/configuration (`mcp/config.py`, `mcp/server.py`, `scripts/browser-mcp`)

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
| Script normalization/input decoding | `DS-001`, `DS-002` | Application/CLI respectively | Canonical script execution; direct `--script`/`--arg-json` decoding plus optional file/stdin/arg-file sources | Preserve one application script value while keeping direct argv as the normal agent path | Application becomes shell-aware or adapters diverge |
| Runtime establishment/launch | `DS-001`, `DS-002`, `DS-005` | `BrowserRuntime` | Validate config; gate every authoritative probe; choose/start executable only when unavailable; retain pending gate through connect/context promote-or-abort; clean exact owned failure | Makes the bundle independent and prevents ready-but-abortable Chrome from becoming shared | Ungated ready return, early gate release, external library, or adapter regains lifecycle ownership |
| Envelope serialization | `DS-001`, `DS-004`, `DS-006` | CLI | Exactly one JSON stdout value | Agent-machine contract | Browser core becomes CLI-specific |
| MCP translation/progress | `DS-002` | MCP adapter | FastMCP schema/errors/progress | Retained transport concern | MCP Context leaks into core |
| MCP launch/configuration | `DS-002`, `DS-008` | MCP composition | Stdio wrapper, transport/host/port validation, loopback default, exposure warning | Retained operational surface must survive rename safely | Launch/security behavior becomes implicit or stale |
| Optional agent metadata | `DS-003` | Agent framework registry/UI | UI display metadata only | Supports vendors without changing skill contract | Vendor path/runtime assumptions enter `SKILL.md` |
| Capability vocabulary | `DS-001`–`DS-004`, `DS-006`, `DS-008` | Project/skill package | Generic catalog/folder/resource/help/result/error/MCP/package identifiers with ownership-only provenance allowlist | Agents need capability meaning, not product provenance; debug/setup paths can leak internals | Per-file ad hoc labels or branded internal names escape through supported surfaces |

## Ownership Boundaries

1. **Agent procedure -> launcher:** `SKILL.md` names only the relative resource `scripts/browser`; it must not contain an absolute installation path, vendor home, shell-variable prerequisite, or Python module command. The runtime-advertised absolute `SKILL.md` locator is the only external path premise, and the agent composes the executable path before invoking Bash.
2. **Launcher -> CLI:** launcher owns environment/bootstrap until the private ready marker is written and captures uv stdout during that interval. After readiness, the CLI owns syntax and machine output; the launcher forwards captured output/status exactly once without interpretation.
3. **Adapter -> application:** both adapters depend only on `BrowserApplication` and canonical contracts/errors. Neither adapter receives `BrowserRuntime` or Playwright objects.
4. **Application -> runtime:** application requests browser operations through an owned runtime session and opaque target resolver. It never imports Playwright, launcher internals, or an external browser manager.
5. **Application -> policy:** file/URL/input rules are called by application before effects. Adapter-only validation may improve messages but never substitutes for these invariants.
6. **Runtime -> external browser:** acquire the per-port establishment gate before authoritative probe. A ready endpoint under the gate is durable and attaches without kill authority. An unavailable endpoint may create one pending owned group, but the gate remains held through initial Playwright connection/first-context `promote()` or `abort()`. Promotion clears abort authority before unlock; abort completes exact owned cleanup before unlock. Connection close after establishment means Playwright-client disconnect only. Page close occurs only for explicit target close or cleanup of a newly created page whose open/navigation failed.
7. **MCP launch/configuration -> MCP adapter:** the stdio wrapper and `McpRuntimeConfig` own process launch/bind decisions only. They compose the retained FastMCP adapter and may not reach application/runtime internals. HTTP default is loopback; explicit non-loopback selection is warned, not silently broadened.
8. **Capability package -> every public facade:** `browser-automation` naming metadata is authoritative. Skill, launcher, CLI, MCP, schema/config identifiers, active docs, and tests consume their assigned generic names; product ownership metadata does not flow into these facades.

## Boundary Encapsulation Map

| Authoritative Boundary | Internal Owned Mechanism(s) It Encapsulates | Upstream Callers That Must Use The Boundary | Forbidden Bypass Shape | If Boundary API Is Too Thin, Fix By |
| --- | --- | --- | --- | --- |
| `BrowserApplication` | runtime, policies, cleaning, snapshot/script normalization, result construction | CLI, MCP tools, tests of public behavior | adapter -> runtime/page/policy directly | Add a command-specific application method or explicit parameter |
| `BrowserRuntime.session()` | owned config/launcher, establishment-lease completion, direct Playwright lifecycle, context selection, CDP target info | `BrowserApplication` | application -> Playwright/launcher fields or external browser manager | Extend owned session/target APIs; never expose pending lease above runtime |
| `ChromeLauncher.ensure_available()` | per-port gate, authoritative endpoint probe, executable resolution, process spawn, readiness wait, pending lease, promote/abort release | `BrowserRuntime` only | caller probes before gate, ready-path bypasses gate, pending launch unlocks before connect/context outcome, or any global kill | Extend `ChromeAvailability`; never add registry/global kill |
| `ArtifactPolicy` | root resolution, containment, parent creation, overwrite/read checks | `BrowserApplication` | CLI/MCP -> `Path.resolve` and write | Add explicit input/output resolution method |
| CLI envelope encoder | Ready marking, JSON stdout and exit mapping | CLI main and launcher readiness gate | application prints or logger writes stdout | Add error/result encoder cases |
| Skill launcher | uv discovery, self-root resolution, captured stdout/readiness gate | `SKILL.md` workflows | skill runs `uv`, `.venv/python`, or module directly; launcher unconditionally `exec`s uv | Add launcher behavior/help, not skill shell setup |
| MCP composition/configuration | stdio wrapper, `RuntimeConfig`, warning/log policy | MCP clients/operators | tool modules parse env/bind sockets or old wrapper imports old namespace | Extend `mcp/config.py`/server composition |

## Dependency Rules

Allowed direction:

`SKILL.md -> launcher -> CLI adapter -> BrowserApplication -> {owned BrowserRuntime, policy, cleaning, DOM/script components} -> Playwright/CDP/Chrome`

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
- Any candidate branded skill/folder/launcher/console/import/environment/schema/MCP identifier, forwarding alias, or fallback read in active source.
- `SKILL.md` or active examples -> generic payload envelopes or complexity-only preference for `--script-file`, `--script-stdin`, or `--arg-file` over the matching direct flags.
- Any active source/package/lock path -> `brui_core`, `BrowserManager`, `UIIntegrator`, sibling checkout, editable/path dependency, singleton browser state, clipboard/UI helpers, or global Chrome enumeration/kill.
- Any supported runtime path -> authoritative endpoint probe or durable-ready classification without first holding the per-port establishment gate; any `PENDING_OWNED` path -> gate release before `promote()` clears abort authority or `abort()` completes exact cleanup.

## Interface Boundary Mapping

| Interface / API / Query / Command / Method | Subject Owned | Responsibility | Accepted Identity Shape(s) | Notes |
| --- | --- | --- | --- | --- |
| `BrowserApplication.health_check()` | browser runtime | Connect without creating page; report endpoint/context/page count | none | Owned runtime attaches first or launches if unavailable; failure is classified |
| `list_tabs()` | current browser context | Enumerate addressable page metadata | none | All pages in first configured context |
| `attach_tab(url_contains, title_contains)` | existing page discovery | Return exactly one matched page ID/metadata | at least one nonempty matcher | Zero/multiple match are distinct stable errors |
| `open_tab(url, wait_until, timeout_ms)` | new page | Create optionally navigate; return ID | no ID input | Close newly opened page on failed initialization/navigation |
| `close_tab(tab_id)` | one live page | Resolve then close exactly one page | opaque CDP target ID | Never context/browser close |
| `navigate(tab_id, url, wait_until, timeout_ms)` | one live page | Navigate and return response metadata | opaque CDP target ID | http/https only |
| `read_page(tab_id, cleaning_mode, output)` | one live page | Read/clean inline or artifact result | opaque CDP target ID | enum values `raw`, `text`, or `thorough` |
| `screenshot(tab_id, output_file, full_page, format, overwrite)` | one live page/artifact | Capture workspace-contained png/jpeg | opaque target ID + relative path | extension/format consistency |
| `dom_snapshot(tab_id, options, output)` | one live page | Structured visible element snapshot inline/artifact | opaque CDP target ID | element IDs snapshot-local |
| `run_script(tab_id, script, arg, output)` | one live page | Evaluate normalized script and return serializable result | opaque CDP target ID | core accepts direct script/arg values; CLI normally supplies `--script`/`--arg-json` and only decodes optional alternate sources before calling core |
| `BrowserRuntime.resolve_page(tab_id)` | live Chrome target | Find page by target ID | opaque nonempty bounded string | Uses public Playwright CDP session, no private attributes |
| `BrowserRuntimeConfig.from_env()` | local Chrome/CDP runtime | Parse/validate supported runtime settings and resolved endpoint | fixed loopback host, port, optional profile/user-data/executable/log values | No mutable global config dictionary, silent invalid-port fallback, or parsed no-op download setting |
| `ChromeLauncher.ensure_available(config)` | configured endpoint / establishment state | Acquire gate, authoritatively probe, return durable-existing or start/wait and return pending-owned | validated loopback port | Durable-existing releases gate and has no abort; pending-owned retains gate through `promote()`/`abort()`; no global stop |
| `ChromeAvailability.promote()` / `abort()` | one pending owned launch | End abortable establishment exactly once | private process-group handle + held gate | Promote clears abort authority before unlock; abort terminates/reaps exact group before unlock; idempotent terminal state guards cleanup |
| `ArtifactPolicy.resolve_output(relative_path, overwrite)` | workspace file | Validate containment/existence and prepare parent | relative workspace path | Returns resolved absolute path |
| CLI readiness handshake | launcher/CLI stdout ownership | Prove whether Python CLI started before choosing bootstrap vs forwarded output | launcher-created temporary file path via private env | No public CLI flag; cleaned on every launcher exit |
| `McpRuntimeConfig.from_env()` | retained MCP process | Parse transport/host/port and assess exposure | `stdio` or `streamable-http`, validated host, port 1..65535 | HTTP default `127.0.0.1`; explicit non-loopback logs no-auth warning |
| Capability naming contract | active skill/CLI/MCP package | Map each public/runtime surface to one generic identifier and isolate ownership-only provenance | fixed set from `REQ-013` | Static contract, not runtime discovery or alias negotiation |

## Interface Boundary Check

| Interface | Responsibility Is Singular? | Identity Shape Is Explicit? | Ambiguous Selector Risk | Corrective Action |
| --- | --- | --- | --- | --- |
| `BrowserApplication.*` command methods | Yes | Yes | Low | Keep command-specific methods; no generic `execute(tool, payload)` |
| `attach_tab` | Yes | Yes | Medium by nature | Require one or both matchers and fail unless exactly one match |
| `resolve_page` | Yes | Yes | Low | Treat ID as opaque and return `TAB_NOT_FOUND` when absent |
| CLI `run-script` input source | Yes | Yes | Medium | Keep sources mutually exclusive; document `--script` plus `--arg-json` as normal argument-isomorphic use and file/stdin/arg-file only as optional alternate sources |
| Artifact output | Yes | Yes | Low | Relative path + explicit overwrite only |
| CLI readiness handshake | Yes | Yes | Low | Marker is presence/token only; launcher never parses CLI payload |
| MCP runtime config | Yes | Yes | Low | Keep bind policy in `mcp/config.py`; do not add auth claims |
| Browser establishment gate / availability lease | Yes | Yes | Low | All callers gate before authoritative probe; durable-existing has no abort authority; pending-owned retains gate until one terminal promote/abort transition |

## Main Domain Subject Naming Check

| Node / Subject | Current / Proposed Name | Name Is Natural And Self-Descriptive? | Naming Drift Risk | Corrective Action |
| --- | --- | --- | --- | --- |
| Product/skill root and catalog ID | original `browser-mcp`, candidate `autobyteus-browser` -> `browser-automation` | Yes | Low | Folder exactly matches skill name; remove both old active paths |
| Human-facing title | candidate **AutoByteus Browser** -> **Browser Automation** | Yes | Low | Use in heading and agent display metadata |
| Agent launcher / CLI identity | candidate `scripts/autobyteus-browser` / `autobyteus-browser` -> `scripts/browser` / `browser` | Yes | Low | Relative launcher is specific by skill context; CLI help matches basename |
| Python namespace | original `browser_mcp`, candidate `autobyteus_browser` -> `browser_automation` | Yes | Low | Place retained adapter under `mcp/`; no import alias |
| MCP identity | candidate branded wrapper/server -> `scripts/browser-mcp` / `browser-automation` | Yes | Low | Generic MCP console `browser-mcp-server` remains |
| Governing owner | `BrowserApplication` | Yes | Low | Do not rename to generic `Service`/`Manager` |
| Runtime owner | `BrowserRuntime` | Yes | Low | Keep target lifecycle here, not application policy |
| Runtime mechanism files | `runtime/config.py`, `runtime/chrome_launcher.py`, `runtime/session.py` | Yes | Low | Keep config, process launch, and Playwright session responsibilities distinct; package facade exposes the stable seam |
| Tab identity | `tab_id` | Yes at public surface | Medium | Document that value is an opaque CDP target ID |
| Existing page discovery | `attach_tab` | Yes for user task language | Low | Clarify it discovers/returns ID; it does not persist registration |

## Existing Capability / Subsystem Reuse Check

| Need / Concern | Existing Capability Area / Subsystem | Decision | Why | If New, Why Existing Areas Are Not Right |
| --- | --- | --- | --- | --- |
| Chrome launch/CDP connection | Candidate wrapper over `brui_core.browser.BrowserManager` | Replace with focused owned runtime | Only two external symbols are used; current application-facing `BrowserRuntime` seam and behavior are reusable | External release, unused UI/clipboard/transitives, singleton/global-kill, and Linux-only assumptions conflict with self-scoped ownership |
| HTML cleaning | `cleaning.py` | Reuse/strengthen | Transport-neutral implementation exists | Add strict enum at application/policy boundary |
| DOM snapshot | Current MCP tool script | Move/extend | Existing behavior is valuable and tested | It must leave MCP adapter ownership |
| Script normalization | Current `run_script.py` | Move/extend | Existing expression/body handling is reusable | It must become application-owned |
| CLI/envelope | Image/audio CLI pattern | Create new | Pattern informs shape but browser needs state/error/artifact semantics | No browser CLI exists |
| Launcher/uv bootstrap | Image/audio and MCP launchers | Extend pattern | Self-location/uv discovery are proven | New launcher lives in skill root and preserves caller workspace/fixed JSON |
| MCP stdio launch | `scripts/browser_mcp_stdio.sh` | Extend/rename | It is a current documented public path with useful GUI-PATH/log behavior | Rename to new capability path; no old wrapper retained |
| Agent skill path | Existing bundled-resource skills plus user-confirmed framework model | Refine convention | Keep `scripts/browser` relative inside `SKILL.md`; resolve it from the runtime-advertised absolute `SKILL.md` locator at use time | Do not use imagegen's `$CODEX_HOME`, assume `SKILL_DIR`, or embed an installation path |

## Subsystem / Capability-Area Allocation

| Subsystem / Capability Area | Owns Which Concerns | Related Spine ID(s) | Governing Owner(s) Served | Decision | Notes |
| --- | --- | --- | --- | --- | --- |
| Portable skill bundle | `SKILL.md`, optional vendor metadata, launcher entry | `DS-003`, `DS-006` | Agent workflow / CLI | Create at renamed project root | Project itself is the bundle; no second runtime copy |
| Browser application | command orchestration, canonical results/errors | `DS-001`, `DS-002`, `DS-004`, `DS-007` | `BrowserApplication` | Create | Authoritative shared core |
| Browser runtime | validated config, endpoint probe/optional launch, Playwright connection, context/target lifecycle | `DS-001`, `DS-002`, `DS-005` | `BrowserRuntime` | Replace external-manager wrapper with owned `runtime/` package | Chrome owns durable state; no global stop |
| Browser content | cleaning, DOM snapshot, script normalization | `DS-001`, `DS-002` | `BrowserApplication` | Reuse/move | Focused owned modules |
| Policy | URL/input/artifact rules | `DS-001`, `DS-002`, `DS-007` | `BrowserApplication` | Create/replace utils | Enforced below adapters |
| CLI adapter | argparse, input files/stdin, JSON/exit | `DS-001`, `DS-004` | `BrowserApplication` | Create | No MCP calls |
| MCP adapter | FastMCP composition/tools plus launch/bind configuration | `DS-002`, `DS-008` | `BrowserApplication` and MCP composition | Refactor | Rename stdio wrapper; HTTP default loopback; explicit non-loopback warning |
| Coverage | unit/adapter/launcher/real browser/skill forward tests | all | all | Extend/reorganize | Final durable coverage decisions belong downstream |

## Draft File Responsibility Mapping

| Candidate File | Owning Subsystem | Owner / Boundary | Concrete Concern | Why This Is One File | Reuses Shared Structure? |
| --- | --- | --- | --- | --- | --- |
| `SKILL.md` | skill | procedural facade | `browser-automation` metadata, sole `scripts/browser` resource, runtime-locator procedure, and browser workflow | one concise agent instruction source | CLI help/contracts |
| `scripts/browser` | skill/bootstrap | launcher | root/uv/workspace bootstrap and readiness gate | one executable facade | project lock/script |
| `application.py` | application | `BrowserApplication` | all command methods and sequencing | one coherent browser command subject | contracts/runtime/policy/content |
| `runtime/config.py` | runtime | `BrowserRuntimeConfig` | immutable validated endpoint/launch inputs | separate pure boundary with dense config tests | errors |
| `runtime/chrome_launcher.py` | runtime | `ChromeLauncher` / `ChromeAvailability` | per-port establishment gate, authoritative probe, executable/spawn/wait, pending lease, atomic promote/abort and failed-group cleanup | process ownership transition is explicit and testable across session establishment | config/errors |
| `runtime/session.py` | runtime | `BrowserRuntime` / `BrowserSession` | direct Playwright connection, first context, target lookup, client disconnect | one CDP session lifecycle boundary | config/launcher/contracts/errors |
| `runtime/__init__.py` | runtime | package facade | stable runtime exports | clean file-to-package migration seam | owned modules only |
| `contracts.py` | application | canonical contracts | results/enums/artifacts | cross-adapter shared shapes | N/A |
| `errors.py` | application | error taxonomy | stable codes/retry/exit categories | one public failure vocabulary | N/A |
| `policy.py` | policy | URL/artifact/input policy | all effect-bound validation | coherent safety concern | contracts/errors |
| `content.py` / `dom.py` | browser content | transform owners | cleaning versus DOM/script program | split because HTML transformation and page programs change independently | contracts |
| `cli.py` | CLI | thin adapter | parser/decoding/envelope/main | one transport boundary | application/contracts/errors |
| `mcp/config.py`, `mcp/server.py`, `mcp/tools/*.py` | MCP | thin adapter/config | transport config/exposure, composition, and schemas | config is distinct from one-tool adapters | application/contracts/errors |
| `scripts/browser-mcp` | MCP/bootstrap | stdio facade | self-locating frozen stdio launch and log routing | preserves supported GUI/stdin entry cleanly | project console entry |

## Reusable Owned Structures Check

| Repeated Structure / Logic | Candidate Shared File | Owning Subsystem | Why Shared | Redundant Attributes Removed? | Overlapping Representations Removed? | Must Not Become |
| --- | --- | --- | --- | --- | --- | --- |
| Tab/result metadata | `contracts.py` | application | CLI and MCP expose same semantic result | Yes: remove `created_at`, `attached_by`, `attach_state` | Yes: one opaque `tab_id` | Generic untyped response bag |
| Stable browser failures | `errors.py` | application | Both adapters need identical codes/meaning | Yes: no exception-class API | Yes | Transport exception hierarchy |
| Artifact metadata | `contracts.py` + `policy.py` | application/policy | Three content-heavy commands and screenshot return files | Yes | Yes: one `ArtifactResult` | Optional-field kitchen sink |
| Page target lookup | `runtime/session.py` | runtime | Every tab-scoped command resolves the same ID | Yes: no registry aliases | Yes | Adapter-visible Playwright helper |
| Chrome availability/launch | `runtime/chrome_launcher.py` | runtime | CLI/MCP share one attach-first/launch-if-absent policy | Yes: no external manager/singleton | Yes | Generic process manager/global kill utility |
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
| `browser-automation/SKILL.md` | portable skill | procedural facade | Generic name/description/heading, `scripts/browser`, locator resolution, preflight, observe/act/verify, errors, advanced script, cleanup | Single authoritative workflow | CLI help/envelopes |
| `browser-automation/agents/openai.yaml` | optional metadata | vendor metadata only | **Browser Automation** display, generic description, `$browser-automation` prompt | Isolated from portable contract | `SKILL.md` meaning only |
| `browser-automation/pyproject.toml` and `uv.lock` | package | distribution/entry/dependency metadata | Generic distribution/entries/package and direct Playwright dependency; no `brui-core` record; author provenance only | Makes frozen bundle self-scoped and prevents stale external runtime coupling | Legacy entries/import aliases, `brui-core`, sibling paths |
| `browser-automation/README.md` and repository root `README.md` | documentation | active operator/project guidance | Generic capability/examples; root Origin column may retain ownership | Keeps operational instructions aligned | Old path/token except origin metadata |
| `browser-automation/scripts/browser` | bootstrap | launcher | Self-root, caller workspace, uv, captured stdout/ready marker, frozen run, pre-CLI bootstrap error | Shell concern only | root project files/CLI readiness protocol |
| `browser-automation/scripts/browser-mcp` | MCP/bootstrap | stdio facade | Self-root, GUI PATH/uv discovery, frozen MCP run, log/stderr routing | Preserves current supported stdio launch under new name | MCP console entry |
| `src/browser_automation/contracts.py` | application | canonical contracts | Enums and tight result/artifact types | Shared semantic shapes | N/A |
| `src/browser_automation/errors.py` | application | error taxonomy | Stable codes/retry/exit metadata | Shared failure vocabulary | N/A |
| `src/browser_automation/policy.py` | policy | safety owner | URL, scalar bounds, workspace input/output paths, overwrite | Effect-bound rules together | contracts/errors |
| `src/browser_automation/runtime/__init__.py` | runtime | package facade | Stable `BrowserRuntime`/`BrowserSession` exports | Clean public internal import seam | compatibility manager exports |
| `src/browser_automation/runtime/config.py` | runtime | `BrowserRuntimeConfig` | Immutable validated loopback endpoint/profile/executable/log configuration | Pure input boundary | MCP/workspace config |
| `src/browser_automation/runtime/chrome_launcher.py` | runtime | `ChromeLauncher` / `ChromeAvailability` | Cross-process establishment gate, authoritative CDP probe, executable/spawn/readiness, pending ownership, promote/abort, failed-owned-group cleanup | One process-establishment owner | ungated ready return, global process enumeration/kill |
| `src/browser_automation/runtime/session.py` | runtime | `BrowserRuntime` / `BrowserSession` | Direct Playwright start/connect, context/target resolution, client-only disconnect | One connection/target lifecycle owner | adapter serialization/browser close |
| `src/browser_automation/application.py` | application | `BrowserApplication` | Command methods, sequencing, cleanup, result/artifact choice | One authoritative subject boundary | all core structures |
| `src/browser_automation/cleaning.py` | content | HTML cleaner | raw/text/thorough transform only | Existing focused concern | cleaning enum |
| `src/browser_automation/dom_snapshot.py` | content | DOM snapshot owner | Page JavaScript and response normalization | Large specialized program | DOM contracts |
| `src/browser_automation/script.py` | content | script owner | Script normalization/evaluation preconditions | Distinct advanced capability | errors |
| `src/browser_automation/cli.py` | CLI | adapter | Parser, file/stdin/arg JSON decoding, envelope and exit | Shell boundary | application/contracts/errors |
| `src/browser_automation/mcp/config.py` | MCP | configuration | Server/transport/host/port parsing, loopback default, exposure warning classification | Keeps operational/security policy out of tools | errors/logging |
| `src/browser_automation/mcp/server.py` | MCP | composition | FastMCP lifecycle, config application, warning emission, no import CWD mutation | Transport composition | application/config |
| `src/browser_automation/mcp/tools/*.py` | MCP | thin tools | One MCP schema/translation each | Retains readable public inventory | application/contracts |
| `tests/...` | coverage | verification | Unit, adapter, launcher, real runtime, skill forward scenarios | Separate evidence scopes | public boundaries |

## Applied Patterns

- **Thin adapters over an authoritative application boundary:** CLI and MCP translate only.
- **External durable state with stable identity:** Chrome owns pages; CDP target IDs cross process boundaries.
- **Self-locating bundled launcher:** both skill and launcher resolve from their own bundle location, not caller CWD/PATH.
- **Readiness-gated launcher handoff:** launcher owns uv/pre-Python failure; a private marker transfers stdout ownership exactly once to CLI.
- **Resource-safe short-lived runtime:** connect, operate, disconnect without stopping Chrome.
- **Owned narrow runtime instead of library-shaped vendoring:** keep only config/launch/session mechanisms required by this capability; no external manager, compatibility namespace, unused UI/clipboard code, or global kill.
- **Explicit artifact policy:** all file effects remain workspace-contained and overwrite-aware.
- **Observe -> act -> verify skill loop:** structured page observation precedes advanced script action and is followed by verification.
- **Capability-oriented vocabulary with ownership isolation:** every active agent/CLI/MCP/runtime surface uses generic names; provenance survives only in author/origin metadata and immutable history.

## Target Subsystem / Folder / File Mapping

| Path | Kind | Owner / Boundary | Responsibility | Why It Belongs Here | Must Not Contain |
| --- | --- | --- | --- | --- | --- |
| `browser-automation/` | Folder | complete capability/skill bundle | Generic skill, lock, package, docs, launchers, tests | Folder exactly matches skill name; one relocatable unit | Duplicate runtime or branded active path |
| `browser-automation/SKILL.md` | File | portable procedure | Capability-oriented metadata/instructions and `scripts/browser` | Root location lets the whole project be the skill | Vendor homes, branding, alternate launcher |
| `browser-automation/agents/openai.yaml` | File | optional vendor metadata | **Browser Automation** / `$browser-automation` UI metadata | Conventional optional metadata | Runtime/path requirements or branding |
| `browser-automation/pyproject.toml` | File | package metadata | Generic distribution/entries/namespace; direct runtime dependencies; author ownership metadata | Frozen self-contained runtime source | Legacy entries/aliases, `brui-core`, sibling path dependency |
| `browser-automation/uv.lock` | File | frozen dependency graph | Generic local project identity and direct Playwright graph without `brui-core`/unused transitives | Reproducible bootstrap | Stale candidate/external-runtime records |
| `browser-automation/README.md` | File | active operator docs | Generic skill/CLI/MCP/runtime/development guidance | Same project boundary | Branded active examples/prose |
| `browser-automation/scripts/` | Folder | entry facades | `browser` CLI launcher and `browser-mcp` stdio launcher | Executables next to skill/project | Browser logic or old wrapper names |
| `.../scripts/browser` | File | CLI bootstrap | Captured uv/readiness-gated single-output handoff | Owns failures before CLI starts | Application parsing/business logic |
| `.../scripts/browser-mcp` | File | MCP bootstrap | GUI/stdin-safe frozen MCP launch with protocol stdout reserved | Clean successor to tracked wrapper | CLI JSON envelopes or compatibility forwarding |
| `browser-automation/src/browser_automation/` | Folder | shared application/runtime | Canonical generic capability | Capability namespace, not transport/product namespace | FastMCP at root modules or legacy import package |
| `.../application.py` | File | `BrowserApplication` | Command orchestration | Authoritative core boundary | argparse/FastMCP |
| `.../runtime/` | Folder | owned `BrowserRuntime` | Config, Chrome availability/launch, Playwright/CDP session, target lookup | Main-line runtime boundary now fully capability-owned | CLI/MCP serialization, external manager imports, global kill |
| `.../runtime/config.py` | File | runtime config | Validate fixed loopback endpoint/profile/executable/log inputs | Pure/testable input policy | mutable global config or MCP settings |
| `.../runtime/chrome_launcher.py` | File | Chrome establishment owner | Gate every authoritative probe; classify durable or spawn/wait pending; retain gate through lease promote/abort; clean exact failed group | Process ownership transition isolated but coordinated with session success | ungated ready return, early unlock, global process enumeration/kill |
| `.../runtime/session.py` | File | Playwright/CDP owner | Connect, first context, target resolution, client disconnect | Connection lifecycle isolated from launch policy | browser/context close |
| `.../contracts.py` | File | application contracts | Tight shared shapes/enums | Reused across adapters | Generic optional bag |
| `.../errors.py` | File | error taxonomy | Stable error semantics | Reused across adapters | Tracebacks as contract |
| `.../policy.py` | File | policy | URL/input/artifact invariants | Off-spine safety owner | Transport syntax |
| `.../cleaning.py` | File | browser content | HTML transforms | Existing focused behavior | Page lifecycle |
| `.../dom_snapshot.py` | File | browser content | Snapshot program/normalization | Specialized page behavior | MCP decorators |
| `.../script.py` | File | browser content | Script normalization | Advanced capability boundary | CLI file reading |
| `.../cli.py` | File | CLI adapter | Commands/envelopes/exits | Public shell surface | Playwright calls |
| `.../mcp/` | Folder | MCP adapter | Config, server composition, and thin tools | Makes MCP structurally secondary | Core business/state |
| `.../mcp/config.py` | File | MCP configuration | Bind/port/transport validation and exposure assessment | One operational policy owner | Browser operations |
| `browser-automation/tests/unit/` | Folder | coverage | Core/parser/policy/adapter unit tests | Fast deterministic feedback | Real Chrome assumptions |
| `browser-automation/tests/integration/` | Folder | coverage | Launcher, real Chrome, cross-process, skill forward and naming-contract tests | Runtime evidence | Unmarked always-on external tests or old-name assertions |

## Folder Boundary Check

| Path / Folder | Intended Structural Depth | Ownership Boundary Is Clear? | Mixed-Layer Or Over-Split Risk | Justification / Corrective Action |
| --- | --- | --- | --- | --- |
| `browser-automation/` | Mixed Justified | Yes | Low | A skill folder intentionally contains its packaged runtime and metadata |
| `src/browser_automation/` | Main-Line Domain-Control | Yes | Low | Application and owned runtime are primary; focused off-spine files remain nearby because the package is compact |
| `src/browser_automation/runtime/` | Main-Line Runtime | Yes | Low | Three focused mechanisms replace one external-manager wrapper; config, process launch, and Playwright session change/test independently |
| `src/browser_automation/mcp/` | Transport | Yes | Low | All FastMCP-specific code is isolated here |
| `scripts/` | Transport/bootstrap | Yes | Low | Shell facades only |
| `tests/unit`, `tests/integration` | Mixed Justified | Yes | Low | Split by runtime dependency/evidence scope, not source mirroring |

## Concrete Examples / Shape Guidance

| Topic | Good Example | Bad / Avoided Shape | Why The Example Matters |
| --- | --- | --- | --- |
| Portable invocation | `browser-automation/SKILL.md` says `scripts/browser`; agent resolves and invokes it from that exact file's directory | `$CODEX_HOME/...`, bare `browser`, a required `SKILL_DIR`, embedded path, bundle `cd`, or scan/guess | Works across vendors/bundle locations without persistent shell state |
| Shared boundary | `CLI -> BrowserApplication.open_tab -> BrowserRuntime` and `MCP -> same method` | CLI calls MCP or copies tool body | Prevents adapter drift |
| Identity | `open-tab` returns opaque target ID used by later process | Save Playwright object or translate to short numeric alias | Browser, not a daemon, owns durable state |
| Safe output | `screenshot --output-file artifacts/page.png` resolved under caller workspace | absolute `/tmp/...` or `../../...` accepted silently | Enforces filesystem boundary |
| Advanced action | snapshot -> choose selector -> `run-script --tab-id "$TAB_ID" --script '(arg) => ({title: document.title, label: arg.label})' --arg-json '{"label":"direct"}'` -> read/snapshot verify | materialize a file or switch to stdin only because JavaScript is long, multiline, or complex; or execute without prior observation | Direct arguments preserve the former MCP call shape; `(arg) =>` matches the current normalizer contract; safety comes from observe/act/verify and confirmation |
| Owned runtime | every caller gates before authoritative probe; ready-under-gate returns durable/no-abort; unavailable launch retains gate across readiness and connect/context promote-or-abort | ready-path probe bypasses gate, launch unlocks at `/json/version`, imports sibling `brui_core`, or enumerates/kills all Chrome | Makes browser automation independently evolvable and prevents a shared client from attaching to still-abortable Chrome |
| Runtime cleanup | disconnect Playwright client after operation; close page only on explicit close | `stop_browser()` or context close | Preserves unrelated user tabs/session |
| Launcher failure ownership | No ready marker: redirect captured uv stdout to stderr, emit one fixed `bootstrap` JSON, exit `3`; ready marker: forward captured CLI stdout/status only | `exec uv ...` followed by no possible launcher recovery, or unconditional second JSON on any nonzero exit | Distinguishes reachable pre-Python failure from a valid CLI error |
| Retained MCP exposure | HTTP defaults to `127.0.0.1`; explicit `0.0.0.0` is honored with a no-auth warning | Silently retaining unauthenticated `0.0.0.0` default | Documents and tests no-broadening without inventing auth |
| Capability vocabulary | Catalog/folder `browser-automation`, display **Browser Automation**, launcher `scripts/browser`, CLI `browser`, MCP `scripts/browser-mcp`, namespace `browser_automation` | Product name copied across skill, command, errors, MCP, and package internals | Gives the agent one semantic capability and prevents supported debug/setup paths from leaking provenance |

Example skill command sequence:

`SKILL.md` contains only the relative resource reference `scripts/browser` and tells the agent to resolve it from the directory containing this skill's runtime-advertised `SKILL.md` locator. The following design notation uses `<browser-launcher>` for that resolved absolute path; this placeholder is not committed as a literal command:

```bash
bash "<browser-launcher>" health-check
bash "<browser-launcher>" open-tab --url "https://example.com"
# Read result.tab_id from the JSON, then:
bash "<browser-launcher>" read-page --tab-id "$TAB_ID" --cleaning-mode text
bash "<browser-launcher>" run-script --tab-id "$TAB_ID" --script '(arg) => ({title: document.title, label: arg.label, count: arg.count})' --arg-json '{"label":"direct","count":2}'
bash "<browser-launcher>" read-page --tab-id "$TAB_ID" --cleaning-mode text
bash "<browser-launcher>" close-tab --tab-id "$TAB_ID"
```

The agent substitutes the locator-derived launcher path in each independent shell invocation. `SKILL.md` must not guess where a vendor stores skills, embed that absolute path, or assume that a prior shell call exported a variable.

Atomic establishment interleaving (runtime/test shape, not a public command):

```text
A: acquire gate -> authoritative probe unavailable -> launch group A -> /json/version ready -> retain gate -> PAUSE before Playwright connect
B: request session -> wait on same gate -> MUST NOT probe, classify, or connect

Abort branch:
A: forced connect/context failure -> abort group A -> reap -> release gate
B: acquire gate -> fresh authoritative probe -> decide from current endpoint state

Promotion branch:
A: connect + first context -> clear abort authority -> promote -> release gate
B: acquire gate -> probe ready -> DURABLE_EXISTING/no abort authority -> attach
```

The test must observe B blocked before its probe/connect seam, not merely delayed after it already attached. This distinguishes establishment atomicity from duplicate-launch prevention.

Launcher/CLI handoff shape (implementation guidance, not a second public command):

```bash
READY_FILE="$(mktemp)"
STDOUT_FILE="$(mktemp)"
trap 'rm -f "$READY_FILE" "$STDOUT_FILE"' EXIT

set +e
BROWSER_AUTOMATION_CLI_READY_FILE="$READY_FILE" \
  "$UV_PATH" --quiet --directory "$PROJECT_ROOT" run --frozen \
  browser "$@" >"$STDOUT_FILE"
status=$?
set -e

if grep -qx 'browser-cli-ready-v1' "$READY_FILE"; then
  cat "$STDOUT_FILE"
  exit "$status"
fi

# uv/import output is diagnostic because CLI never took stdout ownership.
cat "$STDOUT_FILE" >&2
printf '%s\n' '{"schema_version":"1","ok":false,"command":"bootstrap","error":{"code":"BOOTSTRAP_FAILED","message":"The bundled browser runtime could not be prepared or started.","retryable":true}}'
exit 3
```

The real launcher also performs fixed prechecks and validates secure temporary-file creation. The CLI entry writes `browser-cli-ready-v1` before parsing/help/output. If it cannot write that marker, it exits `3` without writing stdout, so the launcher remains the sole envelope owner. A normal CLI error may also exit nonzero, but its ready marker forces the forward-only branch and prevents a duplicate bootstrap envelope.

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
| Retain `scripts/browser_mcp_stdio.sh` as forwarding wrapper | Existing README/config may name it | Rejected | Rename/update active references to `scripts/browser-mcp`; delete old path |
| Retain HTTP `0.0.0.0` as implicit default | Avoid bind behavior change | Rejected | Default loopback; explicit non-loopback remains operator-selected with warning |
| Keep candidate branded skill/launcher/MCP names as aliases | Could preserve the checkpointed contract | Rejected | Rename active surfaces to the SR-006 generic set and delete old paths/entries |
| Keep candidate `autobyteus_browser` namespace or `AUTOBYTEUS_*` variables as “internal” | Reduces import/config churn | Rejected | Supported uv/debug/error/schema paths can expose them; rename to `browser_automation` / `BROWSER_AUTOMATION_*` with no fallbacks |
| Permit branded absolute skill bundle segment while changing only frontmatter | Avoid root rename | Rejected | Folder must match `browser-automation`; capability-controlled locator ends `browser-automation/SKILL.md` |
| Keep `brui-core` as a separately released runtime dependency | Avoid moving a few browser lifecycle functions | Rejected | Own the required config/launcher/session mechanisms in `browser_automation.runtime`; remove dependency/lock/import |
| Vendor the whole `brui_core` package or keep a compatibility namespace | Fast mechanical copy | Rejected | Independently reimplement only behavior required by the current runtime; omit UI/clipboard/singleton/global-kill/unused transitives |
| Reference `/Users/normy/autobyteus_org/brui_core` through editable/path/submodule setup | Reuse sibling checkout without release | Rejected | Whole skill bundle must relocate independently; no parent path is a runtime premise |
| Retain `CHROME_DOWNLOAD_DIRECTORY` as parsed no-op | Superficial config compatibility | Rejected | Current candidate never consumes it; remove and assert absence rather than preserve misleading configuration |

## Derived Layering (If Useful)

Explanatory only:

1. Portable procedure/bootstrap: `SKILL.md`, `scripts/`.
2. Public adapters: `cli.py`, `mcp/`.
3. Application control: `BrowserApplication`, contracts/errors.
4. Owned runtime and policy/content concerns: runtime config/launcher/session, policy, cleaning, DOM/script.
5. External mechanisms: Playwright/CDP, Chrome, filesystem.

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
| `run-script` | `--tab-id` plus exactly one script source; normal source is direct `--script` | normal structured arg `--arg-json`; optional alternate sources/output/overwrite | inline JSON result or artifact metadata |

`run-script` script sources are mutually exclusive: `--script`, `--script-file`, or `--script-stdin`. JSON argument sources are mutually exclusive: `--arg-json` or `--arg-file`. The normal agent form is direct `--script` plus direct structured `--arg-json`; Bash quoting is agent-owned and nontrivial/multiline content does not change that default. File/stdin/arg-file are optional alternate sources only for pre-existing input or a concrete shell/process transport constraint. File inputs are resolved through workspace policy. Help remains human-readable; every other path emits one JSON value.

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

Launcher pre-Python errors use command `bootstrap` and fixed strings so shell values never need JSON interpolation. The launcher captures stdout while uv runs and uses `BROWSER_AUTOMATION_CLI_READY_FILE` as a private ownership handshake. No marker means uv/environment/import failed before CLI startup: captured stdout becomes stderr diagnostic, the launcher emits one `BOOTSTRAP_FAILED` envelope, and exits `3`. A valid marker means the CLI started: the launcher prints only the captured CLI stdout and exits with the CLI status, including when that status is nonzero. It never maps “nonzero” alone to bootstrap failure.

The ready-file path is launcher-created with secure temporary-file semantics, never accepted as a public CLI argument, and removed by an exit trap. CLI readiness is written before help/parser/application output. If readiness cannot be written, the CLI emits no stdout and exits `3`, leaving the launcher as sole owner. Python logging is configured to stderr. Tracebacks never appear in stdout and are emitted to stderr only when an explicit debug mode is active.

### Retained MCP operational/security contract

- Console entry: keep `browser-mcp-server`, repointed directly to `browser_automation.mcp.server:main`.
- Stdio wrapper: use `scripts/browser-mcp`; self-resolve the generic root, use quiet frozen uv, keep JSON-RPC stdout untouched, and route generic diagnostics to a generic cache/log path. Remove both prior wrapper names and active references.
- Server surface: default name `browser-automation`; generic instructions, configuration failure, exposure warning, startup log, and log filename. MCP tool names remain their already-generic verb/object names.
- Transport owner: `browser_automation.mcp.config.McpRuntimeConfig` parses `BROWSER_MCP_TRANSPORT`, `BROWSER_MCP_HOST`, and `BROWSER_MCP_PORT` before server construction.
- HTTP default: `127.0.0.1`, not `0.0.0.0`.
- Explicit remote bind: a configured non-loopback host is accepted, but `server.main` logs one prominent warning that the server has no built-in authentication and requires a trusted/external protection boundary.
- Auth scope: no authentication/TLS/proxy implementation or multi-user remote-service promise is added.

## Change / Refactor Sequence

The generic SR-006 implementation passed `ARCH-REV-006`, `IR-005`, and `CRR-008`. Architecture review halted SR-007 without issuing a result for that basis; cumulative SR-008 was then reviewed as `ARCH-REV-007` and failed only on `DR-006`. SR-009 preserves every passing direct-argument and owned-runtime decision while correcting the establishment-gate lifetime:

1. Update `SKILL.md` and active guidance so direct MCP-argument-to-CLI-flag mapping is normative. Use the implementation-compatible example `(arg) => ({..., label: arg.label})` with `--arg-json`; remove complexity-based file/stdin preference and retain all alternate input modes.
2. Introduce `runtime/config.py` with immutable validation for fixed-loopback endpoint, port/profile/user-data/log, and generic executable override/discovery. Explicitly remove the unused `CHROME_DOWNLOAD_DIRECTORY` no-op.
3. Introduce `runtime/chrome_launcher.py`: every caller acquires a secure per-port establishment gate before its authoritative probe. A ready-under-gate endpoint returns durable-existing/no-abort; an unavailable path launches at most one group and returns pending-owned while retaining the gate after CDP readiness. Provide no process enumeration/global kill.
4. Move `BrowserRuntime`/`BrowserSession` to `runtime/session.py`, start Playwright directly, call `connect_over_cdp`, and require first context while a new launch remains gated. On success call `promote()` to clear abort authority before unlock; on failure/cancellation call `abort()` to terminate/reap only that group before unlock. Preserve target-ID behavior and client-only cleanup. Export the stable seam from `runtime/__init__.py`; delete old `runtime.py`.
5. Remove `brui-core` from `pyproject.toml` and regenerate `uv.lock`; remove every active `brui_core`/manager/UI/clipboard/singleton/global-kill reference and any now-unused transitive dependency. Do not modify the sibling library or add a path/editable/submodule dependency.
6. Update owned-runtime units, dependency/source contract checks, current CLI/MCP/application tests, and active docs. Add deterministic readiness-before-promotion two-caller interleavings for both abort and promotion, plus real Chrome coverage for pre-existing endpoint attachment and production-owned launch; assert failed-attempt cleanup and successful Chrome persistence.
7. Return the complete source/prose/test delta through code review. Then API/E2E refreshes its held coverage investigation and reruns the relevant suite plus fresh-agent direct `--script`/`--arg-json` and owned-runtime lifecycle journeys. Any later durable coverage edit returns through code review before delivery.
8. Refresh delivery only after current SR-009 evidence passes. Preserve prior reports and held provisional runs as truthful historical evidence, not final proof.

### SR-009 re-entry delta against the generic candidate

1. **Preserved SR-007 contract:** direct operation flags; implementation-compatible `(arg) => ...` script; `--arg-json`; optional-only file/stdin/arg-file; no generic payload.
2. **Runtime ownership:** external two-symbol `brui_core` wrapper becomes an owned config/launcher/session package using direct Playwright/stdlib.
3. **Clean dependency removal:** no `brui-core` metadata/lock/import, vendored namespace, unused UI/clipboard/singleton/global-kill code, or sibling checkout premise.
4. **Atomic establishment:** all supported callers gate before authoritative probe; a pending owned launch retains the gate across readiness and connect/context; promote removes abort authority before unlock; abort completes exact cleanup before unlock.
5. **Lifecycle preservation:** gated ready path attaches without kill authority; launch only if unavailable; never terminate durable-existing or promoted Chrome; client-only disconnect.
6. **Unchanged higher layers:** `BrowserApplication`, CLI/MCP adapters, target IDs, JSON, artifacts, safety, locator/bootstrap, generic naming, and MCP exposure policy retain their approved contracts.
7. **Revalidation:** runtime/package/prose/contract coverage changes, source review repeats, and held API/E2E/delivery re-enter only afterward.

## Key Tradeoffs

- **Whole project as skill bundle:** Larger than a prose-only skill, but it is the only simple way to make the skill relocatable and executable without copying runtime code or relying on a vendor install path.
- **CDP target IDs:** Longer and Chromium-specific, but remove daemon/state-management complexity and are stable across independent clients in the validated probe.
- **Retained MCP:** Preserves an existing transport while increasing adapter/test surface. Thin delegation prevents it from remaining the architecture owner.
- **Loopback HTTP default:** Changes the old all-interface default, but prevents the refactor from silently preserving an unauthenticated broad exposure. Explicit non-loopback deployment remains available with an honest warning rather than an out-of-scope auth implementation.
- **Readiness-gated stdout capture:** Adds two temporary files and delays stdout until command completion, but preserves exactly-one machine output across both uv startup and CLI-owned failures without parsing CLI JSON in Bash.
- **Owned focused runtime:** Duplicates a small amount of low-level configuration/launch code inside the capability, but removes a separate release boundary, unused transitives, singleton/global-kill policy, and parent-project coupling. The external library remains available independently for other consumers.
- **Gate every establishment decision:** Adds brief per-port serialization to all new Playwright sessions, including the ready path, but it is the minimal daemon-free way to prove that no live owner can still abort an endpoint another supported caller treats as durable. Normal page operations are not held under this gate after establishment.
- **First Chrome context:** Matches the current validated behavior and keeps command identity simple. Multi-context selection is deferred rather than guessed.
- **Strict workspace outputs:** Restricts arbitrary absolute paths, but gives agents a reliable safety boundary and explicit artifact paths.
- **Advanced generic script instead of new click/fill commands:** Preserves current capability and scope. Direct `--script`/`--arg-json` keeps the CLI close to the former tool call and trusts coding agents to quote Bash correctly; optional file/stdin sources remain for actual source/transport needs rather than complexity heuristics.
- **Genericizing internal package/protocol identifiers:** Broader than a prose rename, but avoids product leakage through supported uv/bootstrap/debug/error/schema/MCP paths and is simpler than maintaining a fragile public/private token allowlist. Author/origin metadata and history still retain provenance.

## Risks

1. `Target.getTargetInfo`/target discovery behavior is Chromium/CDP-specific and partly experimental; lock versions and run real regression coverage.
2. Owned launcher behavior may start Chrome when the endpoint is absent. Cross-process gate-before-probe and gate-through-promotion coordination plus production-real tests must distinguish successful automatic launch from configuration/launch failure without killing durable-existing, promoted, or unrelated Chrome.
3. Multiple independent clients can intentionally race on the same tab. The skill must keep one tab's observe/action sequence serial; explicit IDs prevent wrong-tab fallback but cannot infer desired ordering.
4. `uv --directory` changes execution context. The launcher must capture/export caller workspace first, and tests must verify output confinement from unrelated CWDs.
5. uv can fail after launcher prechecks but before Python imports. The readiness/captured-stdout protocol is mandatory; any unconditional `exec` reopens `DR-001`.
6. The SR-006 root/package/public-protocol rename is broad. Removal checks must cover path basenames, skill/agent metadata, README/config, console scripts, imports/lock, CLI/MCP output, environment/readiness/schema identifiers, tests, and provider projections. Scans must allowlist ownership metadata/history only and reject forwarding/fallback paths.
7. Explicit non-loopback MCP binds remain unauthenticated. Documentation/log warnings prevent accidental exposure, but operators must supply any external protection; remote auth remains outside scope.
8. Large script results may not be JSON serializable. Application/adapter must classify this as a stable script/result serialization error and recommend artifact-safe or simplified output.
9. Runtime skill projections differ across vendors, but must yield an exact readable `SKILL.md` locator. The instruction must resolve `scripts/browser` from `dirname(advertised SKILL.md)`, must not assume a populated shell variable, and must classify absence of any locator as unsupported rather than scan or guess paths.
10. Runtime-owned parent paths may contain organization/workspace names outside this package's control. Validation must assert the capability-controlled projection segment `browser-automation/SKILL.md` and keep active skill content/output generic rather than promising control over arbitrary host ancestors.
11. Direct argv still has finite host limits and shell quoting semantics. The skill should use normal Bash quoting and only select a file/stdin source when it identifies a concrete transport limit or the content already lives there; tests must not convert that bounded exception into a general complexity preference.
12. Chrome executable locations and process-group semantics vary across supported macOS/Linux hosts. An explicit generic executable override, deterministic fallback discovery, isolated unit seams, and real launch evidence bound this risk; Windows/native-shell ownership remains deferred.
13. Multiple clients can enter establishment concurrently. Every supported caller must acquire the secure per-port gate before authoritative probe, and a pending owner must retain it after readiness until promote/abort. Tests must prove B cannot even probe/classify/connect during A's readiness-before-promotion pause; the lock remains coordination only, not persisted browser identity.
14. The sibling package declares MIT in metadata but the inspected checkout has no root `LICENSE` file. Prefer an independent focused rewrite; any copied source requires terms/attribution verification before implementation.

## Guidance For Implementation

- Preserve the implemented `browser-automation` folder/frontmatter, **Browser Automation** title, generic trigger language, and `$browser-automation` metadata. In `SKILL.md`, continue to refer only to `scripts/browser`, resolve it from the runtime-advertised file, and never require `SKILL_DIR` or branded vocabulary.
- Keep `SKILL.md` concise and workflow-oriented. Put detailed flags in CLI `--help`; do not duplicate the parser reference in prose.
- Teach the argument-isomorphic normal form explicitly. For scripted interaction, show direct `--script` plus structured `--arg-json`; do not recommend temporary files or stdin merely because JavaScript is nontrivial, long, or multiline. Preserve file/stdin/arg-file as optional parser capabilities.
- The CLI launcher must use `BASH_SOURCE[0]`, `pwd -P`, quoted variables, secure temporary files, an exit trap, `uv --quiet --directory "$PROJECT_ROOT" run --frozen`, captured stdout, and the ready marker. It must not unconditionally `exec` uv, `cd` the caller shell, parse CLI JSON, or emit uv diagnostics to stdout.
- Capture `CALLER_WORKSPACE="$PWD"` before uv and export `BROWSER_AUTOMATION_WORKSPACE` only when the caller has not explicitly set it.
- Use console/prog `browser`, namespace `browser_automation`, distribution `browser-automation`, readiness token `browser-cli-ready-v1`, generic temp/debug identifiers, and DOM schema `browser-dom-snapshot-v1`. Do not read old environment names or retain import/console aliases.
- Write the ready marker before CLI help/parser/application output. If marker write fails, emit no CLI stdout; let the launcher produce the bootstrap envelope. Test nonzero CLI errors separately from pre-CLI uv failures to prove no double envelope.
- Use public Playwright APIs plus page-bound CDP sessions; do not depend on private `_impl_obj` target identifiers.
- Treat target IDs as opaque strings. Do not truncate or derive human aliases.
- Replace `src/browser_automation/runtime.py` with `runtime/{__init__,config,chrome_launcher,session}.py`. Keep `BrowserApplication` imports stable through `runtime/__init__.py`; do not retain the old module alongside the package.
- Implement immutable `BrowserRuntimeConfig` with fixed host `127.0.0.1`, validated port `1..65535`, preserved profile/user-data/log settings, generic `BROWSER_AUTOMATION_CHROME_BIN`, and deterministic macOS/Linux executable discovery. Do not parse `CHROME_DOWNLOAD_DIRECTORY`.
- Implement `ChromeLauncher` as acquire secure per-port establishment gate -> authoritative probe -> either release durable-existing/no-abort or optional process-group spawn/readiness with a pending lease that keeps the gate. Do not make a ready-path decision before acquiring the gate.
- Start Playwright and call `connect_over_cdp` directly in `runtime/session.py`; require the first context while a new launch remains pending. On success, clear abort authority and promote before unlocking. On exception, timeout, or cancellation, terminate/reap only the exact owned group and abort before unlocking. Preserve public page-bound CDP target-ID lookup; promoted Chrome remains alive for later commands.
- `BrowserRuntime` cleanup disconnects its client only. Never call `stop_browser`, close a browser context, or close unrelated pages.
- On `open_tab` failure after page creation, close only that new page before disconnecting.
- Application methods must enforce policy even when called directly by MCP/tests; CLI parser validation is an ergonomics layer, not the invariant owner.
- Make artifact write operations atomic where practical (temporary sibling + replace only when overwrite is allowed) and return resolved path, media type, and byte count.
- Ensure bootstrap, CLI, application, and MCP errors are tested separately so transport mapping does not leak into the core.
- Keep `scripts/browser-mcp` distinct from the skill CLI launcher: it reserves stdout for MCP JSON-RPC, may use `exec`, and routes launch errors to stderr/log rather than a CLI envelope.
- Set the MCP default server name to `browser-automation`; make instructions, config failures, exposure warnings, cache/log filenames, and startup messages generic. MCP tool names already remain capability-oriented.
- Default streamable HTTP to `127.0.0.1`; warn exactly once for explicit non-loopback hosts and never imply that the retained adapter authenticates clients.
- Scan designated active agent/operator/runtime surfaces case-insensitively for `autobyteus`, with explicit exceptions only for package author/root repository Origin metadata. Separately assert the old root/launchers/namespace/entries/env/schema/default prompt are absent and rerun all functional evidence.
- Add/refresh durable contract assertions and the fresh-agent journey so direct inline script plus structured JSON is visibly the normal path, while all alternate input sources retain parser/application coverage.
- Remove `brui-core` metadata/lock/imports and now-unused transitives; add source/package/lock rejection scans. Do not modify the sibling repository, create a path/editable/submodule dependency, or expose manager/UI/clipboard/singleton compatibility APIs.
- Add focused units for runtime config, executable selection, gate-before-authoritative-probe, gate retention through terminal lease transition, spawn/logging, exact failed-process-group cleanup, connection/context failures, and client-only disconnect. Add real Chrome scenarios for durable-existing attachment and production-owned launch, persistence across later CLI processes, and survival of unrelated Chrome.
- Add a deterministic gate interleaving hook after owned `/json/version` readiness but before initial connect/promotion. Assert a second caller has not reached probe/classify/connect; cover A-abort/B-fresh-decision and A-promote/B-durable-attach branches.
- Do not create `implementation-handoff.md` during solution/design work.
