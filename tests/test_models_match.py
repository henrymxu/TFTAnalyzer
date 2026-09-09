from tft.models.match import MatchSummary

RAW_MATCH = {
    "info": {
        "game_datetime": 1700000000000,
        "game_length": 2145.6,
        "tft_set_number": 11,
        "participants": [
            {
                "puuid": "player-1",
                "placement": 1,
                "level": 9,
                "gold_left": 4,
                "last_round": 32,
                "players_eliminated": 3,
                "total_damage_to_players": 120,
                "traits": [{"name": "TFT11_Vanguard", "num_units": 4, "tier_current": 2, "tier_total": 3}],
                "units": [
                    {"character_id": "TFT11_Ahri", "tier": 2, "rarity": 4, "itemNames": ["TFT_Item_BlueBuff"]},
                ],
            },
            {
                "puuid": "player-2",
                "placement": 8,
                "level": 7,
                "gold_left": 0,
                "last_round": 15,
                "players_eliminated": 0,
                "total_damage_to_players": 20,
                "traits": [],
                "units": [],
            },
        ],
    }
}


def test_parses_match_summary_fields():
    summary = MatchSummary.from_raw("NA1_123", RAW_MATCH)

    assert summary.match_id == "NA1_123"
    assert summary.tft_set_number == 11
    assert len(summary.participants) == 2


def test_parses_participant_units_and_traits():
    summary = MatchSummary.from_raw("NA1_123", RAW_MATCH)
    winner = summary.participant("player-1")

    assert winner.placement == 1
    assert winner.units[0].character_id == "TFT11_Ahri"
    assert winner.units[0].items == ("TFT_Item_BlueBuff",)
    assert winner.traits[0].tier_current == 2


def test_participant_lookup_returns_none_for_unknown_puuid():
    summary = MatchSummary.from_raw("NA1_123", RAW_MATCH)
    assert summary.participant("nonexistent") is None
