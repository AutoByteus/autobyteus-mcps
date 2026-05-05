# Requirements Doc

## Status (`Draft`/`Design-ready`/`Refined`)

Design-ready

## Goal / Problem Statement

Create a fresh, narrowly scoped ticket for adding a direct command-line interface to the existing `autobyteus-image-audio` MCP project.

The previous `codex/mcp-cli-tools` worktree/ticket was a broad multi-MCP CLI rollout and included workflow-state/stage-control artifacts that the user said were produced by the wrong process. That stale work has been removed. This replacement ticket keeps only the clean requirement: users and coding agents need a terminal CLI for image/audio MCP capabilities without starting or speaking MCP, while existing MCP behavior remains intact. The future consumer is expected to be an agent skill: the skill will document simple CLI commands, and the agent should only invoke those commands. User/skill-facing guidance should not expose detailed environment setup mechanics as work the agent has to perform. The agent must not need to run `uv sync`, activate a virtual environment, install project dependencies manually, or know where the project `.venv` lives. The CLI wrapper/script must keep `uv` in the internal execution path so `uv run` automatically creates/syncs the project environment before executing the requested command. The CLI should expose the existing MCP capabilities through an intuitive command-line design, not as a raw MCP protocol surface or a generic `call-tool` wrapper. MCP tools are the capability inventory and compatibility target, but the CLI shape should be chosen for clear user/agent ergonomics rather than mechanically copying MCP schemas.

## Investigation Findings

- Fresh task worktree created at `/Users/normy/autobyteus_org/autobyteus_mcps-image-audio-mcp-cli` on branch `codex/image-audio-mcp-cli` from refreshed `origin/main`.
- Stale worktree `/Users/normy/autobyteus_org/autobyteus_mcps-mcp-cli-tools` and branch `codex/mcp-cli-tools` were removed after extracting the image/audio CLI requirement. The old stale in-progress folder contained `workflow-state.md`; the new ticket intentionally does not create that artifact.
- Target project is `autobyteus-image-audio/`.
- `autobyteus-image-audio/pyproject.toml` currently has only the MCP server console script: `autobyteus-image-audio-server = image_audio_mcp.server:main`.
- Current public MCP tools are `health_check`, `list_audio_models`, `list_image_models`, `generate_image`, `edit_image`, `generate_speech`, and `find_target_coordinates`.
- Tool bodies live as nested FastMCP closures inside `create_server()` in `src/image_audio_mcp/server.py`; helper functions and provider factories are module-level. A CLI should not duplicate those closures or call MCP internals. It needs an importable service boundary reused by both MCP and CLI.
- Existing safe path behavior uses `resolve_safe_path` with `AUTOBYTEUS_AGENT_WORKSPACE` fallback to current working directory. CLI must preserve this exact safety behavior for file inputs and outputs.
- `uv run --frozen` successfully creates/syncs the project environment and imports `create_server()` from a clean fresh worktree.
- Local pytest collection currently fails in a clean worktree because `tests/conftest.py` raises if `.env.test` is missing. CLI implementation should fix this validation blocker so local/mock tests run without private credentials; remote/provider tests should skip when required env is absent.

## Design Health Assessment (Mandatory)

- Change posture (`Feature`/`Bug Fix`/`Behavior Change`/`Refactor`/`Cleanup`/`Performance`/`Larger Requirement`): Feature
- Initial design issue signal (`Yes`/`No`/`Unclear`): Yes
- Root cause classification (`Local Implementation Defect`/`Missing Invariant`/`Boundary Or Ownership Issue`/`Duplicated Policy Or Coordination`/`File Placement Or Responsibility Drift`/`Shared Structure Looseness`/`Legacy Or Compatibility Pressure`/`No Design Issue Found`/`Unclear`): Boundary Or Ownership Issue
- Refactor posture (`Likely Needed`/`Likely Not Needed`/`Deferred`/`Unclear`): Likely Needed
- Evidence basis: MCP transport registration and business execution are currently coupled inside `server.py:create_server()` closures. Adding a CLI without extraction would either duplicate generation/speech/coordinate logic or force the CLI through an MCP transport boundary. A reusable service boundary is needed so MCP and CLI are two thin surfaces over one authoritative capability implementation.
- Requirement or scope impact: The ticket must include a narrow service extraction for `autobyteus-image-audio`, a new CLI entrypoint/wrapper, tests that exercise the shared service through both surfaces, and docs. Broad multi-MCP CLI infrastructure remains out of scope.

