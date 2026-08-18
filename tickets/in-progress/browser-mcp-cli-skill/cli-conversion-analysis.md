# Browser MCP → CLI + Skill Conversion Analysis

## Status And Purpose

- Status: `Approved analysis baseline — initial direction approved 2026-08-17; runtime-locator, capability-oriented naming, argument-isomorphic CLI, and owned-browser-runtime corrections approved 2026-08-18; SR-009 resolves ARCH-REV-007/DR-006 and awaits architecture re-review`
- Purpose: Record the evidence-backed feasibility assessment, current tool disposition, image/audio lessons, CLI principles, agent-facing naming boundary, argument mapping, runtime ownership/establishment, and material choices approved before design.
- Relationship to requirements: This supplement clarifies `REQ-001` through `REQ-015` and `AC-001` through `AC-015`. Its target behavior is approved through the refined requirements; the design spec remains authoritative for technical structure.

## Executive Finding

The browser MCP can become a practical CLI plus one agent skill, but it is **not** a mechanical MCP-tool-to-subcommand rewrite.

The image/audio CLI works because each provider operation is stateless: one process can parse arguments, perform one generation, emit JSON, and exit. Browser automation is different. The current MCP keeps `TabManager`, Playwright `Page` objects, and short numeric `tab_id` values in one long-lived server process. A naive CLI process would lose that state after every command.

A focused runtime probe found a cleaner path than adding a local daemon: the connected Chrome browser already owns durable tab state, and a Chrome DevTools Protocol target ID remained stable after Playwright disconnected and a completely new Playwright connection attached. Therefore separate CLI processes can address the same live tab if the browser-owned CDP target ID becomes the canonical `tab_id`.

This avoids a background CLI daemon, but it intentionally changes the current MCP-local short-ID and tracked-tab semantics. It also relies on Chromium/CDP behavior. The current candidate reaches that behavior through two imported `brui_core` symbols; the approved target owns the narrow configuration/launch/session mechanisms directly and must retain real-browser coverage.

## Original Browser MCP Architecture

### Original primary path

`MCP client -> FastMCP registered nested tool function -> TabManager / tool-local validation -> UIIntegrator / Playwright Page -> Chrome over CDP -> MCP structured result`

### Original ownership and state

- `browser_mcp.server.create_server()` creates one in-memory `TabManager` per MCP server process.
- `TabManager` owns a map of short numeric IDs to `BrowserTab` records containing live `UIIntegrator` and Playwright `Page` objects.
- `open_tab` and `attach_tab` populate that map; all other stateful tools require an explicit ID from the map.
- `list_tabs` lists only tabs tracked by that process, not all pages in the Chrome context.
- Tool execution is split across MCP-decorated nested functions. Navigation, read, screenshot, DOM snapshot, and script policy do not currently live behind one transport-neutral application boundary.
- `navigate_to` is directly coupled to MCP `Context.report_progress`.
- Importing `browser_mcp.server` immediately evaluates workspace/CWD initialization, which is an entry-adapter concern and should not affect an importable shared core.
- `UIIntegrator.initialize()` always creates a new page. Reusing it naively in a one-command CLI would create stray tabs before resolving an existing target.

### Original behavior and safety constraints

- Nine public tools exist: `open_tab`, `attach_tab`, `close_tab`, `list_tabs`, `navigate_to`, `read_page`, `screenshot`, `dom_snapshot`, and `run_script`.
- The current contract intentionally requires explicit `tab_id` for stateful operations; earlier active-tab and ephemeral fallback behavior was removed because it caused ambiguity in parallel workflows.
- `run_script` is the only general interaction mechanism. There are no public click/type/fill/select tools. DOM snapshot element IDs are snapshot-local labels; selectors, not element IDs, are the actionable output.
- `close_tab(close_browser=true)` reaches `BrowserManager.stop_browser()`, whose installed `brui_core` implementation ultimately invokes a global Chrome-kill path. This is too destructive for normal skill guidance and should not be projected casually into the CLI.
- `resolve_output_path` permits arbitrary absolute screenshot paths and creates parent directories. `AUTOBYTEUS_AGENT_WORKSPACE` changes CWD but is not an output sandbox.
- `is_valid_url` checks only for a scheme and network location; it does not explicitly constrain navigation to approved schemes.
- `read_page.cleaning_mode` treats any value other than `raw` or `text` as the thorough cleaning branch instead of rejecting invalid values.

