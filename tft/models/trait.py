from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TraitTier:
    min_units: int
    style: str | int | None = None


@dataclass(frozen=True)
class Trait:
    api_name: str
    display_name: str
    tiers: tuple[TraitTier, ...] = field(default_factory=tuple)
    icon_path: str | None = None

    @classmethod
    def from_cdragon(cls, raw: dict) -> "Trait":
        # Verified against a live fetch of cdragon/tft/en_us.json (set 18):
        # tier breakpoints live under "effects" as {"minUnits", "maxUnits",
        # "style", ...} - "conditionalTraitSets"/"sets"/"min" (this file's
        # previous guess, unverified at the time) don't appear in the real
        # data, so tiers silently came out empty before this fix.
        tiers = tuple(
            TraitTier(min_units=t.get("minUnits", t.get("min", 0)), style=t.get("style"))
            for t in raw.get("effects", raw.get("conditionalTraitSets", raw.get("sets", [])))
        )
        return cls(
            api_name=raw["apiName"],
            display_name=raw.get("name", raw["apiName"]),
            tiers=tiers,
            icon_path=raw.get("icon"),
        )
