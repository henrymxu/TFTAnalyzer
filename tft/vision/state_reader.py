"""Combines screen capture + OCR + template matching into a LiveGameState
snapshot. This module only reads pixels off the screen; it has no
capability to move the mouse, press keys, or otherwise act in the game.
"""

from __future__ import annotations

import time
from pathlib import Path

from tft.models.game_state import LiveGameState, PlayerHUD, ShopSlot
from tft.vision.capture import ScreenCapture
from tft.vision.ocr import OCRReader
from tft.vision.regions import ScreenLayout
from tft.vision.templates import TemplateLibrary

SHOP_SLOT_NAMES = ("shop_slot_0", "shop_slot_1", "shop_slot_2", "shop_slot_3", "shop_slot_4")


class LiveStateReader:
    def __init__(
        self,
        layout: ScreenLayout,
        capture: ScreenCapture | None = None,
        ocr: OCRReader | None = None,
        templates: TemplateLibrary | None = None,
        templates_dir: Path | None = None,
    ):
        self._layout = layout
        self._capture = capture or ScreenCapture()
        self._ocr = ocr or OCRReader()
        self._templates = templates or TemplateLibrary(templates_dir or Path("data/templates/champions"))

    def _read_int_region(self, name: str) -> int | None:
        if name not in self._layout:
            return None
        return self._ocr.read_int(self._capture.grab_region(self._layout.get(name)))

    def _read_hud(self) -> PlayerHUD:
        stage_round = None
        timer_seconds = None
        if "stage_round" in self._layout:
            stage_round = self._ocr.read_stage_round(self._capture.grab_region(self._layout.get("stage_round")))
        if "round_timer" in self._layout:
            timer_seconds = self._ocr.read_timer_seconds(self._capture.grab_region(self._layout.get("round_timer")))
        return PlayerHUD(
            gold=self._read_int_region("gold"),
            level=self._read_int_region("level"),
            health=self._read_int_region("health"),
            stage_round=stage_round,
            round_timer_seconds=timer_seconds,
        )

    def _read_shop(self) -> tuple[ShopSlot, ...]:
        slots = []
        for index, name in enumerate(SHOP_SLOT_NAMES):
            if name not in self._layout:
                continue
            crop = self._capture.grab_region(self._layout.get(name))
            match = self._templates.best_match(crop)
            slots.append(
                ShopSlot(
                    index=index,
                    champion_name=match.name if match else None,
                    confidence=match.confidence if match else 0.0,
                )
            )
        return tuple(slots)

    def read(self) -> LiveGameState:
        """Take one read-only snapshot of the current screen."""
        return LiveGameState(
            captured_at=time.time(),
            hud=self._read_hud(),
            shop=self._read_shop(),
        )
