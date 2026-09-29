# Design Spec

## Solution And Approval Basis

- Current solution revision ID: SR-003
- Approved requirements baseline / user-approval reference: requirements-doc.md as approved in SR-002 (user "approved", 2026-09-29; DEC-001..005 resolved to recommendations)
- Behavior-defining supplements: none
- Design status: `Ready`
- Canonical investigation-notes path: `/home/autobyteus/workspace/autobyteus-mcps-video-audio-cli-skill/tickets/in-progress/video-audio-cli-skill/investigation-notes.md`
- Golden evidence: `evidence/mcp-tools-baseline-pre-change.json` (32 tools: name, description, inputSchema, outputSchema captured before any change)

## Current-State Read

`video-audio-mcp` is a flat Python project. `core.py` creates the module-global `FastMCP("VideoAudioServer")` and also holds the domain helpers (`resolve_path`, ffmpeg fallback runner, time parsing, media probe). `tools/{composition,editing,properties}.py` register 31 tools with `@mcp.tool`, each mixing schema declaration, path resolution, ffmpeg logic and *string* success/error results (about 80 error-return sites plus catch-all "An unexpected error occurred" handlers). `server.py` adds `health_check` and runs stdio. There is no console script and no installable package. Consequence: nothing can be reused without importing FastMCP, and failures are unparseable text (BEH-001..007, evidence in notes).

## Task Size And Architectural Risk (Mandatory)

- Task size: `Large`
- Size rationale: new installable package layout; all 32 operations relocated and their ~80 error sites converted; new CLI, launchers, skill, tests and docs; directory rename. Three subsystems (core operations, CLI surface, MCP adapter) plus packaging.
- Architectural risk: `High`
- Risk rationale: new public contract (CLI envelope, error codes, exit codes), ownership-boundary change (transport decoupled from operations), deployment/launch-path change (directory rename, new launcher, `uv.lock`), security-relevant path/overwrite policy, and a hard compatibility obligation (REQ-004/QR-003: 32 MCP schemas and string results unchanged through a refactor).
- Content-vs-structure check: media fixtures are payload evidence only; classification rests on the structural surfaces above.
- Escalation trigger: if FastMCP cannot reproduce the baseline schemas from generated wrappers (see Risks R-1), or any operation cannot be moved without behavior change, return `Design Impact`.

## Architecture Investigation Evidence

See `investigation-notes.md`, section "Architecture-Phase Investigation". Key: baseline probe (32 tools + outputSchemas), nested `resolve_path` sites (`font_file`, `clip_path`), missing-ffmpeg misclassification, single external reference (root README row), ffmpeg absent on host.

## Intended Change

Turn the project into one relocatable bundle `video-audio-editing/` (git-renamed from `video-audio-mcp/`), with a transport-neutral operations core; a task-oriented CLI (`video-audio`) and a thin MCP adapter (`video-audio-mcp`) are two surfaces generated from the same operation registry. Add launchers, `SKILL.md`, agent metadata, tests and docs following `browser-automation`.

## Relevant Behavior And Production-Path Map (Mandatory)

| Behavior ID | Kind | Requirement / AC IDs | Trigger | Existing Behavior Evidence | Change / Preserved Outcome | Target Path / Spine |
| --- | --- | --- | --- | --- | --- | --- |
| BEH-001 | Contract | REQ-002/003/004, AC-001/006 | CLI invocation or MCP tool call | notes BEH-001 | Every op available on both surfaces; MCP schemas identical | DS-001, DS-002 |
| BEH-002 | Contract | REQ-012, AC-007 | Any path argument | `core.resolve_path` | CLI: `WorkspacePathPolicy`; MCP: `LegacyPathPolicy` = old behavior | DS-001 (path policy off-spine) |
| BEH-003 | Contract | REQ-006/007/008, AC-003 | Op failure | strings | Core raises `MediaError`; CLI renders envelope; MCP renders legacy text | DS-001, DS-002 |
| BEH-004 | Contract | REQ-012, AC-007 | Output written | `overwrite_output=True` | CLI refuses existing output without `--overwrite`; MCP unchanged | DS-001 |
| BEH-005 | System | REQ-011, AC-006 | Op body | in-line fallbacks, concat normalization | Bodies moved verbatim except error/return conversion | DS-003 |
| BEH-006 | Operational | REQ-009/010, AC-002/008 | Launcher + `health-check` | `health_check` static string | Launcher provisions env; health op reports ffmpeg/ffprobe | DS-001, DS-004 |
| BEH-007 | Contract | REQ-003, AC-004 | structured args | dict/list params | `--*-json` options validated with pydantic `TypeAdapter` | DS-001 |

