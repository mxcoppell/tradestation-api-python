import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.MarketData.market_data_service import MarketDataService
from src.ts_types.market_data import SymbolDetailsResponse, QuoteSnapshot, SymbolNames, Expirations


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
        """Test handling network errors."""
        # Arrange
        underlying = "MSFT"
        error_message = "Network error"
        http_client_mock.get.side_effect = Exception(error_message)

        # Act & Assert
        with pytest.raises(Exception, match=error_message):
            await market_data_service.get_option_expirations(underlying)
