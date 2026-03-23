#!/usr/bin/env python3
from __future__ import annotations

import argparse
import inspect


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate speech with XTTS v2.")
    parser.add_argument("--text", required=True)
    parser.add_argument("--output-path", required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--language", required=True)
    parser.add_argument("--speaker-wav")
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument("--device", default="auto", choices=("auto", "cpu", "cuda", "mps"))
    return parser.parse_args()


def _resolve_device(requested: str) -> str:
    if requested != "auto":
        return requested

    import torch

    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def main() -> None:
    args = _parse_args()

    from TTS.api import TTS

    device = _resolve_device(args.device)
    tts = TTS(model_name=args.model_name).to(device)
    signature = inspect.signature(tts.tts_to_file)

    kwargs: dict[str, object] = {
        "text": args.text,
        "file_path": args.output_path,
    }
    if "language" in signature.parameters:
        kwargs["language"] = args.language
    if args.speaker_wav and "speaker_wav" in signature.parameters:
        kwargs["speaker_wav"] = args.speaker_wav
    if args.speed != 1.0 and "speed" in signature.parameters:
        kwargs["speed"] = args.speed

    tts.tts_to_file(**kwargs)


if __name__ == "__main__":
    main()
