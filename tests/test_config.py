import pytest

from tft.config import Settings


def test_routing_region_maps_platform_to_continent():
    assert Settings(riot_api_key="x", platform="na1").routing_region == "americas"
    assert Settings(riot_api_key="x", platform="euw1").routing_region == "europe"
    assert Settings(riot_api_key="x", platform="kr").routing_region == "asia"


def test_routing_region_rejects_unknown_platform():
    with pytest.raises(ValueError):
        Settings(riot_api_key="x", platform="not-a-region").routing_region
