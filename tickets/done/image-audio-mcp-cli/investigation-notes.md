# Investigation Notes

## Investigation Status

- Bootstrap Status: Complete
- Current Status: Investigation complete for requirements; pending user approval before design handoff
- Investigation Goal: Extract the clean requirement for an `autobyteus-image-audio` CLI from the stale broad CLI ticket, verify the current code structure, and produce a design-ready requirements basis without workflow-state artifacts.
- Scope Classification (`Small`/`Medium`/`Large`): Medium
- Scope Classification Rationale: One MCP project, but implementation likely spans service extraction, a new CLI module, pyproject script, root wrapper, test bootstrap cleanup, local/mock tests, MCP compatibility checks, and docs.
- Scope Summary: Add a direct terminal CLI for `autobyteus-image-audio` while preserving MCP mode.
- Primary Questions To Resolve:
  - What current tool functions and package entrypoints exist in `autobyteus-image-audio`? Resolved.
  - Are tool implementations importable outside `create_server()` or do they require service extraction? Resolved: extraction required.
  - What should the first CLI command set expose? Resolved recommendation: all seven public MCP capabilities.
  - How should CLI execution preserve `uv` project isolation and credential/model configuration behavior? Resolved recommendation: project script plus path-independent root wrapper using `uv --directory ... run --frozen`.

## Request Context

The user reported that the existing worktree/ticket for CLI work was likely run incorrectly and created workflow-state files. The user asked to redo the ticket, bootstrap a new ticket from the requirement, and remove or avoid those workflow-state artifacts. The intended requirement is a CLI for image/audio MCP, not the stale broad multi-MCP workflow. The clarified future consumer is an agent skill that documents CLI usage. Agents should invoke a simple CLI command only; they must not need to install/sync the project environment manually or understand the runtime setup details. Therefore the CLI wrapper/script must keep `uv run` in the internal command path so the project `.venv` and dependencies are created/synced automatically on first use, while user-facing skill guidance remains simple. The CLI should translate existing MCP capabilities into polished command-line commands/options rather than exposing raw MCP invocation mechanics. The MCP tool list should be treated as capability coverage, not a rigid command-shape mandate.

## Environment Discovery / Bootstrap Context

- Project Type (`Git`/`Non-Git`): Git
- Task Workspace Root: `/Users/normy/autobyteus_org/autobyteus_mcps-image-audio-mcp-cli`
- Task Artifact Folder: `/Users/normy/autobyteus_org/autobyteus_mcps-image-audio-mcp-cli/tickets/in-progress/image-audio-mcp-cli`
- Current Branch: `codex/image-audio-mcp-cli`
- Current Worktree / Working Directory: `/Users/normy/autobyteus_org/autobyteus_mcps-image-audio-mcp-cli`
- Bootstrap Base Branch: `origin/main`
- Remote Refresh Result: `git fetch origin --prune` completed successfully on 2026-05-05 before fresh worktree creation.
- Task Branch: `codex/image-audio-mcp-cli`
- Expected Base Branch (if known): `origin/main`
- Expected Finalization Target (if known): `origin/main`
- Bootstrap Blockers: None
- Notes For Downstream Agents: Do not use or recreate workflow-state/stage-control artifacts. This ticket uses `requirements.md`, `investigation-notes.md`, and, after approval, `design-spec.md` only.

## Source Log