## Relevant Supplemental Task Artifacts

| Artifact | Purpose | Reqs | Relationship | Status |
| --- | --- | --- | --- | --- |
| `evidence/mcp-tools-baseline-pre-change.json` | Golden MCP contract | REQ-004, QR-003, AC-001/006 | Snapshot test input; must not be regenerated from new code | Final |
| `docs/mcp-to-cli-mapping.md` | Governing mapping convention | REQ-002/003 | Checklist applied in this design | Repo policy |

## Task Design Health Assessment (Mandatory)

- Change posture: `Larger Requirement` (new surface plus required refactor)
- Current design issue found: `Yes`
- Root cause classification: `Boundary Or Ownership Issue` (transport registration coupled with domain logic; global `mcp` instance; string-typed outcomes)
- Refactor needed now: `Yes`
- Evidence: `core.py` owns `FastMCP`; every tool module imports it; results are strings.
- Design response: one `operations` package owns behavior; typed `OperationResult`/`MediaError` cross the boundary; CLI and MCP are adapters generated from one registry.
- Refactor rationale: a CLI without extraction would duplicate ~1500 lines or route through MCP (rejected by the convention doc).
- Deferrals: none of the ffmpeg logic is redesigned (bodies preserved); no new editing features.

## Terminology

- **Operation**: one former MCP tool (`trim_video`), the unit registered once and projected to both surfaces.
- **Path policy**: injected object deciding how input/output paths are resolved and validated.
- **Legacy text**: the exact string an MCP tool returned before this change.

## Design Reading Order

Follows the template order below.

## Legacy Removal Policy (Mandatory)

- Policy: `No backward compatibility; remove legacy code paths.`
- Obsolete in scope: `core.py`, `tools/`, `server.py`, `main.py` (hello-world stub), old flat layout, the `video-audio-mcp/` directory name, the documented launch command `uv --directory … run server.py`.
- Note on REQ-004: "MCP unchanged" means unchanged *tool contract and results*, not the launch command. The documented launch changes to `scripts/video-audio-mcp` at the new path (approved DEC-002 with README migration note). No `server.py` shim is retained.

## Persisted Data / State Transition Decision

`Not Affected`: the only persisted artifacts are user media files written on request; no schema/state store exists.

## Data-Flow Spine Inventory

| Spine ID | Scope | Behavior IDs | Start | End | Governing Owner | Why It Matters |
| --- | --- | --- | --- | --- | --- | --- |
| DS-001 | Primary End-to-End (CLI) | BEH-001..004,006,007 | `scripts/video-audio <cmd> --opts` | one JSON envelope + exit status | `cli` (main) over `operations.registry` | The new agent path |
| DS-002 | Primary End-to-End (MCP) | BEH-001,003 | MCP `call_tool` | legacy string/float | `mcp.server` over `operations.registry` | Compatibility path |
| DS-003 | Bounded Local | BEH-005 | Operation body | ffmpeg process | `operations.<family>` + `ffmpeg_runtime` | Behavior must not change |
| DS-004 | Bounded Local | BEH-006 | Launcher | ready token / bootstrap envelope | `scripts/video-audio` | Self-provisioning |

## Primary Execution Spine(s)

- DS-001: `video-audio <subcommand> → cli.main → cli_parser (spec→argparse) → decode/validate JSON options → registry.spec.invoke(ctx{WorkspacePathPolicy}) → operations.<family>.<op> → ffmpeg_runtime → OperationResult | MediaError → envelope writer → stdout/exit code`
- DS-002: `MCP tool call → FastMCP → generated wrapper → registry.spec.invoke(ctx{LegacyPathPolicy}) → same operation → legacy renderer (message | legacy value | error text)`

## Spine Narratives (Mandatory)

