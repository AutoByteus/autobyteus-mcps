# Proposed Design

## Design Version

- Current Version: `v3`

## Artifact Basis

- Investigation Notes: `tickets/done/tts-mcp-macos-qwen3-zh-auto-routing/investigation-notes.md`
- Requirements: `tickets/done/tts-mcp-macos-qwen3-zh-auto-routing/requirements.md`
- Requirements Status: `Design-ready`

## Summary

Preserve the public `speak(..., language_code=...)` behavior and the Apple Silicon MLX Qwen route, but correct the remaining Kokoro contract gap by separating four owners:

1. executable startup assembly
2. runtime routing policy
3. runtime path semantics
4. runtime installation/readiness orchestration

The new design keeps the earlier architecture cleanup and adds one missing rule:
- Kokoro per-call Chinese routing is allowed only when the runtime-installation owner can actually guarantee the needed profile assets, or when explicit operator pins intentionally replace the managed profile behavior.

## Goal / Intended Change

- Preserve the public `speak(..., language_code=...)` surface.
- Preserve Apple Silicon Chinese routing to MLX Qwen.
- Preserve explicit MLX override precedence.
- Preserve Linux and Intel Mac runtime behavior.
- Make Kokoro Chinese per-call behavior coherent on clean installs.
- Make explicit Kokoro asset pins authoritative instead of guessed from path equality.

## Non-Goals

- Do not introduce new user-facing MCP tools.
- Do not broaden the supported backend matrix.
- Do not redesign unrelated runtime/version-check flows.

## Current-State Read

| Area | Findings | Evidence |
| --- | --- | --- |
| Startup ownership | Fixed in the prior re-entry. Startup bootstrap is already separate from the public MCP boundary. | `src/tts_mcp/app_runtime.py`, `src/tts_mcp/server.py` |
| Routing ownership | Fixed in the prior re-entry for MLX and basic Kokoro routing. | `src/tts_mcp/routing_policy.py` |
| Kokoro clean-install contract | Still broken: startup install resolves a default profile while a later Chinese request may require a different managed profile. | `src/tts_mcp/runtime_bootstrap.py`, `src/tts_mcp/routing_policy.py`, `src/tts_mcp/runtime_assets/install_kokoro_onnx_linux.sh` |
| Kokoro explicit-pin precedence | Still broken: explicit Kokoro path pins are inferred from path equality rather than represented explicitly in settings. | `src/tts_mcp/config.py`, `src/tts_mcp/routing_policy.py` |

## Data-Flow Spine Inventory

| Spine ID | Scope | Start | End | Governing Owner | Why It Matters |
| --- | --- | --- | --- | --- | --- |
| DS-001 | Startup spine | executable entrypoint | bootstrapped MCP server ready to run | `app_runtime.py` + `runtime installation owner` | Startup must remain boundary-free and may prepare default runtime assets. |
| DS-002 | Public request spine | `server.speak(...)` | `runner.run_speak(...)` with one canonical request intent | `server.py` | Public MCP handling stays small and boundary-only. |
| DS-003 | Runtime routing spine | `runner.run_speak(...)` | resolved backend request object | `routing_policy.py` | Effective backend language/model/profile/path choices must still be owned once. |
| DS-004 | Runtime readiness spine | resolved request object | backend runtime confirmed ready for that request | `runtime installation owner` | Request-time managed-profile installation is the missing owner for Kokoro Chinese on clean installs. |
| DS-005 | Execution spine | runtime-ready request | subprocess/runtime generation + output validation | `runner.py` + backend command/runtime owners | Execution should consume resolved and ready policy, not repair readiness ad hoc. |

## Architecture Direction

- Keep `server.py` boundary-only.
- Keep `runner.py` orchestration-focused.
- Keep `routing_policy.py` as the single routing/runtime-policy owner.
- Keep `runtime_paths.py` as the path-semantics owner.
- Replace startup-only runtime-install orchestration with one concrete runtime-installation/readiness owner used from both startup and request-time execution.
- Represent Kokoro explicit asset pins explicitly in settings instead of inferring them from normalized path values.

## Ownership Map

| File | Owns | Must Not Own |
| --- | --- | --- |
| `src/tts_mcp/server.py` | MCP tool definitions and boundary-level argument forwarding | startup/runtime install side effects, backend routing policy |
| `src/tts_mcp/app_runtime.py` | executable startup assembly | public tool semantics, backend execution details |
| `src/tts_mcp/routing_policy.py` | public language canonicalization, MLX request resolution, Kokoro request resolution, backend-specific language normalization | install side effects, subprocess execution |
| `src/tts_mcp/runtime_paths.py` | runtime root, script lookup, command-path normalization, backend file-path normalization | backend routing choices, install policy |
| `src/tts_mcp/runtime_installation.py` | startup runtime preparation and request-time runtime readiness/install orchestration | public MCP boundary semantics, backend routing decisions |
| `src/tts_mcp/config.py` | env parsing, normalized setting values, explicit override metadata | language/profile auto-switch policy, install side effects |
| `src/tts_mcp/backend_commands.py` | build subprocess commands from ready, resolved requests/settings | routing or install decisions |
| `src/tts_mcp/kokoro_runtime.py` | Kokoro synthesis from a ready, resolved Kokoro request | installer profile selection, path-precedence policy |

