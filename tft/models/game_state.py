"""State reconstructed by reading the client's own screen (see tft.vision).

These are observations only - nothing in this module, or anything that
produces it, sends input back into the game.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ShopSlot:
    index: int
    champion_name: str | None
    confidence: float


@dataclass(frozen=True)
class BoardUnit:
    champion_name: str
    position: tuple[int, int]
    star_level: int
    confidence: float


@dataclass(frozen=True)
class PlayerHUD:
    gold: int | None
    level: int | None
    health: int | None
    stage_round: str | None
    round_timer_seconds: float | None


@dataclass(frozen=True)
class LiveGameState:
    captured_at: float
    hud: PlayerHUD
    shop: tuple[ShopSlot, ...] = field(default_factory=tuple)
    board: tuple[BoardUnit, ...] = field(default_factory=tuple)

    @classmethod
    def empty(cls) -> "LiveGameState":
        return cls(captured_at=time.time(), hud=PlayerHUD(None, None, None, None, None))
