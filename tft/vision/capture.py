"""Screen capture only. There is no companion module in this package that
sends mouse or keyboard input - reading pixels is the entire interface."""

from __future__ import annotations

import numpy as np


class FractionalRegion:
    """A screen region expressed as fractions of the full screen size, so
    it stays valid across different monitor resolutions."""

    __slots__ = ("x", "y", "w", "h")

    def __init__(self, x: float, y: float, w: float, h: float):
        self.x, self.y, self.w = x, y, w
        self.h = h

    def to_pixels(self, screen_width: int, screen_height: int) -> dict:
        return {
            "left": round(self.x * screen_width),
            "top": round(self.y * screen_height),
            "width": round(self.w * screen_width),
            "height": round(self.h * screen_height),
        }


class ScreenCapture:
    """Wraps `mss` to grab screenshots as numpy BGR arrays for OpenCV."""

    def __init__(self, monitor_index: int = 1):
        import mss  # imported lazily so headless/CI environments without a display can still import this package

        self._mss = mss.mss()
        self._monitor_index = monitor_index

    @property
    def monitor(self) -> dict:
        return self._mss.monitors[self._monitor_index]

    def resolution(self) -> tuple[int, int]:
        m = self.monitor
        return m["width"], m["height"]

    def grab_full(self) -> np.ndarray:
        shot = self._mss.grab(self.monitor)
        return np.array(shot)[:, :, :3]  # drop alpha channel, BGR order

    def grab_region(self, region: FractionalRegion) -> np.ndarray:
        screen_w, screen_h = self.resolution()
        pixel_region = region.to_pixels(screen_w, screen_h)
        monitor = self.monitor
        pixel_region["left"] += monitor["left"]
        pixel_region["top"] += monitor["top"]
        shot = self._mss.grab(pixel_region)
        return np.array(shot)[:, :, :3]

    def close(self) -> None:
        self._mss.close()

    def __enter__(self) -> "ScreenCapture":
        return self

    def __exit__(self, *exc_info) -> None:
        self.close()
