# Design Spec

## Current-State Read

`autobyteus-image-audio` is currently an MCP-only Python project under `autobyteus-image-audio/` with its own `pyproject.toml`, `uv.lock`, and `autobyteus-image-audio-server = image_audio_mcp.server:main` console script. The recommended MCP launch path already uses `uv --directory <project> run ...`, so dependency isolation and first-run environment sync are healthy in MCP mode.

The current code path is concentrated in `autobyteus-image-audio/src/image_audio_mcp/server.py`:

- `main()` creates and runs the FastMCP server.
- `create_server()` constructs `FastMCP` and registers seven public tools as nested closures:
  - `health_check`
  - `list_audio_models`
  - `list_image_models`
  - `generate_image`
  - `edit_image`
  - `generate_speech`
  - `find_target_coordinates`
- Those closures own both MCP transport wiring and business execution: workspace/path resolution, default model resolution, Autobyteus client creation, provider calls, output download/write, marker detection, and cleanup.
- Helper logic (`_get_workspace_root`, `_resolve_output_path`, `_normalize_media_source`, coordinate helpers, default model helpers) is module-level and can be moved/reused, but the actual public capability functions are not importable outside the MCP factory.

Current coupling/fragmentation problem: adding a CLI directly against this shape would either duplicate tool bodies in a new CLI file or route CLI calls through an MCP subprocess/client boundary. Both are wrong for the target skill-facing CLI. The needed authoritative boundary is an importable image/audio service layer used by both public surfaces.

Current validation constraint: local tests are not clean-checkout friendly because `tests/conftest.py` raises if `.env.test` is missing. That blocks local/mock validation before remote integration skip logic can run.

## Intended Change

Add a simple command-line surface for `autobyteus-image-audio` while preserving MCP mode unchanged. The CLI exposes the same practical capabilities as the MCP tools, but it should be designed as a polished command-line UX rather than a raw MCP schema/JSON-RPC wrapper. MCP parity defines capability coverage; CLI ergonomics define the command shape.

The future consumer is an agent skill. The skill should document commands like:

```bash
/path/to/repo/cli/autobyteus-image-audio health-check
/path/to/repo/cli/autobyteus-image-audio generate-speech --prompt "Hello" --output-file-path speech.wav
```

The skill and invoking agent should not need to understand, run, or document environment setup steps such as `uv sync`, `.venv` activation, or dependency installation. The root wrapper owns that setup internally by invoking `uv --directory <repo>/autobyteus-image-audio run --frozen autobyteus-image-audio ...`; `uv run` creates/syncs the project environment on first use. The project CLI maps MCP-style tool inputs into idiomatic CLI subcommands/options where that is the clearest UX: readable command names, named flags, repeatable list flags, and dynamic per-call `--config key=value` settings. It should not blindly copy raw MCP schema shape when a better CLI shape is available.

Implement the CLI as a thin parser/JSON-envelope facade over shared service functions. Refactor `server.py` so MCP tools also delegate to the same service functions.

CLI UX design rules:

- Provide stable, intuitive command coverage for every public MCP capability. The baseline command set is `health-check`, `list-image-models`, `list-audio-models`, `generate-image`, `edit-image`, `generate-speech`, and `find-target-coordinates`; implementation may refine grouping or aliases if that is clearly more usable and still documented.
- Prefer kebab-case command and option names for CLI readability; use MCP snake_case only inside Python/service boundaries.
- Required scalar inputs become required named flags, not positional guessing; for example `--prompt`, `--output-file-path`, `--image`, `--target`.
- List inputs become repeatable singular flags; for example MCP `input_images` becomes repeated `--input-image`.
- Generation settings should be dynamic per call through repeatable `--config key=value` options. Nested keys use dot notation, for example `--config image_config.aspect_ratio=16:9`. Raw JSON may exist as an advanced escape hatch, but config files are not the preferred primary UX for per-call generation settings.
- Do not provide a generic `call-tool --name ... --arguments ...` as the primary UX. If such a debug escape hatch is ever added, it must be out of scope for normal skill usage and must not replace the ergonomic commands.
- For multi-speaker speech, use repeated paired flags `--speaker NAME --voice VOICE`. The CLI pairs them by order, validates matching counts, and builds `generation_config.speaker_mapping`. This is preferred over comma syntax or `Speaker=Voice` because the command reads naturally.
- `--help` should include practical examples that a future skill can copy or summarize.


## Task Design Health Assessment (Mandatory)

- Change posture (`Feature`/`Bug Fix`/`Behavior Change`/`Refactor`/`Cleanup`/`Performance`/`Larger Requirement`): Feature
- Current design issue found (`Yes`/`No`/`Unclear`): Yes
- Root cause classification (`Local Implementation Defect`/`Missing Invariant`/`Boundary Or Ownership Issue`/`Duplicated Policy Or Coordination`/`File Placement Or Responsibility Drift`/`Shared Structure Looseness`/`Legacy Or Compatibility Pressure`/`No Design Issue Found`/`Unclear`): Boundary Or Ownership Issue
- Refactor needed now (`Yes`/`No`/`Deferred`/`Unclear`): Yes
- Evidence: `server.py:create_server()` currently nests capability execution inside MCP decorators. A CLI cannot import those closures as a clean capability owner. The stale broad ticket/workflow-state approach was removed; this ticket must use a new narrow boundary.
- Design response: Introduce `image_audio_mcp.services` as the authoritative capability owner. Keep `image_audio_mcp.server` and `image_audio_mcp.cli` as thin public facades. Add a root wrapper that owns automatic `uv` project execution. Shape `image_audio_mcp.cli` as an ergonomic task-oriented CLI over MCP capabilities rather than a raw MCP wrapper.
- Refactor rationale: Service extraction prevents duplicate provider/path/client logic and keeps MCP and CLI behavior identical by construction.
- Intentional deferrals and residual risk, if any: Real provider generation E2E remains optional/credential-gated; local validation uses mocked providers. This leaves residual risk in provider-specific network behavior but does not weaken CLI/service architecture.

