# Docs Sync: Image/Audio CLI generation_config JSON support

## Scope

- Ticket: `image-audio-cli-generation-config-json`
- Trigger Stage: `9`
- Workflow state source: `tickets/in-progress/image-audio-cli-generation-config-json/workflow-state.md`

## Why Docs Were Updated

- Summary: The CLI now accepts MCP-shaped nested JSON through `--generation-config` and file-based JSON through `--generation-config-file`.
- Why this change matters to long-lived project understanding: README command-line usage is the durable user-facing source for how agents and humans should call the CLI. It must reflect that direct nested `generation_config` is now supported and preferred for Agent DX.

## Long-Lived Docs Reviewed

| Doc Path | Why It Was Reviewed | Result | Notes |
| --- | --- | --- | --- |
| `autobyteus-image-audio/README.md` | Primary CLI and MCP usage guide. | Updated | Added direct JSON and file config examples; retained simple `--config` docs. |
| `autobyteus-image-audio/DESIGN.md` | Design overview check. | No change | Existing high-level design does not need detail for this CLI argument additive change. |

## Docs Updated

| Doc Path | Type Of Update | What Was Added / Changed | Why |
| --- | --- | --- | --- |
| `autobyteus-image-audio/README.md` | CLI usage documentation | Added `--generation-config` examples, `--generation-config-file` example, updated multi-speaker example to direct MCP-shaped JSON, clarified that `--config` remains simple override syntax. | Align durable docs with implemented CLI behavior and Agent DX preference. |

## Durable Design / Runtime Knowledge Promoted

| Topic | What Future Readers Need To Understand | Source Ticket Artifact(s) | Target Long-Lived Doc |
| --- | --- | --- | --- |
| Direct MCP-shaped generation config | The CLI can now accept a full nested JSON object that maps directly to MCP `generation_config`. | `requirements.md`, `implementation.md`, `api-e2e-testing.md` | `autobyteus-image-audio/README.md` |
| File-based generation config | Larger nested configs can be stored in a JSON file and passed with `--generation-config-file`. | `requirements.md`, `implementation.md` | `autobyteus-image-audio/README.md` |
| Simple overrides remain available | `--config key=value` and `--speaker/--voice` remain available for simple human CLI use. | `requirements.md`, `implementation.md` | `autobyteus-image-audio/README.md` |

## Removed / Replaced Components Recorded

| Old Component / Path / Concept | What Replaced It | Where The New Truth Is Documented |
| --- | --- | --- |
| CLI docs implying no raw MCP JSON/config-file workflow for normal use | Additive docs explaining direct nested JSON as primary Agent DX path and config-file as larger-config path | `autobyteus-image-audio/README.md` |

## Final Result

- Result: `Updated`
- If blocked because earlier-stage work is required, classification: `N/A`
- Required return path or unblock condition: `N/A`
- Follow-up needed: `None`

---

# Re-Entry Docs Sync: Removed split config flags

## Why Docs Were Updated

The README now needs to state that model-specific CLI configuration is intentionally MCP-shaped only. Split aliases such as `--config`, `--speaker`, and `--voice` are no longer part of the CLI contract.

## Long-Lived Docs Reviewed

| Doc Path | Why It Was Reviewed | Result | Notes |
| --- | --- | --- | --- |
| `autobyteus-image-audio/README.md` | Primary CLI usage guide. | Updated | Removed simple override example and documented that split aliases are not exposed. |

## Docs Updated

| Doc Path | Type Of Update | What Was Added / Changed | Why |
| --- | --- | --- | --- |
| `autobyteus-image-audio/README.md` | CLI usage documentation | Removed `--config` example; clarified no `--config`, `--speaker`, or `--voice` aliases. | Align docs with no-backward-compat/no-legacy policy and final CLI behavior. |

## Final Result

- Result: `Updated`
- Follow-up needed: `None`
