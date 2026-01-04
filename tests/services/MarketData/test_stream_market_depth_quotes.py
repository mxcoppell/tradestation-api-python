"""
Test suite for the stream_market_depth_quotes method.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from tradestation.services.MarketData.market_data_service import MarketDataService
from tradestation.ts_types.market_data import Heartbeat, MarketDepthQuote, StreamErrorResponse


@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client with mocked create_stream."""
    client = AsyncMock()
    client.create_stream = AsyncMock()
    return client


@pytest.fixture
def market_data_service(mock_http_client):
    """Create a MarketDataService with mock http_client."""
    # StreamManager mock might not be needed if not used by other methods
    mock_stream_manager = AsyncMock()
    return MarketDataService(mock_http_client, mock_stream_manager)


@pytest.fixture
def mock_stream_reader():
    """Create a mock StreamReader for SSE."""
    mock = AsyncMock(spec=aiohttp.StreamReader)
    # Simulate readline yielding JSON data
    mock_data = [
        json.dumps({"Bids": [{"Price": "100.00", "Size": 10, "Name": "ARCA"}], "Asks": []}).encode(
            "utf-8"
        ),
        json.dumps({"Heartbeat": 1, "Timestamp": "2023-01-01T00:01:00Z"}).encode("utf-8"),
        b"",
    ]
    mock.readline.side_effect = mock_data
    return mock


class TestStreamMarketDepthQuotes:
    """Test cases for stream_market_depth_quotes."""

    @pytest.mark.asyncio
    async def test_stream_with_default_parameters(
        self, market_data_service, mock_http_client, mock_stream_reader
    ):
        """Test streaming with default parameters."""
        # Arrange
        symbol = "MSFT"
        expected_endpoint = f"/v3/marketdata/stream/marketdepth/quotes/{symbol}"
        expected_headers = {"Accept": "application/vnd.tradestation.streams.v2+json"}
        mock_http_client.create_stream.return_value = mock_stream_reader

        # Act
        result = await market_data_service.stream_market_depth_quotes(symbol)

        # Assert
        mock_http_client.create_stream.assert_called_once_with(
            expected_endpoint,
            params={},
            headers=expected_headers,
        )
        assert result == mock_stream_reader

    @pytest.mark.asyncio
    async def test_stream_with_custom_maxlevels(
        self, market_data_service, mock_http_client, mock_stream_reader
    ):
        """Test streaming with a custom maxlevels parameter."""
        # Arrange
        symbol = "AAPL"
        params = {"maxlevels": 10}
        expected_endpoint = f"/v3/marketdata/stream/marketdepth/quotes/{symbol}"
        expected_headers = {"Accept": "application/vnd.tradestation.streams.v2+json"}
        mock_http_client.create_stream.return_value = mock_stream_reader

        # Act
        result = await market_data_service.stream_market_depth_quotes(symbol, params)

        # Assert
        mock_http_client.create_stream.assert_called_once_with(
            expected_endpoint,
            params=params,
            headers=expected_headers,
        )
        assert result == mock_stream_reader

    @pytest.mark.asyncio
    async def test_stream_invalid_maxlevels(self, market_data_service):
        """Test that an error is raised for invalid maxlevels."""
        # Arrange
        symbol = "GOOG"
        params = {"maxlevels": 0}  # Invalid level

        # Act & Assert
        with pytest.raises(ValueError, match="maxlevels must be a positive integer"):
            await market_data_service.stream_market_depth_quotes(symbol, params)

    # Remove or adapt tests that rely on WebSocketStream specific features like set_callback