| Date | Source Type (`Code`/`Doc`/`Spec`/`Web`/`Repo`/`Issue`/`Command`/`Trace`/`Log`/`Data`/`Setup`/`Other`) | Exact Source / Query / Command | Why Consulted | Relevant Findings | Follow-Up Needed |
| --- | --- | --- | --- | --- | --- |
| 2026-05-05 | Command | `git -C /Users/normy/autobyteus_org/autobyteus_mcps fetch origin --prune` | Refresh tracked remote refs before creating fresh task worktree | Completed successfully | No |
| 2026-05-05 | Command | `git worktree add -b codex/image-audio-mcp-cli /Users/normy/autobyteus_org/autobyteus_mcps-image-audio-mcp-cli origin/main` | Create dedicated clean ticket worktree/branch from latest tracked base | Created branch/worktree at commit `d04d9ab` | No |
| 2026-05-05 | Other | `/Users/normy/autobyteus_org/autobyteus_mcps-mcp-cli-tools/tickets/in-progress/mcp-cli-tools/{requirements.md,investigation-notes.md,workflow-state.md}` | Inspect stale ticket before cleanup | Stale ticket was a broad multi-MCP CLI rollout and included workflow-state stage-control artifact; user requested rebootstrap | Extracted only image/audio CLI requirement; stale ticket not continued |
| 2026-05-05 | Command | `rm -rf /Users/normy/autobyteus_org/autobyteus_mcps-mcp-cli-tools/tickets/in-progress/mcp-cli-tools && git worktree remove /Users/normy/autobyteus_org/autobyteus_mcps-mcp-cli-tools --force && git branch -D codex/mcp-cli-tools` | Remove stale incorrect worktree/ticket artifacts | Removed stale in-progress ticket folder, old worktree, and old `codex/mcp-cli-tools` branch; no committed source diff existed | No |
| 2026-05-05 | Command | `git status --short --branch` in fresh worktree | Confirm clean branch state | Only new ticket artifacts are untracked | No |
| 2026-05-05 | Code | `autobyteus-image-audio/pyproject.toml` | Inspect package metadata and entrypoints | Project requires Python `>=3.11,<3.12`, depends on `mcp>=1.13.1` and `autobyteus==1.4.3`, has `autobyteus-image-audio-server` script only, and has `uv.lock` | Add CLI script in design/implementation |
| 2026-05-05 | Doc | `autobyteus-image-audio/README.md` | Inspect documented MCP tools/env/path behavior | Seven public tools documented; output paths are resolved with `resolve_safe_path`; `uv` is recommended for dependency isolation | CLI docs must preserve/separate MCP docs |
| 2026-05-05 | Doc | `autobyteus-image-audio/DESIGN.md` | Inspect current architecture notes | Current design says server is a thin MCP wrapper, stateless calls create/cleanup clients, safe file writes use `resolve_safe_path` | Update design docs after CLI/service extraction |
| 2026-05-05 | Code | `autobyteus-image-audio/src/image_audio_mcp/server.py` | Inspect current implementation and ownership | `create_server()` registers all public tools as nested closures; generation/edit/speech/coordinate logic is not importable as CLI services; helper functions are module-level; `_find_target_coordinates_vlm_impl` is a nested helper with no observed references outside its definition | Design service extraction and possible unused-helper cleanup |
| 2026-05-05 | Code | `autobyteus-image-audio/tests/test_server_local.py` | Inspect local MCP tests | Tests use in-memory MCP client, monkeypatch model/factory behavior, verify hidden grounding tools remain excluded, and test coordinate marker behavior | Reuse patterns for MCP compatibility and service tests |
| 2026-05-05 | Code | `autobyteus-image-audio/tests/test_integration.py` | Inspect remote/provider tests | Integration tests already skip when required env values are missing | Keep provider tests credential-gated |
| 2026-05-05 | Code | `autobyteus-image-audio/tests/conftest.py` | Inspect test bootstrap | Raises `FileNotFoundError` if `.env.test` is missing, blocking clean local test collection before integration skip helpers can run | Fix required in implementation scope |
| 2026-05-05 | Command | `uv run --frozen python - <<'PY' ... create_server() ... PY` in `autobyteus-image-audio` | Probe clean `uv` environment and importability | `uv` created `.venv`, installed locked dependencies, built package, and `create_server()` imported successfully. Current shell has env overrides for default model identifiers; values intentionally not recorded. | Use `uv --directory ... run --frozen` in CLI wrapper/docs |
| 2026-05-05 | Command | `uv run --frozen python -m compileall -q src` in `autobyteus-image-audio` | Verify current source compiles before design | Passed | No |
| 2026-05-05 | Command | `uv run --frozen pytest tests/test_server_local.py -q` in `autobyteus-image-audio` | Probe local test execution | Failed because pytest is not installed unless optional test extra is requested | Use `--extra test` for validation |
| 2026-05-05 | Command | `uv run --frozen --extra test pytest tests/test_server_local.py -q` in `autobyteus-image-audio` | Probe local test collection with test extra | Failed at conftest import because `.env.test` is missing | Fix conftest/test bootstrap in scope |
| 2026-05-05 | Command | `git worktree list --porcelain && git branch --list 'codex/mcp-cli-tools' 'codex/image-audio-mcp-cli'` | Confirm stale worktree/branch cleanup and new branch presence | Only main and fresh `codex/image-audio-mcp-cli` worktrees remain; old branch absent | No |
| 2026-05-05 | User Clarification | Conversation clarification after bootstrap | Confirm intended usage model | Future skill will document a simple CLI; agents invoke CLI only and must not run setup/activation or reason through setup details. CLI wrapper/script must internally auto-provision the project uv environment via `uv run`. | Update design to make wrapper/environment provisioning a first-class boundary while keeping user-facing docs simple |
| 2026-05-05 | User Clarification | Conversation clarification after design draft | Confirm CLI UX expectation | The CLI should expose the original MCP capabilities, but the designer/implementation should choose the most intuitive command-line shape rather than mechanically copying the user's wording or raw MCP schemas. | Add explicit CLI UX authority/projection rules to requirements/design |

