# Design: Image + Audio MCP Server

## Goal
Provide a standalone MCP server that exposes Autobyteus image and TTS capabilities as MCP tools. The server is a thin wrapper around the Autobyteus multimedia client factories and keeps output handling consistent with existing Autobyteus tooling.

## Key Decisions
- **Dependency**: The MCP server depends on the `autobyteus` library to reuse its multimedia clients and configuration logic.
- **Stateless calls**: Each tool call creates a fresh client instance and cleans it up after use. This keeps the server simple and avoids shared state across MCP sessions.
- **Safe file writes**: All outputs are written via `resolve_safe_path` to workspace, Downloads, or temp directories only.

## File-by-file responsibilities
- `pyproject.toml`
  - Packaging metadata, runtime dependencies (`mcp`, `autobyteus`), and CLI entry point.
- `requirements.txt`
  - Lightweight install path for environments that do not use `uv`.
- `README.md`
  - Usage instructions, environment variables, and MCP configuration example.
- `DESIGN.md`
  - Architecture, design decisions, and runtime simulations.
- `src/image_audio_mcp/__init__.py`
  - Package version marker.
- `src/image_audio_mcp/server.py`
  - MCP server definition, tool registration, model selection logic, path normalization, and file output handling.

## Runtime dependencies (by concern)
- **MCP runtime**: `mcp.server.fastmcp.FastMCP`
- **Image generation**: `autobyteus.multimedia.image.ImageClientFactory`
- **Speech generation**: `autobyteus.multimedia.audio.AudioClientFactory`
- **File safety**: `autobyteus.utils.file_utils.resolve_safe_path`
- **Output IO**: `autobyteus.utils.download_utils.download_file_from_url`

## Tool contract summary
- `health_check`
  - Returns server status and resolved default model identifiers.
- `generate_image`
  - Inputs: `prompt`, `output_file_path`, optional `input_images`, `generation_config`, `model_identifier`
  - Output: `file_path`, `model`, optional `revised_prompt`
- `edit_image`
  - Inputs: `prompt`, `output_file_path`, optional `input_images`, `mask_image`, `generation_config`, `model_identifier`
  - Output: `file_path`, `model`
- `generate_speech`
  - Inputs: `prompt`, `output_file_path`, optional `generation_config`, `model_identifier`
  - Output: `file_path`, `model`
- `list_audio_models`
  - Output: `models` list including `parameter_schema` and `default_config`

## Runtime simulation (debug-style call stacks)
The following stacks illustrate typical execution paths. Provider-specific frames vary based on the configured model (OpenAI, Gemini, or Autobyteus remote).

### Case 1: `health_check`
1. `mcp.server.fastmcp.FastMCP._call_tool`
2. `image_audio_mcp.server.health_check`
3. `os.environ.get` (resolve defaults)

### Case 2: `generate_image` (text-only)
1. `mcp.server.fastmcp.FastMCP._call_tool`
2. `image_audio_mcp.server.generate_image`
3. `image_audio_mcp.server._get_workspace_root`
4. `image_audio_mcp.server._resolve_output_path`
5. `autobyteus.utils.file_utils.resolve_safe_path`
6. `autobyteus.multimedia.image.image_client_factory.ImageClientFactory.create_image_client`
7. Provider-specific client call:
   - `autobyteus.multimedia.image.api.openai_image_client.OpenAIImageClient.generate_image`
   - or `autobyteus.multimedia.image.api.gemini_image_client.GeminiImageClient.generate_image`
   - or `autobyteus.multimedia.image.api.autobyteus_image_client.AutobyteusImageClient.generate_image`
8. `autobyteus.utils.download_utils.download_file_from_url`
9. `aiohttp.ClientSession.get` or local file copy
10. `image_audio_mcp.server._safe_cleanup`
11. `autobyteus.multimedia.image.base_image_client.BaseImageClient.cleanup`

### Case 3: `edit_image` (with input + mask)
1. `mcp.server.fastmcp.FastMCP._call_tool`
2. `image_audio_mcp.server.edit_image`
3. `image_audio_mcp.server._get_workspace_root`
4. `image_audio_mcp.server._normalize_media_sources`
5. `image_audio_mcp.server._normalize_media_source`
6. `autobyteus.utils.file_utils.resolve_safe_path`
7. `autobyteus.multimedia.image.image_client_factory.ImageClientFactory.create_image_client`
8. Provider-specific client call:
   - `autobyteus.multimedia.image.api.openai_image_client.OpenAIImageClient.edit_image`
   - or `autobyteus.multimedia.image.api.gemini_image_client.GeminiImageClient.edit_image`
   - or `autobyteus.multimedia.image.api.autobyteus_image_client.AutobyteusImageClient.edit_image`
9. `autobyteus.utils.download_utils.download_file_from_url`
10. `image_audio_mcp.server._safe_cleanup`

### Case 4: `generate_speech`
1. `mcp.server.fastmcp.FastMCP._call_tool`
2. `image_audio_mcp.server.generate_speech`
3. `image_audio_mcp.server._get_workspace_root`
4. `image_audio_mcp.server._resolve_output_path`
5. `autobyteus.utils.file_utils.resolve_safe_path`
6. `autobyteus.multimedia.audio.audio_client_factory.AudioClientFactory.create_audio_client`
7. Provider-specific client call:
   - `autobyteus.multimedia.audio.api.openai_audio_client.OpenAIAudioClient.generate_speech`
   - or `autobyteus.multimedia.audio.api.gemini_audio_client.GeminiAudioClient.generate_speech`
   - or `autobyteus.multimedia.audio.api.autobyteus_audio_client.AutobyteusAudioClient.generate_speech`
8. `autobyteus.utils.download_utils.download_file_from_url`
9. `image_audio_mcp.server._safe_cleanup`

## Future extension points
- Client caching keyed by MCP session ID for conversational image editing.
- Dedicated tool to list available image/audio models from factories.
- Optional enforcement for absolute input paths only (stricter security).
