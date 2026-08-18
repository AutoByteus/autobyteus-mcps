# Docs Sync - Simplify SSH MCP Configuration

## Scope

- Ticket: `simplify-ssh-mcp-config`
- Trigger Stage: `9`
- Workflow state source: `tickets/done/simplify-ssh-mcp-config/workflow-state.md`

## Why Docs Were Updated

- Summary: Long-lived SSH MCP docs now present the simplified one-host setup first, document one auth source at a time, and describe the split runtime owners (`runner`, `session`, `execution`, `types`) instead of leaving that knowledge only in ticket artifacts.
- Why this change matters to long-lived project understanding: Future users should configure SSH MCP like ordinary SSH software (host/user/optional-port plus password-file/private-key/secret-injected password) without learning old raw OpenSSH args or separate allowlist concepts. Future maintainers should also see the new runtime ownership boundaries directly in `docs/runtime-flow.md`.

## Long-Lived Docs Reviewed

| Doc Path | Why It Was Reviewed | Result | Notes |
| --- | --- | --- | --- |
| `ssh-mcp/README.md` | Primary user-facing setup/config docs. | Updated | Simple config and MCP examples now show destination + one auth source; inline password text warns against committed secrets. |
| `ssh-mcp/docs/runtime-flow.md` | Canonical runtime/operational flow doc. | Updated | Runtime layers now include `session.py`, `execution.py`, and `types.py`; ownership boundaries are explicit. |
| `ssh-mcp/ARCHITECTURE.md` | Checked whether a broader architecture doc exists. | No change | No such file exists under `ssh-mcp`; `docs/runtime-flow.md` is the canonical runtime doc. |

## Docs Updated

| Doc Path | Type Of Update | What Was Added / Changed | Why |
| --- | --- | --- | --- |
| `ssh-mcp/README.md` | Public setup/config docs | Split simple vs advanced environment sections; added first-class private-key/password-file examples; clarified inline password should come from runtime secret injection; kept security best practices aligned with no password-on-argv behavior. | Makes normal setup intuitive and avoids reintroducing removed legacy concepts. |
| `ssh-mcp/docs/runtime-flow.md` | Runtime architecture docs | Expanded runtime layers, session lifecycle, and added runtime ownership boundaries for server/config/runner/session/execution/types/OpenSSH. | Promotes Stage 3/4 runtime-split knowledge into durable docs. |

## Durable Design / Runtime Knowledge Promoted

| Topic | What Future Readers Need To Understand | Source Ticket Artifact(s) | Target Long-Lived Doc |
| --- | --- | --- | --- |
| Simple SSH MCP config model | Configure host, user, optional port, and exactly one auth source; advanced runtime guardrails usually stay defaulted. | `requirements.md`, `proposed-design.md` | `ssh-mcp/README.md`, `ssh-mcp/docs/runtime-flow.md` |
| Default-host pinning | A configured default host pins this MCP server; a different explicit host is rejected, and separate hosts should use separate MCP server entries. | `requirements.md`, `future-state-runtime-call-stack.md` | `ssh-mcp/README.md`, `ssh-mcp/docs/runtime-flow.md` |
| Private-key and password auth behavior | Private-key path is first-class; password/password-file use askpass env and do not put the secret in argv. | `proposed-design.md`, `api-e2e-testing.md` | `ssh-mcp/README.md`, `ssh-mcp/docs/runtime-flow.md` |
| Runtime split ownership | `runner` is authoritative orchestration, `session` owns local session state, `execution` owns subprocess/result mapping, and `types` owns structured output. | `proposed-design.md` v2, `future-state-runtime-call-stack.md` v2, `code-review.md` | `ssh-mcp/docs/runtime-flow.md` |
| Verification expectations | Fast pytest suite plus optional Docker-backed OpenSSH E2E validate config/auth/session lifecycle. | `api-e2e-testing.md`, `code-review.md` | `ssh-mcp/README.md`, `ssh-mcp/docs/runtime-flow.md` |

## Removed / Replaced Components Recorded

| Old Component / Path / Concept | What Replaced It | Where The New Truth Is Documented |
| --- | --- | --- |
| Raw OpenSSH argument env as the normal key-auth path | First-class private-key file setting plus internal runner auth args. | `ssh-mcp/README.md` Simple Environment/Auth Sources; `ssh-mcp/docs/runtime-flow.md` Session Lifecycle |
| Separate host allowlist mental model for normal setup | Default-host pinning and one MCP server config per fixed host. | `ssh-mcp/README.md` Destination section; `ssh-mcp/docs/runtime-flow.md` Configuration Flow |
| All-in-one runtime ownership in `runner.py` | Split `runner`, `session`, `execution`, and `types` ownership. | `ssh-mcp/docs/runtime-flow.md` Runtime Layers and Runtime Ownership Boundaries |

## Validation Performed

```bash
rg -n "SSH_MCP_BASE_ARGS|SSH_MCP_ALLOWED_HOSTS" ssh-mcp/README.md ssh-mcp/docs/runtime-flow.md
rg -n "SSH_MCP_DEFAULT_HOST|SSH_MCP_PRIVATE_KEY_FILE|SSH_MCP_PASSWORD_FILE|Runtime Layers|Runtime Ownership Boundaries" ssh-mcp/README.md ssh-mcp/docs/runtime-flow.md
```

Results:
- Exact removed env names are absent from long-lived docs.
- Simple destination/auth controls and runtime ownership sections are present.

## No-Impact Decision

N/A. Docs impact exists and was updated.

## Final Result

- Result: `Updated`
- If `Blocked` because earlier-stage work is required, classification: `N/A`
- Required return path or unblock condition: `N/A`
- Follow-up needed: `None`
