import asyncio
import json
import time

import tft.overwolf_server as overwolf_server
from tft.models.champion import Champion
from tft.models.item import Item
from tft.models.trait import Trait, TraitTier
from tft.overwolf_server import EventRelay, build_name_maps, create_app


class _FakeCDragonClient:
    def get_champions(self):
        return [
            Champion(
                api_name="TFT14_Draven",
                display_name="Draven",
                cost=1,
                icon_path="/Assets/Draven.tex",
                # Community Dragon's champion.traits holds trait *display*
                # names ("Executioner"), not apiNames - confirmed against a
                # live fetch.
                traits=("Executioner",),
            ),
            Champion(api_name="TFT14_NoIcon", display_name="No Icon", cost=1, icon_path=None),
        ]

    def get_items(self):
        return [Item(api_name="TFT_Item_InfinityEdge", display_name="Infinity Edge", icon_path="/Assets/IE.dds")]

    def get_traits(self):
        return [
            Trait(
                api_name="TFT14_Executioner",
                display_name="Executioner",
                icon_path="/Assets/Executioner.dds",
                tiers=(TraitTier(min_units=2, style="bronze"), TraitTier(min_units=4, style="silver")),
            )
        ]

    def get_augments(self):
        return [Item(api_name="TFT9_Augment_Test", display_name="Test Augment", icon_path="/Assets/Augment.dds")]


class _BrokenCDragonClient:
    def get_champions(self):
        raise RuntimeError("network down")

    def get_items(self):
        raise RuntimeError("network down")

    def get_traits(self):
        raise RuntimeError("network down")

    def get_augments(self):
        raise RuntimeError("network down")


def test_build_name_maps_lowercases_api_names_as_keys():
    maps = build_name_maps(client=_FakeCDragonClient())

    assert maps["champions"]["tft14_draven"]["name"] == "Draven"
    assert maps["champions"]["tft14_draven"]["icon"] == "https://raw.communitydragon.org/latest/game/assets/draven.png"
    assert maps["champions"]["tft14_draven"]["traits"] == ["Executioner"]
    assert maps["items"]["tft_item_infinityedge"]["name"] == "Infinity Edge"
    assert maps["items"]["tft_item_infinityedge"]["icon"] == "https://raw.communitydragon.org/latest/game/assets/ie.png"
    assert maps["augments"]["tft9_augment_test"]["name"] == "Test Augment"


def test_build_name_maps_includes_trait_tiers():
    maps = build_name_maps(client=_FakeCDragonClient())

    # Keyed by display name, not apiName - that's what a champion's own
    # "traits" list actually contains, so that's what the webapp looks up.
    trait = maps["traits"]["executioner"]
    assert trait["name"] == "Executioner"
    assert trait["tiers"] == [{"min_units": 2, "style": "bronze"}, {"min_units": 4, "style": "silver"}]


def test_build_name_maps_handles_missing_icon_path():
    maps = build_name_maps(client=_FakeCDragonClient())

    assert maps["champions"]["tft14_noicon"] == {"name": "No Icon", "icon": None, "traits": []}


def test_build_name_maps_degrades_gracefully_on_failure():
    maps = build_name_maps(client=_BrokenCDragonClient())

    assert maps == {"champions": {}, "items": {}, "traits": {}, "augments": {}}


async def test_names_route_serves_built_name_maps(aiohttp_client, mocker):
    fake_maps = {"champions": {"a": "A"}, "items": {}, "traits": {}, "augments": {}}
    mocker.patch("tft.overwolf_server.build_name_maps", return_value=fake_maps)
    client = await aiohttp_client(create_app())

    resp = await client.get("/names.json")

    assert resp.status == 200
    assert await resp.json() == fake_maps


async def test_static_index_is_served(aiohttp_client):
    client = await aiohttp_client(create_app())
    resp = await client.get("/")
    assert resp.status == 200
    body = await resp.text()
    assert "TFT Events Dashboard" in body


class _HangingClient:
    """Simulates a client whose send_str() never returns - e.g. a
    suspended browser tab that stopped draining its socket."""

    async def send_str(self, raw):
        await asyncio.sleep(3600)


class _FastClient:
    def __init__(self):
        self.received = []

    async def send_str(self, raw):
        self.received.append(raw)


async def test_broadcast_does_not_block_on_a_slow_client(monkeypatch):
    # A real hang would take forever to actually test - shorten the
    # timeout so the test itself stays fast.
    monkeypatch.setattr(overwolf_server, "CLIENT_SEND_TIMEOUT_SECONDS", 0.05)
    relay = EventRelay()
    hanging = _HangingClient()
    fast = _FastClient()
    relay._clients = {hanging, fast}

    start = time.monotonic()
    await relay.broadcast("hello")
    elapsed = time.monotonic() - start

    # Bounded by the (patched, short) per-client timeout - not the hang -
    # and dispatched concurrently, so it isn't the sum of both clients'
    # timeouts either.
    assert elapsed < 1
    assert fast.received == ["hello"]
    assert hanging not in relay._clients
    assert fast in relay._clients


async def test_broadcasts_message_to_other_connected_clients(aiohttp_client):
    client = await aiohttp_client(create_app())

    sender = await client.ws_connect("/ws")
    receiver = await client.ws_connect("/ws")

    message = json.dumps({"seq": 1, "ts": 123, "kind": "event", "payload": {"foo": "bar"}})
    await sender.send_str(message)

    received = await receiver.receive_str(timeout=2)
    assert received == message

    await sender.close()
    await receiver.close()


async def test_late_joiner_receives_history_replay(aiohttp_client):
    client = await aiohttp_client(create_app())

    sender = await client.ws_connect("/ws")
    first = json.dumps({"seq": 1, "ts": 100, "kind": "info_update", "payload": {}})
    await sender.send_str(first)
    # broadcast() echoes to every connected client (sender included) only
    # after appending to history, so waiting for our own echo guarantees
    # the message is already in history before the late joiner connects.
    await sender.receive_str(timeout=2)

    late_joiner = await client.ws_connect("/ws")
    replayed = await late_joiner.receive_str(timeout=2)
    assert replayed == first

    await sender.close()
    await late_joiner.close()
