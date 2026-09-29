# Investigation Notes

## Investigation Meta

- Package identifier: `video-audio-cli-skill`
- Request / ticket: "Learn from the browser automation and convert the video audio mcp to CLI with skill" (user, 2026-09-29)
- Workspace root: `/home/autobyteus/workspace/autobyteus-mcps-video-audio-cli-skill`
- Repository mode: Git
- Task worktree / branch: `/home/autobyteus/workspace/autobyteus-mcps-video-audio-cli-skill` / `codex/video-audio-cli-skill`
- Resolved base: `origin/main` @ `d0fb10ddc879fa713612096a9c176a8c3b9130bd` (refreshed with `git fetch origin` before worktree creation; base chosen from the tracked default branch, no explicit user override)
- Finalization target: `origin/main` (default; confirm with user at delivery)
- Bootstrap result: worktree and ticket folder created; `requirements-doc.md` and this file created before deeper investigation. No blocker.
- Current solution revision ID: SR-001
- Investigation status: Requirements-phase investigation complete; architecture-level investigation deferred until requirements approval.

## Initial Request And Clarifications

- Original request: study `browser-automation` (the completed MCP→CLI+skill conversion) and convert `video-audio-mcp` to a CLI with a skill.
- Clarifications received: none yet. Open decisions listed in requirements DEC-001..DEC-005.
- User-supplied facts: `browser-mcp` was removed on remote (replaced by `browser-automation`); local copy deleted earlier in this session.
- Initial ambiguity: whether the MCP server is retained; whether the project directory is renamed; path/overwrite policy for the CLI.

## Product And Domain Understanding

- Product area: `video-audio-mcp/`, a FastMCP server ("VideoAudioServer") over ffmpeg for editing video/audio (trim, concat, overlays, subtitles, format/property conversion, silence removal, etc.).
- Actors: AutoByteus agents (primary), developers/users running commands.
- Purpose of the conversion: give agents a Bash-invokable, self-provisioning CLI plus a `SKILL.md`, per the repository convention in `docs/mcp-to-cli-mapping.md`.

## Source Log

