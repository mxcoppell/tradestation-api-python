"""
Test suite for the stream_option_chain method in the Market Data Service.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.MarketData.market_data_service import MarketDataService
from src.ts_types.market_data import Spread, Heartbeat, StreamErrorResponse
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


class TestStreamOptionChain:
    """Test cases for the stream_option_chain method."""

    @pytest.mark.asyncio
    async def test_stream_option_chain_with_valid_parameters(
        self, market_data_service, mock_stream_manager
    ):
        """Test streaming option chain with valid parameters."""
        # Arrange
        underlying = "AAPL"
        params = {
            "spreadType": "Butterfly",
            "strikeInterval": 5,
            "expiration": "2024-01-19",
            "strikeProximity": 3,
            "enableGreeks": True,
            "optionType": "Call",
        }

        # Mock the StreamManager.create_stream method
        mock_stream = MagicMock(spec=WebSocketStream)
        mock_stream_manager.create_stream.return_value = mock_stream

        # Act
        result = await market_data_service.stream_option_chain(underlying, params)

        # Assert
        mock_stream_manager.create_stream.assert_called_once_with(
            "/v3/marketdata/stream/options/chains/AAPL",
            params,
            {"headers": {"Accept": "application/vnd.tradestation.streams.v2+json"}},
        )
        assert result == mock_stream

    @pytest.mark.asyncio
    async def test_stream_option_chain_with_no_parameters(
        self, market_data_service, mock_stream_manager
    ):
        """Test streaming option chain without parameters, using default values."""
        # Arrange
        underlying = "MSFT"
        mock_stream = MagicMock(spec=WebSocketStream)
        mock_stream_manager.create_stream.return_value = mock_stream

        # Expected default parameters
        expected_params = {
            "strikeProximity": 5,
            "spreadType": "Single",
            "strikeInterval": 1,
            "enableGreeks": True,
            "strikeRange": "All",
            "optionType": "All",
        }

        # Act
        result = await market_data_service.stream_option_chain(underlying)

        # Assert
        mock_stream_manager.create_stream.assert_called_once_with(
            "/v3/marketdata/stream/options/chains/MSFT",
            expected_params,
            {"headers": {"Accept": "application/vnd.tradestation.streams.v2+json"}},
        )
        assert result == mock_stream

    @pytest.mark.asyncio
    async def test_stream_option_chain_calendar_spread_missing_expiration2(
        self, market_data_service
    ):
        """Test that an error is raised when expiration2 is missing for Calendar spreads."""
        # Arrange
        underlying = "SPY"
        params = {
            "spreadType": "Calendar",
            "expiration": "2024-01-19",
            # Missing expiration2
        }

        # Act & Assert
        with pytest.raises(
            ValueError, match="expiration2 is required for Calendar and Diagonal spreads"
        ):
            await market_data_service.stream_option_chain(underlying, params)

    @pytest.mark.asyncio
    async def test_stream_option_chain_diagonal_spread_missing_expiration2(
        self, market_data_service
    ):
        """Test that an error is raised when expiration2 is missing for Diagonal spreads."""
        # Arrange
        underlying = "SPY"
        params = {
            "spreadType": "Diagonal",
            "expiration": "2024-01-19",
            # Missing expiration2
        }

        # Act & Assert
        with pytest.raises(
            ValueError, match="expiration2 is required for Calendar and Diagonal spreads"
        ):
            await market_data_service.stream_option_chain(underlying, params)

    @pytest.mark.asyncio
    async def test_stream_option_chain_invalid_strike_interval(self, market_data_service):
        """Test that an error is raised when strike interval is less than 1."""
        # Arrange
        underlying = "AAPL"
        params = {"strikeInterval": 0}

        # Act & Assert
        with pytest.raises(ValueError, match="strikeInterval must be greater than or equal to 1"):
            await market_data_service.stream_option_chain(underlying, params)

    @pytest.mark.asyncio
    async def test_stream_option_chain_invalid_risk_free_rate_negative(self, market_data_service):
        """Test that an error is raised when risk-free rate is negative."""
        # Arrange
        underlying = "AAPL"
        params = {"riskFreeRate": -0.01}

        # Act & Assert
        with pytest.raises(
            ValueError, match="riskFreeRate must be a decimal value between 0 and 1"
        ):
            await market_data_service.stream_option_chain(underlying, params)

    @pytest.mark.asyncio
    async def test_stream_option_chain_invalid_risk_free_rate_too_large(self, market_data_service):
        """Test that an error is raised when risk-free rate is greater than 1."""
        # Arrange
        underlying = "AAPL"
        params = {"riskFreeRate": 1.01}

        # Act & Assert
        with pytest.raises(
            ValueError, match="riskFreeRate must be a decimal value between 0 and 1"
        ):
            await market_data_service.stream_option_chain(underlying, params)

    @pytest.mark.asyncio
    async def test_integration_with_websocket_stream(
        self, market_data_service, mock_stream_manager
    ):
        """Test the integration with WebSocketStream for processing option chain data."""
        # Arrange
        underlying = "AAPL"
        mock_stream = AsyncMock(spec=WebSocketStream)

        # Simulate WebSocketStream behavior with callback handling
        mock_callback = None

        def mock_set_callback(callback):
            nonlocal mock_callback
            mock_callback = callback

        mock_stream.set_callback.side_effect = mock_set_callback
        mock_stream_manager.create_stream.return_value = mock_stream

        # Act
        stream = await market_data_service.stream_option_chain(underlying)

        # Define example data messages
        spread_data = {
            "Delta": "0.55",
            "Gamma": "0.03",
            "Theta": "-0.045",
            "Vega": "0.12",
            "Rho": "0.08",
            "ImpliedVolatility": "0.225",
            "IntrinsicValue": "5.75",
            "ExtrinsicValue": "2.25",
            "TheoreticalValue": "8.00",
            "ProbabilityITM": "0.68",
            "ProbabilityOTM": "0.32",
            "ProbabilityBE": "0.42",
            "StandardDeviation": "0.18",
            "DailyOpenInterest": 450,
            "Ask": "8.15",
            "Bid": "7.85",
            "Mid": "8.00",
            "AskSize": 15,
            "BidSize": 20,
            "Close": "7.95",
            "High": "8.25",
            "Last": "8.10",
            "Low": "7.80",
            "NetChange": "+0.15",
            "NetChangePct": "1.89%",
            "Open": "7.95",
            "PreviousClose": "7.95",
            "Volume": 325,
            "Side": "Call",
            "Strikes": ["190", "195", "200"],
            "Legs": [
                {
                    "Symbol": "AAPL 240119C190",
                    "Ratio": 1,
                    "StrikePrice": "190",
                    "Expiration": "2024-01-19",
                    "OptionType": "Call",
                },
                {
                    "Symbol": "AAPL 240119C195",
                    "Ratio": -2,
                    "StrikePrice": "195",
                    "Expiration": "2024-01-19",
                    "OptionType": "Call",
                },
                {
                    "Symbol": "AAPL 240119C200",
                    "Ratio": 1,
                    "StrikePrice": "200",
                    "Expiration": "2024-01-19",
                    "OptionType": "Call",
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
        await mock_callback(spread_data)
        await mock_callback(heartbeat_data)
        await mock_callback(error_data)

        # Assert data was processed correctly
        assert len(received_data) == 3
        assert received_data[0] == spread_data
        assert received_data[1] == heartbeat_data
        assert received_data[2] == error_data