| Spine | Narrative | Main Nodes | Owner | Off-Spine Concerns |
| --- | --- | --- | --- | --- |
| DS-001 | Launcher captures caller cwd → Python CLI builds the parser from registered operation specs (option names/types/defaults come from the operation signatures), validates strict JSON options with the annotation's `TypeAdapter`, builds a `MediaContext` with the workspace path policy and overwrite flag, invokes the operation, and prints one envelope. | parser, registry, operation, runtime | `cli.main` | path policy, error taxonomy, JSON codec |
| DS-002 | At startup the MCP adapter iterates the same registry; each wrapper exposes the operation's original annotated signature, so FastMCP derives the original schemas; results/errors are rendered to the legacy text. | registry, wrapper | `mcp.server` | legacy path policy, legacy renderer |
| DS-003 | Operation bodies are the current tool bodies with three mechanical changes: `ctx.paths.input/output` instead of `resolve_path`, `raise MediaError(...)` instead of `return "Error…"`, `return OperationResult(...)` instead of success strings. | operation, ffmpeg wrapper | family module | — |
| DS-004 | Same launcher contract as `browser-automation`: locate bundle, `uv run --frozen video-audio`, forward stdout only if the Python entrypoint wrote the ready token, else canned `BOOTSTRAP_FAILED`. | launcher | script | — |

## Spine Actors / Main-Line Nodes

`cli.main`, `cli_parser`, `operations.registry` (spec + `MediaContext`), operation functions, `ffmpeg_runtime`, `mcp.server`.

## Ownership Map

- `operations.registry`: the single catalog of operations, their public signatures, descriptions, output flag; owns `invoke` (catch-all → `INTERNAL_ERROR`, keeping behavior of the old per-tool catch-alls in one place).
- `operations.<family>`: ffmpeg behavior of each operation.
- `ffmpeg_runtime`: binary discovery/preflight (`FFMPEG_MISSING`), `run`, probe, time parsing, media properties, fallback runner (ex-`core` helpers).
- `paths`: both path policies.
- `errors`/`contracts`: `MediaError` (code, message = legacy text, retryable, exit_status, details) and `OperationResult` (message, outputs, data).
- `cli`/`cli_parser`: argv → invocation; envelope; exit codes. `mcp.server`: registration and legacy rendering only.

## Thin Entry Facades / Public Wrappers

| Facade | Governing Owner | Why | Must Not Secretly Own |
| --- | --- | --- | --- |
| `cli.main` | registry + operations | process entry | ffmpeg logic, path rules |
| `mcp.server` wrappers | registry + operations | MCP compatibility | ffmpeg logic, path rules beyond selecting `LegacyPathPolicy` |
| `scripts/video-audio`, `scripts/video-audio-mcp` | Python entrypoints | env bootstrap | any behavior |

## Removal / Decommission Plan (Mandatory)

| Item | Why Unnecessary | Replaced By | Scope | Notes |
| --- | --- | --- | --- | --- |
| `core.py` global `mcp`, helpers | Transport-coupled | `operations.registry`, `ffmpeg_runtime`, `paths` | In this change | |
| `tools/*.py` `@mcp.tool` registration and string returns | Coupled | `operations/*.py` with `@operation` | In this change | `git mv` to keep history |
| `server.py`, `main.py` | Flat entry stubs | `mcp/server.py`, console scripts | In this change | |
| `video-audio-mcp/` directory name | Bundle is now CLI+skill first | `video-audio-editing/` | In this change | root README row updated |
| `pytest` as runtime dependency | Test-only | `[project.optional-dependencies].test` | In this change | DEC-005 |
| Tracked `tests/test_outputs/video_from_image.mp4` | Generated artifact | ignored output dir | In this change | |

## Return Or Event Spine(s)

N/A (synchronous request/response; no events).

## Bounded Local / Internal Spines

- DS-003 (parent: operation family) `operation → ffmpeg-python stream → ffmpeg_runtime.run → (ffmpeg.Error → primary/fallback logic) → OperationResult | MediaError`.
- DS-004 (parent: launcher) `pwd → find uv → uv run --frozen → ready-file check → forward stdout | bootstrap envelope`.

## Off-Spine Concerns Around The Spine

