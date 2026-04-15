# Docs Sync

## Scope

- Ticket: `tts-mcp-voice-parameter`
- Trigger Stage: `9`
- Workflow state source: `tickets/done/tts-mcp-voice-parameter/workflow-state.md`

## Why Docs Were Updated

- Summary: The durable `tts-mcp` README needed to match the final public `speak` contract after the ticket's re-entry rounds completed.
- Why this change matters to long-lived project understanding:
  - Future readers need one truthful place that explains the public `language`, `voice`, and `temperature` inputs, the deterministic MLX default, and the route-specific Chinese default voice behavior without reconstructing it from ticket history or tests.

## Long-Lived Docs Reviewed

| Doc Path | Why It Was Reviewed | Result (`Updated`/`No change`/`Needs follow-up`) | Notes |
| --- | --- | --- | --- |
| `tts-mcp/README.md` | It is the canonical long-lived doc for the public MCP `speak` contract, runtime defaults, and operator configuration. | `Updated` | Removed stale Chinese voice examples, added temperature guidance, and documented the deterministic MLX default. |

## Docs Updated

| Doc Path | Type Of Update | What Was Added / Changed | Why |
| --- | --- | --- | --- |
| `tts-mcp/README.md` | Public API + runtime behavior sync | Replaced stale Chinese voice examples with truthful tested examples, documented the optional public `temperature` input, added `MLX_TTS_DEFAULT_TEMPERATURE`, and recorded Chinese default-voice/default-temperature behavior. | The README must match the final implemented and validated behavior. |

## Durable Design / Runtime Knowledge Promoted

| Topic | What Future Readers Need To Understand | Source Ticket Artifact(s) | Target Long-Lived Doc |
| --- | --- | --- | --- |
| Public `speak` contract | The stable public API now uses `language`, optional `voice`, and optional MLX-only `temperature` with deterministic default `0.0`. | `requirements.md`, `implementation.md`, `api-e2e-testing.md` | `tts-mcp/README.md` |
| Chinese MLX routing defaults | Chinese auto-routes to `qwen_customvoice_hq`, defaults to `Vivian` when `voice` is omitted, and keeps deterministic sampling when `temperature` is omitted. | `future-state-runtime-call-stack.md`, `api-e2e-testing.md` | `tts-mcp/README.md` |
| Truthful voice guidance | Route-specific examples must stay truthful to the installed/runtime model inventory instead of advertising unsupported names. | `investigation-notes.md`, `api-e2e-testing.md` | `tts-mcp/README.md` |

## Removed / Replaced Components Recorded

| Old Component / Path / Concept | What Replaced It | Where The New Truth Is Documented |
| --- | --- | --- |
| Public `language_code` wording | Concise public `language` field | `tts-mcp/README.md` |
| Stale Chinese examples `Chelsie`, `Ethan` | Truthful tested examples `Vivian`, `eric`, `serena` | `tts-mcp/README.md` |
| Implicit/undocumented MLX sampling default | Explicit public and env-backed deterministic default `temperature = 0.0` | `tts-mcp/README.md` |

## Final Result

- Result: `Updated`
- If `Blocked` because earlier-stage work is required, classification: `N/A`
- Required return path or unblock condition: `N/A`
- Follow-up needed:
  - Revisit the README voice examples if a future `mlx_audio` upgrade changes the installed Qwen CustomVoice speaker inventory.
