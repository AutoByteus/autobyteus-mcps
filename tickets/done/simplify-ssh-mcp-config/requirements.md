# Requirements - Simplify SSH MCP Configuration

## Status

Design-ready

## Goal / Problem Statement

Simplify `ssh-mcp` so normal MCP setup matches ordinary SSH software: configure a destination host, user, optional port, and exactly one intuitive auth path (password, password file, or private key file). Low-level OpenSSH flags and duplicated allowlist/default-host concepts should not be part of the primary user-facing setup.

## In-Scope Requirements

| Requirement ID | Requirement | Expected Outcome |
| --- | --- | --- |
| REQ-001 | Provide a first-class private-key file env variable. | `SSH_MCP_PRIVATE_KEY_FILE=/path/to/private_key` configures key-based auth without requiring users to write raw `ssh -i ...` args. |
| REQ-002 | Preserve simple password auth. | `SSH_MCP_PASSWORD` and `SSH_MCP_PASSWORD_FILE` continue to support non-interactive password auth, with exactly one password source allowed. |
| REQ-003 | Keep the normal target model simple. | `SSH_MCP_DEFAULT_HOST`, `SSH_MCP_DEFAULT_USER`, and optional `SSH_MCP_DEFAULT_PORT` are the primary destination settings. |
| REQ-004 | Remove confusing public advanced target/args knobs from normal config. | `SSH_MCP_ALLOWED_HOSTS` and `SSH_MCP_BASE_ARGS` are no longer supported env settings; stale non-empty use fails fast with an actionable error. |
| REQ-005 | Keep runtime safety defaults internal/advanced. | Timeout, command/output limits, session idle timeout, session count, command path, and health-check args retain sane defaults and remain documented as advanced optional settings only. |
| REQ-006 | Use default-host pinning instead of a separate allowlist for the normal one-host MCP. | When `SSH_MCP_DEFAULT_HOST` is set, a tool call may omit `host` or pass the same host, but cannot override it to a different host. |
| REQ-007 | Preserve non-interactive behavior. | Private-key/no-password modes add `BatchMode=yes` internally; password mode uses askpass internally. |
| REQ-008 | Update durable docs and tests. | README/runtime docs and unit/E2E tests reflect the simplified public config surface and the new private-key file path. |

## In-Scope Use Cases

| Use Case ID | Description | Requirement IDs |
| --- | --- | --- |
| UC-001 | Load minimal password-file MCP env config. | REQ-002, REQ-003 |
| UC-002 | Load minimal inline password MCP env config. | REQ-002, REQ-003 |
| UC-003 | Load minimal private-key MCP env config. | REQ-001, REQ-003, REQ-007 |
| UC-004 | Reject ambiguous auth configuration. | REQ-001, REQ-002 |
| UC-005 | Reject removed legacy env knobs when non-empty. | REQ-004 |
| UC-006 | Resolve target with default-host pinning. | REQ-003, REQ-006 |
| UC-007 | Build OpenSSH commands with internal auth/default options. | REQ-001, REQ-002, REQ-007 |
| UC-008 | Preserve session lifecycle and structured MCP results. | REQ-005, REQ-007 |
| UC-009 | Document the simple config first and advanced settings separately. | REQ-005, REQ-008 |

## Acceptance Criteria

