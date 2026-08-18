# Future-State Runtime Call Stacks - Simplify SSH MCP Configuration

## Design Basis

- Scope Classification: `Medium`
- Call Stack Version: `v2`
- Requirements: `tickets/done/simplify-ssh-mcp-config/requirements.md` (`Design-ready`)
- Source Artifact: `tickets/done/simplify-ssh-mcp-config/proposed-design.md`
- Source Design Version: `v2`
- Referenced Sections: Data-Flow Spine Inventory, Ownership Map, Runtime Split, Error Handling And Edge Cases

## Future-State Modeling Rule

This document models the target behavior only. It intentionally excludes legacy raw OpenSSH arg passthrough, separate host allowlist checks, compatibility fallback branches, and the old all-in-one runtime file shape.

## Use Case Index

| use_case_id | Spine ID(s) | Spine Scope | Governing Owner | Source Type | Requirement ID(s) | Design-Risk Objective | Use Case Name | Coverage Target |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| UC-001 | DS-004, DS-001, DS-007 | Bounded Local + Primary End-to-End | config/runner/execution | Requirement | REQ-002, REQ-003 | N/A | Load minimal password-file MCP env config | Primary/Error |
| UC-002 | DS-004, DS-001, DS-007 | Bounded Local + Primary End-to-End | config/runner/execution | Requirement | REQ-002, REQ-003 | N/A | Load minimal inline password MCP env config | Primary/Error |
| UC-003 | DS-004, DS-005, DS-001, DS-007 | Bounded Local + Primary End-to-End | config/runner/execution | Requirement | REQ-001, REQ-003, REQ-007 | N/A | Load minimal private-key MCP env config | Primary/Error |
| UC-004 | DS-004 | Bounded Local | `ssh_mcp.config` | Requirement | REQ-001, REQ-002 | N/A | Reject ambiguous auth configuration | Error |
| UC-005 | DS-004 | Bounded Local | `ssh_mcp.config` | Requirement | REQ-004 | N/A | Reject removed legacy env knobs | Error |
| UC-006 | DS-004, DS-001 | Bounded Local + Primary End-to-End | `ssh_mcp.config` | Requirement | REQ-003, REQ-006 | N/A | Resolve target with default-host pinning | Primary/Error |
| UC-007 | DS-005, DS-001, DS-002, DS-003 | Bounded Local + Primary End-to-End | `ssh_mcp.runner` | Requirement | REQ-001, REQ-002, REQ-007 | Uniform internal auth argv across lifecycle commands. | Build OpenSSH commands with internal auth/default options | Primary/Fallback/Error |
| UC-008 | DS-001, DS-002, DS-003, DS-006, DS-007 | Primary End-to-End + Bounded Local | runner/session/execution | Requirement | REQ-005, REQ-007 | Preserve lifecycle semantics after runtime split. | Preserve session lifecycle and structured MCP results | Primary/Fallback/Error |
| UC-009 | DS-004, DS-005 | Bounded Local | docs/validation | Requirement | REQ-005, REQ-008 | Prevent docs/tests from retaining legacy env paths. | Document simple config first and advanced separately | Primary/Error |
| UC-010 | DS-006, DS-007 | Bounded Local | session/execution | Design-Risk | REQ-005 | Verify runtime split preserves file-size and authoritative boundary constraints. | Split runtime owners without server bypass | Primary/Error |

## Transition Notes

- No temporary migration behavior is modeled.
- Stale non-empty legacy env variables cause immediate `ConfigError`.
- `ssh_mcp.runner` remains the authoritative runtime entrypoint for `ssh_mcp.server`; session and execution files are internal runtime owners.

## Use Case: UC-001 Load Minimal Password-File MCP Env Config

### Spine Context

- Spine ID(s): DS-004, DS-001, DS-007
- Governing Owner: `ssh_mcp.config` for env/auth; `ssh_mcp.runner` for lifecycle; `ssh_mcp.execution` for result mapping.

### Goal

Load host/user/optional-port plus `SSH_MCP_PASSWORD_FILE`, then open a session using askpass-backed password auth.

### Preconditions

Password file exists and no other auth source is configured.

