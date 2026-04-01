# Future-State Runtime Call Stack Review

## Review Status

- Current Status: `Go Confirmed`
- Reviewed Artifacts:
  - `requirements.md`
  - `proposed-design.md`
  - `future-state-runtime-call-stack.md`

## Round 1

- Result: `Clean`
- Findings:
  - The public language boundary is placed correctly in `server.py` and does not leak backend-specific alias policy into the MCP surface.
  - The Apple Silicon Chinese route stays inside the existing MLX spine rather than introducing a special-case backend fork.
  - Explicit MLX override precedence is preserved.
  - The Stage 7 requirement now explicitly requires public `speak`-tool executable validation for the Chinese Apple Silicon path.
- Required Artifact Updates: `None`
- New Use Cases Discovered: `No`
- Blocking Issues: `No`

## Round 2

- Result: `Clean`
- Findings:
  - Ownership remains coherent:
    - `server.py` owns public argument resolution.
    - `backend_contracts.py` owns public language canonicalization and MLX request resolution.
    - `backend_commands.py` consumes resolved MLX request data.
    - `runner.py` stays orchestration-focused.
  - The design covers the necessary end-to-end scenarios:
    - Chinese Apple Silicon automatic Qwen routing
    - English/German non-regression
    - explicit MLX override preservation
    - one canonical public `language_code` field with alias-value canonicalization
  - No additional upstream requirement or design changes are required before implementation.
- Required Artifact Updates: `None`
- New Use Cases Discovered: `No`
- Blocking Issues: `No`

## Gate Decision

- Decision: `Pass`
- Reason:
  - Two consecutive clean rounds were completed with no blockers, no required persisted updates, and no newly discovered use cases.
- Next Stage:
  - `Stage 6 Implementation`

## Re-Entry Round 3

- Trigger: `User review rejected the duplicated public API fields language and language_code.`
- Classification: `Requirement Gap`
- Persisted Artifact Updates:
  - `requirements.md`
  - `proposed-design.md`
  - `future-state-runtime-call-stack.md`
- Result: `Clean`
- Findings:
  - The public API should expose only one language field.
  - `language_code` is the correct canonical surface because values are code-like and align with existing env naming.
  - Accepting alias values remains fine, but alias parameter names are not.
- Required Artifact Updates: `Completed in this round`
- New Use Cases Discovered: `No`
- Blocking Issues: `No`

## Re-Entry Round 4

- Result: `Clean`
- Findings:
  - The updated design still preserves the same Apple Silicon Chinese Qwen routing.
  - The re-entry narrowed the API surface instead of broadening it.
  - No further upstream updates are required before implementation resumes.
- Required Artifact Updates: `None`
- New Use Cases Discovered: `No`
- Blocking Issues: `No`

## Re-Entry Round 5

- Trigger: `Stage 8 architecture review found ownership drift in startup, MLX routing, Kokoro Chinese policy, and backend asset path semantics.`
- Classification: `Design Impact`
- Persisted Artifact Updates:
  - `investigation-notes.md`
  - `proposed-design.md`
  - `future-state-runtime-call-stack.md`
- Result: `Clean`
- Findings:
  - The future-state spine is materially clearer once startup assembly is separated from the MCP boundary.
  - Routing policy now has one explicit owner instead of being split across config-time and runtime logic.
  - Kokoro Chinese bootstrap and synthesis now share one policy owner instead of duplicating profile/asset logic.
  - Backend asset path semantics are now modeled as one owned concern rather than a backend-by-backend choice.
- Required Artifact Updates: `Completed in this round`
- New Use Cases Discovered: `No`
- Blocking Issues: `No`

## Re-Entry Round 6

- Result: `Clean`
- Findings:
  - The redesign preserves all accepted user-facing behavior while removing the repeated-coordination smells identified in Stage 8.
  - File responsibilities are now scope-appropriate:
    - `server.py` owns boundary construction
    - `app_runtime.py` owns executable startup assembly
    - `routing_policy.py` owns routing/runtime policy
    - `runtime_paths.py` owns path semantics
  - No further upstream artifact changes are required before implementation resumes.
- Required Artifact Updates: `None`
- New Use Cases Discovered: `No`
- Blocking Issues: `No`

## Re-Entry Gate Decision

- Decision: `Pass`
- Reason:
  - Two consecutive clean rounds were completed for the design-impact re-entry with no blockers, no further persisted updates, and no newly discovered use cases.
- Next Stage:
  - `Stage 6 Implementation`

## Re-Entry Round 7

- Trigger: `Independent Stage 8 review found a Kokoro clean-install/per-call Chinese contract gap and missing explicit Kokoro path-precedence metadata.`
- Classification: `Design Impact`
- Persisted Artifact Updates:
  - `investigation-notes.md`
  - `proposed-design.md`
  - `future-state-runtime-call-stack.md`
- Result: `Clean`
- Findings:
  - The new runtime-installation/readiness owner closes the missing request-time Kokoro asset-availability spine.
  - The revised design makes explicit Kokoro path pins representable instead of guessing from path equality.
  - The future-state contract now distinguishes managed Kokoro profile switching from explicit custom asset usage.
- Required Artifact Updates: `Completed in this round`
- New Use Cases Discovered: `No`
- Blocking Issues: `No`

## Re-Entry Round 8

- Result: `Clean`
- Findings:
  - The revised spine remains coherent:
    - `app_runtime.py` owns executable startup
    - `routing_policy.py` owns request resolution
    - `runtime_installation.py` owns startup and request-time runtime readiness
    - execution code consumes only ready resolved requests
  - The new design addresses both independent review findings without reopening the earlier MLX or public-API work.
  - No further upstream artifact changes are required before implementation resumes.
- Required Artifact Updates: `None`
- New Use Cases Discovered: `No`
- Blocking Issues: `No`

## Re-Entry Gate Decision 2

- Decision: `Pass`
- Reason:
  - Two consecutive clean rounds were completed for the new design-impact re-entry with no blockers, no further persisted updates, and no newly discovered use cases.
- Next Stage:
  - `Stage 6 Implementation`
