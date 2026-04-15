# Autobyteus Image + Audio MCP Server

A lightweight MCP server that exposes Autobyteus image and audio generation tools over the Model Context Protocol (MCP). It wraps the existing Autobyteus multimedia clients so you can reuse the same image and TTS stack in other projects.

## Tools
- `generate_image`: Text-to-image or image-to-image generation.
- `edit_image`: Prompt-based image editing (optional mask).
- `generate_speech`: Text-to-speech (TTS).
- `find_target_coordinates`: Standard coordinate finder for GUI automation (edit-marker pipeline).
- `health_check`: Basic status + default model identifiers.
- `list_audio_models`: List audio models and their `generation_config` JSON schemas.
- `list_image_models`: List image models and their `generation_config` JSON schemas.

**Note:** `generate_image`, `edit_image`, and `generate_speech` use environment-configured default models and do not accept `model_identifier` in tool input.  
`find_target_coordinates` expects `target` text and uses `DEFAULT_IMAGE_EDIT_MODEL`; it may use `DEFAULT_GROUNDING_MODEL` only as marker-detection fallback.
Direct VLM grounding and public visual-grounding model listing are kept internal and are not exposed as public MCP tools.

## Installation
This server depends on the published `autobyteus` library (`1.4.0`).

### Recommended (uv)
From this directory:
```bash
uv sync
```

### Pip
```bash
pip install -r requirements.txt
```

## Running the server
```bash
python -m image_audio_mcp.server
```

## Environment variables
- `IMAGE_AUDIO_MCP_NAME`: Override server name (default `autobyteus-image-audio`).
- `IMAGE_AUDIO_MCP_INSTRUCTIONS`: Override server instructions.
- `AUTOBYTEUS_AGENT_WORKSPACE`: Base path for relative file paths.
- `DEFAULT_IMAGE_GENERATION_MODEL`: Override image generation model.
- `DEFAULT_IMAGE_EDIT_MODEL`: Override image edit model.
- `DEFAULT_SPEECH_GENERATION_MODEL`: Override TTS model.
- `DEFAULT_GROUNDING_MODEL`: Override default grounding LLM for marker-fallback logic.

Provider credentials:
- OpenAI: `OPENAI_API_KEY`
- Gemini: `GEMINI_API_KEY` or `VERTEX_AI_API_KEY` or `VERTEX_AI_PROJECT` + `VERTEX_AI_LOCATION`

## Example MCP config (Cursor/Claude)
```json
{
  "mcpServers": [
    {
      "name": "autobyteus-image-audio",
      "command": "uv",
      "args": [
        "--directory",
        "<ABSOLUTE_PATH_TO_WORKSPACE>/autobyteus_mcps/autobyteus-image-audio",
        "run",
        "python",
        "-m",
        "image_audio_mcp.server"
      ],
      "env": {
        "AUTOBYTEUS_AGENT_WORKSPACE": "<ABSOLUTE_PATH_TO_WORKSPACE>",
        "DEFAULT_IMAGE_GENERATION_MODEL": "gpt-image-1.5",
        "DEFAULT_SPEECH_GENERATION_MODEL": "gemini-2.5-flash-tts"
      }
    }
  ]
}
```

## MCP configuration (stdio)
This server runs over stdio by default. The minimal working configuration is:
```json
{
  "mcpServers": [
    {
      "name": "autobyteus-image-audio",
      "command": "python",
      "args": [
        "<ABSOLUTE_PATH_TO_WORKSPACE>/autobyteus_mcps/autobyteus-image-audio/src/image_audio_mcp/server.py"
      ],
      "env": {
        "AUTOBYTEUS_AGENT_WORKSPACE": "<ABSOLUTE_PATH_TO_WORKSPACE>"
      }
    }
  ]
}
```

### Model overrides (env)
If you want to change the default models, set these in the MCP `env`:
```json
{
  "mcpServers": [
    {
      "name": "autobyteus-image-audio",
      "command": "python",
      "args": [
        "<ABSOLUTE_PATH_TO_WORKSPACE>/autobyteus_mcps/autobyteus-image-audio/src/image_audio_mcp/server.py"
      ],
      "env": {
        "AUTOBYTEUS_AGENT_WORKSPACE": "<ABSOLUTE_PATH_TO_WORKSPACE>",
        "DEFAULT_IMAGE_GENERATION_MODEL": "gpt-image-1.5",
        "DEFAULT_IMAGE_EDIT_MODEL": "gpt-image-1.5",
        "DEFAULT_SPEECH_GENERATION_MODEL": "gemini-2.5-flash-tts",
        "OPENAI_API_KEY": "your-key",
        "GEMINI_API_KEY": "your-key"
      }
    }
  ]
}
```

### Choosing model identifiers
Call:
- `list_audio_models` for speech models,
- `list_image_models` for image generation/edit models.

Use one of those `model_identifier` values when setting `DEFAULT_GROUNDING_MODEL` or passing `grounding_model_identifier` to `find_target_coordinates`.

### Notes on configuration
- Use `uv` if you want dependency isolation without manual venv management.
- Set provider credentials in `env` (e.g., `OPENAI_API_KEY`, `GEMINI_API_KEY`).
- Set `DEFAULT_IMAGE_GENERATION_MODEL`, `DEFAULT_IMAGE_EDIT_MODEL`, `DEFAULT_SPEECH_GENERATION_MODEL`, and `DEFAULT_GROUNDING_MODEL` if you want non-default models.

## Notes
- Input image/audio paths can be URLs, data URIs, or local file paths.
- Output paths are resolved using `resolve_safe_path`, limiting writes to the workspace, Downloads, or system temp directories.