## Terminology

- `Subsystem` / `capability area`: a larger functional area that owns a broader category of work and may contain multiple files plus optional module groupings.
- `Module`: an optional intermediate grouping inside a subsystem when the codebase benefits from it. Do not use `module` as a synonym for one file or as the default ownership term.
- `Folder` / `directory`: a physical grouping used to organize files and any optional module groupings.
- `File`: one concrete source file and the primary unit where one concrete concern should land.

## Design Reading Order

1. data-flow spine
2. subsystem / capability-area allocation
3. draft file responsibilities -> extract reusable owned structures -> finalize file responsibilities
4. folder/path mapping

## Legacy Removal Policy (Mandatory)

- Policy: `No backward compatibility; remove legacy code paths.`
- Required action: do not revive the stale `mcp-cli-tools` workflow-state process. Do not add host-specific generated absolute-path wrappers from the stale ticket. Remove/decommission duplicated business logic from `server.py` closures by extracting it into services.
- Treat removal as first-class design work: dead hidden VLM helper code inside `create_server()` should not be preserved unless implementation proves an active reference. Hidden public grounding tools must remain unexposed.
- Decision rule: the design must not depend on an MCP-client subprocess wrapper only to avoid refactoring, nor on duplicated CLI/MCP tool bodies, nor on a generic raw `call-tool` UX as the primary command-line interface.

Keeping the existing MCP server is not treated as legacy compatibility; it is an explicit product requirement and remains a supported public surface.

## Data-Flow Spine Inventory

| Spine ID | Scope (`Primary End-to-End`/`Return-Event`/`Bounded Local`) | Start | End | Governing Owner | Why It Matters |
| --- | --- | --- | --- | --- | --- |
| DS-001 | Primary End-to-End | Agent skill/user shell command | Autobyteus provider call and output JSON/file | Root CLI wrapper + project CLI + services | Main new behavior: skill-facing command hides environment setup and invokes image/audio capability. |
| DS-002 | Primary End-to-End | MCP client tool call | Autobyteus provider call and MCP structured result/file | FastMCP facade + services | Ensures existing MCP mode stays supported while sharing execution logic. |
| DS-003 | Return-Event | Service result or exception | CLI JSON stdout/stderr + exit code | CLI facade | Defines automation-safe agent output. |
| DS-004 | Bounded Local | Wrapper process start | Project CLI process start in `.venv` | Root wrapper | Hides `uv` environment creation/sync from the agent. |
| DS-005 | Bounded Local | Service starts provider operation | Provider client cleanup | Services | Preserves stateless client lifecycle and cleanup invariant. |
| DS-006 | Bounded Local | Coordinate service receives target image | Pixel/normalized coordinate result | Coordinate service function | Captures marker-edit, marker-detection, optional fallback flow. |

## Primary Execution Spine(s)

CLI spine:

`Agent Skill / Shell -> cli/autobyteus-image-audio wrapper -> uv project execution -> image_audio_mcp.cli -> image_audio_mcp.services -> Autobyteus clients / filesystem -> CLI JSON envelope`

MCP spine:

`MCP Client -> image_audio_mcp.server FastMCP tool facade -> image_audio_mcp.services -> Autobyteus clients / filesystem -> MCP structured result`

## Spine Narratives (Mandatory)

| Spine ID | Short Narrative | Main Domain Subject Nodes | Governing Owner | Key Off-Spine Concerns |
| --- | --- | --- | --- | --- |
| DS-001 | A skill/user invokes one simple wrapper command. The wrapper resolves the project path and runs the project CLI through `uv run --frozen`, letting `uv` create/sync `.venv`. The project CLI parses ergonomic CLI arguments and delegates capability execution to services. Services perform model/path/provider work and return a result that the CLI wraps in JSON. | Skill command, root wrapper, uv project execution, project CLI, services, provider/filesystem | Root wrapper for setup; CLI for command contract; services for capability execution | JSON envelope, usage errors, `uv` missing/setup errors, docs simplicity |
| DS-002 | An existing MCP client launches the server and invokes tools. FastMCP decorators keep the public MCP schema, but their bodies delegate to the same services as the CLI. | MCP client, FastMCP facade, services, provider/filesystem | FastMCP facade for MCP schema; services for execution | MCP schema preservation, hidden tool exclusion |
| DS-003 | A service return becomes `{"ok": true, "command": ..., "result": ...}`. A service/parse/setup failure becomes `{"ok": false, "command": ..., "error_type": ..., "error_message": ...}` and non-zero exit. | Service result, CLI response formatter, stdout/exit code | CLI facade | Error classification, stderr diagnostics |
| DS-004 | The wrapper checks/uses `uv`, resolves repo/project path relative to itself, and invokes `uv --directory <project> run --frozen autobyteus-image-audio ...`. | Wrapper, uv, project console script | Root wrapper | Missing `uv`, first-run sync, path independence |
| DS-005 | Each service call creates the required image/audio/LLM client, awaits the provider call, downloads/writes output where needed, and calls cleanup in `finally`. | Service operation, provider client, cleanup | Services | Credentials/model env, output IO |
| DS-006 | Coordinate finding normalizes the image, asks the edit model to mark the target, downloads marked image, detects magenta marker center, maps coordinates to original size, and optionally uses LLM fallback when color detection fails. | Coordinate service, edit image client, marker detector, optional LLM fallback | Services | Temporary marked output path, image-size detection, fallback model |