### Expected Outcome

Settings contain `password_file`; runner uses askpass env; execution returns structured result.

### Primary Runtime Call Stack

```text
[ENTRY] ssh-mcp/src/ssh_mcp/server.py:create_server(settings=None)
├── ssh-mcp/src/ssh_mcp/config.py:load_settings(env)
│   ├── _reject_removed_env_settings(env) [ERROR if removed setting is non-empty]
│   ├── _parse_optional_host/_identifier/_port(...)
│   ├── _parse_optional_file("SSH_MCP_PASSWORD_FILE")
│   └── _validate_auth_source_exclusivity(...)
├── ssh-mcp/src/ssh_mcp/runner.py:create_session_manager(settings)
│   └── ssh-mcp/src/ssh_mcp/session.py:SessionManager(session_dir) [STATE]
└── ssh-mcp/src/ssh_mcp/server.py:ssh_open_session(host=None, user=None, port=None, cwd=None)
    └── ssh-mcp/src/ssh_mcp/runner.py:run_open_session(...)
        ├── ssh-mcp/src/ssh_mcp/config.py:resolve_target(...)
        ├── ssh-mcp/src/ssh_mcp/config.py:resolve_password(settings) [IO]
        ├── ssh-mcp/src/ssh_mcp/runner.py:_build_execution_env(...)
        ├── ssh-mcp/src/ssh_mcp/runner.py:_build_open_command(..., password_auth_enabled=True)
        ├── ssh-mcp/src/ssh_mcp/execution.py:execute(ExecutionSpec(...)) [IO subprocess]
        └── ssh-mcp/src/ssh_mcp/session.py:SessionManager.add(record) [STATE]
```

### Branching / Fallback Paths

```text
[ERROR] password file unreadable/empty/invalid
ssh-mcp/src/ssh_mcp/config.py:resolve_password(...)
└── ssh-mcp/src/ssh_mcp/runner.py:run_open_session(...)
    └── ssh-mcp/src/ssh_mcp/execution.py:error_result(...)
```

### State And Data Transformations

- Env path string -> expanded absolute `settings.password_file`.
- Password file contents -> child env `SSH_MCP_TOOL_PASSWORD` only.
- Execution output -> `SshToolResult` from `types.py`.

### Coverage Status

- Primary Path: `Covered`
- Fallback Path: `N/A`
- Error Path: `Covered`

## Use Case: UC-002 Load Minimal Inline Password MCP Env Config

### Spine Context

- Spine ID(s): DS-004, DS-001, DS-007
- Governing Owner: config/runner/execution.

### Goal

Load `SSH_MCP_PASSWORD` and use askpass-backed password auth without placing the password in argv.

### Preconditions

Inline password is injected into env and no other auth source is set.

### Expected Outcome

OpenSSH command contains password auth flags; child env contains password; structured command list does not contain password.

### Primary Runtime Call Stack

```text
[ENTRY] ssh-mcp/src/ssh_mcp/config.py:load_settings(env)
├── _parse_optional_secret("SSH_MCP_PASSWORD")
├── _parse_optional_file("SSH_MCP_PASSWORD_FILE")
├── _parse_optional_file("SSH_MCP_PRIVATE_KEY_FILE")
└── _validate_auth_source_exclusivity(...)
[ENTRY] ssh-mcp/src/ssh_mcp/server.py:ssh_open_session(...)
└── ssh-mcp/src/ssh_mcp/runner.py:run_open_session(...)
    ├── ssh-mcp/src/ssh_mcp/runner.py:_ensure_askpass_script(path) [IO]
    ├── ssh-mcp/src/ssh_mcp/runner.py:_build_execution_env(...)
    ├── ssh-mcp/src/ssh_mcp/runner.py:_build_auth_args(settings, password_auth_enabled=True)
    └── ssh-mcp/src/ssh_mcp/execution.py:execute(...) [IO subprocess]
```

### Branching / Fallback Paths

```text
[ERROR] password contains carriage return
ssh-mcp/src/ssh_mcp/config.py:_parse_optional_secret(...)
└── ConfigError
```

### Coverage Status

