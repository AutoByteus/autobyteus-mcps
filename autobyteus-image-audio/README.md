# Autobyteus Image + Audio + Video MCP / CLI

Autobyteus Image + Audio + Video exposes image, speech, video, model-listing, and UI-coordinate capabilities in two ways. The package name stays `autobyteus-image-audio` for existing MCP/CLI configurations; video is exposed through explicit `generate_video` / `list_video_models` tools and `generate-video` / `list-video-models` CLI commands.

- a task-oriented command-line interface for users and coding agents;
- the existing Model Context Protocol (MCP) server for MCP clients.

Both public surfaces delegate to the same `image_audio_mcp.services` implementation, so file safety, model defaults, provider calls, and result payloads stay consistent.

## Command-line usage

Use the repo-level wrapper from any current working directory:

```bash
/ABS/PATH/TO/REPO/cli/autobyteus-image-audio health-check
```

The wrapper runs the project CLI through `uv --directory ... run --frozen` and lets `uv` prepare the project runtime automatically. Callers do **not** need to run `uv sync`, activate `.venv`, install dependencies manually, or know where the project virtual environment lives.

### Output format

Normal command output is JSON on stdout:

```json
{"ok":true,"command":"health-check","result":{"status":"ok"}}
```

Failures exit non-zero and print a JSON envelope on stdout:

```json
{"ok":false,"command":"generate-image","error_type":"FileNotFoundError","error_message":"..."}
```

`--help` prints human-readable help text instead of a JSON envelope.

### CLI commands

```bash
# Health/default model status
/ABS/PATH/TO/REPO/cli/autobyteus-image-audio health-check

# Model catalogs
/ABS/PATH/TO/REPO/cli/autobyteus-image-audio list-image-models
/ABS/PATH/TO/REPO/cli/autobyteus-image-audio list-audio-models
/ABS/PATH/TO/REPO/cli/autobyteus-image-audio list-video-models

# Generate an image
/ABS/PATH/TO/REPO/cli/autobyteus-image-audio generate-image \
  --prompt "A friendly robot reading a book" \
  --output-file-path robot.png

# Generate an image with a reference image and per-call settings
/ABS/PATH/TO/REPO/cli/autobyteus-image-audio generate-image \
  --prompt "Restyle this as watercolor" \
  --input-image reference.png \
  --generation-config '{"size":"1024x1024","image_config":{"aspect_ratio":"16:9"}}' \
  --output-file-path watercolor.png

# Generate an image with reusable generation_config JSON from a file
/ABS/PATH/TO/REPO/cli/autobyteus-image-audio generate-image \
  --prompt "Restyle this as watercolor" \
  --input-image reference.png \
  --generation-config-file generation_config.json \
  --output-file-path watercolor.png

# Edit an image; repeat --input-image for multiple inputs
/ABS/PATH/TO/REPO/cli/autobyteus-image-audio edit-image \
  --prompt "Replace the sky with a sunset" \
  --input-image photo.png \
  --mask-image mask.png \
  --output-file-path edited.png

# Generate speech
/ABS/PATH/TO/REPO/cli/autobyteus-image-audio generate-speech \
  --prompt "Hello from Autobyteus." \
  --output-file-path hello.wav

# Generate video with optional media references
/ABS/PATH/TO/REPO/cli/autobyteus-image-audio generate-video \
  --prompt "A calm cinematic shot of a friendly robot waving" \
  --input-image robot-reference.png \
  --input-audio narration.wav \
  --input-video previous-clip.mp4 \
  --output-file-path robot.mp4

# Multi-speaker speech with MCP-shaped generation_config JSON
/ABS/PATH/TO/REPO/cli/autobyteus-image-audio generate-speech \
  --prompt "Joe: Hi.\nJane: Hello." \
  --generation-config '{"mode":"multi-speaker","speaker_mapping":{"Joe":"Kore","Jane":"Puck"}}' \
  --output-file-path dialog.wav

# Find a UI target coordinate
/ABS/PATH/TO/REPO/cli/autobyteus-image-audio find-target-coordinates \
  --image screenshot.png \
  --target "Submit button" \
  --marked-image-output-path marked.png
```

Model-specific generation settings can be passed in the same nested shape as the MCP `generation_config` argument:

```bash
--generation-config '{"mode":"multi-speaker","speaker_mapping":{"Joe":"Kore","Jane":"Puck"}}'
```

For larger configs or human-edited configs, write the object to a file and pass:

```bash
--generation-config-file generation_config.json
```

The CLI intentionally keeps model-specific configuration in the same nested object shape as MCP. It does not expose split `--config`, `--speaker`, or `--voice` aliases; multi-speaker speech should be expressed with `generation_config.speaker_mapping`.