## Spine Actors / Main-Line Nodes

- Agent skill / shell user
- Root wrapper `cli/autobyteus-image-audio`
- `uv` project executor
- Project CLI `image_audio_mcp.cli`
- MCP facade `image_audio_mcp.server`
- Shared services `image_audio_mcp.services`
- Autobyteus multimedia/LLM clients
- Filesystem output paths

## Ownership Map

| Main-Line Node | Owns |
| --- | --- |
| Agent skill / shell user | Command intent and arguments only; no environment setup lifecycle. |
| Root wrapper | Repo/project path resolution, `uv` binary preflight, automatic project environment execution, hiding setup details from callers. |
| `uv` project executor | Project `.venv` creation/sync, locked dependency execution, Python interpreter/dependency environment. |
| Project CLI | Argument parsing, command naming, JSON success/failure envelope, exit codes, user-facing help. It does not own provider/path/client logic. |
| MCP facade | FastMCP server creation, public MCP tool signatures/schemas, MCP structured output bridge. It does not own capability execution. |
| Services | Default model resolution, workspace/path/media normalization, provider client lifecycle, generation/edit/speech/model-list/coordinate business execution, result payload shape shared by CLI and MCP. |
| Autobyteus clients | Provider-specific API/model execution. |
| Filesystem output | Safe write location constrained by `resolve_safe_path`. |

## Thin Entry Facades / Public Wrappers (If Applicable)

| Facade / Entry Wrapper | Governing Owner Behind It | Why It Exists | Must Not Secretly Own |
| --- | --- | --- | --- |
| `cli/autobyteus-image-audio` | `uv` project execution + project CLI | Skill-facing command and automatic environment setup | Provider calls, path normalization, business result shaping beyond setup error handling |
| `image_audio_mcp.cli` | `image_audio_mcp.services` | Terminal command contract and JSON automation surface | Autobyteus client lifecycle or duplicated MCP tool bodies |
| `image_audio_mcp.server:create_server()` | `image_audio_mcp.services` | Existing MCP public surface and schemas | Business execution, provider policy, duplicated helper logic |

## Removal / Decommission Plan (Mandatory)

| Item To Remove / Decommission | Why It Becomes Unnecessary | Replaced By Which Owner / File / Structure | Scope (`In This Change`/`Follow-up`) | Notes |
| --- | --- | --- | --- | --- |
| Stale `mcp-cli-tools` ticket/workflow-state approach | User rejected it; it was broad and process-heavy | Fresh `image-audio-mcp-cli` artifacts | In This Change | Already removed from old worktree/branch during bootstrap. Do not recreate `workflow-state.md`. |
| Business execution inside nested MCP closures | Would duplicate or trap behavior behind MCP transport | `image_audio_mcp.services` | In This Change | MCP closures become thin delegates. |
| Host-specific generated absolute-path wrapper concept | Too much setup detail for skill/users; stale broad-ticket artifact pattern | Path-independent repo wrapper | In This Change | Wrapper resolves repo path relative to itself. |
| Unreferenced nested `_find_target_coordinates_vlm_impl` if still unused after extraction | Hidden/public grounding tools must remain unexposed; dead code confuses ownership | Coordinate service fallback logic actually used by `find_target_coordinates` | In This Change | If implementation finds a real active use, fold it under service ownership instead of leaving it nested in `server.py`. |

## Return Or Event Spine(s) (If Applicable)

CLI return spine:

`Service result/exception -> CLI response formatter -> JSON stdout -> process exit code -> skill/agent parser`

MCP return spine:

`Service result/exception -> FastMCP tool return/error -> MCP client structured content/error`

## Bounded Local / Internal Spines (If Applicable)

- Parent owner: root wrapper
  `wrapper start -> resolve project dir -> check uv -> uv --directory project run --frozen project CLI -> propagate exit`
  Matters because the agent skill sees only the wrapper command; environment setup is internal.

- Parent owner: services
  `create provider client -> await provider call -> download/write output -> cleanup in finally -> return payload`
  Matters because MCP and CLI must preserve stateless call behavior.

- Parent owner: coordinate service
  `normalize source image -> infer original size -> edit marker image -> download marked image -> detect magenta center -> map to original coordinates -> return pixel/normalized coordinates`
  Matters because this flow is the most complex tool and must not be duplicated in CLI.

## Off-Spine Concerns Around The Spine

