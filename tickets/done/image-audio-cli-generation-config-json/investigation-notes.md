# Investigation Notes: Image/Audio CLI generation_config JSON support

## Investigation Goals

1. Understand the current `autobyteus-image-audio` CLI argument model for generation config.
2. Identify how the CLI maps to MCP service arguments.
3. Determine the smallest safe refactor that preserves existing CLI behavior while allowing MCP-shaped nested `generation_config` JSON.
4. Keep API-key behavior out of scope; environment inheritance remains unchanged.

## Scope Triage

Scope: **Small**

Rationale:

- Expected source changes are limited to the CLI parser and local tests, with README/help documentation updates.
- No service-layer, MCP server, provider-client, or credential behavior changes are required.
- The main data-flow spine remains `CLI argv -> argparse namespace -> generation_config dict -> services.* -> provider client`.

## Sources Consulted

### Local files

- `autobyteus-image-audio/src/image_audio_mcp/cli.py`
  - `_load_generation_config(args)` currently builds `generation_config` only from repeatable `--config key=value` items and optional `--speaker/--voice` pairs.
  - `_add_generation_config_options(parser)` currently exposes only `--config KEY=VALUE`.
  - `_dispatch(args)` forwards `_load_generation_config(args)` to `services.generate_image`, `services.generate_video`, `services.edit_image`, and `services.generate_speech`.
- `autobyteus-image-audio/src/image_audio_mcp/server.py`
  - MCP tools accept `generation_config: Optional[Dict[str, Any]]` directly for image/video/edit/speech tools.
- `autobyteus-image-audio/src/image_audio_mcp/services.py`
  - Services accept `generation_config: Optional[Dict[str, Any]]` and pass it through to multimedia clients without needing flattened CLI-specific representation.
- `autobyteus-image-audio/tests/test_cli_local.py`
  - Existing tests cover `--config` parsing, nested dotted keys, JSON scalar coercion, parent/child conflict errors, and `--speaker/--voice` mapping.
- `autobyteus-image-audio/README.md`
  - Current docs present `--config key=value` and paired `--speaker/--voice` as the CLI usage style.

### Commands run

```bash
grep -n "generation_config\|config\|speaker\|voice" -n autobyteus-image-audio/src/image_audio_mcp/cli.py
grep -n "config\|speaker\|generation" autobyteus-image-audio/tests/test_cli_local.py
grep -n "generation_config\|--config\|speaker\|voice" autobyteus-image-audio/README.md
./cli/autobyteus-image-audio generate-speech --help
```

Key command finding: running the CLI wrapper in the new worktree auto-created `.venv` using `uv run --frozen`, confirming the wrapper continues to use uv environment setup.

## Current Behavior

- Supported generation config input:
  - `--config KEY=VALUE`, repeatable.
  - Dot notation for nested keys, e.g. `--config image_config.aspect_ratio=16:9`.
  - JSON scalar/array/object parsing for individual values only.
  - `--speaker NAME --voice VOICE` pairs for speech mapping convenience.
- Unsupported generation config input:
  - A single MCP-shaped nested JSON object such as `--generation-config '{"mode":"multi-speaker","speaker_mapping":{"Joe":"Kore"}}'`.
  - A config JSON file path.

## Entry Points and Boundaries

- CLI entrypoint: `image_audio_mcp.cli:main` via project script `autobyteus-image-audio`.
- Parser boundary: `build_parser()` and helper `_add_generation_config_options()`.
- Config normalization boundary: `_load_generation_config(args)`.
- Service boundary: `image_audio_mcp.services.*` functions already accept native `dict[str, Any]` generation config.

## File Ownership / Placement

- `cli.py` is the correct owning file for CLI argument parsing and normalization.
- `test_cli_local.py` is the correct test file for parser and dispatch behavior with monkeypatched services.
- `README.md` is the current user-facing CLI/MCP documentation file and should be updated in place.

## Constraints and Unknowns

- Existing `--config` behavior must remain backward-compatible.
- API-key handling is intentionally out of scope. CLI processes inherit environment variables from the parent process via shell/uv/Python process inheritance.
- Inline JSON is shell-quoting sensitive for humans, but the user specifically identified Agent DX as preferring nested JSON. File-based JSON can cover complex or human-edited cases.

## Design Implications

- Add `--generation-config JSON_OBJECT` and `--generation-config-file PATH` as direct MCP-shaped inputs.
- Merge all generation-config sources into one dict before dispatch.
- Preserve existing duplicate/conflict protections so mixed input sources cannot silently override each other.
- Keep `--config key=value` as simple Human DX / backward-compatible sugar rather than the only path.
