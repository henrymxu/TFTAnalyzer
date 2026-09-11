"""Parses the plain-text console output of Overwolf's game-events-sdk
`consumer.exe` diagnostic tool into structured records.

This format isn't documented anywhere by Overwolf - it was reverse
engineered from an actual captured TFT session (see
tests/test_consumer_log_parser.py, built from real captured lines). It
looks like:

    -------------------------
    Received 2 new info db updates:

    <game_info, tft_gold>: 56

    <game_info, tft_xp>: {"xp_level":"10", "xp_progress":"0", "xp_progress_max":"2"}

    -------------------------

and, for discrete events:

    -------------------------
    Received 1 new events:

    Name: tft_shop_visible
    Data: false

    -------------------------

and a final, one-line disconnect notice:

    Game events controller is now disconnected!
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Any, Union

_INFO_HEADER_RE = re.compile(r"^Received \d+ new info db updates:$")
_EVENTS_HEADER_RE = re.compile(r"^Received \d+ new events:$")
_SEPARATOR_RE = re.compile(r"^-{3,}$")
_INFO_LINE_RE = re.compile(r"^<([^,>]+),\s*([^>]+)>:\s?(.*)$")
_NAME_LINE_RE = re.compile(r"^Name:\s?(.*)$")
_DATA_LINE_RE = re.compile(r"^Data:\s?(.*)$")
_DISCONNECT_LINE = "Game events controller is now disconnected!"


@dataclass(frozen=True)
class InfoUpdate:
    category: str
    key: str
    value: Any


@dataclass(frozen=True)
class GameEvent:
    name: str
    value: Any


@dataclass(frozen=True)
class Disconnected:
    pass


ParsedRecord = Union[InfoUpdate, GameEvent, Disconnected]


def _parse_value(raw: str) -> Any:
    """Values are usually JSON (objects, arrays, quoted strings, bare
    numbers) but sometimes a bare unquoted word like `match_end` - which
    isn't valid JSON, so it's kept as a plain string instead."""
    raw = raw.strip()
    if raw == "":
        return None
    try:
        return json.loads(raw)
    except ValueError:
        return raw


def parse_lines(lines: Iterable[str]) -> Iterator[ParsedRecord]:
    """Streams ParsedRecord objects out of raw consumer.exe output lines."""
    mode: str | None = None  # "info" | "events" | None
    pending_name: str | None = None

    for raw_line in lines:
        stripped = raw_line.rstrip("\r\n").strip()

        if stripped == _DISCONNECT_LINE:
            yield Disconnected()
            mode = None
            pending_name = None
            continue

        if _SEPARATOR_RE.match(stripped):
            mode = None
            pending_name = None
            continue

        if not stripped:
            continue

        if _INFO_HEADER_RE.match(stripped):
            mode = "info"
            continue

        if _EVENTS_HEADER_RE.match(stripped):
            mode = "events"
            continue

        if mode == "info":
            match = _INFO_LINE_RE.match(stripped)
            if match:
                category, key, value = match.groups()
                yield InfoUpdate(category=category.strip(), key=key.strip(), value=_parse_value(value))
            continue

        if mode == "events":
            match = _NAME_LINE_RE.match(stripped)
            if match:
                pending_name = match.group(1).strip()
                continue
            match = _DATA_LINE_RE.match(stripped)
            if match and pending_name is not None:
                yield GameEvent(name=pending_name, value=_parse_value(match.group(1)))
                pending_name = None
            continue


def parse_text(text: str) -> Iterator[ParsedRecord]:
    return parse_lines(text.splitlines())
