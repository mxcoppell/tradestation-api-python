from unittest.mock import AsyncMock, MagicMock

import pytest

from tradestation.services.MarketData.market_data_service import MarketDataService
from tradestation.ts_types.market_data import SymbolDetailsResponse


@pytest.fixture
def http_client_mock():
    """Create a mock HTTP client for testing."""
    mock = AsyncMock()
    return mock


@pytest.fixture
def stream_manager_mock():
    """Create a mock stream manager for testing."""
    mock = MagicMock()
    return mock


@pytest.fixture
def market_data_service(http_client_mock, stream_manager_mock):
    """Create a MarketDataService instance with mock dependencies."""
    return MarketDataService(http_client_mock, stream_manager_mock)


class TestSymbolDetails:
    """Tests for the symbol details functionality in MarketDataService."""

    @pytest.mark.asyncio
    async def test_get_symbol_details_single_symbol(self, market_data_service, http_client_mock):
        """Test getting details for a single symbol."""
        # Arrange
        symbols = ["MSFT"]
        mock_response = {
            "Symbols": [
                {
                    "AssetType": "STOCK",
                    "Country": "US",
                    "Currency": "USD",
                    "Description": "Microsoft Corporation",
                    "Exchange": "NASDAQ",
                    "PriceFormat": {
                        "Format": "Decimal",
                        "Decimals": "2",
                        "IncrementStyle": "Simple",
                        "Increment": "0.01",
                        "PointValue": "1.0",
                    },
                    "QuantityFormat": {
                        "Format": "Decimal",
                        "Decimals": "0",
                        "IncrementStyle": "Simple",
                        "Increment": "1",
                        "MinimumTradeQuantity": "1",
                    },
                    "Root": "MSFT",
                    "Symbol": "MSFT",
                }
            ],
            "Errors": [],
        }
        http_client_mock.get.return_value = mock_response

        # Act
        result = await market_data_service.get_symbol_details(symbols)

        # Assert
        http_client_mock.get.assert_called_once_with("/v3/marketdata/symbols/MSFT")
        assert isinstance(result, SymbolDetailsResponse)
        assert len(result.Symbols) == 1
        assert result.Symbols[0].Symbol == "MSFT"
        assert result.Symbols[0].AssetType == "STOCK"
        assert len(result.Errors) == 0

    @pytest.mark.asyncio
    async def test_get_symbol_details_multiple_symbols(self, market_data_service, http_client_mock):
        """Test getting details for multiple symbols."""
        # Arrange
        symbols = ["MSFT", "AAPL"]
        mock_response = {
            "Symbols": [
                {
                    "AssetType": "STOCK",
                    "Country": "US",
                    "Currency": "USD",
                    "Description": "Microsoft Corporation",
                    "Exchange": "NASDAQ",
                    "PriceFormat": {
                        "Format": "Decimal",
                        "Decimals": "2",
                        "IncrementStyle": "Simple",
                        "Increment": "0.01",
                        "PointValue": "1.0",
                    },
                    "QuantityFormat": {
                        "Format": "Decimal",
                        "Decimals": "0",
                        "IncrementStyle": "Simple",
                        "Increment": "1",
                        "MinimumTradeQuantity": "1",
                    },
                    "Root": "MSFT",
                    "Symbol": "MSFT",
                },
                {
                    "AssetType": "STOCK",
                    "Country": "US",
                    "Currency": "USD",
                    "Description": "Apple Inc.",
                    "Exchange": "NASDAQ",
                    "PriceFormat": {
                        "Format": "Decimal",
                        "Decimals": "2",
                        "IncrementStyle": "Simple",
                        "Increment": "0.01",
                        "PointValue": "1.0",
                    },
                    "QuantityFormat": {
                        "Format": "Decimal",
                        "Decimals": "0",
                        "IncrementStyle": "Simple",
                        "Increment": "1",
                        "MinimumTradeQuantity": "1",
                    },
                    "Root": "AAPL",
                    "Symbol": "AAPL",
                },
            ],
            "Errors": [],
        }
        http_client_mock.get.return_value = mock_response

        # Act
        result = await market_data_service.get_symbol_details(symbols)

        # Assert
        http_client_mock.get.assert_called_once_with("/v3/marketdata/symbols/MSFT,AAPL")
        assert isinstance(result, SymbolDetailsResponse)
        assert len(result.Symbols) == 2
        assert result.Symbols[0].Symbol == "MSFT"
        assert result.Symbols[1].Symbol == "AAPL"
        assert len(result.Errors) == 0

    @pytest.mark.asyncio
    async def test_get_symbol_details_with_errors(self, market_data_service, http_client_mock):
        """Test getting details with some invalid symbols."""
        # Arrange
        symbols = ["MSFT", "INVALID"]
        mock_response = {
            "Symbols": [
                {
                    "AssetType": "STOCK",
                    "Country": "US",
                    "Currency": "USD",
                    "Description": "Microsoft Corporation",
                    "Exchange": "NASDAQ",
                    "PriceFormat": {
                        "Format": "Decimal",
                        "Decimals": "2",
                        "IncrementStyle": "Simple",
                        "Increment": "0.01",
                        "PointValue": "1.0",
                    },
                    "QuantityFormat": {
                        "Format": "Decimal",
                        "Decimals": "0",
                        "IncrementStyle": "Simple",
                        "Increment": "1",
                        "MinimumTradeQuantity": "1",
                    },
                    "Root": "MSFT",
                    "Symbol": "MSFT",
                }
            ],
            "Errors": [{"Symbol": "INVALID", "Message": "Symbol not found"}],
        }
        http_client_mock.get.return_value = mock_response

        # Act
        result = await market_data_service.get_symbol_details(symbols)

        # Assert
        http_client_mock.get.assert_called_once_with("/v3/marketdata/symbols/MSFT,INVALID")
        assert isinstance(result, SymbolDetailsResponse)
        assert len(result.Symbols) == 1
        assert result.Symbols[0].Symbol == "MSFT"
        assert len(result.Errors) == 1
        assert result.Errors[0].Symbol == "INVALID"
        assert result.Errors[0].Message == "Symbol not found"

    @pytest.mark.asyncio
    async def test_get_symbol_details_empty_symbols(self, market_data_service):
        """Test that an error is raised when no symbols are provided."""
        # Act & Assert
        with pytest.raises(ValueError, match="At least one symbol must be provided"):
            await market_data_service.get_symbol_details([])
