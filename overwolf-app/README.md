# TFT Game Events Proxy (Overwolf app)

A minimal, headless Overwolf app that subscribes to every documented TFT
Game Events (GEP) feature and both (a) writes the raw stream to a local
JSON file and (b) streams it live over a plain WebSocket. It has no window,
no UI, and does not send any input to the game - it's purely a bridge so a
completely separate application (this repo's Python package, a browser
dashboard, or anything else) can consume live TFT match data without
reimplementing Overwolf's game integration itself.

## Why this exists

Riot's own API has no live in-match data (see the main README). Overwolf
maintains its own TFT integration that *does* expose live state - board,
bench, shop, augments, roster, etc. - but only to apps built on their
platform. This app is that thin platform-side piece; everything else
(decision logic, storage, UI) can live in ordinary Python/whatever, reading
the file this app writes.

## What gets written, and where

Every GEP callback (`onNewEvents`, `onInfoUpdates2`, `onError`) is appended
to an in-memory buffer (capped at the last 5000 entries) and the whole
buffer is rewritten as one JSON array to:

```
<Documents folder>\TFTEventsProxy\events.json
```

Each entry looks like:

```json
{
  "seq": 42,
  "ts": 1735689600000,
  "kind": "event",
  "payload": { "..." : "whatever overwolf.games.events handed us" }
}
```

- `kind` is `"event"` (from `onNewEvents`), `"info_update"` (from
  `onInfoUpdates2` - fires with the full current state on first
  subscription, then on any change to slower-moving data), or `"error"`.
- `seq` is a monotonically increasing counter for this app session, so a
  consumer can poll the file and only process entries past the highest
  `seq` it's already seen.

A consumer (see `../examples/overwolf_events_example.py` and
`../tft/overwolf_bridge.py`) just polls/reads that file - no Overwolf SDK,
no special permissions, nothing game-specific required on that side.

## Live streaming (the webapp dashboard)

Independently of the file above, every entry is also pushed out over a
plain `WebSocket` (deliberately the native browser API, not
`overwolf.web.createWebSocket` - Overwolf's own docs recommend the native
one unless you need to bypass TLS cert checks for a `wss://` server, which
doesn't apply here) to `ws://localhost:8765/ws`. That's the address of
`tft/overwolf_server.py` (see the main README) - a small relay + static
file server this repo also provides, which re-broadcasts whatever it
receives to any connected browser tab running `webapp/index.html`.

This is a best-effort, live-only tap: if `tft.overwolf_server` isn't
running yet, or briefly drops, `background.js` just retries the connection
every 3 seconds and silently drops anything that couldn't be sent in the
meantime - `events.json` above is unaffected and remains the complete,
durable record regardless of whether anything was ever streamed live.

**One spot here is best-effort, not verified**: resolving the Documents
folder path relies on `overwolf.io.paths.documents` existing on your
Overwolf client version. If nothing shows up in the output file, open this
app's dev console (right-click the (invisible) app while it's running →
there should be a dev tools option in Overwolf's own tray/dev menu) and
check the console log line printed on startup - `background.js` will log an
explicit error there telling you to inspect `overwolf.io.paths` and
hardcode a working path if that property isn't there.

## Loading it

1. Install the [Overwolf client](https://www.overwolf.com/) if you don't
   have it, and enable Developer mode (Settings → About → toggle Developer
   Options, or via the "Dev Tools" tray icon).
2. Overwolf's dev tools → "Load unpacked extension" → point it at this
   `overwolf-app/` folder (the one containing `manifest.json`).
3. Launch TFT. Overwolf should detect it (per `game_targeting`/`game_events`
   in the manifest) and load this app in the background - no visible
   window will appear, by design.
4. Check `%USERPROFILE%\Documents\TFTEventsProxy\events.json` for output.

## Verifying TFT's current Overwolf game id

TFT's Overwolf class id has changed over time (see the comment at the top
of `background.js`). If events aren't showing up at all even though the
app loaded, check the current value on Overwolf's own
[Games IDs page](https://dev.overwolf.com/ow-native/guides/dev-tools/games-ids/)
and add it to `TFT_CLASS_IDS` in `background.js` and `game_ids`/`game_events`
in `manifest.json` if it's changed again.

## What this does *not* do

No mouse/keyboard input, no memory writes, no network calls - it only
subscribes to Overwolf's own read-only game-events feed and writes it to a
file on disk. Building automation on top of the data this exposes would be
a separate, much riskier decision (see the ToS discussion in the main
project README) - this app itself is just a data tap.