| Date | Type | Source / Command | Why | Finding | Follow-up |
| --- | --- | --- | --- | --- | --- |
| 2026-09-29 | Command | `git pull --ff-only`, `git ls-tree origin/main` | Confirm state of main | `browser-mcp` absent on origin/main; `browser-automation` present | none |
| 2026-09-29 | Doc | `docs/mcp-to-cli-mapping.md` | Governing conversion convention | Argument-isomorphic mapping: tool→kebab subcommand, arg→`--kebab-option`, structured→strict `--*-json`, one JSON envelope on stdout, shared application boundary for CLI+MCP | Apply |
| 2026-09-29 | Code | `browser-automation/README.md`, `SKILL.md`, `scripts/browser`, `pyproject.toml`, `src/browser_automation/{cli,application,errors,policy}.py`, `mcp/server.py`, `mcp/tools/screenshot.py` | Learn the reference implementation | See "Reference Pattern" below | Apply in design |
| 2026-09-29 | Code | `video-audio-mcp/{server,core,main}.py`, `tools/{editing,composition,properties}.py`, `pyproject.toml`, README | Inventory current behavior | See tool inventory below | Design phase |
| 2026-09-29 | Doc | `tickets/done/image-audio-mcp-cli/requirements.md`, `tickets/done/browser-mcp-cli-skill/cli-conversion-analysis.md` | Prior conversion precedent | image-audio: service extraction + wrapper + `--config` options; browser: argument-isomorphic CLI, schema-v1 envelope, exit categories, skill locator rules, structured errors | Reuse decisions |
| 2026-09-29 | Command | `which ffmpeg ffprobe uv; python3 --version` | Runtime prerequisites on this host | `uv` present (`/usr/local/bin/uv`); Python 3.13.15; **ffmpeg/ffprobe not found on PATH** | Risk RISK-002 |
| 2026-09-29 | Command | `git ls-files video-audio-mcp` | Tracked fixtures | Sample media tracked under `tests/` (sample.mp4, sample.png, sample_audio.wav, sample_files/*.mp4, test_outputs/video_from_image.mp4) | Design/test phase |

## Relevant Existing Behavior And Supported Product Paths

| Behavior ID | Kind | Supported Trigger | Current Supported Path | Outcome / Invariants | Evidence | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| BEH-001 | Contract | MCP client launches `server.py` over stdio | FastMCP registers 32 tools (31 media tools + `health_check`) on one module-global `mcp` instance (`core.py`); tool bodies run ffmpeg via `ffmpeg-python` synchronously | Tool names/args/descriptions are the public contract | `server.py`, `tools/*.py` | High |
| BEH-002 | Contract | Any tool call with a path | `core.resolve_path`: absolute paths as-is; relative paths joined to `AUTOBYTEUS_AGENT_WORKSPACE` if set, else left relative (server cwd). No confinement to a workspace | Absolute inputs/outputs anywhere are allowed | `core.py:resolve_path` | High |
| BEH-003 | Contract | Any tool failure | Errors are returned as plain strings beginning `Error…` or `An unexpected error occurred…`, not raised; success also a string ("...saved to <path>"), except `get_media_duration` returning a float | No structured error code, no exit status; callers parse text | 81 error-return sites across `tools/*.py` (grep) | High |
| BEH-004 | Contract | Any output-producing tool | ffmpeg invoked with `overwrite_output=True`: existing outputs are silently replaced | Overwrite is default | `tools/*.py`, `core._run_ffmpeg_with_fallback` | High |
| BEH-005 | System | ffmpeg operations | Several tools retry with a fallback method (primary→fallback kwargs; trim copy→re-encode); concat normalizes fps/sample-rate/bitrate (SR from ticket `video-audio-mcp-safe-concat-normalization`) | Fallback and normalization semantics must remain identical | `core.py`, `tools/editing.py` | High |
| BEH-006 | Operational | Host prerequisites | Requires system `ffmpeg`/`ffprobe` on PATH and Python ≥3.13 (`pyproject.toml`); dependencies `ffmpeg-python`, `mcp[cli]`, `pydantic`, `pillow`, `pytest` (pytest is a runtime dep!) | No preflight beyond `health_check` returning a static string | `pyproject.toml`, `server.py` | High |
| BEH-007 | Contract | `add_subtitles`, `add_text_overlay`, `add_b_roll` | Structured args: `font_style: dict`, `text_elements: list[dict]`, `broll_clips: list[dict]` | Map to strict `--*-json` per convention | signatures in `tools/composition.py` | High |

## Relevant Codebase And Technical Facts

| Path / Component | Current Responsibility | Requirement Implication | Architecture Question |
| --- | --- | --- | --- |
| `core.py` | Creates the global `FastMCP` instance **and** holds `resolve_path`, ffmpeg fallback runner, time parser, media probe | Transport (FastMCP) and domain helpers are coupled; importing `core` requires `mcp` | Extract transport-neutral application/service layer; MCP adapter becomes thin |
| `tools/*.py` | `@mcp.tool` functions containing both signature/description registration and ffmpeg logic; return strings | Cannot call from CLI without importing FastMCP; error-as-string blocks structured CLI errors | Split capability functions (typed result / typed error) from MCP registration; MCP adapter renders legacy strings to preserve behavior |
| `server.py` | Imports `core.mcp`, `tools`, adds `health_check`, `mcp.run()` | Entrypoint invoked by existing MCP clients (`uv --directory … run server.py`) | Keep working launch path or provide equivalent wrapper |
| `pyproject.toml` | No console scripts, no package layout (flat modules: `core`, `tools`) | uv `run --frozen <script>` pattern of browser-automation needs an installable package with `[project.scripts]` | Package restructure (`src/` layout) implied |
| `tests/*` | 8 pytest modules importing `tools.*` directly and running real ffmpeg; `.mp4` fixtures committed | Existing tests are behavior evidence for parity | Re-home tests against the shared layer; add CLI process tests |
| `browser-automation/` | Reference conversion | See Reference Pattern | — |

### Reference Pattern (browser-automation) — what to learn from

1. **One relocatable bundle**: `SKILL.md`, `agents/openai.yaml`, `scripts/<cli>` launcher, `pyproject.toml` + `uv.lock`, `src/<pkg>/` (cli, application, contracts, errors, policy, mcp adapter), `tests/{unit,integration}`, README.
2. **Launcher `scripts/browser`**: self-locates the bundle, captures caller cwd into `<PKG>_WORKSPACE`, finds `uv` (env `UV_BIN`, PATH, common locations), runs `uv run --frozen <console-script> "$@"`, captures stdout to a temp file and only forwards it if a ready-file token was written by the Python entrypoint; otherwise emits a canned `BOOTSTRAP_FAILED` JSON and exits 3 (so `uv` resolve noise never masquerades as CLI output).
3. **CLI**: stdlib `argparse` subclass whose `error()` raises so usage errors become the JSON envelope; subcommands mirror MCP tool names in kebab-case, options mirror argument names; `--*-json` for structured values; optional file/stdin sources as mutually exclusive alternates; `health-check` subcommand.
4. **Output contract**: one strict JSON value on stdout — `{"schema_version":"1","ok":true,"command":…,"result":…}` or `{…"ok":false,"error":{"code","message","retryable","details?"}}`; stderr diagnostics; exit codes 0/2/3/4/5.
5. **Errors**: `BrowserError(code, message, retryable, exit_status, details)` taxonomy shared by CLI and MCP; MCP adapter converts via `invoke(...)`.
6. **Policy module**: workspace-confined artifact paths (absolute/escaping rejected), `--overwrite` required to replace, strict JSON codec, bounded validation.
7. **Shared core**: a transport-neutral `BrowserApplication` used by both CLI `execute()` and MCP tool registration; MCP tool files are one per tool and thin.
8. **Skill**: `SKILL.md` front matter (`name`, `description` with when/when-not), runtime-locator rules (resolve `scripts/<cli>` relative to the exact advertised `SKILL.md`; no PATH registration, no `cd` into bundle, no venv/uv steps), workflow, output/recovery code table, safety section.
9. **Tests**: unit tests for parser/app/policy; integration tests that launch the real launcher as a subprocess (black box), a skill-contract test, and real-MCP-transport tests.
10. **Docs**: README section per surface; convention captured in `docs/mcp-to-cli-mapping.md`; ticket artifacts under `tickets/`.

### Tool inventory (32 registered tools: `grep -c "@mcp.tool"` = 9 + 5 + 17 + 1)

- `composition.py` (9): `extract_audio_from_video`, `replace_audio_track`, `add_subtitles` (dict arg), `add_text_overlay` (list[dict]), `add_image_overlay`, `create_video_from_image_and_audio`, `extract_frame_from_video` (`frame_location: str|float`), `add_b_roll` (list[dict]), `add_basic_transitions`.
- `editing.py` (5): `trim_video`, `concatenate_videos` (list[str]), `concatenate_audios` (list[str]), `change_video_speed`, `remove_silence`.
- `properties.py` (17): `get_media_duration`, `convert_audio_properties`, `convert_video_properties`, `change_aspect_ratio`, `convert_audio_format`, `set_audio_bitrate`, `set_audio_sample_rate`, `set_audio_channels`, `convert_video_format`, `set_video_resolution`, `set_video_codec`, `set_video_bitrate`, `set_video_frame_rate`, `set_video_audio_track_codec`, `set_video_audio_track_bitrate`, `set_video_audio_track_sample_rate`, `set_video_audio_track_channels`.
- `server.py` (1): `health_check` (static string).
- Proposed disposition for all 32: direct subcommand. Exact schemas to be re-verified by an in-memory MCP `list_tools` probe in the design phase (Unknown-001).

## Structural And Payload Surface Inventory

### Payload Or Content Surfaces
- Sample media fixtures listed in the Source Log; consumed by `tests/*.py`.
- README documents subtitle `font_style` payload example (ASS style dict) that must remain expressible via `--font-style-json`.

### Structural Surfaces
- Flat-module Python project with no console scripts → package restructure and lockfile update needed.
- MCP launch command documented in README (`uv --directory … run server.py`) is an external contract for existing clients.
- Global FastMCP instance in `core.py` is the structural coupling to break.

## Unknowns And Risks

- RISK-001: Existing MCP behavior (string outputs, overwrite default, arbitrary absolute paths) must not regress while CLI gets stricter policies (structured errors, workspace/overwrite policy).
- RISK-002: `ffmpeg`/`ffprobe` are not installed on this host, so real-media tests cannot execute here until installed (may need approval/network); CI/host expectations must be stated in the skill.
- RISK-003: `requires-python >=3.13` and `pytest` as a runtime dependency are pre-existing; keep or fix is a design/scope matter (see DEC-005).
- Unknown-001: exact registered tool count/schemas — probe in design phase.
- Unknown-002: whether existing tests pass unmodified on a host with ffmpeg.

## Architecture-Phase Investigation (after SR-002 approval)

| Date | Source / Command | Observation | Design Decision Supported | Remaining Uncertainty |
| --- | --- | --- | --- | --- |
| 2026-09-29 | `uv run --frozen python` in worktree `video-audio-mcp/`, `await mcp.list_tools()` | 32 tools; each has `name`, `description`, `inputSchema` and `outputSchema` (`{"result": string}`; `get_media_duration` → `number \| string`). Saved as `evidence/mcp-tools-baseline-pre-change.json` (pre-change golden baseline). uv built a Python 3.14 venv (lock `>=3.13`); import works without ffmpeg | QR-003 snapshot test uses this baseline; MCP wrapper must keep annotated signatures and `str` return annotation so FastMCP reproduces identical schemas | none |
| 2026-09-29 | `grep -n "resolve_path(" tools core.py` | Besides top-level path args, `resolve_path` is applied to nested `text_elements[].font_file` and `broll_clips[].clip_path` (composition.py:303, :469) and inside helpers (`core.py:24,25,58`) | Path policy must be an injected object used at every path use site, including nested JSON fields | none |
| 2026-09-29 | Read `tools/editing.py` trim/concat, `composition.py` extract_frame | Error/success both returned as strings; fallbacks encoded in-line; `FileNotFoundError` handler labels a missing **ffmpeg binary** as "Input file not found" (ffmpeg-python runs `ffmpeg` via Popen) | Error taxonomy needs explicit `FFMPEG_MISSING`; MCP legacy text for that unsupported host state becomes accurate | Minor deviation recorded in design (DR-1) |
| 2026-09-29 | `grep -c "return f\?[\"']Error"` | 30 + 30 + 21 error-return sites across three modules (plus unexpected-error returns) | Mechanical conversion `return "Error…"` → `raise MediaError(code, legacy_text)`; per-site code classification listed in design | Exact site count re-derived by implementer |
| 2026-09-29 | `grep -rn "video-audio-mcp" .` outside the project | Only root `README.md:18` table row references it; no CI/config elsewhere in repo | Rename impact inside repo is one README row + the project's own README client configs | External AutoByteus configs pointing at the old path are outside the repo (risk) |
| 2026-09-29 | `git ls-files video-audio-mcp`, `.gitignore` | Tracked media fixtures + tracked generated `tests/test_outputs/video_from_image.mp4`; `tests/__init__` absent, tests use `sys.path.insert` | Tests re-homed under the new package layout; generated output artifact untracked/ignored | none |
| 2026-09-29 | `which ffmpeg` / root user / `apt-get` present | No ffmpeg; installable via apt on this host | Downstream validation must install ffmpeg (RISK-002 mitigation); tests skip cleanly when absent (AC-012) | Needs implementer/validator action |
| 2026-09-29 | Read `browser-automation/src/browser_automation/{cli,errors,mcp/tools/__init__}.py`, `scripts/browser` | Confirmed patterns recorded above; note browser's MCP adapter converts `BrowserError` to `ToolError` and returns structured models — i.e. the browser conversion *changed* its MCP contract, whereas approved REQ-004 here forbids that | Adapter must render legacy strings, not structured results | none |
