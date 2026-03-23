# Code Review

## Review Meta

- Ticket: `tts-mcp-xtts-chatterbox-backends`
- Review Round: `4`
- Trigger Stage: `8`
- Workflow state source: `tickets/done/tts-mcp-xtts-chatterbox-backends/workflow-state.md`
- Earlier design artifact(s) reviewed as context:
  - `tickets/done/tts-mcp-xtts-chatterbox-backends/proposed-design.md`
  - `tickets/done/tts-mcp-xtts-chatterbox-backends/implementation-plan.md`
- Runtime call stack artifact:
  - `tickets/done/tts-mcp-xtts-chatterbox-backends/future-state-runtime-call-stack.md`

## Scope

- Files reviewed (source + packaging + tests):
  - `tts-mcp/src/tts_mcp/config.py`
  - `tts-mcp/src/tts_mcp/platform.py`
  - `tts-mcp/src/tts_mcp/runner.py`
  - `tts-mcp/src/tts_mcp/backend_contracts.py`
  - `tts-mcp/src/tts_mcp/backend_commands.py`
  - `tts-mcp/src/tts_mcp/kokoro_runtime.py`
  - `tts-mcp/src/tts_mcp/execution_support.py`
  - `tts-mcp/src/tts_mcp/runtime_bootstrap.py`
  - `tts-mcp/src/tts_mcp/runtime_paths.py`
  - `tts-mcp/src/tts_mcp/runtime_assets/`
  - `tts-mcp/src/tts_mcp/server.py`
  - `tts-mcp/src/tts_mcp/version_check.py`
  - `tts-mcp/scripts/`
  - `tts-mcp/pyproject.toml`
  - `tts-mcp/tests/test_server.py`
  - `tts-mcp/tests/test_config.py`
  - `tts-mcp/tests/test_platform.py`
  - `tts-mcp/tests/test_runner.py`
  - `tts-mcp/tests/test_runtime_bootstrap.py`
  - `tts-mcp/tests/test_runtime_paths.py`
  - `tts-mcp/tests/test_version_check.py`
  - `tts-mcp/tests/test_real_mlx_smoke.py`
  - `tts-mcp/tests/test_real_kokoro_smoke.py`
  - `tts-mcp/tests/test_real_xtts_smoke.py`
  - `tts-mcp/tests/test_real_chatterbox_smoke.py`
- Additional validation performed during this review:
  - `uv --directory tts-mcp run python -m py_compile scripts/xtts_generate.py scripts/chatterbox_generate.py src/tts_mcp/config.py src/tts_mcp/backend_commands.py src/tts_mcp/runtime_bootstrap.py src/tts_mcp/runtime_paths.py src/tts_mcp/runtime_assets/xtts_generate.py src/tts_mcp/runtime_assets/chatterbox_generate.py`
  - `bash -n` across the root installer shims and packaged runtime-asset installer scripts
  - `uv --directory tts-mcp run python -m pytest -q tests/test_server.py tests/test_config.py tests/test_runner.py tests/test_runtime_bootstrap.py tests/test_platform.py tests/test_version_check.py tests/test_runtime_paths.py`
  - `uv --directory tts-mcp run python -m pytest -q tests/test_real_mlx_smoke.py tests/test_real_kokoro_smoke.py tests/test_real_xtts_smoke.py tests/test_real_chatterbox_smoke.py`
  - `uv --directory tts-mcp build --wheel`
  - `unzip -l tts-mcp/dist/tts_mcp-0.1.0-py3-none-any.whl`
  - Fresh wheel-install smoke in a temporary Python 3.11 virtualenv, verifying that packaged `runtime_assets/*` resolve from `site-packages`, the Python wrappers exist, and the installer scripts remain executable

## Source File Size And Structure Audit

