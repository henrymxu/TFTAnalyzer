"""Thin, read-only client for the Riot Games / TFT REST API.

Every method here is a GET request against a documented Riot endpoint
(https://developer.riotgames.com/apis). There is nothing in this client
that submits actions into a match - the API itself doesn't expose that,
and this library wouldn't use it if it did.
"""

from __future__ import annotations

import time
from typing import Any

import requests

from tft.config import Settings, get_settings
from tft.riot_api.exceptions import RateLimitError, RiotAPIError
from tft.riot_api.rate_limiter import TokenBucketLimiter

DEFAULT_TIMEOUT = 10


class RiotAPIClient:
    def __init__(self, settings: Settings | None = None, max_retries: int = 3):
        self._settings = settings or get_settings()
        if not self._settings.riot_api_key:
            raise ValueError(
                "No Riot API key configured. Set RIOT_API_KEY in the environment or a .env file "
                "(get a personal key at https://developer.riotgames.com/)."
            )
        self._max_retries = max_retries
        self._session = requests.Session()
        self._session.headers["X-Riot-Token"] = self._settings.riot_api_key
        # Default personal-key limits: 20 req/1s and 100 req/2min.
        self._short_limiter = TokenBucketLimiter(max_tokens=20, refill_seconds=1)
        self._long_limiter = TokenBucketLimiter(max_tokens=100, refill_seconds=120)

    def _get(self, host: str, path: str, params: dict[str, Any] | None = None) -> Any:
        url = f"https://{host}.api.riotgames.com{path}"
        last_error: RiotAPIError | None = None
        for attempt in range(self._max_retries + 1):
            self._short_limiter.acquire()
            self._long_limiter.acquire()
            response = self._session.get(url, params=params, timeout=DEFAULT_TIMEOUT)
            if response.status_code == 200:
                return response.json()
            if response.status_code == 429:
                retry_after = float(response.headers.get("Retry-After", 1))
                last_error = RateLimitError(response.text, url, retry_after)
                if attempt < self._max_retries:
                    time.sleep(retry_after)
                    continue
                raise last_error
            raise RiotAPIError(response.status_code, response.text, url)
        raise last_error  # pragma: no cover - unreachable, loop always returns or raises

    # -- Account (routing region: americas/europe/asia) --------------------

    def get_account_by_riot_id(self, game_name: str, tag_line: str) -> dict:
        """Look up puuid/game name/tag line for a Riot ID (e.g. 'Name#TAG')."""
        return self._get(
            self._settings.routing_region,
            f"/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}",
        )

    # -- TFT summoner / league (platform region: na1/euw1/kr/...) ----------

    def get_tft_summoner_by_puuid(self, puuid: str) -> dict:
        return self._get(self._settings.platform, f"/tft/summoner/v1/summoners/by-puuid/{puuid}")

    def get_tft_league_entries_by_puuid(self, puuid: str) -> list[dict]:
        return self._get(self._settings.platform, f"/tft/league/v1/by-puuid/{puuid}")

    def get_tft_active_game_by_puuid(self, puuid: str) -> dict | None:
        """Current live match info if the summoner is in an active game, else None."""
        try:
            return self._get(self._settings.platform, f"/tft/spectator/v5/active-games/by-puuid/{puuid}")
        except RiotAPIError as exc:
            if exc.status_code == 404:
                return None
            raise

    # -- TFT match history (routing region) ---------------------------------

    def get_tft_match_ids_by_puuid(self, puuid: str, count: int = 20, start: int = 0) -> list[str]:
        return self._get(
            self._settings.routing_region,
            f"/tft/match/v1/matches/by-puuid/{puuid}/ids",
            params={"count": count, "start": start},
        )

    def get_tft_match(self, match_id: str) -> dict:
        return self._get(self._settings.routing_region, f"/tft/match/v1/matches/{match_id}")
