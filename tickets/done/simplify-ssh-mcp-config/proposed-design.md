# Proposed Design Document - Simplify SSH MCP Configuration

## Design Version

- Current Version: `v2`

## Revision History

| Version | Trigger | Summary Of Changes | Related Review Round |
| --- | --- | --- | --- |
| v1 | Initial draft | Simplified public env surface around host/user/optional-port plus one auth source. | 1 |
| v2 | Stage 6 Design Impact re-entry | Added runtime split so changed source implementation files remain under the 500 effective-line gate: `types.py`, `session.py`, `execution.py`, slimmer `runner.py`. | 3 |

## Artifact Basis

- Investigation Notes: `tickets/done/simplify-ssh-mcp-config/investigation-notes.md`
- Requirements: `tickets/done/simplify-ssh-mcp-config/requirements.md`
- Requirements Status: `Design-ready`
- Shared Design Principles: `shared/design-principles.md`

## Summary

The SSH MCP public setup should match normal SSH clients: destination (`host`, `user`, optional `port`) plus exactly one auth source (`password`, `password_file`, or `private_key_file`). The target design removes public raw OpenSSH args and separate host allowlisting, adds first-class `SSH_MCP_PRIVATE_KEY_FILE`, uses default-host pinning for one-host MCP configs, and splits the oversized runtime file into explicit owners.

## Goal / Intended Change

- Make normal MCP config intuitive for humans and LLMs.
- Keep low-level OpenSSH policy inside runtime code, not env examples.
- Keep runtime guardrails as advanced settings with defaults.
- Preserve MCP tool names and session lifecycle.
- Keep changed implementation files below workflow source-size gates by splitting real runtime owners instead of retaining a large catch-all file.

## Legacy Removal Policy (Mandatory)

- Policy: `No backward compatibility; remove legacy code paths.`
- Remove `base_args` and `allowed_hosts` from `SshSettings`, env parsing, command construction, tests, and docs.
- Stale non-empty removed env values fail fast with actionable `ConfigError`; no compatibility wrapper, dual-path command builder, or silent fallback remains.
- Decommission the oversized all-in-one runtime file shape: session metadata and subprocess-result mapping move to explicit owner files.

## Requirements And Use Cases

| Requirement ID | Description | Acceptance Criteria ID(s) | Use Case IDs |
| --- | --- | --- | --- |
| REQ-001 | First-class private key file env. | AC-001, AC-007 | UC-003, UC-007 |
| REQ-002 | Preserve password and password-file auth. | AC-002, AC-003, AC-008 | UC-001, UC-002, UC-004, UC-007 |
| REQ-003 | Keep target model simple. | AC-006 | UC-001, UC-002, UC-003, UC-006 |
| REQ-004 | Remove confusing public args/allowlist knobs. | AC-004, AC-005 | UC-005, UC-009 |
| REQ-005 | Keep runtime safety defaults internal/advanced. | AC-009 | UC-008, UC-009 |
| REQ-006 | Use default-host pinning. | AC-006 | UC-006 |
| REQ-007 | Preserve non-interactive behavior. | AC-007, AC-008 | UC-003, UC-007, UC-008 |
| REQ-008 | Update durable docs and tests. | AC-010, AC-011, AC-012 | UC-009 |

## Current-State Read

| Area | Findings | Evidence | Open Unknowns |
| --- | --- | --- | --- |
| Entrypoints / Current Spine | MCP tools call runner functions through `create_server`; settings load once at server construction. | `ssh_mcp.server.create_server`, tool handlers | None. |
| Current Ownership Boundaries | `config.py`, `runner.py`, and `server.py` are coherent at a coarse level. | `load_settings`, `run_open_session`, `create_server` | None. |
| Coupling / Fragmentation Problems | Raw OpenSSH args and host allowlist leak low-level policy into public env/docs/tests. `runner.py` also bundles session state, command building, subprocess execution, and result mapping in one oversized file. | `SshSettings.base_args`, `SshSettings.allowed_hosts`, line count 717 | None. |
| Constraints | Host-key verification remains OpenSSH default. Stage 8 source-size hard limit applies to changed source files. | Requirements + Stage 6 re-entry notes | None. |
| Relevant Files | Config, server, runtime split files, tests, README, runtime docs. | `ssh-mcp/src/ssh_mcp/*`, `ssh-mcp/tests/*` | None. |

## Current State (As-Is)

Current setup treats a raw OpenSSH arg string as the only first-class way to configure private-key auth and non-interactive flags. It also separates default host from a host allowlist, making normal one-host config repeat itself. The runtime implementation has coherent behavior but too many source concerns in `runner.py` for a changed file under this workflow.

## Data-Flow Spine Inventory

