# API / E2E Testing

Status: Pass

## Executed Validation

```bash
uv run --directory alexa-mcp pytest
```

Result: `22 passed`.

```bash
AMAZON=amazon.de \
ALEXA=alexa.amazon.de \
ALEXA_REFRESH_TOKEN_FILE=/Users/normy/autobyteus_org/autobyteus_mcps/alexa-mcp/.secrets/refresh_token \
ALEXA_COMMAND=/Users/normy/autobyteus_org/autobyteus_mcps/alexa-mcp/scripts/alexa_adapter.sh \
ALEXA_ALLOWED_ROUTINES=plug_on,plug_off,play_focus_music,stop_music \
ALEXA_ALLOWED_MUSIC_ACTIONS=play,stop \
ALEXA_DEFAULT_DEVICE='nogrethumphreys Echo Dot' \
ALEXA_ROUTINE_EVENT_ALIASES='play_focus_music=textcommand:play focus music;stop_music=textcommand:stop' \
uv run --directory alexa-mcp python - <<'PY'
from alexa_mcp.config import load_settings
from alexa_mcp.runner import run_routine
settings = load_settings()
print(run_routine(settings, 'stop_music'))
PY
```

Result: `ok=True`, command sent `textcommand:stop`.

## Not Executed

`play_focus_music` live command was not re-run during validation to avoid unexpectedly starting music during code review. The same alias path is covered by unit test command construction and `stop_music` live execution.
