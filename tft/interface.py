"""TFTInterface: the single read-only entry point this library exposes.

It combines the official Riot API (account lookup, rank, match history)
with an optional local screen reader for live in-match state. Nothing
here writes to the game - there is no method that clicks, drags, or
sends a keystroke. If you're building toward an AI that plays TFT, this
is meant to be the "senses" half: pair it with a decision engine you run
against a local simulator (see the README) rather than wiring it up to
send actions into live matches, which breaks Riot's Terms of Service.
"""

from __future__ import annotations

from pathlib import Path

from tft.config import Settings, get_settings
from tft.models.game_state import LiveGameState
from tft.models.match import MatchSummary
from tft.riot_api.client import RiotAPIClient
from tft.static_data.cdragon import CDragonClient
from tft.vision.regions import ScreenLayout
from tft.vision.state_reader import LiveStateReader


class TFTInterface:
    def __init__(self, settings: Settings | None = None):
        self._settings = settings or get_settings()
        self._riot: RiotAPIClient | None = None
        self._cdragon = CDragonClient(self._settings)
        self._live_reader: LiveStateReader | None = None

    @property
    def riot(self) -> RiotAPIClient:
        if self._riot is None:
            self._riot = RiotAPIClient(self._settings)
        return self._riot

    @property
    def static_data(self) -> CDragonClient:
        return self._cdragon

    # -- Account / rank / match history (Riot API) --------------------------

    def get_puuid(self, game_name: str, tag_line: str) -> str:
        account = self.riot.get_account_by_riot_id(game_name, tag_line)
        return account["puuid"]

    def get_ranked_stats(self, puuid: str) -> list[dict]:
        return self.riot.get_tft_league_entries_by_puuid(puuid)

    def get_match_history(self, puuid: str, count: int = 20) -> list[MatchSummary]:
        match_ids = self.riot.get_tft_match_ids_by_puuid(puuid, count=count)
        return [MatchSummary.from_raw(mid, self.riot.get_tft_match(mid)) for mid in match_ids]

    def is_in_active_game(self, puuid: str) -> bool:
        return self.riot.get_tft_active_game_by_puuid(puuid) is not None

    # -- Live screen state (optional, local only, read-only) -----------------

    def enable_live_reading(self, layout_path: Path, templates_dir: Path | None = None) -> None:
        """Enable capture_live_state() using a screen layout you calibrated
        with tools/calibrate_regions.py for your own resolution/UI scale."""
        layout = ScreenLayout.load(layout_path)
        self._live_reader = LiveStateReader(layout, templates_dir=templates_dir)

    def capture_live_state(self) -> LiveGameState:
        if self._live_reader is None:
            raise RuntimeError("Call enable_live_reading(layout_path) first.")
        return self._live_reader.read()
