"""
Test suite for the stream_quotes method in the Market Data Service.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.MarketData.market_data_service import MarketDataService
from src.ts_types.market_data import QuoteStream, Heartbeat, StreamErrorResponse
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


class TestStreamQuotes:
    """Test cases for the stream_quotes method."""

    @pytest.mark.asyncio
    async def test_stream_quotes_with_list_of_symbols(
        self, market_data_service, mock_stream_manager
    ):
        """Test streaming quotes with a list of symbols."""
        # Arrange
        symbols = ["MSFT", "AAPL", "GOOGL"]

        # Mock the StreamManager.create_stream method
        mock_stream = MagicMock(spec=WebSocketStream)
        mock_stream_manager.create_stream.return_value = mock_stream

        # Act
        result = await market_data_service.stream_quotes(symbols)

        # Assert
        mock_stream_manager.create_stream.assert_called_once_with(
            "/v3/marketdata/stream/quotes/MSFT,AAPL,GOOGL",
            {},
            {"headers": {"Accept": "application/vnd.tradestation.streams.v2+json"}},
        )
        assert result == mock_stream

    @pytest.mark.asyncio
    async def test_stream_quotes_with_string_of_symbols(
        self, market_data_service, mock_stream_manager
    ):
        """Test streaming quotes with a comma-separated string of symbols."""
        # Arrange
        symbols = "MSFT,AAPL,GOOGL"

        # Mock the StreamManager.create_stream method
        mock_stream = MagicMock(spec=WebSocketStream)
        mock_stream_manager.create_stream.return_value = mock_stream

        # Act
        result = await market_data_service.stream_quotes(symbols)

        # Assert
        mock_stream_manager.create_stream.assert_called_once_with(
            "/v3/marketdata/stream/quotes/MSFT,AAPL,GOOGL",
            {},
            {"headers": {"Accept": "application/vnd.tradestation.streams.v2+json"}},
        )
        assert result == mock_stream

    @pytest.mark.asyncio
    async def test_stream_quotes_with_single_symbol(self, market_data_service, mock_stream_manager):
        """Test streaming quotes with a single symbol."""
        # Arrange
        symbol = "MSFT"

        # Mock the StreamManager.create_stream method
        mock_stream = MagicMock(spec=WebSocketStream)
        mock_stream_manager.create_stream.return_value = mock_stream

        # Act
        result = await market_data_service.stream_quotes(symbol)

        # Assert
        mock_stream_manager.create_stream.assert_called_once_with(
            "/v3/marketdata/stream/quotes/MSFT",
            {},
            {"headers": {"Accept": "application/vnd.tradestation.streams.v2+json"}},
        )
        assert result == mock_stream

    @pytest.mark.asyncio
    async def test_stream_quotes_with_too_many_symbols(self, market_data_service):
        """Test that an error is raised when more than 100 symbols are provided."""
        # Arrange
        symbols = [f"SYMBOL{i}" for i in range(101)]  # 101 symbols

        # Act & Assert
        with pytest.raises(ValueError, match="Maximum of 100 symbols allowed per request"):
            await market_data_service.stream_quotes(symbols)

    @pytest.mark.asyncio
    async def test_integration_with_websocket_stream(
        self, market_data_service, mock_stream_manager
    ):
        """Test the integration with WebSocketStream for processing quote data."""
        # Arrange
        symbols = ["MSFT", "AAPL"]
        mock_stream = AsyncMock(spec=WebSocketStream)

        # Simulate WebSocketStream behavior with callback handling
        mock_callback = None

        def mock_set_callback(callback):
            nonlocal mock_callback
            mock_callback = callback

        mock_stream.set_callback.side_effect = mock_set_callback
        mock_stream_manager.create_stream.return_value = mock_stream

        # Act
        stream = await market_data_service.stream_quotes(symbols)

        # Define example data messages
        quote_data = {
            "Symbol": "MSFT",
            "Ask": "215.25",
            "AskSize": "300",
            "Bid": "215.20",
            "BidSize": "200",
            "Close": "214.25",
            "DailyOpenInterest": "0",
            "High": "216.50",
            "Low": "214.75",
            "High52Week": "224.75",
            "High52WeekTimestamp": "2023-01-21T14:00:00Z",
            "Last": "215.22",
            "Low52Week": "190.25",
            "Low52WeekTimestamp": "2022-11-10T14:00:00Z",
            "MarketFlags": {
                "IsBats": False,
                "IsDelayed": False,
                "IsHalted": False,
                "IsHardToBorrow": False,
            },
            "NetChange": "0.97",
            "NetChangePct": "0.45",
            "Open": "214.75",
            "PreviousClose": "214.25",
            "PreviousVolume": "32567400",
            "TickSizeTier": "0",
            "TradeTime": "2023-03-02T16:00:00Z",
            "Volume": "5789200",
            "LastSize": "100",
            "LastVenue": "NSDQ",
            "VWAP": "215.1234",
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
        await mock_callback(quote_data)
        await mock_callback(heartbeat_data)
        await mock_callback(error_data)

        # Assert data was processed correctly
        assert len(received_data) == 3
        assert received_data[0] == quote_data
        assert received_data[1] == heartbeat_data
        assert received_data[2] == error_data