| Source File | Effective Non-Empty Line Count | `>500` Hard-Limit Check | `>220` Changed-Line Delta Gate | Scope-Appropriate SoC Check | File Placement Check | Required Action |
| --- | --- | --- | --- | --- | --- | --- |
| `tts-mcp/src/tts_mcp/config.py` | `428` | Pass | Pass (`93 + 4`) | Pass | Pass | Keep |
| `tts-mcp/src/tts_mcp/platform.py` | `132` | Pass | Pass (`20 + 2`) | Pass | Pass | Keep |
| `tts-mcp/src/tts_mcp/runner.py` | `378` | Pass | Pass (`88 + 644`) | Pass | Pass | Keep |
| `tts-mcp/src/tts_mcp/backend_contracts.py` | `166` | Pass | Pass (`new file, 201 raw lines`) | Pass | Pass | Keep |
| `tts-mcp/src/tts_mcp/backend_commands.py` | `159` | Pass | Pass (`new file, 176 raw lines`) | Pass | Pass | Keep |
| `tts-mcp/src/tts_mcp/kokoro_runtime.py` | `175` | Pass | Pass (`new file, 201 raw lines`) | Pass | Pass | Keep |
| `tts-mcp/src/tts_mcp/execution_support.py` | `167` | Pass | Pass (`new file, 204 raw lines`) | Pass | Pass | Keep |
| `tts-mcp/src/tts_mcp/runtime_bootstrap.py` | `202` | Pass | Pass (`33 + 5`) | Pass | Pass | Keep |
| `tts-mcp/src/tts_mcp/runtime_paths.py` | `31` | Pass | Pass (`new file, 43 raw lines`) | Pass | Pass | Keep |
| `tts-mcp/src/tts_mcp/runtime_assets/install_kokoro_onnx_linux.sh` | `259` | Pass | Pass (`new file, 288 raw lines`) | Pass | Pass | Keep |
| `tts-mcp/src/tts_mcp/runtime_assets/install_kokoro_onnx_macos.sh` | `260` | Pass | Pass (`new file, 292 raw lines`) | Pass | Pass | Keep |
| `tts-mcp/src/tts_mcp/version_check.py` | `379` | Pass | Pass (`137 + 5`) | Pass | Pass | Keep |
| `tts-mcp/src/tts_mcp/server.py` | `63` | Pass | Pass (`2 + 1`) | Pass | Pass | Keep |

Assessment notes:
- `runner.py` remains comfortably below the `<=500` hard limit, and its large raw churn is still an extraction-heavy reduction rather than new accretive logic.
- The two packaged Kokoro installer assets exceed the `>220` delta threshold only because the existing installer behavior was rehomed into packaged owner files; the root `scripts/` copies are now thin shims, so this did not reintroduce duplicated active logic.
- No changed source file exceeds the `<=500` effective non-empty-line hard limit.

## Structural Integrity Checks