## Runtime Feasibility Probe

### Question

Can a tab opened during one short-lived CLI process be found deterministically during a later independent CLI process without a daemon?

### Method

1. Launch an isolated headless Google Chrome process with a temporary user-data directory and loopback CDP port.
2. Connect with Playwright, open and navigate a page, and obtain its CDP target ID through a page-bound `CDPSession` and `Target.getTargetInfo`.
3. Close the Playwright connection.
4. Start a new Playwright runtime, reconnect to the same Chrome endpoint, enumerate context pages, and obtain each page's target ID through a new CDP session.
5. Verify the original ID identifies the original page, close the probe page, terminate only the isolated Chrome process, and remove the temporary profile.

### Result

```json
{
  "created_target_id": "580DAAA08093B376A0AB698FED8B6D7B",
  "first_connection_page_count": 2,
  "stable_match": true,
  "matched_title": "Browser CLI Identity Probe"
}
```

The second independent connection observed the same target ID and page URL. The successful reconnect also proves that closing the Playwright CDP client connection did not terminate the isolated Chrome process.

### Interpretation

- A direct, short-lived CLI process per command is technically feasible without persisting Playwright objects or running a CLI daemon.
- Canonical tab identity should be browser-owned rather than a process-local counter if this approach is approved.
- The current `TabManager` tracked-map model should not be serialized to disk; its values contain live runtime objects and its short IDs have no meaning after process exit.
- Chrome DevTools Protocol documents target IDs and target discovery, while Playwright documents page-bound CDP sessions as Chromium-only. The CDP methods used for discovery/target information are marked experimental in the current protocol documentation, so real-browser regression coverage and locked runtime execution are required.

## Tool-To-CLI Disposition

| Current MCP Tool / Capability | Target CLI Disposition | Resolved Rationale / Behavioral Decision |
| --- | --- | --- |
| `open_tab` | `open-tab` | Direct command. Open a page in the connected Chrome context and return the browser-owned target ID. |
| `attach_tab` | `attach-tab` | Retain as deterministic unique-match discovery for an already-open tab; it no longer needs to register a process-local object. |
| `list_tabs` | `list-tabs` | Direct command listing all addressable pages in the selected first CDP context rather than one process's tracked map. Remove metadata that cannot be truthfully reconstructed (`created_at`, process-local `attached_by`). |
| `close_tab` | `close-tab` | Direct command for one explicit target ID. Do not expose global browser termination in ordinary skill usage; recommended CLI scope removes `close_browser`. |
| `navigate_to` | `navigate` | Direct command with explicit target ID, URL, wait mode, and timeout. MCP progress callback becomes stderr diagnostic/progress only; final stdout remains one JSON value. |
| `read_page` | `read-page` | Direct command. Constrain cleaning mode to an explicit enum; optionally support writing very large content to a requested safe output file. |
| `screenshot` | `screenshot` | Direct command. Output path must be workspace-safe and result must return the resolved artifact path. |
| `dom_snapshot` | `dom-snapshot` | Direct command. Keep the structured element/selector contract; clearly state snapshot-local `element_id` semantics. |
| `run_script` | `run-script` | Direct advanced command. Normal form maps `script` to `--script` and structured `arg` to `--arg-json`; file/stdin/arg-file remain optional alternate sources, not a preference for complex code. No generic MCP request JSON wrapper. |
| Server health/config discovery | Add `health-check` | New CLI operational capability needed to distinguish missing `uv`, Chrome/CDP unavailability, configuration errors, and successful connectivity. |
| MCP tool schema discovery | CLI help, plus stable JSON contracts | The CLI must be task-oriented; do not add a generic `call-tool` command. Command help and versioned JSON output replace MCP schema discovery for normal use. |
| Click/type/fill/select | Skill-only composition over `dom-snapshot` + `run-script` in this scope | These are not current public MCP capabilities. Adding first-class interaction commands would be a separate product expansion, not a conversion requirement. |

## What To Learn From Image/Audio

### Strong patterns to adopt

