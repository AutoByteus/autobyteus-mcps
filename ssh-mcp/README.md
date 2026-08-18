# ssh-mcp

MCP server that wraps local `ssh` for bounded, non-interactive remote command execution with reusable session lifecycle control.

Detailed runtime notes: `docs/runtime-flow.md`.

## Tools

- `ssh_health_check`: validates SSH command availability and runs a configurable probe (default: `ssh -V`).
- `ssh_open_session`: opens one reusable SSH session and returns `session_id`.
- `ssh_session_exec`: runs one command using an existing `session_id`.
- `ssh_close_session`: closes one `session_id` and releases control socket resources.

## Simple Environment

Configure SSH the same way you would in a normal SSH client: host, user, optional port, and one auth source.

### Destination

- `SSH_MCP_DEFAULT_HOST` (optional, but recommended for one-host MCP configs)
- `SSH_MCP_DEFAULT_USER` (optional)
- `SSH_MCP_DEFAULT_PORT` (optional; OpenSSH default is used when omitted)

When `SSH_MCP_DEFAULT_HOST` is set, tool calls may omit `host` or pass the same host. A different explicit host is rejected. For multiple fixed hosts, create multiple MCP server entries.

### Auth Sources

Set at most one:

- `SSH_MCP_PRIVATE_KEY_FILE` (optional; local private key path)
- `SSH_MCP_PASSWORD_FILE` (optional; path to a file containing the password)
- `SSH_MCP_PASSWORD` (optional; useful when a secret manager injects env directly)

The public key matching `SSH_MCP_PRIVATE_KEY_FILE` must already be installed on the remote host.

## Advanced Optional Environment

These have defaults and are not needed for normal setup:

- `SSH_MCP_COMMAND` (default: `ssh`)
- `SSH_MCP_TIMEOUT_SECONDS` (default: `60`)
- `SSH_MCP_MAX_COMMAND_CHARS` (default: `4000`)
- `SSH_MCP_MAX_OUTPUT_CHARS` (default: `20000`)
- `SSH_MCP_HEALTH_CHECK_ARGS` (default: `-V`)
- `SSH_MCP_SESSION_IDLE_TIMEOUT_SECONDS` (default: `300`)
- `SSH_MCP_MAX_SESSIONS` (default: `32`)
- `SSH_MCP_SESSION_DIR` (optional)
- `SSH_MCP_NAME` (default: `ssh-mcp`)
- `SSH_MCP_INSTRUCTIONS` (optional custom instructions)

## Run

```bash
python -m pip install -e .
ssh-mcp-server
```

With `uv` from this repository, replace the directory with your local checkout:

```bash
uv --directory /path/to/autobyteus_mcps/ssh-mcp run python -m ssh_mcp.server
```

## MCP Config Examples

### Single Host With Password File

```json
{
  "mcpServers": {
    "ssh_remote": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/normy/autobyteus_org/autobyteus_mcps/ssh-mcp",
        "run",
        "python",
        "-m",
        "ssh_mcp.server"
      ],
      "env": {
        "SSH_MCP_DEFAULT_HOST": "203.0.113.10",
        "SSH_MCP_DEFAULT_USER": "ubuntu",
        "SSH_MCP_DEFAULT_PORT": "22",
        "SSH_MCP_PASSWORD_FILE": "/Users/normy/.codex/secrets/ssh_remote_password"
      }
    }
  }
}
```

### Single Host With Private Key

```json
{
  "mcpServers": {
    "ssh_remote": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/normy/autobyteus_org/autobyteus_mcps/ssh-mcp",
        "run",
        "python",
        "-m",
        "ssh_mcp.server"
      ],
      "env": {
        "SSH_MCP_DEFAULT_HOST": "203.0.113.10",
        "SSH_MCP_DEFAULT_USER": "ubuntu",
        "SSH_MCP_PRIVATE_KEY_FILE": "/Users/normy/.ssh/id_ed25519"
      }
    }
  }
}
```

### Inline Password From Secret Injection

Prefer password files for normal local config. Use `SSH_MCP_PASSWORD` only when your MCP launcher or secret manager injects the value at runtime; do not commit a real password in JSON.

```json
{
  "mcpServers": {
    "ssh_lan_box": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/normy/autobyteus_org/autobyteus_mcps/ssh-mcp",
        "run",
        "python",
        "-m",
        "ssh_mcp.server"
      ],
      "env": {
        "SSH_MCP_DEFAULT_HOST": "lan-box.local",
        "SSH_MCP_DEFAULT_USER": "normy",
        "SSH_MCP_PASSWORD": "secret-manager-injected-value"
      }
    }
  }
}
```

## Docker E2E Test

This project includes real end-to-end SSH tests that start a disposable Dockerized OpenSSH daemon and validate lifecycle calls (`ssh_open_session` -> `ssh_session_exec` -> `ssh_close_session`) over loopback for:

- key-based auth
- username/password auth
- password-file auth

```bash
python -m pip install -e '.[test]'
pytest
SSH_MCP_RUN_DOCKER_E2E=1 pytest tests/test_e2e_docker.py
```

## Security Best Practice

- Prefer `SSH_MCP_PRIVATE_KEY_FILE` with a normal SSH key/agent setup when possible.
- Use `SSH_MCP_PASSWORD_FILE` rather than inline passwords unless a secret manager injects env securely.
- Do not pass passwords in tool input or shell command-line arguments.
- Keep host/user/auth in MCP server environment config rather than per-call tool input for normal one-host setups.
- Keep host-key verification enabled. First-time hosts may need a normal `ssh` connection first so OpenSSH can record `known_hosts`.