## Current Behavior / Current Flow

- Current entrypoint or first observable boundary: MCP clients launch `autobyteus-image-audio-server` or `python -m image_audio_mcp.server`, usually via `uv --directory <project> run ...`.
- Current execution flow:
  1. MCP client starts process in the project environment.
  2. `image_audio_mcp.server:main()` calls `create_server()`.
  3. `create_server()` constructs `FastMCP` and registers nested tool closures.
  4. MCP client calls one of the seven public tools.
  5. Tool closure resolves workspace/path/model configuration, creates Autobyteus client/factory, performs provider call or model listing, downloads/writes output when applicable, and cleans up clients.
- Ownership or boundary observations:
  - `server.py` currently owns both MCP transport registration and capability execution.
  - Helper functions for workspace/path/model/media/coordinate parsing are module-level and reusable, but the actual tool execution functions are nested and not importable.
  - The existing MCP boundary is healthy for MCP-only use, but it is not an authoritative reusable execution boundary for both MCP and CLI.
- Current behavior summary: MCP mode is the only supported public interface. There is no CLI console script for user/tool commands. `uv` project isolation works. Clean local test execution is blocked by required `.env.test` in conftest.

## Design Health Assessment Evidence

- Change posture (`Feature`/`Bug Fix`/`Behavior Change`/`Refactor`/`Cleanup`/`Performance`/`Larger Requirement`): Feature
- Candidate root cause classification (`Local Implementation Defect`/`Missing Invariant`/`Boundary Or Ownership Issue`/`Duplicated Policy Or Coordination`/`File Placement Or Responsibility Drift`/`Shared Structure Looseness`/`Legacy Or Compatibility Pressure`/`No Design Issue Found`/`Unclear`): Boundary Or Ownership Issue
- Refactor posture evidence summary: Refactor needed now. Adding CLI directly into `server.py` would overload the MCP transport file and duplicate execution policy. The correct target is a shared service owner under `image_audio_mcp` that both surfaces call.

| Evidence Source | Observation | Design Health Implication | Follow-Up Needed |
| --- | --- | --- | --- |
| User request | Stale ticket/process artifacts should be removed; new image/audio CLI ticket should be bootstrapped | Requirements must be cleanly narrowed and workflow-state artifacts excluded | No |
| `server.py:create_server()` | Public tool implementations are nested closures | CLI cannot import the actual behavior without transport coupling; service extraction needed | Yes |
| `server.py` helper functions | Path/model/media helpers are already module-level | Service extraction can reuse/move these without changing public MCP schemas | Yes |
| `pyproject.toml` | Only server script exists | Add separate CLI script while preserving server script | Yes |
| `tests/conftest.py` | Missing `.env.test` aborts local test collection | Validation infrastructure must be corrected for clean checkout/local tests | Yes |
| `uv run --frozen` import probe | Project env sync/import works | Wrapper/docs can depend on `uv --directory ... run --frozen` | No |

