# Investigation Notes - Simplify SSH MCP Configuration

## Status

Stage 1 current on 2026-08-18.

## Investigation Goals / Questions

1. Identify the current SSH MCP configuration surface and which variables are primary vs advanced.
2. Determine how password/password-file auth is currently implemented.
3. Determine whether private-key auth is first-class or only possible through low-level OpenSSH arguments.
4. Decide whether `SSH_MCP_ALLOWED_HOSTS` and `SSH_MCP_BASE_ARGS` are necessary user-facing configuration or should be replaced/removed.
5. Identify affected code, docs, and tests for a clean no-legacy simplification.

## Sources Consulted

### Local files

- `ssh-mcp/src/ssh_mcp/config.py`
  - Defines `SshSettings`, env parsing, target resolution, password/password-file parsing.
- `ssh-mcp/src/ssh_mcp/runner.py`
  - Builds OpenSSH commands, manages control socket sessions, implements askpass password flow.
- `ssh-mcp/src/ssh_mcp/server.py`
  - Exposes MCP tools: `ssh_health_check`, `ssh_open_session`, `ssh_session_exec`, `ssh_close_session`.
- `ssh-mcp/tests/test_config.py`
  - Covers env parsing, allowlist/default target behavior, password/password-file behavior.
- `ssh-mcp/tests/test_runner.py`
  - Covers command construction, session lifecycle, password askpass command/env behavior.
- `ssh-mcp/tests/test_server.py`
  - Covers MCP tool delegation and structured results.
- `ssh-mcp/tests/test_e2e_docker.py`
  - Docker-backed real SSH scenarios; current key-based E2E injects `-i`, `BatchMode`, and host-key options via `base_args`.
- `ssh-mcp/README.md`
  - Presents many env vars together, including `SSH_MCP_BASE_ARGS` and `SSH_MCP_ALLOWED_HOSTS`, before minimal setup examples.
- `ssh-mcp/docs/runtime-flow.md`
  - Documents current runtime flow and bounded controls.

### Commands run

- `rg -n 'SSH_MCP_|base_args|password|private|allowed_hosts|default_host|default_user|default_port|timeout|max_sessions' ssh-mcp/src/ssh_mcp ssh-mcp/tests ssh-mcp/README.md ssh-mcp/docs/runtime-flow.md`
  - Confirmed all current env variables and code/test references.
- `uv --directory ssh-mcp run --frozen pytest tests/test_config.py tests/test_runner.py tests/test_server.py`
  - Failed because test extras were not installed and `pytest` was unavailable in the default environment. This confirms tests should be run with `--extra test`.
- `uv --directory ssh-mcp run --frozen --extra test pytest tests/test_config.py tests/test_runner.py tests/test_server.py`
  - Passed: `27 passed in 1.40s`.

## Current Behavior Findings

### Current user-facing env surface is broad

`load_settings` currently reads:

- `SSH_MCP_COMMAND`
- `SSH_MCP_BASE_ARGS`
- `SSH_MCP_TIMEOUT_SECONDS`
- `SSH_MCP_ALLOWED_HOSTS`
- `SSH_MCP_DEFAULT_HOST`
- `SSH_MCP_DEFAULT_USER`
- `SSH_MCP_DEFAULT_PORT`
- `SSH_MCP_MAX_COMMAND_CHARS`
- `SSH_MCP_MAX_OUTPUT_CHARS`
- `SSH_MCP_HEALTH_CHECK_ARGS`
- `SSH_MCP_PASSWORD`
- `SSH_MCP_PASSWORD_FILE`
- `SSH_MCP_SESSION_IDLE_TIMEOUT_SECONDS`
- `SSH_MCP_MAX_SESSIONS`
- `SSH_MCP_SESSION_DIR`
- `SSH_MCP_NAME`
- `SSH_MCP_INSTRUCTIONS`

This makes the README and config examples look like a low-level OpenSSH wrapper instead of a normal SSH connection UI.

### Password auth is already first-class

`SSH_MCP_PASSWORD` and `SSH_MCP_PASSWORD_FILE` are parsed in `config.py`. `runner.py` resolves the password and creates an `SSH_ASKPASS` helper script so OpenSSH can authenticate non-interactively. `load_settings` rejects configuring both password and password file.

### Private-key auth is not first-class

Key-based auth is currently configured by writing OpenSSH flags into `SSH_MCP_BASE_ARGS`, for example:

```text
-i /path/to/private_key -o BatchMode=yes -o IdentitiesOnly=yes
```

This is the main UX issue: users must know OpenSSH flags instead of setting an intuitive `SSH_MCP_PRIVATE_KEY_FILE`.

### `SSH_MCP_ALLOWED_HOSTS` creates duplicated mental model

