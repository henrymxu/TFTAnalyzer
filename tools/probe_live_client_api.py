"""One-off diagnostic: polls Riot's official Live Client Data API
(https://127.0.0.1:2999/liveclientdata/...) during a live TFT match and
dumps everything it returns, so we can see - with current, real data,
not old bug reports - exactly what is and isn't populated for TFT.

This is the same local, official, read-only endpoint League itself uses;
nothing here sends any input to the game. It only responds while a match
is actively running (the port isn't open otherwise), and its TLS
certificate is self-signed by the game client itself - hence
verify=False below, which is expected and specific to this one local
endpoint, not something to do for any other request.

Usage:
    python -m tools.probe_live_client_api
    # then start/continue a TFT match. Ctrl+C when done to save + summarize.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://127.0.0.1:2999/liveclientdata"
POLL_INTERVAL_SECONDS = 5
OUTPUT_DIR = Path("live_client_probe_output")


def fetch_all_game_data() -> dict | None:
    try:
        response = requests.get(f"{BASE_URL}/allgamedata", verify=False, timeout=3)
    except requests.exceptions.RequestException:
        return None
    if response.status_code != 200:
        return None
    try:
        return response.json()
    except ValueError:
        return None


def summarize(sample: dict) -> str:
    active_player = sample.get("activePlayer", {})
    game_data = sample.get("gameData", {})
    all_players = sample.get("allPlayers", [])
    me = next(
        (p for p in all_players if p.get("summonerName") == active_player.get("summonerName")),
        {},
    )
    parts = [
        f"mode={game_data.get('gameMode')}",
        f"time={game_data.get('gameTime')}",
        f"gold={active_player.get('currentGold')}",
        f"level={active_player.get('level')}",
        f"items={len(me.get('items', []))}",
        f"events={len(sample.get('events', {}).get('Events', []))}",
    ]
    return " ".join(parts)


def main() -> None:
    print(f"Polling {BASE_URL}/allgamedata every {POLL_INTERVAL_SECONDS}s.")
    print("Start/continue a TFT match now. Ctrl+C to stop and save.\n")

    samples: list[dict] = []
    seen_keys: set[str] = set()

    try:
        while True:
            data = fetch_all_game_data()
            if data is None:
                print("(not in a match yet - waiting...)")
                time.sleep(POLL_INTERVAL_SECONDS)
                continue

            samples.append({"ts": datetime.now(timezone.utc).isoformat(), "data": data})
            seen_keys.update(data.keys())
            try:
                print(summarize(data))
            except Exception:
                print(f"got a sample with top-level keys: {sorted(data.keys())}")

            time.sleep(POLL_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        pass

    if not samples:
        print(
            "\nNo samples captured - the endpoint never responded. "
            "Make sure you were actually in a TFT match while this ran "
            "(the port is closed outside of an active game)."
        )
        return

    OUTPUT_DIR.mkdir(exist_ok=True)
    out_path = OUTPUT_DIR / f"probe_{int(time.time())}.json"
    out_path.write_text(json.dumps(samples, indent=2), encoding="utf-8")

    print(f"\nCaptured {len(samples)} samples over ~{len(samples) * POLL_INTERVAL_SECONDS}s.")
    print(f"Saved full raw data to: {out_path}")
    print(f"Top-level keys ever seen across all samples: {sorted(seen_keys)}")
    print("\nSend that file back and I'll tell you exactly what's usable for TFT.")


if __name__ == "__main__":
    main()
