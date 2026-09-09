from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Item:
    api_name: str
    display_name: str
    composition: tuple[str, ...] = field(default_factory=tuple)
    icon_path: str | None = None

    @classmethod
    def from_cdragon(cls, raw: dict) -> "Item":
        return cls(
            api_name=raw["apiName"],
            display_name=raw.get("name", raw["apiName"]),
            composition=tuple(raw.get("composition", [])),
            icon_path=raw.get("icon"),
        )
