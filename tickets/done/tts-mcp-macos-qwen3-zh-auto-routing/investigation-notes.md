# Investigation Notes

## Scope Triage

- Scope: `Large`
- Reasoning:
  - The re-entry is no longer about one public API field or one Apple Silicon route.
  - The failure is architectural and crosses the public MCP boundary, runtime bootstrap lifecycle, MLX routing policy, Kokoro Chinese profile/asset policy, backend asset-path handling, tests, and docs.
  - Multiple backend families are affected even though the user-visible feature target remains the same.

## Current Implementation Findings

### Primary Spine Today

- The effective runtime spine is split across:
  - `server.create_server(...)`
  - `runtime_bootstrap.bootstrap_runtime(...)`
  - `runner.run_speak(...)`
  - backend-specific command/runtime helpers
- The MCP boundary and runtime bootstrap lifecycle currently share one owner in `server.py`, which makes the start-up boundary harder to reason about and test independently.

### MLX Routing Ownership Drift

- MLX language-to-model selection is currently owned twice:
  - config-time default preset selection in `config.py`
  - per-call request resolution in `backend_contracts.py`
- Public language alias handling also lives in `backend_contracts.py`.
- This means the same routing policy is split between parse-time settings logic and runtime request logic.

### Kokoro Chinese Policy Drift

- Kokoro Chinese behavior is also split across multiple owners:
  - language normalization in `backend_contracts.py`
  - install-profile and asset-availability policy in `runtime_bootstrap.py`
  - runtime asset/voice selection in `kokoro_runtime.py`
- Installer profile, asset defaults, and runtime synthesis config are logically one concern but are not owned in one place.

### Backend Asset Path Semantics Are Inconsistent

- Relative-path behavior is not coherent across backends:
  - command paths are normalized one way in `config.py`
  - XTTS speaker WAV is resolved against `cwd` in `backend_commands.py`
  - Chatterbox prompt path is forwarded raw
  - Kokoro assets are resolved against runtime root in more than one module
- There is no single owner for “configured runtime asset path semantics.”

### Tests And Validation Shape

- The recent Apple Silicon/Qwen behavior is well covered by focused tests and a real MCP end-to-end test.
- The architecture issue is therefore not a lack of proof for the feature itself.
- The problem is that future changes will continue to land on top of duplicated routing and path policy unless ownership is corrected now.

### New Independent Review Finding: Kokoro Clean-Install / Per-Call Chinese Gap

- The refactor cleaned up the earlier ownership drift, but the new independent review exposed a still-missing Kokoro use case in the runtime spine.
- Startup bootstrap currently resolves the Kokoro install profile with `language_code=None`.
- That means a clean Linux or Intel Mac server started with default English settings installs the `v1_0` profile by default.
- A later per-call Chinese request on that same server resolves to the `zh_v1_1` asset profile at runtime.
- Because the installer is profile-specific, startup bootstrap and first Chinese synthesis can disagree about which Kokoro asset set exists.
- The current real Linux Kokoro Chinese validation does not cover this path:
  - it disables auto-install,
  - preconfigures zh assets directly,
  - and uses zh defaults rather than an English-default clean install followed by a Chinese request.

### New Independent Review Finding: Kokoro Explicit Path Precedence Is Under-Modeled

- `TtsSettings` carries explicit override metadata for MLX model routing, but not for Kokoro asset paths.
- Kokoro routing therefore guesses “default vs explicit” only by comparing configured Kokoro paths to the default path values.
- That guess breaks an operator case the docs currently imply should work:
  - if the operator explicitly sets the English default Kokoro model/voices paths,
  - a Chinese request is still treated as if the paths were not explicitly pinned,
  - and runtime auto-switches to zh assets anyway.
- The current settings model therefore cannot actually represent “the user explicitly pinned Kokoro defaults.”

## Architectural Conclusion

- The next design must establish three explicit owners:
  1. `startup / runtime lifecycle owner`
  - owns runtime bootstrap/install side effects
  - must not also own MCP tool argument boundaries
  2. `routing policy owner`
  - owns public language canonicalization
  - owns MLX effective-model selection
  - owns Kokoro effective language/profile/asset/runtime-config selection
  - must be reused by bootstrap and synthesis/runtime code
  3. `path semantics owner`
  - owns how backend config file paths and relative paths are normalized
  - command builders should consume already-normalized values rather than re-deciding path bases
- The next design must also establish one coherent Kokoro `clean install -> first request` policy and one explicit representation of Kokoro asset-pin precedence.

## Likely Structural Direction

- Keep `server.py` boundary-only:
  - build the MCP tool surface
  - forward already-resolved user intent into `run_speak(...)`
- Move bootstrap/startup side effects behind a separate startup entrypoint used by `main()`.
- Consolidate backend routing and backend asset/profile selection into one dedicated policy layer instead of leaving pieces in `config.py`, `runtime_bootstrap.py`, and `kokoro_runtime.py`.
- Move runtime-relative path normalization into one reusable owner and apply it consistently to backend file-path settings.
- Revisit whether Kokoro asset installation should be:
  - eager for all profiles needed by future per-call routing,
  - lazy on the first request that needs a missing profile,
  - or narrowed to an explicit env-default-only contract.
- Revisit whether Kokoro asset-path settings need explicit `*_explicit` metadata similar to MLX so path-precedence behavior is representable instead of guessed.

## Risks To Address

- Do not regress the current Apple Silicon Chinese Qwen behavior while consolidating ownership.
- Do not regress German or English MLX routing.
- Keep explicit MLX overrides authoritative.
- Keep Linux Kokoro Chinese support intact while moving Kokoro policy into a single owner.
- Do not leave the Kokoro clean-install path in a state where the first per-call Chinese request resolves to assets startup bootstrap never installed.
- Do not keep documentation that says Kokoro auto-switching happens only when paths were not explicitly set unless the settings model can actually represent that explicitness.
- Avoid introducing a new “helper blob”; the new owner must be concrete and clearly responsible for routing/runtime policy rather than becoming a catch-all utility file.
