# API / E2E Testing

## Status

- Stage: `7`
- Result: `Pass`

## Acceptance Criteria Coverage

| Acceptance Criterion | Evidence | Result |
| --- | --- | --- |
| Executable startup keeps bootstrap side effects outside the MCP boundary constructor | `tests/test_app_runtime.py` focused suite | Pass |
| Public `speak` schema still exposes one canonical `language_code` field | `tests/test_server.py` focused suite | Pass |
| Apple Silicon MLX routing remains language-aware after config stops owning language-based preset selection | `tests/test_runner.py` focused suite | Pass |
| Kokoro startup preparation and first per-call Chinese request now share one readiness owner | `tests/test_runtime_installation.py`, `tests/test_runner.py` focused suite | Pass |
| Explicit Kokoro asset pins are authoritative and no longer auto-switch by path equality | `tests/test_config.py`, `tests/test_runtime_installation.py`, `tests/test_runner.py` focused suite | Pass |
| Backend file paths use one runtime-root-relative normalization policy | `tests/test_config.py` focused suite | Pass |
| Real Apple Silicon Chinese public MCP `speak` execution still succeeds after the architecture refactor | real pytest execution below | Pass |

## Executed Validation

### Focused Unit / Integration Validation

```bash
uv --directory tts-mcp run python -m pytest -q \
  tests/test_app_runtime.py \
  tests/test_config.py \
  tests/test_runtime_installation.py \
  tests/test_runner.py \
  tests/test_server.py \
  tests/test_platform.py
```

- Result: `Pass`
- Notes:
  - `runtime_bootstrap.py` was removed from the runtime spine and replaced by `runtime_installation.py`.
  - The focused suites now include explicit-asset Kokoro precedence and request-time managed-profile readiness coverage.

### Real Apple Silicon Chinese Public MCP Execution

```bash
TTS_MCP_RUN_REAL_MCP_SPEAK=1 \
MLX_TTS_COMMAND=/Users/normy/autobyteus_org/autobyteus_mcps/tts-mcp/.venv-mlx/bin/mlx_audio.tts.generate \
uv --directory tts-mcp run python -m pytest -q tests/test_real_mcp_speak_tool_chinese_qwen.py
```

- Result: `Pass`
- Notes:
  - Host: `Darwin arm64`
  - This exercised the public MCP `speak` boundary after the Kokoro runtime-installation and explicit-precedence refactor, not just the internal runner path.
  - The Chinese Apple Silicon request still completed successfully through the MLX Qwen route.
  - Real Linux / Intel-mac Kokoro execution was not rerun on this Darwin arm64 host.

### Local-Fix Real Apple Silicon Public MCP Regression Pair

```bash
TTS_MCP_RUN_REAL_MCP_SPEAK=1 \
MLX_TTS_COMMAND=/Users/normy/autobyteus_org/autobyteus_mcps/tts-mcp/.venv-mlx/bin/mlx_audio.tts.generate \
uv --directory tts-mcp run python -m pytest -q \
  tests/test_real_mcp_speak_tool.py \
  tests/test_real_mcp_speak_tool_chinese_qwen.py
```

- Result: `Pass`
- Notes:
  - The failing English real MCP test was a test-setup issue, not a runtime regression.
  - The fix was to resolve and inject `MLX_TTS_COMMAND` in `tests/test_real_mcp_speak_tool.py`, matching the already-working Chinese public MCP test.
