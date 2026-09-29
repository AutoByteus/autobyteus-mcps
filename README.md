# AutoByteus MCPs

Collection of Model Context Protocol (MCP) tools maintained in one workspace.

## Projects

| Project | Description | Origin |
| --- | --- | --- |
| `alexa-mcp` | MCP server for bounded Alexa routine/music control via local adapter command. | AutoByteus (internal) |
| `tts-mcp` | MCP server with one `speak` tool that auto-selects MLX Audio (Apple Silicon) or llama.cpp TTS (Linux NVIDIA). | AutoByteus (internal) |
| `codex-cli-mcp` | MCP server exposing bounded non-interactive Codex CLI tools (`codex_health_check`, `codex_exec`). | AutoByteus (internal) |
| `browser-mcp` | Standalone browser MCP server using brui_core/Playwright, with stdio and streamable HTTP transports. | AutoByteus (internal) |
| `ssh-mcp` | MCP server exposing bounded SSH lifecycle tools (`ssh_health_check`, `ssh_open_session`, `ssh_session_exec`, `ssh_close_session`). | AutoByteus (internal) |
| `pptx-mcp` | MCP server for creating/editing PPTX decks from images. | AutoByteus (internal) |
| `yt_dlp_mcp` | MCP server that shells out to yt-dlp for downloading social videos with curated metadata filenames. | AutoByteus (internal) |
| `moss-ttsd-mcp` | MCP server for bilingual dialogue TTS using fnlp/MOSS-TTSD-v0.5. | https://huggingface.co/fnlp/MOSS-TTSD-v0.5 |
| `wss_mcp_toy` | Toy MCP server that speaks the protocol over secure WebSockets with echo/time tools. | AutoByteus (internal) |
| `streamable_http_mcp_toy` | Toy MCP server that exposes echo/time tools over streamable HTTP. | AutoByteus (internal) |
| `index-tts-mcp` | Planned MCP server wrapping IndexTeam/IndexTTS-2 for fast TTS + voice cloning. | https://huggingface.co/IndexTeam/IndexTTS-2 |

## Moved To The Skills Repository

`browser-automation` and `video-audio-editing` are CLI-first agent skills and now live in [autobyteus-skills](https://github.com/AutoByteus/autobyteus-skills), together with the [Argument-Isomorphic MCP-to-CLI Mapping](https://github.com/AutoByteus/autobyteus-skills/blob/main/docs/mcp-to-cli-mapping.md) guide. Their thin MCP adapters remain available there; MCP client configurations must point at the new launcher paths (`browser-automation/scripts/browser-mcp`, `video-audio-editing/scripts/video-audio-mcp`).

## Contributing

Each MCP project is maintained in its own folder. When adding a new project:

1. Copy the project into its own subdirectory at the repository root.
2. Document the original source in this README table.
3. Keep build artifacts, virtual environments, and editor state out of version control (see `.gitignore`).
4. Add and run tests for the new project when applicable.