| Concern | Spine | Serves | Responsibility | Why | Risk If On Main Line |
| --- | --- | --- | --- | --- | --- |
| Path policy | DS-001/002/003 | operations | Resolve/validate every input and output path incl. nested `font_file`, `clip_path` | BEH-002/004 differ per surface | Duplicated resolution per tool; surface-specific `if` in ops |
| Error taxonomy | DS-001/002 | cli, mcp | Stable code/exit/message | REQ-006 | String parsing |
| Strict JSON codec | DS-001 | cli | Reject NaN/Infinity; single-envelope encoding | Convention | Invalid stdout |
| ffmpeg preflight | DS-001/003 | ops | `FFMPEG_MISSING` before running | Misleading legacy error | Wrong error category |
| Artifact result extraction | DS-001 | cli | `outputs` list from `OperationResult` | REQ-007 | Agents parse text |

## Ownership Boundaries

Authoritative boundary: `operations.registry.OperationSpec.invoke(ctx, **kwargs)` (public) — everything below it (ffmpeg wrappers, path policies, parsing helpers) is internal. Adapters never import ffmpeg-python or operation bodies directly.

## Boundary Encapsulation Map

| Boundary | Internal Mechanisms | Callers That Must Use It | Forbidden Bypass | If Too Thin |
| --- | --- | --- | --- | --- |
| `OperationSpec.invoke` | catch-all conversion, ffmpeg runtime, path policy | `cli`, `mcp.server`, tests | CLI calling operation function directly to skip conversion | Add a field to `OperationSpec`, not adapter-side logic |
| `MediaContext.paths` | `LegacyPathPolicy`, `WorkspacePathPolicy` | operation bodies | `os.path`/`resolve_path` in ops | Extend `PathPolicy` |

## Dependency Rules

`cli` → `operations`, `errors`, `contracts`, `paths`, `json_codec`. `mcp` → `operations`, `errors`, `paths`. `operations` → `ffmpeg_runtime`, `errors`, `contracts`, `paths`. `operations`/`ffmpeg_runtime`/`paths`/`errors` **must not** import `mcp` (FastMCP) or `cli` (AC-009). No adapter imports another adapter.

## Interface Boundary Mapping

| Interface | Subject | Responsibility | Identity | Notes |
| --- | --- | --- | --- | --- |
| `operation(...)` decorator | operation catalog | register + wrap | function name = MCP tool name; CLI name = kebab-case | `writes_output`, `legacy_value` options |
| `OperationSpec.invoke(ctx, **kw)` | one operation | run, convert unexpected exceptions | kwargs = original argument names | returns `OperationResult` or raises `MediaError` |
| `PathPolicy.input(p)` / `.output(p)` | path resolution | resolve and validate | raw string from caller | separate methods: read vs write semantics differ |
| `MediaError.to_payload()` | error rendering | code/message/retryable/details | — | message bounded for CLI |

## Interface Boundary Check

All interfaces singular, identity explicit, ambiguous-selector risk Low. `PathPolicy` deliberately split into `input`/`output`.

## Main Domain Subject Naming Check

Names retained from MCP tools (`trim_video`, …); package `video_audio`, CLI `video-audio`, bundle `video-audio-editing`. Natural and consistent with browser precedent.

## Existing Capability / Subsystem Reuse Check

| Need | Existing Area | Decision | Why |
| --- | --- | --- | --- |
| Launcher, JSON codec, envelope/exit pattern | `browser-automation` (pattern, not import) | Reuse pattern, copy small files | Bundles must be relocatable; no cross-bundle Python dependency |
| Operation bodies | current `tools/*.py` | Reuse (move) | Preserve behavior |
| Workspace/overwrite policy | browser `ArtifactPolicy` | Extend (new, media-specific) | Different rules: absolute inputs allowed, outputs confined |

## Subsystem / Capability-Area Allocation

| Area | Concerns | Spines | Decision |
| --- | --- | --- | --- |
| `operations` | Behavior, registry | DS-001..003 | Create New (from `tools`/`core`) |
| `ffmpeg_runtime`, `paths`, `errors`, `contracts`, `json_codec` | Shared mechanisms | all | Create New (from `core`) |
| `cli` | Surface + envelope | DS-001 | Create New |
| `mcp` | Adapter | DS-002 | Create New |
| `scripts`, skill, docs | Delivery | DS-004 | Create New |

## Draft / Reusable / Final File Responsibility Mapping

