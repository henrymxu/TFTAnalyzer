from tft.static_data.cdragon import CDragonClient

# Shape confirmed against a live fetch of
# https://raw.communitydragon.org/latest/cdragon/tft/en_us.json: augments
# are items in the same top-level "items" array as everything else,
# flagged with isAugment=True - there's no separate per-set "augments"
# object with full details (a set's own "augments" field, when present, is
# just bare apiName strings).
RAW_RESPONSE = {
    "items": [
        {"apiName": "TFT_Item_InfinityEdge", "name": "Infinity Edge", "icon": "assets/ie.tex", "isAugment": False},
        {"apiName": "TFT13_Augment_Academy", "name": "Academic Research", "icon": "assets/academy.tex", "isAugment": True},
    ],
    "sets": {"18": {"champions": [], "traits": []}},
}


def _client_with_raw(raw):
    client = CDragonClient.__new__(CDragonClient)
    client._raw = raw
    return client


def test_get_augments_filters_items_by_is_augment_flag():
    client = _client_with_raw(RAW_RESPONSE)

    augments = client.get_augments()

    assert [a.api_name for a in augments] == ["TFT13_Augment_Academy"]
    assert augments[0].display_name == "Academic Research"


def test_get_items_returns_everything_including_augments():
    client = _client_with_raw(RAW_RESPONSE)

    items = client.get_items()

    assert {i.api_name for i in items} == {"TFT_Item_InfinityEdge", "TFT13_Augment_Academy"}
