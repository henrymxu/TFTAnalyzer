"""Dumps each calibrated region to a PNG (and, for text regions, the raw
OCR output before parsing) so you can see exactly what the reader is
looking at instead of guessing why a value came back as None/garbage.

Usage:
    python -m tools.debug_capture              # all calibrated regions
    python -m tools.debug_capture gold shop_slot_0
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2

from tft.vision.capture import ScreenCapture
from tft.vision.ocr import OCRReader
from tft.vision.regions import ScreenLayout

LAYOUT_PATH = Path("regions.local.json")
OUTPUT_DIR = Path(".tft_cache/debug_captures")

TEXT_REGIONS = {"gold", "level", "health"}


def main() -> None:
    if not LAYOUT_PATH.exists():
        print(f"No calibrated layout at {LAYOUT_PATH}. Run: python -m tools.calibrate_regions")
        raise SystemExit(1)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("regions", nargs="*", help="Region names to dump (default: all calibrated ones).")
    args = parser.parse_args()

    layout = ScreenLayout.load(LAYOUT_PATH)
    names = args.regions or layout.names()
    unknown = [n for n in names if n not in layout]
    if unknown:
        print(f"Not calibrated: {unknown}. Calibrated regions are: {layout.names()}")
        raise SystemExit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ocr = OCRReader()

    with ScreenCapture() as capture:
        for name in names:
            crop = capture.grab_region(layout.get(name))
            out_path = OUTPUT_DIR / f"{name}.png"
            cv2.imwrite(str(out_path), crop)

            line = f"{name}: saved {out_path} ({crop.shape[1]}x{crop.shape[0]}px)"
            if name in TEXT_REGIONS:
                line += f"  raw OCR text={ocr.read_text(crop)!r}  parsed int={ocr.read_int(crop)}"
            elif name == "stage_round":
                line += f"  parsed={ocr.read_stage_round(crop)}"
            elif name == "round_timer":
                line += f"  parsed={ocr.read_timer_seconds(crop)}"
            print(line)


if __name__ == "__main__":
    main()
