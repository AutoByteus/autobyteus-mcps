# Investigation Notes

## Investigation Status

- Bootstrap Status: `Complete`
- Current Status: `Architecture review round 1 returned Fail / Design Impact; SR-002 corrections completed for re-review`
- Investigation Goal: Determine how the current browser MCP should become task-oriented CLI tools plus one agent skill, informed by the incomplete image/audio CLI/skill-facing work.
- Scope Classification (`Small`/`Medium`/`Large`): `Large`
- Scope Classification Rationale: The change affects a stateful browser lifecycle, cross-process identity, public contracts, runtime ownership, two possible entry adapters, packaging, safety, skill authoring, and real browser validation.
- Scope Summary: Requirements and design are complete. Architecture round 1 confirmed the core and requested four design/coherence corrections: pre-CLI uv failure ownership, retained HTTP exposure assessment, tracked stdio-launcher disposition, and stale state text. Those corrections are incorporated for round 2.
- Primary Questions Resolved: Retain MCP as a thin adapter; use browser-owned CDP IDs/no daemon; derive `SKILL_DIR` from the loader-supplied `SKILL.md` path without vendor homes; rename the complete skill root to `autobyteus-browser/`; validate Bash-capable macOS/Linux first; use first configured Chrome context; support safe optional large-output files; gate launcher/CLI stdout with a readiness marker; rename the MCP stdio wrapper; default MCP HTTP to loopback and warn on explicit non-loopback.

## Request Context

The user asked to inspect the repository's browser MCP, analyze turning it into command-line tools, and create one agent skill. They identified the incomplete image/audio CLI as a worthwhile reference and framed a broader hypothesis: many industry MCPs could be expressed as CLI tools plus one procedural agent skill.

The request is being handled as analysis/requirements/design first. No browser CLI or skill source implementation has been started.

## Environment Discovery / Bootstrap Context

- Project Type (`Git`/`Non-Git`): `Git`
- Task Workspace Root: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill`
- Task Artifact Folder: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill`
- Current Branch: `codex/browser-mcp-cli-skill`
- Current Worktree / Working Directory: `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill`
- Bootstrap Base Branch: `origin/main` at `9643f1459246c9f003196afc146a7f783eda6208`
- Remote Refresh Result: `git fetch --prune origin` succeeded on 2026-08-17; `origin/main` advanced from `e3d6de5` to `9643f14` before worktree creation.
- Task Branch: `codex/browser-mcp-cli-skill`
- Expected Base Branch (if known): `main`
- Expected Finalization Target (if known): `main`
- Bootstrap Blockers: None
- Notes For Downstream Agents: The shared main checkout contained unrelated untracked directories and was not used as the authoritative workspace. Use only this dedicated worktree for task artifacts/source changes.

## Supplemental Task Artifact Inventory

