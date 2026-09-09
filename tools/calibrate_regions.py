"""Interactive one-time calibration: draw a box around each HUD element on
your own screen, so tft.vision can find gold/level/shop/etc regardless of
your resolution or UI scale.

Usage:
    1. Open TFT (or just have the client/a screenshot of the match screen visible).
    2. python -m tools.calibrate_regions
    3. For each prompted region, drag a box around it in the popup window,
       then press ENTER (or SPACE) to confirm, or 'c' to skip that region.

This tool only takes a screenshot and reads back the boxes you draw with
the mouse in its own preview window - it never sends input to any other
application, including the game.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2

from tft.vision.capture import FractionalRegion, ScreenCapture
from tft.vision.regions import KNOWN_REGION_NAMES, ScreenLayout

DEFAULT_OUTPUT = Path("regions.local.json")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--regions",
        nargs="*",
        default=list(KNOWN_REGION_NAMES),
        help="Subset of region names to calibrate (default: all known regions).",
    )
    args = parser.parse_args()

    layout = ScreenLayout.load(args.output) if args.output.exists() else ScreenLayout.empty()

    with ScreenCapture() as capture:
        screen_w, screen_h = capture.resolution()
        frame = capture.grab_full()

        for name in args.regions:
            window = f"Select region: {name}  (ENTER=confirm, c=skip)"
            x, y, w, h = cv2.selectROI(window, frame, showCrosshair=True, fromCenter=False)
            cv2.destroyWindow(window)
            if w == 0 or h == 0:
                print(f"skipped {name}")
                continue
            layout.set_region(name, FractionalRegion(x / screen_w, y / screen_h, w / screen_w, h / screen_h))
            print(f"set {name} = ({x}, {y}, {w}, {h}) px")

    layout.save(args.output)
    print(f"saved layout to {args.output}")


if __name__ == "__main__":
    main()
