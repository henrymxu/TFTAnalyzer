"""OCR helpers for the small HUD text elements (gold, level, hp, timers)."""

from __future__ import annotations

import re

import cv2
import numpy as np
import pytesseract

_DIGIT_CONFIG = "--psm 7 -c tessedit_char_whitelist=0123456789:/"


def _preprocess(image: np.ndarray, upscale: float = 3.0) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=upscale, fy=upscale, interpolation=cv2.INTER_CUBIC)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh


class OCRReader:
    def read_text(self, image: np.ndarray) -> str:
        processed = _preprocess(image)
        return pytesseract.image_to_string(processed, config="--psm 7").strip()

    def read_int(self, image: np.ndarray) -> int | None:
        processed = _preprocess(image)
        text = pytesseract.image_to_string(processed, config=_DIGIT_CONFIG)
        digits = re.sub(r"[^0-9]", "", text)
        return int(digits) if digits else None

    def read_stage_round(self, image: np.ndarray) -> str | None:
        """Reads a 'stage-round' label, e.g. '3-2'."""
        processed = _preprocess(image)
        text = pytesseract.image_to_string(processed, config=_DIGIT_CONFIG)
        match = re.search(r"(\d+)[^\d]+(\d+)", text)
        return f"{match.group(1)}-{match.group(2)}" if match else None

    def read_timer_seconds(self, image: np.ndarray) -> float | None:
        """Reads an 'mm:ss' style round timer."""
        processed = _preprocess(image)
        text = pytesseract.image_to_string(processed, config=_DIGIT_CONFIG)
        match = re.search(r"(\d+):(\d{2})", text)
        if not match:
            return None
        minutes, seconds = match.groups()
        return int(minutes) * 60 + int(seconds)