## Relevant Files / Components

| Path / Component | Current Responsibility | Finding / Observation | Design / Ownership Implication |
| --- | --- | --- | --- |
| `autobyteus-image-audio/src/image_audio_mcp/server.py` | MCP server setup, tool registration, helper functions, tool execution | Mixed transport and business execution; nested closures block direct CLI reuse | Extract service functions; leave server as thin MCP facade |
| `autobyteus-image-audio/src/image_audio_mcp/__init__.py` | Package version marker | No CLI exports | Likely unchanged |
| `autobyteus-image-audio/pyproject.toml` | Project metadata, dependencies, server script | Has `autobyteus-image-audio-server`; no CLI script; has optional test dependencies | Add CLI script; no new dependency expected |
| `autobyteus-image-audio/README.md` | MCP docs, tools, env vars, examples | MCP docs include both recommended `uv` and raw Python examples | Add separate CLI section, keep MCP docs intact |
| `autobyteus-image-audio/DESIGN.md` | Current MCP architecture/design notes | Mentions server.py as core owner | Update to reflect service boundary + dual surfaces |
| `autobyteus-image-audio/tests/test_server_local.py` | Local MCP tests using in-memory client and monkeypatching | Useful compatibility test pattern | Add or extend for service/CLI tests |
| `autobyteus-image-audio/tests/test_integration.py` | Remote/provider integration tests | Env-gated skip helpers exist | Keep optional; no mandatory provider calls |
| `autobyteus-image-audio/tests/conftest.py` | Test env loading | Requires untracked `.env.test` for all tests | Must be relaxed so local tests can run |
| `cli/autobyteus-image-audio` | Proposed root wrapper | Does not exist | Add path-independent wrapper in implementation |

## Runtime / Probe Findings

| Date | Method (`Repro`/`Trace`/`Probe`/`Script`/`Test`/`Setup`) | Exact Command / Method | Observation | Implication |
| --- | --- | --- | --- | --- |
| 2026-05-05 | Probe | `uv run --frozen python - <<'PY' ... create_server() ... PY` | Locked project environment synced and server object created | Confirms `uv --directory ... run --frozen` is viable CLI execution base |
| 2026-05-05 | Probe | `uv run --frozen python -m compileall -q src` | Passed | Current source is syntactically valid before changes |
| 2026-05-05 | Test | `uv run --frozen pytest tests/test_server_local.py -q` | Failed: `pytest` executable not installed without optional test extra | Validation should invoke `uv run --frozen --extra test pytest ...` |
| 2026-05-05 | Test | `uv run --frozen --extra test pytest tests/test_server_local.py -q` | Failed during conftest import because `.env.test` is missing | Implementation should change conftest behavior |

## External / Public Source Findings

- Public API / spec / issue / upstream source: None used.
- Version / tag / commit / freshness: N/A.
- Relevant contract, behavior, or constraint learned: N/A.
- Why it matters: N/A.

## Reproduction / Environment Setup

- Required services, mocks, emulators, or fixtures: Local tests should use mocked Autobyteus clients/factories; real generation requires provider credentials and possibly running model/provider services depending on configured defaults.
- Required config, feature flags, env vars, or accounts: `AUTOBYTEUS_AGENT_WORKSPACE` governs relative path safety. Defaults may be overridden by `DEFAULT_IMAGE_GENERATION_MODEL`, `DEFAULT_IMAGE_EDIT_MODEL`, `DEFAULT_SPEECH_GENERATION_MODEL`, and `DEFAULT_GROUNDING_MODEL`. Provider credentials may include Autobyteus/OpenAI/Gemini/Vertex-related env vars. Values were not recorded.
- External repos, samples, or artifacts cloned/downloaded for investigation: None.
- Setup commands that materially affected the investigation: Fresh worktree creation; stale worktree cleanup; `uv run --frozen` created ignored `.venv` and package build metadata inside `autobyteus-image-audio`.
- Cleanup notes for temporary investigation-only setup: Ignored `.venv`, `*.egg-info`, and `__pycache__` were created by probes and are not source artifacts. The stale `codex/mcp-cli-tools` worktree and branch were removed.

