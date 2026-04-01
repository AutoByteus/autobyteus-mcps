# Code Review

## Review Meta

- Ticket: `tts-mcp-macos-qwen3-zh-auto-routing`
- Review Round: `7`
- Trigger Stage: `Local-fix Stage 7 pass for the English real MCP test setup repair`
- Prior Review Round Reviewed: `6`
- Latest Authoritative Round: `7`
- Workflow state source: `tickets/done/tts-mcp-macos-qwen3-zh-auto-routing/workflow-state.md`
- Inputs reviewed:
  - changed source files in current worktree
  - changed tests in current worktree
  - `implementation-progress.md`
  - `api-e2e-testing.md`
  - Stage 8 review principles/guidance

## Scope

- Changed file reviewed for this local fix:
  - `tts-mcp/tests/test_real_mcp_speak_tool.py`
- Directly related validation file rechecked:
  - `tts-mcp/tests/test_real_mcp_speak_tool_chinese_qwen.py`
- Carry-forward runtime boundary spot-check:
  - no product-code changes in this local fix

## Prior Findings Resolution Check

| Finding ID | Previous Severity | Current Resolution | Evidence |
| --- | --- | --- | --- |
| `CR-005` | `Blocker` | `Resolved` | `runtime_installation.py` now owns both startup preparation and request-time managed-profile readiness, and `tests/test_runtime_installation.py` covers the clean-install later-Chinese-request case. |
| `CR-006` | `Major` | `Resolved` | `config.py` now records explicit Kokoro pin metadata directly, and `routing_policy.py` uses that metadata instead of guessing from path equality. |
| `Local English MCP test setup mismatch` | `N/A` | `Resolved` | `tests/test_real_mcp_speak_tool.py` now resolves and injects `MLX_TTS_COMMAND`, matching the working Chinese public MCP test setup. |

## Source File Size And Structure Audit

- No source implementation files changed in this local fix.
- The Stage 8 hard source-file size gate remains satisfied by the latest authoritative source review from Round `6`.
- The changed test file remains small, direct, and maintainable.

## Findings

- None.

## Structural Integrity Checks

| Check | Result | Evidence |
| --- | --- | --- |
| Data-flow spine clarity | `Pass` | No product-code spine changes were made in this local fix; Round `6` remains authoritative for the runtime architecture. |
| Ownership boundary clarity | `Pass` | The only change is test setup alignment in `tests/test_real_mcp_speak_tool.py`. |
| Repeated coordination ownership | `Pass` | The English and Chinese public MCP tests now use the same MLX command-resolution setup pattern. |
| Interface/API/query/command boundary clarity | `Pass` | The fix only supplies the existing runtime command through test settings; no API boundary changed. |
| Cleanup completeness | `Pass` | No dead or replaced test setup remains in the touched local-fix scope. |
| Test quality / validation sufficiency | `Pass` | The repaired English public MCP test and the Chinese public MCP test passed together on this host. |

## Open Questions / Assumptions

- Residual environment constraint: a real Linux or Intel-mac Kokoro executable run was not rerun from this Darwin arm64 host. The focused runtime-installation and routing tests cover the contract change, and the residual host-specific gap is recorded in `api-e2e-testing.md`.

## Round History

| Round | Trigger | New Findings Found | Gate Decision | Latest Authoritative | Notes |
| --- | --- | --- | --- | --- | --- |
| `1` | `Stage 7 pass` | `No` | `Pass` | `No` | Initial feature-scope review only. |
| `2` | `Requirement-gap re-entry` | `No` | `Pass` | `No` | Single-field public API cleanup review. |
| `3` | `User-requested full-project architecture revisit` | `Yes` | `Fail` | `No` | Found the startup/routing/path ownership drift. |
| `4` | `Design-impact re-entry implementation + Stage 7 pass` | `No` | `Pass` | `No` | Resolved the startup/routing/path ownership findings. |
| `5` | `User-requested independent Stage 8 rerun` | `Yes` | `Fail` | `No` | Found the remaining Kokoro clean-install and explicit-pin issues. |
| `6` | `Design-impact Kokoro contract re-entry + Stage 7 pass` | `No` | `Pass` | `Yes` | Resolved `CR-005` and `CR-006`; no new blocking findings. |
| `7` | `Local English real MCP test fix + Stage 7 pass` | `No` | `Pass` | `Yes` | Bounded test-setup repair only; no product-code findings. |

## Gate Decision

- Latest authoritative review round: `7`
- Decision: `Pass`
- Implementation can proceed to `Stage 9`: `Yes`
- Notes:
  - The Kokoro clean-install and explicit-pin contract issues from Round 5 remain resolved.
  - The local fix only repaired the English real MCP test setup.
  - No new product-code or architectural findings were introduced.