| Off-Spine Concern | Related Spine ID(s) | Serves Which Owner | Responsibility | Why It Exists | Risk If Misplaced On Main Line |
| --- | --- | --- | --- | --- | --- |
| JSON envelope formatting | DS-001, DS-003 | Project CLI | Standard success/failure stdout and exit codes | Agent automation needs stable parseable output | Services become CLI-specific or MCP result shapes get polluted. |
| Argument parsing/help | DS-001 | Project CLI | Parse ergonomic subcommands/options, validate JSON strings, show user-friendly examples | Keeps skill docs simple and avoids raw MCP mechanics | Business services become aware of shell syntax, or users must pass raw MCP JSON. |
| `uv` preflight/setup failure handling | DS-004 | Root wrapper | Hide setup mechanics and fail clearly if `uv` is absent or setup fails before CLI starts | Agent should not run setup manually | Skill docs expose too much setup detail or failures become opaque. |
| Workspace/path/media normalization | DS-001, DS-002, DS-005 | Services | Reuse existing `resolve_safe_path` and URL/data URI/local file behavior | Keeps MCP and CLI behavior identical | CLI and MCP diverge on file safety. |
| Default model/env resolution | DS-001, DS-002, DS-005 | Services | Resolve default image/edit/speech/grounding models from env | Current MCP behavior depends on env defaults | CLI starts accepting conflicting model policy. |
| Provider client cleanup | DS-005 | Services | Always cleanup clients after call | Prevents leaks and preserves stateless calls | Cleanup responsibility gets scattered. |
| Optional remote/provider tests | DS-001, DS-002 | Validation | Skip when credentials absent | Avoids mandatory paid/external calls | Local validation becomes unreliable. |

## Existing Capability / Subsystem Reuse Check

| Need / Concern | Existing Capability Area / Subsystem | Decision (`Reuse`/`Extend`/`Create New`) | Why | If New, Why Existing Areas Are Not Right |
| --- | --- | --- | --- | --- |
| Provider image/audio execution | Existing Autobyteus multimedia clients | Reuse | Current MCP already depends on these clients and behavior should not change | N/A |
| Safe path resolution | `autobyteus.utils.file_utils.resolve_safe_path` | Reuse | Current MCP safety invariant | N/A |
| File download/write | `autobyteus.utils.download_utils.download_file_from_url` | Reuse | Current MCP output IO invariant | N/A |
| MCP transport | `image_audio_mcp.server` | Extend/refactor | Keep existing MCP facade but make it thin | N/A |
| CLI surface | None in project | Create New | No current terminal command surface exists | Existing server is transport-specific and should not parse shell args. |
| Shared capability owner | None as importable service boundary | Create New | Current closures are not reusable | Existing `server.py` owns MCP transport; keeping services there would preserve mixed ownership. |
| Root skill-facing wrapper | None in repo | Create New | Needed to hide `uv` setup and allow invocation from any cwd | Project console script alone only works after entering env or invoking `uv` manually. |

## Subsystem / Capability-Area Allocation

| Subsystem / Capability Area | Owns Which Concerns | Related Spine ID(s) | Governing Owner(s) Served | Decision (`Reuse`/`Extend`/`Create New`) | Notes |
| --- | --- | --- | --- | --- | --- |
| Project services | Capability execution, env/model/path/media normalization, provider lifecycle, result payloads | DS-001, DS-002, DS-005, DS-006 | CLI and MCP facades | Create New | `image_audio_mcp.services` |
| MCP facade | FastMCP server, tool signatures, structured MCP bridge | DS-002 | MCP clients | Extend/refactor | Keep public signatures stable. |
| Project CLI facade | Argparse commands, intuitive option design, JSON envelopes, exit codes | DS-001, DS-003 | Agent skills/users | Create New | `image_audio_mcp.cli` |
| Root wrapper | `uv` execution and hidden setup | DS-001, DS-004 | Agent skills/users | Create New | `cli/autobyteus-image-audio` |
| Tests | Local/mocked validation and optional remote integration | All | Implementation/review | Extend | Fix `.env.test` blocker. |
| Docs | MCP and CLI usage docs | DS-001, DS-002 | Users/skills | Extend | Main CLI docs should be simple. |

## Draft File Responsibility Mapping

| Candidate File | Owning Subsystem / Capability Area | Owner / Boundary | Concrete Concern | Why This Is One File | Reuses Shared Structure? |
| --- | --- | --- | --- | --- | --- |
| `src/image_audio_mcp/services.py` | Project services | Capability service boundary | Async functions for health/model lists/generate/edit/speech/coordinates plus helper functions currently in `server.py` | One cohesive owner for image/audio MCP capability execution | N/A initially; may use small dataclasses if needed |
| `src/image_audio_mcp/cli.py` | Project CLI facade | CLI command boundary | `argparse` parser, intuitive CLI option mapping, command dispatch, JSON envelope, exit codes | CLI concern is separate from services and MCP | Calls services |
| `src/image_audio_mcp/server.py` | MCP facade | MCP transport boundary | FastMCP server config/tool signatures/main; delegates to services | Keeps MCP schema public surface in one file | Calls services |
| `cli/autobyteus-image-audio` | Root wrapper | Skill-facing wrapper | Resolve repo/project path, check `uv`, call `uv --directory ... run --frozen autobyteus-image-audio` | Shell wrapper owns setup hiding only | Calls project CLI through `uv` |
| `tests/test_services_local.py` | Tests | Service validation | Mock providers and validate service result shapes/path behavior | Keeps service tests independent of MCP/CLI | N/A |
| `tests/test_cli_local.py` | Tests | CLI validation | Validate parser/JSON envelope via monkeypatched services or local mocks | CLI tests should not require provider creds | N/A |
| `tests/test_server_local.py` | Tests | MCP validation | Existing compatibility tests; update imports for moved helpers if needed | Existing file already owns MCP local tests | Calls MCP facade/services indirectly |
| `tests/conftest.py` | Tests | Test bootstrap | Optional `.env.test` loading | Must stop blocking clean local tests | N/A |
| `README.md` / `DESIGN.md` | Docs | User/design docs | CLI usage and architecture updates | Existing docs for this project | N/A |
| `pyproject.toml` / `uv.lock` | Packaging | Project package metadata | Add console script; update lock if needed | Existing project metadata owner | N/A |

