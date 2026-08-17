# Browser MCP → CLI + Skill Conversion Analysis

## Status And Purpose

- Status: `Approved analysis baseline — design input as of 2026-08-17`
- Purpose: Record the evidence-backed feasibility assessment, current tool disposition, image/audio lessons, CLI principles, and material choices approved before design.
- Relationship to requirements: This supplement clarifies `REQ-001` through `REQ-012` and `AC-001` through `AC-012`. Its target behavior is approved through the refined requirements; the design spec remains authoritative for technical structure.

## Executive Finding

The browser MCP can become a practical CLI plus one agent skill, but it is **not** a mechanical MCP-tool-to-subcommand rewrite.

The image/audio CLI works because each provider operation is stateless: one process can parse arguments, perform one generation, emit JSON, and exit. Browser automation is different. The current MCP keeps `TabManager`, Playwright `Page` objects, and short numeric `tab_id` values in one long-lived server process. A naive CLI process would lose that state after every command.

A focused runtime probe found a cleaner path than adding a local daemon: the connected Chrome browser already owns durable tab state, and a Chrome DevTools Protocol target ID remained stable after Playwright disconnected and a completely new Playwright connection attached. Therefore separate CLI processes can address the same live tab if the browser-owned CDP target ID becomes the canonical `tab_id`.

This avoids a background CLI daemon, but it intentionally changes the current MCP-local short-ID and tracked-tab semantics. It also relies on Chromium/CDP behavior; that matches the current `brui_core` implementation but must be explicitly approved and covered by real-browser tests.

## Current Browser MCP Architecture

### Current primary path

`MCP client -> FastMCP registered nested tool function -> TabManager / tool-local validation -> UIIntegrator / Playwright Page -> Chrome over CDP -> MCP structured result`

### Current ownership and state

- `browser_mcp.server.create_server()` creates one in-memory `TabManager` per MCP server process.
- `TabManager` owns a map of short numeric IDs to `BrowserTab` records containing live `UIIntegrator` and Playwright `Page` objects.
- `open_tab` and `attach_tab` populate that map; all other stateful tools require an explicit ID from the map.
- `list_tabs` lists only tabs tracked by that process, not all pages in the Chrome context.
- Tool execution is split across MCP-decorated nested functions. Navigation, read, screenshot, DOM snapshot, and script policy do not currently live behind one transport-neutral application boundary.
- `navigate_to` is directly coupled to MCP `Context.report_progress`.
- Importing `browser_mcp.server` immediately evaluates workspace/CWD initialization, which is an entry-adapter concern and should not affect an importable shared core.
- `UIIntegrator.initialize()` always creates a new page. Reusing it naively in a one-command CLI would create stray tabs before resolving an existing target.

### Current behavior and safety constraints

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
| `run_script` | `run-script` | Direct advanced command. Support agent-safe script input (`--script`, file, or stdin) and structured JSON args without requiring shell-escaped MCP request JSON. |
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

- Command name: `autobyteus-browser`; agent-facing launcher: skill-bundled `scripts/autobyteus-browser`.
- Kebab-case task commands; no generic MCP `call-tool` command.
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

Primary skill-native invocation:

```bash
# SKILL_DIR is the absolute directory containing the SKILL.md that the
# current agent's skill loader activated.
SKILL_DIR="<absolute path to this skill>"
BROWSER_CLI="$SKILL_DIR/scripts/autobyteus-browser"
bash "$BROWSER_CLI" health-check
```

`scripts/autobyteus-browser` is part of the same skill bundle as `SKILL.md`. The launcher resolves its packaged runtime relative to itself and internally runs locked `uv` execution. Conceptually:

```bash
uv --quiet --directory "$BUNDLED_RUNTIME_DIR" run --frozen autobyteus-browser health-check
```

The internal `uv run --frozen` invocation owns runtime preparation. On the first call it creates/synchronizes the environment from the bundled lockfile before the Python CLI starts. Neither the human nor the agent registers a PATH command or performs Python setup. The agent must **not** run `uv sync`, activate `.venv`, run `pip install`, locate the environment, or find a repository checkout. `uv` itself remains the one host runtime prerequisite; if it is missing, the launcher returns a clear bootstrap failure instead of silently installing host software.

The launcher does not unconditionally `exec` uv. It captures uv/CLI stdout and passes a private launcher-created ready-file path to the CLI. The CLI marks readiness before parsing or emitting. If readiness is absent, frozen environment/import startup failed before the CLI owned stdout: captured text is diagnostic on stderr, the launcher emits one fixed `BOOTSTRAP_FAILED` JSON envelope, and exits `3`. If readiness exists, the launcher forwards the CLI output and exit status exactly once, even when the CLI status is nonzero. This prevents both lost bootstrap errors and duplicate envelopes.

Approved flat command surface:

```bash
# Resolve the launcher relative to the loaded SKILL.md. First call also prepares its locked environment.
SKILL_DIR="<absolute path to the directory containing this SKILL.md>"
BROWSER_CLI="$SKILL_DIR/scripts/autobyteus-browser"
bash "$BROWSER_CLI" health-check

# Discover or establish a tab.
bash "$BROWSER_CLI" list-tabs
bash "$BROWSER_CLI" attach-tab --url-contains chat.openai.com
bash "$BROWSER_CLI" open-tab --url https://example.com

# Use the returned explicit tab_id in later, independent shell calls.
bash "$BROWSER_CLI" navigate --tab-id TAB_ID --url https://example.com/docs
bash "$BROWSER_CLI" read-page --tab-id TAB_ID --cleaning-mode text
bash "$BROWSER_CLI" dom-snapshot --tab-id TAB_ID --max-elements 200
bash "$BROWSER_CLI" run-script --tab-id TAB_ID --script 'document.title'
bash "$BROWSER_CLI" screenshot --tab-id TAB_ID --output-file ./shots/page.png
bash "$BROWSER_CLI" close-tab --tab-id TAB_ID
```

