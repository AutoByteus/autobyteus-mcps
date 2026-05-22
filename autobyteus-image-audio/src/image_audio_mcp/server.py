from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Annotated, Any, Dict, List, Optional

from mcp.server.fastmcp import Context, FastMCP
from pydantic import Field

from image_audio_mcp import services

DEFAULT_SERVER_NAME = "autobyteus-image-audio"
DEFAULT_INSTRUCTIONS = (
    "Expose Autobyteus image, audio, and video generation tools. "
    "Outputs are written to local files under the configured workspace, Downloads, or temp directories."
)


@dataclass(slots=True)
class ServerConfig:
    name: str = DEFAULT_SERVER_NAME
    instructions: str = DEFAULT_INSTRUCTIONS

    @classmethod
    def from_env(cls) -> "ServerConfig":
        return cls(
            name=os.environ.get("IMAGE_AUDIO_MCP_NAME", DEFAULT_SERVER_NAME),
            instructions=os.environ.get("IMAGE_AUDIO_MCP_INSTRUCTIONS", DEFAULT_INSTRUCTIONS),
        )


def create_server(config: ServerConfig | None = None) -> FastMCP:
    cfg = config or ServerConfig.from_env()
    server = FastMCP(name=cfg.name, instructions=cfg.instructions)

    @server.tool(
        name="health_check",
        title="Health check",
        description="Return basic server status and default model identifiers.",
        structured_output=True,
    )
    async def health_check(*, context: Context) -> dict[str, str]:
        return await services.health_check()

    @server.tool(
        name="list_audio_models",
        title="List audio models",
        description="List available audio models and their generation_config schemas.",
        structured_output=True,
    )
    async def list_audio_models(*, context: Context) -> dict[str, Any]:
        return await services.list_audio_models()

    @server.tool(
        name="list_image_models",
        title="List image models",
        description="List available image models and their generation_config schemas.",
        structured_output=True,
    )
    async def list_image_models(*, context: Context) -> dict[str, Any]:
        return await services.list_image_models()

    @server.tool(
        name="list_video_models",
        title="List video models",
        description="List available video models and their generation_config schemas.",
        structured_output=True,
    )
    async def list_video_models(*, context: Context) -> dict[str, Any]:
        return await services.list_video_models()

    @server.tool(
        name="generate_image",
        title="Generate image",
        description=(
            "Generate an image from a text prompt, optionally using reference images. "
            "Uses the configured default image generation model. "
            "The output image is written to output_file_path."
        ),
        structured_output=True,
    )
    async def generate_image(
        prompt: str,
        output_file_path: str,
        input_images: Optional[List[str]] = None,
        generation_config: Optional[Dict[str, Any]] = None,
        *,
        context: Context,
    ) -> dict[str, Any]:
        return await services.generate_image(
            prompt=prompt,
            output_file_path=output_file_path,
            input_images=input_images,
            generation_config=generation_config,
        )

    @server.tool(
        name="generate_video",
        title="Generate video",
        description=(
            "Generate a video from a text prompt, optionally using image, audio, or video references. "
            "Uses the configured default video generation model. "
            "The output video is written to output_file_path."
        ),
        structured_output=True,
    )
    async def generate_video(
        prompt: Annotated[
            str,
            Field(description="A detailed textual description of the video to generate."),
        ],
        output_file_path: Annotated[
            str,
            Field(description="Absolute path or workspace-relative path where the generated video should be written."),
        ],
        input_images: Annotated[
            Optional[List[str]],
            Field(description="Optional image references as URLs, data URIs, or safe local paths."),
        ] = None,
        input_audios: Annotated[
            Optional[List[str]],
            Field(description="Optional audio references as URLs, data URIs, or safe local paths."),
        ] = None,
        input_videos: Annotated[
            Optional[List[str]],
            Field(description="Optional video references as URLs, data URIs, or safe local paths."),
        ] = None,
        generation_config: Annotated[
            Optional[Dict[str, Any]],
            Field(
                description=(
                    "Optional model-specific video generation settings. Please call `list_video_models` first "
                    "to inspect the live `generation_config` schema for each available model."
                )
            ),
        ] = None,
        *,
        context: Context,
    ) -> dict[str, Any]:
        return await services.generate_video(
            prompt=prompt,
            output_file_path=output_file_path,
            input_images=input_images,
            input_audios=input_audios,
            input_videos=input_videos,
            generation_config=generation_config,
        )

    @server.tool(
        name="find_target_coordinates",
        title="Find target coordinates",
        description=(
            "Default coordinate finder for UI automation. Uses edit_image to place a temporary "
            "marker on the target, detects marker center, and maps back to original coordinates."
        ),
        structured_output=True,
    )
    async def find_target_coordinates(
        image: str,
        target: str,
        marked_image_output_path: Optional[str] = None,
        grounding_model_identifier: Optional[str] = None,
        *,
        context: Context,
    ) -> dict[str, Any]:
        return await services.find_target_coordinates(
            image=image,
            target=target,
            marked_image_output_path=marked_image_output_path,
            grounding_model_identifier=grounding_model_identifier,
        )

    @server.tool(
        name="edit_image",
        title="Edit image",
        description=(
            "Edit an existing image with a text prompt. Optionally provide a mask image. "
            "Uses the configured default image edit model. "
            "The output image is written to output_file_path."
        ),
        structured_output=True,
    )
    async def edit_image(
        prompt: str,
        output_file_path: str,
        input_images: Optional[List[str]] = None,
        mask_image: Optional[str] = None,
        generation_config: Optional[Dict[str, Any]] = None,
        *,
        context: Context,
    ) -> dict[str, Any]:
        return await services.edit_image(
            prompt=prompt,
            output_file_path=output_file_path,
            input_images=input_images,
            mask_image=mask_image,
            generation_config=generation_config,
        )

    @server.tool(
        name="generate_speech",
        title="Generate speech",
        description=(
            "Generate spoken audio from text using a TTS model. "
            "Uses the configured default speech model. "
            "The output audio is written to output_file_path."
        ),
        structured_output=True,
    )
    async def generate_speech(
        prompt: Annotated[
            str,
            Field(
                description=(
                    "The text to speak. You can include expressive stage directions directly in the prompt, "
                    "for example `[amused] That's a great idea! [laughs softly]` or `[pause] Let me think.` "
                    "For multi-speaker generation, put each speaker on its own line and match the labels used "
                    "in `generation_config.speaker_mapping`, for example `Joe: Hello.\\nJane: Hi.` "
                    "Gemini multi-speaker currently supports up to 2 distinct speakers; additional speech "
                    "blocks reuse those two alternating speaker slots."
                )
            ),
        ],
        output_file_path: Annotated[
            str,
            Field(
                description=(
                    "Absolute path or workspace-relative path where the generated audio file should be written."
                )
            ),
        ],
        generation_config: Annotated[
            Optional[Dict[str, Any]],
            Field(
                description=(
                    "Optional model-specific speech settings. Please call `list_audio_models` first to inspect "
                    "the live `generation_config` schema for each available model, then pass only the fields "
                    "supported by the current default speech model."
                )
            ),
        ] = None,
        *,
        context: Context,
    ) -> dict[str, Any]:
        return await services.generate_speech(
            prompt=prompt,
            output_file_path=output_file_path,
            generation_config=generation_config,
        )

    return server


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    server = create_server()
    server.run()


if __name__ == "__main__":
    main()
