#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import runpy


def main() -> None:
    root_dir = Path(__file__).resolve().parents[1]
    target = root_dir / "src" / "tts_mcp" / "runtime_assets" / "chatterbox_generate.py"
    runpy.run_path(str(target), run_name="__main__")


if __name__ == "__main__":
    main()
