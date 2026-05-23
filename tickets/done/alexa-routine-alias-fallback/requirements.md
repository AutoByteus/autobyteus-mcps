# Requirements

Status: Design-ready

## Problem

Alexa authentication and generic text commands work after refreshing the token, but `alexa_run_routine` fails for allowlisted routine names such as `play_focus_music`, `stop_music`, and `plug_on` because the upstream Alexa routines endpoint returns no routine metadata for the current account/session.

## Scope

- Preserve existing allowlist enforcement for routine names.
- Allow selected allowlisted routine names to map to explicit Alexa adapter event values.
- Configure music-oriented aliases for `play_focus_music` and `stop_music`.
- Keep direct Alexa routine execution as the default for unaliased routine names.

## Acceptance Criteria

- `play_focus_music` can be handled without relying on the Alexa routines endpoint.
- `stop_music` can be handled without relying on the Alexa routines endpoint.
- Unaliased routines still use `automation:<routine_name>`.
- Invalid routine names remain rejected by the existing MCP allowlist.
- Tests cover alias command construction.
