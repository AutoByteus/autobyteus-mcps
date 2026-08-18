# Solution Revision Record — SSH MCP Seamless Multi-Auth Sessions

## SR-001 — Initial implementation-ready baseline

- **Prior result:** N/A
- **Trigger:** User-requested workflow investigation of LAN password-session timeout while preserving droplet key sessions.
- **Current result:** Requirements refined and design ready.
- **Established:** The host-key/askpass prompt loop is a reachable local runner defect. `StrictHostKeyChecking=accept-new` is the approved shared policy; changed keys remain rejected. Timeout diagnostics will preserve output.
- **Artifacts:** `requirements.md`, `investigation-notes.md`, `design-spec.md`.
- **Implementation impact:** Modify runner/execution, focused tests, and SSH MCP docs; no persisted data migration.
- **Remaining gaps:** Docker daemon is unavailable in the current environment; a real LAN smoke is available through temporary known-hosts isolation.
