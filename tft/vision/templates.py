"""Champion icon recognition via template matching against a local library
of reference images (populate with `tools/fetch_templates.py`, which pulls
icons from Community Dragon's public asset CDN - see tft/static_data)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


@dataclass(frozen=True)
class TemplateMatch:
    name: str
    confidence: float


class TemplateLibrary:
    def __init__(self, templates_dir: Path):
        self._templates_dir = Path(templates_dir)
        self._templates: dict[str, np.ndarray] = {}
        self._load()

    def _load(self) -> None:
        if not self._templates_dir.exists():
            return
        for path in self._templates_dir.glob("*.png"):
            image = cv2.imread(str(path), cv2.IMREAD_COLOR)
            if image is not None:
                self._templates[path.stem] = image

    def __len__(self) -> int:
        return len(self._templates)

    def best_match(self, image: np.ndarray, min_confidence: float = 0.75) -> TemplateMatch | None:
        best_name: str | None = None
        best_score = -1.0
        for name, template in self._templates.items():
            resized_template = cv2.resize(template, (image.shape[1], image.shape[0]))
            result = cv2.matchTemplate(image, resized_template, cv2.TM_CCOEFF_NORMED)
            score = float(result.max())
            if score > best_score:
                best_score = score
                best_name = name
        if best_name is None or best_score < min_confidence:
            return None
        return TemplateMatch(name=best_name, confidence=best_score)