## Key Design Decisions

### D-001 Keep Startup Separate

- `app_runtime.py` remains the executable startup owner.
- It should call the runtime-installation owner, not a startup-only bootstrap module, before constructing the server.

### D-002 Keep Routing Separate From Installation

- `routing_policy.py` stays responsible for:
  - `canonicalize_public_language(...)`
  - `resolve_mlx_request(...)`
  - `resolve_kokoro_request(...)`
  - XTTS / Chatterbox language adaptation
- It must not perform install side effects.

### D-003 Introduce Explicit Kokoro Override Metadata

- Extend `TtsSettings` with explicit Kokoro metadata:
  - `kokoro_model_path_explicit`
  - `kokoro_voices_path_explicit`
  - `kokoro_vocab_config_path_explicit`
  - `kokoro_default_voice_explicit`
- Routing will stop guessing “explicit vs default” from path equality.
- Effective rule:
  - if Kokoro asset paths are not explicitly pinned, managed profile switching may occur
  - if Kokoro asset paths are explicitly pinned, those pins are authoritative

### D-004 Separate Managed Kokoro Profiles From Explicit Custom Assets

- `ResolvedKokoroRequest` should distinguish:
  - managed profile requests:
    - `managed_v1_0`
    - `managed_zh_v1_1`
  - explicit asset requests:
    - operator-pinned/custom assets
- The request object should carry enough information for readiness orchestration, for example:
  - effective language
  - effective voice
  - effective paths
  - `managed_profile` or `None`
  - whether runtime installation is allowed for that request

### D-005 Add One Runtime-Installation / Readiness Owner

- Add `src/tts_mcp/runtime_installation.py`.
- It will own two related but distinct flows:
  - `prepare_startup_runtime(settings)`:
    - existing startup install behavior
    - installs the default managed runtime/profile when applicable
  - `ensure_request_runtime_ready(settings, backend, resolved_request)`:
    - called from `runner.py` before generation
    - for Kokoro managed-profile requests, installs missing required profile assets on demand when auto-install is enabled
    - for explicit custom Kokoro assets, does not switch/install a managed profile; missing files remain a config/dependency error

### D-006 Keep Builders And Runtimes Small

- `backend_commands.py` consumes normalized settings and resolved request data only.
- `kokoro_runtime.py` consumes a ready `ResolvedKokoroRequest` only.
- `runner.py` owns orchestration:
  - select backend
  - resolve request
  - ensure runtime ready
  - execute

## Change Inventory

| Change ID | Change Type | Current Path | Target Path | Rationale |
| --- | --- | --- | --- | --- |
| C-001 | Add | N/A | `tts-mcp/src/tts_mcp/runtime_installation.py` | Create one owner for startup/runtime install orchestration and request-time readiness. |
| C-002 | Modify | `tts-mcp/src/tts_mcp/config.py` | same | Add explicit Kokoro override metadata; keep config parse/normalize-only. |
| C-003 | Modify | `tts-mcp/src/tts_mcp/routing_policy.py` | same | Distinguish managed Kokoro profiles from explicit pinned assets. |
| C-004 | Modify | `tts-mcp/src/tts_mcp/app_runtime.py` | same | Call the runtime-installation owner for startup preparation. |
| C-005 | Modify | `tts-mcp/src/tts_mcp/runner.py` | same | Ensure request-time runtime readiness before generation. |
| C-006 | Modify | `tts-mcp/src/tts_mcp/kokoro_runtime.py` | same | Consume a ready `ResolvedKokoroRequest` without install/profile fallback logic. |
| C-007 | Modify | `tts-mcp/src/tts_mcp/runtime_bootstrap.py` | remove or fold into `runtime_installation.py` | Eliminate the startup-only install owner now that readiness must be shared between startup and request-time flows. |
| C-008 | Modify | tests and docs | same | Cover clean-install per-call Chinese Kokoro behavior and explicit Kokoro path precedence. |

## Failure And Edge Cases

- If explicit MLX preset/model is configured, runtime routing must still honor it exactly.
- If Kokoro managed defaults are used and a first Chinese request arrives after startup, the runtime-installation owner must ensure zh assets exist before synthesis or fail with an intentional contract decision.
- If Kokoro asset paths are explicitly pinned, routing must not silently switch to managed zh assets.
- If explicit pinned Kokoro assets are missing, runtime should return a clear config/dependency failure instead of attempting a managed-profile install.
- Relative asset paths must resolve identically in tests, executable entrypoints, and MCP runtime use.
- The Apple Silicon Chinese end-to-end behavior must remain unchanged.

## Implementation Outline

1. Replace startup-only bootstrap ownership with `runtime_installation.py`.
2. Extend `TtsSettings` with explicit Kokoro pin metadata.
3. Update `routing_policy.resolve_kokoro_request(...)` to model managed profiles vs explicit pins explicitly.
4. Add request-time readiness/install orchestration for Kokoro managed-profile requests.
5. Update `runner.py` and `app_runtime.py` to call the new installation owner.
6. Remove or fold obsolete startup-only install code.
7. Add focused tests for:
   - clean install + first per-call Chinese Kokoro request
   - explicit Kokoro path precedence
8. Re-run validation and then redo Stage 8 review.