- Primary Path: `Covered`
- Fallback Path: `N/A`
- Error Path: `Covered`

## Use Case: UC-003 Load Minimal Private-Key MCP Env Config

### Spine Context

- Spine ID(s): DS-004, DS-005, DS-001, DS-007
- Governing Owner: config + runner + execution.

### Goal

Load `SSH_MCP_PRIVATE_KEY_FILE` and build non-interactive OpenSSH commands.

### Preconditions

Private key path is configured; matching public key is already installed remotely.

### Expected Outcome

Open/exec/close commands include `-i <private_key>`, `IdentitiesOnly=yes`, and `BatchMode=yes` before destination.

### Primary Runtime Call Stack

```text
[ENTRY] ssh-mcp/src/ssh_mcp/config.py:load_settings(env)
├── _parse_optional_file("SSH_MCP_PRIVATE_KEY_FILE")
└── _validate_auth_source_exclusivity(...)
[ENTRY] ssh-mcp/src/ssh_mcp/runner.py:run_open_session(...)
├── ssh-mcp/src/ssh_mcp/config.py:resolve_target(...)
├── ssh-mcp/src/ssh_mcp/runner.py:_build_auth_args(settings, password_auth_enabled=False)
│   └── returns ["-i", key, "-o", "IdentitiesOnly=yes", "-o", "BatchMode=yes"]
├── ssh-mcp/src/ssh_mcp/runner.py:_build_open_command(...)
└── ssh-mcp/src/ssh_mcp/execution.py:execute(...) [IO subprocess]
```

### Branching / Fallback Paths

```text
[ERROR] OpenSSH rejects unreadable/invalid private key
ssh-mcp/src/ssh_mcp/execution.py:execute(...)
└── ssh-mcp/src/ssh_mcp/execution.py:error_result(error_type="execution", stderr=...)
```

### Coverage Status

- Primary Path: `Covered`
- Fallback Path: `N/A`
- Error Path: `Covered`

## Use Case: UC-004 Reject Ambiguous Auth Configuration

### Spine Context

- Spine ID(s): DS-004
- Governing Owner: `ssh_mcp.config`.

### Goal / Expected Outcome

Reject any env with more than one auth source before server startup.

### Primary Runtime Call Stack

```text
[ENTRY] ssh-mcp/src/ssh_mcp/config.py:load_settings(env)
├── _parse_optional_secret("SSH_MCP_PASSWORD")
├── _parse_optional_file("SSH_MCP_PASSWORD_FILE")
├── _parse_optional_file("SSH_MCP_PRIVATE_KEY_FILE")
└── _validate_auth_source_exclusivity(...) [ERROR]
    └── raise ConfigError("Set at most one SSH auth source...")
```

### Coverage Status

- Primary Path: `Covered`
- Fallback Path: `N/A`
- Error Path: `Covered`

## Use Case: UC-005 Reject Removed Legacy Env Knobs

### Spine Context

- Spine ID(s): DS-004
- Governing Owner: `ssh_mcp.config`.

### Goal / Expected Outcome

Reject non-empty removed env settings with actionable messages.

### Primary Runtime Call Stack

```text
[ENTRY] ssh-mcp/src/ssh_mcp/config.py:load_settings(env)
├── _reject_removed_env_settings(env)
│   ├── [ERROR] removed raw args setting non-empty -> ConfigError(replacement mentions private key file)
│   └── [ERROR] removed host allowlist setting non-empty -> ConfigError(replacement mentions default-host pinning)
└── continue only when removed env settings are unset/empty
```

### Coverage Status

- Primary Path: `Covered`
- Fallback Path: `N/A`
- Error Path: `Covered`

## Use Case: UC-006 Resolve Target With Default-Host Pinning

### Spine Context

- Spine ID(s): DS-004, DS-001
- Governing Owner: `ssh_mcp.config`.

### Goal / Expected Outcome

Use default host when omitted, allow same explicit host, reject different explicit host.

### Primary Runtime Call Stack