## Recommendations

1. Proceed with a new `image-audio-mcp-cli` ticket rather than reviving the stale broad `mcp-cli-tools` ticket.
2. Use direct import, not an MCP-client subprocess wrapper. Extract image/audio capability execution into `image_audio_mcp.services` and make both FastMCP tools and the CLI delegate to it.
3. Add a stdlib `argparse` CLI module instead of adding a new CLI framework dependency.
4. Add a project console script named `autobyteus-image-audio` and keep the existing `autobyteus-image-audio-server` script unchanged.
5. Add a path-independent repo wrapper `cli/autobyteus-image-audio` that internally calls `uv --directory <repo>/autobyteus-image-audio run --frozen autobyteus-image-audio "$@"`; do not commit host-specific absolute-path generated wrappers. This wrapper is the command an agent skill should document, so first invocation must automatically create/sync the project `.venv` through `uv run` without any separate setup step. User-facing examples should show the wrapper command, not the internal `uv` plumbing, except in a short implementation note.
6. Project CLI commands should be ergonomic, task-oriented projections of the MCP capabilities: readable subcommands, named flags for required/optional scalar fields, repeatable flags for list inputs, and dynamic per-call config options. Do not expose a generic `call-tool` command as the primary UX. Do not force a mechanical one-to-one shape if a different command shape is clearly more intuitive, but preserve coverage for every public MCP capability.
7. Keep JSON as the default and only required output format for this ticket.
8. Fix local test bootstrap so tests that do not need real provider credentials can run without `.env.test`.

## Scope Classification (`Small`/`Medium`/`Large`)

Medium

Rationale: one MCP project, but the change spans service extraction, a CLI entrypoint, wrapper script, test bootstrap cleanup, mock/local validation, MCP compatibility checks, and docs.

## In-Scope Use Cases

| Use Case ID | Use Case |
| --- | --- |
| UC-001 | A coding agent runs an image/audio health check from any current working directory and gets JSON without starting an MCP client/server session. |
| UC-002 | A user lists available image and audio models from the CLI in the project `uv` environment. |
| UC-003 | A user runs `generate-image` with a prompt, optional reference images, optional generation config, and an explicit output path; the command writes the image and prints JSON with the resolved file path. |
| UC-004 | A user runs `edit-image` with a prompt, optional input images/mask, optional generation config, and an explicit output path; the command writes the edited image and prints JSON with the resolved file path. |
| UC-005 | A user runs `generate-speech` with text, optional generation config, and an explicit output path; the command writes audio and prints JSON with the resolved file path. |
| UC-006 | A user runs `find-target-coordinates` with an image, target text, optional marked output path, and optional grounding model; the command prints JSON coordinates matching the MCP tool result shape. |
| UC-007 | Existing MCP clients continue to launch `autobyteus-image-audio-server` or `python -m image_audio_mcp.server` and see the same public tool names/schemas. |
| UC-008 | Local/mock tests can run in a clean checkout without private `.env.test`; remote/provider tests skip when credentials or model settings are absent. |

## Out of Scope

- Broad CLI rollout for `pdf_mcp`, `browser-mcp`, `ssh-mcp`, `tts-mcp`, `alexa-mcp`, `pptx-mcp`, `computer-use-mcp`, or `video-audio-mcp`.
- Any `workflow-state.md` or stage-control artifact for this ticket.
- Changing MCP tool names, public MCP schemas, or existing MCP server launch commands.
- A single shared monorepo Python environment for all MCPs.
- A host-specific generated wrapper system with committed absolute paths.
- Interactive CLI mode.
- Per-call model override for `generate-image`, `edit-image`, or `generate-speech`; those continue to use environment-configured defaults. `find-target-coordinates` may keep its existing `grounding_model_identifier` option.
- Real paid/provider generation as a mandatory automated test; it may be documented or skipped when credentials are absent.

## Functional Requirements

