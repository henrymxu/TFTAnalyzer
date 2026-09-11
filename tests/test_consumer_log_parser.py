from tft.consumer_log_parser import Disconnected, GameEvent, InfoUpdate, parse_text

# Fragments below are taken verbatim from a real captured consumer.exe
# session against a live TFT match.

INFO_BLOCK = """\
-------------------------
Received 3 new info db updates:

<game_info, tft_gold>: 56

<game_info, tft_xp>: {"xp_level":"10", "xp_progress":"0", "xp_progress_max":"2"}

<game_info, tft_match>: match_end

-------------------------
"""

EVENT_BLOCK = """\
-------------------------
Received 1 new events:

Name: tft_shop_visible
Data: false

-------------------------
"""

SHOP_BLOCK = """\
-------------------------
Received 1 new info db updates:

<game_info, tft_shop>: {"slot_1":{"name":"DA_18_Ivern"}, "slot_2":{"name":"DA_CrimsonRaptor18"}}

-------------------------
"""

DISCONNECT_TAIL = """\
-------------------------
Received 1 new info db updates:

<plugin_status, state>: shutdown

-------------------------
Game events controller is now disconnected!
"""


def test_parses_scalar_and_object_info_updates():
    records = list(parse_text(INFO_BLOCK))

    assert records == [
        InfoUpdate(category="game_info", key="tft_gold", value=56),
        InfoUpdate(category="game_info", key="tft_xp", value={"xp_level": "10", "xp_progress": "0", "xp_progress_max": "2"}),
        InfoUpdate(category="game_info", key="tft_match", value="match_end"),
    ]


def test_parses_discrete_event_with_boolean_data():
    records = list(parse_text(EVENT_BLOCK))

    assert records == [GameEvent(name="tft_shop_visible", value=False)]


def test_parses_nested_object_value():
    records = list(parse_text(SHOP_BLOCK))

    assert records == [
        InfoUpdate(
            category="game_info",
            key="tft_shop",
            value={"slot_1": {"name": "DA_18_Ivern"}, "slot_2": {"name": "DA_CrimsonRaptor18"}},
        )
    ]


def test_parses_plugin_status_and_disconnect():
    records = list(parse_text(DISCONNECT_TAIL))

    assert records == [
        InfoUpdate(category="plugin_status", key="state", value="shutdown"),
        Disconnected(),
    ]


def test_ignores_blank_lines_and_separators_between_blocks():
    combined = INFO_BLOCK + "\n" + EVENT_BLOCK
    records = list(parse_text(combined))

    assert len(records) == 4
    assert isinstance(records[0], InfoUpdate)
    assert isinstance(records[-1], GameEvent)


def test_empty_value_parses_to_none():
    text = """\
-------------------------
Received 1 new info db updates:

<game_info, tft_board_spectate>:

-------------------------
"""
    records = list(parse_text(text))

    assert records == [InfoUpdate(category="game_info", key="tft_board_spectate", value=None)]
