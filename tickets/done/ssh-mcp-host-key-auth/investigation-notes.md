# Investigation Notes — SSH MCP Seamless Multi-Auth Sessions

## Status

- **Ticket:** `ssh-mcp-host-key-auth`
- **Repository:** `/Users/normy/autobyteus-org/autobyteus-mcps`
- **Authoritative worktree:** `/Users/normy/autobyteus-org/autobyteus-mcps-worktrees/ssh-mcp-host-key-auth`
- **Branch:** `codex/ssh-mcp-host-key-auth`
- **Base:** `origin/main` at `7d0ff82191d045402f8ec84405a56fccba1c969a`
- **Expected finalization target:** `main`

## Problem Framing

This is a reachable production-path bug in the multi-MCP SSH lifecycle: the LAN MCP uses a password, while the droplet MCP uses a private key. The LAN session open can enter an askpass loop when the host key is not trusted. The desired behavior is seamless, bounded, and safe for both auth modes.

## Supplemental Artifact Inventory

| Artifact Path | Purpose And Scope | Status |
| --- | --- | --- |
| `requirements.md` | Approved behavior basis and acceptance criteria. | Draft; refine before implementation. |
| `design-spec.md` | Target ownership and change design. | To be created. |
| `solution-revision-record.md` | Durable design-round index. | To be created. |

## Source Log

| Date | Source Type | Exact Source / Command | Finding |
| --- | --- | --- | --- |
| 2026-08-18 | Code | `src/ssh_mcp/server.py`, `config.py`, `runner.py`, `execution.py`, `session.py` | `health_check` runs only `ssh -V`; `open_session` resolves fixed host/user/port and launches OpenSSH through the runner. |
| 2026-08-18 | Data | `/Users/normy/.autobyteus/server-data/mcps.json` (values inspected with secrets redacted) | `lan` configuration is fixed host `192.168.2.142`, user `ryan-ai`, port 22, password auth. `droplet` is fixed host `68.183.210.24`, user `autobyteus`, port 22, private-key auth. |
| 2026-08-18 | Code | `src/ssh_mcp/runner.py:398-443` | Password mode sets `BatchMode=no`, disables public-key auth, prefers password/keyboard-interactive, and forces an askpass script that prints the configured password. |
| 2026-08-18 | Code | `src/ssh_mcp/execution.py:20-78` | Child process receives `stdin=DEVNULL` and is bounded by the configured timeout; timeout result may omit non-string `TimeoutExpired` stderr. |
| 2026-08-18 | Doc | `README.md`, `docs/runtime-flow.md` | Host-key verification is delegated to normal OpenSSH; docs warn first-time hosts may need manual setup. |
| 2026-08-18 | Test | `uv run --frozen --extra test pytest tests/test_config.py tests/test_runner.py tests/test_server.py` | 34 tests passed. |
| 2026-08-18 | Probe | Exact runner invocation using current LAN env with a 10-second timeout | Open session timed out; resolved destination was `ryan-ai@192.168.2.142`; no session was registered. |
| 2026-08-18 | Probe | Same runner invocation through a temporary wrapper with a verified temporary `known_hosts` containing the LAN host key | Session opened successfully in about 1.4 seconds and closed successfully. This proves target reachability, credentials, askpass, control master, and cleanup work when host trust is established. |
| 2026-08-18 | Probe | Askpass instrumentation with no trusted host key | Askpass was invoked repeatedly; the generic password-printing script was answering a host-key confirmation prompt, explaining the timeout loop. |
| 2026-08-18 | Setup | `docker info` | Docker CLI exists but Docker daemon is unavailable in this environment; current Docker E2E cannot be rerun here without daemon setup. |

## Relevant Existing Behavior And Production Paths