Shared structures: `OperationResult`, `MediaError`, `PathPolicy` are single definitions in `contracts.py`, `errors.py`, `paths.py` (extracted once; no per-family copies). Redundant attributes removed: `MediaError` carries `message` only (no separate legacy string) — the legacy text *is* the message; `OperationResult.legacy_value` only via the decorator option.

| File | Area | Boundary | Concern | Why One File |
| --- | --- | --- | --- | --- |
| `src/video_audio/errors.py` | shared | error taxonomy | `MediaError` + factories, codes/exit map | one taxonomy |
| `src/video_audio/contracts.py` | shared | result types | `OperationResult`, `RuntimeReport` | one result shape |
| `src/video_audio/paths.py` | shared | path policy | `PathPolicy` protocol, `LegacyPathPolicy`, `WorkspacePathPolicy` | both policies compared side-by-side |
| `src/video_audio/ffmpeg_runtime.py` | shared | ffmpeg | discovery, `run`, probe, `parse_time`, `get_media_properties`, `run_with_fallback` | ex-`core` helpers |
| `src/video_audio/json_codec.py` | shared | JSON | strict load/dump | copy of browser pattern |
| `src/video_audio/operations/registry.py` | operations | catalog | `operation`, `OperationSpec`, `MediaContext`, `all_operations()` | one registry |
| `src/video_audio/operations/composition.py` | operations | family | 9 ops | ex-`tools/composition.py` |
| `src/video_audio/operations/editing.py` | operations | family | 5 ops | ex-`tools/editing.py` (keeps safe-concat constants) |
| `src/video_audio/operations/properties.py` | operations | family | 17 ops | ex-`tools/properties.py` |
| `src/video_audio/operations/runtime.py` | operations | family | `health_check` op returning `RuntimeReport` data | separates from media ops |
| `src/video_audio/cli_parser.py` | cli | parser | spec→argparse mapping | mapping rules in one place |
| `src/video_audio/cli.py` | cli | entry | envelope, exit codes, ready token, `main` | mirrors `browser_automation/cli.py` |
| `src/video_audio/mcp/server.py` | mcp | adapter | `create_server`, `main` | small |
| `src/video_audio/mcp/legacy.py` | mcp | adapter | wrapper builder, `render_legacy` | compat rules isolated |

## Applied Patterns

- **Registry + decorator**: one declaration per operation; both surfaces derived. Solves 32×(parser+tool+wrapper) duplication and guarantees AC-001 parity.
- **Adapter**: `mcp/legacy.py`, `cli.py`.
- **Strategy**: `PathPolicy` implementations chosen per surface.

## Target Subsystem / Folder / File Mapping

| Path | Kind | Owner | Responsibility | Must Not Contain |
| --- | --- | --- | --- | --- |
| `video-audio-editing/` (git rename of `video-audio-mcp/`) | Folder | bundle | one relocatable bundle | build artifacts |
| `SKILL.md`, `agents/openai.yaml` | File | skill | agent instructions + metadata | implementation detail beyond usage |
| `scripts/video-audio`, `scripts/video-audio-mcp` | File | launchers | bootstrap (DS-004); MCP launcher keeps stdout for JSON-RPC, logs to file | logic |
| `pyproject.toml`, `uv.lock` | File | packaging | src layout; `[project.scripts] video-audio = video_audio.cli:main`, `video-audio-mcp-server = video_audio.mcp.server:main`; `mcp` stays a dependency (adapter is retained); `pytest` → `test` extra; `pillow` only if used by code (verify) | — |
| `src/video_audio/**` | Folder | per table above | | FastMCP imports outside `mcp/` |
| `tests/unit`, `tests/media`, `tests/integration` | Folder | validation | see Guidance | |
| `README.md`, root `README.md` row | File | docs | CLI/skill/MCP/ffmpeg prerequisites; migration note for renamed launch path | stale claims (Python 3.8 badge) |
| deleted: `core.py`, `tools/`, `server.py`, `main.py` | — | — | — | — |

## Folder Boundary Check

| Path | Depth | Boundary Clear | Risk | Note |
| --- | --- | --- | --- | --- |
| `src/video_audio/` flat shared modules | Mixed Justified | Yes | Low | five small modules; sub-folders would over-split |
| `operations/` | Main-Line | Yes | Low | one file per family retained from current split |
| `mcp/` | Transport | Yes | Low | only place importing FastMCP |

## Concrete Examples / Shape Guidance

