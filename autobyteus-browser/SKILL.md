---
name: autobyteus-browser
description: Operate a local Chrome/Chromium session through the bundled AutoByteus browser CLI for explicit-tab navigation, authenticated-page inspection, DOM observation, JavaScript interaction, screenshots, and multi-step browser workflows. Use when an agent must act in or inspect a live browser, especially existing signed-in tabs. Do not use for generic web research or ordinary URL lookup when a non-browser web tool is sufficient.
---

# AutoByteus Browser

Use only the bundled launcher. Derive `SKILL_DIR` from the absolute source path supplied by the agent platform for this loaded `SKILL.md`; it is the directory containing this file. Never guess a checkout, use a vendor-specific skill home, register a PATH command, activate an environment, or invoke Python/uv directly.

```bash
SKILL_DIR="<absolute directory containing this loaded SKILL.md>"
BROWSER_CLI="$SKILL_DIR/scripts/autobyteus-browser"
bash "$BROWSER_CLI" health-check
```

The placeholder above is an instruction to substitute the actual loader-supplied directory, not a literal path.

## Workflow

1. Run `health-check`. If it fails, interpret the JSON error before retrying.
2. Run `list-tabs`; use `attach-tab` with a precise URL/title matcher for an existing user tab, or use `open-tab` for a task-owned tab.
3. Retain the returned opaque `result.tab_id`. Supply it explicitly to every tab-scoped command. Never shorten it or infer an active tab.
4. Observe with `read-page` or `dom-snapshot` before acting.
5. Act with `navigate` or, only when needed, `run-script`.
6. Verify the result with a fresh read or DOM snapshot. Serialize commands against the same tab; independent clients can race.
7. Close only tabs opened for the task. Do not automatically close tabs discovered with `attach-tab` or other user-owned tabs.

Use `bash "$BROWSER_CLI" --help` and `bash "$BROWSER_CLI" <command> --help` for exact flags. Core commands are `list-tabs`, `attach-tab`, `open-tab`, `close-tab`, `navigate`, `read-page`, `screenshot`, `dom-snapshot`, and `run-script`.

## Output and recovery

Except for help, parse stdout as exactly one JSON value:

- Success: `{"schema_version":"1","ok":true,"command":"...","result":{...}}`
- Failure: `{"schema_version":"1","ok":false,"command":"...","error":{"code":"...","message":"...","retryable":...}}`

Treat stderr as diagnostics, not machine output. Recover by code:

- `BOOTSTRAP_FAILED`, `CONFIGURATION_ERROR`, `BROWSER_UNAVAILABLE`: check the diagnostic and retry only when the environment/browser condition can change.
- `TAB_NOT_FOUND`: list tabs again; the target was closed or replaced.
- `NO_TAB_MATCH`: refine or correct discovery criteria.
- `AMBIGUOUS_TAB_MATCH`: add a more specific URL/title matcher.
- `INVALID_ARGUMENT`, `INVALID_URL`, `ARTIFACT_PATH_REJECTED`, `ARTIFACT_EXISTS`: correct the request; use a workspace-relative path and explicit `--overwrite` only when replacement is intended.
- `NAVIGATION_TIMEOUT`, `BROWSER_OPERATION_FAILED`: observe current tab state before deciding whether retry is safe.
- `SCRIPT_FAILED`: simplify/fix the script or return a JSON-serializable value.

## Safety

- Obtain normal confirmation before any consequential external side effect, including purchases, submissions, messages, account/security changes, or destructive actions.
- Treat `run-script` as advanced. Prefer a workspace-relative `--script-file` or `--script-stdin` for nontrivial code, and verify after execution.
- Keep screenshots and optional large results under the caller workspace. Absolute paths and escapes are rejected; existing files are preserved unless overwrite is explicit.
- Never attempt to terminate Chrome globally. The CLI deliberately exposes only single-tab close.
