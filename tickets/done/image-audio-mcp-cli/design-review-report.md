# Design Review Report

## Review Round Meta

- Upstream Requirements Doc: `/Users/normy/autobyteus_org/autobyteus_mcps-image-audio-mcp-cli/tickets/in-progress/image-audio-mcp-cli/requirements.md`
- Upstream Investigation Notes: `/Users/normy/autobyteus_org/autobyteus_mcps-image-audio-mcp-cli/tickets/in-progress/image-audio-mcp-cli/investigation-notes.md`
- Reviewed Design Spec: `/Users/normy/autobyteus_org/autobyteus_mcps-image-audio-mcp-cli/tickets/in-progress/image-audio-mcp-cli/design-spec.md`
- Current Review Round: 3
- Trigger: Superseding design package from `solution_designer` after user clarified generation-config CLI UX: primary per-call dynamic `--config key=value`, dot notation for nested settings, optional advanced raw JSON only, config files not primary, and paired `--speaker` / `--voice` flags for multi-speaker speech.
- Prior Review Round Reviewed: 2
- Latest Authoritative Round: 3
- Current-State Evidence Basis: Reviewed the updated requirements, investigation notes, and design spec; rechecked the prior round-2 design review report. The working tree also contains in-progress implementation changes from downstream work, but this report is a design-package review rather than a code review.

Round rules:
- Reuse the same finding IDs across reruns for the same unresolved design-review issues.
- Create new finding IDs only for newly discovered issues.

## Round History

| Round | Trigger | Prior Unresolved Findings Rechecked | New Findings Found | Review Decision | Latest Authoritative | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Initial design handoff from `solution_designer` | N/A | No blocking findings | Pass | No | Superseded by round 2 after CLI UX clarification. |
| 2 | Updated design handoff with explicit CLI UX authority | None from round 1 | No blocking findings | Pass | No | Superseded by round 3 after generation-config UX clarification. |
| 3 | Updated design handoff with dynamic config and multi-speaker flag UX | None from round 2 | No blocking findings | Pass | Yes | Updated design remains ready for implementation. |

## Reviewed Design Spec

The reviewed design now proposes the boundary:

`skill-facing wrapper -> uv project execution -> ergonomic project CLI -> image_audio_mcp.services -> Autobyteus clients/filesystem`

and preserves MCP mode as:

`MCP client -> image_audio_mcp.server FastMCP facade -> image_audio_mcp.services -> Autobyteus clients/filesystem`.

Round 3 specifically reviewed the generation-config UX update:

- Primary generation settings UX is repeatable `--config key=value`.
- Nested settings use dot notation, for example `--config image_config.aspect_ratio=16:9`.
- Raw JSON config may exist only as an advanced escape hatch if implementation keeps it; it is not the documented primary path.
- Config files are not preferred for normal per-call generation settings.
- Multi-speaker speech uses paired flags, for example `--speaker Joe --voice Kore --speaker Jane --voice Puck`.
- The CLI validates matching speaker/voice counts and builds `generation_config.speaker_mapping` in pair order.

This is architecturally sound because dynamic config parsing and speaker/voice pairing are shell-input adaptation concerns owned by `image_audio_mcp.cli`; shared services still receive a normal `generation_config` dict and remain independent of CLI syntax.

## Task Design Health Assessment Verdict

| Assessment Area | Result (`Pass`/`Fail`) | Evidence | Required Action |
| --- | --- | --- | --- |
| Assessment is present for the current task posture | Pass | Updated design keeps the work classified as a feature with required refactor. | None. |
| Root-cause classification is explicit and evidence-backed | Pass | Classification remains `Boundary Or Ownership Issue`, supported by current nested MCP closures in `server.py:create_server()` and the need to avoid duplicated execution or MCP-subprocess CLI coupling. | None. |
| Refactor needed now / no refactor needed / deferred decision is explicit | Pass | Refactor needed now; service extraction is the response. | None. |
| Refactor decision is supported by the concrete design sections or residual-risk rationale | Pass | Spines, ownership map, file mapping, dependency rules, migration sequence, and validation plan all reflect shared services plus thin MCP/CLI facades. | None. |

## Prior Findings Resolution Check (Mandatory On Round >1)

