# Future-State Runtime Call Stacks: Image/Audio CLI generation_config JSON support

## Design Basis

- Scope Classification: `Small`
- Call Stack Version: `v2`
- Requirements: `tickets/in-progress/image-audio-cli-generation-config-json/requirements.md` (`Refined`)
- Source Artifact: `tickets/in-progress/image-audio-cli-generation-config-json/implementation.md` solution sketch v2
- Referenced Sections: Re-Entry Design Update v2

## Use Case Index

| use_case_id | Spine ID(s) | Spine Scope | Governing Owner | Source Type | Requirement ID(s) | Use Case Name | Coverage Target |
| --- | --- | --- | --- | --- | --- | --- | --- |
| UC-001 | DS-001, DS-002 | Primary End-to-End + Bounded Local | `image_audio_mcp.cli` | Requirement | REQ-001 | Inline nested JSON generation config | Primary/Error |
| UC-002 | DS-001, DS-002 | Primary End-to-End + Bounded Local | `image_audio_mcp.cli` | Requirement | REQ-002 | File-based generation config | Primary/Error |
| UC-003 | DS-002 | Bounded Local | `_load_generation_config` | Requirement | REQ-003 | Invalid/conflicting full-object config fails clearly | Error |
| UC-004 | DS-003 | Primary Documentation | argparse help + README | Requirement | REQ-004 | Help/docs discovery | Primary |
| UC-005 | DS-004 | Error Boundary | argparse + `JsonArgumentParser` | Requirement | REQ-005 | Removed split config flags fail as unrecognized | Error |

## Transition Notes

- Legacy split config flags are removed, not retained as compatibility aliases.
- No provider/API-key runtime path changes are modeled.

## Use Case: UC-001 Inline nested JSON generation config

### Primary Runtime Call Stack

```text
[ENTRY] src/image_audio_mcp/cli.py:main(argv)
├── src/image_audio_mcp/cli.py:run(argv)
│   ├── src/image_audio_mcp/cli.py:build_parser()
│   ├── argparse.ArgumentParser:parse_args(argv)
│   ├── src/image_audio_mcp/cli.py:_dispatch(args)
│   │   ├── src/image_audio_mcp/cli.py:_load_generation_config(args)
│   │   │   ├── src/image_audio_mcp/cli.py:_parse_generation_config_json(args.generation_config, "--generation-config")
│   │   │   └── src/image_audio_mcp/cli.py:_merge_config_object(config, parsed_json, "--generation-config") [STATE]
│   │   └── src/image_audio_mcp/services.py:generate_speech(..., generation_config=config) [ASYNC]
│   └── src/image_audio_mcp/cli.py:_emit_success(command, result)
```

### Error Paths

```text
[ERROR] malformed or non-object JSON
_parse_generation_config_json(...)
└── raises CliUsageError -> run(...) -> _emit_failure(command, "UsageError", message)
```

## Use Case: UC-002 File-based generation config

### Primary Runtime Call Stack

```text
[ENTRY] src/image_audio_mcp/cli.py:run(argv)
├── argparse.ArgumentParser:parse_args(argv)
├── src/image_audio_mcp/cli.py:_dispatch(args)
│   ├── src/image_audio_mcp/cli.py:_load_generation_config(args)
│   │   ├── src/image_audio_mcp/cli.py:_load_generation_config_file(args.generation_config_file) [IO]
│   │   ├── src/image_audio_mcp/cli.py:_parse_generation_config_json(file_text, "--generation-config-file")
│   │   └── src/image_audio_mcp/cli.py:_merge_config_object(config, file_config, "--generation-config-file") [STATE]
│   └── src/image_audio_mcp/services.py:generate_image(..., generation_config=config) [ASYNC]
└── src/image_audio_mcp/cli.py:_emit_success(command, result)
```

### Error Paths

```text
[ERROR] file missing / unreadable / malformed / non-object
_load_generation_config_file(...)
└── raises CliUsageError -> JSON failure envelope
```

## Use Case: UC-003 Conflicting full-object config fails clearly

```text
[ENTRY] src/image_audio_mcp/cli.py:run(argv)
├── src/image_audio_mcp/cli.py:_load_generation_config(args)
│   ├── _merge_config_object(file_config)
│   ├── _merge_config_object(inline_config)
│   └── detects duplicate key or nested conflict [ERROR]
└── src/image_audio_mcp/cli.py:_emit_failure(command, "UsageError", message)
```

## Use Case: UC-004 Help/docs discovery

```text
[ENTRY] user/agent:readsHelpOrReadme(...)
├── src/image_audio_mcp/cli.py:build_parser()
│   └── src/image_audio_mcp/cli.py:_add_generation_config_options(parser)
│       ├── exposes --generation-config
│       └── exposes --generation-config-file
├── autobyteus-image-audio/README.md:Command-line usage
└── user/agent:formsCommandWithNativeGenerationConfig(...)
```

## Use Case: UC-005 Removed split config flags fail as unrecognized

```text
[ENTRY] src/image_audio_mcp/cli.py:run(argv includes --config or --speaker or --voice)
├── argparse.ArgumentParser:parse_args(argv)
│   └── src/image_audio_mcp/cli.py:JsonArgumentParser.error("unrecognized arguments: ...") [ERROR]
└── src/image_audio_mcp/cli.py:_emit_failure(command, "UsageError", message)
```
