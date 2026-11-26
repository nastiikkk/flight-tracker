from unittest.mock import Mock, patch

import pytest
from requests import HTTPError

from src.api_classes import AeroplanesAPI, BaseAPI


@pytest.fixture
def api():
    return AeroplanesAPI()


def test_api_init(api):
    assert api.openstreetmap_url == ("https://nominatim.openstreetmap.org/search")
    assert api.opensky_url == ("https://opensky-network.org/api/states/all?")
    assert api.aeroplanes is None


def test_aeroplanes_api_inherits_base_api():
    assert issubclass(AeroplanesAPI, BaseAPI)


def test_base_api_is_abstract():
    with pytest.raises(TypeError):
        BaseAPI()


@patch("src.api_classes.get")
def test_get_aeroplanes_success(mock_get, api):
    nominatim_response = Mock()
    nominatim_response.status_code = 200
    nominatim_response.json.return_value = [
        {"boundingbox": ["40.0", "50.0", "10.0", "20.0"]}
    ]

    opensky_response = Mock()
    opensky_response.json.return_value = {"time": 123456789, "states": [["AAA111"]]}

    mock_get.side_effect = [nominatim_response, opensky_response]

    result = api.get_aeroplanes("Germany")

    assert result == {"time": 123456789, "states": [["AAA111"]]}

    assert api.aeroplanes == result
    assert mock_get.call_count == 2

    mock_get.assert_any_call(
        url=api.openstreetmap_url,
        params={"country": "Germany", "format": "json", "limit": 1},
        headers={"User-Agent": "flight-tracker/1.0"},
    )

    mock_get.assert_any_call(
        url=api.opensky_url,
        params={"lamin": "40.0", "lamax": "50.0", "lomin": "10.0", "lomax": "20.0"},
    )


@patch("src.api_classes.get")
def test_get_aeroplanes_country_not_found(mock_get, api):
    response = Mock()
    response.status_code = 200
    response.json.return_value = []

    mock_get.return_value = response

    result = api.get_aeroplanes("Unknown country")

    assert result == {"time": None, "states": []}

    assert api.aeroplanes is None
    mock_get.assert_called_once()


@patch("src.api_classes.get")
def test_get_aeroplanes_http_error(mock_get, api):
    response = Mock()
    response.status_code = 404

    mock_get.return_value = response

    with pytest.raises(HTTPError):
        api.get_aeroplanes("Germany")

    mock_get.assert_called_once()


@patch("src.api_classes.get")
def test_get_aeroplanes_opensky_response(mock_get, api):
    nominatim_response = Mock()
    nominatim_response.status_code = 200
    nominatim_response.json.return_value = [
        {"boundingbox": ["40.0", "50.0", "10.0", "20.0"]}
    ]

    opensky_response = Mock()
    opensky_response.json.return_value = {"time": 123, "states": []}

    mock_get.side_effect = [nominatim_response, opensky_response]

    result = api.get_aeroplanes("France")

    assert result == {"time": 123, "states": []}
    assert api.aeroplanes == result
