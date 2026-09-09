"""Prints every new TFT game event as it's written by the Overwolf proxy
app (see overwolf-app/). Requires Overwolf running with that app loaded
and TFT running - this script itself never touches the Overwolf SDK, it
just polls a JSON file on disk.

Usage:
    python -m examples.overwolf_events_example [path-to-events.json]
"""

from __future__ import annotations

import sys
from pathlib import Path

from tft.overwolf_bridge import OverwolfEventReader, default_events_path


def main() -> None:
    events_path = Path(sys.argv[1]) if len(sys.argv) > 1 else default_events_path()
    print(f"Watching {events_path} ... Ctrl+C to stop")

    reader = OverwolfEventReader(events_path)
    try:
        for event in reader.poll_forever():
            print(f"[{event.kind}] {event.payload}")
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
