# API, E2E, And Executable Validation Report

## Validation Round Meta

- Requirements Doc: `/Users/normy/autobyteus_org/autobyteus_mcps-image-audio-mcp-cli/tickets/in-progress/image-audio-mcp-cli/requirements.md`
- Investigation Notes: `/Users/normy/autobyteus_org/autobyteus_mcps-image-audio-mcp-cli/tickets/in-progress/image-audio-mcp-cli/investigation-notes.md`
- Design Spec: `/Users/normy/autobyteus_org/autobyteus_mcps-image-audio-mcp-cli/tickets/in-progress/image-audio-mcp-cli/design-spec.md`
- Design Review Report: `/Users/normy/autobyteus_org/autobyteus_mcps-image-audio-mcp-cli/tickets/in-progress/image-audio-mcp-cli/design-review-report.md`
- Implementation Handoff: `/Users/normy/autobyteus_org/autobyteus_mcps-image-audio-mcp-cli/tickets/in-progress/image-audio-mcp-cli/implementation-handoff.md`
- Review Report: `/Users/normy/autobyteus_org/autobyteus_mcps-image-audio-mcp-cli/tickets/in-progress/image-audio-mcp-cli/review-report.md`
- Current Validation Round: `2`
- Trigger: User asked whether real provider-backed CLI CMD end-to-end execution had been tested; credentialed CLI/provider addendum was run.
- Prior Round Reviewed: `1`
- Latest Authoritative Round: `2`

## Round History

| Round | Trigger | Prior Unresolved Failures Rechecked | New Failures Found | Result | Latest Authoritative | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Code review round 2 pass for `image-audio-mcp-cli` | N/A | None | Pass | No | Covered wrapper first-run behavior, CLI contract, MCP compatibility, durable tests, docs/readiness checks, and remote-test gating. |
| 2 | User-requested credentialed CLI/provider addendum | N/A | None classified as implementation failures | Pass | Yes | Real wrapper CLI commands succeeded for `generate-image`, `edit-image`, `generate-speech`, and `find-target-coordinates` using available credentials with OpenAI-backed model overrides; credential-gated MCP integration pytest passed. Current RPA default provider config was also probed and recorded as an environment/provider caveat. |

## Validation Basis

Validation was derived from the approved requirements, reviewed design, implementation handoff, and code review report. Key acceptance surfaces were:

- Additive task-oriented CLI over `autobyteus-image-audio` while preserving existing MCP tools and server entrypoints.
- Wrapper-hidden `uv --directory ... run --frozen` execution from arbitrary current working directories, including first-run `.venv` creation/sync behavior.
- JSON stdout envelopes and non-zero structured failures for usage/runtime errors.
- Repeatable `--config KEY=VALUE` with dot notation and JSON scalar parsing.
- Paired `--speaker NAME --voice VOICE` multi-speaker syntax and conflict/mismatch validation.
- Safe-path input/output behavior via existing service boundary.
- Local/mock tests running without `.env.test`, with remote/provider tests skipped unless explicitly enabled.
- No stale `workflow-state.md`, broad multi-MCP CLI rollout, raw generic MCP `call-tool` UX, or old raw JSON config option retained in tracked implementation/docs/tests.

## Compatibility / Legacy Scope Check

- Reviewed requirements/design introduce, tolerate, or ambiguously describe backward compatibility in scope: `No`
  - Existing MCP server launch commands and tool names are intentionally preserved by requirement; this is not legacy-retention drift.
- Compatibility-only or legacy-retention behavior observed in implementation: `No`
- Durable validation added or retained only for compatibility-only behavior: `No`
- If compatibility-related invalid scope was observed, reroute classification used: `N/A`
- Upstream recipient notified: `N/A`

## Validation Surfaces / Modes

- Durable repository tests: full `uv run --frozen --extra test pytest -q` suite.
- Project compile check: `uv run --frozen python -m compileall -q src`.
- CLI wrapper black-box process checks from `/tmp`.
- First-run wrapper validation with project `.venv` temporarily absent and restored afterward.
- Direct underlying `uv --directory ... run --frozen autobyteus-image-audio --help` smoke check.
- CLI usage/runtime error black-box process checks with parsed JSON stdout.
- In-memory MCP client validation against `create_server()` for tool inventory, `health_check`, and `generate_speech` schema details.
- Documentation and cleanup checks using tracked-file `git grep` / `find`.