## Reusable Owned Structures Check

| Repeated Structure / Logic | Candidate Shared File | Owning Subsystem | Why Shared | Redundant Attributes Removed? (`Yes`/`No`) | Overlapping Representations Removed? (`Yes`/`No`) | Must Not Become |
| --- | --- | --- | --- | --- | --- | --- |
| Tool execution payload shapes | `services.py` function return dicts | Project services | MCP and CLI should share the same result payloads | Yes | Yes | A generic kitchen-sink DTO for every command |
| Path/media normalization helpers | `services.py` | Project services | Both generate/edit/coordinate need same path policy | Yes | Yes | CLI-only path handling |
| CLI response envelope | `cli.py` | Project CLI facade | All commands need consistent automation output | Yes | Yes | A service-layer return shape |
| JSON config parsing | `cli.py` | Project CLI facade | Only shell input concern | Yes | Yes | Provider/business validation |

## Shared Structure / Data Model Tightness Check

| Shared Structure / Type / Schema | One Clear Meaning Per Field? (`Yes`/`No`) | Redundant Attributes Removed? (`Yes`/`No`) | Parallel / Overlapping Representation Risk (`Low`/`Medium`/`High`) | Corrective Action |
| --- | --- | --- | --- | --- |
| Service result dicts | Yes | Yes | Low | Keep existing MCP result keys (`file_path`, `model`, `models`, coordinate fields). CLI wraps them under `result`. |
| CLI envelope | Yes | Yes | Low | `ok`, `command`, `result` for success; `ok`, `command`, `error_type`, `error_message` for failure. |
| Generation config JSON | Yes | Yes | Medium | Parse once in CLI to a dict; pass through unchanged to services/provider. |

## Final File Responsibility Mapping

| File | Owning Subsystem / Capability Area | Owner / Boundary | Concrete Concern | Why This Is One File | Reuses Shared Structure? |
| --- | --- | --- | --- | --- | --- |
| `autobyteus-image-audio/src/image_audio_mcp/services.py` | Project services | Authoritative capability owner | Async service functions: `health_check`, `list_audio_models`, `list_image_models`, `generate_image`, `edit_image`, `generate_speech`, `find_target_coordinates`; helper functions; client cleanup | Centralizes behavior shared by MCP and CLI | N/A |
| `autobyteus-image-audio/src/image_audio_mcp/server.py` | MCP facade | Thin MCP public boundary | `ServerConfig`, `create_server`, FastMCP decorators/signatures/descriptions, `main` | Keeps MCP schema stable and transport-specific | Calls services |
| `autobyteus-image-audio/src/image_audio_mcp/cli.py` | CLI facade | Thin CLI public boundary | Parser, intuitive subcommands/options, JSON config parsing, async dispatch, envelope/exit | Keeps CLI syntax/output separate from capability execution | Calls services |
| `cli/autobyteus-image-audio` | Root wrapper | Skill-facing setup boundary | Path-independent wrapper and internal `uv run --frozen` execution | Makes skill docs simple and setup automatic | Calls project CLI through `uv` |
| `autobyteus-image-audio/tests/conftest.py` | Tests | Test bootstrap | Load `.env.test` only if present | Enables clean local tests | N/A |
| `autobyteus-image-audio/tests/test_services_local.py` | Tests | Service behavior validation | Mocked service-level tests | Catches shared behavior regressions | N/A |
| `autobyteus-image-audio/tests/test_cli_local.py` | Tests | CLI validation | Command parsing/envelope tests | Catches skill-facing command regressions | Calls services/mocks |
| `autobyteus-image-audio/tests/test_server_local.py` | Tests | MCP compatibility validation | Existing + adjusted tests for MCP tool list/schema/safe calls | Ensures MCP unchanged | Calls server/services |
| `autobyteus-image-audio/README.md` | Docs | User docs | Simple CLI usage first; MCP usage preserved; setup note concise | Future skill can reference usage | N/A |
| `autobyteus-image-audio/DESIGN.md` | Docs | Project design docs | Updated dual-surface/service-boundary runtime flow | Durable implementation rationale | N/A |
| `autobyteus-image-audio/pyproject.toml` | Packaging | Script metadata | Add `autobyteus-image-audio = image_audio_mcp.cli:main` | Existing project package owner | N/A |
| `autobyteus-image-audio/uv.lock` | Packaging | Locked environment | Update if script metadata changes lock content | Ensures `--frozen` works | N/A |

## Ownership Boundaries

The authoritative business boundary is `image_audio_mcp.services`. Upstream surfaces must depend on services, not on each other or on provider internals.