| Requirement ID | Requirement |
| --- | --- |
| REQ-001 | Add CLI as an additive surface over `autobyteus-image-audio`; do not remove, rename, or intentionally change existing MCP server entrypoints, tool names, input schemas, or result shapes. |
| REQ-002 | Preserve project-scoped dependency isolation. CLI execution must run through `uv --directory <absolute-or-wrapper-resolved-project-dir> run --frozen autobyteus-image-audio ...` or an equivalent wrapper-owned `uv run` path so the project `.venv` is automatically created/synced on first use. Agents must not need to run `uv sync`, activate `.venv`, or install Python dependencies manually. |
| REQ-003 | Add a project console script `autobyteus-image-audio = image_audio_mcp.cli:main`; keep `autobyteus-image-audio-server = image_audio_mcp.server:main`. |
| REQ-004 | Add a path-independent repo wrapper `cli/autobyteus-image-audio` that can be invoked from any current working directory and internally delegates to `uv --directory <repo>/autobyteus-image-audio run --frozen autobyteus-image-audio "$@"`. This wrapper is the intended future skill-facing command and must hide project environment setup from the invoking agent. |
| REQ-005 | CLI must provide intuitive command coverage for the public MCP capabilities: health check, image model listing, audio model listing, image generation, image editing, speech generation, and target-coordinate finding. The proposed baseline command names are `health-check`, `list-image-models`, `list-audio-models`, `generate-image`, `edit-image`, `generate-speech`, and `find-target-coordinates`; implementation may refine grouping or aliases if it improves usability without losing capability coverage. |
| REQ-006 | CLI command output must be JSON on stdout by default. Success envelope: `{"ok": true, "command": "...", "result": {...}}`. Failure envelope: `{"ok": false, "command": "...", "error_type": "...", "error_message": "..."}`. |
| REQ-007 | CLI failures must exit non-zero, emit the JSON failure envelope on stdout, and may emit a concise human-readable diagnostic on stderr. Usage errors must distinguish from runtime/provider/path errors. |
| REQ-008 | File-producing commands must require explicit `--output-file-path`, must reuse existing safe path resolution, and must report the resolved output path from the shared service result. |
| REQ-009 | CLI input media arguments must reuse existing media normalization: URLs/data URIs pass through; local paths resolve through `resolve_safe_path`; missing local files fail clearly. |
| REQ-010 | CLI argument design must be idiomatic and agent-friendly: scalar MCP fields become named flags, list fields such as `input_images` become repeatable flags such as `--input-image`, optional paths remain explicit path flags, and generation settings are passed dynamically per call with repeatable `--config key=value` options. Nested config keys should support dot notation such as `--config image_config.aspect_ratio=16:9`. A raw JSON config option may exist only as an advanced escape hatch, not the documented primary path; config files are not the preferred UX for per-call generation settings. |
| REQ-011 | Extract reusable async service functions for all public tool capabilities into an importable owner (for example `src/image_audio_mcp/services.py`). MCP tool closures and CLI handlers must both delegate to those services. |
| REQ-012 | Keep stateless client lifecycle semantics: each generation/edit/speech/coordinate call creates the needed Autobyteus client(s) and cleans them up after use. |
| REQ-013 | CLI `--help` must document required arguments, output behavior, relevant environment variables, path safety rules, provider credential expectations, and examples in user-friendly CLI terms. It may mention that the wrapper auto-prepares the project runtime, but it must not require users or agents to understand or perform the underlying `uv` setup steps. |
| REQ-014 | Local tests must cover service behavior with mocked Autobyteus clients and CLI argument/JSON handling without requiring provider credentials. |
| REQ-015 | Validation must include a command run from outside `autobyteus-image-audio/` proving the wrapper or documented `uv --directory` invocation uses and, when missing, creates/syncs the project environment automatically. |
| REQ-016 | Existing MCP compatibility must be validated at least by listing/calling safe MCP tools through an in-memory MCP client and verifying public tool names/schemas remain available. |
| REQ-017 | Fix the current `.env.test` collection blocker so local/mock tests can run in a clean checkout; remote integration tests should skip if credentials/model env vars are absent. |
| REQ-018 | Update `autobyteus-image-audio/README.md` and `DESIGN.md` with CLI usage, runtime flow, env vars, examples, and validation notes. |
| REQ-019 | Do not create or keep `workflow-state.md` or equivalent stage-control files for this new ticket. |
| REQ-020 | Do not make the primary CLI UX a raw MCP-tool interface, JSON-RPC client, or generic `call-tool --name ... --arguments ...` command. The CLI must be a thoughtful, task-oriented command-line design over the MCP capabilities with stable command names, stable option names, clear examples, and predictable errors. MCP parity is required for coverage, but MCP schema shape is not the authority for CLI ergonomics. |
| REQ-021 | Multi-speaker speech generation must provide an explicit, readable paired CLI syntax: repeated `--speaker NAME --voice VOICE` pairs. The CLI must validate that speaker and voice counts match and build `generation_config.speaker_mapping` in pair order. |

