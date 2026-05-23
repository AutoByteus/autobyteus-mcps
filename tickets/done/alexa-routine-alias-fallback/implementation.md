# Implementation

Status: Complete

## Solution Sketch

Add `ALEXA_ROUTINE_EVENT_ALIASES` as an optional semicolon-separated config value. Each entry maps an allowlisted routine name to the exact adapter event to send, for example `play_focus_music=textcommand:play focus music`.

`alexa_run_routine` keeps the existing server-side allowlist validation. After validation, `runner.run_routine` checks the alias map:

- alias present: send the configured event value.
- alias absent: preserve existing behavior and send `automation:<routine_name>`.

## Changed Files

- `alexa-mcp/src/alexa_mcp/config.py`
- `alexa-mcp/src/alexa_mcp/runner.py`
- `alexa-mcp/tests/test_runner.py`
- `alexa-mcp/tests/test_server.py`
- `alexa-mcp/README.md`
- `/Users/normy/.codex/config.toml`

## Local Validation

- `uv run --directory alexa-mcp pytest`: 22 passed.
- Direct runner validation for `stop_music` with `ALEXA_ROUTINE_EVENT_ALIASES`: succeeded and sent `textcommand:stop`.