| Prior Round | Finding ID | Previous Severity | Current Resolution | Evidence | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | N/A | N/A | No unresolved findings to recheck | Round 1 had no blocking findings and passed. | Superseded by round 2 due to updated upstream artifacts. |
| 2 | N/A | N/A | No unresolved findings to recheck | Round 2 had no blocking findings and passed. | Superseded by round 3 due to updated generation-config UX. |

## Spine Inventory Verdict

| Spine ID | Scope | Spine Is Readable? (`Pass`/`Fail`) | Narrative Is Clear? (`Pass`/`Fail`) | Facade Vs Governing Owner Is Clear? (`Pass`/`Fail`/`N/A`) | Main Domain Subject Naming Is Clear? (`Pass`/`Fail`) | Ownership Is Clear? (`Pass`/`Fail`) | Off-Spine Concerns Stay Off Main Line? (`Pass`/`Fail`) | Verdict (`Pass`/`Fail`) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DS-001 | Skill/user CLI end-to-end | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| DS-002 | Existing MCP tool-call end-to-end | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| DS-003 | CLI result/error return path | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| DS-004 | Wrapper-local uv execution/setup path | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| DS-005 | Service provider call and cleanup lifecycle | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| DS-006 | Coordinate finding internal flow | Pass | Pass | Pass | Pass | Pass | Pass | Pass |

## Subsystem / Capability-Area Allocation Verdict

