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

import logging
from collections import deque
from pathlib import Path

from aiohttp import WSMsgType, web

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


def create_app() -> web.Application:
    app = web.Application()
    app["relay"] = EventRelay()
    app.router.add_get("/ws", websocket_handler)
    app.router.add_get("/", index_handler)
    return app


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    web.run_app(create_app(), host="localhost", port=DEFAULT_PORT)


if __name__ == "__main__":
    main()
