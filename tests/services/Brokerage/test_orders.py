import pytest
from unittest.mock import AsyncMock, MagicMock

from tradestation.client.http_client import HttpClient
from tradestation.services.Brokerage.brokerage_service import BrokerageService
from tradestation.streaming.stream_manager import StreamManager
from tradestation.ts_types.brokerage import (
    Orders,
    Order,
    OrderLeg,
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


class TestGetOrders:
    """Tests for the get_orders method in BrokerageService"""

    @pytest.mark.asyncio
    async def test_get_orders_success(self, brokerage_service, http_client_mock):
        """Test successful retrieval of orders"""
        # Mock response data
        mock_response = {
            "Orders": [
                {
                    "AccountID": "123456",
                    "OrderID": "ORDER123",
                    "Status": "OPN",
                    "StatusDescription": "Sent",
                    "OpenedDateTime": "2024-01-19T12:00:00Z",
                    "OrderType": "Limit",
                    "Duration": "DAY",
                    "LimitPrice": "150.00",
                    "Legs": [
                        {
                            "AssetType": "STOCK",
                            "BuyOrSell": "Buy",
                            "ExecQuantity": "0",
                            "ExecutionPrice": "0.00",
                            "OpenOrClose": "Open",
                            "QuantityOrdered": "100",
                            "QuantityRemaining": "100",
                            "Symbol": "MSFT",
                        }
                    ],
                },
                {
                    "AccountID": "789012",
                    "OrderID": "ORDER456",
                    "Status": "FPR",
                    "StatusDescription": "Partial Fill (Alive)",
                    "OpenedDateTime": "2024-01-19T11:00:00Z",
                    "OrderType": "Market",
                    "Duration": "DAY",
                    "Legs": [
                        {
                            "AssetType": "STOCKOPTION",
                            "BuyOrSell": "Buy",
                            "ExecQuantity": "1",
                            "ExecutionPrice": "2.50",
                            "ExpirationDate": "2024-02-16",
                            "OpenOrClose": "Open",
                            "OptionType": "CALL",
                            "QuantityOrdered": "2",
                            "QuantityRemaining": "1",
                            "StrikePrice": "155.00",
                            "Symbol": "MSFT 240216C155",
                            "Underlying": "MSFT",
                        }
                    ],
                },
            ],
            "NextToken": "NEXT_PAGE_TOKEN",
        }

        # Configure mock
        http_client_mock.get.return_value = mock_response

        # Call the method
        result = await brokerage_service.get_orders("123456,789012", 10)

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with(
            "/v3/brokerage/accounts/123456,789012/orders", params={"pageSize": 10}
        )

        # Verify the result
        assert isinstance(result, Orders)
        assert len(result.Orders) == 2
        assert result.NextToken == "NEXT_PAGE_TOKEN"
        assert result.Errors is None

        # Verify first order
        assert isinstance(result.Orders[0], Order)
        assert result.Orders[0].AccountID == "123456"
        assert result.Orders[0].OrderID == "ORDER123"
        assert result.Orders[0].Status == "OPN"
        assert result.Orders[0].StatusDescription == "Sent"
        assert result.Orders[0].OpenedDateTime == "2024-01-19T12:00:00Z"
        assert result.Orders[0].OrderType == "Limit"
        assert result.Orders[0].Duration == "DAY"
        assert result.Orders[0].LimitPrice == "150.00"

        # Verify first order legs
        assert len(result.Orders[0].Legs) == 1
        assert isinstance(result.Orders[0].Legs[0], OrderLeg)
        assert result.Orders[0].Legs[0].AssetType == "STOCK"
        assert result.Orders[0].Legs[0].BuyOrSell == "Buy"
        assert result.Orders[0].Legs[0].ExecQuantity == "0"
        assert result.Orders[0].Legs[0].ExecutionPrice == "0.00"
        assert result.Orders[0].Legs[0].OpenOrClose == "Open"
        assert result.Orders[0].Legs[0].QuantityOrdered == "100"
        assert result.Orders[0].Legs[0].QuantityRemaining == "100"
        assert result.Orders[0].Legs[0].Symbol == "MSFT"

        # Verify second order (option order)
        assert result.Orders[1].OrderID == "ORDER456"
        assert result.Orders[1].Status == "FPR"
        assert result.Orders[1].StatusDescription == "Partial Fill (Alive)"
        assert result.Orders[1].OrderType == "Market"

        # Verify option leg
        assert result.Orders[1].Legs[0].AssetType == "STOCKOPTION"
        assert result.Orders[1].Legs[0].ExpirationDate == "2024-02-16"
        assert result.Orders[1].Legs[0].OptionType == "CALL"
        assert result.Orders[1].Legs[0].StrikePrice == "155.00"
        assert result.Orders[1].Legs[0].Underlying == "MSFT"

    @pytest.mark.asyncio
    async def test_get_orders_with_pagination(self, brokerage_service, http_client_mock):
        """Test retrieval of orders with pagination"""
        # Mock response for paginated results
        mock_response = {
            "Orders": [
                {
                    "AccountID": "123456",
                    "OrderID": "ORDER789",
                    "Status": "OPN",
                    "StatusDescription": "Sent",
                    "OpenedDateTime": "2024-01-18T12:00:00Z",
                    "OrderType": "Limit",
                    "Duration": "DAY",
                    "LimitPrice": "155.00",
                    "Legs": [
                        {
                            "AssetType": "STOCK",
                            "BuyOrSell": "Sell",
                            "ExecQuantity": "0",
                            "ExecutionPrice": "0.00",
                            "OpenOrClose": "Close",
                            "QuantityOrdered": "50",
                            "QuantityRemaining": "50",
                            "Symbol": "MSFT",
                        }
                    ],
                }
            ]
        }

        # Configure mock
        http_client_mock.get.return_value = mock_response

        # Call the method with pagination parameters
        result = await brokerage_service.get_orders("123456", 10, "NEXT_PAGE_TOKEN")

        # Verify the API was called correctly with pagination parameters
        http_client_mock.get.assert_called_once_with(
            "/v3/brokerage/accounts/123456/orders",
            params={"pageSize": 10, "nextToken": "NEXT_PAGE_TOKEN"},
        )

        # Verify the result
        assert isinstance(result, Orders)
        assert len(result.Orders) == 1
        assert result.NextToken is None  # No more pages
        assert result.Errors is None

    @pytest.mark.asyncio
    async def test_get_orders_with_errors(self, brokerage_service, http_client_mock):
        """Test retrieval of orders with partial errors"""
        # Mock response with errors
        mock_response = {
            "Orders": [
                {
                    "AccountID": "123456",
                    "OrderID": "ORDER123",
                    "Status": "OPN",
                    "StatusDescription": "Sent",
                    "OpenedDateTime": "2024-01-19T12:00:00Z",
                    "OrderType": "Limit",
                    "Duration": "DAY",
                    "LimitPrice": "150.00",
                    "Legs": [
                        {
                            "AssetType": "STOCK",
                            "BuyOrSell": "Buy",
                            "ExecQuantity": "0",
                            "ExecutionPrice": "0.00",
                            "OpenOrClose": "Open",
                            "QuantityOrdered": "100",
                            "QuantityRemaining": "100",
                            "Symbol": "MSFT",
                        }
                    ],
                }
            ],
            "Errors": [
                {"AccountID": "INVALID", "Error": "INVALID_ACCOUNT", "Message": "Account not found"}
            ],
        }

        # Configure mock
        http_client_mock.get.return_value = mock_response

        # Call the method
        result = await brokerage_service.get_orders("123456,INVALID")

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with(
            "/v3/brokerage/accounts/123456,INVALID/orders", params={}
        )

        # Verify the result
        assert isinstance(result, Orders)
        assert len(result.Orders) == 1
        assert len(result.Errors) == 1
        assert result.Errors[0].AccountID == "INVALID"
        assert result.Errors[0].Error == "INVALID_ACCOUNT"
        assert result.Errors[0].Message == "Account not found"

    @pytest.mark.asyncio
    async def test_get_orders_empty_response(self, brokerage_service, http_client_mock):
        """Test empty response handling"""
        # Mock empty response
        mock_response = {"Orders": []}

        # Configure mock
        http_client_mock.get.return_value = mock_response

        # Call the method
        result = await brokerage_service.get_orders("123456")

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with(
            "/v3/brokerage/accounts/123456/orders", params={}
        )

        # Verify the result
        assert isinstance(result, Orders)
        assert len(result.Orders) == 0
        assert result.NextToken is None
        assert result.Errors is None

    @pytest.mark.asyncio
    async def test_get_orders_network_error(self, brokerage_service, http_client_mock):
        """Test network error handling"""
        # Configure mock to raise an exception
        http_client_mock.get.side_effect = Exception("Network error")

        # Call the method and expect an exception
        with pytest.raises(Exception) as excinfo:
            await brokerage_service.get_orders("123456")

        # Verify the exception
        assert "Network error" in str(excinfo.value)

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with(
            "/v3/brokerage/accounts/123456/orders", params={}
        )

    @pytest.mark.asyncio
    async def test_get_orders_validation_errors(self, brokerage_service):
        """Test input validation errors"""
        # Test too many accounts
        with pytest.raises(ValueError) as excinfo:
            too_many_accounts = ",".join([str(i) for i in range(1, 27)])  # 26 accounts
            await brokerage_service.get_orders(too_many_accounts)
        assert "Maximum of 25 accounts allowed per request" in str(excinfo.value)

        # Test invalid page size (too small)
        with pytest.raises(ValueError) as excinfo:
            await brokerage_service.get_orders("123456", 0)
        assert "Page size must be between 1 and 600" in str(excinfo.value)

        # Test invalid page size (too large)
        with pytest.raises(ValueError) as excinfo:
            await brokerage_service.get_orders("123456", 601)
        assert "Page size must be between 1 and 600" in str(excinfo.value)
