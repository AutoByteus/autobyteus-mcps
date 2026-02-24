# Implementation Plan

## Scope Classification

- Classification: `Medium`
- Reasoning: platform routing + bootstrap + installer scripts + playback behavior + tests + docs.
- Workflow Depth: `Medium` -> proposed design -> call stack -> review (`Go Confirmed`) -> implementation plan -> progress tracking.

## Upstream Artifacts (Required)

- Investigation notes: `tickets/in-progress/tts-mcp-macos-intel-kokoro-onnx-support/investigation-notes.md`
- Requirements: `tickets/in-progress/tts-mcp-macos-intel-kokoro-onnx-support/requirements.md`
  - Current Status: `Design-ready`
- Runtime call stacks: `tickets/in-progress/tts-mcp-macos-intel-kokoro-onnx-support/future-state-runtime-call-stack.md`
- Runtime review: `tickets/in-progress/tts-mcp-macos-intel-kokoro-onnx-support/future-state-runtime-call-stack-review.md`
- Proposed design: `tickets/in-progress/tts-mcp-macos-intel-kokoro-onnx-support/proposed-design.md`

## Plan Maturity

- Current Status: `Ready For Implementation`
- Notes: review gate is `Go Confirmed`.

## Preconditions (Must Be True Before Finalizing This Plan)

- `requirements.md` is at least `Design-ready`: Yes
- Runtime call stack review artifact exists and is current: Yes
- All in-scope use cases reviewed: Yes
- No unresolved blocking findings: Yes
- Runtime review has `Go Confirmed` with two consecutive clean deep-review rounds: Yes

## Runtime Call Stack Review Gate Summary (Required)

| Round | Review Result | Findings Requiring Write-Back | Write-Back Completed | Round State (`Reset`/`Candidate Go`/`Go Confirmed`) | Clean Streak After Round |
| --- | --- | --- | --- | --- | --- |
| 1 | Pass | No | N/A | Candidate Go | 1 |
| 2 | Pass | No | N/A | Go Confirmed | 2 |

## Go / No-Go Decision

- Decision: `Go`
- Evidence:
  - Final review round: 2
  - Clean streak at final round: 2
  - Final review gate line (`Implementation can start`): Yes

## Principles

- Bottom-up implementation order by dependency.
- Test updates with each behavior change.
- No legacy compatibility branches.

## Dependency And Sequencing Map

| Order | File/Module | Depends On | Why This Order |
| --- | --- | --- | --- |
| 1 | `src/tts_mcp/platform.py` | none | core backend policy gate used by runtime |
| 2 | `src/tts_mcp/runtime_bootstrap.py` | `platform.py` behavior | bootstrap uses host/runtime policy |
| 3 | `scripts/install_kokoro_onnx_macos.sh` | none | installer target for bootstrap/dispatch |
| 4 | `scripts/install_tts_runtime.sh` | new installer script | dispatch path wiring |
| 5 | `src/tts_mcp/runner.py` | none | playback fallback support |
| 6 | tests + `README.md` | all above | verify and document final behavior |

## Requirement And Design Traceability

| Requirement | Design Section | Use Case / Call Stack | Planned Task ID(s) | Verification |
| --- | --- | --- | --- | --- |
| R-001 | Target State + C-001 | UC-001 | T-001 | `tests/test_platform.py` |
| R-002 | Target State + C-001 | UC-002 | T-001 | `tests/test_platform.py` |
| R-003 | Target State + C-002 | UC-003 | T-002 | `tests/test_runtime_bootstrap.py` |
| R-004 | Target State + C-003/C-004 | UC-004 | T-003, T-004 | script smoke/manual validation |
| R-005 | Target State + C-005 | UC-005 | T-005 | unit/manual playback path |

## Design Delta Traceability (Required For `Medium/Large`)

| Change ID (from proposed design doc) | Change Type | Planned Task ID(s) | Includes Remove/Rename Work | Verification |
| --- | --- | --- | --- | --- |
| C-001 | Modify | T-001 | No | platform unit tests |
| C-002 | Modify | T-002 | No | bootstrap unit tests |
| C-003 | Add | T-003 | No | installer smoke |
| C-004 | Modify | T-004 | No | installer dispatch check |
| C-005 | Modify | T-005 | No | runner behavior + manual check |
| C-006 | Modify | T-006 | No | pytest |
| C-007 | Modify | T-007 | No | README review |

## Step-By-Step Plan

1. Implement platform + bootstrap support for Intel macOS Kokoro.
2. Add Intel macOS Kokoro installer and dispatch wiring.
3. Add playback fallback update (`afplay` in auto list).
4. Update tests and run targeted/full pytest.
5. Update README and progress/docs sync logs.

## Per-File Definition Of Done

| File | Implementation Done Criteria | Unit Test Criteria | Integration Test Criteria | E2E Criteria | Notes |
| --- | --- | --- | --- | --- | --- |
| `src/tts_mcp/platform.py` | Intel mac Kokoro route works | `test_platform.py` passes | N/A | N/A | preserve existing routes |
| `src/tts_mcp/runtime_bootstrap.py` | bootstrap installs Kokoro on Intel mac | `test_runtime_bootstrap.py` passes | N/A | N/A | correct script selected |
| `scripts/install_kokoro_onnx_macos.sh` | script installs runtime/assets | N/A | manual run path check | N/A | profile/lang behavior |
| `scripts/install_tts_runtime.sh` | dispatch supports Intel mac | N/A | manual dispatch checks | N/A | explicit unsupported messages |
| `src/tts_mcp/runner.py` | auto playback includes afplay fallback | existing runner tests pass | N/A | N/A | no API changes |
| `README.md` | docs reflect supported host matrix | N/A | N/A | N/A | include Intel mac instructions |

## Test Strategy

- Unit tests: `tests/test_platform.py`, `tests/test_runtime_bootstrap.py`, relevant `tests/test_runner.py`.
- Integration tests: N/A for this scope (no cross-process contract changes).
- E2E feasibility: `Not Feasible`
- If E2E is not feasible, concrete reason and current constraints: full MCP host/client E2E not provisioned in this environment for this ticket; scope validated by unit + local smoke.
- Best-available non-E2E verification evidence when E2E is not feasible: direct local Kokoro generation on Intel mac + targeted pytest.
- Residual risk notes: upstream runtime package changes can affect future install behavior.
