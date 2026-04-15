# Code Review

## Review Meta

- Ticket: `tts-mcp-voice-parameter`
- Review Round: `5`
- Trigger Stage: `Re-entry`
- Prior Review Round Reviewed: `4`
- Latest Authoritative Round: `5`
- Workflow state source: `tickets/in-progress/tts-mcp-voice-parameter/workflow-state.md`
- Investigation notes reviewed as context:
  - `tickets/in-progress/tts-mcp-voice-parameter/investigation-notes.md`
- Earlier design artifact(s) reviewed as context:
  - `tickets/in-progress/tts-mcp-voice-parameter/requirements.md`
  - `tickets/in-progress/tts-mcp-voice-parameter/implementation.md`
- Runtime call stack artifact:
  - `tickets/in-progress/tts-mcp-voice-parameter/future-state-runtime-call-stack.md`
  - `tickets/in-progress/tts-mcp-voice-parameter/future-state-runtime-call-stack-review.md`
- Shared Design Principles: `shared/design-principles.md`
- Code Review Principles: `stages/08-code-review/code-review-principles.md`

## Scope

- Files reviewed (source + tests):
  - `tts-mcp/src/tts_mcp/config.py`
  - `tts-mcp/src/tts_mcp/backend_commands.py`
  - `tts-mcp/src/tts_mcp/runner.py`
  - `tts-mcp/src/tts_mcp/server.py`
  - `tts-mcp/tests/test_config.py`
  - `tts-mcp/tests/test_server.py`
  - `tts-mcp/tests/test_speak_voice.py`
  - `tts-mcp/tests/test_speak_temperature.py`
  - `tts-mcp/tests/test_mlx_language_chinese.py`
  - `tts-mcp/tests/test_mlx_language_english.py`
  - `tts-mcp/tests/test_runner.py`
  - `tts-mcp/tests/test_real_mcp_speak_tool_chinese_qwen.py`
  - directly impacted related file: `tts-mcp/tests/test_real_mcp_speak_tool_english.py`
- Why these files:
  - The current re-entry adds a new public `temperature` boundary, a deterministic MLX default, truthful Chinese CustomVoice examples, and stronger real-validation coverage. Stage 8 must therefore review the public contract, config ownership, runner/command propagation, and the new focused + real validation slice together.

## Prior Findings Resolution Check (Mandatory On Round >1)

| Prior Round | Finding ID | Previous Severity | Current Resolution (`Resolved`/`Partially Resolved`/`Still Failing`/`Not Applicable After Rework`) | Evidence | Notes |
| --- | --- | --- | --- | --- | --- |
| `1` | `CR-001` | `Major` | `Resolved` | `test_runner.py` still reuses `mlx_language_test_support.py`; duplicate fake-runtime helper bodies remain removed. | Round-1 support-ownership finding stays resolved. |
| `1` | `CR-002` | `Major` | `Resolved` | `test_real_linux_kokoro_chinese.py` still reuses `mcp_session_test_support.py`; duplicate session helper remains removed. | Round-1 support-ownership finding stays resolved. |
| `4` | `N/A` | `N/A` | `Not Applicable After Rework` | Round 4 passed with no open Stage 8 findings; round 5 was triggered by the user-directed temperature-control requirement gap. | No unresolved round-4 finding carried into round 5. |

## Source File Size And Structure Audit (Mandatory)

| Source File | Effective Non-Empty Line Count | Adds/Expands Functionality (`Yes`/`No`) | `>500` Hard-Limit Check | `>220` Changed-Line Delta Gate | Scope-Appropriate SoC Check (`Pass`/`Fail`) | File Placement Check (`Pass`/`Fail`) | Preliminary Classification (`N/A`/`Local Fix`/`Validation Gap`/`Design Impact`/`Requirement Gap`/`Unclear`) | Required Action (`Keep`/`Split`/`Move`/`Refactor`) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `tts-mcp/src/tts_mcp/config.py` | `465` | `Yes` | `Pass` | `Pass` (`31` added, `2` removed) | `Pass` | `Pass` | `N/A` | `Keep` |
| `tts-mcp/src/tts_mcp/backend_commands.py` | `158` | `Yes` | `Pass` | `Pass` (`4` added, `1` removed) | `Pass` | `Pass` | `N/A` | `Keep` |
| `tts-mcp/src/tts_mcp/runner.py` | `473` | `Yes` | `Pass` | `Pass` (`55` added, `3` removed) | `Pass` | `Pass` | `N/A` | `Keep` |
| `tts-mcp/src/tts_mcp/server.py` | `121` | `Yes` | `Pass` | `Pass` (`66` added, `3` removed) | `Pass` | `Pass` | `N/A` | `Keep` |

