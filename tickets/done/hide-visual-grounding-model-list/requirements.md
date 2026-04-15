# Requirements

## Status

- Status: `Refined`

## Summary

- Hide the public `list_visual_grounding_models` MCP tool from `autobyteus-image-audio`.

## User Intent

- The image-audio MCP should not publicly expose the list of visual grounding models.
- Internal grounding behavior for `find_target_coordinates` should continue to work.

## Acceptance Criteria

- `list_visual_grounding_models` is no longer registered as a public MCP tool.
- Public README/docs no longer advertise `list_visual_grounding_models` as an available tool.
- Existing public tools such as `find_target_coordinates` still remain available.
- Local server tests pass for the changed public tool list.

## Non-Goals

- Do not remove internal grounding-model fallback logic used by `find_target_coordinates`.
- Do not change the rest of the public tool inventory.
