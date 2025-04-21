"""
Test suite for the stream_option_chain method.
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp

from tradestation.services.MarketData.market_data_service import MarketDataService
from tradestation.ts_types.market_data import Spread, Heartbeat, StreamErrorResponse


@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client with mocked create_stream."""
    client = AsyncMock()
    client.create_stream = AsyncMock()
    return client


@pytest.fixture
def market_data_service(mock_http_client):
    """Create a MarketDataService with mock http_client."""
    mock_stream_manager = AsyncMock()  # Keep if needed elsewhere
    return MarketDataService(mock_http_client, mock_stream_manager)


@pytest.fixture
def mock_stream_reader():
    """Create a mock StreamReader for SSE."""
    mock = AsyncMock(spec=aiohttp.StreamReader)
    # Simulate readline yielding JSON data
    mock_data = [
        json.dumps({"Delta": "0.5", "Strikes": ["100"]}).encode("utf-8"),  # Simplified Spread
        json.dumps({"Heartbeat": 1, "Timestamp": "2023-01-01T00:01:00Z"}).encode("utf-8"),
        b"",
    ]
    mock.readline.side_effect = mock_data
    return mock


class TestStreamOptionChain:
    """Test cases for stream_option_chain."""

    @pytest.mark.asyncio
    async def test_stream_with_default_parameters(
        self, market_data_service, mock_http_client, mock_stream_reader
    ):
        """Test streaming with default parameters."""
        # Arrange
        underlying = "MSFT"
        expected_endpoint = f"/v3/marketdata/stream/options/chains/{underlying}"
        expected_headers = {"Accept": "application/vnd.tradestation.streams.v2+json"}
        default_params = {  # Expected default parameters used by the method
            "strikeProximity": 5,
            "spreadType": "Single",
            "strikeInterval": 1,
            "enableGreeks": True,
            "strikeRange": "All",
            "optionType": "All",
        }
        mock_http_client.create_stream.return_value = mock_stream_reader

        # Act
        result = await market_data_service.stream_option_chain(underlying)

        # Assert
        mock_http_client.create_stream.assert_called_once_with(
            expected_endpoint,
            params=default_params,
            headers=expected_headers,
        )
        assert result == mock_stream_reader

    @pytest.mark.asyncio
    async def test_stream_with_custom_parameters(
        self, market_data_service, mock_http_client, mock_stream_reader
    ):
        """Test streaming with custom parameters."""
        # Arrange
        underlying = "AAPL"
        params = {
            "expiration": "2024-12-20",
            "spreadType": "Vertical",
            "strikeInterval": 2,
            "optionType": "Call",
            "strikeRange": "ITM",
            "riskFreeRate": 0.05,
        }
        expected_endpoint = f"/v3/marketdata/stream/options/chains/{underlying}"
        expected_headers = {"Accept": "application/vnd.tradestation.streams.v2+json"}
        # Merge custom params with defaults for assertion
        expected_params = {
            "strikeProximity": 5,
            "enableGreeks": True,
            **params,  # Custom params override defaults
        }
        mock_http_client.create_stream.return_value = mock_stream_reader

        # Act
        result = await market_data_service.stream_option_chain(underlying, params)

        # Assert
        mock_http_client.create_stream.assert_called_once_with(
            expected_endpoint,
            params=expected_params,
            headers=expected_headers,
        )
        assert result == mock_stream_reader

    @pytest.mark.asyncio
    async def test_stream_calendar_spread_requires_expiration2(self, market_data_service):
        """Test ValueError is raised for Calendar spread without expiration2."""
        with pytest.raises(ValueError, match="expiration2 is required for Calendar"):
            await market_data_service.stream_option_chain("SPY", {"spreadType": "Calendar"})

    @pytest.mark.asyncio
    async def test_stream_invalid_strike_interval(self, market_data_service):
        """Test ValueError for strikeInterval < 1."""
        with pytest.raises(ValueError, match="strikeInterval must be greater than or equal to 1"):
            await market_data_service.stream_option_chain("TSLA", {"strikeInterval": 0})

    @pytest.mark.asyncio
    async def test_stream_invalid_risk_free_rate(self, market_data_service):
        """Test ValueError for riskFreeRate outside [0, 1]."""
        with pytest.raises(
            ValueError, match="riskFreeRate must be a decimal value between 0 and 1"
        ):
            await market_data_service.stream_option_chain("GOOG", {"riskFreeRate": 1.1})
        with pytest.raises(
            ValueError, match="riskFreeRate must be a decimal value between 0 and 1"
        ):
            await market_data_service.stream_option_chain("GOOG", {"riskFreeRate": -0.1})

    # Remove or adapt tests that rely on WebSocketStream specific features
