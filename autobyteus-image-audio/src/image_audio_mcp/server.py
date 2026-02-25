from __future__ import annotations

import base64
import io
import json
import logging
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import unquote_to_bytes
from urllib.request import urlopen

from mcp.server.fastmcp import Context, FastMCP
from PIL import Image

from autobyteus.multimedia.audio import AudioClientFactory, AudioModel
from autobyteus.multimedia.image import ImageClientFactory, ImageModel
from autobyteus.llm.llm_factory import LLMFactory
from autobyteus.llm.models import LLMModel
from autobyteus.llm.user_message import LLMUserMessage
from autobyteus.utils.download_utils import download_file_from_url
from autobyteus.utils.file_utils import resolve_safe_path

logger = logging.getLogger(__name__)

DEFAULT_SERVER_NAME = "autobyteus-image-audio"
DEFAULT_INSTRUCTIONS = (
    "Expose Autobyteus image and audio generation tools. "
    "Outputs are written to local files under the configured workspace, Downloads, or temp directories."
)

DEFAULT_IMAGE_GENERATION_MODEL = "gpt-image-1.5"
DEFAULT_IMAGE_EDIT_MODEL = "gpt-image-1.5"
DEFAULT_SPEECH_MODEL = "gemini-2.5-flash-tts"
DEFAULT_GROUNDING_MODEL = "gpt-5.2"
DEFAULT_GROUNDING_SYSTEM_PROMPT = (
    "You are a visual grounding assistant for GUI automation. "
    "Given a screenshot and intent, return the center of the target clickable element as strict JSON only."
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


def _get_workspace_root() -> str:
    workspace = os.getenv("AUTOBYTEUS_AGENT_WORKSPACE")
    if workspace:
        return workspace
    return os.getcwd()


def _is_url_like(value: str) -> bool:
    lowered = value.lower()
    return lowered.startswith("http://") or lowered.startswith("https://") or lowered.startswith("data:")


def _normalize_media_source(value: str, workspace_root: str) -> str:
    if _is_url_like(value):
        return value
    resolved = resolve_safe_path(value, workspace_root)
    if not resolved.exists():
        raise FileNotFoundError(f"Input file not found: {resolved}")
    return str(resolved)


def _normalize_media_sources(values: Optional[Iterable[str]], workspace_root: str) -> Optional[List[str]]:
    if not values:
        return None
    return [_normalize_media_source(item, workspace_root) for item in values]


def _resolve_output_path(value: str, workspace_root: str) -> Path:
    return resolve_safe_path(value, workspace_root)


def _get_default_grounding_model() -> str:
    if os.environ.get("DEFAULT_GROUNDING_MODEL"):
        return os.environ["DEFAULT_GROUNDING_MODEL"]
    return DEFAULT_GROUNDING_MODEL


def _get_default_image_generation_model() -> str:
    return os.environ.get("DEFAULT_IMAGE_GENERATION_MODEL", DEFAULT_IMAGE_GENERATION_MODEL)


def _get_default_image_edit_model() -> str:
    return os.environ.get("DEFAULT_IMAGE_EDIT_MODEL", DEFAULT_IMAGE_EDIT_MODEL)


def _get_default_speech_model() -> str:
    return os.environ.get("DEFAULT_SPEECH_GENERATION_MODEL", DEFAULT_SPEECH_MODEL)


def _extract_first_json_object(raw_text: str) -> Dict[str, Any]:
    text = (raw_text or "").strip()
    if not text:
        raise ValueError("Model returned an empty response.")

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    decoder = json.JSONDecoder()
    for idx, char in enumerate(text):
        if char != "{":
            continue
        try:
            parsed, _ = decoder.raw_decode(text[idx:])
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed

    raise ValueError("Model did not return a valid JSON object.")


def _as_optional_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _get_grounding_relative_coordinate_max() -> float:
    raw = os.environ.get("GROUNDING_RELATIVE_COORDINATE_MAX", "1000")
    try:
        value = float(raw)
    except ValueError:
        return 1000.0
    if value <= 1.0:
        return 1000.0
    return value


def _extract_normalized_coordinates(
    payload: Dict[str, Any],
    image_size: Optional[Tuple[int, int]] = None,
) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[str], Optional[str]]:
    x = _as_optional_float(payload.get("x"))
    y = _as_optional_float(payload.get("y"))

    if x is None or y is None:
        point = payload.get("point")
        if isinstance(point, dict):
            x = _as_optional_float(point.get("x"))
            y = _as_optional_float(point.get("y"))

    coordinate_mode: Optional[str] = None
    if x is not None and y is not None:
        # Case 1: already normalized [0, 1].
        if 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0:
            coordinate_mode = "normalized_0_1"
        # Case 2: absolute pixels from the image coordinate system.
        elif image_size is not None:
            width, height = image_size
            if width > 0 and height > 0 and 0.0 <= x <= width and 0.0 <= y <= height:
                x = x / float(width)
                y = y / float(height)
                coordinate_mode = "pixel_absolute"
        # Case 3: Qwen-style relative coordinates (typically 0..1000 or 0..999).
        if coordinate_mode is None and 0.0 <= x <= 1000.0 and 0.0 <= y <= 1000.0:
            relative_max = _get_grounding_relative_coordinate_max()
            x = x / relative_max
            y = y / relative_max
            coordinate_mode = f"relative_0_{int(relative_max)}"

    if x is not None and y is not None and coordinate_mode is None:
        coordinate_mode = "clamped_fallback"

    if x is not None:
        x = max(0.0, min(1.0, x))
    if y is not None:
        y = max(0.0, min(1.0, y))

    confidence = _as_optional_float(payload.get("confidence"))
    if confidence is not None:
        confidence = max(0.0, min(1.0, confidence))

    reason = payload.get("reason")
    if reason is not None and not isinstance(reason, str):
        reason = str(reason)

    return x, y, confidence, reason, coordinate_mode


