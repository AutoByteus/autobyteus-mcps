# Handoff Summary — SSH MCP Seamless Multi-Auth Sessions

## Status

- Ticket: `ssh-mcp-host-key-auth`
- Worktree: `/Users/normy/autobyteus-org/autobyteus-mcps-worktrees/ssh-mcp-host-key-auth`
- Branch: `codex/ssh-mcp-host-key-auth`
- Base: `origin/main@7d0ff82191d045402f8ec84405a56fccba1c969a`
- Finalization target: `origin/main`
- Current state: **Ready for user verification; local checkpoint `e47ff6f` exists, but the ticket is not archived, pushed, merged, or deployed.**

## What Changed

- Added `StrictHostKeyChecking=accept-new` to all SSH lifecycle commands.
- LAN password sessions now automatically trust a new host key without an askpass prompt loop; changed keys are still rejected.
- Limited password prompts to one.
- Preserved droplet private-key auth and independent fixed-host MCP configuration.
- Preserved timeout stderr/stdout diagnostics.
- Added regression tests, first-use Docker E2E coverage, and updated SSH docs.

## Verification Evidence

- Targeted suite: `35 passed`.
- Full local suite: `35 passed, 7 skipped` (Docker-gated tests skipped because Docker daemon unavailable).
- Compileall: passed.
- Real patched-source MCP protocol smoke: LAN opened, ran `whoami` as `ryan-ai`, and closed; droplet opened, ran `whoami` as `autobyteus`, and closed.
- Changed-key probe: rejected in under one second; no session registered.
- Proportional durable-test review: Pass, no findings.

## Security Note

The default is OpenSSH trust-on-first-use: new keys are accepted and stored; changed keys are rejected. Operators needing verified first-use fingerprints can pre-seed a managed `known_hosts` file.

## Remaining Limitation

The currently running MCP connector must be restarted/reloaded from the finalized branch for the new behavior to become active in the live tool instance. Docker E2E should be run on a host with a running Docker daemon.

## User Verification Request

Please verify the intended policy: automatic first-use host-key acceptance (`accept-new`) for seamless LAN and droplet sessions, with changed host keys rejected. After explicit confirmation, delivery can commit/push/merge the ticket.
