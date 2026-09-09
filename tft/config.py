"""Runtime configuration, loaded from environment variables / .env."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Riot's regional routing values for TFT match-v5 / account-v1 endpoints.
REGION_TO_ROUTING = {
    "na1": "americas",
    "br1": "americas",
    "la1": "americas",
    "la2": "americas",
    "oc1": "americas",
    "kr": "asia",
    "jp1": "asia",
    "euw1": "europe",
    "eun1": "europe",
    "tr1": "europe",
    "ru": "europe",
}

CACHE_DIR = Path(os.environ.get("TFT_CACHE_DIR", ".tft_cache"))


@dataclass(frozen=True)
class Settings:
    riot_api_key: str | None = field(default_factory=lambda: os.environ.get("RIOT_API_KEY"))
    platform: str = field(default_factory=lambda: os.environ.get("RIOT_PLATFORM", "na1").lower())
    cache_dir: Path = CACHE_DIR

    @property
    def routing_region(self) -> str:
        try:
            return REGION_TO_ROUTING[self.platform]
        except KeyError as exc:
            raise ValueError(
                f"Unknown platform '{self.platform}'. Valid values: {sorted(REGION_TO_ROUTING)}"
            ) from exc


def get_settings() -> Settings:
    return Settings()
