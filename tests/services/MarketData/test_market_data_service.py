import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.MarketData.market_data_service import MarketDataService
from src.ts_types.market_data import (
    SymbolDetailsResponse,
    QuoteSnapshot,
    SymbolNames,
    Expirations,
    BarsResponse,
    SpreadTypes,
)


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
            ]
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
    async def test_get_quote_snapshots_string_symbol(self, market_data_service, http_client_mock):
        """Test getting quote snapshots with a string symbol."""
        # Arrange
        symbol = "MSFT"
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
            ]
        }
        http_client_mock.get.return_value = mock_response

        # Act
        result = await market_data_service.get_quote_snapshots(symbol)

        # Assert
        http_client_mock.get.assert_called_once_with("/v3/marketdata/quotes/MSFT")
        assert isinstance(result, QuoteSnapshot)
        assert len(result.Quotes) == 1
        assert result.Quotes[0].Symbol == "MSFT"
        assert result.Quotes[0].Last == "214.75"
        assert len(result.Errors) == 0

    @pytest.mark.asyncio
    async def test_get_quote_snapshots_comma_string(self, market_data_service, http_client_mock):
        """Test getting quote snapshots with a comma-separated string."""
        # Arrange
        symbols = "MSFT,AAPL"
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
            ]
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
            ]
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
    async def test_get_quote_snapshots_missing_errors_field(
        self, market_data_service, http_client_mock
    ):
        """Test getting quote snapshots when the API response is missing the Errors field."""
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
            ]
            # Errors field intentionally omitted
        }
        http_client_mock.get.return_value = mock_response

        # Act
        result = await market_data_service.get_quote_snapshots(symbols)

        # Assert
        http_client_mock.get.assert_called_once_with("/v3/marketdata/quotes/MSFT")
        assert isinstance(result, QuoteSnapshot)
        assert len(result.Quotes) == 1
        assert result.Quotes[0].Symbol == "MSFT"
        # The method should add an empty Errors array
        assert len(result.Errors) == 0

    @pytest.mark.asyncio
    async def test_get_quote_snapshots_too_many_symbols(self, market_data_service):
        """Test that an error is raised when too many symbols are provided."""
        # Arrange
        symbols = ["MSFT"] * 101  # 101 symbols, which exceeds the limit of 100

        # Act & Assert
        with pytest.raises(ValueError, match="Too many symbols"):
            await market_data_service.get_quote_snapshots(symbols)

    @pytest.mark.asyncio
    async def test_get_crypto_symbol_names(self, market_data_service, http_client_mock):
        """Test getting crypto symbol names."""
        # Arrange
        mock_response = {"SymbolNames": ["BTCUSD", "ETHUSD", "LTCUSD", "BCHUSD"]}
        http_client_mock.get.return_value = mock_response

        # Act
        result = await market_data_service.get_crypto_symbol_names()

        # Assert
        http_client_mock.get.assert_called_once_with(
            "/v3/marketdata/symbollists/cryptopairs/symbolnames"
        )
        assert isinstance(result, SymbolNames)
        assert result.SymbolNames == ["BTCUSD", "ETHUSD", "LTCUSD", "BCHUSD"]

    @pytest.mark.asyncio
    async def test_get_option_expirations_without_strike_price(
        self, market_data_service, http_client_mock
    ):
        """Test getting option expirations without strike price."""
        # Arrange
        underlying = "MSFT"
        mock_response = {
            "Expirations": [
                {"Date": "2024-01-19T00:00:00Z", "Type": "Monthly"},
                {"Date": "2024-01-26T00:00:00Z", "Type": "Weekly"},
                {"Date": "2024-02-16T00:00:00Z", "Type": "Monthly"},
                {"Date": "2024-03-15T00:00:00Z", "Type": "Quarterly"},
            ]
        }
        http_client_mock.get.return_value = mock_response

        # Act
        result = await market_data_service.get_option_expirations(underlying)

        # Assert
        http_client_mock.get.assert_called_once_with(
            "/v3/marketdata/options/expirations/MSFT", params={}
        )
        assert isinstance(result, Expirations)
        assert len(result.Expirations) == 4
        assert result.Expirations[0].Date == "2024-01-19T00:00:00Z"
        assert result.Expirations[0].Type == "Monthly"
        assert result.Expirations[1].Type == "Weekly"
        assert result.Expirations[3].Type == "Quarterly"

    @pytest.mark.asyncio
    async def test_get_option_expirations_with_strike_price(
        self, market_data_service, http_client_mock
    ):
        """Test getting option expirations with strike price."""
        # Arrange
        underlying = "MSFT"
        strike_price = 400
        mock_response = {
            "Expirations": [
                {"Date": "2024-01-19T00:00:00Z", "Type": "Monthly"},
                {"Date": "2024-02-16T00:00:00Z", "Type": "Monthly"},
            ]
        }
        http_client_mock.get.return_value = mock_response

        # Act
        result = await market_data_service.get_option_expirations(underlying, strike_price)

        # Assert
        http_client_mock.get.assert_called_once_with(
            "/v3/marketdata/options/expirations/MSFT", params={"strikePrice": 400}
        )
        assert isinstance(result, Expirations)
        assert len(result.Expirations) == 2
        assert result.Expirations[0].Date == "2024-01-19T00:00:00Z"
        assert result.Expirations[0].Type == "Monthly"
        assert result.Expirations[1].Type == "Monthly"

    @pytest.mark.asyncio
    async def test_get_option_expirations_empty_list(self, market_data_service, http_client_mock):
        """Test handling empty expirations list."""
        # Arrange
        underlying = "MSFT"
        mock_response = {"Expirations": []}
        http_client_mock.get.return_value = mock_response

        # Act
        result = await market_data_service.get_option_expirations(underlying)

        # Assert
        http_client_mock.get.assert_called_once_with(
            "/v3/marketdata/options/expirations/MSFT", params={}
        )
        assert isinstance(result, Expirations)
        assert len(result.Expirations) == 0

    @pytest.mark.asyncio
    async def test_get_option_expirations_missing_underlying(self, market_data_service):
        """Test that an error is raised when no underlying symbol is provided."""
        # Act & Assert
        with pytest.raises(ValueError, match="Underlying symbol is required"):
            await market_data_service.get_option_expirations("")

    @pytest.mark.asyncio
    async def test_get_option_expirations_invalid_strike_price(self, market_data_service):
        """Test that an error is raised when strike price is not positive."""
        # Act & Assert
        with pytest.raises(ValueError, match="Strike price must be a positive number"):
            await market_data_service.get_option_expirations("MSFT", -1)

    @pytest.mark.asyncio
    async def test_get_option_expirations_network_error(
        self, market_data_service, http_client_mock
    ):
        """Test that network errors during option expirations fetch are raised."""
        # Arrange
        http_client_mock.get.side_effect = Exception("Network Error")

        # Act & Assert
        with pytest.raises(Exception, match="Network Error"):
            await market_data_service.get_option_expirations("MSFT")

    @pytest.mark.asyncio
    async def test_get_option_spread_types_success(self, market_data_service, http_client_mock):
        """Test successful retrieval of option spread types."""
        # Mock response data
        mock_response_data = {
            "SpreadTypes": [
                {"Name": "Single", "StrikeInterval": False, "ExpirationInterval": False},
                {"Name": "Vertical", "StrikeInterval": True, "ExpirationInterval": False},
                {"Name": "Calendar", "StrikeInterval": False, "ExpirationInterval": True},
                {"Name": "Butterfly", "StrikeInterval": True, "ExpirationInterval": False},
            ]
        }

        # Configure mock response
        http_client_mock.get.return_value = mock_response_data

        # Call the method
        result = await market_data_service.get_option_spread_types()

        # Verify the result
        assert isinstance(result, SpreadTypes)
        assert len(result.SpreadTypes) == 4

        # Verify specific spread types
        assert result.SpreadTypes[0].Name == "Single"
        assert result.SpreadTypes[0].StrikeInterval == False
        assert result.SpreadTypes[0].ExpirationInterval == False

        assert result.SpreadTypes[1].Name == "Vertical"
        assert result.SpreadTypes[1].StrikeInterval == True
        assert result.SpreadTypes[1].ExpirationInterval == False

        assert result.SpreadTypes[2].Name == "Calendar"
        assert result.SpreadTypes[2].StrikeInterval == False
        assert result.SpreadTypes[2].ExpirationInterval == True

        # Verify the API call
        http_client_mock.get.assert_called_once_with("/v3/marketdata/options/spreadtypes")

    @pytest.mark.asyncio
    async def test_get_option_spread_types_empty_response(
        self, market_data_service, http_client_mock
    ):
        """Test handling of empty spread types response."""
        # Mock an empty response
        mock_response_data = {"SpreadTypes": []}

        # Configure mock
        http_client_mock.get.return_value = mock_response_data

        # Call the method
        result = await market_data_service.get_option_spread_types()

        # Verify the result
        assert isinstance(result, SpreadTypes)
        assert len(result.SpreadTypes) == 0

        # Verify the API call
        http_client_mock.get.assert_called_once_with("/v3/marketdata/options/spreadtypes")

    @pytest.mark.asyncio
    async def test_get_option_spread_types_network_error(
        self, market_data_service, http_client_mock
    ):
        """Test handling network errors for get_option_spread_types."""
        # Configure mock to raise an exception
        http_client_mock.get.side_effect = Exception("Network error")

        # Call the method and expect an exception
        with pytest.raises(Exception, match="Network error"):
            await market_data_service.get_option_spread_types()

        # Verify the API call attempt
        http_client_mock.get.assert_called_once_with("/v3/marketdata/options/spreadtypes")

    @pytest.mark.asyncio
    async def test_get_bar_history_daily(self, market_data_service, http_client_mock):
        """Test getting daily bars."""
        # Arrange
        symbol = "MSFT"
        params = {"unit": "Daily", "barsback": 5}

        mock_response = {
            "Bars": [
                {
                    "High": "218.32",
                    "Low": "212.42",
                    "Open": "214.02",
                    "Close": "216.39",
                    "TimeStamp": "2024-01-19T21:00:00Z",
                    "TotalVolume": "42311777",
                    "DownTicks": 231021,
                    "DownVolume": 19575455,
                    "OpenInterest": "0",
                    "IsRealtime": False,
                    "IsEndOfHistory": False,
                    "TotalTicks": 460552,
                    "UpTicks": 229531,
                    "UpVolume": 22736321,
                    "Epoch": 1705694400000,
                    "BarStatus": "Closed",
                },
                {
                    "High": "219.52",
                    "Low": "214.42",
                    "Open": "215.82",
                    "Close": "218.59",
                    "TimeStamp": "2024-01-22T21:00:00Z",
                    "TotalVolume": "38221577",
                    "DownTicks": 210021,
                    "DownVolume": 18775455,
                    "OpenInterest": "0",
                    "IsRealtime": False,
                    "IsEndOfHistory": False,
                    "TotalTicks": 420552,
                    "UpTicks": 210531,
                    "UpVolume": 19446122,
                    "Epoch": 1705953600000,
                    "BarStatus": "Closed",
                },
            ]
        }

        http_client_mock.get.return_value = mock_response

        # Act
        result = await market_data_service.get_bar_history(symbol, params)

        # Assert
        http_client_mock.get.assert_called_once_with(
            f"/v3/marketdata/barcharts/{symbol}", params=params
        )
        assert len(result.Bars) == 2
        assert result.Bars[0].Close == "216.39"
        assert result.Bars[0].High == "218.32"
        assert result.Bars[0].Low == "212.42"
        assert result.Bars[0].Open == "214.02"
        assert result.Bars[0].TotalVolume == "42311777"
        assert result.Bars[0].BarStatus == "Closed"
        assert result.Bars[1].TimeStamp == "2024-01-22T21:00:00Z"

    @pytest.mark.asyncio
    async def test_get_bar_history_minute(self, market_data_service, http_client_mock):
        """Test getting minute bars."""
        # Arrange
        symbol = "MSFT"
        params = {"unit": "Minute", "interval": "5", "barsback": 2}

        mock_response = {
            "Bars": [
                {
                    "High": "388.45",
                    "Low": "388.10",
                    "Open": "388.45",
                    "Close": "388.24",
                    "TimeStamp": "2024-01-22T14:40:00Z",
                    "TotalVolume": "12345",
                    "DownTicks": 32,
                    "DownVolume": 6000,
                    "OpenInterest": "0",
                    "IsRealtime": False,
                    "IsEndOfHistory": False,
                    "TotalTicks": 64,
                    "UpTicks": 32,
                    "UpVolume": 6345,
                    "Epoch": 1705932000000,
                    "BarStatus": "Closed",
                },
                {
                    "High": "388.65",
                    "Low": "388.22",
                    "Open": "388.24",
                    "Close": "388.53",
                    "TimeStamp": "2024-01-22T14:45:00Z",
                    "TotalVolume": "15789",
                    "DownTicks": 42,
                    "DownVolume": 7500,
                    "OpenInterest": "0",
                    "IsRealtime": False,
                    "IsEndOfHistory": False,
                    "TotalTicks": 86,
                    "UpTicks": 44,
                    "UpVolume": 8289,
                    "Epoch": 1705932300000,
                    "BarStatus": "Closed",
                },
            ]
        }

        http_client_mock.get.return_value = mock_response

        # Act
        result = await market_data_service.get_bar_history(symbol, params)

        # Assert
        http_client_mock.get.assert_called_once_with(
            f"/v3/marketdata/barcharts/{symbol}", params=params
        )
        assert len(result.Bars) == 2
        assert result.Bars[0].TimeStamp == "2024-01-22T14:40:00Z"
        assert result.Bars[1].TimeStamp == "2024-01-22T14:45:00Z"
        assert result.Bars[0].Epoch == 1705932000000
        assert result.Bars[1].Epoch == 1705932300000
        assert result.Bars[0].BarStatus == "Closed"
        assert result.Bars[1].BarStatus == "Closed"

    @pytest.mark.asyncio
    async def test_get_bar_history_date_range(self, market_data_service, http_client_mock):
        """Test getting bars for a specific date range."""
        # Arrange
        symbol = "MSFT"
        params = {
            "unit": "Minute",
            "interval": "1",
            "firstdate": "2024-01-22T14:30:00Z",
            "lastdate": "2024-01-22T15:00:00Z",
            "sessiontemplate": "USEQPreAndPost",
        }

        mock_response = {
            "Bars": [
                {
                    "High": "388.45",
                    "Low": "388.10",
                    "Open": "388.45",
                    "Close": "388.24",
                    "TimeStamp": "2024-01-22T14:30:00Z",
                    "TotalVolume": "12345",
                    "DownTicks": 32,
                    "DownVolume": 6000,
                    "OpenInterest": "0",
                    "IsRealtime": False,
                    "IsEndOfHistory": False,
                    "TotalTicks": 64,
                    "UpTicks": 32,
                    "UpVolume": 6345,
                    "Epoch": 1705931400000,
                    "BarStatus": "Closed",
                },
                {
                    "High": "388.65",
                    "Low": "388.22",
                    "Open": "388.24",
                    "Close": "388.53",
                    "TimeStamp": "2024-01-22T15:00:00Z",
                    "TotalVolume": "15789",
                    "DownTicks": 42,
                    "DownVolume": 7500,
                    "OpenInterest": "0",
                    "IsRealtime": False,
                    "IsEndOfHistory": True,
                    "TotalTicks": 86,
                    "UpTicks": 44,
                    "UpVolume": 8289,
                    "Epoch": 1705933200000,
                    "BarStatus": "Closed",
                },
            ]
        }

        http_client_mock.get.return_value = mock_response

        # Act
        result = await market_data_service.get_bar_history(symbol, params)

        # Assert
        http_client_mock.get.assert_called_once_with(
            f"/v3/marketdata/barcharts/{symbol}", params=params
        )
        assert len(result.Bars) == 2
        assert result.Bars[0].TimeStamp == "2024-01-22T14:30:00Z"
        assert result.Bars[1].TimeStamp == "2024-01-22T15:00:00Z"
        assert result.Bars[0].IsEndOfHistory is False
        assert result.Bars[1].IsEndOfHistory is True

    @pytest.mark.asyncio
    async def test_get_bar_history_empty_symbol(self, market_data_service):
        """Test that an empty symbol raises a ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Symbol is required"):
            await market_data_service.get_bar_history("")

    @pytest.mark.asyncio
    async def test_get_bar_history_invalid_interval_non_minute(self, market_data_service):
        """Test that an invalid interval for non-minute bars raises a ValueError."""
        # Arrange
        params = {"unit": "Daily", "interval": "5"}

        # Act & Assert
        with pytest.raises(ValueError, match="Interval must be 1 for non-minute bars"):
            await market_data_service.get_bar_history("MSFT", params)

    @pytest.mark.asyncio
    async def test_get_bar_history_invalid_minute_interval(self, market_data_service):
        """Test that an invalid minute interval raises a ValueError."""
        # Arrange
        params = {"unit": "Minute", "interval": "1500"}  # Exceeds max of 1440

        # Act & Assert
        with pytest.raises(ValueError, match="Maximum interval for minute bars is 1440"):
            await market_data_service.get_bar_history("MSFT", params)

    @pytest.mark.asyncio
    async def test_get_bar_history_too_many_bars(self, market_data_service):
        """Test that too many requested intraday bars raises a ValueError."""
        # Arrange
        params = {"unit": "Minute", "barsback": 60000}  # Exceeds max of 57600

        # Act & Assert
        with pytest.raises(ValueError, match="Maximum of 57,600 intraday bars allowed per request"):
            await market_data_service.get_bar_history("MSFT", params)

    @pytest.mark.asyncio
    async def test_get_bar_history_mutually_exclusive_params(self, market_data_service):
        """Test that mutually exclusive parameters raise a ValueError."""
        # Arrange
        params = {"barsback": 10, "firstdate": "2024-01-22T14:30:00Z"}

        # Act & Assert
        with pytest.raises(
            ValueError, match="barsback and firstdate parameters are mutually exclusive"
        ):
            await market_data_service.get_bar_history("MSFT", params)

    @pytest.mark.asyncio
    async def test_get_bar_history_deprecated_param(self, market_data_service):
        """Test that deprecated 'startdate' parameter raises a ValueError when used with 'lastdate'."""
        # Arrange
        params = {"lastdate": "2024-01-22T15:00:00Z", "startdate": "2024-01-22T14:30:00Z"}

        # Act & Assert
        with pytest.raises(
            ValueError, match="lastdate and startdate parameters are mutually exclusive"
        ):
            await market_data_service.get_bar_history("MSFT", params)

    @pytest.mark.asyncio
    async def test_get_bar_history_none_params(self, market_data_service, http_client_mock):
        """Test getting bars with None params (should use defaults)."""
        # Arrange
        symbol = "MSFT"
        mock_response = {
            "Bars": [
                {
                    "High": "388.45",
                    "Low": "388.10",
                    "Open": "388.45",
                    "Close": "388.24",
                    "TimeStamp": "2024-01-22T14:40:00Z",
                    "TotalVolume": "12345",
                    "DownTicks": 32,
                    "DownVolume": 6000,
                    "OpenInterest": "0",
                    "IsRealtime": False,
                    "IsEndOfHistory": True,
                    "TotalTicks": 64,
                    "UpTicks": 32,
                    "UpVolume": 6345,
                    "Epoch": 1705932000000,
                    "BarStatus": "Closed",
                }
            ]
        }

        http_client_mock.get.return_value = mock_response

        # Act
        result = await market_data_service.get_bar_history(symbol, None)

        # Assert
        http_client_mock.get.assert_called_once_with(
            f"/v3/marketdata/barcharts/{symbol}", params={}
        )
        assert len(result.Bars) == 1

    @pytest.mark.asyncio
    async def test_get_bar_history_network_error(self, market_data_service, http_client_mock):
        """Test that network errors during bar history fetch are raised."""
        # Arrange
        http_client_mock.get.side_effect = Exception("Network Error")

        # Act & Assert
        with pytest.raises(Exception, match="Network Error"):
            await market_data_service.get_bar_history("MSFT")
