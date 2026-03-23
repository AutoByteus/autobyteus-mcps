# Implementation Plan

## Status

- Ticket: `tts-mcp-xtts-chatterbox-backends`
- Stage: `6`
- Plan Status: `Completed`
- Last Updated: `2026-03-23`

## Re-Entry Context

- The Stage 8 design-impact issue is already resolved.
- The current re-entry is a `Local Fix` cycle triggered by the second deep code review.
- The new Stage 6 cycle is therefore a backend-hardening and package-boundary cycle:
  - preserve the public MCP API
  - preserve the split-owner runner architecture
  - fail XTTS fast when no reference speaker is configured
  - make explicit backend wrappers and runtime auto-install work outside a source checkout

## Objectives

1. Add XTTS preflight validation so the backend fails as a config error before spawning Coqui when no usable speaker reference is configured.
2. Remove runtime dependence on repo-root wrapper-script paths for explicit XTTS and Chatterbox execution.
3. Remove runtime dependence on repo-root installer-script paths for MLX, XTTS, Chatterbox, llama.cpp, and Kokoro bootstrap.
4. Keep source-checkout workflows working for existing manual commands and local validation.
5. Re-run Stage 7 and Stage 8 on the fixed package-boundary implementation.

## Implementation Slices

### Slice 1: XTTS Config Preflight

- Update XTTS command construction so it requires a configured reference speaker WAV in the current MCP design.
- Validate that the configured path exists before launching the XTTS subprocess.
- Add focused tests for:
  - missing `XTTS_DEFAULT_SPEAKER_WAV`
  - nonexistent `XTTS_DEFAULT_SPEAKER_WAV`
  - Result: `Completed`

### Slice 2: Script Asset Resolution

- Add one small runtime-path helper that can:
  - detect a source checkout
  - choose a stable runtime root when no checkout exists
  - resolve wrapper/installer scripts from either the source tree or packaged assets
- Update explicit backend command builders to use that resolver instead of `Path(__file__).parents[2] / "scripts"`.
  - Result: `Completed`

### Slice 3: Packaged Runtime Assets

- Ship the explicit backend wrapper scripts and installer scripts as package-owned assets.
- Keep existing root `scripts/` entrypoints usable in a source checkout.
- Update package metadata so the asset scripts are included in wheel builds.
  - Result: `Completed`

### Slice 4: Bootstrap Root Hardening

- Update runtime bootstrap to:
  - use the new runtime-root helper instead of assuming the package lives inside a repository root
  - pass the resolved runtime root through to installer scripts
  - keep current checkout behavior intact
  - Result: `Completed`

### Slice 5: Verification

- Re-run targeted unit/integration tests covering:
  - config/runner validation
  - platform/bootstrap behavior
  - version-check and wrapper resolution
- Rebuild the wheel and verify the needed scripts are present.
- Refresh Stage 7 evidence if behavior or packaging-boundary execution changed.
  - Result: `Completed`

## Non-Goals

- Changing the MCP `speak` signature
- Changing backend selection policy
- Changing the preferred German backend
- Reopening the resolved Stage 8 ownership split

## Risks and Mitigations

- Risk: package-boundary fixes reintroduce empty indirection.
  - Mitigation: keep one small path/asset helper and reuse existing owners.
- Risk: packaged-script support creates unjustified duplication.
  - Mitigation: keep source-checkout entrypoints thin and treat packaged assets as distribution support, not another orchestration layer.
- Risk: runtime-root fallback changes existing checkout behavior.
  - Mitigation: preserve source-root detection first and only use fallback when no checkout is present.

## Exit Criteria For This Stage 6 Cycle

- XTTS fails fast on missing or invalid default speaker reference.
- Explicit XTTS and Chatterbox backend wrappers resolve in both source-checkout and wheel-installed layouts.
- Runtime bootstrap no longer depends on repo-root script paths.
- Wheel contents include the required packaged runtime assets.
- Targeted verification passes and is recorded.