| Acceptance Criteria ID | Expected Outcome | Validation Intent |
| --- | --- | --- |
| AC-001 | `load_settings` parses `SSH_MCP_PRIVATE_KEY_FILE`, resolves `~`, and stores it on settings. | Unit test in `tests/test_config.py`. |
| AC-002 | `load_settings` rejects simultaneous private-key and password/password-file auth. | Unit test in `tests/test_config.py`. |
| AC-003 | `load_settings` rejects simultaneous `SSH_MCP_PASSWORD` and `SSH_MCP_PASSWORD_FILE`. | Existing/updated unit test in `tests/test_config.py`. |
| AC-004 | Non-empty `SSH_MCP_BASE_ARGS` fails with an actionable unsupported-setting message. | Unit test in `tests/test_config.py`. |
| AC-005 | Non-empty `SSH_MCP_ALLOWED_HOSTS` fails with an actionable unsupported-setting message. | Unit test in `tests/test_config.py`. |
| AC-006 | When a default host exists, omitted host resolves to it, same host is accepted, and different explicit host is rejected. | Unit test in `tests/test_config.py`. |
| AC-007 | Private-key open/session/close commands include `-i <private_key>`, `IdentitiesOnly=yes`, and `BatchMode=yes` internally. | Unit test in `tests/test_runner.py`. |
| AC-008 | Password open command still uses askpass, `BatchMode=no`, and password-oriented authentication internally. | Unit test in `tests/test_runner.py`. |
| AC-009 | Existing MCP server lifecycle tests pass with updated settings shape. | `pytest tests/test_server.py` plus full non-Docker test suite. |
| AC-010 | Docker E2E fixtures are updated to use `SSH_MCP_PRIVATE_KEY_FILE` semantics and no removed env concepts. | Static test update plus optional Docker E2E run if environment supports it. |
| AC-011 | README shows minimal host/user/password-file and host/user/private-key examples first. | Docs review and grep. |
| AC-012 | Runtime docs no longer list `SSH_MCP_ALLOWED_HOSTS` or `SSH_MCP_BASE_ARGS` as supported controls. | Docs review and grep. |

## Constraints / Dependencies

- Local runtime depends on OpenSSH client binary `ssh`.
- Password auth uses OpenSSH `SSH_ASKPASS` non-interactively.
- Private-key auth uses the private key file on the local client machine. The public key must already be installed on the remote server.
- Host-key verification remains OpenSSH's normal behavior. Users may need to trust the host manually or manage known_hosts before MCP use.
- No public config compatibility shims for `SSH_MCP_ALLOWED_HOSTS` or `SSH_MCP_BASE_ARGS` under the workflow's no-legacy policy.
- Docker E2E tests are optional and gated by `SSH_MCP_RUN_DOCKER_E2E=1`.

## Assumptions

- The primary intended deployment is one MCP server config per SSH target.
- Users who need multiple hosts can create multiple MCP server entries, each with its own `SSH_MCP_DEFAULT_HOST`, or omit a default host and pass `host` explicitly.
- Users needing private-key passphrases will use ssh-agent/normal SSH setup rather than a passphrase env var.
- Advanced time/session/output limits are useful as guardrails but should not be required to understand normal setup.

## Open Questions / Risks

- Removing raw base args may inconvenience power users who need unusual OpenSSH options. This is accepted to keep the normal MCP surface simple and avoid legacy escape-hatch complexity.
- First-time connections to unknown hosts may fail until `known_hosts` is prepared. This is intentionally left to normal OpenSSH behavior rather than adding a confusing host-key bypass setting.

## Requirement-to-Use-Case Coverage

| Requirement ID | Covered By Use Cases |
| --- | --- |
| REQ-001 | UC-003, UC-004, UC-007 |
| REQ-002 | UC-001, UC-002, UC-004, UC-007 |
| REQ-003 | UC-001, UC-002, UC-003, UC-006 |
| REQ-004 | UC-005, UC-009 |
| REQ-005 | UC-008, UC-009 |
| REQ-006 | UC-006 |
| REQ-007 | UC-003, UC-007, UC-008 |
| REQ-008 | UC-009 |

## Acceptance-Criteria-to-Scenario Intent

| Acceptance Criteria ID | Stage 7 Scenario ID |
| --- | --- |
| AC-001 | SC-001 |
| AC-002 | SC-002 |
| AC-003 | SC-002 |
| AC-004 | SC-003 |
| AC-005 | SC-003 |
| AC-006 | SC-004 |
| AC-007 | SC-005 |
| AC-008 | SC-006 |
| AC-009 | SC-007 |
| AC-010 | SC-008 |
| AC-011 | SC-009 |
| AC-012 | SC-009 |

## Scope Classification

Medium.

Rationale: the implementation touches configuration contract, runner command construction, unit/E2E tests, and docs. The public MCP tool names stay the same, but the environment surface changes enough to justify a proposed design before implementation.
