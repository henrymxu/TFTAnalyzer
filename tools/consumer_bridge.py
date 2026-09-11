"""Bridges Overwolf's `consumer.exe` (game-events-sdk diagnostic tool)
into this project's existing relay server + dashboard
(tft/overwolf_server.py, webapp/index.html) - same downstream pipeline,
fed from a source that needs no Overwolf app, no app-store whitelisting:
a plain console tool anyone can run.

Two modes:

    python -m tools.consumer_bridge --exe path\\to\\consumer.exe [--game-id 21570]
        Launches consumer.exe with TFT's game id as its one required
        argument (found empirically: it exits immediately printing
        "Missing parameter: [game id]" if omitted - not documented
        anywhere by Overwolf), reads its stdout live, streams parsed
        records to the relay server, and periodically saves them to a
        local JSON file (durable record, same role events.json played
        in the Overwolf-app version of this pipeline).

    python -m tools.consumer_bridge --replay path\\to\\captured_log.txt
        Replays a previously captured text log (e.g. output you saved
        from consumer.exe) through the same pipeline, for testing the
        dashboard without needing to be in a live game.

Either way, start tft.overwolf_server first (`python -m tft.overwolf_server`)
so there's something listening at ws://localhost:8765/ws - if it's not
running, this still saves everything to disk, it just won't stream live.

Add --verbose to either mode to print every raw line received before
parsing - useful if nothing seems to be happening, since it distinguishes
"the source produced no output at all" (e.g. consumer.exe exiting
immediately - often a missing DLL) from "output arrived but didn't match
the expected format".
"""

from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import time
from collections.abc import Iterable, Iterator
from pathlib import Path

import aiohttp

from tft.consumer_log_parser import Disconnected, GameEvent, InfoUpdate, ParsedRecord, parse_lines

WS_URL = "ws://localhost:8765/ws"
OUTPUT_PATH = Path("consumer_bridge_output/events.json")
MAX_BUFFER_ENTRIES = 5000
SAVE_EVERY_N_RECORDS = 5

try:
    _WS_CONNECT_TIMEOUT = aiohttp.ClientWSTimeout(ws_close=3)
except AttributeError:  # older aiohttp without ClientWSTimeout
    _WS_CONNECT_TIMEOUT = 3


def _to_payload(record: ParsedRecord) -> dict:
    if isinstance(record, InfoUpdate):
        return {"category": record.category, "key": record.key, "value": record.value}
    if isinstance(record, GameEvent):
        return {"name": record.name, "value": record.value}
    return {"state": "disconnected"}


def _kind_of(record: ParsedRecord) -> str:
    if isinstance(record, InfoUpdate):
        return "info_update"
    if isinstance(record, GameEvent):
        return "event"
    return "lifecycle"


class Bridge:
    def __init__(self):
        self._buffer: list[dict] = []
        self._next_seq = 1

    def make_entry(self, record: ParsedRecord) -> dict:
        entry = {
            "seq": self._next_seq,
            "ts": int(time.time() * 1000),
            "kind": _kind_of(record),
            "payload": _to_payload(record),
        }
        self._next_seq += 1
        self._buffer.append(entry)
        if len(self._buffer) > MAX_BUFFER_ENTRIES:
            self._buffer = self._buffer[-MAX_BUFFER_ENTRIES:]
        return entry

    @property
    def entry_count(self) -> int:
        return len(self._buffer)

    def save(self) -> None:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(json.dumps(self._buffer), encoding="utf-8")


def _tap_lines(lines: Iterable[str], verbose: bool) -> Iterator[str]:
    """Passes lines through unchanged, optionally printing each raw line
    first - so a source that produces no parseable records is visibly
    different from one that produces no output at all."""
    saw_any = False
    for line in lines:
        saw_any = True
        if verbose:
            print(f"[raw] {line.rstrip()}")
        yield line
    if not saw_any:
        print(
            "\nNo output at all was received from the source before it ended. "
            "If using --exe, this usually means the process exited immediately "
            "(e.g. a missing dependency DLL, or it needs to be run from its own "
            "folder) - try running it directly, outside this bridge, and see what "
            "happens."
        )


async def run(lines_iter: Iterable[str], verbose: bool = False) -> None:
    bridge = Bridge()
    session = aiohttp.ClientSession()
    ws = None
    try:
        try:
            ws = await session.ws_connect(WS_URL, timeout=_WS_CONNECT_TIMEOUT)
            print(f"Streaming live to {WS_URL}")
        except Exception as exc:
            print(f"Could not connect to relay server ({exc}); saving to disk only.")

        count = 0
        try:
            for record in parse_lines(_tap_lines(lines_iter, verbose)):
                entry = bridge.make_entry(record)
                print(f"[{entry['kind']}] {entry['payload']}")
                if ws is not None:
                    try:
                        await ws.send_str(json.dumps(entry))
                    except Exception:
                        print("Lost connection to relay server; continuing to save to disk only.")
                        ws = None
                count += 1
                if count % SAVE_EVERY_N_RECORDS == 0:
                    bridge.save()
        finally:
            bridge.save()
            print(f"\nSaved {bridge.entry_count} entries to {OUTPUT_PATH}")
    finally:
        if ws is not None:
            await ws.close()
        await session.close()


def iter_subprocess_lines(exe_path: Path, game_id: int) -> Iterator[str]:
    print(f"Launching {exe_path} {game_id} ...")
    process = subprocess.Popen(
        [str(exe_path), str(game_id)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=exe_path.parent,  # some native tools expect their own DLLs alongside them
    )
    assert process.stdout is not None
    try:
        yield from process.stdout
    finally:
        process.terminate()
        returncode = process.wait(timeout=5)
        print(f"{exe_path.name} exited with code {returncode}")


def iter_file_lines(path: Path, delay_seconds: float = 0.0) -> Iterator[str]:
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if delay_seconds:
                time.sleep(delay_seconds)
            yield line


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--exe", type=Path, help="Path to consumer.exe to launch and read live.")
    group.add_argument("--replay", type=Path, help="Path to a previously captured text log to replay.")
    parser.add_argument(
        "--game-id",
        type=int,
        default=21570,
        help="TFT's Overwolf game/class id, passed to consumer.exe (default: 21570, "
        "TFT's current dedicated id per Overwolf's docs at time of writing - try 5426, "
        "the older shared League/TFT id, if that one comes back empty).",
    )
    parser.add_argument(
        "--replay-delay", type=float, default=0.0, help="Seconds to sleep between replayed lines (default: as fast as possible)."
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Print every raw line received before parsing, for troubleshooting."
    )
    args = parser.parse_args()

    lines_iter = (
        iter_subprocess_lines(args.exe, args.game_id) if args.exe else iter_file_lines(args.replay, args.replay_delay)
    )

    try:
        asyncio.run(run(lines_iter, verbose=args.verbose))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
