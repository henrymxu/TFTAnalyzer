# TFTAnalyzer

A read-only, programmatic interface to Teamfight Tactics data, meant as the
"senses" layer for building analysis tools or, eventually, a decision-making
AI. It has three independent pieces:

1. **`tft.riot_api`** - a client for the official [Riot Games API](https://developer.riotgames.com/):
   account lookup, ranked stats, and match history. Fully within Riot's ToS.
2. **`tft.vision`** - an optional local screen reader (screen capture + OCR +
   template matching) that reconstructs *your own* live in-match state (gold,
   level, shop, board) by reading pixels off your screen.
3. **`tools/consumer_bridge.py` + `tft/overwolf_server.py` + `webapp/`** - the
   richest live data source: Overwolf's own TFT Game Events feed (board, bench,
   shop, augments, roster, damage, etc), read via `consumer.exe` - a small
   diagnostic tool Overwolf publishes as part of their `game-events-sdk`, which
   needs no Overwolf app, no app-store submission, and no developer whitelisting.
   See "Live TFT game events" below.

**There is no code anywhere in this repo that sends input to the game** - no
mouse movement, no key presses, no memory injection. `tft.vision` only reads;
it has no write half. That's intentional: Riot's Terms of Service prohibit
bots/scripts that act in live matches, and an agent that plays ranked games
unattended is effectively cheating against real opponents. If your goal is an
AI that plays TFT, the recommended path is:

- Use `tft.riot_api` + `tft.vision` to observe state (this repo).
- Build/train your decision-making logic against a **local TFT simulator**
  instead of the live client - the standard approach for game-playing agents
  (comparable to how Dota/StarCraft bots are trained offline before any
  online use). That simulator is a separate, larger project from this one.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt   # or requirements.txt for runtime-only
cp .env.example .env                  # then fill in RIOT_API_KEY
```

`tft.vision` also needs the [Tesseract OCR engine](https://github.com/UB-Mannheim/tesseract/wiki)
installed and on your `PATH` (only required if you use live screen reading).

## Riot API usage

```bash
python -m examples.match_history_example "GameName#TAG"
```

```python
from tft import TFTInterface

tft = TFTInterface()
puuid = tft.get_puuid("GameName", "TAG")
print(tft.get_ranked_stats(puuid))
for match in tft.get_match_history(puuid, count=10):
    print(match.match_id, match.participant(puuid).placement)
```

## Live screen state (optional)

This part is resolution/UI-scale specific, so it needs one-time calibration
per machine:

```bash
python -m tools.fetch_templates       # downloads champion icons for shop recognition
python -m tools.calibrate_regions     # draw boxes around gold/level/shop/etc on your screen
python -m tools.debug_capture         # sanity-check: saves each region as a PNG + prints raw OCR text
python -m examples.live_state_example # prints a read-only snapshot once per second
```

If a value comes back wrong or `None`, run `tools.debug_capture` first - it saves
exactly what was captured for each region to `.tft_cache/debug_captures/*.png`
and prints the raw OCR text before parsing, which is almost always faster
than guessing from `live_state_example`'s output alone. Common fixes: redraw
the region tighter around just the digits/icon, or increase your UI scale so
small text isn't too blurry for OCR.

```python
from tft import TFTInterface

tft = TFTInterface()
tft.enable_live_reading("regions.local.json")
state = tft.capture_live_state()
print(state.hud.gold, state.hud.level, [s.champion_name for s in state.shop])
```

Recognition accuracy depends entirely on your calibration and template
quality - this is a best-effort computer-vision pipeline, not a guaranteed
readout, and shop/board recognition will need retemplating each time a new
set changes champion art.

## Live TFT game events (richest live data, no Overwolf app needed)

Riot's own API has no live in-match data, and screen-reading is inherently
approximate. Overwolf maintains its own TFT integration with much richer
data (board, bench, shop, augments, roster, per-fight damage) - normally
that's only exposed to apps built and whitelisted on their platform, which
requires an application/review process even for personal, local use.

Overwolf separately publishes [`game-events-sdk`](https://github.com/overwolf/game-events-sdk),
a toolkit for *game developers* to test their own instrumentation. It ships
`consumer.exe`, a standalone diagnostic tool that prints the exact same live
event feed to plain text - independent of the Overwolf client, any app,
or whitelisting. Real field names, captured from an actual TFT session and
now covered by `tft/consumer_log_parser.py`'s tests:

`tft_gold`, `tft_xp`, `tft_round`, `tft_match`, `tft_combat`, `tft_opp`,
`tft_shop`, `tft_board`, `tft_bench`, `tft_board_opponent`, `tft_board_players`,
`tft_roster`, `tft_item_select` (augments/item choices), `tft_carousel`,
`tft_round_outcome`, `tft_item_bench`, `tft_damage`, `tft_damage_tracker` -
all under an info-db category of `game_info`, plus discrete events like
`tft_shop_visible`.

Pipeline: `consumer.exe` (Windows-only, produces plain text) →
`tools/consumer_bridge.py` (parses it, streams to the relay server, saves
a durable JSON file) → `tft/overwolf_server.py` (relay + serves the
dashboard) → `webapp/index.html` (browser dashboard) - or read the JSON
file directly from Python via `tft.overwolf_bridge`.

```bash
# Terminal 1: the relay server + dashboard
python -m tft.overwolf_server
# open http://localhost:8765/ in a browser

# Terminal 2 (Windows, while in a TFT match): point at your consumer.exe
python -m tools.consumer_bridge --exe path\to\consumer.exe

# Or, to try the dashboard without a live game, replay a captured log:
python -m tools.consumer_bridge --replay path\to\captured_log.txt
```

This whole pipeline is tested end-to-end here, including replaying a real
captured TFT session (2806 lines, 602 parsed records) through the parser,
bridge, relay server, and dashboard in a headless browser - gold, level,
stage, shop, board, bench, roster with health bars, augment choices,
carousel, and round outcomes all render correctly from real data, not
guesses. What's still unverified is `consumer.exe` itself against *your*
TFT session (its command-line behavior isn't documented by Overwolf - see
`tools/consumer_bridge.py`'s docstring for the `--exe` vs `--replay` split).

**`overwolf-app/`** (an actual Overwolf app using `overwolf.games.events`)
is kept in this repo but is no longer the recommended path, since it
requires applying for Overwolf's developer whitelist even for personal use
- see `overwolf-app/README.md` if you want that route instead.

## Project layout

```
tft/
  riot_api/               Riot API client, rate limiting, exceptions
  static_data/            Community Dragon set data (champions/traits/items) + icon downloads
  models/                 Typed dataclasses for match history and live game state
  vision/                 Screen capture, OCR, template matching, live state reader
  consumer_log_parser.py  Parses consumer.exe's plain-text output into structured records
  overwolf_bridge.py      Reads the durable JSON file the bridge/Overwolf app writes
  overwolf_server.py      Relay server: WebSocket stream -> browser dashboard
  interface.py            TFTInterface - the top-level facade
webapp/           Browser dashboard served by tft.overwolf_server
overwolf-app/     Alternative: an actual Overwolf app (requires dev whitelisting - see its README)
tools/            One-off scripts: consumer_bridge.py, calibrate_regions.py, fetch_templates.py, debug_capture.py
examples/         Runnable usage examples
tests/            Unit tests (mocked network, synthetic images, in-process server - no live game needed)
```

## Running tests

```bash
python -m pytest
```
