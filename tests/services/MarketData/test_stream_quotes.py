"""
Test suite for the stream_quotes method in the Market Data Service.
"""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from tradestation.services.MarketData.market_data_service import MarketDataService
from tradestation.ts_types.market_data import Heartbeat, QuoteStream, StreamErrorResponse

# Remove WebSocketStream import as it's no longer used directly by stream_quotes
# from tradestation.utils.websocket_stream import WebSocketStream


@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client for testing."""
    client = AsyncMock()
    # Mock the create_stream method specifically for these tests
    client.create_stream = AsyncMock()
    return client


@pytest.fixture
def mock_stream_manager():
    """Create a mock StreamManager (kept for other service tests, but not used here)."""
    return AsyncMock()


@pytest.fixture
def market_data_service(mock_http_client, mock_stream_manager):
    """Create a MarketDataService with mock dependencies."""
    return MarketDataService(mock_http_client, mock_stream_manager)


class TestStreamQuotes:
    """Test cases for the stream_quotes method."""

    @pytest.mark.asyncio
    async def test_stream_quotes_with_list_of_symbols(self, market_data_service, mock_http_client):
        """Test streaming quotes with a list of symbols."""
        # Arrange
        symbols = ["MSFT", "AAPL", "GOOGL"]
        expected_url = "/v3/marketdata/stream/quotes/MSFT,AAPL,GOOGL"
        expected_headers = {"Accept": "application/vnd.tradestation.streams.v2+json"}

        mock_stream_reader = AsyncMock(spec=aiohttp.StreamReader)
        mock_http_client.create_stream.return_value = mock_stream_reader

        # Act
        result = await market_data_service.stream_quotes(symbols)

        # Assert
        mock_http_client.create_stream.assert_called_once_with(
            expected_url, params=None, headers=expected_headers  # Explicitly check params is None
        )
        assert result == mock_stream_reader

    @pytest.mark.asyncio
    async def test_stream_quotes_with_string_of_symbols(
        self, market_data_service, mock_http_client
    ):
        """Test streaming quotes with a comma-separated string of symbols."""
        # Arrange
        symbols = "MSFT,AAPL,GOOGL"
        expected_url = "/v3/marketdata/stream/quotes/MSFT,AAPL,GOOGL"
        expected_headers = {"Accept": "application/vnd.tradestation.streams.v2+json"}

        mock_stream_reader = AsyncMock(spec=aiohttp.StreamReader)
        mock_http_client.create_stream.return_value = mock_stream_reader

        # Act
        result = await market_data_service.stream_quotes(symbols)

        # Assert
        mock_http_client.create_stream.assert_called_once_with(
            expected_url, params=None, headers=expected_headers
        )
        assert result == mock_stream_reader

    @pytest.mark.asyncio
    async def test_stream_quotes_with_single_symbol(self, market_data_service, mock_http_client):
        """Test streaming quotes with a single symbol."""
        # Arrange
        symbol = "MSFT"
        expected_url = "/v3/marketdata/stream/quotes/MSFT"
        expected_headers = {"Accept": "application/vnd.tradestation.streams.v2+json"}

        mock_stream_reader = AsyncMock(spec=aiohttp.StreamReader)
        mock_http_client.create_stream.return_value = mock_stream_reader

        # Act
        result = await market_data_service.stream_quotes(symbol)

        # Assert
        mock_http_client.create_stream.assert_called_once_with(
            expected_url, params=None, headers=expected_headers
        )
        assert result == mock_stream_reader

    @pytest.mark.asyncio
    async def test_stream_quotes_with_too_many_symbols(self, market_data_service):
        """Test that an error is raised when more than 100 symbols are provided."""
        # Arrange
        symbols = [f"SYMBOL{i}" for i in range(101)]  # 101 symbols

        # Act & Assert
        with pytest.raises(ValueError, match="Maximum of 100 symbols allowed per request"):
            await market_data_service.stream_quotes(symbols)

    @pytest.mark.asyncio
    async def test_integration_with_stream_reader(self, market_data_service, mock_http_client):
        """Test the integration with StreamReader for processing quote data."""
        # Arrange
        symbols = ["MSFT", "AAPL"]
        mock_stream_reader = AsyncMock(spec=aiohttp.StreamReader)

        # Define example data messages
        quote_data = {"Symbol": "MSFT", "Ask": "215.25", "Bid": "215.20", "Last": "215.22"}
        heartbeat_data = {"Heartbeat": 1, "Timestamp": "2023-03-02T14:01:00Z"}
        error_data = {"Error": "InvalidSymbol", "Message": "Symbol not found"}
        non_json_line = b"this is not json\n"
        empty_line = b"\n"

        # Simulate StreamReader behavior
        lines_to_return = [
            json.dumps(quote_data).encode("utf-8") + b"\n",  # Valid quote
            json.dumps(heartbeat_data).encode("utf-8") + b"\n",  # Valid heartbeat
            json.dumps(error_data).encode("utf-8") + b"\n",  # Valid error
            non_json_line,
            empty_line,
            b"",  # Simulate end of stream
        ]

        mock_stream_reader.readline = AsyncMock(side_effect=lines_to_return)
        mock_http_client.create_stream.return_value = mock_stream_reader

        # Act: Call the service method to get the stream reader
        stream_reader = await market_data_service.stream_quotes(symbols)

        # Assert the stream reader was returned
        assert stream_reader == mock_stream_reader

        # Act: Simulate processing the stream reader (like in the example)
        processed_data = []
        non_json_count = 0
        while True:
            line = await stream_reader.readline()
            if not line:
                break
            try:
                line_str = line.strip().decode("utf-8")
                if not line_str:
                    continue  # Skip empty lines
                data = json.loads(line_str)
                processed_data.append(data)
            except json.JSONDecodeError:
                non_json_count += 1
            except UnicodeDecodeError:
                # Handle potential decode errors if needed
                pass

        # Assert data was processed correctly
        assert len(processed_data) == 3
        assert processed_data[0] == quote_data
        assert processed_data[1] == heartbeat_data
        assert processed_data[2] == error_data
        assert non_json_count == 1