The CLI intentionally does not require a generic `call-tool` command for normal use.

### CLI help

```bash
/ABS/PATH/TO/REPO/cli/autobyteus-image-audio --help
/ABS/PATH/TO/REPO/cli/autobyteus-image-audio generate-image --help
```

You may also run the project console script directly through `uv`:

```bash
uv --directory /ABS/PATH/TO/REPO/autobyteus-image-audio run --frozen autobyteus-image-audio --help
```

## MCP tools

Public MCP tools:

- `health_check`: Basic status + default model identifiers.
- `list_audio_models`: List audio models and their `generation_config` JSON schemas.
- `list_image_models`: List image models and their `generation_config` JSON schemas.
- `list_video_models`: List video models and their `generation_config` JSON schemas.
- `generate_image`: Text-to-image or image-to-image generation.
- `edit_image`: Prompt-based image editing with optional mask.
- `generate_speech`: Text-to-speech (TTS).
- `generate_video`: Text-to-video generation with optional image, audio, and video references.
- `find_target_coordinates`: Standard coordinate finder for GUI automation using the edit-marker pipeline.

Direct VLM grounding and public visual-grounding model listing remain internal and are not exposed as public MCP tools.

## Environment variables

- `IMAGE_AUDIO_MCP_NAME`: Override MCP server name (default `autobyteus-image-audio`).
- `IMAGE_AUDIO_MCP_INSTRUCTIONS`: Override MCP server instructions.
- `AUTOBYTEUS_AGENT_WORKSPACE`: Base path for relative input/output paths.
- `DEFAULT_IMAGE_GENERATION_MODEL`: Override image generation model.
- `DEFAULT_IMAGE_EDIT_MODEL`: Override image edit model.
- `DEFAULT_SPEECH_GENERATION_MODEL`: Override TTS model.
- `DEFAULT_VIDEO_GENERATION_MODEL`: Override video generation model (default `gemini-omni-app-rpa`).
- `DEFAULT_GROUNDING_MODEL`: Override fallback grounding LLM for coordinate marker detection.
- `GROUNDING_RELATIVE_COORDINATE_MAX`: Override relative coordinate max for fallback grounding parsing.

Provider credentials may be required depending on configured models:

- OpenAI: `OPENAI_API_KEY`
- Gemini: `GEMINI_API_KEY`
- Vertex AI: `VERTEX_AI_API_KEY` or `VERTEX_AI_PROJECT` + `VERTEX_AI_LOCATION`
- Autobyteus remote: `AUTOBYTEUS_API_KEY` and `AUTOBYTEUS_LLM_SERVER_HOSTS` when using remote-backed models

## Path safety

Input image, audio, and video paths can be URLs, data URIs, or local paths. Local paths are resolved with `resolve_safe_path` against `AUTOBYTEUS_AGENT_WORKSPACE` when set, otherwise the current working directory. Output paths use the same safe resolver and are constrained to allowed workspace, Downloads, or temp locations.

File-producing commands require `--output-file-path`.

## Running the MCP server

Recommended isolated launch with `uv`:

```bash
uv --directory /ABS/PATH/TO/REPO/autobyteus-image-audio run --frozen autobyteus-image-audio-server
```

Module launch remains supported:

```bash
uv --directory /ABS/PATH/TO/REPO/autobyteus-image-audio run --frozen python -m image_audio_mcp.server
```

## Example MCP config (Cursor/Claude)

```json
{
  "mcpServers": [
    {
      "name": "autobyteus-image-audio",
      "command": "uv",
      "args": [
        "--directory",
        "/ABS/PATH/TO/REPO/autobyteus-image-audio",
        "run",
        "--frozen",
        "autobyteus-image-audio-server"
      ],
      "env": {
        "AUTOBYTEUS_AGENT_WORKSPACE": "/ABS/PATH/TO/WORKSPACE",
        "DEFAULT_IMAGE_GENERATION_MODEL": "gpt-image-1.5",
        "DEFAULT_IMAGE_EDIT_MODEL": "gpt-image-1.5",
        "DEFAULT_SPEECH_GENERATION_MODEL": "gemini-2.5-flash-tts",
        "DEFAULT_VIDEO_GENERATION_MODEL": "gemini-omni-app-rpa"
      }
    }
  ]
}
```

## Local validation

Local/mock tests do not require `.env.test`:

```bash
uv --directory /ABS/PATH/TO/REPO/autobyteus-image-audio run --frozen --extra test pytest
```

Remote/provider tests skip unless the required credential/model environment variables are configured.
Set `RUN_REMOTE_IMAGE_AUDIO_TESTS=1` to opt in to real provider tests.