## Acceptance Criteria

| Acceptance Criteria ID | Criteria |
| --- | --- |
| AC-001 | `git worktree list` shows the stale `codex/mcp-cli-tools` worktree removed and a fresh `codex/image-audio-mcp-cli` worktree present. |
| AC-002 | The new ticket artifact folder contains `requirements.md` and `investigation-notes.md` and does not contain `workflow-state.md`. |
| AC-003 | From `/tmp` or another unrelated directory, `cli/autobyteus-image-audio health-check` prints a JSON success envelope without any prior `uv sync`, `.venv` activation, or manual dependency installation step by the caller. |
| AC-004 | `cli/autobyteus-image-audio --help`, the underlying `uv --directory autobyteus-image-audio run --frozen autobyteus-image-audio --help`, and each in-scope subcommand `--help` succeed and document key env/path/auto-provisioning behavior plus practical examples. |
| AC-005 | `list-image-models` and `list-audio-models` return JSON envelopes whose `result.models` entries include model identifiers and parameter/default config schema data, or fail with a clear structured runtime error if Autobyteus initialization fails. |
| AC-006 | Mocked local tests prove `generate-image`, `edit-image`, and `generate-speech` service functions write/download to the expected resolved output path and return the same result shape used by MCP. |
| AC-007 | Mocked/in-process CLI tests prove `generate-image`, `edit-image`, `generate-speech`, and `find-target-coordinates` parse arguments, call the shared service boundary, and print the standardized JSON envelope. |
| AC-008 | MCP compatibility validation proves the public tool list still includes exactly the expected exposed tools and excludes hidden grounding tools. |
| AC-009 | `uv run --frozen --extra test pytest` can collect and run local/mock tests in a clean checkout without `.env.test`; remote/provider tests skip cleanly when credentials are absent. |
| AC-010 | Documentation contains simple wrapper-based CLI examples for health check, model listing, image generation, image editing, speech generation, and coordinate finding; setup internals stay in a short implementation note rather than the main usage flow. |
| AC-013 | The implemented CLI exposes intuitive task-oriented subcommands/options covering each in-scope MCP capability and does not require users or agents to pass raw MCP JSON arguments to a generic `call-tool` command for normal use. |
| AC-014 | Multi-speaker speech can be invoked with `--speaker Joe --voice Kore --speaker Jane --voice Puck`; the resulting service call receives `generation_config.speaker_mapping` with matching speaker/voice objects in order, and mismatched speaker/voice counts fail with a clear usage error. |
| AC-011 | Existing MCP launch docs remain present and are clearly separate from CLI docs. |
| AC-012 | No source or doc change introduces a broad multi-MCP CLI rollout or host-specific generated absolute-path wrapper system. |

## Constraints / Dependencies

- Python requirement remains `>=3.11,<3.12` for `autobyteus-image-audio`.
- Runtime dependency on `autobyteus==1.4.3` remains.
- Provider credentials may be needed for real generation/edit/speech calls: Autobyteus, OpenAI, Gemini, or Vertex AI depending on configured default models.
- The `uv` binary must be installed on target hosts for the wrapper/documented CLI path; the wrapper is responsible for using `uv run` to create/sync the project `.venv` and Python dependencies automatically.
- `uv.lock` exists, so wrapper/default docs should prefer `--frozen`.
- Safe file behavior must continue to be governed by `resolve_safe_path` and `AUTOBYTEUS_AGENT_WORKSPACE`.
- No new third-party CLI dependency unless implementation discovers a compelling need and updates the design first.

## Assumptions

- The intended CLI target is only `autobyteus-image-audio`.
- Users and agents are comfortable invoking a repo wrapper command; future skills should document the wrapper command as the primary interface, not manual environment setup or underlying `uv` details.
- JSON-only default output is acceptable for the first CLI ticket.
- Current MCP behavior is correct and should be preserved.
- The stale broad ticket's image/audio-related requirement is superseded by this document.

