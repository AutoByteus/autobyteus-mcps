# Future-State Runtime Call Stack Review

## Round 1

- Result: `Clean`
- Findings:
  - Public boundary ownership is correct in `server.py`
  - Lower layers already support MLX `voice`, so no cross-layer redesign is needed
  - Example-based schema metadata is safer than a hardcoded enum because backend support differs
- Required Updates:
  - None

## Round 2

- Result: `Clean`
- Findings:
  - No new use cases discovered beyond public-schema exposure and pass-through delegation
  - Existing backend rejection behavior remains authoritative for unsupported named-voice backends
- Required Updates:
  - None

## Round 3

- Result: `Update Required`
- Findings:
  - Stage 8 review found that the branch scope also includes a partially completed test-support extraction
  - The future-state for this ticket must therefore include one shared owner for MCP session bootstrap and one shared owner for MLX fake-runtime test scaffolding across the touched test slice
- Required Updates:
  - Extend the future-state runtime call stack to include the shared test-support owners that the re-entry implementation must converge on

## Round 4

- Result: `Clean`
- Findings:
  - The public boundary rename from `language_code` to `language` improves the MCP contract without changing lower-layer ownership.
  - Keeping public `language` before `voice` still matches the route-selection flow recorded in the call stack.
  - No new use cases were introduced beyond the renamed route hint and the already-modeled English/Kokoro versus Chinese/Qwen voice paths.
- Required Updates:
  - None

## Round 5

- Result: `Clean`
- Findings:
  - The new Chinese speaker-stability use case is now modeled explicitly instead of being hidden under generic Qwen voice examples.
  - Routing now distinguishes between speaker-capable Chinese Qwen CustomVoice behavior and incompatible pinned-model behavior.
  - Deterministic Chinese no-voice behavior is now owned in routing rather than left to backend drift.
- Required Updates:
  - None

## Round 6

- Result: `Clean`
- Findings:
  - Rechecked the updated future-state call stack with no new use cases, blockers, or required persisted updates.
  - Ownership remains clear: public API stays in `server.py`, routing truth stays in `routing_policy.py`, and backend command emission stays in `backend_commands.py`.
  - The design is narrow and sufficient for a small-scope fix.
- Required Updates:
  - None

## Round 7

- Result: `Clean`
- Findings:
  - The future-state now owns deterministic MLX temperature handling at the public boundary instead of relying on undocumented runtime defaults.
  - Keeping `temperature` optional preserves the intuitive API while letting MCP default omitted MLX requests to `0.0`.
  - Truthful Chinese speaker examples belong in the public schema and should be drawn from the actual installed CustomVoice runtime set rather than generic upstream help text.
- Required Updates:
  - None

## Round 8

- Result: `Clean`
- Findings:
  - Rechecked the updated future-state with no new use cases, blockers, or required persisted updates.
  - Ownership remains clear: `server.py` owns the public `temperature` contract, `config.py` owns the deterministic default, `runner.py` owns override propagation, and `backend_commands.py` owns MLX CLI emission.
  - The design remains small-scope and avoids inventing a seed feature the installed MLX runtime does not expose.
- Required Updates:
  - None

## Gate Decision

- Status: `Go Confirmed`
- Latest Authoritative Round: `8`
