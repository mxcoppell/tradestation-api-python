"""
Test suite for the stream_market_depth_aggregates method in the Market Data Service.
"""

import asyncio
import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp

from tradestation.services.MarketData.market_data_service import MarketDataService
from tradestation.ts_types.market_data import (
    MarketDepthAggregate,
    AggregatedQuoteData,
    Heartbeat,
    StreamErrorResponse,
)


@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client with mocked create_stream."""
    client = AsyncMock()
    client.create_stream = AsyncMock()
    return client


@pytest.fixture
def market_data_service(mock_http_client):
    """Create a MarketDataService with mock dependencies."""
    mock_stream_manager = AsyncMock()
    return MarketDataService(mock_http_client, mock_stream_manager)


@pytest.fixture
def mock_stream_reader():
    """Create a mock StreamReader for testing stream consumption."""
    mock = AsyncMock(spec=aiohttp.StreamReader)
    mock.readline = AsyncMock()
    return mock


class TestStreamMarketDepthAggregates:
    """Test cases for the stream_market_depth_aggregates method."""

    @pytest.mark.asyncio
    async def test_stream_with_default_parameters(
        self, market_data_service, mock_http_client, mock_stream_reader
    ):
        """Test streaming with default parameters."""
        # Arrange
        symbol = "MSFT"
        expected_endpoint = f"/v3/marketdata/stream/marketdepth/aggregates/{symbol}"
        expected_headers = {"Accept": "application/vnd.tradestation.streams.v2+json"}
        mock_http_client.create_stream.return_value = mock_stream_reader

        # Act
        result = await market_data_service.stream_market_depth_aggregates(symbol)

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
        params = {"maxlevels": 50}
        expected_endpoint = f"/v3/marketdata/stream/marketdepth/aggregates/{symbol}"
        expected_headers = {"Accept": "application/vnd.tradestation.streams.v2+json"}
        mock_http_client.create_stream.return_value = mock_stream_reader

        # Act
        result = await market_data_service.stream_market_depth_aggregates(symbol, params)

        # Assert
        mock_http_client.create_stream.assert_called_once_with(
            expected_endpoint,
            params=params,
            headers=expected_headers,
        )
        assert result == mock_stream_reader

    @pytest.mark.asyncio
    async def test_stream_invalid_maxlevels_too_low(self, market_data_service):
        """Test that an error is raised for maxlevels < 1."""
        # Arrange
        symbol = "GOOG"
        params = {"maxlevels": 0}  # Invalid level

        # Act & Assert
        with pytest.raises(ValueError, match="maxlevels must be between 1 and 100"):
            await market_data_service.stream_market_depth_aggregates(symbol, params)

    @pytest.mark.asyncio
    async def test_stream_invalid_maxlevels_too_high(self, market_data_service):
        """Test that an error is raised for maxlevels > 100."""
        # Arrange
        symbol = "AMZN"
        params = {"maxlevels": 101}  # Invalid level

        # Act & Assert
        with pytest.raises(ValueError, match="maxlevels must be between 1 and 100"):
            await market_data_service.stream_market_depth_aggregates(symbol, params)

    @pytest.mark.asyncio
    async def test_integration_with_stream_reader(
        self, market_data_service, mock_http_client, mock_stream_reader
    ):
        """Test the integration with StreamReader for processing market depth data."""
        # Arrange
        symbol = "MSFT"
        mock_http_client.create_stream.return_value = mock_stream_reader

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
            ],
        }
        heartbeat_data = {"Heartbeat": 1, "Timestamp": "2023-03-02T14:01:00Z"}
        error_data = {"Error": "InvalidSymbol", "Message": "Symbol not found"}
        non_json_line = b"this is not json\n"
        empty_line = b"\n"

        # Simulate StreamReader behavior
        lines_to_return = [
            json.dumps(market_depth_data).encode("utf-8") + b"\n",
            json.dumps(heartbeat_data).encode("utf-8") + b"\n",
            json.dumps(error_data).encode("utf-8") + b"\n",
            non_json_line,
            empty_line,
            b"",  # Simulate end of stream
        ]
        mock_stream_reader.readline.side_effect = lines_to_return

        # Act: Call the service method to get the stream reader
        stream_reader_result = await market_data_service.stream_market_depth_aggregates(symbol)

        # Assert the stream reader was returned
        assert stream_reader_result == mock_stream_reader

        # Act: Simulate processing the stream reader (similar to test_stream_quotes)
        processed_data = []
        non_json_count = 0
        while True:
            line = await stream_reader_result.readline()
            if not line:
                break
            try:
                line_str = line.strip().decode("utf-8")
                if not line_str:
                    continue
                data = json.loads(line_str)
                processed_data.append(data)
            except json.JSONDecodeError:
                non_json_count += 1
            except UnicodeDecodeError:
                pass

        # Assert data was processed correctly
        assert len(processed_data) == 3
        assert processed_data[0] == market_depth_data
        assert processed_data[1] == heartbeat_data
        assert processed_data[2] == error_data
        assert non_json_count == 1

        # Optional: Add specific validation for market depth data structure if needed
        assert len(processed_data[0]["Bids"]) >= 1
        assert len(processed_data[0]["Asks"]) >= 1
        assert processed_data[0]["Bids"][0]["Price"] == "214.95"
        assert processed_data[0]["Asks"][0]["Price"] == "215.05"