## Structural Integrity Checks (Mandatory)

| Check | Result (`Pass`/`Fail`) | Evidence | Required Action |
| --- | --- | --- | --- |
| Data-flow spine inventory clarity and preservation under shared principles | Pass | The path is clear and still single-subject: MCP caller -> public `speak` schema (`language`, `voice`, `temperature`) -> canonicalization / argument shaping -> `run_speak` -> MLX routing + effective-temperature selection -> command emission. | None |
| Ownership boundary preservation and clarity | Pass | `server.py` owns only public contract wording and delegation, `config.py` owns the default temperature, `runner.py` owns backend-specific validation/override selection, and `backend_commands.py` owns CLI construction. | None |
| Off-spine concern clarity (off-spine concerns serve clear owners and stay off the main line) | Pass | Schema descriptions, config defaults, and runtime validation remain in their existing owners; the real deterministic-hash check lives in the real Chinese MCP test instead of leaking into runtime code. | None |
| Existing capability/subsystem reuse check (no fresh helper where an existing subsystem should own it) | Pass | The delta extends existing config/server/runner layers and existing route-specific real tests instead of inventing a parallel temperature subsystem or ad hoc probe harness. | None |
| Reusable owned structures check (repeated structures extracted into the right owned file instead of copied across files) | Pass | Public temperature schema coverage is isolated in `test_speak_temperature.py`, while shared MCP-session and MLX-runtime fixtures continue to live in their existing support owners. | None |
| Shared-structure/data-model tightness check (no kitchen-sink base, no overlapping parallel shapes, specialization/composition used meaningfully) | Pass | One additional scalar setting (`mlx_default_temperature`) is added to `TtsSettings` without widening it into a multi-backend pseudo-capability matrix. | None |
| Repeated coordination ownership check (shared policy has a clear owner instead of being repeated across callers) | Pass | Deterministic MLX temperature policy is now owned once in config/runner rather than being recreated by callers or external scripts. | None |
| Empty indirection check (no pass-through-only boundary) | Pass | `server.py` still adds schema/help text and public argument shaping; `runner.py` still performs meaningful validation and backend-specific branching. | None |
| Scope-appropriate separation of concerns and file responsibility clarity | Pass | The delta is narrow and lands in the right layers: one config field, one server boundary addition, one runner propagation path, and one backend command emission change. | None |
| Ownership-driven dependency check (no forbidden shortcuts or unjustified cycles) | Pass | No new mixed-level dependency was introduced; tests continue to use the MCP boundary or runner boundary instead of bypassing into lower helpers for behavior that should stay above them. | None |
| Authoritative Boundary Rule check (callers do not depend on both an outer owner and that owner's internal manager/repository/helper/lower-level concern) | Pass | Callers still speak only to `speak` or `run_speak`; the new real deterministic test proves behavior through the MCP boundary rather than combining server and lower-layer direct calls. | None |
| File placement check (file/folder path matches owning concern or explicitly justified shared boundary) | Pass | The new public temperature tests live in `tests/test_speak_temperature.py`, route-specific runtime behavior remains in the existing Chinese/English test files, and source changes stay inside the existing TTS ownership folders. | None |
| Flat-vs-over-split layout judgment (layout is readable for the scope and not artificially fragmented) | Pass | One new focused test file is justified because temperature is a distinct public concern; the rest of the layout remains flat and readable for the scope. | None |
| Interface/API/query/command/service-method boundary clarity (one subject, one responsibility, explicit identity shape) | Pass | `speak` still exposes one subject, “generate speech,” with optional route hints only. The new `temperature` input is clearly defined as an MLX sampling override with a deterministic default. | None |
| Naming quality and naming-to-responsibility alignment check (files, folders, APIs, types, functions, parameters, variables) | Pass | Names such as `mlx_default_temperature`, `test_speak_tool_schema_describes_temperature_input`, and `test_real_mcp_speak_tool_defaults_chinese_temperature_to_deterministic_output` are explicit and match behavior. | None |
| No unjustified duplication of code / repeated structures in changed scope | Pass | The public schema and validation additions are split cleanly by concern; there is no new duplicate helper layer or repeated deterministic-hash logic spread across files. | None |
| Patch-on-patch complexity control | Pass | The re-entry delta remains coherent instead of layering hidden fallback behavior on top of the earlier voice-routing fix. It completes the story by owning temperature and truthful examples directly. | None |
| Dead/obsolete code cleanup completeness in changed scope | Pass | No compatibility wrapper, stale example list, or obsolete validation path remains in the changed scope after the fix. | None |
| Test quality is acceptable for the changed behavior | Pass | The suite now proves the public schema, config parsing, command propagation, non-MLX rejection, and real repeated deterministic output rather than only checking that a WAV exists. | None |
| Test maintainability is acceptable for the changed behavior | Pass | Fast schema/runner tests and real route-specific tests stay separated. The new deterministic real test is concise and directly tied to the user-reported regression. | None |
| Validation evidence sufficiency for the changed flow | Pass | The focused suite passed, the real Apple Silicon English/Chinese suite passed, and the new Chinese real test proves identical output hashes under the public MCP path with omitted temperature. | None |
| No backward-compatibility mechanisms (no compatibility wrappers/dual-path behavior) | Pass | The public contract grows by one field but does not retain an old path or compatibility wrapper for replaced behavior. | None |
| No legacy code retention for old behavior | Pass | The stale unsupported Chinese examples are removed from the public schema, and the deterministic default replaces the older implicit runtime-sampling behavior in changed scope. | None |

## Review Scorecard (Mandatory)

- Overall score (`/10`): `9.5`
- Overall score (`/100`): `95`
- Score calculation note: simple average for visibility only; Stage 8 passes because every category is `>= 9.0` and no blocking findings remain.

| Priority | Category | Score (`1.0-10.0`) | Why This Score | What Is Weak / Holding It Down | What Should Improve |
| --- | --- | --- | --- | --- | --- |
| `1` | `Data-Flow Spine Inventory and Clarity` | `9.5` | The new behavior is easy to trace end-to-end: public `temperature` enters once, resolves to one MLX default, and reaches one command owner. | The deterministic policy is still partly conveyed by schema prose instead of a machine-readable capability surface. | Add capability discovery later only if callers need stronger automation than curated schema guidance. |
| `2` | `Ownership Clarity and Boundary Encapsulation` | `9.5` | Default temperature ownership is placed correctly in config/runner rather than leaking into the server or tests. | The route-specific voice examples remain hand-maintained copy in the public boundary. | Keep them synchronized with tested runtime support; revisit only if the supported inventory changes often. |
| `3` | `API / Interface / Query / Command Clarity` | `9.5` | `language`, `voice`, and `temperature` remain intuitive and do not expose lower-layer naming like `language_code` or model ids. | `temperature` is MLX-specific, so the public contract necessarily contains one backend caveat. | Keep the MLX-only caveat explicit and resist widening the field into a fake cross-backend promise. |
| `4` | `Separation of Concerns and File Placement` | `9.0` | Each changed source file owns one clear part of the new policy, and the new focused temperature test is in the right place. | `runner.py` continues to accumulate per-backend validation branches because it is the orchestration owner. | Keep future backend-specific parameter growth small and extract only when another parameter starts repeating the same patterns. |
| `5` | `Shared-Structure / Data-Model Tightness and Reusable Owned Structures` | `9.0` | The data-model change is minimal: one new scalar default plus one public input, without widening into a shared kitchen-sink options object. | The real-route tests still rely on curated route-specific setup instead of a broader shared real-MLX factory. | Introduce a broader shared real-test factory only if more route files genuinely repeat the same setup shape. |
| `6` | `Naming Quality and Local Readability` | `9.0` | New names are concrete and unsurprising, especially around temperature and deterministic-output testing. | The public Chinese example set mixes one title-cased name (`Vivian`) with lowercase ids (`eric`, `serena`). | Standardize example casing later if the product wants a stricter “canonical id” convention in the public schema. |
| `7` | `Validation Strength` | `10.0` | This round closes the exact gap the user found: it adds command-level default/override proof and a real repeated Chinese hash test through the public MCP boundary. | No material validation weakness remains in the changed scope. | None. |
| `8` | `Runtime Correctness Under Edge Cases` | `9.5` | Non-MLX temperature rejection, negative-value validation, incompatible pinned-model behavior, and real deterministic-output validation are all covered. | The curated Chinese speaker list still assumes the runtime model inventory stays stable across future upstream changes. | Recheck curated examples whenever the MLX runtime/model version changes. |
| `9` | `No Backward-Compatibility / No Legacy Retention` | `10.0` | The implementation replaces implicit runtime defaults with an owned deterministic default and does not preserve a legacy parallel path. | No meaningful weakness in this category. | None. |
| `10` | `Cleanup Completeness` | `9.0` | The stale unsupported speaker examples are cleaned up, and the new test slice is tidy rather than layered on top of probe-only evidence. | README / docs sync still remains for Stage 9, so the user-facing prose outside the code/test boundary is not yet updated in this round. | Finish docs sync in Stage 9 so the repository prose matches the new schema/runtime contract. |

## Findings

- None

## Round History

| Round | Trigger | Prior Unresolved Findings Rechecked (`Yes`/`No`/`N/A`) | New Findings Found (`Yes`/`No`) | Gate Decision (`Pass`/`Fail`) | Latest Authoritative (`Yes`/`No`) | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `1` | `Stage 7 pass` | `N/A` | `Yes` | `Fail` | `No` | Shared test-support extraction was incomplete, leaving duplicate helper ownership in the touched test slice. |
| `2` | `Re-entry` | `Yes` | `No` | `Pass` | `No` | Round-1 ownership/cleanup findings were resolved. |
| `3` | `Re-entry` | `Yes` | `No` | `Pass` | `No` | Route-specific public voice guidance and explicit English/Chinese real MCP voice scenarios were structurally clean and sufficiently validated. |
| `4` | `Re-entry` | `Yes` | `No` | `Pass` | `No` | The concise public `language` rename kept the boundary cleaner while preserving real Chinese validation. |
| `5` | `Re-entry` | `Yes` | `No` | `Pass` | `Yes` | The deterministic MLX temperature default, truthful Chinese speaker examples, and real repeated-output proof are structurally clean and sufficiently validated. |

## Re-Entry Declaration (Mandatory On `Fail`)

- Latest authoritative round status: `Pass`
- Latest authoritative round has no active re-entry declaration.
- Historical note: Round `1` failed with classification `Design Impact` and returned through `Stage 1 -> Stage 3 -> Stage 4 -> Stage 5 -> Stage 6 -> Stage 7 -> Stage 8`.

## Gate Decision

- Latest authoritative review round: `5`
- Decision: `Pass`
- Implementation can proceed to `Stage 9`: `Yes`
- Mandatory pass checks:
  - Review scorecard is recorded with rationale, weakness, and required-improvement notes for all ten categories in the canonical priority order -> `Pass`
  - No scorecard category is below `9.0` -> `Pass`
  - All changed source files have effective non-empty line count `<=500` -> `Pass`
  - Required `>220` changed-line delta-gate assessments are recorded for all applicable changed source files -> `Pass`
  - Data-flow spine inventory clarity and preservation under shared principles = `Pass`
  - Ownership boundary preservation = `Pass`
  - Support structure clarity = `Pass`
  - Existing capability/subsystem reuse check = `Pass`
  - Reusable owned structures check = `Pass`
  - Shared-structure/data-model tightness check = `Pass`
  - Repeated coordination ownership check = `Pass`
  - Empty indirection check = `Pass`
  - Scope-appropriate separation of concerns and file responsibility clarity = `Pass`
  - Ownership-driven dependency check = `Pass`
  - Authoritative Boundary Rule check = `Pass`
  - File placement check = `Pass`
  - Flat-vs-over-split layout judgment = `Pass`
  - Interface/API/query/command/service-method boundary clarity = `Pass`
  - Naming quality and naming-to-responsibility alignment check = `Pass`
  - No unjustified duplication of code / repeated structures in changed scope = `Pass`
  - Patch-on-patch complexity control = `Pass`
  - Dead/obsolete code cleanup completeness in changed scope = `Pass`
  - Test quality is acceptable for the changed behavior = `Pass`
  - Test maintainability is acceptable for the changed behavior = `Pass`
  - Validation evidence sufficiency = `Pass`
  - No backward-compatibility mechanisms = `Pass`
  - No legacy code retention = `Pass`
- Notes:
  - The public MCP contract is now cleaner and more truthful because it exposes `language`, `voice`, and `temperature` while keeping lower-layer routing/model details below the boundary.
  - The exact user-reported regression is now closed by durable validation: repeated Chinese real MCP output hashes are identical when temperature is omitted and defaults to `0.0`.
