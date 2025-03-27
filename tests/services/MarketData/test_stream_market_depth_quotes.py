"""
Tests for the stream_market_depth_quotes method of the MarketDataService class.
"""

import json
import pytest
from unittest.mock import MagicMock, AsyncMock

import logging

from src.services.MarketData.market_data_service import MarketDataService
from src.utils.websocket_stream import WebSocketStream
from src.ts_types.market_data import MarketDepthQuote, Heartbeat, StreamErrorResponse


@pytest.fixture
def mock_http_client():
    """Create a mock HttpClient for testing."""
    return AsyncMock()


@pytest.fixture
def mock_stream_manager():
    """Create a mock StreamManager for testing."""
    return AsyncMock()


@pytest.fixture
def market_data_service(mock_http_client, mock_stream_manager):
    """Create a MarketDataService with mock dependencies."""
    return MarketDataService(mock_http_client, mock_stream_manager)


class TestStreamMarketDepthQuotes:
    """Test cases for the stream_market_depth_quotes method."""

    @pytest.mark.asyncio
    async def test_stream_market_depth_quotes_with_valid_parameters(
        self, market_data_service, mock_stream_manager
    ):
        """Test streaming market depth quotes with valid parameters."""
        # Arrange
        symbol = "MSFT"
        params = {"maxlevels": 50}

        # Mock the StreamManager.create_stream method
        mock_stream = MagicMock(spec=WebSocketStream)
        mock_stream_manager.create_stream.return_value = mock_stream

        # Act
        result = await market_data_service.stream_market_depth_quotes(symbol, params)

        # Assert
        mock_stream_manager.create_stream.assert_called_once_with(
            "/v3/marketdata/stream/marketdepth/quotes/MSFT",
            params,
            {"headers": {"Accept": "application/vnd.tradestation.streams.v2+json"}},
        )
        assert result == mock_stream

    @pytest.mark.asyncio
    async def test_stream_market_depth_quotes_with_no_parameters(
        self, market_data_service, mock_stream_manager
    ):
        """Test streaming market depth quotes without parameters."""
        # Arrange
        symbol = "AAPL"
        mock_stream = MagicMock(spec=WebSocketStream)
        mock_stream_manager.create_stream.return_value = mock_stream

        # Act
        result = await market_data_service.stream_market_depth_quotes(symbol)

        # Assert
        mock_stream_manager.create_stream.assert_called_once_with(
            "/v3/marketdata/stream/marketdepth/quotes/AAPL",
            {},
            {"headers": {"Accept": "application/vnd.tradestation.streams.v2+json"}},
        )
        assert result == mock_stream

    @pytest.mark.asyncio
    async def test_stream_market_depth_quotes_maxlevels_not_positive(self, market_data_service):
        """Test that an error is raised when maxlevels is not a positive integer."""
        # Arrange
        symbol = "AAPL"
        params = {"maxlevels": 0}

        # Act & Assert
        with pytest.raises(ValueError, match="maxlevels must be a positive integer"):
            await market_data_service.stream_market_depth_quotes(symbol, params)

    @pytest.mark.asyncio
    async def test_integration_with_websocket_stream(
        self, market_data_service, mock_stream_manager
    ):
        """Test the integration with WebSocketStream for processing market depth data."""
        # Arrange
        symbol = "MSFT"
        mock_stream = AsyncMock(spec=WebSocketStream)

        # Create a list to record processed messages
        processed_data = []

        # Define a helper function to capture data for assertions
        async def capture_data(data):
            processed_data.append(data)

        # Setup mock stream
        mock_stream_manager.create_stream.return_value = mock_stream

        # Act
        stream = await market_data_service.stream_market_depth_quotes(symbol)

        # Verify the stream is created correctly
        assert stream == mock_stream

        # Set the callback on our mock stream
        stream.set_callback(capture_data)

        # Get the callback that was registered
        callback_func = mock_stream.set_callback.call_args[0][0]

        # Prepare test data
        market_depth_data = {
            "Bids": [
                {
                    "TimeStamp": "2023-03-02T14:00:00Z",
                    "Side": "Bid",
                    "Price": "214.95",
                    "Size": "500",
                    "OrderCount": 5,
                    "Name": "NSDQ",
                },
                {
                    "TimeStamp": "2023-03-02T14:00:01Z",
                    "Side": "Bid",
                    "Price": "214.90",
                    "Size": "1000",
                    "OrderCount": 8,
                    "Name": "ARCA",
                },
            ],
            "Asks": [
                {
                    "TimeStamp": "2023-03-02T14:00:00Z",
                    "Side": "Ask",
                    "Price": "215.05",
                    "Size": "800",
                    "OrderCount": 6,
                    "Name": "EDGX",
                },
                {
                    "TimeStamp": "2023-03-02T14:00:01Z",
                    "Side": "Ask",
                    "Price": "215.10",
                    "Size": "1200",
                    "OrderCount": 10,
                    "Name": "BATS",
                },
            ],
        }

        heartbeat_data = {"Heartbeat": 1, "Timestamp": "2023-03-02T14:01:00Z"}

        error_data = {"Error": "InvalidSymbol", "Message": "Symbol not found"}

        # Simulate callbacks being called with different types of data
        await callback_func(market_depth_data)
        await callback_func(heartbeat_data)
        await callback_func(error_data)

        # Verify data was processed correctly
        assert len(processed_data) == 3
        assert processed_data[0] == market_depth_data
        assert processed_data[1] == heartbeat_data
        assert processed_data[2] == error_data
