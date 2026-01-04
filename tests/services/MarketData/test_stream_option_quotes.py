"""
Test suite for the stream_option_quotes method in the Market Data Service.
"""

import json
import re
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

# from tradestation.utils.websocket_stream import WebSocketStream
from pydantic import ValidationError

from tradestation.services.MarketData.market_data_service import MarketDataService
from tradestation.ts_types.market_data import (
    Heartbeat,
    OptionQuoteLeg,
    OptionQuoteParams,
    Spread,
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
    # Pass None or remove the stream_manager argument if no longer needed by the service constructor
    mock_stream_manager = AsyncMock()  # Keep if constructor still requires it
    return MarketDataService(mock_http_client, mock_stream_manager)


@pytest.fixture
def mock_stream_reader():
    """Create a mock StreamReader for testing stream consumption."""
    mock = AsyncMock(spec=aiohttp.StreamReader)
    mock.readline = AsyncMock()  # Will set side_effect in the test
    return mock


class TestStreamOptionQuotes:
    """Test cases for the stream_option_quotes method."""

    @pytest.mark.asyncio
    async def test_stream_with_valid_parameters(
        self, market_data_service, mock_http_client, mock_stream_reader
    ):
        """Test streaming with valid parameters."""
        # Arrange
        legs = [
            OptionQuoteLeg(Symbol="MSFT 240119C400"),
            OptionQuoteLeg(Symbol="MSFT 240119C405", Ratio=-1),
        ]
        params_obj = OptionQuoteParams(legs=legs, riskFreeRate=0.03, enableGreeks=True)

        expected_endpoint = "/v3/marketdata/stream/options/quotes"
        expected_headers = {"Accept": "application/vnd.tradestation.streams.v2+json"}
        expected_query_params = {
            "enableGreeks": "true",
            "riskFreeRate": 0.03,
            "legs[0].Symbol": "MSFT 240119C400",
            "legs[1].Symbol": "MSFT 240119C405",
            "legs[1].Ratio": -1,
        }
        mock_http_client.create_stream.return_value = mock_stream_reader

        # Act
        result = await market_data_service.stream_option_quotes(params_obj)

        # Assert
        mock_http_client.create_stream.assert_called_once_with(
            expected_endpoint,
            params=expected_query_params,
            headers=expected_headers,
        )
        assert result == mock_stream_reader

    @pytest.mark.asyncio
    async def test_stream_with_minimal_parameters(
        self, market_data_service, mock_http_client, mock_stream_reader
    ):
        """Test streaming with only required parameters (legs)."""
        # Arrange
        legs = [OptionQuoteLeg(Symbol="AAPL 241220P180")]
        params_obj = OptionQuoteParams(legs=legs)

        expected_endpoint = "/v3/marketdata/stream/options/quotes"
        expected_headers = {"Accept": "application/vnd.tradestation.streams.v2+json"}
        expected_query_params = {
            "enableGreeks": "true",
            "legs[0].Symbol": "AAPL 241220P180",
        }
        mock_http_client.create_stream.return_value = mock_stream_reader

        # Act
        result = await market_data_service.stream_option_quotes(params_obj)

        # Assert
        mock_http_client.create_stream.assert_called_once_with(
            expected_endpoint,
            params=expected_query_params,
            headers=expected_headers,
        )
        assert result == mock_stream_reader

    @pytest.mark.asyncio
    async def test_stream_no_legs_raises_error(self, market_data_service):
        """Test that ValueError is raised if no legs are provided."""
        with pytest.raises(ValueError, match="At least one leg is required"):
            await market_data_service.stream_option_quotes(OptionQuoteParams(legs=[]))

    @pytest.mark.asyncio
    async def test_stream_invalid_risk_free_rate(self, market_data_service):
        """Test ValueError for riskFreeRate outside [0, 1]."""
        legs = [OptionQuoteLeg(Symbol="GOOG 250117C2000")]
        with pytest.raises(
            ValueError, match="riskFreeRate must be a decimal value between 0 and 1"
        ):
            await market_data_service.stream_option_quotes(
                OptionQuoteParams(legs=legs, riskFreeRate=1.1)
            )
        with pytest.raises(
            ValueError, match="riskFreeRate must be a decimal value between 0 and 1"
        ):
            await market_data_service.stream_option_quotes(
                OptionQuoteParams(legs=legs, riskFreeRate=-0.1)
            )

    @pytest.mark.asyncio
    async def test_stream_invalid_symbol_format(self, market_data_service):
        """Test ValueError for invalid option symbol format."""
        legs = [OptionQuoteLeg(Symbol="MSFT C400")]  # Invalid format
        with pytest.raises(ValueError, match="Invalid option symbol format"):
            await market_data_service.stream_option_quotes(OptionQuoteParams(legs=legs))

    # Rename and refactor this test
    @pytest.mark.asyncio
    async def test_integration_with_stream_reader(
        self, market_data_service, mock_http_client, mock_stream_reader
    ):
        """Test the integration with StreamReader for processing option quote data."""
        # Arrange
        params = OptionQuoteParams(
            legs=[
                OptionQuoteLeg(Symbol="AAPL 240119C190", Ratio=1),
                OptionQuoteLeg(Symbol="AAPL 240119P190", Ratio=1),
            ],
            enableGreeks=True,
        )

        # Mock HttpClient.create_stream to return the mock StreamReader
        mock_http_client.create_stream.return_value = mock_stream_reader

        # Define example data messages
        spread_data = {
            "Delta": "0.55",
            "Gamma": "0.03",
            # ... (rest of spread_data fields) ...
            "Strikes": ["190"],
            "Legs": [
                {
                    "Symbol": "AAPL 240119C190",
                    "Ratio": 1,
                    "StrikePrice": "190",
                    "Expiration": "2024-01-19",
                    "OptionType": "Call",
                },
                {
                    "Symbol": "AAPL 240119P190",
                    "Ratio": 1,
                    "StrikePrice": "190",
                    "Expiration": "2024-01-19",
                    "OptionType": "Put",
                },
            ],
        }
        heartbeat_data = {"Heartbeat": "HeartbeatValue", "Timestamp": "2023-01-01T00:00:00Z"}
        error_data = {"Error": "ErrorValue", "Message": "Error message details", "StatusCode": 400}
        non_json_line = b"this is not json\n"
        empty_line = b"\n"

        # Simulate StreamReader behavior
        lines_to_return = [
            json.dumps(spread_data).encode("utf-8") + b"\n",
            json.dumps(heartbeat_data).encode("utf-8") + b"\n",
            json.dumps(error_data).encode("utf-8") + b"\n",
            non_json_line,
            empty_line,
            b"",  # Simulate end of stream
        ]
        mock_stream_reader.readline.side_effect = lines_to_return

        # Act: Call the service method to get the stream reader
        stream_reader_result = await market_data_service.stream_option_quotes(params)

        # Assert the stream reader was returned
        assert stream_reader_result == mock_stream_reader

        # Act: Simulate processing the stream reader
        processed_data = []
        non_json_count = 0
        while True:
            line = await stream_reader_result.readline()
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
                pass  # Handle if necessary

        # Assert data was processed correctly
        assert len(processed_data) == 3
        assert processed_data[0] == spread_data
        assert processed_data[1] == heartbeat_data
        assert processed_data[2] == error_data
        assert non_json_count == 1

        # Optional: Add specific validation for spread data structure if needed
        assert "Delta" in processed_data[0]
        assert len(processed_data[0]["Legs"]) == 2

    @pytest.mark.asyncio
    async def test_stream_option_quotes_single_leg(
        self, market_data_service, mock_http_client, mock_stream_reader
    ):
        """Test streaming option quotes with a single leg using StreamReader."""
        # Arrange
        params = OptionQuoteParams(
            legs=[OptionQuoteLeg(Symbol="AAPL 240119C190", Ratio=1)], enableGreeks=True
        )

        # Expected query parameters (match the service logic)
        expected_query_params = {
            "enableGreeks": "true",
            "legs[0].Symbol": "AAPL 240119C190",
        }
        if hasattr(params.legs[0], "Ratio") and params.legs[0].Ratio is not None:
            expected_query_params["legs[0].Ratio"] = params.legs[0].Ratio

        expected_endpoint = "/v3/marketdata/stream/options/quotes"
        expected_headers = {"Accept": "application/vnd.tradestation.streams.v2+json"}

        # Mock the HttpClient.create_stream method
        mock_http_client.create_stream.return_value = mock_stream_reader

        # Act
        result = await market_data_service.stream_option_quotes(params)

        # Assert create_stream was called correctly
        mock_http_client.create_stream.assert_called_once_with(
            expected_endpoint,
            params=expected_query_params,
            headers=expected_headers,
        )

        # Assert the StreamReader was returned
        assert result == mock_stream_reader
