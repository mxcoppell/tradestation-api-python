"""
Test suite for the stream_bars method in the Market Data Service.
"""

import asyncio
import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp

from tradestation.services.MarketData.market_data_service import MarketDataService
from tradestation.ts_types.market_data import Bar, Heartbeat, StreamErrorResponse


@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client for testing."""
    # Mock the create_stream method
    client = AsyncMock()
    client.create_stream = AsyncMock()
    return client


@pytest.fixture
def mock_stream_manager():
    """Create a mock StreamManager for testing (might not be needed)."""
    return AsyncMock()


@pytest.fixture
def market_data_service(mock_http_client, mock_stream_manager):
    """Create a MarketDataService with mock dependencies."""
    return MarketDataService(mock_http_client, mock_stream_manager)


@pytest.fixture
def mock_stream_reader():
    """Create a mock StreamReader for SSE."""
    mock = AsyncMock(spec=aiohttp.StreamReader)
    # Simulate readline yielding JSON data and then None
    mock_data = [
        json.dumps(
            {
                "Close": "215.25",
                "TimeStamp": "2023-03-02T14:00:00Z",
                # ... other fields ...
            }
        ).encode("utf-8"),
        json.dumps({"Heartbeat": 1, "Timestamp": "2023-03-02T14:01:00Z"}).encode("utf-8"),
        json.dumps({"Error": "InvalidSymbol", "Message": "Symbol not found"}).encode("utf-8"),
        b"",  # End of stream
    ]
    mock.readline.side_effect = mock_data
    return mock


class TestStreamBars:
    """Test cases for the stream_bars method."""

    @pytest.mark.asyncio
    async def test_stream_bars_with_valid_parameters(
        self, market_data_service, mock_http_client, mock_stream_reader
    ):
        """Test streaming bars with valid parameters using SSE."""
        # Arrange
        symbol = "MSFT"
        params = {
            "unit": "Minute",
            "interval": "5",
            "barsback": 100,
            "sessiontemplate": "USEQPreAndPost",
        }
        expected_endpoint = f"/v3/marketdata/stream/barcharts/{symbol}"
        expected_headers = {"Accept": "application/vnd.tradestation.streams.v2+json"}

        # Mock the HttpClient.create_stream method
        mock_http_client.create_stream.return_value = mock_stream_reader

        # Act
        result = await market_data_service.stream_bars(symbol, params)

        # Assert
        mock_http_client.create_stream.assert_called_once_with(
            expected_endpoint,
            params=params,
            headers=expected_headers,
        )
        assert result == mock_stream_reader

    @pytest.mark.asyncio
    async def test_stream_bars_with_no_parameters(
        self, market_data_service, mock_http_client, mock_stream_reader
    ):
        """Test streaming bars without parameters using SSE."""
        # Arrange
        symbol = "AAPL"
        expected_endpoint = f"/v3/marketdata/stream/barcharts/{symbol}"
        expected_headers = {"Accept": "application/vnd.tradestation.streams.v2+json"}
        mock_http_client.create_stream.return_value = mock_stream_reader

        # Act
        result = await market_data_service.stream_bars(symbol)

        # Assert
        mock_http_client.create_stream.assert_called_once_with(
            expected_endpoint,
            params={},
            headers=expected_headers,
        )
        assert result == mock_stream_reader

    @pytest.mark.asyncio
    async def test_stream_bars_invalid_interval_for_non_minute(self, market_data_service):
        """Test that an error is raised when using an invalid interval for non-minute bars."""
        # Arrange
        symbol = "AAPL"
        params = {"unit": "Daily", "interval": "5"}

        # Act & Assert
        with pytest.raises(ValueError, match="Interval must be 1 for non-minute bars"):
            await market_data_service.stream_bars(symbol, params)

    @pytest.mark.asyncio
    async def test_stream_bars_interval_too_large_for_minute(self, market_data_service):
        """Test that an error is raised when the interval for minute bars is too large."""
        # Arrange
        symbol = "AAPL"
        params = {"unit": "Minute", "interval": "1441"}

        # Act & Assert
        with pytest.raises(ValueError, match="Maximum interval for minute bars is 1440"):
            await market_data_service.stream_bars(symbol, params)

    @pytest.mark.asyncio
    async def test_stream_bars_too_many_bars_back(self, market_data_service):
        """Test that an error is raised when requesting too many bars back."""
        # Arrange
        symbol = "AAPL"
        params = {"barsback": 57601}

        # Act & Assert
        with pytest.raises(ValueError, match="Maximum of 57,600 bars allowed per request"):
            await market_data_service.stream_bars(symbol, params)
