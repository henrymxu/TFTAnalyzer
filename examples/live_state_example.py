"""Read your own current gold/level/shop off the screen, once per second,
purely as observation - nothing here clicks or types anything.

Requires you to have run `python -m tools.calibrate_regions` first, and
`python -m tools.fetch_templates` if you want shop champion recognition.

Usage:
    python -m examples.live_state_example
"""

from __future__ import annotations

import time
from pathlib import Path

from tft import TFTInterface

LAYOUT_PATH = Path("regions.local.json")


def main() -> None:
    if not LAYOUT_PATH.exists():
        print(f"No calibrated layout found at {LAYOUT_PATH}. Run: python -m tools.calibrate_regions")
        raise SystemExit(1)

    tft = TFTInterface()
    tft.enable_live_reading(LAYOUT_PATH)

    print("Reading live state, Ctrl+C to stop...")
    try:
        while True:
            state = tft.capture_live_state()
            hud = state.hud
            shop = ", ".join(s.champion_name or "?" for s in state.shop)
            print(f"gold={hud.gold} level={hud.level} hp={hud.health} round={hud.stage_round} shop=[{shop}]")
            time.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