The skill should normally issue one command per shell-tool call, read the JSON result returned by that call, retain `result.tab_id`, and pass it explicitly to the next command. It does not need to construct shell pipelines or use `jq`; the agent can read the structured result directly. For long or multiline JavaScript, the CLI should also accept a script file or stdin so the skill does not depend on fragile shell quoting.

Example success output:

```json
{"schema_version":"1","ok":true,"command":"open-tab","result":{"tab_id":"580DAAA08093B376A0AB698FED8B6D7B","url":"https://example.com"}}
```

Example recoverable failure:

```json
{"schema_version":"1","ok":false,"command":"read-page","error":{"code":"TAB_NOT_FOUND","message":"The requested tab is closed or unavailable.","retryable":true}}
```

### How the agent finds the command

The short command `autobyteus-browser ...` is **not** the primary contract because Bash would search `$PATH` and no human is expected to register it. Instead, an agent skill loader makes `SKILL.md` and its bundled resources available together and exposes the actual `SKILL.md` source location. The skill instructs the agent to resolve all resource paths from the directory containing that file:

```bash
SKILL_DIR="<absolute path to the directory containing this SKILL.md>"
bash "$SKILL_DIR/scripts/autobyteus-browser" health-check
```

There is one runtime bootstrap moment: on the first browser command, the bundled launcher invokes locked `uv` execution, which creates/synchronizes its environment and runs the requested command. No separate CLI installation/bootstrap step exists.

The bundle remains relocatable in both directions: `SKILL.md` resolves the launcher relative to the loaded skill directory, while the launcher independently resolves the project/skill root relative to itself. The renamed `autobyteus-browser/` project directory itself becomes the complete skill folder, so `SKILL.md`, launchers, lockfile, Python package, and retained MCP adapter travel together without copying browser logic or depending on `/Users/normy/...`, `$CODEX_HOME`, or another vendor-specific home.

## Resolved Material Decisions

| Decision | Resolved Choice | Rejected Alternative / Tradeoff |
| --- | --- | --- |
| Existing MCP end state | Keep MCP for the first release as a thin adapter over the same shared core; evaluate removal after CLI+skill validation. | Removing MCP immediately was rejected because it would break current consumers before the replacement is validated. |
| Cross-command tab identity | Use browser-owned CDP target IDs and short-lived CLI processes; no daemon. | A persistent daemon was rejected because it adds lifecycle, IPC, auth, concurrency, upgrade, and recovery state without need. |
| Skill/runtime packaging | Rename the capability to `autobyteus-browser/` and make that complete project the vendor-neutral skill root. `SKILL.md` uses its loader-supplied own directory; `scripts/autobyteus-browser` self-resolves the same root and runs the root lock/package. | PATH installation, `$CODEX_HOME`, other vendor homes, hardcoded checkout paths, and a copied skill-only runtime are rejected. |
| Listing/context scope | List all addressable pages in the first configured Chrome context; endpoint/context configuration is the isolation boundary. | A new context/session selector is deferred because current `brui_core` uses the first context and no approved multi-context product surface exists. |
| Tab cleanup ownership | The skill records which target IDs it opened and automatically closes only those; attached/user tabs are never automatically closed. Explicit `close-tab --tab-id` remains available when the user asks. | A persisted ownership registry is rejected because no durable alias state is needed and it would create stale coordination state. |
| Large outputs | `read-page`, `dom-snapshot`, and `run-script` accept optional workspace-safe output files and reject overwrite unless explicitly requested. | Inline-only output is retained as default but is not the only route for large results. |
| Script safety | Keep `run-script` in a clearly marked advanced workflow; require observe/action/verify sequencing and normal confirmation for consequential actions. | Hiding/removing the current capability or treating it as an ordinary first step are rejected. |
| MCP stdio launcher | Rename/update `scripts/browser_mcp_stdio.sh` to `scripts/autobyteus-browser-mcp`; remove the old path and update README/config examples. | A forwarding wrapper is rejected by the clean-cut namespace/root policy. |
| MCP HTTP exposure | Change the streamable-HTTP default from unauthenticated `0.0.0.0` to `127.0.0.1`; honor explicit non-loopback host configuration with a prominent no-auth warning. | Silently copying the all-interface default or adding an out-of-scope auth subsystem are rejected. |

## Risks And Follow-Up Evidence

1. Verify CDP target-ID lookup across supported Chrome/Chromium versions beyond the current macOS Google Chrome probe.
2. Verify the launcher readiness/captured-stdout protocol for missing uv, frozen setup/import failure, marker failure, CLI success/error/help, and temporary-file cleanup.
3. Verify default-loopback HTTP bind, explicit non-loopback warning, host/port rejection, and renamed stdio wrapper behavior without protocol stdout contamination.
4. First release validation covers Bash-capable macOS/Linux agents; Windows/native-shell portability remains a follow-up risk.
5. Concurrent independent clients can still race intentionally on one target; the skill must sequence its own observe/action/verify loop.