| Behavior ID | Kind | Current Supported Trigger Or Governing Contract | Current Production Path And Lifecycle | Outcome / Invariant | Evidence |
| --- | --- | --- | --- | --- | --- |
| BEH-001 | Contract | MCP caller invokes `ssh_health_check`. | `server.ssh_health_check -> runner.run_health_check -> execution.execute -> local ssh -V -> structured result`. | Local executable/version health only; no remote target. | `server.py`, `runner.py`, tool result observed. |
| BEH-002 | User/Operational | MCP caller invokes LAN `ssh_open_session` with omitted/default host. | `server -> runner.run_open_session -> resolve_target -> _build_execution_env -> askpass SSH control master -> execution timeout/result`. | Current path can loop on first-use host key and timeout. | Exact LAN probe and askpass instrumentation. |
| BEH-003 | User/Operational | MCP caller invokes droplet `ssh_open_session` with omitted/default host. | Same runner path, but `private_key_file` selects key args and batch mode. | Must remain key-authenticated and isolated from LAN password. | `mcps.json`, runner command builder, existing tests. |
| BEH-004 | Contract | OpenSSH sees changed key, bad credential, or network failure. | OpenSSH child process -> `execution.execute` -> structured error -> no session record. | Must be bounded and diagnostically useful. | Existing timeout/non-zero handling plus reproduction. |

## Current-State Architecture / Ownership

- `server.py` is the thin MCP boundary and owns tool schemas/progress.
- `config.py` owns environment parsing, auth-source exclusivity, target resolution, and default-host pinning.
- `runner.py` owns lifecycle orchestration and OpenSSH argv/environment policy.
- `session.py` owns control-socket/session metadata and cleanup.
- `execution.py` owns subprocess invocation and structured error mapping.
- The design issue is local to the runner's OpenSSH host-key/password interaction policy; no subsystem split is required.

## Root Cause

`runner._build_execution_env` forces `SSH_ASKPASS` to return the configured password. The command builders do not specify a non-interactive host-key policy. When the host key is unknown, OpenSSH asks for confirmation. With no stdin and forced askpass, the askpass helper responds with the password to a yes/no host-key prompt. OpenSSH does not receive a valid confirmation and repeatedly invokes askpass until the outer timeout.

The current implementation's timeout is bounded, but the behavior is not seamless and its `TimeoutExpired` mapping can hide useful stderr. The root cause is a local implementation defect / missing host-key invariant, not a credential mismatch: the same code succeeds when the host key is pre-trusted.

## Design Premise Reachability

| Premise | Reachability | Evidence |
| --- | --- | --- |
| A normal MCP caller can invoke `ssh_open_session` for a configured fixed host before that host is in the local known-hosts file. | Reachable | Current LAN configuration is a normal fixed-host MCP entry; exact open-session probe reproduced the timeout without hidden-state mutation. |
| Multiple fixed-host MCP entries can coexist with different auth sources. | Reachable | `mcps.json` contains separate `lan` and `droplet` entries and the tool registry exposes both prefixes. |

## Persisted Data Transition

- **Decision:** Not Affected.
- This change only modifies OpenSSH command policy, temporary control sockets, askpass handling, and tests/docs. No application-persisted schema or semantic data changes.

## Open Unknowns / Risks

- Whether the desired default should be `StrictHostKeyChecking=accept-new` (seamless TOFU, rejects changed keys) or an explicit managed known-hosts file. User requirement favors seamless operation; design must document the security tradeoff.
- Whether the MCP runtime's `HOME`/known-hosts path is stable across launcher restarts. The safest implementation should avoid relying on an undocumented per-process path and should fail clearly if it cannot record a new host key.
- Docker daemon is unavailable for local rerun; repository history records prior Docker E2E success, but current validation must classify this environment limitation honestly.

## Notes For Implementation And Review

- Preserve separate auth-source selection and fixed-host pinning.
- Never put a password on argv or in structured output.
- Add a regression test proving an unknown host cannot trigger a password/host-key prompt loop.
- Prefer `StrictHostKeyChecking=accept-new` over blind `no`: automatically trust only new keys, but reject changed keys.
- Add explicit `NumberOfPasswordPrompts=1` and ensure timeout diagnostics retain stderr where possible.