| Spine ID | Scope | Start | End | Owning Node / Governing Owner | Why It Matters |
| --- | --- | --- | --- | --- | --- |
| DS-001 | Primary End-to-End | MCP client calls `ssh_open_session` | Structured open result + stored session | SSH MCP runtime orchestration | Shows config/auth resolution before OpenSSH launch. |
| DS-002 | Primary End-to-End | MCP client calls `ssh_session_exec` | Structured command result + touched session | SSH MCP runtime orchestration | Preserves reusable command execution. |
| DS-003 | Primary End-to-End | MCP client calls `ssh_close_session` | Structured close result + removed session | SSH MCP runtime orchestration | Preserves control-master cleanup. |
| DS-004 | Bounded Local | Process env mapping | Frozen `SshSettings` | `ssh_mcp.config` | Owns public env contract, auth exclusivity, and target pinning. |
| DS-005 | Bounded Local | `SshSettings` + target/session | OpenSSH argv/env | `ssh_mcp.runner` | Keeps OpenSSH flags internal and deterministic. |
| DS-006 | Bounded Local | Session lifecycle request | In-memory session map/control path | `ssh_mcp.session` | Gives session state/lifecycle metadata a separate owner. |
| DS-007 | Bounded Local | Execution spec | Structured `SshToolResult` | `ssh_mcp.execution` | Gives subprocess/error/output result mapping a separate owner. |

## Primary Execution / Data-Flow Spine(s)

- DS-001: `MCP client -> ssh_mcp.server.ssh_open_session -> ssh_mcp.runner.run_open_session -> ssh_mcp.config.resolve_target/auth settings -> ssh_mcp.runner auth/command builder -> ssh_mcp.execution.execute -> OpenSSH control master -> ssh_mcp.session.SessionManager.add -> structured result`
- DS-002: `MCP client -> ssh_mcp.server.ssh_session_exec -> ssh_mcp.runner.run_session_exec -> ssh_mcp.session.SessionManager.get -> ssh_mcp.runner command builder -> ssh_mcp.execution.execute -> OpenSSH control socket exec -> SessionManager.touch -> structured result`
- DS-003: `MCP client -> ssh_mcp.server.ssh_close_session -> ssh_mcp.runner.run_close_session -> SessionManager.pop -> runner close command -> execution.execute -> OpenSSH control socket close -> structured result`

## Spine Actors / Main-Line Nodes

| Node | Role In Spine | What It Advances |
| --- | --- | --- |
| MCP client | Initiating caller | Provides tool payload or session command. |
| `ssh_mcp.server` | Authoritative MCP tool surface | Stable tool names, descriptions, progress, structured output. |
| `ssh_mcp.config` | Configuration and validation owner | Env/tool input to target/auth/runtime settings. |
| `ssh_mcp.runner` | Runtime orchestration and OpenSSH command-policy owner | Coordinates config/session/execution and builds OpenSSH argv/env. |
| `ssh_mcp.session` | Session metadata owner | Owns `SessionRecord`, `SessionManager`, control paths, capacity, idle expiry. |
| `ssh_mcp.execution` | Subprocess/result owner | Owns execution specs, subprocess call, output truncation, error mapping. |
| `ssh_mcp.types` | Shared result-contract owner | Owns `SshToolResult` used by server/runner/execution. |
| OpenSSH process | External runtime dependency | Performs auth, control-master reuse, remote command execution. |

## Spine Narratives (Mandatory)

| Spine ID | Short Narrative | Main Domain Subject Nodes | Governing Owner | Key Off-Spine Concerns |
| --- | --- | --- | --- | --- |
| DS-001 | A client opens a session. Server delegates; runner resolves target/auth, builds argv/env, execution runs OpenSSH, session stores metadata. | Target, AuthSource, OpenSshCommand, ExecutionSpec, SessionRecord | `ssh_mcp.runner` | Env parsing, askpass, capacity, output mapping. |
| DS-002 | A client executes by session id. Runner validates, session manager resolves metadata, runner composes command, execution maps subprocess result. | SessionId, RemoteCommand, OpenSshCommand, ExecutionSpec | `ssh_mcp.runner` | Command length, cwd quoting, timestamp touch. |
| DS-003 | A client closes one session. Session manager removes metadata; runner asks OpenSSH to exit the control master; socket cleanup follows. | SessionId, SessionRecord, OpenSshCommand | `ssh_mcp.runner` | Socket unlink, missing-session error mapping. |
| DS-004 | Env becomes one tight settings model: removed keys rejected, exactly one auth source accepted, default host pins the server. | EnvSettings, AuthSource, TargetDefaults | `ssh_mcp.config` | Path expansion, numeric parsing, password-file reading. |
| DS-005 | Runner translates settings/session into argv/env. Password mode uses askpass; key/no-password mode uses batch-safe options. | AuthSource, OpenSshArgv, ExecutionEnv | `ssh_mcp.runner` | OpenSSH availability, health probe, timeout. |
| DS-006 | Session state operations are centralized in a manager that owns ids, control paths, capacity, timestamps, and expiry removal. | SessionRecord, SessionId, ControlPath | `ssh_mcp.session` | Temp/fallback socket directories. |
| DS-007 | Execution receives a complete spec, runs subprocess safely, truncates output, and returns one structured result shape. | ExecutionSpec, SshToolResult | `ssh_mcp.execution` | Timeout/non-zero/OS error mapping. |

