from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Champion:
    api_name: str
    display_name: str
    cost: int
    traits: tuple[str, ...] = field(default_factory=tuple)
    icon_path: str | None = None

    @classmethod
    def from_cdragon(cls, raw: dict) -> "Champion":
        return cls(
            api_name=raw["apiName"],
            display_name=raw.get("name", raw["apiName"]),
            cost=raw.get("cost", 0),
            traits=tuple(raw.get("traits", [])),
            icon_path=raw.get("tileIcon") or raw.get("icon"),
        )
