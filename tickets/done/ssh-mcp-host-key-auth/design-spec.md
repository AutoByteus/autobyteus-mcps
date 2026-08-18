# Design Spec — SSH MCP Seamless Multi-Auth Sessions

## Current-State Read

The MCP server exposes a thin `server.py` tool boundary over `runner.py`. `runner.py` resolves the fixed target, selects one configured auth source, builds OpenSSH commands, and delegates subprocess/result handling to `execution.py`; `session.py` owns control-master metadata and cleanup. This boundary is healthy for the bug fix.

Password mode uses a forced `SSH_ASKPASS` script. Because the command builders do not set host-key behavior, a first-use host can trigger an interactive host-key confirmation. With stdin disabled and askpass forced, the password helper answers the wrong prompt repeatedly until the timeout. Key mode is not affected by password handling but must receive the same non-interactive host-key policy.

## Intended Change

Make host-key handling an explicit shared OpenSSH policy: use `StrictHostKeyChecking=accept-new` for lifecycle commands. New host keys are recorded automatically using the normal OpenSSH known-hosts mechanism; changed keys are rejected. Add one password prompt maximum and preserve bounded timeout/error output. Keep LAN password and droplet private-key auth as independent configured sources.

This is trust-on-first-use, not blind acceptance: the first key is accepted automatically, but a later changed key fails. The policy must be documented so operators can pre-seed or manage known-hosts when stronger verification is required.

## Relevant Behavior And Production-Path Map

| Behavior ID | Approved Use Case(s) | Kind | Requirement / AC | Trigger | Existing Evidence | Approved Change / Preserved Outcome | Target Path / Spine |
| --- | --- | --- | --- | --- | --- | --- | --- |
| BEH-001 | Health check | Contract | REQ-006 / AC-007 | `ssh_health_check` | `server -> run_health_check -> ssh -V` | Preserve local-only health semantics and clarify docs. | `DS-001` |
| BEH-002 | LAN password session | User/Operational | REQ-001/002/004 / AC-001/003/005 | `ssh_open_session` with LAN defaults | Unknown host reproduced askpass loop; trusted-key probe succeeded. | Automatically accept new key, then password-authenticate without prompt; fail bounded on later key change. | `DS-001`, `DS-002` |
| BEH-003 | Droplet key session | User/Operational | REQ-003/005 / AC-004/006 | `ssh_open_session` with droplet defaults | Existing private-key command path and separate MCP config. | Add only shared host-key policy; preserve key-only auth and host isolation. | `DS-001`, `DS-002` |
| BEH-004 | Failure handling | Contract | REQ-004 / AC-002/005 | OpenSSH failure or timeout | `execution.execute` maps nonzero/timeout. | Changed keys and wrong auth return structured errors; timeout output is decoded and retained. | `DS-002`, `DS-003` |

## Material Design Premises

| Premise ID | Related Behavior | Independent Trigger / Evidence | Forward Path | Consequence | Reachability | Design Consequence |
| --- | --- | --- | --- | --- | --- | --- |
| DP-001 | BEH-002 | Normal caller opens a configured LAN host before it is trusted; reproduced with current config. | MCP open -> OpenSSH -> unknown host key -> askpass. | A reachable first-use state can hang. | Reachable | Shared host-key policy is required. |
| DP-002 | BEH-003 | Two MCP entries are configured independently in `mcps.json`. | Tool prefix -> server config -> runner settings. | Auth/host settings must not cross-contaminate. | Reachable | Keep settings immutable per server instance. |

## Task Design Health Assessment

- **Change posture:** Bug Fix / Behavior Change.
- **Current design issue found:** Yes, local implementation policy defect.
- **Root cause classification:** Local Implementation Defect / Missing Invariant.
- **Refactor needed now:** No.
- **Evidence:** `runner.py` is already the authoritative OpenSSH command-policy owner; the issue is one missing shared invariant in `_build_auth_args`, plus timeout output coercion.
- **Design response:** Add host-key policy and password-prompt bound at the existing runner owner; add focused regression tests and docs.
- **Refactor rationale:** No new boundary or data model is needed. Adding a helper or new subsystem would fragment a small, coherent policy owner.
- **Residual risk:** `accept-new` is TOFU. Operators needing preverified trust can pre-seed a managed `known_hosts`; changed keys remain rejected.

