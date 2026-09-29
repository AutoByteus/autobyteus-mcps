# API/E2E Coverage Investigation (video-audio-cli-skill)

- Guidelines: No project testing guideline (TESTING*.md) found; used video-audio-editing/README.md, pyproject.toml (pytest markers), implementation-handoff.md. Env: `uv sync --extra test`, `.venv`, ffmpeg/ffprobe 6.1.1 on host.
- Surfaces: CLI/API transport (launcher), MCP stdio adapter, launcher lifecycle/bootstrap, ffmpeg external integration, skill contract. No browser/desktop surface.
- Handoff checks: Legacy removal clean; persisted data Not Affected (no transition to validate).
- Existing coverage (Still Valid): unit (schema parity vs frozen baseline 32 tools, mapping, paths, envelopes, import isolation), integration (launcher black box, MCP stdio parity, skill contract), media (legacy-text real ffmpeg).
- Gaps -> Add Durable Coverage: per-family CLI happy paths and SKILL.md recipes (subtitles CJK, text/image overlay, concat + xfade, audio concat, extract audio/frame, replace audio, speed, crop aspect, remove-silence, fades, image+audio->video, convert/set-* wrappers, add-b-roll). Launcher-without-uv -> temporary probe only (uv fallback path /usr/local/bin/uv is hardcoded so a durable test would be host-dependent).
- Findings during validation (not regressions, verified against legacy commit d0fb10d): `mkv` is not an ffmpeg muxer name (use `matroska`); `change-aspect-ratio --resize-mode pad` fails on tests/sample.mp4 with ffmpeg 6.1.1 identically in legacy code. SKILL.md recipe `remove-silence` lacks flags (real flags `--media-path/--output-media-path`), minor doc note.
