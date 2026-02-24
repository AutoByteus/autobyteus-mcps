# Implementation Progress

## Kickoff Preconditions Checklist

- Scope classification confirmed (`Small`/`Medium`/`Large`): Yes (`Medium`)
- Investigation notes are current: Yes
- Requirements status is `Design-ready` or `Refined`: Yes (`Design-ready`)
- Runtime review final gate is `Implementation can start: Yes`: Yes
- Runtime review reached `Go Confirmed` with two consecutive clean deep-review rounds: Yes
- No unresolved blocking findings: Yes

## Progress Log

- 2026-02-24: Implementation kickoff baseline created.
- 2026-02-24: Applied C-001/C-002/C-003/C-004/C-005/C-006/C-007.
- 2026-02-24: Targeted pytest initially failed due missing `numpy` in test env after `uv sync --extra test`; classified as `Local Fix` and resolved by installing `numpy` in `.venv`.
- 2026-02-24: Verification complete (`72 passed, 5 skipped`).

## File-Level Progress Table

| Change ID | Change Type | File | Depends On | File Status | Unit Test File | Unit Test Status | Integration Test File | Integration Test Status | E2E Scenario | E2E Status | Last Failure Classification | Last Failure Investigation Required | Cross-Reference Smell | Design Follow-Up | Requirement Follow-Up | Last Verified | Verification Command | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C-001 | Modify | `src/tts_mcp/platform.py` | N/A | Completed | `tests/test_platform.py` | Passed | N/A | N/A | N/A | N/A | N/A | N/A | None | Not Needed | Not Needed | 2026-02-24 | `uv run python -m pytest -q tests/test_platform.py` | Intel mac auto+explicit Kokoro routing added |
| C-002 | Modify | `src/tts_mcp/runtime_bootstrap.py` | `C-001` | Completed | `tests/test_runtime_bootstrap.py` | Passed | N/A | N/A | N/A | N/A | N/A | N/A | None | Not Needed | Not Needed | 2026-02-24 | `uv run python -m pytest -q tests/test_runtime_bootstrap.py` | bootstrap installs Kokoro on Intel mac |
| C-003 | Add | `scripts/install_kokoro_onnx_macos.sh` | N/A | Completed | N/A | N/A | manual script smoke | Passed | N/A | N/A | N/A | N/A | None | Not Needed | Not Needed | 2026-02-24 | `scripts/install_tts_runtime.sh --linux-runtime kokoro_onnx --lang en` | added `.venv` python preference to avoid PEP 668 failure |
| C-004 | Modify | `scripts/install_tts_runtime.sh` | `C-003` | Completed | N/A | N/A | manual dispatch check | Passed | N/A | N/A | N/A | N/A | None | Not Needed | Not Needed | 2026-02-24 | `scripts/install_tts_runtime.sh --linux-runtime llama_cpp` | Intel mac dispatch + unsupported runtime guard |
| C-005 | Modify | `src/tts_mcp/runner.py` | N/A | Completed | `tests/test_runner.py` | Passed | N/A | N/A | N/A | N/A | N/A | N/A | None | Not Needed | Not Needed | 2026-02-24 | `uv run python -m pytest -q tests/test_runner.py` | auto playback candidate list includes `afplay` |
| C-006 | Modify | `tests/test_platform.py`, `tests/test_runtime_bootstrap.py` | C-001/C-002 | Completed | same | Passed | N/A | N/A | N/A | N/A | `Local Fix` (env dependency) | No | None | Not Needed | Not Needed | 2026-02-24 | `uv run python -m pytest` | full suite green after local env fix |
| C-007 | Modify | `tts-mcp/README.md` | C-001..C-005 | Completed | N/A | N/A | doc review | Passed | N/A | N/A | N/A | N/A | None | Not Needed | Not Needed | 2026-02-24 | manual read-through | docs updated for Intel mac support |

## E2E Feasibility Record

- E2E Feasible In Current Environment: `No`
- If `No`, concrete infeasibility reason: no full MCP-hosted client/server E2E harness configured for this ticket.
- Current environment constraints: CLI-only local environment.
- Best-available non-E2E verification evidence:
  - `uv run python -m pytest` (all unit suites)
  - direct Intel mac Kokoro generation smoke
  - installer dispatch and runtime install smoke
- Residual risk accepted: Yes, limited to host-integration edge cases.

## Docs Sync Log (Mandatory Post-Implementation)

| Date | Docs Impact (`Updated`/`No impact`) | Files Updated | Rationale | Status |
| --- | --- | --- | --- | --- |
| 2026-02-24 | Updated | `tts-mcp/README.md` | Added Intel macOS Kokoro support matrix, install flow, and config example | Completed |

## Completion Gate

- Implementation plan scope delivered: Yes
- Required unit tests passing: Yes
- Feasible E2E executed or infeasibility documented: Infeasibility documented with compensating evidence
- Docs sync result recorded: Yes (`Updated`)