| Topic | Good | Avoided | Why |
| --- | --- | --- | --- |
| Operation | `@operation(description=<verbatim old text>, writes_output=True) def trim_video(ctx, video_path: Annotated[str, Field(description=…)], …, reencode: Annotated[bool, Field(…)] = True) -> OperationResult:` … `raise MediaError.input_not_found(f"Error: Input video file not found at {p}")` | `return "Error: …"`; module-global `mcp` | typed outcome, same text |
| CLI mapping | `trim-video --video-path a.mp4 --output-video-path b.mp4 --start-time 1 --end-time 3 --no-reencode [--overwrite]` | `call-tool trim_video --payload {...}` | argument-isomorphic |
| Structured | `add-text-overlay … --text-elements-json '[{"text":"Hi","start_time":0,"end_time":2}]'` | `--text-elements a=b` | strict JSON rule |

### CLI parser mapping rules (implementation guidance, from the signature annotations)

| Annotation | Option | Notes |
| --- | --- | --- |
| `str` (no default) | `--x-y VALUE`, required | |
| `str \| None`, `int \| None`, `float \| None` = None | optional, default None (omitted → not passed) | |
| `int`, `float` | typed; floats must be finite | bound checks only where the op already enforces them |
| `bool = True` | `--x/--no-x` (`BooleanOptionalAction`) | e.g. `--reencode/--no-reencode` |
| `bool = False` | value-less flag | (none today; rule for future) |
| `list[…]`, `dict`, `dict \| None` | `--x-json` (strict JSON) validated by `pydantic.TypeAdapter(annotation)` | `video_paths`→`--video-paths-json`, `font_style`→`--font-style-json`, … |
| `Union[str, float]` (`frame_location`) | `--frame-location` as string (`first`, `last`, `12.5`, `00:00:03`) | numeric strings accepted by ffmpeg `-ss` unchanged |
| any op with `writes_output=True` | extra CLI-only `--overwrite` flag | not an MCP argument; documented |

### Error classification (applies to every converted site)

| Legacy site | Code | Exit | Retryable |
| --- | --- | --- | --- |
| "Input … not found", `FileNotFoundError`, `os.path.exists` guards | `INPUT_NOT_FOUND` | 4 | no |
| ffprobe/probe failure on an existing file (`RuntimeError` from `get_media_properties`, "Error probing…") | `MEDIA_UNREADABLE` | 4 | no |
| Parameter validation returns ("No video paths provided", "xfade only for exactly two videos", "Invalid frame_location type", missing keys, bad transition type) | `INVALID_ARGUMENT` | 2 | no |
| `ffmpeg.Error` (primary+fallback failed included) | `FFMPEG_FAILED` (details: bounded `ffmpeg_stderr`, `attempts`) | 5 | no |
| ffmpeg/ffprobe binary absent | `FFMPEG_MISSING` | 3 | no |
| Path policy violation / existing output | `ARTIFACT_PATH_REJECTED` / `ARTIFACT_EXISTS` | 2 | no |
| Anything else caught by `invoke` | `INTERNAL_ERROR` ("An unexpected error occurred: …") | 5 | yes |
| CLI usage/JSON errors | `INVALID_ARGUMENT` | 2 | no |
| Launcher/runtime bootstrap | `BOOTSTRAP_FAILED` | 3 | yes |

## Backward-Compatibility Rejection Log (Mandatory)

| Mechanism | Why Considered | Decision | Replacement |
| --- | --- | --- | --- |
| Keep `server.py` shim / old launch command | Existing MCP client configs | Rejected | Documented new launcher + README migration note (approved DEC-002) |
| Keep `tools/` re-exports | Old tests import them | Rejected | Tests re-homed to registry/`legacy` helper |
| Dual "legacy vs new" branches inside operations | Path/overwrite differences | Rejected | Injected `PathPolicy` — one body |
| Generic `call-tool` CLI | Cheap uniform CLI | Rejected | Argument-isomorphic subcommands (convention doc) |

## Derived Layering

`launchers → cli | mcp → operations.registry → operations.<family> → ffmpeg_runtime / paths / errors / contracts`.

## Change / Refactor Sequence