## Findings From Code / Docs / Data / Logs

### Public MCP tool inventory

- `health_check`
- `list_audio_models`
- `list_image_models`
- `generate_image`
- `edit_image`
- `generate_speech`
- `find_target_coordinates`

Hidden/removed grounding tools are explicitly tested as excluded in `tests/test_server_local.py`.

### Current execution boundaries

- MCP facade: `create_server()` and FastMCP decorators.
- Capability execution: currently inside nested closure bodies.
- Provider clients: Autobyteus `ImageClientFactory`, `AudioClientFactory`, `LLMFactory`.
- File safety and IO: `resolve_safe_path`, `download_file_from_url`.
- Workspace root: `AUTOBYTEUS_AGENT_WORKSPACE` or current process directory.

### Proposed CLI command set from requirements

- `health-check`
- `list-image-models`
- `list-audio-models`
- `generate-image`
- `edit-image`
- `generate-speech`
- `find-target-coordinates`

## Constraints / Dependencies / Compatibility Facts

- Existing project script `autobyteus-image-audio-server` must remain.
- Python remains constrained to `>=3.11,<3.12`.
- `uv.lock` exists, so `--frozen` is appropriate for wrapper/default docs. `uv run --frozen` is also the mechanism that hides project `.venv` creation/sync from agent callers.
- Safe path behavior must match MCP behavior.
- Existing MCP output shapes should be reused by services and returned under the CLI JSON `result` envelope.
- Provider/model availability is environment-dependent; real remote calls should not be mandatory for local validation.

## Open Unknowns / Risks

| Risk ID | Risk | Severity | Mitigation |
| --- | --- | --- | --- |
| RISK-001 | Service extraction accidentally changes MCP schemas or behavior | High | Keep MCP wrapper signatures stable; validate tool list/schema and safe calls |
| RISK-002 | Real generation credentials/model services unavailable in validation | Medium | Use mocked local tests; keep remote tests skipped unless env present |
| RISK-003 | `generation_config` CLI JSON errors cause confusing failures | Medium | Validate before async service call; structured usage error envelope |
| RISK-004 | Existing `.env.test` hard requirement blocks local tests | High | Change conftest to optional `.env.test` load; remote tests skip on missing env |
| RISK-005 | Root wrapper with `--frozen` fails if lockfile not updated after pyproject script change | Medium | Implementation must update lockfile as needed and validate wrapper |

## Notes For Architect Reviewer

If/when user approves the requirements basis, design review should focus on keeping the authoritative boundary clean:

- `server.py` should become a thin MCP facade and must not be the only owner of capability execution.
- `cli.py` should parse arguments and format JSON only; it should not duplicate provider/path/client logic.
- `services.py` (or equivalent) should own capability execution, model/default resolution, path normalization, provider client lifecycle, and result payloads reused by MCP and CLI.
- The root wrapper should be path-independent and should not introduce the stale ticket's absolute-path workflow/generation machinery. It should be the future skill-facing command, own automatic project environment provisioning through `uv run`, and keep those setup mechanics behind a simple CLI surface. The project CLI should be a polished command-line design over existing MCP capabilities, not a raw MCP/JSON-RPC wrapper or a mechanically copied schema. Generation config should be per-call CLI options (`--config key=value`) rather than a config file-first workflow; multi-speaker speech should use paired `--speaker NAME --voice VOICE` flags.
- Test bootstrap cleanup is part of the implementation because otherwise local validation in a clean worktree is blocked.