## Ownership Map

| Node / Owner | Owns | Must Not Own | Notes |
| --- | --- | --- | --- |
| `ssh_mcp.config` | Public env names, validation, default-host pinning, auth-source exclusivity, target normalization, password-file reading. | Subprocess command sequencing, control sockets, askpass script creation. | Add `private_key_file`; remove raw args/allowlist. |
| `ssh_mcp.runner` | Authoritative runtime orchestration, OpenSSH argv/env auth policy, command composition, high-level lifecycle functions. | Env parsing, MCP tool schema, session-map internals, subprocess result/error mapping. | Stays the server-facing runtime boundary. |
| `ssh_mcp.session` | `SessionRecord`, `SessionManager`, session id/control path/capacity/expiry/touch/pop. | OpenSSH argv, subprocess execution, env parsing. | New explicit owner to reduce runner size. |
| `ssh_mcp.execution` | `ExecutionSpec`, subprocess.run invocation, output normalization, error/result mapping. | Session state, env parsing, command-building policy. | New explicit owner to reduce runner size. |
| `ssh_mcp.types` | Shared structured result type. | Runtime behavior. | Prevents server from importing execution internals just for the result contract. |
| `ssh_mcp.server` | MCP tool registration, progress messages, structured output delegation. | Auth policy, env parsing, command flags, session internals. | Tool payload remains stable. |
| Docs/tests | Public contract evidence and validation. | Production policy. | Updated to simplified config and runtime split. |

## Return / Event Spine(s)

No asynchronous event spine exists. The return path is synchronous structured MCP result mapping from `ssh_mcp.execution` through `ssh_mcp.runner` and `ssh_mcp.server` to the MCP client.

## Bounded Local / Internal Spines

- DS-004 / config: `env dict -> unsupported env check -> typed/defaulted fields -> auth conflict validation -> SshSettings`.
- DS-005 / runner: `SshSettings/session -> execution env decision -> auth argv builder -> open/exec/close command builders`.
- DS-006 / session: `lifecycle operation -> lock-protected session map -> SessionRecord/control path/capacity/timestamp result`.
- DS-007 / execution: `ExecutionSpec -> subprocess.run -> output normalization -> SshToolResult`.

## Off-Spine Concerns Around The Spine

| Off-Spine Concern | Serves Which Owner | Responsibility | Must Stay Off Main Line? |
| --- | --- | --- | --- |
| Secret-file reading | `ssh_mcp.config` | Read password file only when password auth is active. | Yes |
| Askpass script generation | `ssh_mcp.runner` | Provide password to OpenSSH via child env, not argv. | Yes |
| Host-key trust | OpenSSH | Use normal `known_hosts` behavior. | Yes |
| Timeout/output normalization | `ssh_mcp.execution` | Bound subprocess runtime/output and map errors. | Yes |
| Session capacity/expiry | `ssh_mcp.session` | Protect local resource usage. | Yes |
| Docs examples | Docs | Show simple config first, advanced settings separately. | Yes |

## Existing Capability / Subsystem Reuse Check

| Need / Concern | Existing Capability Area / Subsystem | Decision | Why | If New, Why Existing Areas Are Not Right |
| --- | --- | --- | --- | --- |
| Public env parsing | `ssh_mcp.config` | Extend | Already owns settings/validation. | N/A |
| Internal SSH argv policy | `ssh_mcp.runner` | Extend | Already owns OpenSSH command policy. | N/A |
| Session metadata | Currently inside `runner.py` | Create New File | Real owner exists but is hidden in oversized file. | Keeping inside runner breaches source-size guardrail. |
| Execution result mapping | Currently inside `runner.py` | Create New File | Real owner exists but is hidden in oversized file. | Keeping inside runner breaches source-size guardrail. |
| Result type contract | Currently inside `runner.py` | Create New File | Shared by server/runner/execution after split. | Avoid server importing execution internals. |
| MCP tool descriptions | `ssh_mcp.server` | Reuse | Tool schema remains stable. | N/A |

## Subsystem / Capability-Area Allocation