1. `git mv video-audio-mcp video-audio-editing`; create src layout, `pyproject.toml` (scripts, extras), regenerate `uv.lock`.
2. Add shared modules (`errors`, `contracts`, `paths`, `ffmpeg_runtime`, `json_codec`) and `operations/registry.py`.
3. Move each family from `tools/` to `operations/`, converting path use, returns and errors (per tables above); delete the per-tool catch-all handlers made redundant by `invoke`.
4. Add `mcp/legacy.py` + `mcp/server.py`; **gate**: baseline snapshot (all 32 name/description/inputSchema/outputSchema) matches, and re-homed media tests pass with legacy string assertions (needs ffmpeg).
5. Add `cli_parser.py`, `cli.py`, launchers; process tests.
6. Write `SKILL.md`, `agents/openai.yaml`, README, root README row; skill-contract and black-box tests.
7. Delete `core.py`, `tools/`, `server.py`, `main.py`, tracked generated output; final full-suite run.

## Key Tradeoffs

- Registry/signature introspection adds a small framework but guarantees parity and removes ~64 hand-written mappings.
- Copying launcher/codec from `browser-automation` duplicates ~100 lines; accepted to keep bundles relocatable and independent.
- CLI stricter than MCP (paths/overwrite/`FFMPEG_MISSING` text) — approved DEC-003; MCP stays legacy.

## Risks

- R-1: FastMCP may not honor a wrapper `__signature__`/annotations exactly (schema drift). Mitigation: baseline snapshot gate at sequence step 4. Fallback: generate wrappers via `exec`/hand-written thin wrappers from the spec — no design change beyond `mcp/legacy.py`.
- R-2: Converting ~80 error sites may mis-classify a code; text must remain byte-identical. Mitigation: per-family re-homed tests assert legacy text; classification table above; code review of every `raise`.
- R-3: ffmpeg absent locally: media tests cannot run until installed (`apt-get install ffmpeg`); tests mark `requires_ffmpeg` and skip when absent (AC-012) but the validation gate requires a run with ffmpeg.
- R-4: **DR-1 deviation to record**: when ffmpeg is absent the old MCP text was the misleading "Input file not found…"; the MCP text becomes an accurate "ffmpeg executable not found" message. This is an unsupported host state (README lists ffmpeg as prerequisite) and does not alter any supported result.
- R-5: External AutoByteus MCP configs pointing at the old path/`server.py` will break; migration note required; outside this repo.
- R-6: Python floor: keep `>=3.13` unless verified lower during implementation (DEC-005).

## Guidance For Implementation

- Preserve every tool description string verbatim (they are in the baseline JSON) and each `Field(description=…)`.
- Tests: `tests/unit` (parser mapping vs baseline schemas, policy, codec, envelope, exit codes, registry parity, import-without-`mcp` test for core); `tests/media` (existing 8 modules re-homed, real ffmpeg, marker `requires_ffmpeg`); `tests/integration` (launcher black box from an unrelated cwd incl. quoting/multiline/invalid JSON/missing option/default `--reencode`, skill-contract test, real MCP stdio parity comparing CLI and MCP outputs by ffprobe duration/streams).
- Launcher env: `VIDEO_AUDIO_WORKSPACE` (absolute existing dir; default caller cwd), `VIDEO_AUDIO_CLI_READY_FILE`, `UV_BIN`; ready token `video-audio-cli-ready-v1`.
- `WorkspacePathPolicy`: outputs `realpath`-confined to workspace (absolute allowed only if inside), parent dirs created inside workspace, existing file → `ARTIFACT_EXISTS` unless `--overwrite`; inputs: relative → workspace, absolute allowed. Every use site (incl. nested `font_file`, `clip_path`) goes through the policy; resolve paths *before* ffmpeg `try` blocks.
- `health_check` op returns message "Server is healthy!" (MCP unchanged) and data `{ffmpeg, ffprobe, workspace}`; the CLI `health-check` additionally fails with `FFMPEG_MISSING` if either is absent (CLI-owned readiness policy; documented disposition "combined for a documented reason").
- `SKILL.md`: follow `browser-automation/SKILL.md` structure; include per-family quick recipes (trim, concat, extract audio/frame, subtitles JSON example, convert), error-code recovery table, safety (workspace outputs, `--overwrite`, no destructive inputs).
- Disposition table (AC-001): all 32 operations → direct subcommand (`health_check`→`health-check` with readiness policy); none dropped.
