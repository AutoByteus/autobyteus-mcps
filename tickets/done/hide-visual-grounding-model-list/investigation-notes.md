# Investigation Notes

## Scope

- Small public-surface cleanup in `autobyteus-image-audio`.

## Findings

- `list_visual_grounding_models` is still registered as a public MCP tool in `autobyteus-image-audio/src/image_audio_mcp/server.py`.
- The public README still lists and documents `list_visual_grounding_models`.
- `find_target_coordinates` still uses `_get_default_grounding_model()` internally for marker-fallback logic, so only the public listing should be removed.
- `autobyteus-image-audio/tests/test_server_local.py` already contains a local tool-list test and one direct test for `list_visual_grounding_models`.

## Decision

- Remove only the public tool registration and public docs references.
- Keep internal default-grounding-model logic intact.
