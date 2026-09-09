import json

from tft.overwolf_bridge import OverwolfEventReader

ENTRY_1 = {"seq": 1, "ts": 1000, "kind": "info_update", "payload": {"me": {"level": 1}}}
ENTRY_2 = {"seq": 2, "ts": 1001, "kind": "event", "payload": {"round_outcome": "victory"}}
ENTRY_3 = {"seq": 3, "ts": 1002, "kind": "event", "payload": {"round_outcome": "defeat"}}


def test_missing_file_returns_no_events(tmp_path):
    reader = OverwolfEventReader(tmp_path / "does-not-exist.json")
    assert reader.read_new() == []


def test_reads_all_entries_on_first_poll(tmp_path):
    events_path = tmp_path / "events.json"
    events_path.write_text(json.dumps([ENTRY_1, ENTRY_2]))

    reader = OverwolfEventReader(events_path)
    events = reader.read_new()

    assert [e.seq for e in events] == [1, 2]
    assert events[1].kind == "event"
    assert events[1].payload == {"round_outcome": "victory"}


def test_second_poll_only_returns_events_past_last_seen_seq(tmp_path):
    events_path = tmp_path / "events.json"
    events_path.write_text(json.dumps([ENTRY_1, ENTRY_2]))
    reader = OverwolfEventReader(events_path)
    reader.read_new()

    events_path.write_text(json.dumps([ENTRY_1, ENTRY_2, ENTRY_3]))
    events = reader.read_new()

    assert [e.seq for e in events] == [3]


def test_malformed_json_returns_empty_instead_of_raising(tmp_path):
    events_path = tmp_path / "events.json"
    events_path.write_text("{not valid json, mid-write}")

    reader = OverwolfEventReader(events_path)

    assert reader.read_new() == []
