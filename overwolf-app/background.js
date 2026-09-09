// TFT Game Events Proxy
//
// Subscribes to every documented TFT Game Events (GEP) feature and dumps
// the raw stream to a local JSON file. It does nothing else - no window is
// shown, no input is sent to the game, nothing is uploaded anywhere. A
// separate, non-Overwolf application (e.g. a Python script) is expected to
// read that file. See README.md in this folder for the exact contract.
//
// Built against Overwolf's official TFT events sample
// (github.com/overwolf/events-sample-apps/tree/master/tft-events-sample-app)
// and the documented overwolf.io.writeFileContents signature. One spot is
// best-effort rather than verified against current docs: OUTPUT_PATH below
// depends on `overwolf.io.paths.documents` existing on your Overwolf client
// version - see the fallback logging if it doesn't.

// TFT's Overwolf game/class id has moved at least once as Riot split TFT
// out from the League client (5426 = legacy/shared LoL id used in Overwolf's
// own TFT sample app; 21570 = TFT's current dedicated id per Overwolf's
// docs at time of writing). Both are targeted so this keeps working either
// way - if Overwolf's Games IDs page (dev.overwolf.com) lists a different
// value by the time you read this, add it here.
var TFT_CLASS_IDS = [5426, 21570];

// The full feature set TFT's GEP integration documents. Requesting only
// what you need is the recommended practice, but since the point of this
// app is to proxy *everything* to an external consumer, we ask for all of
// it and let the downstream app decide what matters.
var FEATURES = [
  "counters",
  "match_info",
  "me",
  "roster",
  "store",
  "board",
  "bench",
  "carousel",
  "live_client_data",
  "augments",
  "game_info",
];

var OUTPUT_SUBPATH = "TFTEventsProxy\\events.json";
var MAX_BUFFER_ENTRIES = 5000;
var WRITE_DEBOUNCE_MS = 200;

var g_buffer = [];
var g_nextSeq = 1;
var g_writeTimer = null;
var g_outputPath = null;

function resolveOutputPath() {
  try {
    if (overwolf.io && overwolf.io.paths && overwolf.io.paths.documents) {
      return overwolf.io.paths.documents + "\\" + OUTPUT_SUBPATH;
    }
  } catch (e) {
    // fall through to the error below
  }
  console.error(
    "[TFTEventsProxy] Could not resolve overwolf.io.paths.documents on this " +
      "Overwolf client version. Open this app's dev console, inspect " +
      "`overwolf.io.paths`, and hardcode a working absolute path into " +
      "OUTPUT_SUBPATH/resolveOutputPath() in background.js."
  );
  return null;
}

function recordEntry(kind, payload) {
  g_buffer.push({ seq: g_nextSeq++, ts: Date.now(), kind: kind, payload: payload });
  if (g_buffer.length > MAX_BUFFER_ENTRIES) {
    g_buffer.splice(0, g_buffer.length - MAX_BUFFER_ENTRIES);
  }
  scheduleWrite();
}

function scheduleWrite() {
  if (g_writeTimer) {
    return;
  }
  g_writeTimer = setTimeout(function () {
    g_writeTimer = null;
    writeBufferToDisk();
  }, WRITE_DEBOUNCE_MS);
}

function writeBufferToDisk() {
  if (!g_outputPath) {
    return;
  }
  var content = JSON.stringify(g_buffer);
  overwolf.io.writeFileContents(
    g_outputPath,
    content,
    overwolf.io.enums.eEncoding.UTF8,
    false,
    function (result) {
      if (!result || !result.success) {
        console.error("[TFTEventsProxy] Failed writing events file: " + JSON.stringify(result));
      }
    }
  );
}

var onErrorListener, onInfoUpdates2Listener, onNewEventsListener;

function registerEvents() {
  onErrorListener = function (info) {
    recordEntry("error", info);
  };

  onInfoUpdates2Listener = function (info) {
    // Fires for "static"/slow-changing data (roster, match_info, etc.) and
    // once immediately with the full current state when we first register.
    recordEntry("info_update", info);
  };

  onNewEventsListener = function (info) {
    // Fires for discrete events (augment offered, round outcome, etc.).
    recordEntry("event", info);
  };

  overwolf.games.events.onError.addListener(onErrorListener);
  overwolf.games.events.onInfoUpdates2.addListener(onInfoUpdates2Listener);
  overwolf.games.events.onNewEvents.addListener(onNewEventsListener);
}

function unregisterEvents() {
  overwolf.games.events.onError.removeListener(onErrorListener);
  overwolf.games.events.onInfoUpdates2.removeListener(onInfoUpdates2Listener);
  overwolf.games.events.onNewEvents.removeListener(onNewEventsListener);
}

function classIdOf(gameInfo) {
  // Overwolf running-game ids encode a sequence number in the low digit;
  // dividing by 10 recovers the base class id.
  return Math.floor(gameInfo.id / 10);
}

function gameLaunched(gameInfoResult) {
  if (!gameInfoResult || !gameInfoResult.gameInfo) return false;
  if (!gameInfoResult.runningChanged && !gameInfoResult.gameChanged) return false;
  if (!gameInfoResult.gameInfo.isRunning) return false;
  return TFT_CLASS_IDS.indexOf(classIdOf(gameInfoResult.gameInfo)) !== -1;
}

function gameRunning(gameInfo) {
  if (!gameInfo || !gameInfo.isRunning) return false;
  return TFT_CLASS_IDS.indexOf(classIdOf(gameInfo)) !== -1;
}

function setFeatures() {
  overwolf.games.events.setRequiredFeatures(FEATURES, function (info) {
    if (info.status === "error") {
      // The game process may not have fully attached the events provider
      // yet right after launch - retry until it succeeds.
      window.setTimeout(setFeatures, 2000);
      return;
    }
    console.log("[TFTEventsProxy] Subscribed to features: " + JSON.stringify(info));
  });
}

function start() {
  g_outputPath = resolveOutputPath();
  if (g_outputPath) {
    console.log("[TFTEventsProxy] Writing events to: " + g_outputPath);
  }

  overwolf.games.onGameInfoUpdated.addListener(function (res) {
    if (gameLaunched(res)) {
      unregisterEvents();
      registerEvents();
      setTimeout(setFeatures, 1000);
    }
  });

  overwolf.games.getRunningGameInfo(function (res) {
    if (gameRunning(res)) {
      registerEvents();
      setTimeout(setFeatures, 1000);
    }
  });
}

start();
