import json

from tft.models.champion import Champion
from tft.models.item import Item
from tft.overwolf_server import build_name_maps, create_app


class _FakeCDragonClient:
    def get_champions(self):
        return [Champion(api_name="TFT14_Draven", display_name="Draven", cost=1)]

    def get_items(self):
        return [Item(api_name="TFT_Item_InfinityEdge", display_name="Infinity Edge")]


class _BrokenCDragonClient:
    def get_champions(self):
        raise RuntimeError("network down")

    def get_items(self):
        raise RuntimeError("network down")


def test_build_name_maps_lowercases_api_names_as_keys():
    maps = build_name_maps(client=_FakeCDragonClient())

    assert maps["champions"]["tft14_draven"] == "Draven"
    assert maps["items"]["tft_item_infinityedge"] == "Infinity Edge"


def test_build_name_maps_degrades_gracefully_on_failure():
    maps = build_name_maps(client=_BrokenCDragonClient())

    assert maps == {"champions": {}, "items": {}}


async def test_names_route_serves_built_name_maps(aiohttp_client, mocker):
    mocker.patch("tft.overwolf_server.build_name_maps", return_value={"champions": {"a": "A"}, "items": {}})
    client = await aiohttp_client(create_app())

    resp = await client.get("/names.json")

    assert resp.status == 200
    assert await resp.json() == {"champions": {"a": "A"}, "items": {}}


async def test_static_index_is_served(aiohttp_client):
    client = await aiohttp_client(create_app())
    resp = await client.get("/")
    assert resp.status == 200
    body = await resp.text()
    assert "TFT Events Dashboard" in body


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
