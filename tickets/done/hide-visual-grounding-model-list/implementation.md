# Implementation

## Scope

- Small public-surface cleanup.

## Plan

- Remove the public `@server.tool` registration for `list_visual_grounding_models`.
- Update local server tests so the tool list explicitly excludes `list_visual_grounding_models`.
- Remove README references that advertise the tool publicly.

## Files Expected To Change

- `autobyteus-image-audio/src/image_audio_mcp/server.py`
- `autobyteus-image-audio/tests/test_server_local.py`
- `autobyteus-image-audio/README.md`
