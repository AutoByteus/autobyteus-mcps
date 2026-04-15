# API / E2E Testing

## Result

- Result: `Pass`

## Validation Run

- Command:
  - `uv run --project autobyteus-image-audio python -m pytest -q autobyteus-image-audio/tests/test_server_local.py`
- Temporary setup used:
  - Created a temporary empty `autobyteus-image-audio/.env.test` file because the repo test harness requires that file to exist even for local non-network tests.
  - Removed the temporary file immediately after the test run.

## Assertions Covered

- Local server tool list excludes `list_visual_grounding_models`.
- Local server tool list still includes `find_target_coordinates`.
- Remaining local server behavior in `test_server_local.py` stays green.
