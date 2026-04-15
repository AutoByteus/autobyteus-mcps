# Future-State Runtime Call Stack

## Scenario

- Caller asks the MCP server for its public tool list.

## Future-State Flow

1. `image_audio_mcp.server.create_server()` constructs the FastMCP server.
2. Public tools are registered for:
   - `health_check`
   - `list_audio_models`
   - `list_image_models`
   - `generate_image`
   - `find_target_coordinates`
   - `edit_image`
   - `generate_speech`
3. `list_visual_grounding_models` is not registered as a public tool.
4. A client calling `session.list_tools()` therefore does not see `list_visual_grounding_models`.
5. `find_target_coordinates` still uses `_get_default_grounding_model()` internally only when marker-color detection needs LLM fallback.

## Ownership Notes

- Public MCP surface ownership remains in `autobyteus-image-audio/src/image_audio_mcp/server.py`.
- Public contract verification remains in `autobyteus-image-audio/tests/test_server_local.py`.
- Durable public documentation remains in `autobyteus-image-audio/README.md`.
