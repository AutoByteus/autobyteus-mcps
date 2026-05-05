# Design: Image + Audio MCP / CLI

## Goal

Provide Autobyteus image, audio, model-listing, and UI-coordinate capabilities through two thin public surfaces:

1. a skill-friendly command-line interface; and
2. the existing MCP server.

Both surfaces share one authoritative implementation in `image_audio_mcp.services`.

## Runtime boundary

CLI path:

```text
skill/user shell -> repo wrapper cli/autobyteus-image-audio -> uv project execution -> image_audio_mcp.cli -> image_audio_mcp.services -> Autobyteus clients/filesystem -> JSON envelope
```

MCP path:

```text
MCP client -> image_audio_mcp.server FastMCP facade -> image_audio_mcp.services -> Autobyteus clients/filesystem -> MCP structured result
```

## Key decisions

- **Shared services boundary**: Provider calls, model defaults, safe path resolution, media normalization, output download/write, coordinate detection, and cleanup live in `image_audio_mcp.services`.
- **Thin MCP facade**: `image_audio_mcp.server` owns only FastMCP server creation, public tool registration, tool signatures, descriptions, and launch behavior.
- **Task-oriented CLI facade**: `image_audio_mcp.cli` owns argparse subcommands/options, JSON envelopes, usage errors, and exit codes. It is not a raw MCP/JSON-RPC client and does not expose a generic `call-tool` as normal UX.
- **Wrapper-hidden setup**: `cli/autobyteus-image-audio` resolves the project path and runs `uv --directory <project> run --frozen autobyteus-image-audio ...`, so callers do not need manual `uv sync`, `.venv` activation, or dependency installation.
- **Stateless calls**: Each generation/edit/speech/coordinate operation creates the required client and cleans it up in `finally`.
- **Safe file handling**: Local inputs and outputs go through `resolve_safe_path`, preserving `AUTOBYTEUS_AGENT_WORKSPACE` semantics.

## File-by-file responsibilities

- `cli/autobyteus-image-audio`
  - Repo-level shell wrapper for path-independent, skill-facing execution through `uv run --frozen`.
  - Checks for missing `uv` and reports a clear pre-Python failure.
- `pyproject.toml`
  - Packaging metadata and console scripts:
    - `autobyteus-image-audio = image_audio_mcp.cli:main`
    - `autobyteus-image-audio-server = image_audio_mcp.server:main`
- `src/image_audio_mcp/cli.py`
  - Ergonomic CLI subcommands and options.
  - JSON success/failure envelopes.
  - Repeatable `--config key=value` parsing with dot notation and deterministic scalar typing.
  - Paired `--speaker NAME --voice VOICE` validation for multi-speaker speech.
  - Delegation to services only.
- `src/image_audio_mcp/server.py`
  - MCP server configuration, public tool decorators, public signatures, and `main()`.
  - Delegation to services only.
- `src/image_audio_mcp/services.py`
  - Runtime status/model lists.
  - Image generation/editing.
  - Speech generation.
  - UI target coordinate finding with edit-marker detection and fallback grounding.
  - Workspace/path/media normalization, default model resolution, provider client lifecycle, downloads, and cleanup.
- `tests/test_services_local.py`
  - Mocked service behavior and safe path/output shape checks.
- `tests/test_cli_local.py`
  - CLI parsing, repeatable flags, `--config` dot-notation parsing, speaker/voice pairing, envelopes, and service delegation checks.
- `tests/test_server_local.py`
  - In-memory MCP compatibility checks and public tool inventory.
- `tests/conftest.py`
  - Optional `.env.test` loading; local/mock tests run without private credentials.

## Public capability coverage

| Capability | CLI command | MCP tool | Service function |
| --- | --- | --- | --- |
| Health/default models | `health-check` | `health_check` | `services.health_check()` |
| Image model catalog | `list-image-models` | `list_image_models` | `services.list_image_models()` |
| Audio model catalog | `list-audio-models` | `list_audio_models` | `services.list_audio_models()` |
| Image generation | `generate-image` | `generate_image` | `services.generate_image(...)` |
| Image editing | `edit-image` | `edit_image` | `services.edit_image(...)` |
| Speech generation | `generate-speech` | `generate_speech` | `services.generate_speech(...)` |
| Target coordinates | `find-target-coordinates` | `find_target_coordinates` | `services.find_target_coordinates(...)` |

