import pytest

from tft.config import Settings
from tft.riot_api.client import RiotAPIClient
from tft.riot_api.exceptions import RiotAPIError


class FakeResponse:
    def __init__(self, status_code, json_data=None, text="", headers=None):
        self.status_code = status_code
        self._json_data = json_data
        self.text = text
        self.headers = headers or {}

    def json(self):
        return self._json_data


@pytest.fixture
def client():
    return RiotAPIClient(settings=Settings(riot_api_key="fake-key", platform="na1"), max_retries=0)


def test_requires_api_key():
    with pytest.raises(ValueError):
        RiotAPIClient(settings=Settings(riot_api_key=None, platform="na1"))


def test_get_account_by_riot_id_hits_americas_routing(client, mocker):
    mock_get = mocker.patch.object(client._session, "get", return_value=FakeResponse(200, {"puuid": "abc123"}))

    account = client.get_account_by_riot_id("Name", "TAG")

    assert account == {"puuid": "abc123"}
    called_url = mock_get.call_args.args[0]
    assert called_url == "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/Name/TAG"


def test_get_tft_summoner_uses_platform_routing(client, mocker):
    mocker.patch.object(client._session, "get", return_value=FakeResponse(200, {"puuid": "abc123"}))

    client.get_tft_summoner_by_puuid("abc123")

    called_url = client._session.get.call_args.args[0]
    assert called_url.startswith("https://na1.api.riotgames.com/tft/summoner/v1/summoners/by-puuid/")


def test_active_game_returns_none_on_404(client, mocker):
    mocker.patch.object(client._session, "get", return_value=FakeResponse(404, text="not found"))

    assert client.get_tft_active_game_by_puuid("abc123") is None


def test_non_404_error_is_raised(client, mocker):
    mocker.patch.object(client._session, "get", return_value=FakeResponse(500, text="boom"))

    with pytest.raises(RiotAPIError):
        client.get_tft_match("NA1_123")
