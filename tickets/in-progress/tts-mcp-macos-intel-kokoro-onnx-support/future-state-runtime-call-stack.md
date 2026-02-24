# Future-State Runtime Call Stacks (Debug-Trace Style)

## Design Basis

- Scope Classification: `Medium`
- Call Stack Version: `v1`
- Requirements: `tickets/in-progress/tts-mcp-macos-intel-kokoro-onnx-support/requirements.md` (`Design-ready`)
- Source Artifact: `tickets/in-progress/tts-mcp-macos-intel-kokoro-onnx-support/proposed-design.md`
- Source Design Version: `v1`

## Use Case Index (Stable IDs)

| use_case_id | Requirement | Use Case Name | Coverage Target (Primary/Fallback/Error) |
| --- | --- | --- | --- |
| UC-001 | R-001 | Auto backend route for Intel macOS | Yes/N/A/Yes |
| UC-002 | R-002 | Explicit Kokoro backend on Intel macOS | Yes/N/A/Yes |
| UC-003 | R-003 | Bootstrap auto-installs Kokoro on Intel macOS | Yes/Yes/Yes |
| UC-004 | R-004 | Manual installer dispatch to macOS Intel Kokoro script | Yes/Yes/Yes |
| UC-005 | R-005 | Playback command fallback with macOS player | Yes/Yes/Yes |

## Transition Notes

- Replace Linux-only Kokoro platform assumptions with explicit Intel macOS branch.

## Use Case: UC-001 [Auto backend route for Intel macOS]

### Primary Runtime Call Stack

```text
[ENTRY] src/tts_mcp/runner.py:run_speak(..., preferred_backend=None)
└── src/tts_mcp/platform.py:select_backend(settings, host=detect_host())
    ├── src/tts_mcp/platform.py:detect_host()
    ├── Decision: requested == "auto" [STATE]
    ├── Decision: host == Darwin/x86_64 -> backend = "kokoro_onnx" [STATE]
    └── return BackendSelection(backend="kokoro_onnx", command="kokoro_onnx")
```

### Branching / Error Paths

```text
[ERROR] unsupported host for auto
src/tts_mcp/platform.py:select_backend(...)
└── raise BackendSelectionError("unsupported_platform", ...)
```

### Coverage Status

- Primary Path: `Covered`
- Fallback Path: `N/A`
- Error Path: `Covered`

## Use Case: UC-002 [Explicit Kokoro backend on Intel macOS]

### Primary Runtime Call Stack

```text
[ENTRY] src/tts_mcp/runner.py:run_speak(..., preferred_backend="kokoro_onnx")
└── src/tts_mcp/platform.py:select_backend(...)
    ├── Decision: requested == "kokoro_onnx" [STATE]
    ├── Decision: host.is_linux OR host == Darwin/x86_64 [STATE]
    └── return BackendSelection(backend="kokoro_onnx", command="kokoro_onnx")
```

### Branching / Error Paths

```text
[ERROR] explicit kokoro on unsupported host (ex: Darwin/arm64 when policy disallows)
src/tts_mcp/platform.py:select_backend(...)
└── raise BackendSelectionError("unsupported_platform", ...)
```

### Coverage Status

- Primary Path: `Covered`
- Fallback Path: `N/A`
- Error Path: `Covered`

## Use Case: UC-003 [Bootstrap auto-installs Kokoro on Intel macOS]

### Primary Runtime Call Stack

```text
[ENTRY] src/tts_mcp/server.py:create_server(...)
└── src/tts_mcp/runtime_bootstrap.py:bootstrap_runtime(settings)
    ├── src/tts_mcp/platform.py:detect_host()
    ├── src/tts_mcp/runtime_bootstrap.py:_linux_runtime_target(settings)
    ├── Decision: runtime target == "kokoro_onnx" [STATE]
    ├── Decision: host is Linux OR Darwin/x86_64 [STATE]
    ├── src/tts_mcp/runtime_bootstrap.py:_python_module_available("kokoro_onnx")
    ├── src/tts_mcp/runtime_bootstrap.py:_kokoro_assets_available(...) [IO]
    ├── src/tts_mcp/runtime_bootstrap.py:_run_install_script_with_env(..., KOKORO_TTS_PROFILE)
    │   └── subprocess.run(["scripts/install_kokoro_onnx_macos.sh"], env=...) [IO]
    └── return notes += "Installed Kokoro ONNX runtime automatically."
```

### Branching / Fallback Paths

```text
[FALLBACK] runtime already installed and assets present
src/tts_mcp/runtime_bootstrap.py:bootstrap_runtime(...)
└── skip install script, return []
```

```text
[ERROR] installer missing or install command fails
src/tts_mcp/runtime_bootstrap.py:_run_install_script(...)
└── raise RuntimeError("Runtime auto-install failed ...")
```

### Coverage Status

- Primary Path: `Covered`
- Fallback Path: `Covered`
- Error Path: `Covered`

## Use Case: UC-004 [Manual installer dispatch on Intel macOS]

### Primary Runtime Call Stack

```text
[ENTRY] scripts/install_tts_runtime.sh:main
├── uname -s/-m [IO]
├── Decision: Darwin + x86_64 [STATE]
├── Decision: selected runtime == kokoro_onnx [STATE]
└── scripts/install_kokoro_onnx_macos.sh:main [IO]
    ├── resolve_python_bin()
    ├── pip install --upgrade kokoro-onnx [IO]
    ├── download_assets(... model, voices, optional zh config) [IO]
    └── print configured env hints
```

### Branching / Fallback Paths

```text
[FALLBACK] profile auto-selection
scripts/install_kokoro_onnx_macos.sh:main
└── --lang zh -> profile zh_v1_1; else v1_0
```

```text
[ERROR] unsupported runtime requested on Intel macOS
scripts/install_tts_runtime.sh:main
└── exit 1 with explicit unsupported runtime message
```

### Coverage Status

- Primary Path: `Covered`
- Fallback Path: `Covered`
- Error Path: `Covered`

## Use Case: UC-005 [Playback command fallback on macOS]

### Primary Runtime Call Stack

```text
[ENTRY] src/tts_mcp/runner.py:run_speak(..., play=True)
└── src/tts_mcp/runner.py:_build_linux_play_command(audio_path, linux_player="auto")
    ├── candidate ffplay
    ├── candidate afplay [FALLBACK]
    ├── candidate aplay/paplay (for Linux)
    └── return first available player command
[ASYNC] src/tts_mcp/runner.py:_execute(playback_command)
└── src/tts_mcp/runner.py:_linux_playback_confirmed(...)
```

### Branching / Error Paths

```text
[FALLBACK] no player found
src/tts_mcp/runner.py:_build_linux_play_command(...)
└── return None -> warning appended, speak result ok=false when play=true
```

```text
[ERROR] player command exits non-zero
src/tts_mcp/runner.py:_execute(...)
└── playback not confirmed
```

### Coverage Status

- Primary Path: `Covered`
- Fallback Path: `Covered`
- Error Path: `Covered`