## Platform / Runtime Targets

- Worktree: `/Users/normy/autobyteus_org/autobyteus_mcps-image-audio-mcp-cli`
- Branch: `codex/image-audio-mcp-cli`
- Host timezone/date context: Europe/Berlin, 2026-05-05
- Python target exercised through project `uv` environment: project requires `>=3.11,<3.12`.
- `uv` version: `uv 0.10.2 (Homebrew 2026-02-10)`.
- Remote/provider tests: round 1 left provider tests skipped because `RUN_REMOTE_IMAGE_AUDIO_TESTS` was unset. Round 2 enabled credentialed checks with explicit model overrides: `DEFAULT_IMAGE_GENERATION_MODEL=gpt-image-1.5`, `DEFAULT_IMAGE_EDIT_MODEL=gpt-image-1.5`, and `DEFAULT_SPEECH_GENERATION_MODEL=gpt-4o-mini-tts`. The project `autobyteus-image-audio/.env.test` file was absent; credentials/config were inherited from the Codex process environment without printing secrets.

## Lifecycle / Upgrade / Restart / Migration Checks

- No application upgrade/migration path is in scope.
- Process/lifecycle check performed for the repo wrapper: the existing `.venv` was temporarily moved away, `cli/autobyteus-image-audio health-check` was invoked from `/tmp`, `uv run --frozen` created a fresh project `.venv` and console script, the command returned JSON success, and the original `.venv` was restored.

Evidence:

```text
pre_existing_venv=true
venv_absent_before_wrapper=true
wrapper_exit=0
elapsed_seconds=11
venv_created_after_wrapper=true
console_script_created=true
stdout_ok=True command=health-check status=ok
restored_original_venv=true
```

## Coverage Matrix

