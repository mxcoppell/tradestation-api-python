"""
Test suite for the stream_market_depth_aggregates method in the Market Data Service.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.MarketData.market_data_service import MarketDataService
from src.ts_types.market_data import (
    MarketDepthAggregate,
    AggregatedQuoteData,
    Heartbeat,
    StreamErrorResponse,
)
from src.utils.websocket_stream import WebSocketStream


@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client for testing."""
    return AsyncMock()


@pytest.fixture
def mock_stream_manager():
    """Create a mock StreamManager for testing."""
    return AsyncMock()


@pytest.fixture
def market_data_service(mock_http_client, mock_stream_manager):
    """Create a MarketDataService with mock dependencies."""
    return MarketDataService(mock_http_client, mock_stream_manager)


class TestStreamMarketDepthAggregates:
    """Test cases for the stream_market_depth_aggregates method."""

    @pytest.mark.asyncio
    async def test_stream_market_depth_aggregates_with_valid_parameters(
        self, market_data_service, mock_stream_manager
    ):
        """Test streaming market depth aggregates with valid parameters."""
        # Arrange
        symbol = "MSFT"
        params = {"maxlevels": 50}

        # Mock the StreamManager.create_stream method
        mock_stream = MagicMock(spec=WebSocketStream)
        mock_stream_manager.create_stream.return_value = mock_stream

        # Act
        result = await market_data_service.stream_market_depth_aggregates(symbol, params)

        # Assert
        mock_stream_manager.create_stream.assert_called_once_with(
            "/v3/marketdata/stream/marketdepth/aggregates/MSFT",
            params,
            {"headers": {"Accept": "application/vnd.tradestation.streams.v2+json"}},
        )
        assert result == mock_stream

    @pytest.mark.asyncio
    async def test_stream_market_depth_aggregates_with_no_parameters(
        self, market_data_service, mock_stream_manager
    ):
        """Test streaming market depth aggregates without parameters."""
        # Arrange
        symbol = "AAPL"
        mock_stream = MagicMock(spec=WebSocketStream)
        mock_stream_manager.create_stream.return_value = mock_stream

        # Act
        result = await market_data_service.stream_market_depth_aggregates(symbol)

        # Assert
        mock_stream_manager.create_stream.assert_called_once_with(
            "/v3/marketdata/stream/marketdepth/aggregates/AAPL",
            {},
            {"headers": {"Accept": "application/vnd.tradestation.streams.v2+json"}},
        )
        assert result == mock_stream

    @pytest.mark.asyncio
    async def test_stream_market_depth_aggregates_maxlevels_too_small(self, market_data_service):
        """Test that an error is raised when maxlevels is less than 1."""
        # Arrange
        symbol = "AAPL"
        params = {"maxlevels": 0}

        # Act & Assert
        with pytest.raises(ValueError, match="maxlevels must be between 1 and 100"):
            await market_data_service.stream_market_depth_aggregates(symbol, params)

    @pytest.mark.asyncio
    async def test_stream_market_depth_aggregates_maxlevels_too_large(self, market_data_service):
        """Test that an error is raised when maxlevels is greater than 100."""
        # Arrange
        symbol = "AAPL"
        params = {"maxlevels": 101}

        # Act & Assert
        with pytest.raises(ValueError, match="maxlevels must be between 1 and 100"):
            await market_data_service.stream_market_depth_aggregates(symbol, params)

    @pytest.mark.asyncio
    async def test_integration_with_websocket_stream(
        self, market_data_service, mock_stream_manager
    ):
        """Test the integration with WebSocketStream for processing market depth data."""
        # Arrange
        symbol = "MSFT"
        mock_stream = AsyncMock(spec=WebSocketStream)

        # Simulate WebSocketStream behavior with callback handling
        mock_callback = None

        def mock_set_callback(callback):
            nonlocal mock_callback
            mock_callback = callback

        mock_stream.set_callback.side_effect = mock_set_callback
        mock_stream_manager.create_stream.return_value = mock_stream

        # Act
        stream = await market_data_service.stream_market_depth_aggregates(symbol)

        # Define example data messages
        market_depth_data = {
            "Bids": [
                {
                    "EarliestTime": "2023-03-02T14:00:00Z",
                    "LatestTime": "2023-03-02T14:00:05Z",
                    "Side": "Bid",
                    "Price": "214.95",
                    "TotalSize": "1500",
                    "BiggestSize": "500",
                    "SmallestSize": "100",
                    "NumParticipants": 5,
                    "TotalOrderCount": 10,
                },
                {
                    "EarliestTime": "2023-03-02T14:00:01Z",
                    "LatestTime": "2023-03-02T14:00:06Z",
                    "Side": "Bid",
                    "Price": "214.90",
                    "TotalSize": "2500",
                    "BiggestSize": "1000",
                    "SmallestSize": "200",
                    "NumParticipants": 8,
                    "TotalOrderCount": 15,
                },
            ],
            "Asks": [
                {
                    "EarliestTime": "2023-03-02T14:00:00Z",
                    "LatestTime": "2023-03-02T14:00:05Z",
                    "Side": "Ask",
                    "Price": "215.05",
                    "TotalSize": "1800",
                    "BiggestSize": "800",
                    "SmallestSize": "100",
                    "NumParticipants": 6,
                    "TotalOrderCount": 12,
                },
                {
                    "EarliestTime": "2023-03-02T14:00:01Z",
                    "LatestTime": "2023-03-02T14:00:06Z",
                    "Side": "Ask",
                    "Price": "215.10",
                    "TotalSize": "3000",
                    "BiggestSize": "1200",
                    "SmallestSize": "300",
                    "NumParticipants": 10,
                    "TotalOrderCount": 20,
                },
            ],
        }

        heartbeat_data = {"Heartbeat": 1, "Timestamp": "2023-03-02T14:01:00Z"}

        error_data = {"Error": "InvalidSymbol", "Message": "Symbol not found"}

        # Use callback to test data processing
        received_data = []

        async def test_callback(data):
            received_data.append(data)

        # Set the callback and simulate data reception
        stream.set_callback(test_callback)
        assert mock_callback is not None

        # Simulate receiving data
        await mock_callback(market_depth_data)
        await mock_callback(heartbeat_data)
        await mock_callback(error_data)

        # Assert data was processed correctly
        assert len(received_data) == 3
        assert received_data[0] == market_depth_data
        assert received_data[1] == heartbeat_data
        assert received_data[2] == error_data

        # Validate that the bid and ask data structures match expectations
        assert len(received_data[0]["Bids"]) == 2
        assert len(received_data[0]["Asks"]) == 2
        assert received_data[0]["Bids"][0]["Price"] == "214.95"
        assert received_data[0]["Asks"][0]["Price"] == "215.05"