| Subsystem / Capability Area | Owns Which Concerns | Related Spine ID(s) | Governing Owner(s) Served | Decision | Notes |
| --- | --- | --- | --- | --- | --- |
| SSH config | Env contract, typed settings, target resolution, auth validation. | DS-001, DS-004 | `ssh_mcp.config` | Extend + Remove | Remove obsolete fields. |
| SSH runtime orchestration | Lifecycle functions and OpenSSH argv/env policy. | DS-001..DS-005 | `ssh_mcp.runner` | Modify/Split | Slim authoritative runtime boundary. |
| SSH session state | Session records, control paths, capacity, expiry. | DS-001..DS-003, DS-006 | `ssh_mcp.session` | Add | Extract real owner. |
| SSH execution/result mapping | Execution specs, subprocess, output/errors. | DS-001..DS-003, DS-007 | `ssh_mcp.execution` | Add | Extract real owner. |
| Shared result contract | `SshToolResult` TypedDict. | Return path | `ssh_mcp.types` | Add | Tight shared type. |
| MCP interface | Tool registration/progress/delegation. | DS-001..DS-003 | `ssh_mcp.server` | Keep | No direct session/execution internals. |
| Validation/docs | Durable proof/user docs. | All | Tests/docs | Modify | Update simplified contract and split imports. |

## Ownership-Driven Dependency Rules

- Allowed directions: `server -> runner/types`, `runner -> config/session/execution/types`, `execution -> types`, `session -> config` only for `ConfigError`, tests/docs observe public behavior.
- Authoritative public entrypoints: MCP clients use `server` tools; `server` uses `runner` lifecycle functions; `runner` alone coordinates session/execution internals.
- Forbidden shortcuts: `server` must not manage `SessionManager` internals directly beyond receiving a manager from `runner.create_session_manager`; no env raw args passthrough; no allowlist/default-host dual model.
- Boundary bypasses not allowed: docs/tests must not teach users to pass raw `-i`, batch mode, or identities-only via env.
- Temporary exceptions and removal plan: none.

## Architecture Direction Decision (Mandatory)

- Chosen direction: clean-cut public config replacement plus explicit runtime split into types/session/execution/orchestration files.
- Rationale (`complexity`, `testability`, `operability`, `evolution cost`): public config is simpler, auth/target behavior is directly testable, runtime file sizes become reviewable, and future execution/session changes have clearer owners.
- Data-flow spine clarity assessment: `Yes`
- Spine inventory completeness assessment: `Yes`
- Ownership clarity assessment: `Yes`
- Off-spine concern clarity assessment: `Yes`
- Authoritative Boundary Rule assessment: `Yes`
- File placement within the owning subsystem assessment: `Yes`
- Outcome: `Add` key file/session/execution/types, `Modify` config/runner/docs/tests, `Remove` raw args/allowlist and oversized runtime catch-all shape.

## Ownership And Structure Checks (Mandatory)

| Check | Result | Evidence | Decision |
| --- | --- | --- | --- |
| Repeated coordination policy across callers needs owner | Yes | Auth args used by open/exec/close. | Runner-local auth argv builder. |
| Responsibility overload exists in one file | Yes | Changed `runner.py` 717 effective non-empty lines. | Split session/execution/types. |
| Proposed indirection owns real concern | Yes | New files own session state, execution mapping, result type. | Keep. |
| Every off-spine concern has clear owner | Yes | Config/session/execution/runner split. | Keep. |
| Authoritative Boundary Rule preserved | Yes | `server` stays on runner boundary. | Keep. |
| Existing capability reused/extended naturally | Yes | Config/server/docs/tests reused; runtime split only where real owners exist. | Reuse/Extend/Add. |
| Repeated structures extracted where needed | Yes | `SshToolResult` promoted to `types.py`. | Extract. |
| Current structure can remain unchanged without spine degradation | No for runtime file; Yes for package folder. | Size gate + mixed concerns. | Split files within same package. |

## Optional Alternatives

| Option | Summary | Pros | Cons | Decision | Rationale |
| --- | --- | --- | --- | --- | --- |
| A | Keep raw args or allowlist as legacy escape hatch. | Flexible. | Violates no-legacy policy and user intent. | Rejected | Clean public config is required. |
| B | Keep all runtime code in `runner.py` and seek exception. | Minimal source moves. | Violates hard source-size gate for changed file. | Rejected | Split real owners instead. |
| C | Split into many small command/auth/session/result files. | Very small files. | Over-splits a small package. | Rejected | Four runtime files are enough and owner-driven. |
| D | Add `types.py`, `session.py`, `execution.py`, keep `runner.py` as orchestration boundary. | Clear owners, manageable file sizes, no server bypass. | More files than v1. | Chosen | Best ownership/size balance. |

## Change Inventory (Delta)