## Persisted Data / State Transition Decision

- **Decision:** Not Affected.
- No application-persisted data or schema changes. OpenSSH may update the operator's `known_hosts`, which is an intentional external SSH trust store, not an application data migration.

## Data-Flow Spine Inventory

| Spine ID | Scope | Behaviors | Start | End | Governing Owner | Why It Matters |
| --- | --- | --- | --- | --- | --- | --- |
| DS-001 | Primary End-to-End | BEH-001/002/003 | MCP tool call | Structured health/session result | `server.py` -> `runner.py` | Covers both fixed-host MCP instances and local-vs-remote health distinction. |
| DS-002 | Bounded Local | BEH-002/003/004 | Runner settings | OpenSSH control master / bounded result | `runner.py` | Carries auth, host-key, timeout, and control-socket policy. |
| DS-003 | Return-Event | BEH-004 | Child exit/timeout | `SshToolResult` | `execution.py` | Preserves stderr and maps failures without registering a bad session. |

## Primary Execution Spine(s)

`MCP client -> server tool boundary -> runner target/auth policy -> OpenSSH subprocess -> remote SSH daemon/control master -> structured result`

## Spine Narratives

| Spine | Narrative | Main Nodes | Governing Owner | Off-Spine Concerns |
| --- | --- | --- | --- | --- |
| DS-001 | The MCP caller selects a named tool prefix; that server instance loads one fixed host/user/port/auth source, delegates lifecycle behavior to the runner, and returns a structured result. | MCP client, `server.py`, `runner.py`, OpenSSH, remote daemon, result | `runner.py` for lifecycle policy | `config.py` settings validation; `session.py` control sockets; `execution.py` timeout/result mapping. |
| DS-002 | Runner builds one shared host-key policy plus mode-specific auth flags. OpenSSH accepts only new keys, rejects changed keys, and uses askpass or key auth without interactive stdin. | Target resolver, command builder, OpenSSH, control master | `runner.py` | `SessionManager`, askpass environment. |
| DS-003 | OpenSSH completion or timeout crosses the execution boundary, gets output normalized, and returns a structured result; only a successful open is added to the session manager. | `subprocess.run`, result mapping, session registration | `execution.py` / `runner.py` | Output truncation and cleanup. |

## Ownership Map

- `server.py`: thin public MCP facade; owns tool schemas and progress only.
- `config.py`: owns environment parsing, auth-source exclusivity, and fixed-target resolution.
- `runner.py`: authoritative owner of SSH lifecycle sequencing and OpenSSH argv/environment policy, including host-key policy.
- `session.py`: owns session identity, control socket paths, capacity, expiry, and metadata.
- `execution.py`: owns subprocess invocation, timeout/non-zero mapping, output normalization, and structured result construction.
- OpenSSH/remote daemon: owns host-key cryptographic verification and server-side auth decisions.

## Removal / Decommission Plan

| Item | Why Unnecessary | Replacement | Scope | Notes |
| --- | --- | --- | --- | --- |
| Password-mode implicit host-key prompt path | It causes the reachable askpass loop. | Shared `StrictHostKeyChecking=accept-new` argv policy. | In This Change | No compatibility branch retained. |
| Unbounded repeated password prompts | It delays wrong-password failure. | `NumberOfPasswordPrompts=1`. | In This Change | Password remains off argv. |

## Off-Spine Concerns

| Concern | Spine | Owner | Responsibility | Risk If On Main Line |
| --- | --- | --- | --- | --- |
| Environment/auth validation | DS-001/002 | `config.py` | Resolve one auth source and fixed target. | Runner would duplicate config policy. |
| Control-socket lifecycle | DS-002 | `session.py` | Allocate, register, expire, close. | OpenSSH policy would mix with state ownership. |
| Askpass secret transport | DS-002 | `runner.py` + `SessionManager` path | Supply secret through child env/script, not argv. | Secret could leak into command/result paths. |
| Timeout/output mapping | DS-003 | `execution.py` | Bound child and retain diagnostics. | Lifecycle code would duplicate error semantics. |

