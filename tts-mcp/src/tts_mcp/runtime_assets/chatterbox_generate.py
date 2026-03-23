#!/usr/bin/env python3
from __future__ import annotations

import argparse


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate speech with Chatterbox multilingual TTS.")
    parser.add_argument("--text", required=True)
    parser.add_argument("--output-path", required=True)
    parser.add_argument("--language", required=True)
    parser.add_argument("--audio-prompt-path")
    parser.add_argument("--device", default="auto", choices=("auto", "cpu", "cuda", "mps"))
    return parser.parse_args()


def _resolve_device(requested: str) -> str:
    if requested != "auto":
        return requested

    import torch

    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def main() -> None:
    args = _parse_args()

    import perth
    import torch
    import torchaudio as ta
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS

    device = _resolve_device(args.device)

    # Some Perth builds expose only the dummy implementation on macOS hosts.
    if getattr(perth, "PerthImplicitWatermarker", None) is None:
        perth.PerthImplicitWatermarker = perth.DummyWatermarker

    torch_load_original = torch.load

    def patched_torch_load(*load_args, **load_kwargs):
        load_kwargs.setdefault("map_location", torch.device(device))
        return torch_load_original(*load_args, **load_kwargs)

    torch.load = patched_torch_load
    model = ChatterboxMultilingualTTS.from_pretrained(device=device)
    wav = model.generate(
        args.text,
        language_id=args.language,
        audio_prompt_path=args.audio_prompt_path,
    )
    ta.save(args.output_path, wav.detach().cpu(), model.sr)


if __name__ == "__main__":
    main()