| Change ID | Change Type | Current Path | Target Path | Rationale | Impacted Areas | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| C-001 | Add/Modify | `config.py` | same | Add `private_key_file` field/env parsing. | Config/tests/docs | First-class key file. |
| C-002 | Remove | `config.py` | N/A | Remove `base_args`/`allowed_hosts` fields and parsing. | Config/runner/tests/docs | Non-empty env rejected. |
| C-003 | Modify | `config.py` | same | Implement default-host pinning. | Config/server tests | Replaces allowlist. |
| C-004 | Modify | `runner.py` | same | Runner owns orchestration and auth argv builder only. | Runner/tests | Slim after split. |
| C-005 | Modify | tests | same | Update unit/MCP/E2E coverage. | Validation | No legacy expectations. |
| C-006 | Modify | README/runtime docs | same | Document simple/advanced config. | Docs | No supported old env names. |
| C-007 | Add | N/A | `ssh-mcp/src/ssh_mcp/types.py` | Own shared `SshToolResult`. | Server/runner/execution/tests | Tight type owner. |
| C-008 | Add | N/A | `ssh-mcp/src/ssh_mcp/session.py` | Own `SessionRecord`/`SessionManager`. | Runner/tests | Reduces runner size. |
| C-009 | Add | N/A | `ssh-mcp/src/ssh_mcp/execution.py` | Own `ExecutionSpec`, `execute`, `error_result`. | Runner/tests | Reduces runner size. |
| C-010 | Remove/Split | `runner.py` | `session.py` / `execution.py` / `types.py` | Decommission oversized mixed-concern runtime file shape. | Runtime/tests | Must pass line-count gate. |

## Removal / Decommission Plan (Mandatory)

| Item To Remove / Decommission | Why It Becomes Unnecessary | Replaced By | Scope | Notes |
| --- | --- | --- | --- | --- |
| `SshSettings.base_args` | Key/batch auth is first-class/internal. | `private_key_file` + runner auth argv builder. | In This Change | No passthrough retained. |
| `SshSettings.allowed_hosts` | Default host pins one-host configs. | `resolve_target` default-host pinning. | In This Change | No allowlist parser. |
| `_parse_allowed_hosts` / CSV helper | No allowlist env remains. | Unsupported env check. | In This Change | Remove. |
| All-in-one runtime implementation in `runner.py` | Changed file exceeds 500-line gate and mixes session/execution/result concerns. | `types.py`, `session.py`, `execution.py`, slim `runner.py`. | In This Change | No compatibility imports. |
| Docs/examples using old raw args/allowlist mental model | They teach wrong config. | Simple password-file/private-key examples. | In This Change | Grep docs. |

## Final File Responsibility Mapping

| File | Owning Subsystem / Capability Area | Owner / Boundary | Concrete Concern | Why This Is One File | Reuses Shared Structure? |
| --- | --- | --- | --- | --- | --- |
| `ssh-mcp/src/ssh_mcp/types.py` | Shared runtime contract | Result type | `SshToolResult` only. | Shared by server/runner/execution without importing internals. | N/A |
| `ssh-mcp/src/ssh_mcp/session.py` | SSH session state | Session metadata | `SessionRecord`, `SessionManager`, control path/capacity/expiry. | Cohesive state owner. | `ConfigError` |
| `ssh-mcp/src/ssh_mcp/execution.py` | SSH execution/result mapping | Subprocess execution | `ExecutionSpec`, `execute`, `error_result`, output normalization. | Cohesive IO/result owner. | `SshToolResult` |
| `ssh-mcp/src/ssh_mcp/runner.py` | SSH runtime orchestration | Authoritative runtime boundary | Health/open/exec/close orchestration, auth argv/env, remote command composition. | Server-facing lifecycle owner after extracting internals. | session/execution/types |
| `ssh-mcp/src/ssh_mcp/config.py` | SSH config | Settings/input contract | Env parsing, unsupported env rejection, auth exclusivity, target resolution. | Cohesive validation. | `SshSettings` |
| `ssh-mcp/src/ssh_mcp/server.py` | MCP interface | MCP entrypoint | Tool registration/progress/delegation. | Cohesive MCP boundary. | `SshToolResult` |
| Tests/docs | Validation/docs | Evidence/public contract | Validate and document behavior. | Existing paths fit. | N/A |

## Derived Implementation Mapping

| Target File | Change Type | Mapped Spine ID | Owner / Off-Spine Concern | Responsibility | Key APIs / Interfaces | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `types.py` | Add | Return path | Result contract | Define `SshToolResult`. | `SshToolResult` | No behavior. |
| `session.py` | Add | DS-006 | Session state | Manage records and control paths. | `SessionManager`, `SessionRecord` | No command building. |
| `execution.py` | Add | DS-007 | Execution/result mapping | Run subprocess and map result. | `ExecutionSpec`, `execute`, `error_result` | No session state. |
| `runner.py` | Modify/Split | DS-001..DS-005 | Runtime orchestration | Public lifecycle functions and auth command construction. | `run_*`, `create_session_manager` | Must be <500 effective lines. |
| `config.py` | Modify/Remove | DS-004 | Config contract | Key/env/auth/target. | `load_settings`, `resolve_target` | Remove obsolete fields. |
| Tests/docs | Modify | All | Validation/docs | Durable proof and docs. | pytest/docs | No legacy docs. |