The CLI uses kebab-case command/option names, repeatable `--input-image` flags for list inputs, and repeatable `--config key=value` flags for generation settings. MCP snake_case remains confined to the MCP/Python boundary.

Round-3 generation settings UX uses repeatable `--config key=value` as the primary path. Nested config keys use dot notation such as `--config image_config.aspect_ratio=16:9`. Values are parsed as JSON when they are valid JSON values (`true`, `false`, `null`, numbers, arrays, objects), otherwise they remain strings. Multi-speaker speech uses paired flags such as `--speaker Joe --voice Kore --speaker Jane --voice Puck`; the CLI validates matching counts and builds `generation_config.speaker_mapping` in pair order.

## Service contracts

- `generate_image(prompt, output_file_path, input_images=None, generation_config=None)`
  - Returns `file_path`, `model`, and `revised_prompt`.
- `edit_image(prompt, output_file_path, input_images=None, mask_image=None, generation_config=None)`
  - Returns `file_path` and `model`.
- `generate_speech(prompt, output_file_path, generation_config=None)`
  - Returns `file_path` and `model`.
- `find_target_coordinates(image, target, marked_image_output_path=None, grounding_model_identifier=None)`
  - Returns marker strategy details plus `pixel_coordinates` and `normalized_coordinates`.
- `list_image_models()` / `list_audio_models()`
  - Return `models` lists containing identifiers, provider/runtime, parameter schema, and default config.
- `health_check()`
  - Returns `status` and resolved default model identifiers.

## Runtime dependencies by concern

- **MCP runtime**: `mcp.server.fastmcp.FastMCP`
- **CLI parsing**: Python stdlib `argparse`
- **Image generation/editing**: `autobyteus.multimedia.image.ImageClientFactory`
- **Speech generation**: `autobyteus.multimedia.audio.AudioClientFactory`
- **Fallback grounding**: `autobyteus.llm.llm_factory.LLMFactory`
- **File safety**: `autobyteus.utils.file_utils.resolve_safe_path`
- **Output IO**: `autobyteus.utils.download_utils.download_file_from_url`

## Runtime simulations

### CLI `generate-image`

1. `cli/autobyteus-image-audio generate-image ...`
2. Wrapper resolves repo/project path.
3. Wrapper executes `uv --directory <project> run --frozen autobyteus-image-audio generate-image ...`.
4. `image_audio_mcp.cli` parses `--prompt`, repeated `--input-image`, repeated `--config key=value`, and `--output-file-path`.
5. CLI calls `services.generate_image(...)`.
6. Services resolve workspace paths, create the configured image client, call the provider, download the image, clean up the client, and return the service result.
7. CLI prints `{"ok":true,"command":"generate-image","result":...}`.

### MCP `generate_image`

1. MCP client invokes `generate_image`.
2. `image_audio_mcp.server` FastMCP tool receives the existing MCP schema-shaped arguments.
3. Server delegates to `services.generate_image(...)`.
4. Services perform the same provider/path/download/cleanup flow as CLI.
5. FastMCP returns the unchanged structured result payload.

### CLI usage error

1. CLI receives invalid shell arguments, invalid `--config key=value`, or mismatched `--speaker` / `--voice` counts.
2. `image_audio_mcp.cli` classifies it as `UsageError`.
3. CLI prints `{"ok":false,"command":"...","error_type":"UsageError","error_message":"..."}` to stdout, emits a concise stderr diagnostic, and exits non-zero.

## Validation posture

- Local implementation checks use mocked providers and in-memory MCP clients.
- Real provider generation/editing/speech remains optional and credential-gated with `RUN_REMOTE_IMAGE_AUDIO_TESTS=1`.
- `uv --frozen` must pass after script metadata changes.
- The repo wrapper must be runnable from outside the project directory.
- The ticket intentionally does not introduce broad multi-MCP CLI infrastructure, host-specific wrappers, or `workflow-state.md`.