- CLI must not instantiate provider clients directly.
- MCP tool closures must not contain provider/path/client logic beyond adapting signatures to service calls.
- The root wrapper must not parse image/audio command semantics; it only owns setup/execution.
- Services may depend on Autobyteus factories/utilities and filesystem/path utilities.
- Tests may monkeypatch service dependencies, but production code should not bypass services.

## Boundary Encapsulation Map

| Authoritative Boundary | Internal Owned Mechanism(s) It Encapsulates | Upstream Callers That Must Use The Boundary | Forbidden Bypass Shape | If Boundary API Is Too Thin, Fix By |
| --- | --- | --- | --- | --- |
| `image_audio_mcp.services` | Autobyteus client factories, path/media helpers, model defaults, cleanup, downloads | `server.py`, `cli.py` | CLI calls `ImageClientFactory` directly while MCP calls services | Add/adjust service function parameters |
| `image_audio_mcp.cli` | Argparse, JSON config parsing, envelope/exit code | Project console script invoked by wrapper/uv | Wrapper duplicates subcommand parsing | Add CLI options/helpers |
| `cli/autobyteus-image-audio` | Repo path resolution, uv preflight/execution | Agent skills/users | Skill tells agents to run `uv sync` then call `.venv/bin/...` | Strengthen wrapper/docs |
| `image_audio_mcp.server` | FastMCP registration and schema metadata | MCP launchers/clients | CLI imports FastMCP internals or starts MCP client subprocess for normal calls | Expose/extend services instead |

## Dependency Rules

Allowed:

- `cli/autobyteus-image-audio` -> shell `uv` -> project console script.
- `image_audio_mcp.cli` -> `image_audio_mcp.services`.
- `image_audio_mcp.cli` may translate command/option names but must not translate provider behavior.
- `image_audio_mcp.server` -> `image_audio_mcp.services`.
- `image_audio_mcp.services` -> Autobyteus multimedia/LLM factories and Autobyteus utility functions.
- Tests -> CLI/server/services with monkeypatching.

Forbidden:

- CLI -> FastMCP server internals for normal capability execution.
- MCP server -> CLI parser/envelope.
- CLI and MCP each owning separate copies of provider/path/client logic.
- Skill docs -> manual `uv sync`, `.venv` activation, direct `.venv/bin/python`, or raw MCP `call-tool` JSON as the primary path.
- Host-specific committed absolute-path wrappers.
- Recreating `workflow-state.md` or stale broad ticket stage-control artifacts.

## Interface Boundary Mapping

| Interface / API / Query / Command / Method | Subject Owned | Responsibility | Accepted Identity Shape(s) | Notes |
| --- | --- | --- | --- | --- |
| `services.health_check()` | Runtime status | Return status + resolved default models | None | Same payload as MCP tool. |
| `services.list_audio_models()` | Audio model catalog | Return audio model schemas/defaults | None | Initializes `AudioClientFactory` as today. |
| `services.list_image_models()` | Image model catalog | Return image model schemas/defaults | None | Initializes `ImageClientFactory` as today. |
| `services.generate_image(prompt, output_file_path, input_images, generation_config)` | Image generation | Generate/download output image | Prompt string; path string; optional list of URL/data/local paths; config dict | Uses env default model. |
| `services.edit_image(prompt, output_file_path, input_images, mask_image, generation_config)` | Image editing | Edit/download output image | Prompt/path/media strings/config dict | Uses env default edit model. |
| `services.generate_speech(prompt, output_file_path, generation_config)` | Speech generation | Generate/download audio | Prompt/path/config dict | Uses env default speech model. |
| `services.find_target_coordinates(image, target, marked_image_output_path, grounding_model_identifier)` | Coordinate finding | Return marker-derived coordinates | Image source string; target string; optional output path/model id | Existing public MCP option retained. |
| CLI `health-check` | Runtime status | Print envelope | No args | Skill-friendly. |
| CLI `list-image-models` / `list-audio-models` | Model catalogs | Print envelope | No args | May fail structurally if provider initialization fails. |
| CLI `generate-image` | Image generation | Parse ergonomic shell args/config then call service | `--prompt`, `--output-file-path`, repeated `--input-image`, repeated `--config key=value` | JSON stdout. |
| CLI `edit-image` | Image editing | Parse shell args/config then call service | `--prompt`, `--output-file-path`, repeated `--input-image`, optional `--mask-image`, repeated `--config key=value` | JSON stdout. |
| CLI `generate-speech` | Speech generation | Parse shell args/config then call service | `--prompt`, `--output-file-path`, repeated `--config key=value`, optional repeated paired `--speaker NAME --voice VOICE` for multi-speaker mapping | JSON stdout. |
| CLI `find-target-coordinates` | Coordinate finding | Parse shell args then call service | `--image`, `--target`, optional `--marked-image-output-path`, optional `--grounding-model-identifier` | JSON stdout. |

## Interface Boundary Check

| Interface | Responsibility Is Singular? (`Yes`/`No`) | Identity Shape Is Explicit? (`Yes`/`No`) | Ambiguous Selector Risk (`Low`/`Medium`/`High`) | Corrective Action |
| --- | --- | --- | --- | --- |
| Service functions | Yes | Yes | Low | Keep one function per public capability. |
| CLI subcommands | Yes | Yes | Low | Avoid one generic `call-tool` command as the primary UX. |
| Root wrapper | Yes | Yes | Low | It only launches project CLI through uv. |
| MCP facade | Yes | Yes | Low | Keep public MCP tools split by capability. |