## File Placement And Ownership Check (Mandatory)

| File | Current Path | Target Path | Owning Concern / Platform | Path Matches Concern? | Flat-Or-Over-Split Risk | Action | Rationale |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `types.py` | N/A | `ssh-mcp/src/ssh_mcp/types.py` | SSH MCP shared type | Yes | Low | Add | Shared contract, not execution internals. |
| `session.py` | N/A | `ssh-mcp/src/ssh_mcp/session.py` | SSH session state | Yes | Low | Add | Extract real owner. |
| `execution.py` | N/A | `ssh-mcp/src/ssh_mcp/execution.py` | SSH execution/result mapping | Yes | Low | Add | Extract real owner. |
| `runner.py` | same | same | Runtime orchestration | Yes after split | Low | Split/Modify | Retains authoritative runtime boundary. |
| `config.py` | same | same | Config | Yes | Low | Modify | Existing owner fits. |
| `server.py` | same | same | MCP surface | Yes | Low | Keep | Avoid session/execution bypass. |

## Concrete Examples / Shape Guidance

| Topic | Good Example | Bad / Avoided Shape | Why The Example Matters |
| --- | --- | --- | --- |
| Private key config | `SSH_MCP_PRIVATE_KEY_FILE=/Users/normy/.ssh/id_ed25519` | raw OpenSSH flag env | Auth should be semantic. |
| One-host pin | `SSH_MCP_DEFAULT_HOST=lan-box.local`; tool omits host | duplicate host env concepts | Avoid confusing setup. |
| Runtime split | `server -> runner -> session/execution` | `server -> runner` and `server -> session/execution` mixed boundary | Preserves authoritative boundary. |

## Backward-Compatibility Rejection Log (Mandatory)

| Candidate Compatibility Mechanism | Why It Was Considered | Rejection Decision | Replacement Clean-Cut Design |
| --- | --- | --- | --- |
| Continue parsing removed env settings | Existing docs/tests used them. | Rejected | First-class key + default-host pinning. |
| Ignore removed env values silently | Easier upgrade. | Rejected | Fail fast with actionable error. |
| Leave runner oversized because it already was | Minimal movement. | Rejected | Split into real owner files. |
| Re-export legacy session/execution internals through runner aliases | Easier imports. | Rejected | Tests/server use target owner or runner authoritative entrypoints only. |

## Derived Interface Boundary Mapping

| Owning File | Mapped Spine ID | Owner / Off-Spine Concern | Subject Owned | Concern / Responsibility | Interfaces / APIs / Methods | Accepted Identity Shape(s) | Inputs/Outputs | Dependencies |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `config.py` | DS-004 | Config contract | Settings | Env to `SshSettings`. | `load_settings` | env mapping | `SshSettings`/`ConfigError` | stdlib |
| `config.py` | DS-001 | Target resolution | SSH target | Defaults and pinning. | `resolve_target` | host/user/port | `ResolvedTarget` | `SshSettings` |
| `types.py` | Return path | Result contract | Tool result | Shared result shape. | `SshToolResult` | TypedDict fields | type only | stdlib |
| `session.py` | DS-006 | Session state | Session metadata | session id/control/timestamps/capacity. | `SessionManager`, `SessionRecord` | session id | records/count | `ConfigError` |
| `execution.py` | DS-007 | Execution mapping | Subprocess result | execute command and map errors. | `ExecutionSpec`, `execute`, `error_result` | complete spec | `SshToolResult` | subprocess/types |
| `runner.py` | DS-001..DS-005 | Runtime orchestration | SSH lifecycle | health/open/exec/close + auth argv/env. | `run_*`, `create_session_manager` | settings/session/target/command | `SshToolResult` | config/session/execution |
| `server.py` | DS-001..DS-003 | MCP boundary | Tool calls | Stable tool surface. | `create_server` tools | MCP params | `SshToolResult` | runner/types |

## Scope-Appropriate Separation Of Concerns Check

- Non-UI scope: file/service boundaries are clear.
- Config owns env/input validation; runner owns orchestration/argv policy; session owns session state; execution owns subprocess/result mapping; server owns MCP entrypoints.
- The package remains flat because all files are peer concerns under one small SSH MCP package. Adding nested folders would over-split without improving ownership readability.

## Interface Boundary Check (Mandatory)

