from typing import Any, Dict

import pytest

from tradestation.ts_types.market_data import Strikes


@pytest.mark.asyncio
async def test_get_option_strikes_basic(market_data_service, http_client_mock):
    """Test getting option strikes with basic parameters"""
    # Mock response data
    mock_response = {"SpreadType": "Single", "Strikes": [["150"], ["155"], ["160"]]}
    http_client_mock.get.return_value = mock_response

    # Call the method
    result = await market_data_service.get_option_strikes("AAPL")

    # Verify the HTTP client was called correctly
    http_client_mock.get.assert_called_once_with("/v3/marketdata/options/strikes/AAPL", params={})

    # Verify the response was parsed correctly
    assert isinstance(result, Strikes)
    assert result.SpreadType == "Single"
    assert result.Strikes == [["150"], ["155"], ["160"]]


@pytest.mark.asyncio
async def test_get_option_strikes_with_expiration(market_data_service, http_client_mock):
    """Test getting option strikes with expiration date"""
    # Mock response data
    mock_response = {"SpreadType": "Single", "Strikes": [["150"], ["155"], ["160"]]}
    http_client_mock.get.return_value = mock_response

    # Call the method with expiration
    result = await market_data_service.get_option_strikes("AAPL", expiration="2024-01-19")

    # Verify the HTTP client was called correctly
    http_client_mock.get.assert_called_once_with(
        "/v3/marketdata/options/strikes/AAPL", params={"expiration": "2024-01-19"}
    )

    # Verify the response was parsed correctly
    assert isinstance(result, Strikes)
    assert result.SpreadType == "Single"
    assert result.Strikes == [["150"], ["155"], ["160"]]


@pytest.mark.asyncio
async def test_get_option_strikes_with_spread_type(market_data_service, http_client_mock):
    """Test getting option strikes for a specific spread type"""
    # Mock response data for a butterfly spread
    mock_response = {
        "SpreadType": "Butterfly",
        "Strikes": [["145", "150", "155"], ["150", "155", "160"]],
    }
    http_client_mock.get.return_value = mock_response

    # Call the method with spread type
    result = await market_data_service.get_option_strikes("SPY", spread_type="Butterfly")

    # Verify the HTTP client was called correctly
    http_client_mock.get.assert_called_once_with(
        "/v3/marketdata/options/strikes/SPY", params={"spreadType": "Butterfly"}
    )

    # Verify the response was parsed correctly
    assert isinstance(result, Strikes)
    assert result.SpreadType == "Butterfly"
    assert result.Strikes == [["145", "150", "155"], ["150", "155", "160"]]


@pytest.mark.asyncio
async def test_get_option_strikes_calendar_spread(market_data_service, http_client_mock):
    """Test getting option strikes for a calendar spread with two expiration dates"""
    # Mock response data for a calendar spread
    mock_response = {"SpreadType": "Calendar", "Strikes": [["150"], ["155"], ["160"]]}
    http_client_mock.get.return_value = mock_response

    # Call the method with calendar spread parameters
    result = await market_data_service.get_option_strikes(
        "MSFT",
        expiration="2024-01-19",
        spread_type="Calendar",
        options={"expiration2": "2024-02-16"},
    )

    # Verify the HTTP client was called correctly
    http_client_mock.get.assert_called_once_with(
        "/v3/marketdata/options/strikes/MSFT",
        params={"expiration": "2024-01-19", "spreadType": "Calendar", "expiration2": "2024-02-16"},
    )

    # Verify the response was parsed correctly
    assert isinstance(result, Strikes)
    assert result.SpreadType == "Calendar"
    assert result.Strikes == [["150"], ["155"], ["160"]]


@pytest.mark.asyncio
async def test_get_option_strikes_empty_underlying(market_data_service):
    """Test that empty underlying symbol raises ValueError"""
    with pytest.raises(ValueError, match="Underlying symbol is required"):
        await market_data_service.get_option_strikes("")


@pytest.mark.asyncio
async def test_get_option_strikes_http_error(market_data_service, http_client_mock):
    """Test handling of HTTP errors"""
    # Mock HTTP error
    http_client_mock.get.side_effect = Exception("API Error")

    # Verify the error is propagated
    with pytest.raises(Exception, match="API Error"):
        await market_data_service.get_option_strikes("AAPL")