1. **Path-independent repo wrapper**: `cli/autobyteus-image-audio` resolves its project and calls `uv --directory ... run --frozen`, so agents do not manage `.venv` or run setup steps.
2. **Separate console scripts**: project metadata distinguishes CLI and MCP server entrypoints.
3. **Task-oriented commands**: normal use is not a raw MCP/JSON-RPC `call-tool` escape hatch.
4. **Thin entry adapters over a shared core**: CLI and MCP should delegate to the same authoritative capability implementation.
5. **Machine-readable normal output**: success/failure envelopes on stdout and diagnostics on stderr are appropriate for agent invocation.
6. **Explicit artifact paths and workspace semantics**: file-producing operations return resolved paths and enforce file policy below both public adapters.
7. **Local/mock boundary tests plus real integration gates**: parser/delegation tests, transport inventory tests, and opt-in real provider/runtime execution are distinct evidence surfaces.

### Patterns that do not transfer directly

1. **Stateless per-call service lifecycle**: generation operations can create a client and clean it up in one process; browser workflows must preserve an addressable live tab across commands.
2. **One-to-one command parity as sufficient design**: browser operations form an observation/action loop with state, stale targets, navigation races, and cleanup ownership.
3. **Skill assumed but absent**: the image/audio ticket and design repeatedly call the wrapper “skill-facing,” but no image/audio `SKILL.md` is tracked or installed in the inspected locations. It is a CLI reference, not a completed CLI-plus-skill example.
4. **Unversioned error envelope**: image/audio uses exception class names as `error_type`; the browser CLI should use stable documented error codes and include whether recovery/retry is meaningful.
5. **Documentation drift**: `autobyteus-image-audio/DESIGN.md` still documents removed `--config` and `--speaker/--voice` options while current CLI/README use `--generation-config`. The later investigation notes also contain a stale statement that old config behavior must remain compatible even though the final requirements intentionally removed it. Browser implementation must update canonical design/docs together.
6. **Shell-built JSON preflight**: the wrapper interpolates shell values into JSON directly. A browser wrapper should keep pre-Python failures valid JSON even for unusual paths/arguments, or restrict fields to fixed safe strings.

## Industry-Level Conversion Heuristic

A CLI plus skill is usually a good replacement or companion for an MCP when all of the following can be made explicit:

- one invocation has a deterministic command boundary;
- state is absent, externally owned with a stable identifier, or deliberately hosted in a daemon;
- stdin/stdout/stderr and exit behavior can represent results and failures without server push;
- large/binary output has an artifact-path contract;
- credentials/configuration can be inherited or selected without interactive protocol negotiation;
- cancellation, progress, concurrency, and timeouts remain understandable at process boundaries;
- the skill adds procedural judgment and composition rather than reimplementing runtime logic.

A conversion is not mechanical when the MCP depends materially on connection-scoped state, server-initiated notifications, streaming, sampling/elicitations, interactive authentication, or hidden server lifecycle. In those cases the design must first choose an external identity, a persistent runtime, or a workflow/batch boundary.

Browser MCP is a good candidate **only because Chrome/CDP can be the durable state owner**. Without the stable-target finding, a daemon or batch workflow would be required.

## Approved CLI Contract Principles

These are approved behavioral principles; the design spec defines their implementation structure:

- Skill/catalog/folder identity: `browser-automation`; human title: **Browser Automation**; agent-facing launcher: `scripts/browser`; CLI console/help identity: `browser`.
- The complete bundle owns its narrow Chrome/CDP runtime directly; neither first invocation nor frozen execution depends on a separately released or sibling-checkout browser-management library.
- Kebab-case task commands; no generic MCP `call-tool` command.
- Argument-isomorphic normal syntax: a former MCP function becomes the approved task command and each supported function argument becomes an explicit flag; scalar values are direct, booleans use the command's documented switches, and structured values use the operation-specific JSON flag rather than a generic request envelope.
- One JSON object on stdout for every non-help invocation.
- Versioned envelope with at least `schema_version`, `ok`, `command`, and either `result` or a structured `error` (`code`, `message`, `retryable`, optional details).
- Diagnostics/progress only on stderr; no dependency logs on stdout.
- Stable documented exit categories: success, usage, configuration/connectivity, missing/stale tab, and browser operation failure.
- Explicit browser-owned `tab_id` required for every tab-scoped command.
- No implicit active-tab fallback.
- No global browser-close command in the initial skill-facing surface.
- Default workspace-safe artifact policy and explicit URL-scheme policy enforced in the shared core, not merely described by the skill.
- The skill consumes the CLI contract, retains IDs, sequences observe/act/verify loops, applies side-effect confirmations, and closes only tabs it owns unless the user explicitly instructs otherwise.

## Agent Shell Command Experience (User-Prioritized)

