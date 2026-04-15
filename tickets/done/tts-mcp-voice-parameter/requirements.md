# Requirements

## Status

- Current Status: `Refined`
- Ticket: `tts-mcp-voice-parameter`
- Scope: `Small`

## Problem Statement

The branch already fixes the first half of the Chinese routing problem by moving named-speaker Chinese requests onto the speaker-capable `mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16` path and injecting a deterministic default speaker when `voice` is omitted. Investigation found two remaining contract gaps:

- the public Chinese speaker examples still advertise unsupported names such as `Ethan`, even though the installed CustomVoice runtime actually supports ids such as `vivian`, `eric`, and `serena`
- the MLX runtime is still left on sampling defaults unless the caller manually overrides it, so repeated outputs can drift in tone/prosody even with the same speaker; investigation confirmed that the installed runtime becomes deterministic when `temperature=0`, and no seed control is exposed in the installed TTS runtime

The next fix must make the MCP-owned default deterministic and the public guidance truthful without regressing the existing English/Kokoro route or the concise public `language` API.

## User Intent

Keep the public `speak` API intuitive, but make Chinese voice behavior reliable:

- if the caller omits `voice` for Chinese, MCP should use a deterministic default voice rather than drifting between speakers
- if the caller provides a named Chinese `voice`, MCP should route to a speaker-capable model that actually supports named speakers, or fail clearly instead of silently ignoring the request
- if the caller omits `temperature`, MCP should use a deterministic default (`0.0`) instead of leaving MLX sampling unconstrained
- if the caller explicitly provides `temperature`, MCP should honor that override on MLX routes

## In-Scope Use Cases

- `UC-001` Agent calls `speak(text=..., language="zh")` with no `voice` and gets a deterministic Chinese speaker choice across repeated calls.
- `UC-002` Agent calls `speak(text=..., language="zh", voice="Vivian")` and the Chinese route uses a model variant that actually supports named speakers.
- `UC-003` Agent calls `speak(text=..., language="en", voice="af_heart")` and the existing English/Kokoro route still behaves as before.
- `UC-004` MCP refuses or clearly errors when a caller requests a named Chinese `voice` on a pinned MLX model that does not support named speakers.
- `UC-005` Agent calls `speak(text=..., language="zh")` without a `temperature` override and gets deterministic repeated output because MCP defaults MLX temperature to `0.0`.
- `UC-006` Agent calls `speak(text=..., language="zh", voice="eric", temperature=0.4)` and MCP forwards the explicit temperature override instead of forcing the default.

## Functional Requirements

- `R-001` The public `speak` MCP tool must continue to accept an optional `voice` input.
- `R-002` The public MCP tool must continue to use concise public `language`, not public `language_code`.
- `R-003` The public `speak` MCP tool must accept an optional `temperature` input.
- `R-004` When the caller omits `temperature` on an MLX route, MCP must use a deterministic default temperature of `0.0`.
- `R-005` For Chinese requests on Apple Silicon MLX routes, omitting `voice` must produce a deterministic default speaker choice instead of relying on an unconstrained backend default.
- `R-006` For Chinese requests with a named `voice`, MCP must route to a speaker-capable Qwen model variant that exposes predefined speakers.
- `R-007` MCP must not silently treat a named Chinese `voice` as supported when the selected MLX model has no speaker table.
- `R-008` The MCP schema must describe `voice` examples truthfully enough that agents are not misled into thinking unsupported Chinese speaker ids such as `Ethan` are valid on the routed CustomVoice model.
- `R-009` The MCP schema must describe `temperature` truthfully enough that callers understand the deterministic default and the MLX-specific override behavior.
- `R-010` Existing English/Kokoro behavior, including `language="en"` plus `voice="af_heart"`, must remain unchanged.
- `R-011` Existing internal runner/routing naming may continue to use `language_code` below the public boundary.
- `R-012` Durable Stage 7 executable validation must cover:
  - public schema exposure of `temperature`
  - default MLX temperature propagation at `0.0`
  - explicit MLX temperature override propagation
  - deterministic repeated Chinese no-voice behavior
  - explicit Chinese named-voice behavior on a speaker-capable model
  - explicit English/Kokoro named-voice behavior
  - incompatible pinned-model behavior for named Chinese voices

## Non-Goals

