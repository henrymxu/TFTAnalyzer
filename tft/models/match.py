"""Parsed views over the raw JSON returned by the TFT match-v5 endpoint."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MatchUnit:
    character_id: str
    tier: int
    rarity: int
    items: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def from_raw(cls, raw: dict) -> "MatchUnit":
        return cls(
            character_id=raw["character_id"],
            tier=raw.get("tier", 1),
            rarity=raw.get("rarity", 0),
            items=tuple(raw.get("itemNames", [])),
        )


@dataclass(frozen=True)
class MatchTrait:
    name: str
    num_units: int
    tier_current: int
    tier_total: int

    @classmethod
    def from_raw(cls, raw: dict) -> "MatchTrait":
        return cls(
            name=raw["name"],
            num_units=raw.get("num_units", 0),
            tier_current=raw.get("tier_current", 0),
            tier_total=raw.get("tier_total", 0),
        )


@dataclass(frozen=True)
class MatchParticipant:
    puuid: str
    placement: int
    level: int
    gold_left: int
    last_round: int
    players_eliminated: int
    total_damage_to_players: int
    traits: tuple[MatchTrait, ...]
    units: tuple[MatchUnit, ...]

    @classmethod
    def from_raw(cls, raw: dict) -> "MatchParticipant":
        return cls(
            puuid=raw["puuid"],
            placement=raw["placement"],
            level=raw.get("level", 0),
            gold_left=raw.get("gold_left", 0),
            last_round=raw.get("last_round", 0),
            players_eliminated=raw.get("players_eliminated", 0),
            total_damage_to_players=raw.get("total_damage_to_players", 0),
            traits=tuple(MatchTrait.from_raw(t) for t in raw.get("traits", [])),
            units=tuple(MatchUnit.from_raw(u) for u in raw.get("units", [])),
        )


@dataclass(frozen=True)
class MatchSummary:
    match_id: str
    game_datetime_ms: int
    game_length_seconds: float
    tft_set_number: int
    participants: tuple[MatchParticipant, ...]

    @classmethod
    def from_raw(cls, match_id: str, raw: dict) -> "MatchSummary":
        info = raw["info"]
        return cls(
            match_id=match_id,
            game_datetime_ms=info["game_datetime"],
            game_length_seconds=info["game_length"],
            tft_set_number=info.get("tft_set_number", 0),
            participants=tuple(MatchParticipant.from_raw(p) for p in info["participants"]),
        )

    def participant(self, puuid: str) -> MatchParticipant | None:
        return next((p for p in self.participants if p.puuid == puuid), None)
