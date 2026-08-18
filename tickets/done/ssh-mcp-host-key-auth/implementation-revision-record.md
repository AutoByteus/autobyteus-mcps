# Implementation Revision Record — SSH MCP Seamless Multi-Auth Sessions

## Revision Index

| Revision ID | Trigger | Findings | Classification | Related | Result |
| --- | --- | --- | --- | --- | --- |
| IR-001 | Initial implementation from SR-001 | N/A | Initial Baseline | SR-001; CRR/API-REV N/A | Implementation complete; ready for review |

## IR-001 — Add non-interactive first-use host-key policy

- **Trigger:** Initial implementation-ready design (`SR-001`).
- **Prior result:** N/A.
- **Current result:** Implementation complete; local checks pass.
- **Related solution revision:** `SR-001`.
- **Approved behaviors:** BEH-001 through BEH-004; REQ-001 through REQ-006.
- **Implementation delta:**
  - Added `StrictHostKeyChecking=accept-new` to the runner's shared lifecycle command policy.
  - Limited password prompts to one attempt.
  - Preserved existing password askpass and private-key selection boundaries.
  - Preserved timeout output by decoding bytes from `TimeoutExpired`.
  - Added runner, execution, and first-use Docker E2E regression coverage.
  - Updated README/runtime documentation.
- **Changed files:** `ssh-mcp/src/ssh_mcp/runner.py`, `execution.py`, tests, README, runtime docs.
- **Local validation:** `35 passed`; full local suite `35 passed, 7 skipped`; compileall passed. Real LAN and droplet smoke tests through the patched source both opened, executed `whoami`, and closed successfully using isolated HOME/known-hosts directories.
- **Next recipient:** Code review, then API/E2E coverage review/execution.
- **Remaining limitations:** Docker daemon unavailable in this environment, so Docker E2E is currently skipped here; the new durable test is included and was structurally checked.
