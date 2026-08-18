# Code Review Report — SSH MCP Seamless Multi-Auth Sessions

## Review Round Meta

- Review Entry Point: `Implementation Review`
- Requirements: `requirements.md`
- Investigation: `investigation-notes.md`
- Design: `design-spec.md`
- Solution revision: `SR-001`
- Implementation handoff: `implementation-handoff.md`
- Implementation revision: `IR-001`
- Current code review revision: `CRR-001`
- Current review round: `1`
- Trigger: Initial implementation handoff
- Latest authoritative round: `1`

## Review Scope

Reviewed the changed runner/execution source, lifecycle tests, first-use E2E fixture, and SSH documentation. Explicitly excluded unrelated MCPs and unrelated repository tickets.

## Upstream Behavior And Production-Path Basis Confirmation

- Approved requirements understood: Yes.
- Design behavior map verified: Confirmed.
- Material premises DP-001 and DP-002 verified: Confirmed by the LAN timeout probe, trusted-host smoke, and current separate MCP configuration.
- Behavior-basis status: `Confirmed`.

| Behavior ID | Status | Implementation Evidence |
| --- | --- | --- |
| BEH-001 | Confirmed | `server.py` still delegates health to `run_health_check`, which runs only the configured local probe. |
| BEH-002 | Confirmed | Shared runner policy adds `accept-new`; password askpass remains env-only and prompt count is bounded. |
| BEH-003 | Confirmed | Private-key path remains isolated behind `SSH_MCP_PRIVATE_KEY_FILE`; no password fallback was added. |
| BEH-004 | Confirmed | `execution.py` maps nonzero/timeout results and now decodes timeout bytes for diagnostics. |

## Structural / Design Checks

| Check | Result | Evidence |
| --- | --- | --- |
| Design health assessment preserved | Pass | Local runner defect addressed at existing owner. |
| Behavior-defining artifacts matched | Pass | Implementation matches REQ-001..006 and DS-001..003. |
| Spine clarity/preservation | Pass | MCP -> server -> runner -> OpenSSH -> result remains intact. |
| Ownership boundaries | Pass | `runner` remains the single command/lifecycle policy owner. |
| Off-spine concerns | Pass | Config, sessions, execution, and askpass remain attached to clear owners. |
| Existing capability reuse | Pass | Extended runner/execution; no unnecessary subsystem/helper. |
| Reusable structures | Pass | No repeated new model or parallel representation introduced. |
| Shared data tightness | Pass | No data-model change. |
| Repeated coordination ownership | Pass | Host-key/auth flags are centralized in `_build_auth_args`. |
| Empty indirection | Pass | No pass-through boundary added. |
| Separation/file responsibility | Pass | Source, tests, and docs changes match their owners. |
| Dependency direction | Pass | Existing dependency direction preserved. |
| Authoritative Boundary Rule | Pass | Server still delegates to runner and does not bypass internals. |
| File placement | Pass | Changes remain in existing SSH MCP files/test suite. |
| Flat-vs-over-split | Pass | No artificial new runtime module. |
| Interface clarity | Pass | Public MCP tool contracts unchanged. |
| Naming/readability | Pass | `accept-new` policy and diagnostics changes are explicit. |
| Duplication | Pass | Shared flags remain centralized. |
| Patch-on-patch complexity | Pass | Direct policy replacement; no compatibility wrapper. |
| Dead/obsolete cleanup | Pass | The implicit prompt-loop path is removed by policy; no stale flag remains. |
| Test alignment | Pass | Unit, timeout, and first-use lifecycle assertions map to ACs. |
| Fixture/helper coherence | Pass | Isolated-home helper is small and specific to first-use behavior. |
| Stale/compatibility tests | Pass | Existing auth tests remain valid; no legacy test retained. |
| API/E2E readiness | Pass | Durable first-use scenario is added; Docker execution is environment-gated. |

## Source File Size And Structure Audit

| Source File | Effective Lines | Hard Limit | Delta / SoC Result |
| --- | ---: | --- | --- |
| `ssh-mcp/src/ssh_mcp/runner.py` | 428 | Pass (`<500`) | Small local policy delta; ownership remains coherent. |
| `ssh-mcp/src/ssh_mcp/execution.py` | 190 | Pass (`<500`) | Small output-normalization delta; ownership remains coherent. |

## Legacy / Backward-Compatibility Verdict

All checks pass: no compatibility mechanism, old behavior branch, version-specific data path, or unnecessary migration was introduced. The implementation directly replaces the prompt-loop policy with explicit non-interactive TOFU handling.

## Docs-Impact Verdict

- Docs impact: `Yes`.
- README and runtime flow now document automatic new-key acceptance, changed-key rejection, and local-only health semantics.

## Material Premise Validation

- DP-001: `Confirmed`; exact current LAN env reproduced the timeout, and the same source succeeded with trusted host key / patched accept-new policy.
- DP-002: `Confirmed`; current MCP registry has independent LAN password and droplet key entries, and both patched-source smokes succeeded.
- No new material premise introduced.

## Review Scorecard

- Overall score: `9.6 / 10`
- Overall score: `96 / 100`

| Category | Score | Reason / Remaining Improvement |
| --- | ---: | --- |
| Data-flow spine | 9.7 | Existing end-to-end path remains explicit. |
| Ownership/boundaries | 9.7 | Shared policy stays in runner; no bypass. |
| API/interface clarity | 9.5 | Public contract unchanged and docs distinguish health/session. |
| Separation/file placement | 9.7 | Small changes fit existing owners. |
| Shared structures | 9.5 | No new shared data; existing shapes preserved. |
| Naming/readability | 9.5 | Policy comments explain TOFU tradeoff. |
| API/E2E readiness | 9.2 | Docker execution is still environment-blocked locally, though durable coverage is added. |
| Runtime correctness | 9.7 | LAN and droplet real smokes opened/executed/closed successfully. |
| No legacy retention | 9.8 | Direct clean-cut policy change. |
| Cleanup completeness | 9.4 | No orphaned sessions in smoke; Docker cleanup remains fixture-owned. |

## Findings

None. No implementation finding blocks API/E2E validation.

## Residual Risks

- `accept-new` is trust-on-first-use; preverified managed `known_hosts` remains the stronger option.
- Docker daemon is unavailable in the current environment, so Docker-gated E2E execution remains pending there.

## Latest Authoritative Result

- Review Decision: `Pass`
- Review Entry Point: `Implementation Review`
- Material-Premise Gate: `Pass`
- Recommended Recipient: API/E2E coverage investigation and execution.