- Do not add dynamic runtime enumeration of every available voice in the MCP schema.
- Do not redesign the entire backend selection architecture.
- Do not change English/Kokoro defaults unless required for consistency with the Chinese fix.
- Do not add a synthetic seed feature that the installed MLX TTS runtime does not expose.

## Acceptance Criteria

- `AC-001` `session.list_tools()` for `speak` exposes `language`, `voice`, and `temperature`.
- `AC-002` The `voice` schema description/examples remain route-aware and do not overclaim unsupported named-speaker behavior.
- `AC-003` The `temperature` schema/behavior clearly defaults omitted MLX temperature to `0.0`.
- `AC-004` Repeated Chinese `speak(..., language="zh")` calls resolve to a deterministic default voice path instead of backend drift.
- `AC-005` Repeated Chinese `speak(..., language="zh", voice="Vivian")` calls use a speaker-capable Qwen model variant rather than the current Base variant.
- `AC-006` Explicit `temperature` overrides are forwarded to the MLX command path.
- `AC-007` If the active/pinned MLX model lacks predefined speakers, Chinese named-voice requests fail clearly instead of silently succeeding on an incompatible model.
- `AC-008` Existing English/Kokoro `speak(..., language="en", voice="af_heart")` executable validation still passes.
- `AC-009` Updated focused tests pass under `uv run --extra test python -m pytest`.

## Requirement To Use-Case Coverage

| Requirement ID | Covered Use Case(s) |
| --- | --- |
| `R-001` | `UC-001`, `UC-002`, `UC-003`, `UC-004`, `UC-006` |
| `R-002` | `UC-001`, `UC-002`, `UC-003`, `UC-004`, `UC-005`, `UC-006` |
| `R-003` | `UC-005`, `UC-006` |
| `R-004` | `UC-005` |
| `R-005` | `UC-001`, `UC-005` |
| `R-006` | `UC-002`, `UC-006` |
| `R-007` | `UC-004` |
| `R-008` | `UC-002`, `UC-004`, `UC-006` |
| `R-009` | `UC-005`, `UC-006` |
| `R-010` | `UC-003` |
| `R-011` | `UC-001`, `UC-002`, `UC-003`, `UC-004`, `UC-005`, `UC-006` |
| `R-012` | `UC-001`, `UC-002`, `UC-003`, `UC-004`, `UC-005`, `UC-006` |

## Acceptance Criteria To Scenario Intent

| Acceptance Criteria ID | Validation Intent |
| --- | --- |
| `AC-001` | Public schema inspection through MCP tool listing |
| `AC-002` | Public voice wording/examples align with the routed capability |
| `AC-003` | Public/default MLX temperature behavior is explicit and testable |
| `AC-004` | Repeated Chinese no-voice routing/command validation |
| `AC-005` | Explicit Chinese named-voice routing/command validation |
| `AC-006` | Explicit MLX temperature override validation |
| `AC-007` | Negative test for incompatible pinned Qwen Base + named voice |
| `AC-008` | English/Kokoro regression validation |
| `AC-009` | Focused repo validation suite remains green |

## Constraints

- The current Chinese auto-route uses `mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16`, and investigation confirmed that model has no predefined speaker table.
- The routed Chinese path already moved to `mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16`, but the curated public examples must match that runtime's actual supported speaker ids.
- XTTS and Chatterbox still reject named `voice`.
- Dynamic voice discovery remains out of scope; examples must stay curated and tested.
- The fix must preserve the public `language` API and avoid silently ignoring incompatible named-voice requests.
- The installed MLX TTS runtime exposes `temperature`, `top_p`, and `top_k`, but investigation found no seed control.

## Assumptions

- The `mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16` model remains the correct speaker-capable target for named Chinese voices.
- A deterministic Chinese default speaker can be chosen explicitly by MCP without needing backend auto-selection.
- A deterministic omitted-temperature default of `0.0` is acceptable for MLX routes unless the caller explicitly overrides it.

## Open Questions / Risks

- The exact default Chinese speaker choice must be pinned deliberately; otherwise omitted-voice behavior remains ambiguous.
- The curated Chinese speaker examples must stay synchronized with the actual installed CustomVoice runtime.
- Real speaker-stability validation should validate command intent and repeated-output determinism rather than relying only on WAV existence.
