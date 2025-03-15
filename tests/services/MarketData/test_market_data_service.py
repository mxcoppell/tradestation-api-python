import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.MarketData.market_data_service import MarketDataService
from src.ts_types.market_data import SymbolDetailsResponse, QuoteSnapshot


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


class TestMarketDataService:
    """Tests for the MarketDataService class."""

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

    @pytest.mark.asyncio
    async def test_get_quote_snapshots_single_symbol(self, market_data_service, http_client_mock):
        """Test getting quote snapshots for a single symbol."""
        # Arrange
        symbols = ["MSFT"]
        mock_response = {
            "Quotes": [
                {
                    "Symbol": "MSFT",
                    "Open": "213.65",
                    "High": "215.77",
                    "Low": "212.42",
                    "PreviousClose": "214.46",
                    "Last": "214.75",
                    "Ask": "214.78",
                    "AskSize": "300",
                    "Bid": "214.75",
                    "BidSize": "200",
                    "NetChange": "0.29",
                    "NetChangePct": "0.14",
                    "High52Week": "232.86",
                    "High52WeekTimestamp": "2024-01-01T00:00:00Z",
                    "Low52Week": "132.52",
                    "Low52WeekTimestamp": "2023-01-01T00:00:00Z",
                    "Volume": "5852511",
                    "PreviousVolume": "24154112",
                    "Close": "214.75",
                    "DailyOpenInterest": "0",
                    "TradeTime": "2024-03-14T15:19:14Z",
                    "LastSize": "100",
                    "LastVenue": "NSDQ",
                    "VWAP": "214.23",
                    "TickSizeTier": "0",
                    "MarketFlags": {
                        "IsDelayed": False,
                        "IsHalted": False,
                        "IsBats": False,
                        "IsHardToBorrow": False,
                    },
                }
            ],
            "Errors": [],
        }
        http_client_mock.get.return_value = mock_response

        # Act
        result = await market_data_service.get_quote_snapshots(symbols)

        # Assert
        http_client_mock.get.assert_called_once_with("/v3/marketdata/quotes/MSFT")
        assert isinstance(result, QuoteSnapshot)
        assert len(result.Quotes) == 1
        assert result.Quotes[0].Symbol == "MSFT"
        assert result.Quotes[0].Last == "214.75"
        assert len(result.Errors) == 0

    @pytest.mark.asyncio
    async def test_get_quote_snapshots_multiple_symbols(
        self, market_data_service, http_client_mock
    ):
        """Test getting quote snapshots for multiple symbols."""
        # Arrange
        symbols = ["MSFT", "AAPL"]
        mock_response = {
            "Quotes": [
                {
                    "Symbol": "MSFT",
                    "Open": "213.65",
                    "High": "215.77",
                    "Low": "212.42",
                    "PreviousClose": "214.46",
                    "Last": "214.75",
                    "Ask": "214.78",
                    "AskSize": "300",
                    "Bid": "214.75",
                    "BidSize": "200",
                    "NetChange": "0.29",
                    "NetChangePct": "0.14",
                    "High52Week": "232.86",
                    "High52WeekTimestamp": "2024-01-01T00:00:00Z",
                    "Low52Week": "132.52",
                    "Low52WeekTimestamp": "2023-01-01T00:00:00Z",
                    "Volume": "5852511",
                    "PreviousVolume": "24154112",
                    "Close": "214.75",
                    "DailyOpenInterest": "0",
                    "TradeTime": "2024-03-14T15:19:14Z",
                    "LastSize": "100",
                    "LastVenue": "NSDQ",
                    "VWAP": "214.23",
                    "TickSizeTier": "0",
                    "MarketFlags": {
                        "IsDelayed": False,
                        "IsHalted": False,
                        "IsBats": False,
                        "IsHardToBorrow": False,
                    },
                },
                {
                    "Symbol": "AAPL",
                    "Open": "175.20",
                    "High": "177.35",
                    "Low": "174.98",
                    "PreviousClose": "175.10",
                    "Last": "176.75",
                    "Ask": "176.78",
                    "AskSize": "200",
                    "Bid": "176.75",
                    "BidSize": "100",
                    "NetChange": "1.65",
                    "NetChangePct": "0.94",
                    "High52Week": "198.23",
                    "High52WeekTimestamp": "2023-12-15T00:00:00Z",
                    "Low52Week": "123.64",
                    "Low52WeekTimestamp": "2023-03-15T00:00:00Z",
                    "Volume": "4512367",
                    "PreviousVolume": "15678943",
                    "Close": "176.75",
                    "DailyOpenInterest": "0",
                    "TradeTime": "2024-03-14T15:19:20Z",
                    "LastSize": "200",
                    "LastVenue": "NSDQ",
                    "VWAP": "176.25",
                    "TickSizeTier": "0",
                    "MarketFlags": {
                        "IsDelayed": False,
                        "IsHalted": False,
                        "IsBats": False,
                        "IsHardToBorrow": False,
                    },
                },
            ],
            "Errors": [],
        }
        http_client_mock.get.return_value = mock_response

        # Act
        result = await market_data_service.get_quote_snapshots(symbols)

        # Assert
        http_client_mock.get.assert_called_once_with("/v3/marketdata/quotes/MSFT,AAPL")
        assert isinstance(result, QuoteSnapshot)
        assert len(result.Quotes) == 2
        assert result.Quotes[0].Symbol == "MSFT"
        assert result.Quotes[1].Symbol == "AAPL"
        assert len(result.Errors) == 0

    @pytest.mark.asyncio
    async def test_get_quote_snapshots_with_errors(self, market_data_service, http_client_mock):
        """Test getting quote snapshots with some invalid symbols."""
        # Arrange
        symbols = ["MSFT", "INVALID"]
        mock_response = {
            "Quotes": [
                {
                    "Symbol": "MSFT",
                    "Open": "213.65",
                    "High": "215.77",
                    "Low": "212.42",
                    "PreviousClose": "214.46",
                    "Last": "214.75",
                    "Ask": "214.78",
                    "AskSize": "300",
                    "Bid": "214.75",
                    "BidSize": "200",
                    "NetChange": "0.29",
                    "NetChangePct": "0.14",
                    "High52Week": "232.86",
                    "High52WeekTimestamp": "2024-01-01T00:00:00Z",
                    "Low52Week": "132.52",
                    "Low52WeekTimestamp": "2023-01-01T00:00:00Z",
                    "Volume": "5852511",
                    "PreviousVolume": "24154112",
                    "Close": "214.75",
                    "DailyOpenInterest": "0",
                    "TradeTime": "2024-03-14T15:19:14Z",
                    "LastSize": "100",
                    "LastVenue": "NSDQ",
                    "VWAP": "214.23",
                    "TickSizeTier": "0",
                    "MarketFlags": {
                        "IsDelayed": False,
                        "IsHalted": False,
                        "IsBats": False,
                        "IsHardToBorrow": False,
                    },
                }
            ],
            "Errors": [{"Symbol": "INVALID", "Error": "Symbol not found"}],
        }
        http_client_mock.get.return_value = mock_response

        # Act
        result = await market_data_service.get_quote_snapshots(symbols)

        # Assert
        http_client_mock.get.assert_called_once_with("/v3/marketdata/quotes/MSFT,INVALID")
        assert isinstance(result, QuoteSnapshot)
        assert len(result.Quotes) == 1
        assert result.Quotes[0].Symbol == "MSFT"
        assert len(result.Errors) == 1
        assert result.Errors[0].Symbol == "INVALID"
        assert result.Errors[0].Error == "Symbol not found"

    @pytest.mark.asyncio
    async def test_get_quote_snapshots_too_many_symbols(self, market_data_service):
        """Test that an error is raised when too many symbols are provided."""
        # Arrange
        symbols = ["SYMBOL"] * 101  # Create a list with 101 symbols

        # Act & Assert
        with pytest.raises(ValueError, match="Maximum of 100 symbols allowed per request"):
            await market_data_service.get_quote_snapshots(symbols)
