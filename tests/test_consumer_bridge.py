import json

import pytest

import tools.consumer_bridge as consumer_bridge
from tft.consumer_log_parser import InfoUpdate
from tools.consumer_bridge import Bridge


@pytest.fixture(autouse=True)
def _redirect_output_dir(tmp_path, monkeypatch):
    # Every stage/match transition calls save_stage(), which writes real
    # files - redirect that to a tmp dir for every test in this module so
    # nothing lands in the repo's working directory.
    monkeypatch.setattr(consumer_bridge, "OUTPUT_DIR", tmp_path)


def _round(stage: str) -> InfoUpdate:
    return InfoUpdate(category="game_info", key="tft_round", value={"round_type": "DA_Round_Combat", "stage": stage})


def _match_end() -> InfoUpdate:
    return InfoUpdate(category="game_info", key="tft_match", value="match_end")


def test_new_bridge_starts_in_pre_stage_with_a_match_id():
    bridge = Bridge()

    assert "pre-stage" in bridge.stage_path.name
    assert bridge._match_id in bridge.stage_path.name


def test_stage_change_saves_the_old_stage_file_and_starts_a_new_one():
    bridge = Bridge()

    bridge.make_entry(_round("2-1"))
    first_stage_path = bridge.stage_path
    bridge.make_entry(_round("2-2"))  # stage change - should flush "2-1" to disk

    assert first_stage_path.exists()
    saved = json.loads(first_stage_path.read_text())
    assert len(saved) == 1
    assert saved[0]["payload"]["value"]["stage"] == "2-1"
    assert "stage-2-2" in bridge.stage_path.name
    assert bridge.stage_path != first_stage_path


def test_match_end_starts_a_new_match_id_on_the_next_entry():
    bridge = Bridge()
    bridge.make_entry(_round("6-6"))
    old_match_id = bridge._match_id

    bridge.make_entry(_match_end())
    assert bridge._match_id == old_match_id  # match_end itself still belongs to the old match

    bridge.make_entry(_round("1-1"))
    assert bridge._match_id != old_match_id
    assert "stage-1-1" in bridge.stage_path.name


def test_stage_regression_without_match_end_also_starts_a_new_match():
    bridge = Bridge()
    bridge.make_entry(_round("6-6"))
    old_match_id = bridge._match_id

    bridge.make_entry(_round("1-1"))  # went backwards - a new match, even with no match_end seen

    assert bridge._match_id != old_match_id


def test_live_relay_buffer_is_unaffected_by_stage_and_match_transitions():
    bridge = Bridge()
    bridge.make_entry(_round("2-1"))
    bridge.make_entry(_round("2-2"))
    bridge.make_entry(_match_end())
    bridge.make_entry(_round("1-1"))

    assert bridge.entry_count == 4
    assert [e["payload"]["value"].get("stage") if isinstance(e["payload"]["value"], dict) else None for e in bridge.entries] == [
        "2-1",
        "2-2",
        None,
        "1-1",
    ]