## Risks / Open Questions

| Risk ID | Risk / Open Question | Mitigation / Proposed Resolution |
| --- | --- | --- |
| RISK-001 | Service extraction could accidentally change MCP schemas or result shapes. | Keep MCP decorators in `server.py`; move execution behind services; validate MCP tool list/schema and safe tool calls. |
| RISK-002 | Real generation requires credentials and may incur cost. | Use mocked clients for automated local tests; keep remote/provider tests optional/skipped unless env is configured. |
| RISK-003 | `list_*_models` may initialize Autobyteus internals with environment-dependent defaults. | Accept as current behavior; provide structured errors and mock tests. |
| RISK-004 | The current test suite cannot run without `.env.test`. | Fix conftest to load `.env.test` only if present; integration tests already contain skip helpers and should remain credential-gated. |
| RISK-005 | CLI JSON parsing for `generation_config` can be error-prone. | Validate JSON early, fail with usage error envelope, and document examples. |

## Requirement-To-Use-Case Coverage

| Requirement ID | Covered Use Cases |
| --- | --- |
| REQ-001 | UC-007 |
| REQ-002 | UC-001, UC-002, UC-003, UC-004, UC-005, UC-006 |
| REQ-003 | UC-001, UC-002, UC-003, UC-004, UC-005, UC-006 |
| REQ-004 | UC-001, UC-002, UC-003, UC-004, UC-005, UC-006 |
| REQ-005 | UC-001, UC-002, UC-003, UC-004, UC-005, UC-006 |
| REQ-006 | UC-001, UC-002, UC-003, UC-004, UC-005, UC-006 |
| REQ-007 | UC-001, UC-002, UC-003, UC-004, UC-005, UC-006 |
| REQ-008 | UC-003, UC-004, UC-005 |
| REQ-009 | UC-003, UC-004, UC-006 |
| REQ-010 | UC-003, UC-004, UC-005 |
| REQ-011 | UC-003, UC-004, UC-005, UC-006, UC-007 |
| REQ-012 | UC-003, UC-004, UC-005, UC-006, UC-007 |
| REQ-013 | UC-001, UC-002, UC-003, UC-004, UC-005, UC-006 |
| REQ-014 | UC-003, UC-004, UC-005, UC-006, UC-008 |
| REQ-015 | UC-001, UC-002, UC-003, UC-004, UC-005, UC-006 |
| REQ-016 | UC-007 |
| REQ-017 | UC-008 |
| REQ-018 | UC-001, UC-002, UC-003, UC-004, UC-005, UC-006, UC-007 |
| REQ-019 | UC-008 |
| REQ-020 | UC-001, UC-002, UC-003, UC-004, UC-005, UC-006 |
| REQ-021 | UC-005 |

## Acceptance-Criteria-To-Scenario Intent

| Acceptance Criteria ID | Scenario Intent |
| --- | --- |
| AC-001 | Proves stale wrong worktree was replaced by a fresh scoped worktree. |
| AC-002 | Proves the new ticket avoids the invalid workflow-state process. |
| AC-003 | Proves the CLI can be used by an agent from any current working directory. |
| AC-004 | Proves command discoverability and `uv` project execution. |
| AC-005 | Proves safe informational commands work or fail structurally. |
| AC-006 | Proves file-producing service behavior without paid/provider calls. |
| AC-007 | Proves CLI parsing/envelope behavior for core commands. |
| AC-008 | Proves MCP non-regression and hidden tool policy. |
| AC-009 | Proves local validation no longer depends on private `.env.test`. |
| AC-010 | Proves CLI docs are usable. |
| AC-011 | Proves MCP docs remain available. |
| AC-012 | Proves the scope remains the clean narrow ticket. |
| AC-013 | Proves the CLI is a polished command-line projection of MCP capabilities, not a raw MCP wrapper. |
| AC-014 | Proves multi-speaker generation settings are understandable and agent-friendly. |

## Approval Status

Approved by user clarification on 2026-05-05. User confirmed the narrowed requirement: keep MCP, add a simple skill-facing CLI, hide automatic `uv` environment setup inside the wrapper/script, and design the best intuitive command-line UX over the MCP capabilities rather than blindly copying raw MCP mechanics.