## Main Domain Subject Naming Check

| Node / Subject | Current / Proposed Name | Name Is Natural And Self-Descriptive? (`Yes`/`No`) | Naming Drift Risk | Corrective Action |
| --- | --- | --- | --- | --- |
| Root wrapper | `cli/autobyteus-image-audio` | Yes | Low | Matches project identity. |
| Project CLI | `image_audio_mcp.cli` | Yes | Low | Standard package CLI file. |
| Capability services | `image_audio_mcp.services` | Yes | Medium | Keep service file concrete; do not turn it into unrelated helpers. |
| MCP facade | `image_audio_mcp.server` | Yes | Low | Existing name. |

## Applied Patterns (If Any)

- Thin facade: `server.py` and `cli.py` are public entry facades over services.
- Service extraction: `services.py` owns reusable capability execution.
- Shell wrapper: root `cli/autobyteus-image-audio` owns environment/project execution so skills remain simple.
- Factory usage: services continue to use Autobyteus `ImageClientFactory`, `AudioClientFactory`, and `LLMFactory` as provider creation boundaries.

## Target Subsystem / Folder / File Mapping

| Path | Kind (`Folder`/`Module`/`File`) | Owner / Boundary | Responsibility | Why It Belongs Here | Must Not Contain |
| --- | --- | --- | --- | --- | --- |
| `cli/` | Folder | Root wrappers | Skill-facing repo wrapper scripts | Repo-level path makes wrapper stable and cwd-independent | Python business logic |
| `cli/autobyteus-image-audio` | File | Root wrapper | Internal uv project execution | User/skill invokes this simple command | Provider/path/client logic |
| `autobyteus-image-audio/src/image_audio_mcp/services.py` | File | Services | Shared capability execution | Under project package with current server | CLI parser or FastMCP decorators |
| `autobyteus-image-audio/src/image_audio_mcp/cli.py` | File | CLI facade | Commands/envelopes | Project CLI belongs with package code and console script | Provider client lifecycle |
| `autobyteus-image-audio/src/image_audio_mcp/server.py` | File | MCP facade | FastMCP server/tool registration | Existing MCP surface | Duplicated service bodies |
| `autobyteus-image-audio/tests/` | Folder | Tests | Local, CLI, MCP, optional integration validation | Existing test location | Required private env files for local tests |
| `autobyteus-image-audio/README.md` | File | User docs | Simple CLI usage + MCP docs | Existing user entry doc | Long environment setup as main CLI flow |
| `autobyteus-image-audio/DESIGN.md` | File | Design docs | Dual-surface runtime architecture | Existing design doc | Stale broad multi-MCP scope |
| `tickets/in-progress/image-audio-mcp-cli/` | Folder | Ticket artifacts | Requirements, investigation, design | Fresh scoped ticket | `workflow-state.md` |

## Folder Boundary Check

| Path / Folder | Intended Structural Depth (`Transport`/`Main-Line Domain-Control`/`Persistence-Provider`/`Off-Spine Concern`/`Mixed Justified`) | Ownership Boundary Is Clear? (`Yes`/`No`) | Mixed-Layer Or Over-Split Risk (`Low`/`Medium`/`High`) | Justification / Corrective Action |
| --- | --- | --- | --- | --- |
| `autobyteus-image-audio/src/image_audio_mcp/` | Mixed Justified | Yes | Low | Small project; separate files make boundaries clear without extra folders. |
| `cli/` | Transport/setup wrapper | Yes | Low | Repo-level wrappers are distinct from Python package code. |
| `tests/` | Off-Spine Concern | Yes | Low | Existing tests folder; split by service/CLI/server files. |

## Concrete Examples / Shape Guidance (Mandatory When Needed)

| Topic | Good Example | Bad / Avoided Shape | Why The Example Matters |
| --- | --- | --- | --- |
| Skill-facing usage | `cli/autobyteus-image-audio generate-image --prompt "..." --output-file-path out.png` | Skill says: `cd autobyteus-image-audio && uv sync && source .venv/bin/activate && python ...` | The user explicitly wants setup hidden inside the CLI/script. |
| CLI option design | `edit-image --prompt "..." --input-image a.png --input-image b.png --mask-image mask.png --output-file-path out.png --config image_config.aspect_ratio=16:9` | `call-tool --name edit_image --arguments '{"prompt":...,"input_images":[...]}'` as normal usage | A good CLI should expose capabilities through command-line-native arguments; MCP schema shape is not the UX authority. |
| Multi-speaker speech | `generate-speech --prompt $'Joe: Hello.\nJane: Hi.' --output-file-path dialog.wav --config mode=multi-speaker --speaker Joe --voice Kore --speaker Jane --voice Puck` | `--speaker Joe=Kore`, comma syntax, or raw JSON as normal usage | Paired `--speaker`/`--voice` flags make the semantic relation explicit and readable for agents. |
| Wrapper internals | Wrapper internally executes `uv --directory "$PROJECT_DIR" run --frozen autobyteus-image-audio "$@"` | Committed wrapper with host-specific absolute path | Path-independent but still auto-provisions. |
| Shared execution | MCP `generate_image` and CLI `generate-image` both call `services.generate_image(...)` | CLI copies the old FastMCP closure body | Prevents drift between MCP and CLI. |
| Public surfaces | `server.py` owns MCP schema; `cli.py` owns JSON CLI; `services.py` owns behavior | `server.py` parses CLI args or `cli.py` imports FastMCP internals | Preserves authoritative boundaries. |