The agent skill is procedural guidance around ordinary shell execution. It should instruct the agent to invoke the checked-in wrapper with its Bash/shell execution tool; it should not ask the agent to start an MCP server or issue MCP protocol requests.

Primary skill-native invocation contract:

```text
# This is the relative launcher reference written in SKILL.md:
scripts/browser
```

The runtime advertises this skill's exact absolute `SKILL.md` path through a native system-prompt catalog or provider-specific skill projection. The agent reads that file, resolves the relative reference from its containing directory, and sends the resolved launcher path to its Bash tool. For example, the executed command shape is:

```bash
bash "<resolved-skill-root>/scripts/browser" health-check
```

The placeholder above exists only in this design explanation. The committed `SKILL.md` must not embed an absolute installation/checkout path, and the framework is not expected to populate `SKILL_DIR` or another shell variable.

`scripts/browser` is part of the same skill bundle as `SKILL.md`. The launcher resolves its packaged runtime relative to itself and internally runs locked `uv` execution. Conceptually:

```bash
uv --quiet --directory "$BUNDLED_RUNTIME_DIR" run --frozen browser health-check
```

The internal `uv run --frozen` invocation owns runtime preparation. On the first call it creates/synchronizes the environment from the bundled lockfile before the Python CLI starts. Neither the human nor the agent registers a PATH command or performs Python setup. The agent must **not** run `uv sync`, activate `.venv`, run `pip install`, locate the environment, or find a repository checkout. `uv` itself remains the one host runtime prerequisite; if it is missing, the launcher returns a clear bootstrap failure instead of silently installing host software.

The launcher does not unconditionally `exec` uv. It captures uv/CLI stdout and passes a private launcher-created ready-file path to the CLI. The CLI marks readiness before parsing or emitting. If readiness is absent, frozen environment/import startup failed before the CLI owned stdout: captured text is diagnostic on stderr, the launcher emits one fixed `BOOTSTRAP_FAILED` JSON envelope, and exits `3`. If readiness exists, the launcher forwards the CLI output and exit status exactly once, even when the CLI status is nonzero. This prevents both lost bootstrap errors and duplicate envelopes.

Approved flat command surface, shown with `<browser-launcher>` standing for the absolute path that the agent resolved from `dirname(runtime-advertised SKILL.md)` plus the relative `scripts/browser` reference:

```bash
# First call also prepares the locked environment.
bash "<browser-launcher>" health-check

# Discover or establish a tab.
bash "<browser-launcher>" list-tabs
bash "<browser-launcher>" attach-tab --url-contains chat.openai.com
bash "<browser-launcher>" open-tab --url https://example.com

# Use the returned explicit tab_id in later, independent shell calls.
bash "<browser-launcher>" navigate --tab-id TAB_ID --url https://example.com/docs
bash "<browser-launcher>" read-page --tab-id TAB_ID --cleaning-mode text
bash "<browser-launcher>" dom-snapshot --tab-id TAB_ID --max-elements 200
bash "<browser-launcher>" run-script --tab-id TAB_ID --script '(arg) => ({title: document.title, label: arg.label, count: arg.count})' --arg-json '{"label":"direct","count":2}'
bash "<browser-launcher>" screenshot --tab-id TAB_ID --output-file ./shots/page.png
bash "<browser-launcher>" close-tab --tab-id TAB_ID
```

The skill should normally issue one command per shell-tool call, read the JSON result returned by that call, retain `result.tab_id`, and pass it explicitly to the next command. It does not need to construct shell pipelines or use `jq`; the agent can read the structured result directly. The coding agent owns normal Bash quoting, including nontrivial or multiline JavaScript and direct structured JSON. It must not create a temporary script/argument file or switch to stdin merely because content is long, multiline, complex, or structured. `--script-file`, `--script-stdin`, and `--arg-file` remain optional when the content already resides there or a concrete shell/process limit prevents faithful direct argv transport.

### Argument-isomorphic mapping from MCP tools

“Argument-isomorphic” is semantic rather than byte-for-byte: snake-case operations become approved kebab-case task commands, and every supported user argument has one explicit operation-specific flag rather than being hidden in a generic payload. Most flags use the argument's kebab-case spelling; documented CLI vocabulary, boolean switches, transport-injected values, intentionally removed unsafe behavior, and CLI-only extensions are explicit rather than accidental exceptions.

