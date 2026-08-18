# Docs Sync Report — SSH MCP Seamless Multi-Auth Sessions

## Scope

- Ticket: `ssh-mcp-host-key-auth`
- Trigger: API/E2E and code review passed.
- Bootstrap base: `origin/main@7d0ff82191d045402f8ec84405a56fccba1c969a`
- Integrated base: same; `git fetch origin main` confirmed no advancement.
- Post-integration verification: targeted/full local suites and live LAN/droplet MCP protocol smokes passed.

## Why Docs Were Updated

The host-key behavior changed from potentially requiring manual first-use trust to automatic OpenSSH TOFU (`accept-new`). Health-check semantics also needed explicit clarification because it probes only the local SSH executable.

## Long-Lived Docs Reviewed

| Doc | Result | Notes |
| --- | --- | --- |
| `ssh-mcp/README.md` | Updated | Security and setup guidance updated. |
| `ssh-mcp/docs/runtime-flow.md` | Updated | Runtime/auth/host-key lifecycle updated. |
| `ssh-mcp/pyproject.toml` | No change | Commands/dependencies remain accurate. |

## Docs Updated

| Doc | Update | Why |
| --- | --- | --- |
| `ssh-mcp/README.md` | Document accept-new, changed-key rejection, and local-only health check. | Prevents operators from expecting health check to prove remote access. |
| `ssh-mcp/docs/runtime-flow.md` | Document host-key and prompt bounds. | Keeps runtime design truth durable. |

## Durable Knowledge Promoted

| Topic | Future-reader truth | Source |
| --- | --- | --- |
| First-use host keys | New keys auto-record; changed keys reject; preseed managed known-hosts for stronger trust. | investigation/design/code review |
| Health semantics | `ssh_health_check` runs local `ssh -V`; session open tests remote. | requirements/implementation |

## Delivery Continuation

- Result: `Pass`
- Next action: user verification, then repository finalization if explicitly requested.
- No release/deployment is required for this local MCP source change.
