# Aggregated Validation - x11-computer-use-mcp

## Status

- Stage: `6`
- Result: `Pass`
- Date: `2026-02-26`
- Scope: API + E2E validation across AC-001..AC-010

## Scenario Results

| Scenario ID | Acceptance Criteria | Level | Result | Evidence Command(s) | Notes |
| --- | --- | --- | --- | --- | --- |
| AV-001 | AC-001 | API | Passed | HTTP smoke (`python3 -m computer_use_mcp.server` with `X11_MCP_TRANSPORT=streamable-http`; streamable-http client call) | Server bound on `127.0.0.1:9876`; `/mcp` POST requests succeeded |
| AV-002 | AC-002 | API | Passed | `PYTHONPATH=src python3` runner health check in prefix mode | `health_ok=True`, `missing_tools=[]`, `display=:99` |
| AV-003 | AC-003 | API | Passed | docker-backed runner script (`run_get_screen_info`) | Returned numeric screen dimensions (`1848x987`) and root metadata |
| AV-004 | AC-004 | API | Passed | docker-backed runner script (`run_get_active_window`, `run_list_windows`) | Structured active/list window payloads returned; list count `5` |
| AV-005 | AC-005 | API | Passed (after local fix) | Initial: docker runner focus call with `windowactivate --sync` timeout. Re-run: docker-backed runner script after fix | Local fix changed focus activation to non-sync command; focus by id and name both succeeded |
| AV-006 | AC-006 | API | Passed (after local fix) | docker-backed runner script (`run_mouse_move`, `run_mouse_click`, `run_mouse_scroll`, `run_mouse_drag`) | Local fix removed `--sync` from move/drag paths; pointer operations succeeded; validation error path confirmed |
| AV-007 | AC-007 | API | Passed | docker-backed runner script (`run_key_press`, `run_type_text`) + oversized text validation call | Key combo/text succeeded; oversized text returned `error_type=validation` |
| AV-008 | AC-008 | API | Passed | docker-backed runner script (`run_capture_screenshot`) | PNG file created at `/tmp/computer-use-mcp-screenshots/stage6-full-proof.png`, metadata returned |
| AV-009 | AC-009 | API | Passed | docker-backed validation calls for invalid mouse button and oversized text | Structured non-crashing validation errors returned with stable `error_type` |
| AV-010 | AC-010 | E2E | Passed | `PYTHONPATH=src pytest -q` and docker-backed API loop script + HTTP smoke | `16 passed`; live docker control loop and HTTP transport validated |

## Re-Entry Record

- Trigger: Stage 6 AV-005 failed on first run (`focus_window` timeout with `xdotool windowactivate --sync`).
- Classification: `Local Fix`.
- Fixes applied:
  - `run_focus_window`: switched to non-sync `xdotool windowactivate`.
  - `run_mouse_move` and `run_mouse_drag`: removed `--sync` move steps to avoid container hangs.
  - Added unit tests for focus-id/name and non-sync mouse move/drag commands.
- Revalidation outcome: all AV scenarios passed.

## Gate Decision

- Aggregated validation gate: `Pass`
- Residual blockers: none
- Re-entry still active: no
