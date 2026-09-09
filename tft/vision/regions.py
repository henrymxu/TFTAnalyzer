"""Named, calibrated screen regions for the TFT client HUD.

There are no universal pixel coordinates for these - they depend on the
player's resolution, UI scale, and client version. Generate a layout for
your own machine with `python -m tools.calibrate_regions` (see README),
which saves a JSON file this class loads.
"""

from __future__ import annotations

import json
from pathlib import Path

from tft.vision.capture import FractionalRegion

# Every field a LiveStateReader knows how to fill in, if calibrated.
KNOWN_REGION_NAMES = (
    "gold",
    "level",
    "health",
    "stage_round",
    "round_timer",
    "shop_slot_0",
    "shop_slot_1",
    "shop_slot_2",
    "shop_slot_3",
    "shop_slot_4",
    "board",
)


class ScreenLayout:
    def __init__(self, regions: dict[str, FractionalRegion]):
        self._regions = regions

    def __contains__(self, name: str) -> bool:
        return name in self._regions

    def get(self, name: str) -> FractionalRegion:
        try:
            return self._regions[name]
        except KeyError as exc:
            raise KeyError(
                f"Region '{name}' is not calibrated. Run the calibration tool "
                f"(python -m tools.calibrate_regions) and select it."
            ) from exc

    def names(self) -> list[str]:
        return list(self._regions)

    @classmethod
    def empty(cls) -> "ScreenLayout":
        return cls({})

    @classmethod
    def load(cls, path: Path) -> "ScreenLayout":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        regions = {name: FractionalRegion(*rect) for name, rect in data.items()}
        return cls(regions)

    def save(self, path: Path) -> None:
        data = {name: [r.x, r.y, r.w, r.h] for name, r in self._regions.items()}
        Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")

    def set_region(self, name: str, region: FractionalRegion) -> None:
        self._regions[name] = region
