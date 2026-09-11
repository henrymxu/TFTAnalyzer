"""Local relay server: receives the Overwolf app's live event stream over
a plain WebSocket and re-broadcasts it to any connected browser tabs,
while also serving the small dashboard webapp (see webapp/index.html).

This is a separate concern from the durable events.json file the Overwolf
app writes directly to disk (see overwolf_bridge.py for reading that) -
this server is purely a live, in-memory relay for the webapp UI. If no
browser tab is connected when an event arrives, that event is simply not
seen live (though it's still in events.json, unaffected by this process).

Usage:
    python -m tft.overwolf_server
    # then open http://localhost:8765/ in a browser
"""

from __future__ import annotations

import asyncio
import logging
from collections import deque
from pathlib import Path

from aiohttp import WSMsgType, web

from tft.static_data.cdragon import CDragonClient

logger = logging.getLogger(__name__)

WEBAPP_DIR = Path(__file__).resolve().parent.parent / "webapp"
HISTORY_SIZE = 200
DEFAULT_PORT = 8765


class EventRelay:
    """Fans out messages to every connected client and replays recent
    history to new connections, so a tab opened mid-match isn't blank."""

    def __init__(self, history_size: int = HISTORY_SIZE):
        self._clients: set[web.WebSocketResponse] = set()
        self._history: deque[str] = deque(maxlen=history_size)

    async def register(self, ws: web.WebSocketResponse) -> None:
        self._clients.add(ws)
        for raw in self._history:
            await ws.send_str(raw)

    def unregister(self, ws: web.WebSocketResponse) -> None:
        self._clients.discard(ws)

    async def broadcast(self, raw: str) -> None:
        self._history.append(raw)
        stale = []
        for client in self._clients:
            try:
                await client.send_str(raw)
            except ConnectionResetError:
                stale.append(client)
        for client in stale:
            self._clients.discard(client)

    @property
    def client_count(self) -> int:
        return len(self._clients)


async def websocket_handler(request: web.Request) -> web.WebSocketResponse:
    relay: EventRelay = request.app["relay"]
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    await relay.register(ws)
    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                # Only the Overwolf app is expected to send anything; browser
                # clients are read-only. Re-broadcasting whatever arrives
                # keeps multiple open tabs in sync with each other too.
                await relay.broadcast(msg.data)
            elif msg.type == WSMsgType.ERROR:
                logger.warning("websocket closed with exception %s", ws.exception())
    finally:
        relay.unregister(ws)
    return ws


async def index_handler(request: web.Request) -> web.FileResponse:
    return web.FileResponse(WEBAPP_DIR / "index.html")


def build_name_maps(client: CDragonClient | None = None) -> dict:
    """Champion/item apiName -> {name, icon}, from the same Community
    Dragon source tft.static_data already uses - for prettifying the raw
    internal names (e.g. "TFT14_Draven", or PvE-variant names like
    "DA_Draven18") the game events stream carries, and for showing real
    icons instead of text. icon is a directly hotlinkable CDN URL (or
    None if the set data had no icon for that entry) - the browser loads
    it straight from Community Dragon, this server never proxies bytes.
    Degrades to empty maps (the webapp falls back to a heuristic name
    cleanup and text-only cells) rather than failing the request if
    Community Dragon isn't reachable."""
    client = client or CDragonClient()
    champions: dict[str, dict] = {}
    items: dict[str, dict] = {}
    try:
        for champ in client.get_champions():
            champions[champ.api_name.lower()] = {
                "name": champ.display_name,
                "icon": CDragonClient.icon_url(champ.icon_path) if champ.icon_path else None,
            }
    except Exception:
        logger.warning("Could not fetch champion names from Community Dragon", exc_info=True)
    try:
        for item in client.get_items():
            items[item.api_name.lower()] = {
                "name": item.display_name,
                "icon": CDragonClient.icon_url(item.icon_path) if item.icon_path else None,
            }
    except Exception:
        logger.warning("Could not fetch item names from Community Dragon", exc_info=True)
    return {"champions": champions, "items": items}


async def names_handler(request: web.Request) -> web.Response:
    cache: dict = request.app["name_maps"]
    if not cache:
        # build_name_maps() does a blocking network call (the requests
        # library) - run it off the event loop so it doesn't stall the
        # WebSocket relay for other clients while it fetches. Mutating the
        # pre-existing dict in place (rather than reassigning app["name_maps"])
        # avoids aiohttp's "changing state of a started application" warning.
        loop = asyncio.get_event_loop()
        cache.update(await loop.run_in_executor(None, build_name_maps))
    return web.json_response(cache)


def create_app() -> web.Application:
    app = web.Application()
    app["relay"] = EventRelay()
    app["name_maps"] = {}
    app.router.add_get("/ws", websocket_handler)
    app.router.add_get("/names.json", names_handler)
    app.router.add_get("/", index_handler)
    return app


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    web.run_app(create_app(), host="localhost", port=DEFAULT_PORT)


if __name__ == "__main__":
    main()