| Check | Result | Evidence | Decision |
| --- | --- | --- | --- |
| Data-flow spine inventory clarity and preservation | Pass | The main execution line remains `server -> runner -> backend owner -> execution support`, with package-boundary helpers isolated in `runtime_paths.py` and `runtime_bootstrap.py`. | Keep |
| Ownership boundary preservation and clarity | Pass | `runner.py` still owns orchestration only, backend contract/command policy stays in the split owner files, and packaged runtime assets now own runtime-install/wrapper behavior. | Keep |
| Support structure clarity | Pass | `runtime_paths.py` cleanly centralizes checkout-vs-packaged resolution instead of scattering path probes across multiple modules. | Keep |
| Existing capability/subsystem reuse check | Pass | The package-boundary fix reused the current package and install surfaces rather than introducing a second runtime-management subsystem. | Keep |
| Reusable owned structures check | Pass | Runtime-path resolution and packaged-asset lookup are centralized and reused by command construction plus runtime bootstrap. | Keep |
| Shared-structure/data-model tightness check | Pass | No new kitchen-sink config or cross-cutting mutable registry was introduced. | Keep |
| Repeated coordination ownership check | Pass | The repeated repo-root script resolution defect is removed and replaced by one shared resolver. | Keep |
| Empty indirection check | Pass | The new shims are intentionally thin checkout entrypoints, while the packaged assets own the real behavior. | Keep |
| Scope-appropriate separation of concerns and file responsibility clarity | Pass | Packaged runtime assets, path resolution, and command preflight each live in the correct owner instead of being mixed into `runner.py`. | Keep |
| Ownership-driven dependency check | Pass | Dependency direction remains one-way from orchestration/config into support owners and packaged runtime assets. | Keep |
| File placement check | Pass | `runtime_assets/` is an appropriate package-local home for the wrapper/install assets that must ship inside the wheel. | Keep |
| Flat-vs-over-split layout judgment | Pass | The current split is proportionate: one small resolver module plus packaged assets, without over-fragmenting the public MCP surface. | Keep |
| Interface/API/query/command/service-method boundary clarity | Pass | The public MCP `speak` API remains unchanged and the new work stays behind configuration/runtime boundaries. | Keep |
| Naming quality and naming-to-responsibility alignment | Pass | `runtime_paths`, `runtime_assets`, `backend_commands`, and `execution_support` align with the responsibilities they now own. | Keep |
| No unjustified duplication of code / repeated structures | Pass | Active installer/wrapper logic now exists only in `runtime_assets/`; the repo-root `scripts/` are intentionally thin delegators. | Keep |
| Patch-on-patch complexity control | Pass | The local fix reduced risk by replacing repeated path assumptions with one explicit package-boundary mechanism. | Keep |
| Dead/obsolete code cleanup completeness | Pass | The old repo-root hardcoded command/bootstrap assumptions were removed rather than kept as a parallel legacy path. | Keep |
| Test quality | Pass | Tests now cover XTTS speaker preflight, packaged runtime-path resolution, wheel contents, and unchanged orchestration behavior. | Keep |
| Test maintainability | Pass | The new tests target the specific owner seams that caused the earlier failure instead of relying on broad incidental behavior. | Keep |
| Validation evidence sufficiency | Pass | Review-time validation now includes wheel contents and a real installed-wheel smoke, which closes the earlier package-boundary blind spot. | Keep |
| No backward-compatibility mechanisms | Pass | No temporary dual path or legacy fallback layer was added. | Keep |
| No legacy code retention | Pass | The pre-fix repo-root-only package assumption is gone from the execution path. | Keep |

## Delta-Gate Assessment Note

- `runner.py` retains a large raw diff because the prior refactor removed hundreds of lines from the monolith into explicit owners. The resulting file remains `378` effective non-empty lines and structurally cleaner than the pre-split shape.
- `runtime_assets/install_kokoro_onnx_linux.sh` and `runtime_assets/install_kokoro_onnx_macos.sh` cross the `>220` delta threshold because the installer logic was rehomed into packaged asset owners so wheel installs keep the same behavior. This is packaging relocation, not new mixed-concern growth.

## Findings

- No new findings.

## Residual Risk Notes

- XTTS quality still depends on the configured reference speaker WAV; this review validates execution, packaging, and architecture rather than voice quality.
- The review now includes an installed-wheel path smoke, but not a full wheel-installed live synthesis run for the heavyweight backends because that would require runtime downloads/installers inside the temporary environment.

## Gate Decision

- Decision: `Pass`
- Classification: `N/A`
- Required re-entry path: `N/A`
- Implementation can proceed directly to `Stage 9`: `Yes`
- Mandatory pass checks:
  - All changed source files have effective non-empty line count `<=500`: `Yes`
  - Required `>220` changed-line delta-gate assessments are recorded for all applicable changed source files: `Yes`
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
  - The earlier Stage 8 design-impact finding remains resolved by the split-owner runner architecture.
  - The later package-boundary/local-fix finding is now resolved by packaged runtime assets, centralized runtime-path resolution, XTTS preflight validation, wheel contents validation, and installed-wheel smoke evidence.
