"""
Test suite for the stream_option_quotes method in the Market Data Service.
"""

import pytest
import re
from unittest.mock import AsyncMock, MagicMock, patch
import json
import aiohttp

from src.services.MarketData.market_data_service import MarketDataService
from src.ts_types.market_data import (
    OptionQuoteParams,
    OptionQuoteLeg,
    Spread,
    Heartbeat,
    StreamErrorResponse,
)
from src.utils.websocket_stream import WebSocketStream
from pydantic import ValidationError


@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client with mocked create_stream."""
    client = AsyncMock()
    client.create_stream = AsyncMock()
    return client


@pytest.fixture
def mock_stream_manager():
    """Create a mock StreamManager for testing."""
    return AsyncMock()


@pytest.fixture
def market_data_service(mock_http_client, mock_stream_manager):
    """Create a MarketDataService with mock dependencies."""
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
            "enableGreeks": True,
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
            "enableGreeks": True,  # Default
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

    @pytest.mark.asyncio
    async def test_integration_with_websocket_stream(
        self, market_data_service, mock_stream_manager
    ):
        """Test the integration with WebSocketStream for processing option quote data."""
        # Arrange
        params = OptionQuoteParams(
            legs=[
                OptionQuoteLeg(Symbol="AAPL 240119C190", Ratio=1),
                OptionQuoteLeg(Symbol="AAPL 240119P190", Ratio=1),
            ],
            enableGreeks=True,
        )

        # Set up mock stream with callback handling
        mock_stream = AsyncMock(spec=WebSocketStream)
        mock_callback = None

        def mock_set_callback(callback):
            nonlocal mock_callback
            mock_callback = callback

        mock_stream.set_callback.side_effect = mock_set_callback
        mock_stream_manager.create_stream.return_value = mock_stream

        # Act
        stream = await market_data_service.stream_option_quotes(params)

        # Define example data messages
        spread_data = {
            "Delta": "0.55",
            "Gamma": "0.03",
            "Theta": "-0.045",
            "Vega": "0.12",
            "Rho": "0.08",
            "ImpliedVolatility": "0.23",
            "IntrinsicValue": "5.25",
            "ExtrinsicValue": "2.75",
            "TheoreticalValue": "8.00",
            "TheoreticalValue_IV": "8.10",
            "ProbabilityITM": "0.65",
            "ProbabilityOTM": "0.35",
            "ProbabilityBE": "0.55",
            "ProbabilityITM_IV": "0.66",
            "ProbabilityOTM_IV": "0.34",
            "ProbabilityBE_IV": "0.56",
            "StandardDeviation": "0.28",
            "DailyOpenInterest": 1250,
            "Ask": "8.15",
            "Bid": "7.95",
            "Mid": "8.05",
            "AskSize": 25,
            "BidSize": 30,
            "Close": "8.10",
            "High": "8.25",
            "Last": "8.05",
            "Low": "7.90",
            "NetChange": "0.05",
            "NetChangePct": "0.62%",
            "Open": "8.00",
            "PreviousClose": "8.00",
            "Volume": 450,
            "Side": "Both",
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

        # Assert stream is properly returned
        assert stream == mock_stream

        # Verify callback processes data correctly (if set)
        if mock_callback:
            # Create a tracking list to verify event handling
            processed_events = []

            async def test_callback(data):
                processed_events.append(data)
                return None

            # Set up a callback and trigger data events
            stream.set_callback(test_callback)

            # Simulate data events
            await mock_callback(spread_data)
            await mock_callback(heartbeat_data)
            await mock_callback(error_data)

            # Verify all events were processed
            assert len(processed_events) == 3
            assert processed_events[0] == spread_data
            assert processed_events[1] == heartbeat_data
            assert processed_events[2] == error_data

    @pytest.mark.asyncio
    async def test_stream_option_quotes_single_leg(self, market_data_service, mock_stream_manager):
        """Test streaming option quotes with a single leg."""
        # Arrange
        params = OptionQuoteParams(
            legs=[OptionQuoteLeg(Symbol="AAPL 240119C190", Ratio=1)], enableGreeks=True
        )

        # Expected query parameters
        expected_query_params = {
            "enableGreeks": True,
            "legs[0].Symbol": "AAPL 240119C190",
            "legs[0].Ratio": 1,
        }

        # Mock the StreamManager.create_stream method
        mock_stream = MagicMock(spec=WebSocketStream)
        mock_stream_manager.create_stream.return_value = mock_stream

        # Act
        result = await market_data_service.stream_option_quotes(params)

        # Assert
        mock_stream_manager.create_stream.assert_called_once_with(
            "/v3/marketdata/stream/options/quotes",
            expected_query_params,
            {"headers": {"Accept": "application/vnd.tradestation.streams.v2+json"}},
        )
        assert result == mock_stream
