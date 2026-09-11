"""Bridges Overwolf's `consumer.exe` (game-events-sdk diagnostic tool)
into this project's existing relay server + dashboard
(tft/overwolf_server.py, webapp/index.html) - same downstream pipeline,
fed from a source that needs no Overwolf app, no app-store whitelisting:
a plain console tool anyone can run.

Two modes:

    python -m tools.consumer_bridge --exe path\\to\\consumer.exe [--game-id 10054261]
        Launches consumer.exe with TFT's game id as its one required
        argument (found empirically: it exits immediately printing
        "Missing parameter: [game id]" if omitted - not documented
        anywhere by Overwolf), reads its stdout live, streams parsed
        records to the relay server, and periodically saves them to a
        durable local JSON file under consumer_bridge_output/ - one file
        per (match, stage), named "match-<id>_stage-<stage>.json", so a
        long play session doesn't grow into one ever-larger file. Each
        match gets a short random id (there's no dedicated match-boundary
        event in TFT's stream to key off of).

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
import re
import subprocess
import time
import uuid
from collections.abc import Iterable, Iterator
from pathlib import Path

import aiohttp

from tft.consumer_log_parser import Disconnected, GameEvent, InfoUpdate, ParsedRecord, parse_lines

WS_URL = "ws://localhost:8765/ws"
OUTPUT_DIR = Path("consumer_bridge_output")
MAX_BUFFER_ENTRIES = 5000
SAVE_EVERY_N_RECORDS = 5

_STAGE_RE = re.compile(r"^(\d+)-(\d+)$")
_UNSAFE_FILENAME_CHARS = re.compile(r"[^A-Za-z0-9_.-]")


def _parse_stage(stage: object) -> tuple[int, int] | None:
    """tft_round's "stage" field is a plain "main-sub" string (e.g. "6-2"),
    confirmed against a real captured session - parsed into a sortable
    tuple so a stage going backwards (e.g. 6-6 -> 1-1) can be detected as
    a new match, not just a stage."""
    match = _STAGE_RE.match(stage) if isinstance(stage, str) else None
    return (int(match.group(1)), int(match.group(2))) if match else None


def _safe_filename_part(text: str) -> str:
    return _UNSAFE_FILENAME_CHARS.sub("_", text)

try:
    _WS_CONNECT_TIMEOUT = aiohttp.ClientWSTimeout(ws_close=3)
except AttributeError:  # older aiohttp without ClientWSTimeout
    _WS_CONNECT_TIMEOUT = 3

RECONNECT_COOLDOWN_SECONDS = 3


class RelaySender:
    """Sends entries to the relay server, reconnecting on demand instead
    of giving up permanently after the first failed/lost connection - the
    relay server (or this bridge) restarting mid-session shouldn't require
    restarting the other one too."""

    def __init__(self, session: aiohttp.ClientSession):
        self._session = session
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._last_attempt = 0.0
        self.just_reconnected = False

    async def _ensure_connected(self) -> bool:
        if self._ws is not None and not self._ws.closed:
            return True
        now = time.monotonic()
        if now - self._last_attempt < RECONNECT_COOLDOWN_SECONDS:
            return False  # tried recently, don't hammer a server that's down
        self._last_attempt = now
        try:
            self._ws = await self._session.ws_connect(WS_URL, timeout=_WS_CONNECT_TIMEOUT)
            print(f"Streaming live to {WS_URL}")
            self.just_reconnected = True
            return True
        except Exception:
            self._ws = None
            return False

    async def send(self, entry: dict, history_before: list[dict] | None = None) -> bool:
        """Sends `entry`. If this call is what (re)established the
        connection, first replays `history_before` (in order, ahead of
        `entry`) - so the dashboard catches up immediately on reconnect
        instead of sitting blank until the next sparse game event, even
        though the bridge itself has been working fine the whole time."""
        was_connected = self._ws is not None and not self._ws.closed
        if not await self._ensure_connected():
            return False
        try:
            if self.just_reconnected:
                self.just_reconnected = False
                if history_before:
                    print(f"Backfilling {len(history_before)} entries to the relay server...")
                    for old_entry in history_before:
                        await self._ws.send_str(json.dumps(old_entry))
            await self._ws.send_str(json.dumps(entry))
            return True
        except Exception:
            if was_connected:
                print("Lost connection to relay server; will keep retrying in the background.")
            self._ws = None
            return False

    async def close(self) -> None:
        if self._ws is not None:
            await self._ws.close()


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
    """Buffers parsed entries for two separate purposes: `_buffer` is the
    live-relay backfill history (unaffected by match/stage boundaries,
    capped at MAX_BUFFER_ENTRIES like before), and `_stage_buffer` is what
    gets saved to disk - one file per (match, stage), so a long play
    session doesn't grow into a single ever-larger JSON file.

    TFT's events stream has no dedicated match-boundary event to key off
    of - the one real captured session this project has only ever emits
    tft_match="match_end", never "match_start" - so a new match is
    detected two ways: seeing "match_end" (closes out the current
    match's last stage file; the next record starts a fresh match_id),
    or a new stage sorting *before* the previous one (e.g. 6-6 -> 1-1),
    which covers a bridge started mid-match or a session where match_end
    is missed. Each match gets a short random id in its filename so
    consecutive matches in the same run (or overlapping runs) never
    collide or overwrite each other."""

    def __init__(self):
        self._buffer: list[dict] = []
        self._next_seq = 1
        self._match_id = uuid.uuid4().hex[:8]
        self._stage_label = "pre-stage"
        self._stage_sort_key: tuple[int, int] | None = None
        self._stage_buffer: list[dict] = []
        self._match_ended = False

    def _start_new_match(self) -> None:
        self.save_stage()
        self._match_id = uuid.uuid4().hex[:8]
        self._stage_label = "pre-stage"
        self._stage_sort_key = None
        self._stage_buffer = []

    def _start_new_stage(self, stage_label: str, stage_sort_key: tuple[int, int] | None) -> None:
        self.save_stage()
        self._stage_label = stage_label
        self._stage_sort_key = stage_sort_key
        self._stage_buffer = []

    def _handle_transition(self, record: ParsedRecord) -> None:
        if self._match_ended:
            self._match_ended = False
            self._start_new_match()
        if not isinstance(record, InfoUpdate):
            return
        if record.key == "tft_match" and record.value == "match_end":
            # This record itself still belongs to the ending match/stage
            # (appended below, in make_entry) - the reset happens on the
            # *next* call so match_end lands in the right file.
            self._match_ended = True
            return
        if record.key == "tft_round" and isinstance(record.value, dict):
            stage = record.value.get("stage")
            if not stage or stage == self._stage_label:
                return
            sort_key = _parse_stage(stage)
            went_backwards = (
                sort_key is not None and self._stage_sort_key is not None and sort_key < self._stage_sort_key
            )
            if went_backwards:
                self._start_new_match()
            self._start_new_stage(stage, sort_key)

    def make_entry(self, record: ParsedRecord) -> dict:
        self._handle_transition(record)
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
        self._stage_buffer.append(entry)
        return entry

    @property
    def entry_count(self) -> int:
        return len(self._buffer)

    @property
    def entries(self) -> list[dict]:
        return list(self._buffer)

    @property
    def stage_path(self) -> Path:
        return OUTPUT_DIR / f"match-{self._match_id}_stage-{_safe_filename_part(self._stage_label)}.json"

    def save_stage(self) -> None:
        if not self._stage_buffer:
            return
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.stage_path.write_text(json.dumps(self._stage_buffer), encoding="utf-8")


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
    sender = RelaySender(session)
    try:
        count = 0
        try:
            for record in parse_lines(_tap_lines(lines_iter, verbose)):
                entry = bridge.make_entry(record)
                print(f"[{entry['kind']}] {entry['payload']}")
                # best-effort; self-reconnects (with backfill) if the relay comes back
                await sender.send(entry, history_before=bridge.entries[:-1])
                count += 1
                if count % SAVE_EVERY_N_RECORDS == 0:
                    bridge.save_stage()
        finally:
            bridge.save_stage()
            print(f"\nSaved {count} entries this run; most recent stage file: {bridge.stage_path}")
    finally:
        await sender.close()
        await session.close()


def iter_subprocess_lines(exe_path: Path, game_id: int) -> Iterator[str]:
    print(f"Launching {exe_path} {game_id} ...")
    process = subprocess.Popen(
        [str(exe_path), str(game_id)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",  # consumer.exe's output isn't guaranteed to match the OS's default codepage
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
        default=10054261,
        help="TFT's Overwolf running-game id, passed to consumer.exe (default: 10054261, "
        "confirmed working empirically - Overwolf's docs suggested 21570 or 5426 as the "
        "base class id, but consumer.exe wants the full running-instance id instead).",
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
