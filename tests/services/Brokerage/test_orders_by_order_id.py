import pytest
from unittest.mock import AsyncMock, MagicMock

from src.client.http_client import HttpClient
from src.services.Brokerage.brokerage_service import BrokerageService
from src.streaming.stream_manager import StreamManager
from src.ts_types.brokerage import (
    OrdersById,
    Order,
    OrderLeg,
    OrderByIDError,
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


class TestGetOrdersByOrderID:
    """Tests for the get_orders_by_order_id method in BrokerageService"""

    @pytest.mark.asyncio
    async def test_get_orders_by_order_id_success(self, brokerage_service, http_client_mock):
        """Test successful retrieval of orders by order ID"""
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
            ]
        }

        # Configure mock
        http_client_mock.get.return_value = mock_response

        # Call the method
        result = await brokerage_service.get_orders_by_order_id(
            "123456,789012", "ORDER123,ORDER456"
        )

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with(
            "/v3/brokerage/accounts/123456,789012/orders/ORDER123,ORDER456"
        )

        # Verify the result
        assert isinstance(result, OrdersById)
        assert len(result.Orders) == 2
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
    async def test_get_orders_by_order_id_with_errors(self, brokerage_service, http_client_mock):
        """Test retrieval of orders by order ID with errors"""
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
                {
                    "AccountID": "789012",
                    "OrderID": "INVALID",
                    "Error": "INVALID_ORDER",
                    "Message": "Order not found",
                }
            ],
        }

        # Configure mock
        http_client_mock.get.return_value = mock_response

        # Call the method
        result = await brokerage_service.get_orders_by_order_id("123456,789012", "ORDER123,INVALID")

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with(
            "/v3/brokerage/accounts/123456,789012/orders/ORDER123,INVALID"
        )

        # Verify the result
        assert isinstance(result, OrdersById)
        assert len(result.Orders) == 1
        assert len(result.Errors) == 1
        assert result.Errors[0].AccountID == "789012"
        assert result.Errors[0].OrderID == "INVALID"
        assert result.Errors[0].Error == "INVALID_ORDER"
        assert result.Errors[0].Message == "Order not found"

    @pytest.mark.asyncio
    async def test_get_orders_by_order_id_empty_response(self, brokerage_service, http_client_mock):
        """Test retrieval of orders by order ID with empty response"""
        # Mock empty response
        mock_response = {"Orders": []}

        # Configure mock
        http_client_mock.get.return_value = mock_response

        # Call the method
        result = await brokerage_service.get_orders_by_order_id("123456", "ORDER123")

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with(
            "/v3/brokerage/accounts/123456/orders/ORDER123"
        )

        # Verify the result
        assert isinstance(result, OrdersById)
        assert len(result.Orders) == 0
        assert result.Errors is None

    @pytest.mark.asyncio
    async def test_get_orders_by_order_id_network_error(self, brokerage_service, http_client_mock):
        """Test network error handling when retrieving orders by order ID"""
        # Configure mock to raise exception
        http_client_mock.get.side_effect = Exception("Network error")

        # Verify the exception is propagated
        with pytest.raises(Exception, match="Network error"):
            await brokerage_service.get_orders_by_order_id("123456", "ORDER123")

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with(
            "/v3/brokerage/accounts/123456/orders/ORDER123"
        )

    @pytest.mark.asyncio
    async def test_get_orders_by_order_id_validation_errors(self, brokerage_service):
        """Test input validation errors"""
        # Test too many accounts
        with pytest.raises(ValueError) as excinfo:
            too_many_accounts = ",".join([str(i) for i in range(1, 27)])  # 26 accounts
            await brokerage_service.get_orders_by_order_id(too_many_accounts, "ORDER123")
        assert "Maximum of 25 accounts allowed per request" in str(excinfo.value)

        # Test too many order IDs
        with pytest.raises(ValueError) as excinfo:
            too_many_orders = ",".join([f"ORDER{i}" for i in range(1, 52)])  # 51 orders
            await brokerage_service.get_orders_by_order_id("123456", too_many_orders)
        assert "Maximum of 50 order IDs allowed per request" in str(excinfo.value)