def _read_image_bytes(media_source: str) -> bytes:
    if media_source.startswith("data:"):
        _, encoded = media_source.split(",", 1)
        if ";base64" in media_source[: media_source.find(",")]:
            return base64.b64decode(encoded)
        return unquote_to_bytes(encoded)

    if media_source.startswith(("http://", "https://")):
        with urlopen(media_source, timeout=10) as response:
            return response.read()

    return Path(media_source).read_bytes()


def _get_image_size(media_source: str) -> Optional[Tuple[int, int]]:
    try:
        image_bytes = _read_image_bytes(media_source)
        with Image.open(io.BytesIO(image_bytes)) as image:
            return image.width, image.height
    except Exception as exc:
        logger.warning("Unable to infer image size for '%s': %s", media_source, exc)
        return None


def _detect_magenta_marker_center(media_source: str) -> Optional[Tuple[float, float, int]]:
    try:
        image_bytes = _read_image_bytes(media_source)
        with Image.open(io.BytesIO(image_bytes)) as image:
            rgb = image.convert("RGB")
            width, height = rgb.size
            pixels = rgb.getdata()
    except Exception as exc:
        logger.warning("Unable to read edited image for marker detection: %s", exc)
        return None

    xs: List[int] = []
    ys: List[int] = []

    # Robust magenta detector for marker-like pixels.
    for idx, (r, g, b) in enumerate(pixels):
        if r < 170 or b < 170:
            continue
        if g > 130:
            continue
        if abs(int(r) - int(b)) > 90:
            continue
        x = idx % width
        y = idx // width
        xs.append(x)
        ys.append(y)

    if not xs:
        return None

    # Trim outliers around median to stabilize centroid.
    x_sorted = sorted(xs)
    y_sorted = sorted(ys)
    x_median = x_sorted[len(x_sorted) // 2]
    y_median = y_sorted[len(y_sorted) // 2]

    xs_core: List[int] = []
    ys_core: List[int] = []
    for x, y in zip(xs, ys):
        if abs(x - x_median) <= 40 and abs(y - y_median) <= 40:
            xs_core.append(x)
            ys_core.append(y)

    if xs_core:
        xs = xs_core
        ys = ys_core

    x_center = sum(xs) / float(len(xs))
    y_center = sum(ys) / float(len(ys))
    return x_center, y_center, len(xs)


async def _safe_cleanup(client: Any) -> None:
    try:
        await client.cleanup()
    except Exception as exc:
        logger.warning("Failed to cleanup client: %s", exc)


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
        return {
            "status": "ok",
            "default_image_generation_model": _get_default_image_generation_model(),
            "default_image_edit_model": _get_default_image_edit_model(),
            "default_speech_model": _get_default_speech_model(),
            "default_grounding_model": _get_default_grounding_model(),
        }

    @server.tool(
        name="list_audio_models",
        title="List audio models",
        description="List available audio models and their generation_config schemas.",
        structured_output=True,
    )
    async def list_audio_models(*, context: Context) -> dict[str, Any]:
        AudioClientFactory.ensure_initialized()
        models: List[Dict[str, Any]] = []
        for model in AudioModel:
            models.append(
                {
                    "model_identifier": model.model_identifier,
                    "name": model.name,
                    "value": model.value,
                    "provider": model.provider.value,
                    "runtime": model.runtime.value,
                    "parameter_schema": model.parameter_schema.to_json_schema_dict(),
                    "default_config": model.default_config.to_dict(),
                }
            )
        return {"models": models}

    @server.tool(
        name="list_image_models",
        title="List image models",
        description="List available image models and their generation_config schemas.",
        structured_output=True,
    )
    async def list_image_models(*, context: Context) -> dict[str, Any]:
        ImageClientFactory.ensure_initialized()
        models: List[Dict[str, Any]] = []
        for model in ImageModel:
            models.append(
                {
                    "model_identifier": model.model_identifier,
                    "name": model.name,
                    "value": model.value,
                    "provider": model.provider.value,
                    "runtime": model.runtime.value,
                    "parameter_schema": model.parameter_schema.to_json_schema_dict(),
                    "default_config": model.default_config.to_dict(),
                }
            )
        return {"models": models}

    @server.tool(
        name="list_visual_grounding_models",
        title="List visual grounding models",
        description=(
            "List available LLM models for screenshot grounding tasks. "
            "Image support can vary by provider/model."
        ),
        structured_output=True,
    )
    async def list_visual_grounding_models(*, context: Context) -> dict[str, Any]:
        LLMFactory.ensure_initialized()
        models: List[Dict[str, Any]] = []
        for model in LLMModel:
            models.append(
                {
                    "model_identifier": model.model_identifier,
                    "name": model.name,
                    "value": model.value,
                    "provider": model.provider.value,
                    "runtime": model.runtime.value,
                    "canonical_name": model.canonical_name,
                    "config_schema": (
                        model.config_schema.to_json_schema_dict()
                        if model.config_schema
                        else None
                    ),
                    "default_config": model.default_config.to_dict(),
                }
            )
        return {
            "models": models,
            "note": "Use a model that supports image input for grounding accuracy.",
        }

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
        workspace_root = _get_workspace_root()
        resolved_output = _resolve_output_path(output_file_path, workspace_root)
        normalized_inputs = _normalize_media_sources(input_images, workspace_root)
        model_id = _get_default_image_generation_model()

        client = ImageClientFactory.create_image_client(model_id)
        try:
            response = await client.generate_image(
                prompt=prompt,
                input_image_urls=normalized_inputs,
                generation_config=generation_config,
            )
            if not response.image_urls:
                raise ValueError("Image generation returned no image URLs.")
            await download_file_from_url(response.image_urls[0], resolved_output)
            return {
                "file_path": str(resolved_output),
                "model": model_id,
                "revised_prompt": getattr(response, "revised_prompt", None),
            }
        finally:
            await _safe_cleanup(client)

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
        workspace_root = _get_workspace_root()
        normalized_image = _normalize_media_source(image, workspace_root)

        return await _find_target_coordinates_via_edit_marker_impl(
            normalized_image=normalized_image,
            target=target,
            workspace_root=workspace_root,
            grounding_model_identifier=grounding_model_identifier,
            marked_image_output_path=marked_image_output_path,
        )

    async def _find_target_coordinates_vlm_impl(
        *,
        normalized_image: str,
        intent: str,
        model_identifier: Optional[str] = None,
    ) -> dict[str, Any]:
        image_size = _get_image_size(normalized_image)
        model_id = model_identifier or _get_default_grounding_model()

        instructions = [
            f"Intent: {intent}",
            "Return only a JSON object with keys: x, y, confidence, reason.",
            "Pick the center of the target clickable UI element.",
            "x and y should be normalized coordinates in [0, 1], where (0,0) is top-left.",
            "If the target is not visible, return x=null, y=null, confidence=0.",
            "Do not return markdown or code fences.",
        ]
        if image_size is not None:
            width, height = image_size
            instructions.append(f"Image size is {width}x{height} pixels.")

        llm = LLMFactory.create_llm(model_id)
        llm.configure_system_prompt(DEFAULT_GROUNDING_SYSTEM_PROMPT)
        try:
            response = await llm.send_user_message(
                LLMUserMessage(content="\n".join(instructions), image_urls=[normalized_image])
            )
            payload = _extract_first_json_object(response.content)
            x_norm, y_norm, confidence, reason, coordinate_mode = _extract_normalized_coordinates(
                payload, image_size=image_size
            )

            pixel_coordinates: Optional[Dict[str, int]] = None
            if image_size is not None and x_norm is not None and y_norm is not None:
                width, height = image_size
                pixel_x = int(round(x_norm * (width - 1)))
                pixel_y = int(round(y_norm * (height - 1)))
                pixel_coordinates = {"x": pixel_x, "y": pixel_y}

            return {
                "model": model_id,
                "intent": intent,
                "normalized_coordinates": (
                    {"x": x_norm, "y": y_norm}
                    if x_norm is not None and y_norm is not None
                    else None
                ),
                "pixel_coordinates": pixel_coordinates,
                "image_size": (
                    {"width": image_size[0], "height": image_size[1]}
                    if image_size is not None
                    else None
                ),
                "confidence": confidence,
                "reason": reason,
                "coordinate_mode": coordinate_mode,
                "raw_response": response.content,
            }
        finally:
            await _safe_cleanup(llm)

    async def _find_target_coordinates_via_edit_marker_impl(
        *,
        normalized_image: str,
        target: str,
        workspace_root: str,
        grounding_model_identifier: Optional[str] = None,
        marked_image_output_path: Optional[str] = None,
    ) -> dict[str, Any]:
        original_size = _get_image_size(normalized_image)
        if original_size is None:
            raise ValueError("Unable to infer original image size.")

        if marked_image_output_path:
            resolved_marked = _resolve_output_path(marked_image_output_path, workspace_root)
        else:
            tmp_dir = Path(tempfile.gettempdir())
            resolved_marked = tmp_dir / f"edit_marker_{os.getpid()}_{abs(hash(target)) % 100000}.png"

        edit_prompt = (
            "Task: place one locator marker for GUI automation without changing layout. "
            "Do not redesign, restyle, crop, resize, blur, or move any UI element. Keep original geometry.\n"
            f"Target to mark: {target}\n"
            "Look very, very carefully at the exact target sentence/label before placing the marker.\n"
            "Marker requirements:\n"
            "- Add exactly one small high-contrast magenta crosshair.\n"
            "- Keep the crosshair geometry symmetric: 4 equal arms around one intersection center.\n"
            "- Make it compact and consistent: arm length about 8-12 px and stroke width about 2 px.\n"
            "- Keep edges crisp: no blur, glow, feather, shadow, or anti-aliased halo around the marker.\n"
            "- Marker center must be ON the target's own pixels, never on nearby whitespace.\n"
            "- For text targets, put the center on the text glyph area itself (not to the right/left of the text).\n"
            "- For button/input/icon targets, put the center inside the target bounds near its visual center.\n"
            "- If multiple similar texts/chips/buttons exist, mark only the exact requested one.\n"
            "- Never choose the nearest neighbor or a semantically similar alternative.\n"
            "- Do not mark neighboring elements that are semantically related but not the requested target.\n"
            "- If exact disambiguation is uncertain, prefer the element whose visible text best exactly matches the target phrase.\n"
            "- Do not add labels, arrows, extra dots, highlights, boxes, or any second marker."
        )

        edit_model = _get_default_image_edit_model()
        image_client = ImageClientFactory.create_image_client(edit_model)
        try:
            edit_response = await image_client.edit_image(
                prompt=edit_prompt,
                input_image_urls=[normalized_image],
                mask_url=None,
                generation_config=None,
            )
            if not edit_response.image_urls:
                raise ValueError("Marker edit returned no image URL.")
            await download_file_from_url(edit_response.image_urls[0], resolved_marked)
        finally:
            await _safe_cleanup(image_client)

        marked_size = _get_image_size(str(resolved_marked))
        if marked_size is None:
            raise ValueError("Unable to infer edited image size.")

        detection = _detect_magenta_marker_center(str(resolved_marked))
        detection_method = "color_magenta"
        marker_confidence: Optional[float] = None
        marker_reason: Optional[str] = None

        marker_x: Optional[float] = None
        marker_y: Optional[float] = None
        marker_pixels_detected: Optional[int] = None
        if detection is not None:
            marker_x, marker_y, marker_pixels_detected = detection
        else:
            model_id = grounding_model_identifier or _get_default_grounding_model()
            llm = LLMFactory.create_llm(model_id)
            llm.configure_system_prompt(DEFAULT_GROUNDING_SYSTEM_PROMPT)
            try:
                fallback_instructions = [
                    "Find the center of the magenta crosshair marker in this image.",
                    "Return only a JSON object with keys: x, y, confidence, reason.",
                    "x and y should be normalized coordinates in [0, 1].",
                    "Do not return markdown or code fences.",
                ]
                fallback_response = await llm.send_user_message(
                    LLMUserMessage(content="\n".join(fallback_instructions), image_urls=[str(resolved_marked)])
                )
                fallback_payload = _extract_first_json_object(fallback_response.content)
                x_norm, y_norm, marker_confidence, marker_reason, _ = _extract_normalized_coordinates(
                    fallback_payload, image_size=marked_size
                )
                if x_norm is None or y_norm is None:
                    raise ValueError("Fallback grounding failed to locate marker.")
                marker_x = x_norm * marked_size[0]
                marker_y = y_norm * marked_size[1]
                detection_method = "llm_fallback"
            finally:
                await _safe_cleanup(llm)

        if marker_x is None or marker_y is None:
            raise ValueError("Unable to locate marker center.")

        ow, oh = original_size
        mw, mh = marked_size
        x_original = marker_x * float(ow) / float(mw)
        y_original = marker_y * float(oh) / float(mh)

        x_original = max(0.0, min(float(ow - 1), x_original))
        y_original = max(0.0, min(float(oh - 1), y_original))
        x_pixel = int(round(x_original))
        y_pixel = int(round(y_original))

        return {
            "strategy": "edit_marker",
            "target": target,
            "intent": target,
            "edit_model": edit_model,
            "marked_image_path": str(resolved_marked),
            "original_image_size": {"width": ow, "height": oh},
            "marked_image_size": {"width": mw, "height": mh},
            "marker_center_in_marked_image": {"x": marker_x, "y": marker_y},
            "marker_pixels_detected": marker_pixels_detected,
            "detection_method": detection_method,
            "marker_confidence": marker_confidence,
            "marker_reason": marker_reason,
            "pixel_coordinates": {"x": x_pixel, "y": y_pixel},
            "normalized_coordinates": {
                "x": x_pixel / float(max(1, ow - 1)),
                "y": y_pixel / float(max(1, oh - 1)),
            },
        }

    @server.tool(
        name="find_target_coordinates_vlm",
        title="Find target coordinates (VLM)",
        description=(
            "Alternative VLM-only grounding path. Given a screenshot and intent, ask a vision-capable "
            "LLM directly for normalized and pixel target coordinates."
        ),
        structured_output=True,
    )
    async def find_target_coordinates_vlm(
        image: str,
        intent: str,
        model_identifier: Optional[str] = None,
        *,
        context: Context,
    ) -> dict[str, Any]:
        workspace_root = _get_workspace_root()
        normalized_image = _normalize_media_source(image, workspace_root)
        return await _find_target_coordinates_vlm_impl(
            normalized_image=normalized_image,
            intent=intent,
            model_identifier=model_identifier,
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
        workspace_root = _get_workspace_root()
        resolved_output = _resolve_output_path(output_file_path, workspace_root)
        normalized_inputs = _normalize_media_sources(input_images, workspace_root) or []
        normalized_mask = (
            _normalize_media_source(mask_image, workspace_root) if mask_image else None
        )
        model_id = _get_default_image_edit_model()

        client = ImageClientFactory.create_image_client(model_id)
        try:
            response = await client.edit_image(
                prompt=prompt,
                input_image_urls=normalized_inputs,
                mask_url=normalized_mask,
                generation_config=generation_config,
            )
            if not response.image_urls:
                raise ValueError("Image editing returned no image URLs.")
            await download_file_from_url(response.image_urls[0], resolved_output)
            return {
                "file_path": str(resolved_output),
                "model": model_id,
            }
        finally:
            await _safe_cleanup(client)

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
        prompt: str,
        output_file_path: str,
        generation_config: Optional[Dict[str, Any]] = None,
        *,
        context: Context,
    ) -> dict[str, Any]:
        workspace_root = _get_workspace_root()
        resolved_output = _resolve_output_path(output_file_path, workspace_root)
        model_id = _get_default_speech_model()

        client = AudioClientFactory.create_audio_client(model_id)
        try:
            response = await client.generate_speech(
                prompt=prompt,
                generation_config=generation_config,
            )
            if not response.audio_urls:
                raise ValueError("Speech generation returned no audio URLs.")
            await download_file_from_url(response.audio_urls[0], resolved_output)
            return {
                "file_path": str(resolved_output),
                "model": model_id,
            }
        finally:
            await _safe_cleanup(client)

    return server


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    server = create_server()
    server.run()


if __name__ == "__main__":
    main()
