Status: Stage 7 Passed

# Implementation Progress

## Goal

Implement the Kokoro design-impact re-entry so `tts-mcp` cleanly supports:

- a coherent Kokoro `startup install -> first per-call Chinese request` runtime spine
- authoritative explicit Kokoro asset pins
- the already-accepted Apple Silicon MLX Qwen behavior without regression

Current local-fix subgoal:

- repair the failing real English public MCP test so it resolves the MLX command correctly on this Mac, then rerun the English and Chinese real Mac tests

## Planned Change Set

- Add one runtime-installation/readiness owner for:
  - startup runtime preparation
  - request-time Kokoro managed-profile readiness/install
- Extend `TtsSettings` with explicit Kokoro override metadata:
  - model path explicitness
  - voices path explicitness
  - vocab path explicitness
  - default voice explicitness
- Update `routing_policy.py` so Kokoro request resolution distinguishes:
  - managed profile switching
  - explicit custom/pinned assets
- Update `runner.py` so request-time runtime readiness runs before Kokoro generation.
- Simplify `kokoro_runtime.py` so it consumes ready resolved requests only.
- Remove or fold obsolete startup-only runtime-install code once the new installation owner exists.
- Add focused tests for:
  - clean install with later per-call Chinese Kokoro request
  - explicit Kokoro path-precedence behavior
  - request-time Kokoro runtime readiness
- Re-run the prior focused architecture-refactor suite plus the new Kokoro-specific coverage.

## Progress Checklist

| Item | Status | Notes |
| --- | --- | --- |
| Implementation tracker refreshed for Kokoro re-entry | Complete | Stage 6 reopened after the independent Stage 8 design-impact failure. |
| Runtime-installation/readiness owner | Complete | Added `src/tts_mcp/runtime_installation.py` and removed the old startup-only `runtime_bootstrap.py` owner. |
| Explicit Kokoro pin metadata | Complete | `TtsSettings` now records explicit Kokoro path/voice overrides directly. |
| Kokoro routing contract update | Complete | `routing_policy.py` now distinguishes managed profiles from explicit asset pins and request-time install authority. |
| Focused Kokoro tests | Complete | Added `tests/test_runtime_installation.py` and expanded `tests/test_runner.py` / `tests/test_config.py`. |
| Stage 7 validation rerun | Complete | Focused suites, non-regression suites, and the real Apple Silicon public MCP test all passed. |
| Local English real MCP test fix | Complete | `test_real_mcp_speak_tool.py` now resolves and injects `MLX_TTS_COMMAND` the same way as the working Chinese public MCP test. |

## Validation Plan

- Focused suites:
  - `tests/test_config.py`
  - `tests/test_runtime_installation.py`
  - `tests/test_runner.py`
  - `tests/test_app_runtime.py`
- Non-regression focused suites:
  - `tests/test_server.py`
  - `tests/test_platform.py`
- Real executable checks where feasible on this host:
  - `tests/test_real_mcp_speak_tool_chinese_qwen.py`
- Additional Kokoro executable evidence:
  - existing Linux real Kokoro tests reviewed and updated if the runtime contract changes

## Validation Results

- Focused Stage 6 suites passed:
  - `uv --directory tts-mcp run python -m pytest -q tests/test_app_runtime.py tests/test_config.py tests/test_runtime_installation.py tests/test_runner.py`
- Non-regression focused suites passed:
  - `uv --directory tts-mcp run python -m pytest -q tests/test_server.py tests/test_platform.py`
- Real Apple Silicon public MCP Chinese test passed:
  - `TTS_MCP_RUN_REAL_MCP_SPEAK=1 MLX_TTS_COMMAND=/Users/normy/autobyteus_org/autobyteus_mcps/tts-mcp/.venv-mlx/bin/mlx_audio.tts.generate uv --directory tts-mcp run python -m pytest -q tests/test_real_mcp_speak_tool_chinese_qwen.py`
- Local-fix pre-patch reproduction:
  - `tests/test_real_mcp_speak_tool.py` failed because it built settings without `MLX_TTS_COMMAND`, which produced `Required command 'mlx_audio.tts.generate' is not available or executable.` on this host.
- Local-fix post-patch validation passed:
  - `TTS_MCP_RUN_REAL_MCP_SPEAK=1 MLX_TTS_COMMAND=/Users/normy/autobyteus_org/autobyteus_mcps/tts-mcp/.venv-mlx/bin/mlx_audio.tts.generate uv --directory tts-mcp run python -m pytest -q tests/test_real_mcp_speak_tool.py tests/test_real_mcp_speak_tool_chinese_qwen.py`