`SSH_MCP_ALLOWED_HOSTS` is a safety allowlist separate from `SSH_MCP_DEFAULT_HOST`. It can be useful for reducing target drift, but it makes the simple one-host case look strange because the same host is often repeated twice. A simpler MCP model can make `SSH_MCP_DEFAULT_HOST` itself pin the server to that host: calls may omit `host`, or pass the same host, but cannot override it to another host. Users who need several hosts can create several MCP server configs.

### Advanced limits still have real internal value

Timeouts, max command chars, max output chars, idle timeout, session dir, and max sessions protect the MCP runtime from hangs, runaway output, stale control sockets, and resource leaks. They should retain sane defaults and can remain advanced options, but they should not be required or featured as the normal setup path.

### Entrypoints / boundaries / owners

- `ssh_mcp.server` owns MCP tool schema and progress reporting.
- `ssh_mcp.config` owns env/config parsing, validation, auth-source selection, and target resolution.
- `ssh_mcp.runner` owns OpenSSH command construction, session lifecycle, subprocess execution, and askpass setup.
- Docs live in `ssh-mcp/README.md` and `ssh-mcp/docs/runtime-flow.md`.
- Tests cover config, runner, server, and Docker E2E.

The current folder placement is coherent; no file moves are required.

## Scope Triage

Classification: `Medium`.

Rationale:

- Code changes are concentrated in `config.py` and `runner.py`, but the user-facing environment contract changes.
- Tests and docs must be updated across config, runner, server/E2E docs.
- The design affects an external MCP configuration surface, including removal/replacement of legacy public env knobs.
- A proposed design artifact is useful to capture the exact simplified contract before implementation.

## Design Implications

1. Add first-class `SSH_MCP_PRIVATE_KEY_FILE`.
2. Remove user-facing `SSH_MCP_BASE_ARGS` support from env parsing and docs; key auth should not require raw OpenSSH flags.
3. Remove user-facing `SSH_MCP_ALLOWED_HOSTS` support from env parsing and docs; use default-host pinning for the normal single-host MCP pattern.
4. Keep advanced safety/time/resource values with sane defaults and keep them documented separately as advanced optional settings.
5. Reject old removed env keys when set, rather than silently ignoring them, so stale configs fail with actionable messages.
6. Keep no interactive prompts: password auth uses askpass; key/agent/no-auth modes should use `BatchMode=yes` internally.
7. Preserve session lifecycle tools and structured results.

## Open Unknowns / Risks

- Host-key verification remains normal OpenSSH behavior. First-time LAN connections may require the user to SSH once manually or manage `known_hosts`; this is preferable to adding more public env complexity.
- Private keys with passphrases are expected to use SSH agent or prior setup; no passphrase env is in scope.
- Removing `SSH_MCP_BASE_ARGS` removes a power-user escape hatch. This is intentional under the workflow's no-legacy simplification policy, but README should mention what replaced common usage.

## Re-entry Investigation - Stage 6 Source File Size Gate (2026-08-18)

### Trigger

During Stage 6 implementation, the workflow's proactive source-file size guardrail was measured after initial config/runner/test/doc edits.

### Evidence

Commands:

```bash
for f in ssh-mcp/src/ssh_mcp/config.py ssh-mcp/src/ssh_mcp/runner.py ssh-mcp/src/ssh_mcp/server.py; do rg -n "\\S" "$f" | wc -l; done
git show origin/main:ssh-mcp/src/ssh_mcp/runner.py | rg -n "\\S" | wc -l
git diff --numstat -- ssh-mcp/src/ssh_mcp/runner.py ssh-mcp/src/ssh_mcp/config.py
```

Observed results:

- `ssh-mcp/src/ssh_mcp/config.py`: 303 effective non-empty lines after change.
- `ssh-mcp/src/ssh_mcp/runner.py`: 717 effective non-empty lines after change.
- `ssh-mcp/src/ssh_mcp/server.py`: 175 effective non-empty lines after change.
- `origin/main` `runner.py`: 704 effective non-empty lines, so the file was already oversized, but this ticket touched it and therefore Stage 8 hard-limit policy applies.
- Current diff at discovery: `runner.py` 35 added / 18 removed; `config.py` 44 added / 31 removed.

### Classification

`Design Impact`.

Rationale: the reviewed design v1 kept `runner.py` as one large runtime owner, but the workflow requires changed source implementation files to stay at or below 500 effective non-empty lines. The implementation cannot complete cleanly unless runtime ownership is split into smaller, explicit source files.

### Design Implications

- Introduce `ssh_mcp.types` for the shared structured result contract.
- Introduce `ssh_mcp.session` for `SessionRecord` and `SessionManager`.
- Introduce `ssh_mcp.execution` for execution specs, subprocess execution, output normalization, and error result mapping.
- Keep `ssh_mcp.runner` as the authoritative runtime orchestration/command-building boundary used by `ssh_mcp.server`.
- Preserve server dependency on `runner.create_session_manager` instead of making `server` depend directly on session internals.
- Re-run Stage 3/4/5 with this split before resuming source edits.
