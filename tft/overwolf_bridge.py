"""Reads the events.json file written by overwolf-app/background.js.

This is the Python-side half of the Overwolf proxy: the Overwolf app only
writes a JSON file (see overwolf-app/README.md for the exact contract),
and this module just polls and parses it. No Overwolf SDK, network calls,
or special permissions are needed here - it's a plain file reader.
"""

from __future__ import annotations

import json
import time
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class OverwolfEvent:
    seq: int
    ts_ms: int
    kind: str  # "event" | "info_update" | "error"
    payload: dict


def default_events_path() -> Path:
    return Path.home() / "Documents" / "TFTEventsProxy" / "events.json"


class OverwolfEventReader:
    def __init__(self, events_path: Path):
        self._path = Path(events_path)
        self._last_seq = 0

    def read_new(self) -> list[OverwolfEvent]:
        """Return events with seq greater than the highest already returned."""
        if not self._path.exists():
            return []
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            # The Overwolf app may be mid-write; just try again next poll.
            return []

        new_events = [
            OverwolfEvent(seq=e["seq"], ts_ms=e["ts"], kind=e["kind"], payload=e["payload"])
            for e in raw
            if e["seq"] > self._last_seq
        ]
        if new_events:
            self._last_seq = new_events[-1].seq
        return new_events

    def poll_forever(self, interval_seconds: float = 0.5) -> Iterator[OverwolfEvent]:
        """Yield new events forever, polling the file on an interval."""
        while True:
            yield from self.read_new()
            time.sleep(interval_seconds)
