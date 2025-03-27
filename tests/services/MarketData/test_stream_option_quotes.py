"""
Test suite for the stream_option_quotes method in the Market Data Service.
"""

import pytest
import re
from unittest.mock import AsyncMock, MagicMock

from src.services.MarketData.market_data_service import MarketDataService
from src.ts_types.market_data import OptionQuoteParams, OptionQuoteLeg
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


class TestStreamOptionQuotes:
    """Test cases for the stream_option_quotes method."""

    @pytest.mark.asyncio
    async def test_stream_option_quotes_with_valid_parameters(
        self, market_data_service, mock_stream_manager
    ):
        """Test streaming option quotes with valid parameters."""
        # Arrange
        params = OptionQuoteParams(
            legs=[
                OptionQuoteLeg(Symbol="MSFT 240119C400", Ratio=1),
                OptionQuoteLeg(Symbol="MSFT 240119C405", Ratio=-2),
                OptionQuoteLeg(Symbol="MSFT 240119C410", Ratio=1),
            ],
            enableGreeks=True,
            riskFreeRate=0.0425,
        )

        # Expected query parameters
        expected_query_params = {
            "enableGreeks": True,
            "riskFreeRate": 0.0425,
            "legs[0].Symbol": "MSFT 240119C400",
            "legs[0].Ratio": 1,
            "legs[1].Symbol": "MSFT 240119C405",
            "legs[1].Ratio": -2,
            "legs[2].Symbol": "MSFT 240119C410",
            "legs[2].Ratio": 1,
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

    @pytest.mark.asyncio
    async def test_stream_option_quotes_with_default_values(
        self, market_data_service, mock_stream_manager
    ):
        """Test streaming option quotes with default parameter values."""
        # Arrange
        params = OptionQuoteParams(
            legs=[
                OptionQuoteLeg(Symbol="SPY 240119C470"),  # Default Ratio=None
                OptionQuoteLeg(Symbol="SPY 240119C475", Ratio=-1),
            ]
            # Default enableGreeks=None, riskFreeRate=None
        )

        # Expected query parameters
        expected_query_params = {
            "enableGreeks": True,  # Default value
            "legs[0].Symbol": "SPY 240119C470",
            # legs[0].Ratio is not included because it's None
            "legs[1].Symbol": "SPY 240119C475",
            "legs[1].Ratio": -1,
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

    @pytest.mark.asyncio
    async def test_stream_option_quotes_no_legs(self, market_data_service):
        """Test that an error is raised when no legs are provided."""
        # Arrange
        params = OptionQuoteParams(legs=[])

        # Act & Assert
        with pytest.raises(ValueError, match="At least one leg is required"):
            await market_data_service.stream_option_quotes(params)

    @pytest.mark.asyncio
    async def test_stream_option_quotes_invalid_risk_free_rate_negative(self, market_data_service):
        """Test that an error is raised when risk-free rate is negative."""
        # Arrange
        params = OptionQuoteParams(
            legs=[OptionQuoteLeg(Symbol="AAPL 240119C190")], riskFreeRate=-0.01
        )

        # Act & Assert
        with pytest.raises(
            ValueError, match="riskFreeRate must be a decimal value between 0 and 1"
        ):
            await market_data_service.stream_option_quotes(params)

    @pytest.mark.asyncio
    async def test_stream_option_quotes_invalid_risk_free_rate_too_large(self, market_data_service):
        """Test that an error is raised when risk-free rate is greater than 1."""
        # Arrange
        params = OptionQuoteParams(
            legs=[OptionQuoteLeg(Symbol="AAPL 240119C190")], riskFreeRate=1.01
        )

        # Act & Assert
        with pytest.raises(
            ValueError, match="riskFreeRate must be a decimal value between 0 and 1"
        ):
            await market_data_service.stream_option_quotes(params)

    @pytest.mark.asyncio
    async def test_stream_option_quotes_invalid_symbol_format(self, market_data_service):
        """Test that an error is raised when option symbol has invalid format."""
        # Arrange
        params = OptionQuoteParams(legs=[OptionQuoteLeg(Symbol="AAPL-INVALID")])

        # Act & Assert
        with pytest.raises(
            ValueError,
            match=re.escape(
                "Invalid option symbol format: AAPL-INVALID. "
                "Expected format: UNDERLYING YYMMDDCSTRIKE or UNDERLYING YYMMDDPSTRIKE"
            ),
        ):
            await market_data_service.stream_option_quotes(params)

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
