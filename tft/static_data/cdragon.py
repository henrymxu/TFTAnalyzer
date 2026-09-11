"""Static TFT set data (champions, traits, items) from Community Dragon's
public, unauthenticated data dump - the same source most community TFT
tools use for icons and set data (no API key required).

https://raw.communitydragon.org/latest/cdragon/tft/en_us.json
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

import requests

from tft.config import Settings, get_settings
from tft.models.champion import Champion
from tft.models.item import Item
from tft.models.trait import Trait

CDRAGON_SET_DATA_URL = "https://raw.communitydragon.org/latest/cdragon/tft/en_us.json"
CDRAGON_ASSET_BASE = "https://raw.communitydragon.org/latest/game/"

_CACHE_FILENAME = "cdragon_tft_en_us.json"
_CACHE_TTL_SECONDS = 6 * 60 * 60


class CDragonClient:
    def __init__(self, settings: Settings | None = None):
        self._settings = settings or get_settings()
        self._session = requests.Session()
        self._raw: dict | None = None

    @property
    def _cache_path(self) -> Path:
        self._settings.cache_dir.mkdir(parents=True, exist_ok=True)
        return self._settings.cache_dir / _CACHE_FILENAME

    def _load_raw(self, force_refresh: bool = False) -> dict:
        if self._raw is not None and not force_refresh:
            return self._raw

        cache_path = self._cache_path
        if not force_refresh and cache_path.exists():
            age = time.time() - cache_path.stat().st_mtime
            if age < _CACHE_TTL_SECONDS:
                self._raw = json.loads(cache_path.read_text(encoding="utf-8"))
                return self._raw

        response = self._session.get(CDRAGON_SET_DATA_URL, timeout=30)
        response.raise_for_status()
        self._raw = response.json()
        cache_path.write_text(json.dumps(self._raw), encoding="utf-8")
        return self._raw

    def _latest_set(self, raw: dict) -> dict:
        sets = raw.get("sets") or {}
        if not sets:
            raise ValueError("Community Dragon response had no 'sets' data")
        latest_key = max(sets, key=lambda k: int(k))
        return sets[latest_key]

    def get_champions(self, *, force_refresh: bool = False) -> list[Champion]:
        raw = self._load_raw(force_refresh)
        set_data = self._latest_set(raw)
        return [Champion.from_cdragon(c) for c in set_data.get("champions", [])]

    def get_traits(self, *, force_refresh: bool = False) -> list[Trait]:
        raw = self._load_raw(force_refresh)
        set_data = self._latest_set(raw)
        return [Trait.from_cdragon(t) for t in set_data.get("traits", [])]

    def get_items(self, *, force_refresh: bool = False) -> list[Item]:
        raw = self._load_raw(force_refresh)
        return [Item.from_cdragon(i) for i in raw.get("items", [])]

    def get_augments(self, *, force_refresh: bool = False) -> list[Item]:
        """Augments are items in Community Dragon's data model - confirmed
        against a live fetch, they live in the same top-level "items" array
        as regular items/completed items, flagged with isAugment=True,
        rather than in any separate per-set "augments" list (a set's own
        "augments" field, when present, is just bare apiName strings with
        no name/icon of their own - not useful here)."""
        raw = self._load_raw(force_refresh)
        return [Item.from_cdragon(i) for i in raw.get("items", []) if i.get("isAugment")]

    @staticmethod
    def icon_url(icon_path: str) -> str:
        """Public CDN URL for a game-relative icon path from the set data -
        directly hotlinkable from a browser <img> (no auth, no proxying
        needed), which is what tft.overwolf_server's /names.json uses."""
        normalized = re.sub(r"\.(dds|tex)$", ".png", icon_path.lower().lstrip("/"))
        return CDRAGON_ASSET_BASE + normalized

    def download_icon(self, icon_path: str) -> bytes:
        """Fetch a raw icon asset's bytes (champion tile, trait icon, ...),
        for use as a template match target - see tft.vision.templates."""
        response = self._session.get(self.icon_url(icon_path), timeout=30)
        response.raise_for_status()
        return response.content
