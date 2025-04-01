import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta

from src.client.http_client import HttpClient
from src.services.Brokerage.brokerage_service import BrokerageService
from src.streaming.stream_manager import StreamManager
from src.ts_types.brokerage import (
    HistoricalOrders,
    HistoricalOrder,
    OrderLeg,
    TrailingStop,
    OrderError,
)


@pytest.fixture
def http_client_mock():
    """Create a mock HTTP client for testing"""
    mock = AsyncMock(spec=HttpClient)
    return mock


@pytest.fixture
def stream_manager_mock():
    """Create a mock stream manager for testing"""
    mock = MagicMock(spec=StreamManager)
    return mock


@pytest.fixture
def brokerage_service(http_client_mock, stream_manager_mock):
    """Create a BrokerageService instance with mock dependencies"""
    return BrokerageService(http_client_mock, stream_manager_mock)


class TestGetHistoricalOrders:
    """Tests for the get_historical_orders method in BrokerageService"""

    @pytest.mark.asyncio
    async def test_get_historical_orders_success(self, brokerage_service, http_client_mock):
        """Test successful retrieval of historical orders"""
        # Mock response data
        mock_response = {
            "Orders": [
                {
                    "AccountID": "123456789",
                    "Duration": "DAY",
                    "Legs": [
                        {
                            "AssetType": "STOCK",
                            "BuyOrSell": "Buy",
                            "ExecQuantity": "100",
                            "ExecutionPrice": "150.25",
                            "OpenOrClose": "Open",
                            "QuantityOrdered": "100",
                            "QuantityRemaining": "0",
                            "Symbol": "MSFT",
                        }
                    ],
                    "OpenedDateTime": "2024-03-19T14:30:00Z",
                    "OrderID": "123456",
                    "OrderType": "Market",
                    "Status": "FLL",
                    "StatusDescription": "Filled",
                },
                {
                    "AccountID": "123456789",
                    "Duration": "DAY",
                    "Legs": [
                        {
                            "AssetType": "OPTION",
                            "BuyOrSell": "Buy",
                            "ExecQuantity": "10",
                            "ExecutionPrice": "5.25",
                            "OpenOrClose": "Open",
                            "QuantityOrdered": "10",
                            "QuantityRemaining": "0",
                            "Symbol": "AAPL 240419C180",
                            "ExpirationDate": "2024-04-19",
                            "OptionType": "CALL",
                            "StrikePrice": "180",
                            "Underlying": "AAPL",
                        }
                    ],
                    "OpenedDateTime": "2024-03-18T14:30:00Z",
                    "OrderID": "123457",
                    "OrderType": "Limit",
                    "LimitPrice": "5.25",
                    "Status": "FLL",
                    "StatusDescription": "Filled",
                },
            ],
            "NextToken": "abcdef123456",
        }

        # Configure mock
        http_client_mock.get.return_value = mock_response

        # Call the method
        historical_orders = await brokerage_service.get_historical_orders(
            "123456789",
            "2024-03-01",
            100,
            test_mode=True,  # Enable test mode to bypass date validation
        )

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with(
            "/v3/brokerage/accounts/123456789/historicalorders",
            params={"since": "2024-03-01", "pageSize": 100},
        )

        # Verify the result
        assert isinstance(historical_orders, HistoricalOrders)
        assert len(historical_orders.Orders) == 2
        assert historical_orders.NextToken == "abcdef123456"
        assert historical_orders.Errors is None

        # Verify first order
        assert isinstance(historical_orders.Orders[0], HistoricalOrder)
        assert historical_orders.Orders[0].AccountID == "123456789"
        assert historical_orders.Orders[0].Duration == "DAY"
        assert historical_orders.Orders[0].OpenedDateTime == "2024-03-19T14:30:00Z"
        assert historical_orders.Orders[0].OrderID == "123456"
        assert historical_orders.Orders[0].OrderType == "Market"
        assert historical_orders.Orders[0].Status == "FLL"
        assert historical_orders.Orders[0].StatusDescription == "Filled"

        # Verify first order legs
        assert len(historical_orders.Orders[0].Legs) == 1
        assert isinstance(historical_orders.Orders[0].Legs[0], OrderLeg)
        assert historical_orders.Orders[0].Legs[0].AssetType == "STOCK"
        assert historical_orders.Orders[0].Legs[0].BuyOrSell == "Buy"
        assert historical_orders.Orders[0].Legs[0].ExecQuantity == "100"
        assert historical_orders.Orders[0].Legs[0].ExecutionPrice == "150.25"
        assert historical_orders.Orders[0].Legs[0].OpenOrClose == "Open"
        assert historical_orders.Orders[0].Legs[0].QuantityOrdered == "100"
        assert historical_orders.Orders[0].Legs[0].QuantityRemaining == "0"
        assert historical_orders.Orders[0].Legs[0].Symbol == "MSFT"

        # Verify second order (with option leg)
        assert isinstance(historical_orders.Orders[1], HistoricalOrder)
        assert historical_orders.Orders[1].AccountID == "123456789"
        assert historical_orders.Orders[1].OrderType == "Limit"

        # Verify option leg details
        assert len(historical_orders.Orders[1].Legs) == 1
        assert historical_orders.Orders[1].Legs[0].AssetType == "OPTION"
        assert historical_orders.Orders[1].Legs[0].ExpirationDate == "2024-04-19"
        assert historical_orders.Orders[1].Legs[0].OptionType == "CALL"
        assert historical_orders.Orders[1].Legs[0].StrikePrice == "180"
        assert historical_orders.Orders[1].Legs[0].Underlying == "AAPL"

    @pytest.mark.asyncio
    async def test_get_historical_orders_with_errors(self, brokerage_service, http_client_mock):
        """Test retrieval of historical orders with partial errors"""
        # Mock response with errors
        mock_response = {
            "Orders": [
                {
                    "AccountID": "123456789",
                    "Duration": "DAY",
                    "Legs": [
                        {
                            "AssetType": "STOCK",
                            "BuyOrSell": "Buy",
                            "ExecQuantity": "100",
                            "ExecutionPrice": "150.25",
                            "OpenOrClose": "Open",
                            "QuantityOrdered": "100",
                            "QuantityRemaining": "0",
                            "Symbol": "MSFT",
                        }
                    ],
                    "OpenedDateTime": "2024-03-19T14:30:00Z",
                    "OrderID": "123456",
                    "OrderType": "Market",
                    "Status": "FLL",
                    "StatusDescription": "Filled",
                }
            ],
            "Errors": [
                {
                    "AccountID": "987654321",
                    "Error": "AccountInactive",
                    "Message": "The account is not active or does not exist",
                }
            ],
        }

        # Configure mock
        http_client_mock.get.return_value = mock_response

        # Call the method
        historical_orders = await brokerage_service.get_historical_orders(
            "123456789,987654321",
            "2024-03-01",
            test_mode=True,  # Enable test mode to bypass date validation
        )

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with(
            "/v3/brokerage/accounts/123456789,987654321/historicalorders",
            params={"since": "2024-03-01"},
        )

        # Verify the result
        assert isinstance(historical_orders, HistoricalOrders)
        assert len(historical_orders.Orders) == 1
        assert isinstance(historical_orders.Errors, list)
        assert len(historical_orders.Errors) == 1

        # Verify the successful order
        assert historical_orders.Orders[0].AccountID == "123456789"
        assert historical_orders.Orders[0].OrderID == "123456"

        # Verify the error
        assert isinstance(historical_orders.Errors[0], OrderError)
        assert historical_orders.Errors[0].AccountID == "987654321"
        assert historical_orders.Errors[0].Error == "AccountInactive"
        assert historical_orders.Errors[0].Message == "The account is not active or does not exist"

    @pytest.mark.asyncio
    async def test_get_historical_orders_empty_response(self, brokerage_service, http_client_mock):
        """Test handling of empty orders list"""
        # Mock empty response
        http_client_mock.get.return_value = {"Orders": []}

        # Call the method
        historical_orders = await brokerage_service.get_historical_orders(
            "123456789", "2024-03-01", test_mode=True  # Enable test mode to bypass date validation
        )

        # Verify the result
        assert isinstance(historical_orders, HistoricalOrders)
        assert len(historical_orders.Orders) == 0

    @pytest.mark.asyncio
    async def test_get_historical_orders_with_trailing_stop(
        self, brokerage_service, http_client_mock
    ):
        """Test handling of orders with trailing stop advanced options"""
        # Mock response with trailing stop
        mock_response = {
            "Orders": [
                {
                    "AccountID": "123456789",
                    "Duration": "DAY",
                    "Legs": [
                        {
                            "AssetType": "STOCK",
                            "BuyOrSell": "Sell",
                            "ExecQuantity": "100",
                            "ExecutionPrice": "152.50",
                            "OpenOrClose": "Close",
                            "QuantityOrdered": "100",
                            "QuantityRemaining": "0",
                            "Symbol": "MSFT",
                        }
                    ],
                    "OpenedDateTime": "2024-03-19T14:30:00Z",
                    "OrderID": "123458",
                    "OrderType": "StopMarket",
                    "Status": "FLL",
                    "StatusDescription": "Filled",
                    "StopPrice": "153.00",
                    "AdvancedOptions": '{"TrailingStop":"True","TrailingStopAmount":"1.50"}',
                }
            ]
        }

        # Configure mock
        http_client_mock.get.return_value = mock_response

        # Call the method
        historical_orders = await brokerage_service.get_historical_orders(
            "123456789", "2024-03-01", test_mode=True  # Enable test mode to bypass date validation
        )

        # Verify the order with trailing stop
        assert historical_orders.Orders[0].OrderType == "StopMarket"
        assert historical_orders.Orders[0].StopPrice == "153.00"
        assert isinstance(historical_orders.Orders[0].AdvancedOptions, str)
        assert "TrailingStop" in historical_orders.Orders[0].AdvancedOptions
        assert "TrailingStopAmount" in historical_orders.Orders[0].AdvancedOptions

    @pytest.mark.asyncio
    async def test_get_historical_orders_with_pagination(self, brokerage_service, http_client_mock):
        """Test retrieving historical orders with pagination"""
        # First page response
        first_page = {
            "Orders": [
                {
                    "AccountID": "123456789",
                    "OrderID": "123456",
                    "Status": "FLL",
                    "StatusDescription": "Filled",
                    "Duration": "DAY",
                    "OpenedDateTime": "2024-03-19T14:30:00Z",
                    "OrderType": "Market",
                    "Legs": [
                        {
                            "AssetType": "STOCK",
                            "BuyOrSell": "Buy",
                            "Symbol": "MSFT",
                            "ExecQuantity": "100",
                            "ExecutionPrice": "150.25",
                            "OpenOrClose": "Open",
                            "QuantityOrdered": "100",
                            "QuantityRemaining": "0",
                        }
                    ],
                }
            ],
            "NextToken": "page2token",
        }

        # Second page response
        second_page = {
            "Orders": [
                {
                    "AccountID": "123456789",
                    "OrderID": "123457",
                    "Status": "FLL",
                    "StatusDescription": "Filled",
                    "Duration": "DAY",
                    "OpenedDateTime": "2024-03-18T14:30:00Z",
                    "OrderType": "Market",
                    "Legs": [
                        {
                            "AssetType": "STOCK",
                            "BuyOrSell": "Buy",
                            "Symbol": "AAPL",
                            "ExecQuantity": "50",
                            "ExecutionPrice": "170.50",
                            "OpenOrClose": "Open",
                            "QuantityOrdered": "50",
                            "QuantityRemaining": "0",
                        }
                    ],
                }
            ]
            # No NextToken for last page
        }

        # Configure mock for first call
        http_client_mock.get.return_value = first_page

        # Call the method for first page
        first_result = await brokerage_service.get_historical_orders(
            "123456789",
            "2024-03-01",
            1,
            test_mode=True,  # Enable test mode to bypass date validation
        )

        # Verify first page result
        assert len(first_result.Orders) == 1
        assert first_result.Orders[0].OrderID == "123456"
        assert first_result.NextToken == "page2token"

        # Configure mock for second call with token
        http_client_mock.get.return_value = second_page

        # Call the method for second page
        second_result = await brokerage_service.get_historical_orders(
            "123456789",
            "2024-03-01",
            1,
            "page2token",
            test_mode=True,  # Enable test mode to bypass date validation
        )

        # Verify second page result
        assert len(second_result.Orders) == 1
        assert second_result.Orders[0].OrderID == "123457"
        assert second_result.NextToken is None

        # Verify correct API calls
        assert http_client_mock.get.call_count == 2
        expected_first_call = (
            "/v3/brokerage/accounts/123456789/historicalorders",
            {"params": {"since": "2024-03-01", "pageSize": 1}},
        )
        expected_second_call = (
            "/v3/brokerage/accounts/123456789/historicalorders",
            {"params": {"since": "2024-03-01", "pageSize": 1, "nextToken": "page2token"}},
        )

        first_call = http_client_mock.get.call_args_list[0]
        second_call = http_client_mock.get.call_args_list[1]

        # Check first call arguments
        assert first_call.args[0] == expected_first_call[0]
        assert first_call.kwargs["params"] == expected_first_call[1]["params"]

        # Check second call arguments
        assert second_call.args[0] == expected_second_call[0]
        assert second_call.kwargs["params"] == expected_second_call[1]["params"]

    @pytest.mark.asyncio
    async def test_get_historical_orders_input_validation(self, brokerage_service):
        """Test input validation for the get_historical_orders method"""
        # Test too many account IDs
        too_many_account_ids = ",".join([f"acc{i}" for i in range(30)])
        with pytest.raises(ValueError, match="Maximum of 25 accounts allowed per request"):
            await brokerage_service.get_historical_orders(
                too_many_account_ids,
                "2024-03-01",
                test_mode=True,  # Enable test mode to bypass date validation
            )

        # Test date range exceeding 90 days
        old_date = (datetime.now() - timedelta(days=100)).strftime("%Y-%m-%d")
        with pytest.raises(ValueError, match="Date range cannot exceed 90 days"):
            await brokerage_service.get_historical_orders("123456789", old_date)

        # Test invalid page size
        with pytest.raises(ValueError, match="Page size must be between 1 and 600"):
            await brokerage_service.get_historical_orders(
                "123456789",
                "2024-03-01",
                0,
                test_mode=True,  # Enable test mode to bypass date validation
            )

        with pytest.raises(ValueError, match="Page size must be between 1 and 600"):
            await brokerage_service.get_historical_orders(
                "123456789",
                "2024-03-01",
                601,
                test_mode=True,  # Enable test mode to bypass date validation
            )

        # Test invalid date format
        with pytest.raises(ValueError, match="Invalid date format"):
            await brokerage_service.get_historical_orders("123456789", "03/32/2024")