| Former MCP call shape | Normal CLI shape | Deliberate difference / extension |
| --- | --- | --- |
| `open_tab(url, wait_until, timeout_ms)` | `open-tab --url ... --wait-until ... --timeout-ms ...` | All arguments are optional as in the approved command; output envelope is CLI-specific. |
| `attach_tab(url_contains, title_contains)` | `attach-tab --url-contains ... --title-contains ...` | At least one matcher; unique-match invariant unchanged. |
| `list_tabs()` | `list-tabs` | No request payload. |
| `close_tab(tab_id)` | `close-tab --tab-id ...` | The retained MCP and CLI both omit the earlier unsafe global-close argument. |
| `navigate_to(tab_id, url, wait_until, timeout_ms)` | `navigate --tab-id ... --url ... --wait-until ... --timeout-ms ...` | Command name is shortened; arguments remain direct. |
| `read_page(tab_id, cleaning_mode, output_file, overwrite)` | `read-page --tab-id ... --cleaning-mode ... --output-file ... --overwrite` | Inputs map directly; output remains optional and workspace-confined. |
| `screenshot(tab_id, file_path, full_page, image_format, overwrite)` | `screenshot --tab-id ... --output-file ... --full-page` (or `--viewport-only`) `--format ... --overwrite` | `file_path` uses the clearer CLI flag `--output-file`; output is workspace-confined and switches represent booleans. |
| `dom_snapshot(tab_id, include_non_interactive, include_bounding_boxes, max_elements, output_file, overwrite)` | `dom-snapshot --tab-id ... --include-non-interactive --include-bounding-boxes --max-elements ... --output-file ... --overwrite` | Boolean defaults and positive/negative switches are documented by help. |
| `run_script(tab_id, script, arg, output_file, overwrite)` | `run-script --tab-id ... --script '<JavaScript>' --arg-json '<JSON>' --output-file ... --overwrite` | Direct script/arg is the normal agent path; output is optional, and file/stdin/arg-file are optional alternate input sources only. |

The direct `run-script` command passes two independent argv strings after Bash decoding: JavaScript through `--script` and JSON text through `--arg-json`. The CLI decodes the latter to the same structured application value that the MCP adapter passes to `BrowserApplication.run_script`; neither adapter owns different script semantics.

The example deliberately begins with `(arg) =>`. The current script normalizer recognizes `arg =>` and `(arg) =>` as complete callable expressions. A destructuring prefix such as `({label, count}) =>` is not currently recognized and would be wrapped as a function body, returning an inner function rather than the intended JSON value; SR-008 therefore does not present that misleading shape or require a normalizer expansion.

Example success output:

```json
{"schema_version":"1","ok":true,"command":"open-tab","result":{"tab_id":"580DAAA08093B376A0AB698FED8B6D7B","url":"https://example.com"}}
```

Example recoverable failure:

```json
{"schema_version":"1","ok":false,"command":"read-page","error":{"code":"TAB_NOT_FOUND","message":"The requested tab is closed or unavailable.","retryable":true}}
```

### How the agent finds the command

The bare command `browser ...` is **not** the primary contract because Bash would search `$PATH` and no human is expected to register it. Instead, the runtime advertises the exact `browser-automation/SKILL.md` locator through its system-prompt catalog or provider projection, and the agent reads the skill there. `SKILL.md` names only the relative launcher:

```text
scripts/browser
```

Before calling Bash, the agent joins that relative resource path to the directory containing this skill's runtime-advertised `SKILL.md` and uses the resulting absolute launcher path. This is model-side path composition from prompt context, not a framework-populated `SKILL_DIR`, an environment-variable dependency, or an active skill-load hook.

There is one runtime bootstrap moment: on the first browser command, the bundled launcher invokes locked `uv` execution, which creates/synchronizes its environment and runs the requested command. No separate CLI installation/bootstrap step exists.

The bundle remains relocatable in both directions: the agent resolves the skill's relative launcher reference from the current runtime-advertised `SKILL.md` locator, while the launcher independently resolves the project/skill root relative to itself. The renamed `browser-automation/` project directory itself becomes the complete skill folder, so `SKILL.md`, launchers, lockfile, Python package, and retained MCP adapter travel together without copying browser logic or depending on `/Users/normy/...`, `$CODEX_HOME`, or another vendor-specific home. A framework that provides no prompt/provider-visible skill locator cannot support deterministic bundled-resource discovery and is outside this packaging contract; the skill must not compensate by scanning or guessing paths.