| Scenario ID | Requirement / Acceptance Coverage | Validation Method | Result | Evidence |
| --- | --- | --- | --- | --- |
| VAL-001 | AC-001, AC-002, REQ-019: fresh ticket/worktree, no stale workflow state | `git worktree list`, stale branch/worktree grep, `find tickets/... -name workflow-state.md` | Pass | Worktree list contains `codex/image-audio-mcp-cli`; no `codex/mcp-cli-tools` worktree/local branch; no `workflow-state.md` found. |
| VAL-002 | REQ-002, REQ-004, REQ-015, AC-003: wrapper from unrelated cwd and first-run env sync | Temporarily removed `.venv`; ran wrapper `health-check` from `/tmp` | Pass | Fresh `.venv` and console script created; JSON success returned; original `.venv` restored. |
| VAL-003 | REQ-003, UC-007: console scripts preserved/added | `importlib.metadata.entry_points` check through `uv run --frozen` | Pass | `autobyteus-image-audio => image_audio_mcp.cli:main`; `autobyteus-image-audio-server => image_audio_mcp.server:main`. |
| VAL-004 | REQ-005, REQ-013, AC-004, AC-013: task-oriented help/docs | Wrapper `--help`, underlying `uv --directory ... --help`, all subcommand `--help` checks | Pass | Help includes env/path/provider notes, auto-prepares wording, task commands, `--config`, `--speaker`, `--voice`; no generic call-tool UX in CLI help. |
| VAL-005 | REQ-006, UC-001, UC-002, AC-005: JSON success envelopes for safe commands | Wrapper `health-check`, `list-image-models`, `list-audio-models` from `/tmp` | Pass | `health-check` success result keys present; image models count `17`; audio models count `12`; model entries include identifier/schema/default config keys. |
| VAL-006 | REQ-006, REQ-007, REQ-010, REQ-021, AC-014: structured usage failures | Wrapper process checks for speaker/voice mismatch, old raw option rejection, parent-child config conflict, missing output, empty/duplicate config key, speaker mapping conflict | Pass | All returned exit `2`, JSON `UsageError` envelope on stdout, and concise stderr diagnostic. |
| VAL-007 | REQ-008, REQ-009: safe path handling and clear input errors | Wrapper `generate-image` with `AUTOBYTEUS_AGENT_WORKSPACE` temp dir and missing `--input-image missing.png` | Pass | Exit `1`, JSON `FileNotFoundError`, resolved path under workspace; failure occurred before provider call. |
| VAL-008 | REQ-011, REQ-012, REQ-014, UC-003..UC-006, AC-006, AC-007 | Full durable local pytest suite | Pass | `.........ss.......... [100%]`; `19 passed, 2 skipped`. Durable tests cover service mocked clients, cleanup, CLI envelopes, config parsing, speaker mapping, and coordinate CLI mapping. |
| VAL-009 | REQ-001, REQ-016, UC-007, AC-008: MCP compatibility | Full pytest plus in-memory MCP client probe | Pass | Tool names exactly `health_check`, `list_audio_models`, `list_image_models`, `generate_image`, `edit_image`, `generate_speech`, `find_target_coordinates`; hidden grounding tools absent; `health_check` call succeeded; speech schema includes prompt/config descriptions. |
| VAL-010 | REQ-017, AC-009: clean local/mock tests without `.env.test`; remote skip | Full pytest with current env where `RUN_REMOTE_IMAGE_AUDIO_TESTS` unset | Pass | `19 passed, 2 skipped`; skipped tests are remote/provider generation/speech. |
| VAL-011 | REQ-018, AC-010, AC-011, AC-012: docs and scope | `git grep` in tracked README/DESIGN/source/tests | Pass | README/DESIGN include wrapper examples, `--config` dot notation, speaker/voice pairs, `uv --directory` implementation note, MCP launch docs; tracked source/docs/tests do not contain old `generation-config-json` / `generation-config-file`. |
| VAL-012 | General implementation readiness | `compileall`, `git diff --check` | Pass | Both checks passed. |
| VAL-013 | User-requested real CLI CMD/provider E2E for file-producing commands | Wrapper commands from `/tmp` with `AUTOBYTEUS_AGENT_WORKSPACE` temp dirs and available credentials | Pass | `generate-image` with `gpt-image-1.5` wrote a 45,480-byte PNG; `edit-image` with `gpt-image-1.5` wrote a 49,246-byte PNG; `generate-speech` with `gpt-4o-mini-tts` wrote a 91,392-byte MP3; `find-target-coordinates` with `gpt-image-1.5` returned pixel coordinates `{x: 200, y: 94}` and wrote a 104,675-byte marked image. |
| VAL-014 | Credential-gated MCP integration tests with real providers | `RUN_REMOTE_IMAGE_AUDIO_TESTS=1 DEFAULT_IMAGE_GENERATION_MODEL=gpt-image-1.5 DEFAULT_SPEECH_GENERATION_MODEL=gpt-4o-mini-tts uv run --frozen --extra test pytest -q tests/test_integration.py` | Pass | `.. [100%]`; both remote MCP integration tests passed. |
| VAL-015 | Current inherited RPA default provider smoke | Wrapper `generate-image`/`generate-speech` with inherited `nano-banana-pro-app-rpa@localhost:51739` and `gemini-3.1-flash-tts-rpa@localhost:51739` defaults | Environment/provider caveat | Current default image command returned structured `RuntimeError` from the provider (`HTTP 500`, disabled Create image button). Current default speech command did not complete and was killed after 166.9s. OpenAI-backed model overrides passed, so this is recorded as provider/runtime configuration health rather than an implementation failure. |

## Test Scope

In scope and exercised:

- CLI wrapper process behavior from outside the project directory.
- User-requested credentialed real CLI provider commands for `generate-image`, `edit-image`, `generate-speech`, and `find-target-coordinates` using available environment credentials and explicit OpenAI-backed model overrides.
- Credential-gated MCP integration pytest with real provider calls using OpenAI-backed model overrides.
- First-run automatic project environment creation/sync through wrapper-owned `uv run --frozen`.
- JSON envelopes for successful health/model-list commands and failure paths.
- Dynamic config parsing and conflict cases through durable tests and black-box usage-error commands.
- Multi-speaker paired syntax through durable tests and black-box mismatch/conflict checks.
- Safe path missing-input error behavior through black-box CLI.
- MCP tool inventory/schema/call compatibility through durable tests and an explicit in-memory MCP client probe.
- Documentation and stale-artifact cleanup checks for tracked files.

Out of scope or intentionally not executed:

