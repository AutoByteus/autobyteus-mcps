# Requirements — SSH MCP Seamless Multi-Auth Sessions

- **Ticket:** `ssh-mcp-host-key-auth`
- **Status:** Design-ready
- **Repository:** `/Users/normy/autobyteus-org/autobyteus-mcps`
- **Branch:** `codex/ssh-mcp-host-key-auth`
- **Base:** `origin/main` at `7d0ff82191d045402f8ec84405a56fccba1c969a`
- **Finalization target:** `main`

## Problem Statement

The repository supports multiple fixed-host SSH MCP servers: a password-authenticated LAN server and a private-key-authenticated droplet server. The LAN server can hang during `ssh_open_session` when the target host is not already trusted in `known_hosts`. The MCP must make both auth modes work without interactive prompts or indefinite waits.

## Approved Use Cases

1. Open and use the fixed-host LAN SSH MCP using its configured password when the host is first encountered.
2. Open and use the fixed-host droplet SSH MCP using its configured private key.
3. Reject changed host keys and invalid credentials with a bounded, actionable failure rather than accepting unsafe changes or hanging.
4. Run the existing health check and lifecycle tools for either MCP without changing the fixed-host isolation model.

## Relevant Behavior Summary

| Behavior ID | Current Behavior | Desired Behavior | Must Remain Unchanged |
| --- | --- | --- | --- |
| BEH-001 | `ssh_health_check` only probes the local SSH executable/version. | Preserve local command health semantics; do not claim remote connectivity. | Health check remains fast and side-effect free. |
| BEH-002 | LAN `ssh_open_session` uses password askpass and can loop on first-use host-key confirmation until the 60-second timeout. | First-use host keys are handled automatically through a documented trust-on-first-use policy, or the request fails fast; no prompt loop. | Password is never placed on argv. |
| BEH-003 | Droplet `ssh_open_session` uses private-key flags and batch mode. | Continue to open with private-key auth under the same host-key policy. | No password fallback for the key-configured server. |
| BEH-004 | Host-key changes and invalid credentials are delegated to OpenSSH but timeout diagnostics can be opaque. | Return a bounded non-zero/error result with useful stderr and no session record. | Existing structured result contract and session cleanup. |

## Requirements

### REQ-001 — Seamless host-key handling

For a configured fixed host, `ssh_open_session` MUST avoid interactive host-key confirmation prompts. A new host key MAY be accepted automatically under a documented trust-on-first-use policy, while a changed host key MUST be rejected.

### REQ-002 — Password authentication

When `SSH_MCP_PASSWORD` or `SSH_MCP_PASSWORD_FILE` is configured, the LAN MCP MUST authenticate non-interactively using the configured password, without exposing it in command arguments or result output.

### REQ-003 — Private-key authentication

When `SSH_MCP_PRIVATE_KEY_FILE` is configured, the droplet MCP MUST continue to use the configured key with non-interactive key authentication and MUST NOT require password handling.

### REQ-004 — Bounded failure

Host-key verification failures, authentication failures, network failures, and command hangs MUST return within the configured timeout and MUST NOT leave a registered session or orphaned control master.

### REQ-005 — Multiple fixed-host MCPs

Separate MCP server configurations MUST remain independently pinned to their own default host/user/port/auth source. A fix for LAN password auth MUST NOT cause the droplet key-auth configuration to use the LAN password or host.

### REQ-006 — Diagnostics and documentation

The result and long-lived documentation MUST make clear that `ssh_health_check` validates the local SSH command only, while session open validates the configured remote target. First-use host-key behavior and changed-key behavior MUST be documented.

## Acceptance Criteria

| Acceptance Criteria ID | Requirement(s) | Expected Outcome |
| --- | --- | --- |
| AC-001 | REQ-001, REQ-004 | A first-use host with password auth does not prompt or hang; it either opens successfully and records the key or returns a bounded explicit result. |
| AC-002 | REQ-001, REQ-004 | A changed host key is rejected without a session record and without waiting for interactive input. |
| AC-003 | REQ-002 | LAN password auth opens a reusable session and can run `whoami`/a harmless command; password is absent from argv and structured output. |
| AC-004 | REQ-003 | Droplet private-key auth opens a reusable session and can run a harmless command; password flags are not introduced. |
| AC-005 | REQ-004 | Wrong password, missing key, unreachable host, and timeout paths return within configured timeout with non-success structured results. |
| AC-006 | REQ-005 | Two simultaneously configured MCP instances retain independent host/user/auth settings and session managers. |
| AC-007 | REQ-006 | Unit/integration tests and README/runtime docs describe local health vs remote session behavior and host-key policy. |

## Scope / Non-Goals

- In scope: OpenSSH command construction, host-key policy, password askpass interaction, timeout/error diagnostics, tests, and docs.
- Out of scope: changing remote server accounts, rotating credentials, changing droplet/LAN server configuration, or adding an interactive credential UI.
- No persisted application data is affected; **transition decision: Not Affected**.

## Supplemental Artifacts

- `investigation-notes.md` — evidence and reproductions.
- `design-spec.md` — implementation-ready design.
- `solution-revision-record.md` — solution rounds.
