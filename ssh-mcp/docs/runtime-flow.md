# SSH MCP Runtime Flow

## Tool Surface

- `ssh_health_check`
- `ssh_open_session`
- `ssh_session_exec`
- `ssh_close_session`

## Runtime Layers

1. `ssh_mcp.server`: MCP tool entrypoints, progress reporting, and structured output delegation.
2. `ssh_mcp.config`: environment parsing, auth-source validation, target defaults, and default-host pinning.
3. `ssh_mcp.runner`: authoritative runtime orchestration boundary for health/open/exec/close, OpenSSH command construction, and non-interactive auth wiring.
4. `ssh_mcp.session`: session metadata, session IDs, control-socket paths, capacity checks, timestamp updates, and idle expiry.
5. `ssh_mcp.execution`: subprocess execution, timeout/non-zero/OS error mapping, output truncation, and structured result construction.
6. `ssh_mcp.types`: shared structured-output type contract used by server, runner, and execution.

## Configuration Flow

1. `load_settings` reads the MCP environment once during server creation.
2. Destination settings are host, user, and optional port.
3. Auth settings are mutually exclusive: private key file, password file, or inline password.
4. If a default host is configured, it pins the server to that host; tool calls can omit host or pass that same host only.
5. Runtime guardrails such as timeout, output limit, command length, idle timeout, and session count keep their default values unless advanced environment settings override them.

## Session Lifecycle

1. `ssh_open_session` validates target input and opens an SSH control master using a control socket.
2. Password auth uses an internal `SSH_ASKPASS` script and child-process environment so the password is not passed on the command line.
3. Private-key auth adds the key path and non-interactive key options internally.
4. No-password/no-key mode also runs in OpenSSH batch mode so normal SSH config or ssh-agent can be used without hanging for prompts.
5. `ssh_session_exec` validates `session_id`, asks the session owner for metadata, reuses the control socket, runs one remote command, and updates last-used timestamp.
6. `ssh_close_session` removes session metadata through the session owner, closes the SSH control master, and unlinks the local control socket.
7. Idle sessions are expired automatically based on configured timeout.
8. Session IDs are short 8-character lowercase hex tokens for easier manual use.

## Runtime Ownership Boundaries

- `server` is the public MCP boundary and delegates lifecycle behavior to `runner`.
- `runner` is the single authoritative runtime entrypoint above session/execution internals; callers should not coordinate those internals directly.
- `config` owns public environment variables and validation. It rejects stale removed config concepts instead of silently interpreting them.
- `session` owns local in-memory session state and control-socket path selection.
- `execution` owns child process execution and consistent result/error shapes.
- OpenSSH owns host-key trust, key validity, and server authentication outcomes.

## Error Mapping

- Validation failures: `error_type = validation`
- Missing command binary: `error_type = config`
- Timeout: `error_type = timeout`
- Non-zero exit or missing/expired session: `error_type = execution`

## Bounded Controls

### Simple controls

- `SSH_MCP_DEFAULT_HOST`
- `SSH_MCP_DEFAULT_USER`
- `SSH_MCP_DEFAULT_PORT`
- `SSH_MCP_PRIVATE_KEY_FILE`
- `SSH_MCP_PASSWORD_FILE`
- `SSH_MCP_PASSWORD`

### Advanced controls

- `SSH_MCP_COMMAND`
- `SSH_MCP_TIMEOUT_SECONDS`
- `SSH_MCP_MAX_COMMAND_CHARS`
- `SSH_MCP_MAX_OUTPUT_CHARS`
- `SSH_MCP_HEALTH_CHECK_ARGS`
- `SSH_MCP_SESSION_IDLE_TIMEOUT_SECONDS`
- `SSH_MCP_MAX_SESSIONS`
- `SSH_MCP_SESSION_DIR`
- `SSH_MCP_NAME`
- `SSH_MCP_INSTRUCTIONS`

## Verification

- Unit and integration-style MCP tests run with:
  - `uv --directory ssh-mcp run --frozen --extra test pytest tests/test_config.py tests/test_runner.py tests/test_server.py`
- Docker-backed E2E lifecycle tests run with:
  - `SSH_MCP_RUN_DOCKER_E2E=1 uv --directory ssh-mcp run --frozen --extra test pytest tests/test_e2e_docker.py`
- Runtime docs should keep simple controls and advanced controls separated so normal one-host setup stays host/user/optional-port plus one auth source.