- Exhaustive provider matrix validation. Round 2 covered OpenAI-backed image/edit/speech models with available credentials; it did not exhaustively validate every Autobyteus/RPA/Gemini provider variant.
- Browser/UI testing; no browser surface is part of this ticket.
- Installer/updater/migration validation; no installer/updater/migration behavior is part of this ticket.

## Validation Setup / Environment

Commands were run from `/Users/normy/autobyteus_org/autobyteus_mcps-image-audio-mcp-cli` unless noted.

Representative commands:

```bash
cd /Users/normy/autobyteus_org/autobyteus_mcps-image-audio-mcp-cli/autobyteus-image-audio
uv --version
uv run --frozen python -m compileall -q src
uv run --frozen --extra test pytest -q

cd /Users/normy/autobyteus_org/autobyteus_mcps-image-audio-mcp-cli
git diff --check
find tickets/in-progress/image-audio-mcp-cli -name workflow-state.md -print
git worktree list

cd /tmp
/Users/normy/autobyteus_org/autobyteus_mcps-image-audio-mcp-cli/cli/autobyteus-image-audio health-check
/Users/normy/autobyteus_org/autobyteus_mcps-image-audio-mcp-cli/cli/autobyteus-image-audio list-image-models
/Users/normy/autobyteus_org/autobyteus_mcps-image-audio-mcp-cli/cli/autobyteus-image-audio list-audio-models
```

## Tests Implemented Or Updated

No repository-resident durable validation code was added or updated during this API/E2E round. Existing implementation-stage durable tests were judged sufficient for the changed boundary and were executed successfully.

## Durable Validation Added To The Codebase

- Repository-resident durable validation added or updated this round: `No`
- Paths added or updated: `N/A`
- If `Yes`, returned through `code_reviewer` before delivery: `N/A`
- Post-validation code review artifact: `N/A`

## Other Validation Artifacts

- Canonical validation report: `/Users/normy/autobyteus_org/autobyteus_mcps-image-audio-mcp-cli/tickets/in-progress/image-audio-mcp-cli/validation-report.md`

## Temporary Validation Methods / Scaffolding

Temporary validation only; no durable temporary scripts were left behind.

- Temporary `/tmp` help/stdout/stderr capture files were removed.
- The project `.venv` was temporarily moved aside for first-run wrapper validation; the fresh test-created `.venv` was removed and the original `.venv` was restored.
- Temporary Python one-off probes were supplied through stdin to `python`/`uv run`; no probe files were written into the repository.

## Dependencies Mocked Or Emulated

- Existing durable tests mock Autobyteus image/audio clients and download behavior to validate file-producing service behavior without provider credentials.
- API/E2E black-box commands did not mock the wrapper/CLI process. Provider-producing commands were not executed against live services; path and usage failures were exercised before provider calls.
- In-memory MCP client validation emulated an MCP client session without launching a separate long-running MCP server process.

## Prior Failure Resolution Check (Mandatory On Round >1)

| Prior Round | Scenario / Failure Reference | Previous Classification | Current Resolution | Evidence | Notes |
| --- | --- | --- | --- | --- | --- |
| N/A | N/A | N/A | N/A | N/A | First API/E2E validation round. |

## Scenarios Checked

### VAL-001 — Ticket/worktree and no workflow-state

Result: Pass.

Evidence:

```text
/Users/normy/autobyteus_org/autobyteus_mcps                      d04d9ab [main]
/Users/normy/autobyteus_org/autobyteus_mcps-image-audio-mcp-cli  d04d9ab [codex/image-audio-mcp-cli]
no codex/mcp-cli-tools worktree
no codex/mcp-cli-tools local branch
workflow-state find completed
```

### VAL-002 — Wrapper first run from `/tmp` with `.venv` absent

Result: Pass.

Evidence included in lifecycle section above. The wrapper returned a JSON success envelope for `health-check` and `uv run --frozen` created the project `.venv`/console script automatically.

### VAL-003 — Console script entrypoints

Result: Pass.

```text
autobyteus-image-audio => image_audio_mcp.cli:main
autobyteus-image-audio-server => image_audio_mcp.server:main
```

### VAL-004 — Help and docs

Result: Pass.

- Main help via wrapper and underlying `uv --directory` both succeeded and included task commands, `AUTOBYTEUS_AGENT_WORKSPACE`, provider credential notes, and wrapper auto-preparation guidance.
- All subcommand helps succeeded.
- Generation subcommands document `--config`; `generate-speech` documents `--speaker` and `--voice`; coordinate command documents marker/grounding options.