### Verified runtime projection in AutoByteus Workspace

Inspection of `/Users/normy/autobyteus_org/autobyteus-workspace-superrepo` confirms the relative-resource model and disproves a framework-populated `SKILL_DIR` premise:

| Runtime | Verified projection | Agent behavior | Path consequence |
| --- | --- | --- | --- |
| Native AutoByteus | `appendConfiguredSkillsCatalog` writes the exact absolute `SKILL.md` path into the system prompt without the body. | Agent reads that path with its ordinary file/shell tool; the prompt explicitly says to resolve relative references from the directory containing `SKILL.md`. | Resolve `scripts/browser` from `dirname(advertised SKILL.md)` and invoke the resulting absolute launcher path while keeping the task workspace as CWD. |
| Codex | `CodexThreadBootstrapper` reuses provider-discoverable skills or `CodexWorkspaceSkillMaterializer` symlinks the complete root to `<workspace>/.codex/skills/<name>`. | Codex's provider skill mechanism advertises/reads the projected `SKILL.md`. | Relative launcher/resources work through the whole-directory symlink; `SKILL.md` must not mention `.codex`, `$CODEX_HOME`, or the source root. |
| Claude | `ClaudeWorkspaceSkillMaterializer` symlinks the complete root to `<workspace>/.claude/skills/<name>`; the SDK enables project/local setting sources. | Claude's provider skill mechanism discovers/reads the projected `SKILL.md`. | Relative launcher/resources work through the whole-directory symlink; `SKILL.md` must not mention `.claude` or the source root. |

The server-side class named `SkillLoader` only parses skill packages for configuration/catalog purposes. It is not an agent tool, and the retired `load_skill`/`get_skill_content`/`get_available_skills` tools are not a runtime boundary.

## Capability-Oriented Agent Surface

The user's later correction made product provenance explicitly non-semantic for an LLM. SR-006 has now implemented the resolved generic set across active surfaces:

| Surface | Approved Generic Choice | Why Candidate/Internal Branding Is Not Retained |
| --- | --- | --- |
| Skill/catalog/folder | `browser-automation`; capability-controlled locator ends `browser-automation/SKILL.md` | Matches the skill naming convention and avoids collision with generic web lookup |
| Heading/display/default prompt | **Browser Automation** and `$browser-automation` | Presents capability and invocation, not platform provenance |
| Relative launcher / CLI | `scripts/browser`; console/prog/error prefix `browser` | The skill context makes the short relative filename unambiguous; help matches executed basename |
| Launcher protocol/config | `BROWSER_AUTOMATION_WORKSPACE`, `BROWSER_AUTOMATION_CLI_READY_FILE`, `BROWSER_AUTOMATION_DEBUG`, `browser-cli-ready-v1`, generic temp names | These values can surface through supported failure/debug paths; no fallback to old names |
| Agent-consumed schema | `browser-dom-snapshot-v1`; outer JSON schema remains `"1"` | Results/artifacts must not carry product terminology |
| MCP | `scripts/browser-mcp`, server `browser-automation`, generic instructions/errors/warnings/cache/log; `browser-mcp-server` stays | MCP-using agents/operators can see server metadata and diagnostics |
| Python package | distribution `browser-automation`, namespace `browser_automation` | uv/import/debug traces can expose supposedly internal identifiers |
| Provenance exception | package author/root repository Origin and immutable historical artifacts only | Ownership/history is truthful but never part of active workflow or compatibility |

This is a clean replacement. No old skill ID, folder, launcher, MCP wrapper, console entry, namespace, environment/readiness/schema identifier, default prompt, forwarding alias, or fallback scan remains active. Runtime-owned parent directories outside the `browser-automation` projection segment are not controlled by the skill package.

## Runtime Ownership Decision

Direct inspection of the current candidate and `/Users/normy/autobyteus_org/brui_core` makes the self-contained-runtime change proportionate rather than speculative:

