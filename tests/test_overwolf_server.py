import json

from tft.overwolf_server import create_app


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