| Interface / API / Method | Subject Owned | Responsibility Is Singular? | Identity Shape Is Explicit? | Ambiguous-ID Risk | Corrective Action |
| --- | --- | --- | --- | --- | --- |
| `load_settings(env)` | Settings | Yes | Yes: env names | Low | Add key/remove legacy. |
| `resolve_target(settings, host, user, port)` | SSH target | Yes | Yes | Low | Default-host pinning. |
| `create_session_manager(settings)` | Session manager creation | Yes | Yes: settings/session dir | Low | Keep in runner as server-facing runtime boundary. |
| `SessionManager.*` | Session state | Yes | Yes: session id/record | Low | Move to `session.py`. |
| `execute(spec, timeout, max_output)` | Subprocess execution | Yes | Yes: `ExecutionSpec` | Low | Move to `execution.py`. |
| `run_open_session`, `run_session_exec`, `run_close_session` | SSH lifecycle | Yes | Yes | Low | Use internal auth args. |

## Naming Decisions

| Item Type | Current Name | Proposed Name | Reason | Notes |
| --- | --- | --- | --- | --- |
| Env/API | N/A | `SSH_MCP_PRIVATE_KEY_FILE` | Matches normal SSH wording. | Public key remains remote. |
| Field | N/A | `private_key_file` | Singular auth field. | In `SshSettings`. |
| File | N/A | `types.py` | Shared type owner. | Avoids internal imports. |
| File | N/A | `session.py` | Session state owner. | Extract from runner. |
| File | N/A | `execution.py` | Subprocess/result owner. | Extract from runner. |
| Field/env | `base_args`, removed env | Removed | Exposes raw implementation detail. | No raw args replacement. |
| Field/env | `allowed_hosts`, removed env | Removed | Duplicates target model. | Default host pins normal config. |

## Naming Drift Check (Mandatory)

| Item | Current Responsibility | Does Name Still Match? | Corrective Action | Mapped Change ID |
| --- | --- | --- | --- | --- |
| `base_args` | Raw OpenSSH flags used for auth/policy. | No | Remove. | C-002 |
| `allowed_hosts` | Host guard separate from target default. | No | Remove. | C-002 |
| `runner.py` | Orchestration + session + execution + result mapping. | Partially | Split. | C-010 |
| `SshToolResult` in runner | Shared contract. | No placement mismatch | Move. | C-007 |
| `SessionManager` in runner | Session state. | No placement mismatch | Move. | C-008 |
| `ExecutionSpec`/execute in runner | Subprocess/result mapping. | No placement mismatch | Move. | C-009 |

## Existing-Structure Bias Check (Mandatory)

| Candidate Area | Current-File-Layout Bias Risk | Architecture-First Alternative | Decision | Why |
| --- | --- | --- | --- | --- |
| Keep old public env fields because current tests use them | High | Semantic key/default-host fields | Change | Existing usage is the smell. |
| Keep runtime internals in `runner.py` because current imports work | High | Extract types/session/execution while preserving runner boundary | Change | Changed file must pass source-size gate. |
| Create nested runtime folder | Medium | Flat peer files under package | Keep flat package | The package is small; peer files with clear names are enough. |

## Anti-Hack Check (Mandatory)

| Candidate Change | Shortcut/Hack Risk | Proper Structural Fix | Decision | Notes |
| --- | --- | --- | --- | --- |
| Transform private key into synthetic raw args | High | Direct auth argv builder. | Reject shortcut | Avoid hidden legacy shape. |
| Auto-fill old allowlist from default host | High | Remove allowlist. | Reject shortcut | Avoid dual model. |
| Server imports session/execution internals to construct results | Medium | Server uses runner/tools and shared type only. | Reject shortcut | Preserve authoritative runtime boundary. |
| Source-size exception for runner | High | Split real owners. | Reject shortcut | Workflow hard gate. |

## Dependency Flow And Cross-Reference Risk

| Dependency Boundary | Upstream Dependencies | Downstream Dependents | Cross-Reference Risk | Mitigation / Boundary Strategy |
| --- | --- | --- | --- | --- |
| `server -> runner/types` | Server imports runtime entrypoints and result type | MCP clients | Low | No session/execution imports in server. |
| `runner -> config/session/execution/types` | Runner coordinates owners | Server/tests | Low | One-way dependency. |
| `execution -> types` | Execution returns shared result | Runner | Low | No config/session imports. |
| `session -> config` | Session raises `ConfigError` | Runner | Low | Error type only; no runtime cycle. |

## Decommission / Cleanup Plan

| Item To Remove/Rename | Cleanup Actions | Legacy Removal Notes | Verification |
| --- | --- | --- | --- |
| Removed env support | Delete fields/parser/usages/docs; add unsupported-env tests. | No alias/passthrough. | AC-004/AC-005/AC-012 |
| Oversized `runner.py` internals | Move result/session/execution concerns to owner files; update imports/tests. | No compatibility re-export aliases. | line-count + tests |
| E2E raw key args | Use `private_key_file`; prepare test `known_hosts` via isolated HOME. | No raw args settings. | AC-010 |

## Data Models

Target `SshSettings` fields:

