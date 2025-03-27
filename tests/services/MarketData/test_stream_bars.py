"""
Test suite for the stream_bars method in the Market Data Service.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.MarketData.market_data_service import MarketDataService
from src.ts_types.market_data import Bar, Heartbeat, StreamErrorResponse
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


class TestStreamBars:
    """Test cases for the stream_bars method."""

    @pytest.mark.asyncio
    async def test_stream_bars_with_valid_parameters(
        self, market_data_service, mock_stream_manager
    ):
        """Test streaming bars with valid parameters."""
        # Arrange
        symbol = "MSFT"
        params = {
            "unit": "Minute",
            "interval": "5",
            "barsback": 100,
            "sessiontemplate": "USEQPreAndPost",
        }

        # Mock the StreamManager.create_stream method
        mock_stream = MagicMock(spec=WebSocketStream)
        mock_stream_manager.create_stream.return_value = mock_stream

        # Act
        result = await market_data_service.stream_bars(symbol, params)

        # Assert
        mock_stream_manager.create_stream.assert_called_once_with(
            "/v3/marketdata/stream/barcharts/MSFT",
            params,
            {"headers": {"Accept": "application/vnd.tradestation.streams.v2+json"}},
        )
        assert result == mock_stream

    @pytest.mark.asyncio
    async def test_stream_bars_with_no_parameters(self, market_data_service, mock_stream_manager):
        """Test streaming bars without parameters."""
        # Arrange
        symbol = "AAPL"
        mock_stream = MagicMock(spec=WebSocketStream)
        mock_stream_manager.create_stream.return_value = mock_stream

        # Act
        result = await market_data_service.stream_bars(symbol)

        # Assert
        mock_stream_manager.create_stream.assert_called_once_with(
            "/v3/marketdata/stream/barcharts/AAPL",
            {},
            {"headers": {"Accept": "application/vnd.tradestation.streams.v2+json"}},
        )
        assert result == mock_stream

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

    @pytest.mark.asyncio
    async def test_integration_with_websocket_stream(
        self, market_data_service, mock_stream_manager
    ):
        """Test the integration with WebSocketStream for processing bar data."""
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
        stream = await market_data_service.stream_bars(symbol)

        # Define example data messages
        bar_data = {
            "Close": "215.25",
            "DownTicks": 123,
            "DownVolume": 15000,
            "Epoch": 1614688800000,
            "High": "216.50",
            "IsEndOfHistory": False,
            "IsRealtime": True,
            "Low": "214.75",
            "Open": "215.00",
            "OpenInterest": "0",
            "TimeStamp": "2023-03-02T14:00:00Z",
            "TotalTicks": 450,
            "TotalVolume": "50000",
            "UpTicks": 327,
            "UpVolume": 35000,
            "BarStatus": "Open",
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
        await mock_callback(bar_data)
        await mock_callback(heartbeat_data)
        await mock_callback(error_data)

        # Assert data was processed correctly
        assert len(received_data) == 3
        assert received_data[0] == bar_data
        assert received_data[1] == heartbeat_data
        assert received_data[2] == error_data