## Ownership Boundaries

`server.py` must call `runner` lifecycle functions and must not bypass into `session.py` or `execution.py`. `runner.py` may use `config`, `session`, and `execution`; `execution.py` must not resolve targets or auth. The OpenSSH command builder remains private to `runner.py`.

## Interface Boundary Mapping

| Interface | Subject | Responsibility | Identity | Notes |
| --- | --- | --- | --- | --- |
| `ssh_health_check` | Local SSH executable | Version/availability probe | No remote identity | Explicitly not a remote check. |
| `ssh_open_session` | Fixed SSH target | Open control master | Host + optional user/port resolved by settings | Returns session ID only on success. |
| `ssh_session_exec` | Existing session | Run one bounded command | Session ID | Uses session metadata. |
| `ssh_close_session` | Existing session | Close control master | Session ID | Removes metadata/socket. |

## Existing Capability / Subsystem Reuse

| Need | Existing Area | Decision | Why |
| --- | --- | --- | --- |
| Shared SSH command policy | `ssh_mcp.runner` | Extend | Already owns all lifecycle argv construction. |
| Timeout diagnostics | `ssh_mcp.execution` | Extend | Already owns subprocess/error normalization. |
| Durable proof | `ssh-mcp/tests` | Extend | Existing runner and Docker lifecycle tests are the established boundary. |

## File Responsibility Mapping

| File | Action | Responsibility |
| --- | --- | --- |
| `ssh-mcp/src/ssh_mcp/runner.py` | Modify | Add accept-new host-key option and one-password-prompt option to shared command policy. |
| `ssh-mcp/src/ssh_mcp/execution.py` | Modify | Decode timeout output consistently so diagnostics are not lost. |
| `ssh-mcp/tests/test_runner.py` | Modify | Assert host-key/auth flags for both modes and password prompt bound. |
| `ssh-mcp/tests/test_execution.py` | Add | Prove timeout bytes are surfaced as text. |
| `ssh-mcp/tests/test_e2e_docker.py` | Modify | Add/adjust first-use host-key lifecycle coverage if practical without weakening existing managed-host-key checks. |
| `ssh-mcp/README.md` | Modify | Document automatic new-key acceptance, changed-key rejection, and local health semantics. |
| `ssh-mcp/docs/runtime-flow.md` | Modify | Keep runtime policy and failure mapping current. |

## Dependency Rules

- `server -> runner`; no `server -> session/execution` bypass.
- `runner -> config/session/execution/types` only.
- `execution -> types` only.
- No password/host-key policy in server or tests-only wrappers.
- No compatibility mode for old raw SSH argument settings.

## Change Sequence

1. Modify runner shared command policy and execution timeout normalization.
2. Add focused unit/integration regression coverage.
3. Run repository tests; run real LAN smoke using a temporary known-hosts isolation and the configured MCP source without printing secrets.
4. Update README/runtime docs.
5. Run review and API/E2E checks; classify Docker-daemon limitations honestly.

## Tradeoffs / Risks

- `accept-new` enables seamless first-use TOFU and rejects changed keys; it is safer than `StrictHostKeyChecking=no` but weaker than preverified host keys.
- Existing known-hosts files remain authoritative for changed-key detection.
- If known-hosts storage is unavailable, OpenSSH may fail; the result will be bounded by the configured timeout.
- No persisted application-data migration is needed.

## Implementation Readiness Validation

- All approved use cases appear in BEH-001..BEH-004 and DS-001..DS-003.
- Target paths span MCP boundary, runner owner, OpenSSH/remote daemon, and structured result.
- Existing ownership is preserved; no boundary bypass or new generic abstraction is needed.
- LAN password and droplet key auth remain mutually exclusive per server settings.
- No legacy compatibility path or persisted-data migration is introduced.
- Design is implementation-ready.