```text
[ENTRY] ssh-mcp/src/ssh_mcp/server.py:ssh_open_session(host?)
└── ssh-mcp/src/ssh_mcp/runner.py:run_open_session(...)
    └── ssh-mcp/src/ssh_mcp/config.py:resolve_target(settings, host, user, port)
        ├── normalize explicit host or use settings.default_host
        ├── [ERROR] if explicit host differs from configured default host
        ├── resolve user from explicit/default user
        ├── resolve port from explicit/default port
        └── return ResolvedTarget(destination)
```

### Branching / Fallback Paths

```text
[FALLBACK] host omitted
resolve_target(...)
└── use settings.default_host
```

```text
[ERROR] explicit host differs
resolve_target(...)
└── raise ConfigError("host must match SSH_MCP_DEFAULT_HOST...")
```

### Coverage Status

- Primary Path: `Covered`
- Fallback Path: `Covered`
- Error Path: `Covered`

## Use Case: UC-007 Build OpenSSH Commands With Internal Auth/Default Options

### Spine Context

- Spine ID(s): DS-005, DS-001, DS-002, DS-003
- Governing Owner: `ssh_mcp.runner`.

### Goal / Expected Outcome

Build open/exec/close commands without any public raw args field.

### Primary Runtime Call Stack

```text
[ENTRY] ssh-mcp/src/ssh_mcp/runner.py:run_open_session(...)
├── _build_execution_env(settings, manager)
├── _build_auth_args(settings, password_auth_enabled)
├── _build_open_command(...)
└── ssh-mcp/src/ssh_mcp/execution.py:execute(ExecutionSpec(...))

[ENTRY] ssh-mcp/src/ssh_mcp/runner.py:run_session_exec(...)
├── _build_execution_env(settings, manager)
├── _build_auth_args(settings, password_auth_enabled)
├── _build_session_exec_command(...)
└── ssh-mcp/src/ssh_mcp/execution.py:execute(ExecutionSpec(...))

[ENTRY] ssh-mcp/src/ssh_mcp/runner.py:run_close_session(...)
├── _build_auth_args(settings, password_auth_enabled=False)
├── _build_close_command(...)
└── ssh-mcp/src/ssh_mcp/execution.py:execute(ExecutionSpec(...))
```

### Branching / Fallback Paths

```text
[FALLBACK] no explicit auth source
_build_auth_args(settings, password_auth_enabled=False)
└── returns ["-o", "BatchMode=yes"]
```

```text
[ERROR] subprocess timeout/non-zero
ssh-mcp/src/ssh_mcp/execution.py:execute(...)
└── return timeout/execution SshToolResult
```

### Coverage Status

- Primary Path: `Covered`
- Fallback Path: `Covered`
- Error Path: `Covered`

## Use Case: UC-008 Preserve Session Lifecycle And Structured MCP Results

### Spine Context

- Spine ID(s): DS-001, DS-002, DS-003, DS-006, DS-007
- Governing Owner: runner/session/execution.

### Goal / Expected Outcome

Open a session, execute commands, close it, and return structured results while session state and execution mapping live in separate files.

### Primary Runtime Call Stack

```text
[ENTRY] ssh-mcp/src/ssh_mcp/server.py:ssh_open_session(...)
└── ssh-mcp/src/ssh_mcp/runner.py:run_open_session(...)
    ├── ssh-mcp/src/ssh_mcp/session.py:SessionManager.ensure_capacity(...) [STATE]
    ├── ssh-mcp/src/ssh_mcp/session.py:SessionManager.control_path_for(session_id)
    ├── ssh-mcp/src/ssh_mcp/execution.py:execute(open_spec) [IO]
    └── ssh-mcp/src/ssh_mcp/session.py:SessionManager.add(record) [STATE]
[ENTRY] ssh-mcp/src/ssh_mcp/server.py:ssh_session_exec(...)
└── ssh-mcp/src/ssh_mcp/runner.py:run_session_exec(...)
    ├── ssh-mcp/src/ssh_mcp/session.py:SessionManager.get(session_id) [STATE]
    ├── ssh-mcp/src/ssh_mcp/runner.py:_compose_remote_command(command, cwd)
    ├── ssh-mcp/src/ssh_mcp/execution.py:execute(exec_spec) [IO]
    └── ssh-mcp/src/ssh_mcp/session.py:SessionManager.touch(session_id, time.time()) [STATE]
[ENTRY] ssh-mcp/src/ssh_mcp/server.py:ssh_close_session(...)
└── ssh-mcp/src/ssh_mcp/runner.py:run_close_session(...)
    ├── ssh-mcp/src/ssh_mcp/session.py:SessionManager.pop(session_id) [STATE]
    ├── ssh-mcp/src/ssh_mcp/execution.py:execute(close_spec) [IO]
    └── ssh-mcp/src/ssh_mcp/runner.py:_safe_unlink(control_path) [IO]
```

