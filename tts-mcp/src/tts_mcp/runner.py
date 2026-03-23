from __future__ import annotations

from pathlib import Path
from typing import TypedDict

from . import backend_commands, backend_contracts, execution_support, kokoro_runtime
from .config import BackendName, ConfigError, TtsSettings, model_requires_instruct
from .platform import BackendSelectionError, select_backend
from .version_check import check_backend_runtime_version


class SpeakResult(TypedDict):
    ok: bool
    backend: BackendName | None
    platform: str
    machine: str
    command: list[str]
    output_path: str | None
    played: bool
    playback_command: list[str] | None
    warnings: list[str]
    stdout: str | None
    stderr: str | None
    exit_code: int | None
    error_type: str | None
    error_message: str | None


def run_speak(
    settings: TtsSettings,
    text: str,
    output_path: str | None = None,
    play: bool = True,
    voice: str | None = None,
    speed: float = 1.0,
    language_code: str | None = None,
    preferred_backend: BackendName | None = None,
    instruct: str | None = None,
) -> SpeakResult:
    normalized_text = text.strip()
    if not normalized_text:
        return _error_result(
            error_type="validation",
            error_message="text cannot be empty.",
        )
    if speed <= 0:
        return _error_result(
            error_type="validation",
            error_message="speed must be greater than zero.",
        )

    requested_instruct = backend_contracts.normalize_optional_text(instruct)

    try:
        selection = select_backend(settings=settings, preferred_backend=preferred_backend)
    except BackendSelectionError as exc:
        return _error_result(
            error_type=exc.error_type,
            error_message=str(exc),
        )

    try:
        resolved_output_info = execution_support.resolve_output_path(
            output_path, settings.output_dir
        )
    except ConfigError as exc:
        return _error_result(
            backend=selection.backend,
            platform_name=selection.host.system,
            machine=selection.host.machine,
            error_type="validation",
            error_message=str(exc),
        )
    resolved_output = resolved_output_info["path"]
    auto_generated_output = resolved_output_info["is_auto_generated"]

    if selection.backend == "mlx_audio":
        effective_instruct = requested_instruct or settings.mlx_default_instruct
        if model_requires_instruct(settings.mlx_model) and not effective_instruct:
            return _error_result(
                backend=selection.backend,
                platform_name=selection.host.system,
                machine=selection.host.machine,
                error_type="validation",
                error_message=(
                    "Configured MLX model requires instruct. Set MLX_TTS_DEFAULT_INSTRUCT "
                    "in MCP config or pass instruct in speak()."
                ),
            )
        try:
            command = backend_commands.build_mlx_command(
                settings=settings,
                text=normalized_text,
                output_path=resolved_output,
                play=play,
                voice=voice,
                speed=speed,
                language_code=language_code,
                instruct=effective_instruct,
            )
        except ConfigError as exc:
            return _error_result(
                backend=selection.backend,
                platform_name=selection.host.system,
                machine=selection.host.machine,
                error_type="config",
                error_message=str(exc),
            )
    elif selection.backend == "llama_cpp":
        if requested_instruct:
            return _error_result(
                backend=selection.backend,
                platform_name=selection.host.system,
                machine=selection.host.machine,
                error_type="validation",
                error_message="instruct is currently supported only for mlx_audio backend.",
            )
        try:
            command = backend_commands.build_llama_command(
                settings=settings,
                text=normalized_text,
                output_path=resolved_output,
            )
        except ConfigError as exc:
            return _error_result(
                backend=selection.backend,
                platform_name=selection.host.system,
                machine=selection.host.machine,
                error_type="config",
                error_message=str(exc),
            )
    elif selection.backend == "kokoro_onnx":
        if requested_instruct:
            return _error_result(
                backend=selection.backend,
                platform_name=selection.host.system,
                machine=selection.host.machine,
                error_type="validation",
                error_message="instruct is currently supported only for mlx_audio backend.",
            )
        command = ["kokoro_onnx.generate", str(resolved_output)]
    elif selection.backend == "xtts":
        if requested_instruct:
            return _error_result(
                backend=selection.backend,
                platform_name=selection.host.system,
                machine=selection.host.machine,
                error_type="validation",
                error_message="instruct is currently supported only for mlx_audio backend.",
            )
        try:
            command = backend_commands.build_xtts_command(
                settings=settings,
                text=normalized_text,
                output_path=resolved_output,
                voice=voice,
                speed=speed,
                language_code=language_code,
            )
        except ConfigError as exc:
            return _error_result(
                backend=selection.backend,
                platform_name=selection.host.system,
                machine=selection.host.machine,
                error_type="config",
                error_message=str(exc),
            )
    elif selection.backend == "chatterbox":
        if requested_instruct:
            return _error_result(
                backend=selection.backend,
                platform_name=selection.host.system,
                machine=selection.host.machine,
                error_type="validation",
                error_message="instruct is currently supported only for mlx_audio backend.",
            )
        try:
            command = backend_commands.build_chatterbox_command(
                settings=settings,
                text=normalized_text,
                output_path=resolved_output,
                voice=voice,
                language_code=language_code,
            )
        except ConfigError as exc:
            return _error_result(
                backend=selection.backend,
                platform_name=selection.host.system,
                machine=selection.host.machine,
                error_type="config",
                error_message=str(exc),
            )
    else:
        return _error_result(
            error_type="validation",
            error_message=f"Unsupported backend selected: {selection.backend}",
        )

    warnings: list[str] = []

    if settings.enforce_latest_runtime:
        version_status = check_backend_runtime_version(
            backend=selection.backend,
            command=selection.command,
            timeout_seconds=settings.version_check_timeout_seconds,
        )
        if version_status["status"] != "latest":
            return _error_result(
                backend=selection.backend,
                platform_name=selection.host.system,
                machine=selection.host.machine,
                error_type="dependency",
                error_message=version_status["message"],
            )

    before_signature = execution_support.output_signature(resolved_output)
    generation_env: dict[str, str] | None = None
    if selection.backend == "mlx_audio":
        generation_env = backend_contracts.resolve_mlx_subprocess_env(settings=settings)
    elif selection.backend == "xtts":
        generation_env = backend_contracts.resolve_xtts_subprocess_env(settings=settings)

    lock_fd = execution_support.acquire_global_generation_lock(
        timeout_seconds=settings.process_lock_timeout_seconds
    )
    if lock_fd is None:
        return _error_result(
            backend=selection.backend,
            platform_name=selection.host.system,
            machine=selection.host.machine,
            error_type="busy",
            error_message=(
                "Another speech generation is already running. "
                "Try again in a few seconds."
            ),
        )

    try:
        if selection.backend == "kokoro_onnx":
            generation = kokoro_runtime.run_kokoro_generation(
                settings=settings,
                text=normalized_text,
                output_path=resolved_output,
                voice=voice,
                speed=speed,
                language_code=language_code,
            )
        else:
            generation = execution_support.execute_command(
                command=command,
                timeout_seconds=settings.timeout_seconds,
                env_overrides=generation_env,
            )

        if generation["exit_code"] != 0:
            error_type, error_message = backend_contracts.classify_generation_failure(
                backend=selection.backend,
                generation=generation,
            )
            return _error_result(
                backend=selection.backend,
                platform_name=selection.host.system,
                machine=selection.host.machine,
                command=command,
                output_path=resolved_output,
                stdout=generation["stdout"],
                stderr=generation["stderr"],
                exit_code=generation["exit_code"],
                error_type=error_type,
                error_message=error_message,
            )

        played = False
        playback_command: list[str] | None = None

        after_signature = execution_support.output_signature(resolved_output)
        if after_signature is None or after_signature["size"] <= 44:
            return _error_result(
                backend=selection.backend,
                platform_name=selection.host.system,
                machine=selection.host.machine,
                command=command,
                output_path=resolved_output,
                stdout=generation["stdout"],
                stderr=generation["stderr"],
                exit_code=generation["exit_code"],
                error_type="execution",
                error_message=(
                    "Speech command completed but no valid WAV output was produced at "
                    f"{resolved_output}."
                ),
            )
        if before_signature is not None and before_signature == after_signature:
            return _error_result(
                backend=selection.backend,
                platform_name=selection.host.system,
                machine=selection.host.machine,
                command=command,
                output_path=resolved_output,
                stdout=generation["stdout"],
                stderr=generation["stderr"],
                exit_code=generation["exit_code"],
                error_type="execution",
                error_message=(
                    "Speech command completed, but output file was not updated. "
                    f"Expected a newly generated WAV at {resolved_output}."
                ),
            )

        if (
            play
            and selection.backend in {"llama_cpp", "kokoro_onnx", "xtts", "chatterbox"}
            and resolved_output.exists()
        ):
            playback_command = execution_support.build_linux_play_command(
                audio_path=resolved_output,
                linux_player=settings.linux_player,
            )
            if playback_command is None:
                warnings.append(
                    "Audio generation succeeded, but no audio player is available "
                    "(tried ffplay/afplay/aplay/paplay)."
                )
            else:
                playback = execution_support.execute_command(
                    command=playback_command, timeout_seconds=45
                )
                if execution_support.linux_playback_confirmed(
                    playback_command, playback
                ):
                    played = True
                else:
                    warnings.append(
                        "Audio generation succeeded, but playback command failed."
                    )

        if play and selection.backend == "mlx_audio":
            if backend_contracts.mlx_playback_confirmed(generation):
                played = True
            else:
                warnings.append(
                    "Audio generation succeeded, but MLX playback could not be confirmed "
                    "from command output. Check your default audio output device."
                )

        if auto_generated_output and settings.delete_auto_output:
            try:
                resolved_output.unlink(missing_ok=True)
            except OSError:
                warnings.append(
                    f"Generated audio cleanup failed for {resolved_output}."
                )

        return SpeakResult(
            ok=True,
            backend=selection.backend,
            platform=selection.host.system,
            machine=selection.host.machine,
            command=command,
            output_path=str(resolved_output),
            played=played,
            playback_command=playback_command,
            warnings=warnings,
            stdout=generation["stdout"],
            stderr=generation["stderr"],
            exit_code=generation["exit_code"],
            error_type=None,
            error_message=None,
        )
    finally:
        execution_support.release_global_generation_lock(lock_fd)


def _error_result(
    error_type: str,
    error_message: str,
    *,
    backend: BackendName | None = None,
    platform_name: str = "unknown",
    machine: str = "unknown",
    command: list[str] | None = None,
    output_path: Path | None = None,
    stdout: str | None = None,
    stderr: str | None = None,
    exit_code: int | None = None,
) -> SpeakResult:
    return SpeakResult(
        ok=False,
        backend=backend,
        platform=platform_name,
        machine=machine,
        command=command or [],
        output_path=str(output_path) if output_path else None,
        played=False,
        playback_command=None,
        warnings=[],
        stdout=stdout,
        stderr=stderr,
        exit_code=exit_code,
        error_type=error_type,
        error_message=error_message,
    )