## Backward-Compatibility Rejection Log (Mandatory)

| Candidate Compatibility Mechanism | Why It Was Considered | Rejection Decision (`Rejected`/`N/A`) | Clean-Cut Replacement / Removal Plan |
| --- | --- | --- | --- |
| MCP-client subprocess wrapper for CLI | Would avoid service extraction | Rejected | Direct CLI over shared services. |
| Generic raw `call-tool` CLI as primary interface | Mirrors MCP exactly | Rejected | Intuitive task-oriented subcommands/options that cover MCP capabilities. |
| Duplicate CLI implementation of MCP tool bodies | Quick to implement | Rejected | Extract services and delegate from both surfaces. |
| Host-specific generated absolute-path wrappers | Came from stale broad ticket | Rejected | Path-independent root wrapper resolves project path relative to itself. |
| Manual `uv sync`/activation in skill docs | Common Python setup style | Rejected | Wrapper internally calls `uv run`; docs show simple CLI only. |
| Recreate `workflow-state.md` | Stale ticket process used it | Rejected | Use only requirements/investigation/design artifacts for this ticket. |

## Derived Layering (If Useful)

- External invocation layer: skill/user shell and MCP clients.
- Entry facade layer: root wrapper, project CLI, MCP server.
- Capability layer: `image_audio_mcp.services`.
- Provider/utilities layer: Autobyteus factories/utilities, filesystem.

The dependency direction is downward only. Entry facades depend on services; services do not depend on entry facades.

## Migration / Refactor Sequence

1. Add `services.py` and move reusable helpers/default resolvers/client cleanup and public capability execution out of `server.py` into services.
2. Update `server.py` so FastMCP decorators keep the existing public signatures/descriptions and delegate to services.
3. Remove or fold any unreferenced nested hidden VLM helper into services only if it is actually used by coordinate fallback; otherwise decommission it.
4. Add `cli.py` with stdlib `argparse`, intuitive command/option design, repeatable `--config key=value` parsing with dot notation, paired `--speaker`/`--voice` validation for multi-speaker speech, optional advanced JSON config parsing if kept, async command dispatch, envelopes, examples/help, and exit codes.
5. Add `autobyteus-image-audio` project console script in `pyproject.toml`; update `uv.lock` if required so `--frozen` works.
6. Add root `cli/autobyteus-image-audio` wrapper that resolves project dir relative to itself, checks `uv`, and internally invokes `uv --directory ... run --frozen autobyteus-image-audio "$@"`.
7. Fix `tests/conftest.py` to make `.env.test` optional for local tests.
8. Add local/mocked service and CLI tests; update MCP tests if helper imports move.
9. Validate:
   - `uv run --frozen python -m compileall -q src`
   - `uv run --frozen --extra test pytest` in `autobyteus-image-audio`
   - wrapper command from outside project directory, ideally after removing the ignored project `.venv` or using a clean simulated env where practical
   - MCP tool list/schema compatibility
10. Update README/DESIGN with simple wrapper-based CLI examples, concise setup note, and preserved MCP docs.

## Key Tradeoffs

- Direct services vs MCP subprocess wrapper: direct services require refactor but give clean ownership, lower overhead, and no protocol dependency for CLI.
- Root wrapper vs global install: root wrapper is easier for skills and avoids host-specific package installs; it requires repo path availability.
- JSON-only first version vs human output modes: JSON-only is simpler and best for agents; human text can be a later additive feature if needed.
- Stdlib `argparse` vs `typer/click`: `argparse` avoids new dependencies and is enough for this scoped CLI, but implementation should still invest in clear subcommands, flags, aliases only if useful, and examples.
- Simple docs vs complete setup transparency: main docs should stay simple; detailed `uv` behavior belongs in a short note/troubleshooting section.

## Risks

| Risk | Mitigation |
| --- | --- |
| Service extraction changes MCP schemas | Keep MCP function signatures/decorator metadata in `server.py`; run in-memory MCP tests. |
| `uv --frozen` fails after pyproject script update if lock is stale | Update `uv.lock` as part of implementation and validate wrapper. |
| Missing `uv` on host | Wrapper checks `uv` and exits clearly; docs state host prerequisite. |
| Provider calls require credentials/cost | Local tests mock clients; integration tests skip without env. |
| CLI setup failures before Python CLI starts do not emit project JSON | Wrapper should handle at least missing `uv` and setup invocation failures clearly; Python CLI owns post-start JSON envelopes. |
| Shell JSON escaping for wrapper-level errors can be brittle | Keep wrapper-level error messages concise; prefer simple structured output for missing `uv`, otherwise let `uv` diagnostics go to stderr with non-zero exit if full JSON wrapping is too complex. |

## Guidance For Implementation

- Preserve existing MCP public tool names and signatures.
- Do not make CLI depend on FastMCP internals.
- Do not make services depend on CLI response envelope.
- Keep service result keys identical to existing MCP structured outputs; CLI wraps those under `result`.
- Keep CLI examples simple and skill-ready; do not tell agents to run setup, write config files for normal per-call settings, or pass raw MCP JSON for normal use.
- Use mocked provider clients for local tests rather than real generation.
- Do not add `workflow-state.md` or restart the stale broad CLI ticket.
