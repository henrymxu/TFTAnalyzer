"""Fetch ranked stats and recent match history for a Riot ID via the
official Riot API. Requires RIOT_API_KEY to be set (see README).

Usage:
    python -m examples.match_history_example "GameName#TAG"
"""

from __future__ import annotations

import sys

from tft import TFTInterface


def main() -> None:
    if len(sys.argv) != 2 or "#" not in sys.argv[1]:
        print('Usage: python -m examples.match_history_example "GameName#TAG"')
        raise SystemExit(1)

    game_name, tag_line = sys.argv[1].split("#", 1)
    tft = TFTInterface()

    puuid = tft.get_puuid(game_name, tag_line)
    print(f"puuid: {puuid}")

    for entry in tft.get_ranked_stats(puuid):
        print(f"{entry['queueType']}: {entry['tier']} {entry['rank']} ({entry['leaguePoints']} LP)")

    print("\nRecent matches:")
    for match in tft.get_match_history(puuid, count=5):
        me = match.participant(puuid)
        print(f"  {match.match_id}: placed {me.placement}/8, level {me.level}, {len(me.units)} units")


if __name__ == "__main__":
    main()