| Artifact Path | Purpose And Scope | Evidence, Context, Or Decision Captured | Core Artifact(s) Supported | Related Requirement / Acceptance-Criteria IDs (When Applicable) | Status | Approval Applicability / State | Follow-Up Needed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill/tickets/in-progress/browser-mcp-cli-skill/cli-conversion-analysis.md` | Focused conversion feasibility and decision analysis | Current architecture, real CDP identity probe, tool disposition, image/audio lessons/gaps, industry conversion heuristic, CLI principles, and resolved material decisions | Requirements and design spec | `REQ-001`–`REQ-012`; `AC-001`–`AC-012` | Current | Intended-behavior portions approved with the refined requirements on 2026-08-17 | Keep aligned with the design's portable skill-root and shared-core decisions. |

## Source Log

| Date | Source Type | Exact Source / Query / Command | Why Consulted | Relevant Findings | Follow-Up Needed |
| --- | --- | --- | --- | --- | --- |
| 2026-08-17 | Command | `git status --short --branch; git remote -v; git branch -vv; git worktree list --porcelain` in shared checkout | Establish repository state/isolation needs | Shared checkout was `main` with unrelated untracked content; dedicated task worktree required. | No |
| 2026-08-17 | Command | `git fetch --prune origin` | Refresh base before branching | Succeeded; latest `origin/main` was `9643f145...`. | No |
| 2026-08-17 | Setup | `git worktree add -b codex/browser-mcp-cli-skill /Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill origin/main` | Isolate authoritative task work | Worktree/branch created from refreshed remote main. | No |
| 2026-08-17 | Doc | `/Users/normy/autobyteus_org/autobyteus_mcps/.codex/skills/solution-designer/SKILL.md`, `design-principles.md`, templates | Apply required workflow/design authority | Requires approved requirements before design, evidence-backed production paths, and a revision record before architecture handoff. | No |
| 2026-08-17 | Doc | `/Users/normy/.codex/skills/.system/skill-creator/SKILL.md` | Establish skill structure/validation requirements | Skill needs concise `SKILL.md`, clear trigger metadata, optional bundled executable resources, recommended `agents/openai.yaml`, validation, and forward testing. | Yes — make the browser project itself the complete portable skill root. |
| 2026-08-17 | Code | `browser-mcp/src/browser_mcp/server.py` | Trace server/config/entry ownership | `create_server()` creates one `TabManager`; navigation progress is MCP-coupled; importing module invokes workspace/CWD initialization; two MCP transports supported. | Yes — target design |
| 2026-08-17 | Code | `browser-mcp/src/browser_mcp/tabs.py` | Trace current state owner | Process-local map binds short IDs to live `UIIntegrator` objects. Open always prepares a new integrator/page; list returns only tracked map; close can forward global browser close. | Yes — target identity/lifecycle |
| 2026-08-17 | Code | `browser-mcp/src/browser_mcp/tools/*.py`, `types.py`, `cleaning.py`, `utils.py` | Inventory tools, validation, results, file policy | Nine tools; operation bodies live inside MCP registration functions; DOM element IDs are snapshot-local; arbitrary JS is interaction escape hatch; path/URL/mode validation has gaps. | Yes — shared-core design |
| 2026-08-17 | Code | Installed `brui_core.ui_integrator.UIIntegrator` and `brui_core.browser.browser_manager.BrowserManager` via `inspect.getsource` | Verify actual browser lifecycle dependency | `UIIntegrator.initialize()` connects then creates a new page; browser manager uses Chromium `connect_over_cdp`, first context, and `stop_browser()` calls a Chrome-kill utility. | Yes — isolate connection owner, remove global close from CLI |
| 2026-08-17 | Doc/Code | `browser-mcp/README.md`, `pyproject.toml`, `scripts/browser_mcp_stdio.sh` | Verify public contract, packaging, launch behavior | Only server console entry exists; README defines strict explicit IDs, Chrome/CDP setup, stdout-sensitive MCP wrapper, and Python 3.11+. | Yes — CLI packaging/docs |
| 2026-08-17 | Code/Test | `browser-mcp/tests/test_server.py`, `tests/test_integration_real.py`, `tests/conftest.py` | Establish durable coverage/current scenarios | Fake in-memory MCP suite covers current tools; real suite covers open/attach/list/navigate/read/snapshot/script/screenshot and a script-based search/click flow. Real suite is not automatically skipped by a marker. | Yes — coverage investigation later |
| 2026-08-17 | Command/Test | `uv run --frozen --extra test pytest -q tests/test_server.py` in `browser-mcp` | Verify current local behavior in isolated worktree | Passed `21` tests. `uv` created the project `.venv` and installed locked dependencies. | No |
| 2026-08-17 | Probe | In-memory MCP `ClientSession.list_tools()` script under `uv run --frozen --extra test python` | Capture exact tool/input/output schemas | Confirmed nine tools, explicit required tab IDs on stateful operations, and structured result schemas. | No |
| 2026-08-17 | Doc | Browser ticket history: `strict-tab-id-contract`, `active-tab-default-behavior`, `attach-existing-tab` requirements/investigation | Understand why current contract differs from stale ticket narratives | Active-tab fallback was intentionally replaced by strict IDs for deterministic parallel workflows; attach support was added for existing authenticated CDP pages. Some old/in-progress ticket locations are stale relative to committed behavior. | No |
| 2026-08-17 | Code/Doc | `autobyteus-image-audio/src/image_audio_mcp/{cli,server,services}.py`, `pyproject.toml`, `README.md`, `DESIGN.md`, root `cli/autobyteus-image-audio` | Learn reference architecture/patterns | Task-oriented argparse CLI, wrapper-owned `uv run --frozen`, JSON envelopes, shared services, thin MCP, safe file service; generation operations are stateless. | No |
| 2026-08-17 | Test/Artifact | `autobyteus-image-audio/tests/test_cli_local.py` and `tickets/done/image-audio-mcp-cli/*`, `tickets/done/image-audio-cli-generation-config-json/*` | Assess completeness and later changes | Strong CLI validation exists, but no actual image/audio skill was found. `DESIGN.md` is stale versus later config flags; later investigation contains stale compatibility wording. | Yes — avoid drift, create real skill |
| 2026-08-17 | Command | `rg -l 'autobyteus-image-audio' /Users/normy/.codex/skills /Users/normy/.codex/plugins /Users/normy/autobyteus_org/autobyteus-agents` and repository tracked-file search | Locate claimed/reference skill | No image/audio `SKILL.md` found in inspected installed or repository paths. The earlier project is skill-facing only. | No |
| 2026-08-17 | Web/Spec | `https://playwright.dev/python/docs/api/class-browsercontext#browser-context-new-cdp-session` | Verify supported page CDP session boundary | Playwright officially exposes `browser_context.new_cdp_session(page)` and limits it to Chromium-based browsers. | Yes — platform constraints |
| 2026-08-17 | Web/Spec | `https://chromedevtools.github.io/devtools-protocol/tot/Target/` | Verify browser-owned target identity/discovery contract | Target IDs identify targets; target discovery/info methods provide target metadata. Relevant discovery/info methods are currently marked experimental. | Yes — compatibility risk/tests |
| 2026-08-17 | Code | Installed Playwright `driver/package/lib/server/chromium/crBrowser.js` around `Target.getTargetInfo` | Check local dependency behavior | Playwright itself calls `Target.getTargetInfo` without a target parameter during Chromium connection initialization. | No |
| 2026-08-17 | Probe/Test | Temporary `/tmp/browser_cli_cdp_identity_probe.py`, executed with project `uv run --frozen python`; isolated headless Google Chrome, temporary profile/port, two separate Playwright runtimes | Test daemon-free stable tab identity across CLI-like processes | Target ID `580D...B6D7B` was observed unchanged after disconnect/reconnect; matched title remained correct; reconnect succeeded after client close. Probe cleaned up owned Chrome/profile/script. | Yes — repeat cross-platform during implementation |
| 2026-08-17 | Command | `git log --oneline -- browser-mcp`; `git log --oneline -- autobyteus-image-audio ...` | Establish chronology/current authority | Strict-tab/attach changes are committed current behavior. Image/audio config was changed after its original CLI design, explaining doc drift. | No |
| 2026-08-17 | User Clarification | Conversation after initial analysis package | Identify the highest-priority UX and setup requirement | The skill should be guidance around ordinary Bash/shell CLI execution. First CLI invocation must automatically prepare the project `uv` environment; the agent must not perform environment setup. | Resolved by later approval: preserve as the bundled launcher bootstrap contract. |
| 2026-08-17 | Command | `printf 'PATH=%s'; command -v uv; command -v autobyteus-browser;` plus PATH membership checks | Answer how a short CLI command would be discovered on the current agent host | `~/.local/bin` and `/usr/local/bin` are on `PATH`; `uv` resolves to `/opt/homebrew/bin/uv`; `autobyteus-browser` does not yet exist/resolve. | Superseded for the primary contract: invoke the skill-bundled launcher by its skill-root path rather than registering a PATH command. |
| 2026-08-17 | Code/Doc | `/Users/normy/.codex/skills/.system/imagegen/{SKILL.md,references/cli.md,scripts/*}` and `/Users/normy/.codex/skills/.system/skill-creator/SKILL.md` | Verify how existing Codex skills expose CLI-like deterministic utilities | Skills can bundle executable Python/Bash resources under `scripts/`. Imagegen resolves its bundled CLI through `${CODEX_HOME:-$HOME/.codex}/skills/.system/imagegen/scripts/image_gen.py`; it does not depend on a PATH command. | Yes — bundle the browser launcher with the skill and invoke it through the skill root. |
| 2026-08-17 | User Clarification | Conversation after PATH explanation | Determine who may install/register the browser CLI | Human installation is explicitly rejected. Once an agent platform loads the skill, the agent must be able to execute its bundled CLI without a human-created symlink, PATH change, or checkout-specific absolute path. | Yes — replace PATH-shim recommendation with a self-contained skill bundle contract. |
| 2026-08-17 | Code/Doc | Installed `template-creator` and `presentations` skills under the local plugin cache | Find a vendor-neutral bundled-resource path convention | Both instruct the agent to set `SKILL_DIR` to the absolute directory containing the active `SKILL.md`, then invoke resources below that directory. | Yes — use this portable convention rather than any agent-vendor home variable. |
| 2026-08-17 | User Approval | Conversation after portable-path explanation | Lock the requirements basis and authorize independent continuation | User explicitly required cross-agent portability, prohibited `$CODEX_HOME` assumptions, confirmed that the skill itself must state its resource path clearly, and authorized continuing without further input. | Yes — requirements refined; recommended remaining decisions adopted for design. |
| 2026-08-17 | Command | `git branch --show-current`; `git rev-parse --show-toplevel HEAD origin/main`; `git status --short` | Re-verify isolation before design after approval | Authoritative workspace remains `/Users/normy/autobyteus_org/autobyteus_mcps-browser-mcp-cli-skill` on `codex/browser-mcp-cli-skill`; task HEAD still equals refreshed `origin/main` baseline `9643f145...`; only the ticket package is untracked. | No — bootstrap remains valid for design. |
| 2026-08-17 | Architecture Read | Current browser source, installed `brui_core` source, approved requirements/supplement, design principles/examples | Finalize ownership and target layout | Whole-project skill root avoids a copied runtime; MCP-centric root/namespace would misstate the new owner; one `BrowserApplication` plus a no-page `BrowserRuntime` lets CLI/MCP share behavior while Chrome owns tab state. | Yes — captured in `design-spec.md`. |
| 2026-08-17 | Architecture Review | `design-review-report.md` (`ARCH-REV-001`) and `architecture-review-revision-record.md` | Review SR-001 before implementation | Result `Fail / Design Impact`; core architecture passed. Findings: `DR-001` launcher loses uv-failure encoding through `exec`; `DR-002` HTTP exposure unassessed; `DR-003` current stdio wrapper undisposed; `DR-004` stale artifact state. | Yes — corrected in SR-002 and returned for re-review. |

## Relevant Existing Behavior And Production Paths

| Behavior ID | Kind | Current Supported Trigger Or Governing Contract | Current Production Path And Lifecycle | Meaningful Current Outcome / Invariants | Evidence |
| --- | --- | --- | --- | --- | --- |
| `BEH-001` | Contract | MCP client invokes any registered browser tool. | MCP transport -> `FastMCP` server -> registered nested tool -> `TabManager`/Playwright -> structured MCP result/error. Server process lifetime owns the manager. | Exactly nine tools are exposed; stateful tools require explicit short numeric tab IDs. | `server.py`, `tools/*.py`, schema probe, `test_server.py` |
| `BEH-002` | User/Contract | Client calls `open_tab` or `attach_tab` to establish a target. | Tool -> `TabManager` -> `prepare_integrator()` -> `UIIntegrator.initialize()` creates temporary/new page -> map short ID to live object; attach replaces the temporary page with unique existing match. | Only mapped pages can be addressed; ambiguous/no attach match fails. | `tabs.py`, attach tests, installed `UIIntegrator` source |
| `BEH-003` | Contract | Client calls `list_tabs`/tab-scoped operation with an explicit ID. | Tool -> process-local manager lookup/list -> page operation -> typed result. | No active-tab fallback; untracked IDs fail; list shows tracked pages only. | strict-tab ticket, `tabs.py`, tool modules/tests |
| `BEH-004` | User/Operational | Client requests screenshot or configures `AUTOBYTEUS_AGENT_WORKSPACE`. | Server import may chdir -> screenshot resolves candidate path (absolute accepted; relative from CWD) -> creates parents -> Playwright writes. | Screenshot returns absolute resolved path, but workspace is not an enforcement boundary for absolute paths. | `server.py`, `utils.py`, `screenshot.py` |
| `BEH-005` | User/Contract | Client calls `dom_snapshot` then `run_script` for interaction. | DOM JS collects visible elements/selectors -> caller chooses selector -> arbitrary page JS executes via Playwright evaluation. | Snapshot labels `e1...` are local to one snapshot; selector is actionable. No first-class click/type tool exists. | `dom_snapshot.py`, `run_script.py`, real Google search/click test |
| `BEH-006` | Operational | Client passes `close_browser=true` to `close_tab`. | Tool -> manager -> integrator close -> browser manager `stop_browser()` -> connection reset + Chrome kill utility. | May terminate more than the addressed page/browser instance; too destructive for implicit skill use. | `close_tab.py`, `tabs.py`, installed `brui_core` source |
| `BEH-007` | Operational | User/agent invokes image/audio root wrapper. | Root wrapper -> `uv --directory ... run --frozen` -> argparse CLI -> shared services -> provider/filesystem -> JSON stdout. | Environment prep is hidden; operations are stateless; MCP and CLI share services. No actual image/audio skill was found. | image/audio wrapper/source/docs/tickets and installed-skill search |
| `BEH-008` | Contract | User/agent invokes a browser CLI/skill. | `No Current Path`. | No browser console command or browser skill currently exists. | `browser-mcp/pyproject.toml`, root `cli/` inventory, skill searches |

## Design Health Assessment Evidence

- Change posture: `Larger Requirement`
- Candidate root cause classification: `Boundary Or Ownership Issue` (secondary `File Placement Or Responsibility Drift`)
- Refactor posture evidence summary: The current MCP behavior is internally coherent for one long-lived server, but its transport-bound nested tool bodies and process-local ID owner cannot be reused cleanly by short-lived CLI commands. Shared application ownership must be extracted; naive addition would duplicate policy or force the CLI through MCP.

| Evidence Source | Observation | Design Health Implication | Follow-Up Needed |
| --- | --- | --- | --- |
| `server.py` + tool modules | Server constructs state owner; MCP decorators enclose execution; navigation takes MCP context. | MCP is not a thin adapter and cannot remain the authoritative application boundary for CLI. | Define shared core and adapter dependency direction. |
| `tabs.py` + process model | Short IDs map to live nonserializable Playwright objects. | IDs cannot be persisted across CLI process exit. | Approve CDP target IDs or daemon alternative. |
| `UIIntegrator` source | Initialization always creates a page. | Reusing it for every CLI command would create stray pages. | Introduce connection context that can resolve existing targets without opening. |
| Real CDP probe | Browser-owned target ID survives independent client connections. | Stateless process CLI is viable; Chrome can own durable tab state. | Cross-platform validation and risk treatment. |
| Image/audio source/tickets | Shared services and wrapper are good; skill missing and docs drift. | Reuse architecture principles, not artifacts blindly. | Make skill/versioned docs part of acceptance. |
| Safety code paths | Global browser close, arbitrary output paths, broad URL check. | Skill prose alone is insufficient; shared core must enforce policy. | Specify URL/path/lifecycle constraints. |

## Relevant Files / Components

| Path / Component | Current Responsibility | Finding / Observation | Design / Ownership Implication |
| --- | --- | --- | --- |
| `browser-mcp/src/browser_mcp/server.py` | Workspace init, config, server construction/run | Import side effect; creates `TabManager`; transport config and runtime ownership mixed. | Keep adapter-specific config/launch separate from shared browser core. |
| `browser-mcp/src/browser_mcp/tabs.py` | Process-local tracked tab lifecycle | Correct current MCP state owner, but identity is not cross-process and depends on live objects. | Replace/reframe for browser-owned target resolution if recommended model approved. |
| `browser-mcp/src/browser_mcp/tools/*.py` | MCP registration and most operation execution | MCP boundary and application logic are mixed. | Thin MCP adapter should translate/call shared operations only. |
| `browser-mcp/src/browser_mcp/types.py` | Typed result shapes | Shapes are reusable conceptually but tied to current metadata/ID semantics and use `TypedDict` only. | Define tight canonical application/CLI result/error structures, then adapter translations. |
| `browser-mcp/src/browser_mcp/cleaning.py` | HTML cleaning | Transport-neutral and reusable; mode validation should be explicit. | Retain under shared core concern. |
| `browser-mcp/src/browser_mcp/utils.py` | URL test/output path resolution | Insufficient policy for agent CLI safety. | Strengthen under shared core; do not leave only in CLI parser. |
| `browser-mcp/scripts/browser_mcp_stdio.sh` | Current documented MCP stdio launch | Supported GUI/client path with useful stdout isolation/PATH/uv/log behavior, but it names the old root/module. | Retain capability by renaming/updating to `autobyteus-browser/scripts/autobyteus-browser-mcp`; remove old path and update active docs/config. |
| `browser-mcp/tests/test_server.py` | In-memory MCP boundary coverage | 21 current tests pass; fake page objects useful for shared service tests after refactor. | Preserve/refactor reusable test doubles and adapter parity checks. |
| `browser-mcp/tests/test_integration_real.py` | Real browser MCP workflows | Strong current operation coverage; includes script-based action loop. | Rebase scenarios on shared core/CLI and retained MCP as approved. |
| `autobyteus-image-audio/src/image_audio_mcp/services.py` | Shared stateless capability boundary | Strong reference for adapter ownership, not browser lifecycle. | Reuse ownership principle only. |
| `autobyteus-image-audio/src/image_audio_mcp/cli.py` | Task argparse/JSON/exit adapter | Useful basic pattern; error codes unversioned/exception-derived. | Improve browser contract rather than copy verbatim. |
| `cli/autobyteus-image-audio` | Path-independent wrapper/uv setup | Wrapper self-location and uv setup are reusable patterns; shell-built JSON and repo-external skill location are not. | Create a robust browser launcher inside the browser skill root. |
| `autobyteus-image-audio/DESIGN.md` | Intended long-lived design doc | Stale config flag descriptions after later CLI change. | Require docs/design alignment gate. |

## Runtime / Probe Findings

| Date | Method | Exact Command / Method | Observation | Implication |
| --- | --- | --- | --- | --- |
| 2026-08-17 | Test | `uv run --frozen --extra test pytest -q tests/test_server.py` | `21` tests passed; locked environment created cleanly. | Current MCP behavior is a stable baseline; wrapper-owned uv flow is viable. |
| 2026-08-17 | Probe | In-memory MCP client `list_tools()` | Nine exact schemas captured; stateful IDs required; no click/fill commands. | Command coverage must reflect actual public inventory, not stale fake locator helpers. |
| 2026-08-17 | Probe | Isolated headless Chrome + two Playwright/CDP client lifecycles via temporary Python script | Same `TargetID` resolved the page after complete Playwright disconnect/reconnect; title matched; Chrome remained reachable. | Recommended daemon-free cross-command identity model is technically feasible. |

## External / Public Source Findings

- Public source: [Playwright Python BrowserContext API](https://playwright.dev/python/docs/api/class-browsercontext#browser-context-new-cdp-session)
- Freshness: Accessed 2026-08-17; web result crawled within weeks.
- Relevant contract: A browser context can create a CDP session for a page/frame; CDP sessions are Chromium-only.
- Why it matters: Supports obtaining browser-owned target information without relying on Playwright private Python attributes, but confirms the Chrome/Chromium platform constraint.

- Public source: [Chrome DevTools Protocol Target domain](https://chromedevtools.github.io/devtools-protocol/tot/Target/)
- Freshness: Tip-of-tree protocol accessed 2026-08-17.
- Relevant contract: Target IDs identify browser targets; discovery/information APIs expose target metadata. The relevant target discovery/info methods are currently experimental.
- Why it matters: The approved canonical ID is browser-owned and survives client processes, but protocol/version regression risk must be tested and bounded.

## Reproduction / Environment Setup

- Required services, mocks, emulators, or fixtures: Local fake tests require tracked `.env.test`; real identity probe used isolated headless Google Chrome and a temporary profile/loopback port.
- Required config, feature flags, env vars, or accounts: Browser project normally uses `CHROME_USER_DATA_DIR` and optional remote debugging port. No credentials were used for the feasibility probe.
- External repos, samples, or artifacts cloned/downloaded for investigation: None.
- Setup commands that materially affected the investigation: `uv run --frozen --extra test` created the task worktree's ignored `.venv`; no tracked source was changed.
- Cleanup notes for temporary investigation-only setup: Probe terminated its own isolated Chrome process group, removed its temporary profile and `/tmp` script. Project `.venv` remains ignored as normal local runtime state.

## Findings From Code / Docs / Data / Logs

### Browser-specific conclusions

- The current strict explicit-ID behavior is a deliberate correctness decision and should remain; only the identity source should change if approved.
- Browser-owned target IDs make separate commands possible without a daemon and allow CLI/MCP interoperability if both use the same core.
- `list_tabs` semantics must change or an additional persistence layer must exist. Metadata such as `created_at` and `attached_by` cannot be truthfully reconstructed from the current browser connection alone.
- `attach_tab` remains useful as deterministic unique-match discovery, but no longer needs a “register in this process” side effect under the recommended model.
- A shared connection owner should connect to the current context without auto-creating a page, resolve a target, execute, and disconnect without terminating Chrome.
- Global browser termination must not be part of ordinary CLI/skill use.

### Image/audio reference conclusions

- The wrapper + project CLI + shared service + thin MCP shape is the strongest reusable lesson.
- Image/audio does not supply an actual skill artifact despite repeated “skill-facing” wording.
- Its current source/README use nested JSON config, while `DESIGN.md` still describes removed flags, demonstrating why implementation must update durable design/docs and skill together.
- Its simple JSON envelope is a good start but not sufficient for a stateful agent loop; stable error codes/retryability/schema version are preferable.

### Industry hypothesis conclusion

- The hypothesis is directionally correct for stateless or externally-stateful capabilities.
- A skill is not a substitute for transport/runtime guarantees. It can carry procedural knowledge, but state identity, safety, errors, artifacts, concurrency, and lifecycle must be explicit in the CLI/core.
- MCP-specific features such as server-held connection state, progress/notifications, streaming, elicitation/sampling, and schema discovery require deliberate CLI replacements or may make conversion unsuitable.

### User-prioritized shell/bootstrap conclusion

- The visible agent contract starts by setting `SKILL_DIR` to the absolute directory containing the loader-activated `SKILL.md`, then invoking `bash "$SKILL_DIR/scripts/autobyteus-browser" <command> ...`.
- The skill uses the available Bash/shell execution tool and normally issues one CLI command per tool call.
- The bundled launcher, not the skill prose, human, or agent, resolves its packaged runtime and runs locked `uv` execution.
- First invocation is allowed to take longer while `uv` creates/synchronizes the runtime environment; setup diagnostics stay on stderr and the final command result remains structured stdout.
- `uv` is the host prerequisite. The wrapper should detect its absence and fail clearly rather than installing host software implicitly.
- A short `autobyteus-browser` command is not discovered automatically and is therefore not the primary skill contract. The skill invokes its bundled script by the skill-root path and requires no PATH registration or repository checkout discovery.

## Persisted Data Transition Evidence (When Applicable)

- Current stored subject, location, representative shape, and approximate volume: Chrome profile/cookies/site storage are Chrome-owned; screenshot artifacts are user-directed files. Current `TabManager` map/IDs are memory-only.
- Relevant code-model, serialization, semantic, or physical-store change: Target identity changes from process-local numeric alias to live Chrome target ID; no stored schema is transformed.
- Normal readers and writers, including unknown/extra-field behavior: Chrome/Playwright own profile data; browser MCP reads/acts through the live context. No repository data reader/writer exists for tab IDs.
- Representative direct-read or compatibility evidence: Independent CDP reconnection resolved the same live page by target ID without transforming profile/tab data.
- Required semantics and invariants preserved by direct use: `Yes` for live tab identity in the current Chrome probe; broader platform coverage pending.
- Physical storage, privacy/security, disposal, rebuild, or operational constraints: Do not delete/replace user profile; do not globally terminate Chrome; constrain artifacts.
- Concrete benefit, cost, and risk of migration if it remains a candidate: No migration candidate. Persisting old short IDs would add invalid compatibility state and is rejected.
- Existing migration framework or lifecycle constraints, only if migration may be required: N/A.

## Constraints / Dependencies / Compatibility Facts

- Python project requirement is `>=3.11`; current lock resolved Python 3.13 successfully in the task worktree.
- `brui-core>=2.0.0` currently supplies Playwright/Chrome CDP lifecycle and is not itself transport-neutral around page creation.
- Current short numeric tab IDs are explicitly human-readable and max six digits, but they have only MCP-process meaning.
- Current public behavior is Chrome/Chromium-specific despite generic “browser” naming.
- No backward-compatibility wrapper/dual identity is allowed in the target. If retained MCP moves to CDP IDs, old short IDs break cleanly.
- The image/audio wrapper requires `uv`; the current agent host already provides it. Browser bootstrap must not turn missing `uv` into a human installation instruction.

## Open Unknowns / Risks

1. CDP target-info reliability outside the validated macOS Google Chrome probe; first-release implementation must test the approved Bash-capable macOS/Linux matrix where available.
2. Concurrent external CLI processes sharing one Chrome context; target identity remains deterministic, but browser/site-level operation races cannot be fully serialized across processes.
3. Explicit non-loopback streamable-HTTP binds remain unauthenticated by this package. The new loopback default and warning reduce accidental exposure, but externally protected remote deployments remain operator-owned and out of scope.
4. The launcher readiness handshake adds secure temporary-file behavior that must be validated across supported Bash/macOS/Linux environments.

## Notes For Architecture Reviewer

SR-002 resolves `ARCH-REV-001` findings `DR-001`–`DR-004`. Re-review the cumulative package; do not route to implementation unless architecture review passes.