- Runtime/advanced: `command`, `timeout_seconds`, `max_command_chars`, `max_output_chars`, `health_check_args`, `session_idle_timeout_seconds`, `max_sessions`, `session_dir`.
- Target defaults: `default_host`, `default_user`, `default_port`.
- Auth sources: `password`, `password_file`, `private_key_file`.

Target runtime contracts:

- `SshToolResult`: shared structured MCP result dictionary.
- `ExecutionSpec`: complete subprocess/result context passed from runner to execution.
- `SessionRecord`: session id, destination, host/user/port, default cwd, control path, timestamps.

Auth invariant: at most one of `password`, `password_file`, `private_key_file` may be configured.

## Error Handling And Edge Cases

- Missing host and no default host: validation error.
- Default host set and explicit different host passed: validation error with instruction to create another MCP config.
- Non-empty removed env keys: config error naming unsupported setting and replacement.
- Password + password file or private key + any password source: config error.
- Password file unreadable/empty/carriage-return: validation error.
- Private key unreadable/invalid: OpenSSH execution failure surfaced in structured result.
- No password/private key: runner adds `BatchMode=yes` so SSH agent/config can work without hanging.
- Health check uses command + health args only, not auth args.
- Host-key verification: OpenSSH default; docs and Docker E2E prepare normal known_hosts rather than adding bypass settings.
- Changed source files must be <=500 effective non-empty lines.

## Use-Case Coverage Matrix (Design Gate)

| use_case_id | Requirement | Use Case | Primary Path Covered | Fallback Path Covered | Error Path Covered | Runtime Call Stack Section |
| --- | --- | --- | --- | --- | --- | --- |
| UC-001 | REQ-002, REQ-003 | Load minimal password-file config. | Yes | N/A | Yes | Stage 4 UC-001 |
| UC-002 | REQ-002, REQ-003 | Load minimal inline password config. | Yes | N/A | Yes | Stage 4 UC-002 |
| UC-003 | REQ-001, REQ-003, REQ-007 | Load minimal private-key config. | Yes | N/A | Yes | Stage 4 UC-003 |
| UC-004 | REQ-001, REQ-002 | Reject ambiguous auth config. | Yes | N/A | Yes | Stage 4 UC-004 |
| UC-005 | REQ-004 | Reject removed legacy env knobs. | Yes | N/A | Yes | Stage 4 UC-005 |
| UC-006 | REQ-003, REQ-006 | Resolve target with default-host pinning. | Yes | N/A | Yes | Stage 4 UC-006 |
| UC-007 | REQ-001, REQ-002, REQ-007 | Build OpenSSH commands with internal auth/default options. | Yes | Yes | Yes | Stage 4 UC-007 |
| UC-008 | REQ-005, REQ-007 | Preserve session lifecycle and structured results. | Yes | Yes | Yes | Stage 4 UC-008 |
| UC-009 | REQ-005, REQ-008 | Document simple config first, advanced separately. | Yes | N/A | Yes | Stage 4 UC-009 |

## Migration / Rollout

No compatibility rollout is provided. Users with old raw-args key setup must replace it with `SSH_MCP_PRIVATE_KEY_FILE`. Users with separate host allowlist setup should rely on `SSH_MCP_DEFAULT_HOST` for one-host pinning. Multiple hosts use multiple MCP server entries or omit a default host and pass explicit host intentionally.

## Change Traceability To Implementation

| Change ID | Implementation Task(s) | Verification | Status |
| --- | --- | --- | --- |
| C-001 | Add `private_key_file`. | Config tests SC-001/SC-002. | Planned/In progress |
| C-002 | Remove raw args/allowlist support. | Unsupported env tests + docs grep. | Planned/In progress |
| C-003 | Default-host pinning. | Config tests SC-004. | Planned/In progress |
| C-004 | Runner-local auth argv builder. | Runner tests SC-005/SC-006/SC-007. | Planned/In progress |
| C-005 | Update durable tests. | Full pytest and optional Docker SC-008. | Planned/In progress |
| C-006 | Update docs. | Docs grep/review SC-009. | Planned/In progress |
| C-007 | Add shared result type file. | Import/tests + line count. | Planned |
| C-008 | Add session state file. | Session lifecycle tests + line count. | Planned |
| C-009 | Add execution/result file. | Runner tests + line count. | Planned |
| C-010 | Split runner. | line-count <=500 + full tests. | Planned |

## Design Feedback Loop Notes

| Date | Trigger | Classification | Design Smell | Requirements Updated? | Design Update Applied | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-08-18 | Initial Stage 3 draft | N/A | Legacy raw args/allowlist public knobs | No | Clean-cut target recorded. | Superseded by v2 |
| 2026-08-18 | Stage 6 source-size check | Design Impact | Oversized changed runtime catch-all file | No | Added runtime split into types/session/execution/runner. | Current |

## Open Questions

None blocking. Removing raw OpenSSH option passthrough and splitting runtime ownership are intentional under the workflow's no-legacy and source-size policies.
