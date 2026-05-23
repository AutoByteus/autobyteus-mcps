# Investigation Notes

Status: Complete

## Evidence

- `alexa_get_device_status` succeeds after the refreshed token, proving authentication and device lookup work.
- `alexa_music_control(action="play", query="focus music")` succeeds by sending `textcommand:play focus music`.
- `alexa_run_routine("play_focus_music")`, `alexa_run_routine("stop_music")`, and `alexa_run_routine("plug_on")` all fail with `ERROR: no such utterance ... in Alexa routines`.
- Direct checks of `/api/behaviors/v2/automations?limit=200` return HTTP 200 with an empty body for the current cookie/session.
- The vendored `alexa_remote_control.sh` routine path depends on that endpoint and cannot resolve routine IDs when the body is empty.

## Conclusion

The failure is below the MCP runner and specific to Alexa routine metadata lookup. Text-command execution still works. A bounded alias from allowlisted routine name to explicit adapter event is the smallest reliable local fix for music routines.
