# Requirements: Image/Audio CLI generation_config JSON support

Status: Refined

## Goal / Problem Statement

The `autobyteus-image-audio` CLI must use the same natural argument shape as the MCP tools for model-specific configuration: a single nested `generation_config` JSON object, either inline or loaded from a JSON file. The earlier implementation preserved `--config key=value` and `--speaker/--voice` as compatibility/simple-human styles, but that violates this workflow's no-backward-compatibility/no-legacy policy for the intended CLI contract. Those legacy/simple split config styles must be removed.

API-key behavior remains explicitly out of scope. The CLI continues inheriting provider credentials from the parent process environment through `uv run` and Python process inheritance; no CLI API-key argument is introduced.

## In-Scope Use Cases

| Use Case ID | Description | Primary Actor |
| --- | --- | --- |
| UC-001 | Invoke image/video/edit/speech generation with a full inline nested JSON object passed as `generation_config`. | LLM agent / script |
| UC-002 | Invoke generation with a JSON file containing `generation_config` for complex or reusable configs. | LLM agent / human developer |
| UC-003 | Receive clear usage errors for invalid JSON, non-object generation config JSON, and conflicting full-object config sources. | User / LLM agent |
| UC-004 | Discover the MCP-shaped argument style through `--help` and README examples. | User / LLM agent |
| UC-005 | Confirm legacy split config styles are removed. | User / LLM agent |

## Requirements

| Requirement ID | Requirement | Expected Outcome |
| --- | --- | --- |
| REQ-001 | The CLI shall accept an inline MCP-shaped nested JSON object for `generation_config` on all generation commands. | `generate-image`, `edit-image`, `generate-speech`, and `generate-video` can receive `--generation-config '{...}'`; the resulting dict is passed to services. |
| REQ-002 | The CLI shall accept a file path containing a JSON object for `generation_config`. | `--generation-config-file config.json` loads a JSON object and passes it as generation config. |
| REQ-003 | The CLI shall reject invalid or non-object generation config inputs with clear JSON failure envelopes. | Bad JSON, array/scalar JSON, unreadable files, and duplicate/conflicting object keys return `UsageError`. |
| REQ-004 | The CLI help and README shall present direct nested JSON as the single model-specific configuration path, with file-based JSON as the large-config variant. | Users can discover `--generation-config`, `--generation-config-file`, and their relationship to MCP `generation_config`. |
| REQ-005 | The CLI shall remove legacy/split configuration flags `--config`, `--speaker`, and `--voice`. | These flags do not appear in help and are rejected by argparse as unrecognized arguments. Multi-speaker mapping is represented only inside `generation_config.speaker_mapping`. |
| REQ-006 | API-key handling shall remain unchanged. | No `--api-key` CLI argument is added; credentials remain environment variables inherited by the process. |

## Acceptance Criteria

| Acceptance Criteria ID | Verifiable Expected Outcome |
| --- | --- |
| AC-001 | `generate-speech --generation-config '{"mode":"multi-speaker","speaker_mapping":{"Joe":"Kore","Jane":"Puck"}}'` passes the nested dict to `services.generate_speech`. |
| AC-002 | `generate-image --generation-config '{"image_config":{"aspect_ratio":"16:9"}}'` passes the nested dict to `services.generate_image`. |
| AC-003 | `--generation-config-file` loads a JSON object from disk and passes it to the corresponding service call. |
| AC-004 | Invalid inline JSON, non-object inline JSON, invalid file JSON, non-object file JSON, and unreadable file paths return `UsageError` envelopes. |
| AC-005 | Conflicting keys between `--generation-config-file` and `--generation-config` return `UsageError` rather than silent overrides. |
| AC-006 | `--help` for generation commands includes `--generation-config` and `--generation-config-file`. |
| AC-007 | README command-line usage documents direct nested JSON and file-based config, with no `--config`, `--speaker`, or `--voice` examples. |
| AC-008 | CLI help does not include `--config`, `--speaker`, or `--voice`. |
| AC-009 | Passing `--config`, `--speaker`, or `--voice` returns a usage error. |
| AC-010 | No CLI API-key argument is introduced. |

## Constraints / Dependencies

- Scope is limited to `autobyteus-image-audio` CLI UX, tests, and README docs.
- Service-layer and MCP server function signatures already accept `generation_config: Optional[Dict[str, Any]]` and should not change.
- No backward-compatibility or legacy retention: split config flags are removed rather than retained as aliases.
- API-key handling remains environment-variable based and out of implementation scope.

## Assumptions

- Agent DX is the primary design target for this CLI surface.
- Humans who dislike shell JSON quoting can use `--generation-config-file`.
- Multi-speaker speech should be configured exactly as MCP does: `generation_config.speaker_mapping`.

## Open Questions / Risks

- Inline JSON remains shell-dependent for quote escaping. Mitigation: file-based JSON is supported and documented.
- Removing split flags is a breaking CLI change. This is intentional under the workflow's no-backward-compatibility/no-legacy rule.

## Requirement-to-Use-Case Coverage

| Requirement ID | Covered Use Cases |
| --- | --- |
| REQ-001 | UC-001 |
| REQ-002 | UC-002 |
| REQ-003 | UC-003 |
| REQ-004 | UC-004 |
| REQ-005 | UC-005 |
| REQ-006 | UC-001, UC-002 |

## Acceptance-Criteria-to-Scenario Intent

| Acceptance Criteria ID | Intended Stage 7 Scenario |
| --- | --- |
| AC-001 | SCN-001 inline nested JSON speech config dispatch test |
| AC-002 | SCN-002 inline nested JSON image config dispatch test |
| AC-003 | SCN-003 generation config file dispatch test |
| AC-004 | SCN-004 invalid JSON/file usage-error tests |
| AC-005 | SCN-005 config source conflict usage-error tests |
| AC-006 | SCN-006 help text includes MCP-shaped options |
| AC-007 | SCN-007 README text inspection excludes removed flags |
| AC-008 | SCN-008 help text excludes removed flags |
| AC-009 | SCN-009 removed flags return usage errors |
| AC-010 | SCN-010 code/doc inspection confirms no API-key CLI argument |

## Scope Classification

Confirmed scope: **Small**

Rationale: one CLI parser file plus tests/docs; no provider, service, MCP protocol, or credential changes.