- `browser-automation/src/browser_automation/runtime.py` imports only `BrowserManager` and `get_browser_config` from `brui_core`; no other candidate source imports that package.
- The sibling library is about 608 Python source lines and includes concerns browser automation does not use: `UIIntegrator`, clipboard integration, Pillow/pyperclip, singleton management, process enumeration/global Chrome termination, and Linux-specific launch assumptions.
- The candidate already owns target-ID lookup, `connect_over_cdp` session use, first-context selection, and client-only cleanup behind `BrowserRuntime`; the external manager is therefore a replaceable mechanism dependency rather than the public application boundary.
- The external configuration recognizes `CHROME_PROFILE_DIRECTORY`, `CHROME_REMOTE_DEBUGGING_PORT`, `CHROME_USER_DATA_DIR`, `CHROME_DOWNLOAD_DIRECTORY`, and `CHROME_LOG_PATH`. The candidate never consumes the download-directory value, so preserving it as a parsed no-op would misrepresent compatibility.

| Current external mechanism | Approved owned target | Disposition |
| --- | --- | --- |
| `get_browser_config` mutable dictionary | Immutable `BrowserRuntimeConfig` in `runtime/config.py` | Preserve validated port/profile/user-data/log behavior; add `BROWSER_AUTOMATION_CHROME_BIN`; remove unused download-directory input |
| `BrowserManager.ensure_browser_launched()` | `ChromeLauncher.ensure_available()` in `runtime/chrome_launcher.py` | Every caller acquires the secure per-port establishment gate before authoritative probe; ready returns durable/no-abort, unavailable starts at most one pending process group while retaining the gate |
| Manager Playwright connection / first context | `BrowserRuntime` and `BrowserSession` in `runtime/session.py` | Start Playwright directly; for pending launch, connect/require first context before promote or exact abort releases the gate; then resolve opaque targets and disconnect client only |
| Manager/global shutdown and unrelated UI/clipboard/singleton APIs | No replacement | Never enumerate/kill arbitrary Chrome; never copy or expose unused library-shaped APIs |
| `brui-core` distribution/lock/import | Direct Playwright plus standard-library runtime owned by `browser-automation` | Remove project/lock/import records; no editable/path/submodule or compatibility namespace |

The successful lifecycle keeps Chrome as external durable state, but `/json/version` readiness alone is not promotion. Every supported caller gates before its authoritative probe. If ready under an otherwise-unheld gate, the endpoint is durable/no-longer-abortable and attaches without kill authority. If unavailable, the owner keeps the gate after readiness through initial Playwright connection and first context: `promote()` clears abort authority before unlock; `abort()` terminates/reaps only this attempt's group before unlock. Thus no second supported caller can attach to Chrome that a live owner may still kill. A crashed owner releases the kernel lock and cannot later abort, so no daemon/marker/registry is required. The separate `brui_core` repository remains untouched. A focused independent rewrite is preferred; copied source requires prior terms/attribution verification because the checkout declares MIT in metadata but has no root `LICENSE`.

Deterministic validation must pause caller A after `/json/version` readiness but before connect/promotion, start caller B, and prove B has not reached probe/classify/connect. Forced A abort must finish exact cleanup/unlock before B makes a fresh decision; successful A promotion must clear abort authority/unlock before B classifies the endpoint as durable.

## Resolved Material Decisions