| Subsystem / Capability Area | Ownership Allocation Is Clear? (`Pass`/`Fail`) | Reuse / Extend / Create-New Decision Is Sound? (`Pass`/`Fail`) | Supports The Right Spine Owners? (`Pass`/`Fail`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- |
| Project services | Pass | Pass | Pass | Pass | Correct authoritative capability owner for shared MCP/CLI execution. |
| MCP facade | Pass | Pass | Pass | Pass | Existing `server.py` remains the FastMCP public boundary and compatibility target. |
| Project CLI facade | Pass | Pass | Pass | Pass | Owns argparse command UX, option mapping, dynamic config parsing, speaker/voice pairing, JSON envelopes, examples/help, and exit codes. |
| Root wrapper | Pass | Pass | Pass | Pass | Owns path-independent `uv --directory ... run --frozen` execution and setup hiding. |
| Tests | Pass | Pass | Pass | Pass | Local/mock tests, CLI parser/envelope tests, config parsing tests, MCP compatibility checks, and optional provider tests are appropriately allocated. |
| Docs | Pass | Pass | Pass | Pass | README/DESIGN updates are scoped to simple wrapper-first CLI docs plus preserved MCP docs. |

## Reusable Owned Structures Verdict

| Repeated Structure / Logic | Extraction Need Was Evaluated? (`Pass`/`Fail`) | Shared File Choice Is Sound? (`Pass`/`Fail`/`N/A`) | Ownership Of Shared Structure Is Clear? (`Pass`/`Fail`/`N/A`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- |
| Tool execution payload shapes | Pass | Pass | Pass | Pass | Service return dicts preserve existing MCP result payloads; CLI wraps them under `result`. |
| Path/media normalization helpers | Pass | Pass | Pass | Pass | Belongs in services so CLI and MCP cannot diverge on file safety. |
| CLI response envelope | Pass | Pass | Pass | Pass | Belongs in CLI facade only; services remain CLI-agnostic. |
| Dynamic generation-config parsing | Pass | Pass | Pass | Pass | Belongs in CLI facade; it converts `--config key=value` and optional advanced JSON into one service `generation_config` dict. |
| Multi-speaker speaker/voice pairing | Pass | Pass | Pass | Pass | Belongs in CLI facade; it validates counts and builds `generation_config.speaker_mapping` before service invocation. |
| CLI option projection rules | Pass | Pass | Pass | Pass | Command/option naming is a CLI facade concern, not an MCP schema copy. |

## Shared Structure / Data Model Tightness Verdict

| Shared Structure / Type / Schema | One Clear Meaning Per Field? (`Pass`/`Fail`) | Redundant Attributes Removed? (`Pass`/`Fail`) | Overlapping Representation Risk Is Controlled? (`Pass`/`Fail`) | Shared Core Vs Specialized Variant / Composition Decision Is Sound? (`Pass`/`Fail`/`N/A`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Service result dicts | Pass | Pass | Pass | Pass | Pass | Existing MCP result keys stay authoritative and command-specific. |
| CLI envelope | Pass | Pass | Pass | Pass | Pass | `ok`, `command`, `result` / `error_type`, `error_message` are singular and automation-safe. |
| Generation config dict | Pass | Pass | Pass | N/A | Pass | Multiple CLI syntaxes, if any, must converge into one dict before the service boundary. Primary docs should show `--config`, not raw JSON/config files. |
| `speaker_mapping` constructed from speaker/voice pairs | Pass | Pass | Pass | Pass | Pass | Pair order is explicit; mismatched counts fail as usage errors. |
| MCP schema vs CLI option shape | Pass | Pass | Pass | Pass | Pass | Design avoids overlapping authority: MCP schema governs MCP; CLI facade governs user-facing option projection. |

## Removal / Decommission Completeness Verdict

| Item / Area | Redundant / Obsolete Piece To Remove Is Named? (`Pass`/`Fail`) | Replacement Owner / Structure Is Clear? (`Pass`/`Fail`/`N/A`) | Removal / Decommission Scope Is Explicit? (`Pass`/`Fail`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- |
| Stale `mcp-cli-tools` workflow-state approach | Pass | Pass | Pass | Pass | Already removed; design forbids recreating `workflow-state.md`. |
| Business execution inside nested MCP closures | Pass | Pass | Pass | Pass | Replaced by `image_audio_mcp.services`; server closures become thin delegates. |
| Host-specific generated absolute-path wrappers | Pass | Pass | Pass | Pass | Replaced by path-independent `cli/autobyteus-image-audio`. |
| Generic raw `call-tool` primary UX | Pass | Pass | Pass | Pass | Rejected; ergonomic task-oriented subcommands/options are the replacement. |
| Raw JSON/config-file-first generation settings | Pass | Pass | Pass | Pass | Rejected as primary UX; replaced by repeatable `--config key=value` with dot notation. |
| Unreferenced nested VLM coordinate helper if unused | Pass | Pass | Pass | Pass | Clear fold-or-remove rule under services. |
| Hidden public grounding tools | Pass | Pass | Pass | Pass | Remain unexposed; compatibility validation covers this. |

## File Responsibility Mapping Verdict

| File | Responsibility Is Singular And Clear? (`Pass`/`Fail`) | Responsibility Matches The Intended Owner/Boundary? (`Pass`/`Fail`) | Responsibilities Were Re-Tightened After Shared-Structure Extraction? (`Pass`/`Fail`/`N/A`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- |
| `autobyteus-image-audio/src/image_audio_mcp/services.py` | Pass | Pass | Pass | Pass | Cohesive project capability owner; services receive config dicts and must not parse CLI syntax. |
| `autobyteus-image-audio/src/image_audio_mcp/server.py` | Pass | Pass | Pass | Pass | Owns FastMCP schema/registration and delegates execution. |
| `autobyteus-image-audio/src/image_audio_mcp/cli.py` | Pass | Pass | Pass | Pass | Owns ergonomic subcommands/options, `--config` parsing, optional advanced JSON escape hatch if kept, speaker/voice validation, envelope, dispatch, help/examples, and exit codes. |
| `cli/autobyteus-image-audio` | Pass | Pass | N/A | Pass | Shell wrapper owns repo path resolution and uv execution only. |
| `autobyteus-image-audio/tests/conftest.py` | Pass | Pass | N/A | Pass | Optional `.env.test` loading fixes clean-checkout validation. |
| `autobyteus-image-audio/tests/test_services_local.py` | Pass | Pass | N/A | Pass | Service behavior validation with mocked clients. |
| `autobyteus-image-audio/tests/test_cli_local.py` | Pass | Pass | N/A | Pass | Must cover ergonomic parsing, repeatable flags, `--config` dot notation, multi-speaker pairs, envelopes, and service delegation. |
| `autobyteus-image-audio/tests/test_server_local.py` | Pass | Pass | N/A | Pass | MCP compatibility validation remains isolated. |
| `autobyteus-image-audio/README.md` / `DESIGN.md` | Pass | Pass | N/A | Pass | Docs update scope is clear and rejects raw MCP/manual setup/config-file-first primary usage. |
| `autobyteus-image-audio/pyproject.toml` / `uv.lock` | Pass | Pass | N/A | Pass | Script metadata and locked environment support wrapper `--frozen`. |

## Dependency Direction / Forbidden Shortcut Verdict

| Owner / Boundary | Allowed Dependencies Are Clear? (`Pass`/`Fail`) | Forbidden Shortcuts Are Explicit? (`Pass`/`Fail`) | Direction Is Coherent With Ownership? (`Pass`/`Fail`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- |
| Root wrapper | Pass | Pass | Pass | Pass | Wrapper calls uv/project CLI only and must not parse image/audio semantics. |
| Project CLI | Pass | Pass | Pass | Pass | CLI depends on services, not FastMCP or provider factories; it translates shell syntax into service parameters/config dicts. |
| MCP facade | Pass | Pass | Pass | Pass | Server depends on services; it must not depend on CLI. |
| Services | Pass | Pass | Pass | Pass | Services may depend on Autobyteus factories/utilities and filesystem helpers only. |
| Docs/skills | Pass | Pass | Pass | Pass | Primary docs must not teach manual setup, raw MCP JSON, raw JSON config as primary, or config-file-first workflows for normal per-call settings. |

## Boundary Encapsulation Verdict

| Boundary / Owner | Authoritative Public Entry Point Is Clear? (`Pass`/`Fail`) | Internal Owned Mechanisms Stay Internal? (`Pass`/`Fail`) | Caller Bypass Risk Is Controlled? (`Pass`/`Fail`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- |
| `image_audio_mcp.services` | Pass | Pass | Pass | Pass | Authoritative capability boundary for CLI and MCP. |
| `image_audio_mcp.cli` | Pass | Pass | Pass | Pass | Public project console-script entrypoint and owner of CLI ergonomics/config syntax. |
| `cli/autobyteus-image-audio` | Pass | Pass | Pass | Pass | Skill-facing setup boundary over uv/project CLI. |
| `image_audio_mcp.server` | Pass | Pass | Pass | Pass | Public MCP entrypoint preserving existing tool schemas and launch paths. |

## Interface Boundary Verdict

| Interface / API / Query / Command / Method | Subject Is Clear? (`Pass`/`Fail`) | Responsibility Is Singular? (`Pass`/`Fail`) | Identity Shape Is Explicit? (`Pass`/`Fail`) | Generic Boundary Risk (`Low`/`Medium`/`High`) | Verdict (`Pass`/`Fail`) |
| --- | --- | --- | --- | --- | --- |
| `services.health_check()` | Pass | Pass | Pass | Low | Pass |
| `services.list_audio_models()` | Pass | Pass | Pass | Low | Pass |
| `services.list_image_models()` | Pass | Pass | Pass | Low | Pass |
| `services.generate_image(...)` | Pass | Pass | Pass | Low | Pass |
| `services.edit_image(...)` | Pass | Pass | Pass | Low | Pass |
| `services.generate_speech(...)` | Pass | Pass | Pass | Low | Pass |
| `services.find_target_coordinates(...)` | Pass | Pass | Pass | Low | Pass |
| CLI `--config key=value` projection | Pass | Pass | Pass | Low | Pass |
| CLI `--speaker` / `--voice` pair projection | Pass | Pass | Pass | Low | Pass |
| Root wrapper command | Pass | Pass | Pass | Low | Pass |
| FastMCP tool facade methods | Pass | Pass | Pass | Low | Pass |

## Subsystem / Folder / File Placement Verdict

| Path / Item | Target Placement Is Clear? (`Pass`/`Fail`) | Folder Matches Owning Boundary? (`Pass`/`Fail`) | Mixed-Layer Or Over-Split Risk (`Low`/`Medium`/`High`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- |
| `autobyteus-image-audio/src/image_audio_mcp/` | Pass | Pass | Low | Pass | Flat package layout is justified for the small project; separate files make boundaries readable. |
| `cli/` | Pass | Pass | Low | Pass | Repo-level wrapper location is appropriate for skill-facing path-independent commands. |
| `autobyteus-image-audio/tests/` | Pass | Pass | Low | Pass | Existing test folder extended with service/CLI/MCP split. |
| `tickets/in-progress/image-audio-mcp-cli/` | Pass | Pass | Low | Pass | Ticket artifacts only; no workflow-state artifact. |

## Existing Capability / Subsystem Reuse Verdict

| Need / Concern | Existing Capability Area Was Checked? (`Pass`/`Fail`) | Reuse / Extension Decision Is Sound? (`Pass`/`Fail`) | New Support Piece Is Justified? (`Pass`/`Fail`/`N/A`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- |
| Provider image/audio execution | Pass | Pass | N/A | Pass | Reuses Autobyteus multimedia clients. |
| Safe path resolution | Pass | Pass | N/A | Pass | Reuses `resolve_safe_path`. |
| File download/write | Pass | Pass | N/A | Pass | Reuses `download_file_from_url`. |
| MCP transport | Pass | Pass | N/A | Pass | Extends/refactors existing `server.py`; public surface preserved. |
| CLI surface | Pass | Pass | Pass | Pass | New CLI justified because no terminal command surface exists. |
| Shared capability owner | Pass | Pass | Pass | Pass | New services boundary justified because current closures are not reusable. |
| Root skill-facing wrapper | Pass | Pass | Pass | Pass | New wrapper justified to hide uv setup and allow invocation from any cwd. |

## Legacy / Backward-Compatibility Verdict

| Area | Compatibility Wrapper / Dual-Path / Legacy Retention Exists? (`Yes`/`No`) | Clean-Cut Removal Is Explicit? (`Pass`/`Fail`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- |
| CLI over MCP subprocess | No | Pass | Pass | Rejected in favor of direct services. |
| Generic raw `call-tool` primary UX | No | Pass | Pass | Rejected in favor of task-oriented commands/options. |
| Raw JSON/config-file-first generation settings as normal UX | No | Pass | Pass | Rejected in favor of repeatable `--config key=value`; raw JSON may remain advanced only. |
| Duplicated CLI/MCP tool bodies | No | Pass | Pass | Rejected; services own execution. |
| Host-specific wrapper system | No | Pass | Pass | Rejected; path-independent root wrapper. |
| Manual setup in skill docs | No | Pass | Pass | Rejected as primary path. |
| Existing MCP server | No | Pass | Pass | Preserved as explicit product requirement, not stale compatibility. |

## Migration / Refactor Safety Verdict

| Area | Sequence Is Realistic? (`Pass`/`Fail`) | Temporary Seams Are Explicit? (`Pass`/`Fail`) | Cleanup / Removal Is Explicit? (`Pass`/`Fail`) | Verdict (`Pass`/`Fail`) |
| --- | --- | --- | --- | --- |
| Service extraction | Pass | Pass | Pass | Pass |
| MCP facade update | Pass | Pass | Pass | Pass |
| Ergonomic CLI facade and console script | Pass | Pass | Pass | Pass |
| Dynamic config parser and multi-speaker pair validation | Pass | Pass | Pass | Pass |
| Root wrapper and uv/lock validation | Pass | Pass | Pass | Pass |
| Test bootstrap and local/mock validation | Pass | Pass | Pass | Pass |
| Documentation update | Pass | Pass | Pass | Pass |

## Example Adequacy Verdict

| Topic / Area | Example Was Needed? (`Yes`/`No`) | Example Is Present And Clear? (`Pass`/`Fail`/`N/A`) | Bad / Avoided Shape Is Explained When Helpful? (`Pass`/`Fail`/`N/A`) | Verdict (`Pass`/`Fail`) | Notes |
| --- | --- | --- | --- | --- | --- |
| Skill-facing usage | Yes | Pass | Pass | Pass | Shows wrapper command and rejects manual setup flow. |
| CLI option design | Yes | Pass | Pass | Pass | Shows repeatable `--input-image` and `--config image_config.aspect_ratio=16:9`; rejects raw `call-tool --arguments` as normal UX. |
| Multi-speaker speech | Yes | Pass | Pass | Pass | Shows paired `--speaker` / `--voice` flags and rejects less-readable encodings as normal UX. |
| Wrapper internals | Yes | Pass | Pass | Pass | Shows `uv --directory "$PROJECT_DIR" run --frozen ...` and rejects host-specific paths. |
| Shared execution | Yes | Pass | Pass | Pass | Shows MCP and CLI both calling services. |
| Public surfaces | Yes | Pass | Pass | Pass | Distinguishes server, CLI, and services ownership. |

## Missing Use Cases / Open Unknowns

| Item | Why It Matters | Required Action | Status |
| --- | --- | --- | --- |
| `--config` value typing | `key=value` strings must become provider-appropriate Python/JSON values without surprising agents. | Implementation should define deterministic scalar parsing in CLI help/tests. A reasonable rule is JSON-literal parsing when valid (`true`, `false`, `null`, numbers, arrays/objects), otherwise preserve as string. | Non-blocking implementation detail; belongs in CLI parser/tests. |
| `--config` conflict/merge order | Repeated dynamic config and speaker mapping can target overlapping keys. | Implementation should define merge precedence and reject ambiguous duplicate/conflicting keys where practical, especially if `--config speaker_mapping=...` conflicts with `--speaker/--voice`. | Non-blocking implementation detail; design ownership is clear. |
| Optional advanced raw JSON config | Raw JSON may exist only as an advanced escape hatch; if kept, it can overlap with `--config`. | Implementation must keep docs/examples `--config`-first and define how JSON combines with repeated `--config`; if this becomes complex, omit raw JSON for this ticket. | Non-blocking; requirements allow but do not require raw JSON. |
| Optional command grouping/aliases vs baseline command names | Requirements allow refinement if demonstrably more usable. | If implementation deviates from baseline names, document rationale, preserve coverage for all seven public MCP capabilities, keep skill examples simple, and update tests/docs. | Non-blocking implementation discretion. |
| Wrapper-level failures before Python CLI startup | The skill-facing command begins at the root wrapper, so missing `uv` or `uv --frozen` setup failures must be clear even when Python CLI cannot emit its normal envelope. | Check missing `uv`, emit a clear failure, and validate wrapper from outside the project; arbitrary uv failures may use concise stderr if full JSON wrapping is impractical. | Non-blocking residual implementation risk; design is explicit enough. |
| Real provider generation | Provider calls may need credentials and may incur cost. | Keep automated local validation mocked; leave provider tests optional/skipped without credentials. | Covered by requirements and design. |
| MCP schema drift during extraction | Moving nested closures can accidentally alter FastMCP input schemas/descriptions. | Preserve signatures/decorator metadata and run in-memory MCP compatibility validation. | Covered by design. |

## Review Decision

Pass: the updated design is ready for implementation.

The boundary `skill-facing wrapper -> uv project execution -> ergonomic project CLI -> shared services -> Autobyteus clients/filesystem`, with MCP preserved as a FastMCP facade over the same services, remains sound. The generation-config UX update strengthens the design: `--config key=value` and paired `--speaker` / `--voice` are CLI-facade concerns that improve skill-facing ergonomics without weakening service ownership or MCP compatibility.

## Findings

None.

## Classification

N/A. No blocking `Design Impact`, `Requirement Gap`, or `Unclear` findings were found.

## Recommended Recipient

`implementation_engineer`

## Residual Risks

- Service extraction may unintentionally alter MCP schemas or result shapes; implementation must preserve decorator signatures/metadata and run MCP compatibility tests.
- `--config key=value` parsing needs deterministic scalar typing, dot-notation merge behavior, and tests so provider configs are not silently malformed.
- Speaker/voice pair handling must validate matching counts and build `generation_config.speaker_mapping` in pair order; mismatches should be usage errors with JSON failure envelopes after Python CLI startup.
- Raw JSON config, if kept, must remain advanced-only and must not displace `--config` in docs/examples; if merge semantics become complex, omit raw JSON for this ticket.
- CLI UX latitude must stay bounded: normal skill usage must not devolve into raw MCP JSON, config-file-first workflows, or a generic `call-tool` interface.
- If implementation deviates from baseline command names or adds aliases/grouping, it must document why and keep coverage/tests/docs complete.
- `uv --frozen` may fail after adding the console script unless lock state is updated; implementation must validate wrapper execution from outside the project directory.
- Wrapper-level pre-Python failures cannot always be normalized by `image_audio_mcp.cli`; implementation should make missing `uv` clear and keep other setup failures concise.
- Real provider calls remain credential-gated and should not be required for local validation.
- The `.env.test` collection blocker must be fixed before relying on clean-checkout test results.

## Latest Authoritative Result

- Review Decision: Pass
- Notes: Round 3 supersedes rounds 1 and 2. Proceed with implementation using the latest requirements/design: preserve MCP unchanged, extract shared services, build an ergonomic task-oriented CLI with wrapper-hidden uv setup, make repeatable `--config key=value` the primary generation-settings UX, support paired `--speaker` / `--voice` for multi-speaker speech, and do not recreate `workflow-state.md` or broad multi-MCP CLI scope.
