import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tradestation.client.http_client import HttpClient
from tradestation.services.MarketData.market_data_service import MarketDataService
from tradestation.streaming.stream_manager import StreamManager
from tradestation.ts_types.market_data import RiskRewardAnalysisResult


@pytest.fixture
def mock_http_client():
    mock = AsyncMock(spec=HttpClient)
    return mock


@pytest.fixture
def mock_stream_manager():
    mock = AsyncMock(spec=StreamManager)
    return mock


@pytest.fixture
def market_data_service(mock_http_client, mock_stream_manager):
    return MarketDataService(mock_http_client, mock_stream_manager)


@pytest.fixture
def mock_input():
    return {
        "SpreadPrice": 0.13,
        "Legs": [
            {"Symbol": "AAPL 261218C185", "Quantity": 1, "TradeAction": "BUY"},
            {"Symbol": "AAPL 261218P180", "Quantity": 1, "TradeAction": "SELL"},
        ],
    }


@pytest.fixture
def mock_response():
    return {
        "MaxGainIsInfinite": True,
        "AdjustedMaxGain": "0",
        "MaxLossIsInfinite": False,
        "AdjustedMaxLoss": "-18013",
        "BreakevenPoints": ["185.13"],
    }


class TestGetOptionRiskReward:
    """
    Tests for the get_option_risk_reward method of MarketDataService
    """

    @pytest.mark.asyncio
    async def test_get_risk_reward_success(
        self, market_data_service, mock_http_client, mock_input, mock_response
    ):
        """Test successful call with valid input matching OpenAPI spec"""
        # Configure the mock to return the expected response
        mock_http_client.post.return_value = mock_response

        # Call the method being tested
        result = await market_data_service.get_option_risk_reward(mock_input)

        # Verify the result type and fields based on RiskRewardAnalysisResult
        assert isinstance(result, RiskRewardAnalysisResult)
        assert result.MaxGainIsInfinite == mock_response["MaxGainIsInfinite"]
        assert result.AdjustedMaxGain == mock_response["AdjustedMaxGain"]
        assert result.MaxLossIsInfinite == mock_response["MaxLossIsInfinite"]
        assert result.AdjustedMaxLoss == mock_response["AdjustedMaxLoss"]
        assert result.BreakevenPoints == mock_response["BreakevenPoints"]

        # Verify the HTTP client was called correctly with the updated input structure
        mock_http_client.post.assert_called_with(
            "/v3/marketdata/options/riskreward", data=mock_input
        )

    @pytest.mark.asyncio
    async def test_handle_empty_legs_array(self, market_data_service, mock_http_client):
        """Test input validation for empty legs array"""
        # Create invalid input with empty legs array (structure matches OpenAPI)
        invalid_input = {"SpreadPrice": 0.24, "Legs": []}

        # Test that a ValueError is raised (this check happens before API call)
        with pytest.raises(ValueError, match="At least one leg is required"):
            await market_data_service.get_option_risk_reward(invalid_input)

        # Verify the HTTP client was not called
        mock_http_client.post.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_api_error_response(self, market_data_service, mock_http_client):
        """Test handling of a structured error response from the API"""
        error_message = "Some specific API error occurred"
        # Use an input structure matching OpenAPI
        invalid_input = {
            "SpreadPrice": 0.24,
            "Legs": [
                {
                    "Symbol": "AAPL 240119C150",  # Symbol doesn't matter for this test
                    "Quantity": 1,
                    "TradeAction": "BUY",
                }
            ],
        }

        # Configure the mock to return an error response dictionary
        mock_http_client.post.return_value = {"Error": "SOME_API_ERROR", "Message": error_message}

        # Test that an Exception is raised with the API message
        with pytest.raises(Exception, match=error_message):
            await market_data_service.get_option_risk_reward(invalid_input)

        # Verify the HTTP client was called correctly with the updated input structure
        mock_http_client.post.assert_called_with(
            "/v3/marketdata/options/riskreward", data=invalid_input
        )

    @pytest.mark.asyncio
    async def test_handle_network_errors(self, market_data_service, mock_http_client, mock_input):
        """Test handling of network/connection errors during the API call"""
        # Configure the mock to raise an exception (e.g., network issue)
        error_message = "Network error"
        mock_http_client.post.side_effect = Exception(error_message)

        # Test that the exception is propagated
        with pytest.raises(Exception, match=error_message):
            await market_data_service.get_option_risk_reward(mock_input)

        # Verify the HTTP client was called correctly with the updated input structure
        mock_http_client.post.assert_called_with(
            "/v3/marketdata/options/riskreward", data=mock_input
        )