| Decision | Resolved Choice | Rejected Alternative / Tradeoff |
| --- | --- | --- |
| Existing MCP end state | Keep MCP for the first release as a thin adapter over the same shared core; evaluate removal after CLI+skill validation. | Removing MCP immediately was rejected because it would break current consumers before the replacement is validated. |
| Cross-command tab identity | Use browser-owned CDP target IDs and short-lived CLI processes; no daemon. | A persistent daemon was rejected because it adds lifecycle, IPC, auth, concurrency, upgrade, and recovery state without need. |
| Skill/runtime packaging | Rename the capability to `browser-automation/` and make that complete project the vendor-neutral skill root. `SKILL.md` names only `scripts/browser`; the agent resolves it from the directory containing this skill's runtime-advertised `SKILL.md`, and the launcher self-resolves the same root to run the root lock/package. | Framework-populated shell variables, PATH installation, `$CODEX_HOME`, other vendor homes, absolute paths embedded in `SKILL.md`, path scanning/guessing, and a copied skill-only runtime are rejected. |
| Capability vocabulary | Use the exact generic naming table above across skill, CLI, MCP, package, protocol identifiers, active docs, and tests; keep provenance only in ownership metadata/history. | Copy-only prose edits, branded “internal” namespace/protocol names, and compatibility aliases are rejected because supported uv/debug/error/result paths can leak them. |
| Argument mapping | Make former MCP functions and arguments direct task commands/flags. For `run_script`, use `--script` plus `--arg-json` normally; retain file/stdin/arg-file only for pre-existing sources or a concrete argv constraint. | A generic request payload and complexity-driven file/stdin preference are rejected because they add unnecessary agent work and obscure the operation's natural argument contract. |
| Browser runtime ownership | Own the focused config/Chrome-launch/Playwright-session mechanisms under `browser_automation.runtime`; remove `brui-core` metadata, lock, imports, and unused/policy-conflicting library concerns. | Keeping a separate release, vendoring the full namespace, or referencing a sibling checkout is rejected because the complete skill bundle must evolve and relocate independently. |
| Cross-process Chrome establishment | Every supported caller acquires the per-port gate before authoritative probe. A pending owned launch keeps it through readiness and connect/context `promote()`/`abort()`; promotion clears abort authority before unlock, abort completes exact cleanup before unlock. | A ready-path gate bypass, unlock at `/json/version`, daemon, persisted browser registry, or removal of exact failed-attempt cleanup is rejected. |
| Listing/context scope | List all addressable pages in the first configured Chrome context; endpoint/context configuration is the isolation boundary. | A new context/session selector is deferred because the current candidate and approved behavior use the first context and no approved multi-context product surface exists. |
| Tab cleanup ownership | The skill records which target IDs it opened and automatically closes only those; attached/user tabs are never automatically closed. Explicit `close-tab --tab-id` remains available when the user asks. | A persisted ownership registry is rejected because no durable alias state is needed and it would create stale coordination state. |
| Large outputs | `read-page`, `dom-snapshot`, and `run-script` accept optional workspace-safe output files and reject overwrite unless explicitly requested. | Inline-only output is retained as default but is not the only route for large results. |
| Script safety | Keep `run-script` in a clearly marked advanced workflow; require observe/action/verify sequencing and normal confirmation for consequential actions. | Hiding/removing the current capability or treating it as an ordinary first step are rejected. |
| MCP stdio launcher | Use generic `scripts/browser-mcp`, server `browser-automation`, and generic messages/logs; remove both prior wrapper identities and update active README/config. | A forwarding wrapper or branded server/log identity is rejected by the clean-cut policy. |
| MCP HTTP exposure | Change the streamable-HTTP default from unauthenticated `0.0.0.0` to `127.0.0.1`; honor explicit non-loopback host configuration with a prominent no-auth warning. | Silently copying the all-interface default or adding an out-of-scope auth subsystem are rejected. |

## Risks And Follow-Up Evidence

1. Verify CDP target-ID lookup across supported Chrome/Chromium versions beyond the current macOS Google Chrome probe.
2. Verify the launcher readiness/captured-stdout protocol for missing uv, frozen setup/import failure, marker failure, CLI success/error/help, and temporary-file cleanup.
3. Verify default-loopback HTTP bind, explicit non-loopback warning, host/port rejection, and renamed stdio wrapper behavior without protocol stdout contamination.
4. First release validation covers Bash-capable macOS/Linux agents; Windows/native-shell portability remains a follow-up risk.
5. Concurrent independent clients can still race intentionally on one target; the skill must sequence its own observe/action/verify loop.
6. Preserve the completed SR-006 rename with active path/content scans, package/namespace/entry checks, help/error/debug/schema/MCP output assertions, and a generic runtime projection. Explicitly allowlist ownership metadata/history rather than weakening the active scan.
7. After SR-009 implementation/source review, refresh the held coverage investigation and rerun the relevant browser/launcher/MCP/fresh-agent matrix. `ARCH-REV-006`, `IR-005`, `CRR-008`, and API-REV-003 remain truthful historical evidence for their then-approved bases, not final SR-009 proof. SR-007 received no result; `ARCH-REV-007` reviewed cumulative SR-008 and failed only on `DR-006`.
8. Require at least one fresh-agent real-Chrome scripted interaction to pass nontrivial direct `--script` plus structured `--arg-json` and verify the result. Retain alternate input-source tests, but reject skill/prose assertions that make them the complexity default.
9. Prove the runtime is self-contained with package/lock/source scans, unit coverage for config/executable/secure non-inheritable gate/gate-before-probe/gate-through-terminal-transition/readiness/owned-failure cleanup/session disconnect, deterministic readiness-before-promotion abort and promotion interleavings, and real Chrome journeys for both durable-existing attachment and production-owned launch. A promoted launch must survive later CLI clients; the child must not inherit the gate descriptor; unrelated Chrome must never be terminated.
