# TFTAnalyzer

A read-only, programmatic interface to Teamfight Tactics data, meant as the
"senses" layer for building analysis tools or, eventually, a decision-making
AI. It has two independent pieces:

1. **`tft.riot_api`** - a client for the official [Riot Games API](https://developer.riotgames.com/):
   account lookup, ranked stats, and match history. Fully within Riot's ToS.
2. **`tft.vision`** - an optional local screen reader (screen capture + OCR +
   template matching) that reconstructs *your own* live in-match state (gold,
   level, shop, board) by reading pixels off your screen.

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
python -m examples.live_state_example # prints a read-only snapshot once per second
```

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

## Project layout

```
tft/
  riot_api/       Riot API client, rate limiting, exceptions
  static_data/    Community Dragon set data (champions/traits/items) + icon downloads
  models/         Typed dataclasses for match history and live game state
  vision/         Screen capture, OCR, template matching, live state reader
  interface.py    TFTInterface - the top-level facade
tools/            One-off scripts: calibrate_regions.py, fetch_templates.py
examples/         Runnable usage examples
tests/            Unit tests (mocked network, synthetic images - no live game needed)
```

## Running tests

```bash
python -m pytest
```
