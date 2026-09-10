# TFTAnalyzer

A read-only, programmatic interface to Teamfight Tactics data, meant as the
"senses" layer for building analysis tools or, eventually, a decision-making
AI. It has three independent pieces:

1. **`tft.riot_api`** - a client for the official [Riot Games API](https://developer.riotgames.com/):
   account lookup, ranked stats, and match history. Fully within Riot's ToS.
2. **`tft.vision`** - an optional local screen reader (screen capture + OCR +
   template matching) that reconstructs *your own* live in-match state (gold,
   level, shop, board) by reading pixels off your screen.
3. **`overwolf-app/` + `tft.overwolf_bridge`** - an optional Overwolf app that
   proxies Overwolf's own live TFT Game Events feed (board/bench/shop/augments/etc,
   richer than what vision or the Riot API can see) to a local JSON file, plus a
   Python reader for it. See `overwolf-app/README.md`.

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

## Overwolf game events (optional, richest live data)

Riot's own API has no live in-match data, and screen-reading is inherently
approximate. [Overwolf](https://www.overwolf.com/) maintains its own TFT
integration (board, bench, shop, augments, roster - see `overwolf-app/README.md`
for the full feature list) that's much more complete, but it's only exposed to
apps built on their platform. `overwolf-app/` is a minimal, headless Overwolf
app that subscribes to everything TFT's GEP integration offers, and gives you
two ways to consume it:

1. **File** - every entry is written to a local JSON file;
   `tft.overwolf_bridge` reads that from plain Python (`examples/overwolf_events_example.py`).
2. **Live stream** - every entry is also pushed over a WebSocket to
   `tft/overwolf_server.py`, a small relay server that re-broadcasts it to
   `webapp/index.html`, a browser dashboard with a raw event log and a
   best-effort "recreated state" view (gold/level/health, shop/board/bench
   slots) parsed generically from whatever fields TFT's events actually send.

```bash
# Terminal 1: the relay server + dashboard
python -m tft.overwolf_server
# open http://localhost:8765/ in a browser

# One-time: load overwolf-app/ as an unpacked app in Overwolf's dev tools
# (see overwolf-app/README.md), then with TFT running, both the file and
# the dashboard above should start filling in. Or, without a browser:
python -m examples.overwolf_events_example
```

The relay server + dashboard (`tft/overwolf_server.py`, `webapp/index.html`)
are tested end-to-end here, including a real headless-browser run against
sample payloads shaped like TFT's actual `match_info`/`me` events - the
server, the streaming protocol, and the dashboard's rendering logic all
work. What is **not** verified against a live game (no TFT/Overwolf install
available here) is the Overwolf app itself producing that stream in the
first place - see the "best-effort" notes in `overwolf-app/README.md` about
the two spots (output path resolution, TFT's current game id) that may need
a manual fix depending on your Overwolf client version. The "recreated
state" panel's gold/level/shop guesses are also best-effort until tested
against real payloads - it'll show raw JSON instead of a clean readout for
anything it doesn't recognize.

## Project layout

```
tft/
  riot_api/          Riot API client, rate limiting, exceptions
  static_data/       Community Dragon set data (champions/traits/items) + icon downloads
  models/            Typed dataclasses for match history and live game state
  vision/            Screen capture, OCR, template matching, live state reader
  overwolf_bridge.py Reader for the Overwolf proxy app's event file
  overwolf_server.py Relay server: Overwolf app's WebSocket stream -> browser dashboard
  interface.py       TFTInterface - the top-level facade
overwolf-app/     Headless Overwolf app that proxies TFT Game Events (file + WebSocket)
webapp/           Browser dashboard served by tft.overwolf_server
tools/            One-off scripts: calibrate_regions.py, fetch_templates.py, debug_capture.py
examples/         Runnable usage examples
tests/            Unit tests (mocked network, synthetic images, in-process server - no live game needed)
```

## Running tests

```bash
python -m pytest
```