### Branching / Fallback Paths

```text
[FALLBACK] idle sessions expired before request
ssh-mcp/src/ssh_mcp/runner.py:_cleanup_expired_sessions(...)
├── ssh-mcp/src/ssh_mcp/session.py:SessionManager.remove_expired(...) [STATE]
├── ssh-mcp/src/ssh_mcp/runner.py:_best_effort_close_control_master(...)
└── ssh-mcp/src/ssh_mcp/runner.py:_safe_unlink(control_path) [IO]
```

```text
[ERROR] missing/closed session
ssh-mcp/src/ssh_mcp/session.py:SessionManager.get/pop(...)
└── ssh-mcp/src/ssh_mcp/execution.py:error_result(error_type="execution", ...)
```

### Coverage Status

- Primary Path: `Covered`
- Fallback Path: `Covered`
- Error Path: `Covered`

## Use Case: UC-009 Document Simple Config First And Advanced Settings Separately

### Spine Context

- Spine ID(s): DS-004, DS-005
- Governing Owner: docs/validation.

### Goal / Expected Outcome

Docs include password-file and private-key config examples; docs do not list removed env settings as supported controls.

### Primary Runtime Call Stack

```text
[ENTRY] developer/user reads ssh-mcp/README.md
├── simple destination/auth examples
├── advanced optional defaults
└── security notes: password env inheritance, private key is local private key, host-key verification stays default

[ENTRY] developer/user reads ssh-mcp/docs/runtime-flow.md
├── runtime layers include config/runner/session/execution/types ownership
├── bounded controls list excludes removed supported settings
└── verification section maps tests/E2E
```

### Coverage Status

- Primary Path: `Covered`
- Fallback Path: `N/A`
- Error Path: `Covered`

## Use Case: UC-010 Split Runtime Owners Without Server Bypass

### Spine Context

- Spine ID(s): DS-006, DS-007
- Governing Owner: runner/session/execution/types.

### Goal / Expected Outcome

Runtime source files stay below 500 effective non-empty lines and dependencies stay one-way: `server -> runner/types`, `runner -> session/execution/config/types`.

### Primary Runtime Call Stack

```text
[ENTRY] ssh-mcp/src/ssh_mcp/server.py:create_server(...)
├── imports ssh-mcp/src/ssh_mcp/types.py:SshToolResult  # shared contract only
├── imports ssh-mcp/src/ssh_mcp/runner.py:create_session_manager/run_*  # authoritative runtime boundary
└── does not import ssh-mcp/src/ssh_mcp/session.py or execution.py internals

[ENTRY] ssh-mcp/src/ssh_mcp/runner.py:run_open_session(...)
├── ssh-mcp/src/ssh_mcp/session.py:SessionManager(...)
├── ssh-mcp/src/ssh_mcp/execution.py:ExecutionSpec(...)
└── ssh-mcp/src/ssh_mcp/execution.py:execute(...)
```

### Branching / Fallback Paths

```text
[ERROR] any changed source file exceeds 500 effective non-empty lines
Stage 8/source-size check
└── fail review and require design-impact split/refactor
```

### Coverage Status

- Primary Path: `Covered`
- Fallback Path: `N/A`
- Error Path: `Covered`

## Overall Design Smell Check

- Legacy/backward-compatibility branch present? `No`
- Tight coupling/cyclic cross-subsystem dependency introduced? `No`
- Naming-to-responsibility drift detected? `No`
- Missing use cases from requirements? `No`
- Runtime split represented after Stage 6 re-entry? `Yes`