### VAL-005 — Safe command JSON envelopes and model listings

Result: Pass.

```text
health-check: exit=0, ok=True, result keys default_* plus status
list-image-models: exit=0, ok=True, model_count=17, model entries include model_identifier/default_config/parameter_schema/provider/runtime/value
list-audio-models: exit=0, ok=True, model_count=12, model entries include model_identifier/default_config/parameter_schema/provider/runtime/value
```

Note: model-list commands emitted an Autobyteus TLS certificate warning on stderr because `AUTOBYTEUS_SSL_CERT_FILE` was not set in this environment. The stdout JSON contract remained valid and parseable.

### VAL-006 — Usage-error JSON failures

Result: Pass.

```text
speaker/voice mismatch: exit=2, error_type=UsageError, message includes matching counts
old raw JSON option: exit=2, error_type=UsageError, message says unrecognized arguments: --generation-config-json {}
config parent-child conflict: exit=2, error_type=UsageError, message includes conflicts with non-object key
missing output path: exit=2, error_type=UsageError, message says --output-file-path required
empty config key: exit=2, error_type=UsageError, message says key must not be empty
duplicate config key: exit=2, error_type=UsageError, message says provided more than once or conflicts
speaker_mapping conflict: exit=2, error_type=UsageError, message says use either --speaker/--voice pairs or --config speaker_mapping
```

### VAL-007 — Safe-path missing-input runtime failure

Result: Pass.

With `AUTOBYTEUS_AGENT_WORKSPACE` set to a temporary directory, `generate-image --input-image missing.png` returned exit `1`, JSON `FileNotFoundError`, and a resolved path under the workspace. This proves local input normalization and clear failure before provider execution.

### VAL-008 — Durable local test suite

Result: Pass.

```text
.........ss..........                                                    [100%]
19 passed, 2 skipped
```

### VAL-009 — In-memory MCP compatibility probe

Result: Pass.

```text
tool_names=['health_check', 'list_audio_models', 'list_image_models', 'generate_image', 'find_target_coordinates', 'edit_image', 'generate_speech']
health_is_error=False
health_keys=['default_grounding_model', 'default_image_edit_model', 'default_image_generation_model', 'default_speech_model', 'status']
generate_speech_schema_keys=['generation_config', 'output_file_path', 'prompt']
speech_prompt_desc_has_mapping=True
```

Set comparison in the probe confirmed exactly the expected public tools and excluded hidden grounding tools.

### VAL-010 — Remote/provider gating

Result: Pass.

`RUN_REMOTE_IMAGE_AUDIO_TESTS` was unset, so the two remote/provider tests skipped as designed. This validates the clean local/mock path without requiring private `.env.test` or paid provider execution.

### VAL-011 — Tracked docs/source cleanup

Result: Pass.

- Tracked README/DESIGN include wrapper examples for health check, model listing, image generation, image editing, speech generation, coordinate finding, `--config` dot notation, and speaker/voice pairs.
- `git grep` across tracked README, DESIGN, `src/image_audio_mcp`, and tests found no `generation-config-json` or `generation-config-file` old-option contract.
- `call-tool` appears only in negative explanatory text saying the CLI is not a generic raw MCP `call-tool` interface.

### VAL-012 — Compile and diff hygiene

Result: Pass.

- `uv run --frozen python -m compileall -q src`: passed.
- `git diff --check`: passed.

### VAL-013 — User-requested real CLI CMD/provider E2E

Result: Pass with OpenAI-backed model overrides.

`autobyteus-image-audio/.env.test` was absent, so no secrets were copied into the worktree. The command subprocesses inherited available credentials/config from the Codex process environment. The inherited default RPA image/speech models were unhealthy in this environment, so the passing real-provider CLI addendum used explicit model overrides backed by the available OpenAI credential.

Evidence:

```text
generate-image, DEFAULT_IMAGE_GENERATION_MODEL=gpt-image-1.5: exit=0, ok=True, file_size=45480, output=real-generated-image-openai.png
edit-image, DEFAULT_IMAGE_EDIT_MODEL=gpt-image-1.5: exit=0, ok=True, file_size=49246, output=real-edited-image-openai.png
generate-speech, DEFAULT_SPEECH_GENERATION_MODEL=gpt-4o-mini-tts: exit=0, ok=True, file_size=91392, output=real-speech-openai.mp3
find-target-coordinates, DEFAULT_IMAGE_EDIT_MODEL=gpt-image-1.5: exit=0, ok=True, detection_method=color_magenta, pixel_coordinates={x: 200, y: 94}, marked_file_size=104675
```

Environment/provider caveat from inherited defaults:

```text
generate-image with DEFAULT_IMAGE_GENERATION_MODEL=nano-banana-pro-app-rpa@localhost:51739: exit=1, JSON RuntimeError, provider HTTP 500 because RPA Create Image button was disabled
generate-speech with DEFAULT_SPEECH_GENERATION_MODEL=gemini-3.1-flash-tts-rpa@localhost:51739: no stdout before external kill after 166.9s
```

This caveat is classified as provider/runtime configuration health, not an implementation failure, because the same wrapper/CLI/service paths succeeded against OpenAI-backed real models.

### VAL-014 — Credential-gated remote MCP integration pytest

Result: Pass.

Command:

```bash
RUN_REMOTE_IMAGE_AUDIO_TESTS=1 \
DEFAULT_IMAGE_GENERATION_MODEL=gpt-image-1.5 \
DEFAULT_SPEECH_GENERATION_MODEL=gpt-4o-mini-tts \
uv run --frozen --extra test pytest -q tests/test_integration.py
```

Evidence:

```text
..                                                                       [100%]
```

## Passed

All implementation-owned validation scenarios passed. Round 2 additionally passed real CLI provider E2E for `generate-image`, `edit-image`, `generate-speech`, and `find-target-coordinates` using OpenAI-backed model overrides, plus credential-gated MCP integration pytest.

## Failed

None classified as implementation failures. The inherited RPA default provider config was unhealthy during round 2 smoke checks: image generation returned a provider `HTTP 500` because the RPA Create Image button was disabled, and speech did not complete before it was killed after 166.9 seconds. The same CLI paths passed with OpenAI-backed model overrides.

## Not Tested / Out Of Scope

- Exhaustive real-provider matrix validation beyond the OpenAI-backed models used in round 2.
- Browser/UI validation for the project itself; no browser UI is in scope, though the inherited RPA provider failure message indicates its external browser automation backend was unhealthy for the default image model.
- Installer/updater/migration/restart validation; no such behavior is in scope beyond the wrapper first-run environment creation check.

## Blocked

None.

## Cleanup Performed

- Removed temporary `/tmp` validation capture files.
- Restored the original ignored project `.venv` after first-run wrapper validation.
- Left no temporary validation scripts or harnesses in the repository.

## Classification

No failure classification applies. Latest authoritative validation result is `Pass`.

## Recommended Recipient

`delivery_engineer`

Rationale: validation passed and no repository-resident durable validation code was added or updated after code review, so the cumulative package can proceed directly to delivery.

## Evidence / Notes

- Full local/mock suite and in-memory MCP compatibility checks pass.
- Wrapper first-run behavior was proven with `.venv` absent and current working directory `/tmp`.
- Round 2 real provider-backed wrapper CLI commands passed for `generate-image`, `edit-image`, `generate-speech`, and `find-target-coordinates` with OpenAI-backed model overrides.
- Round 2 credential-gated MCP integration tests passed with `RUN_REMOTE_IMAGE_AUDIO_TESTS=1` and OpenAI-backed model overrides.
- Project `autobyteus-image-audio/.env.test` was absent; no secrets were copied into the worktree. Credentials/config were inherited from the current process environment.
- Current inherited RPA default provider config was unhealthy during smoke checks; see VAL-015.
- Model-list and provider commands returned valid JSON success on stdout when successful; stderr contained a non-fatal Autobyteus SSL certificate warning due to missing `AUTOBYTEUS_SSL_CERT_FILE` in this environment.

## Latest Authoritative Result

- Result values: `Pass` / `Fail` / `Blocked`
- Result: `Pass`
- Notes: API/E2E/executable validation passed for `image-audio-mcp-cli`. User-requested credentialed CLI/provider addendum also passed using OpenAI-backed model overrides. No durable validation code changes were made during this round; route/update `delivery_engineer`.
