from unittest.mock import AsyncMock, MagicMock

import pytest

from tradestation.services.MarketData.market_data_service import MarketDataService
from tradestation.ts_types.market_data import QuoteSnapshot


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


class TestQuoteSnapshots:
    """Tests for the quote snapshots functionality in MarketDataService."""

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
