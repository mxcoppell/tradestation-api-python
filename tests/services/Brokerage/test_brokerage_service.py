import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from tradestation.client.http_client import HttpClient
from tradestation.services.Brokerage.brokerage_service import BrokerageService
from tradestation.streaming.stream_manager import StreamManager
from tradestation.ts_types.brokerage import HistoricalOrdersById


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


class TestGetHistoricalOrdersByOrderID:
    """Tests for the get_historical_orders_by_order_id method"""

    @pytest.mark.asyncio
    async def test_get_historical_orders_by_order_id_success(
        self, brokerage_service, http_client_mock
    ):
        """Test successful retrieval of historical orders by order ID"""
        # Mock response data
        mock_response_data = {
            "Orders": [
                {
                    "AccountID": "123456789",
                    "ClosedDateTime": "2024-01-19T15:30:00Z",
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
                    "OpenedDateTime": "2024-01-19T14:30:00Z",
                    "OrderID": "286234131",
                    "OrderType": "Market",
                    "Status": "FLL",
                    "StatusDescription": "Filled",
                }
            ]
        }

        # Configure mock
        mock_response = AsyncMock()
        mock_response.data = mock_response_data
        http_client_mock.get.return_value = mock_response

        # Call the method with a recent date (within 90 days)
        account_ids = "123456789"
        order_ids = "286234131"
        since = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        result = await brokerage_service.get_historical_orders_by_order_id(
            account_ids, order_ids, since
        )

        # Verify the result
        assert isinstance(result, HistoricalOrdersById)
        assert len(result.Orders) == 1
        assert result.Orders[0].AccountID == "123456789"
        assert result.Orders[0].OrderID == "286234131"
        assert result.Orders[0].Status == "FLL"
        assert result.Orders[0].StatusDescription == "Filled"
        assert len(result.Orders[0].Legs) == 1
        assert result.Orders[0].Legs[0].Symbol == "MSFT"
        assert result.Orders[0].Legs[0].BuyOrSell == "Buy"
        assert result.Orders[0].Legs[0].ExecQuantity == "100"

        # Verify the HTTP client was called correctly
        http_client_mock.get.assert_called_once_with(
            f"/v3/brokerage/accounts/{account_ids}/historicalorders/{order_ids}",
            params={"since": since},
        )

    @pytest.mark.asyncio
    async def test_get_historical_orders_by_order_id_date_validation(self, brokerage_service):
        """Test date validation for historical orders by order ID"""
        # Set a date older than 90 days
        old_date = (datetime.now() - timedelta(days=91)).strftime("%Y-%m-%d")

        # Call the method and expect a ValueError
        with pytest.raises(ValueError, match="Date range cannot exceed 90 days"):
            await brokerage_service.get_historical_orders_by_order_id(
                "123456789", "286234131", old_date
            )

    @pytest.mark.asyncio
    async def test_get_historical_orders_by_order_id_date_formats(
        self, brokerage_service, http_client_mock
    ):
        """Test different date formats for historical orders by order ID"""
        # Mock response
        mock_response = AsyncMock()
        mock_response.data = {"Orders": []}
        http_client_mock.get.return_value = mock_response

        # Get a date within 90 days
        recent_date = datetime.now() - timedelta(days=30)

        # Test different date formats
        valid_dates = [
            recent_date.strftime("%Y-%m-%d"),  # YYYY-MM-DD
            recent_date.strftime("%m-%d-%Y"),  # MM-DD-YYYY
            recent_date.strftime("%Y/%m/%d"),  # YYYY/MM/DD
            recent_date.strftime("%m/%d/%Y"),  # MM/DD/YYYY
        ]

        for date_str in valid_dates:
            # Reset mock
            http_client_mock.get.reset_mock()

            # Call the method
            await brokerage_service.get_historical_orders_by_order_id(
                "123456789", "286234131", date_str
            )

            # Verify the HTTP client was called with the correct parameters
            http_client_mock.get.assert_called_once_with(
                "/v3/brokerage/accounts/123456789/historicalorders/286234131",
                params={"since": date_str},
            )

    @pytest.mark.asyncio
    async def test_get_historical_orders_by_order_id_invalid_date_format(self, brokerage_service):
        """Test invalid date format for historical orders by order ID"""
        # Call the method with an invalid date format
        with pytest.raises(ValueError, match="Invalid date format"):
            await brokerage_service.get_historical_orders_by_order_id(
                "123456789", "286234131", "invalid-date"
            )

    @pytest.mark.asyncio
    async def test_get_historical_orders_by_order_id_with_errors(
        self, brokerage_service, http_client_mock
    ):
        """Test handling of error responses in historical orders by order ID"""
        # Mock response with errors
        mock_response_data = {
            "Orders": [],
            "Errors": [
                {
                    "AccountID": "123456789",
                    "OrderID": "286234131",
                    "Error": "InvalidOrderID",
                    "Message": "Order ID 286234131 not found",
                }
            ],
        }

        # Configure mock
        mock_response = AsyncMock()
        mock_response.data = mock_response_data
        http_client_mock.get.return_value = mock_response

        # Call the method with a recent date (within 90 days)
        since = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        result = await brokerage_service.get_historical_orders_by_order_id(
            "123456789", "286234131", since
        )

        # Verify the result contains the errors
        assert isinstance(result, HistoricalOrdersById)
        assert len(result.Orders) == 0
        assert len(result.Errors) == 1
        assert result.Errors[0].AccountID == "123456789"
        assert result.Errors[0].OrderID == "286234131"
        assert result.Errors[0].Error == "InvalidOrderID"
        assert result.Errors[0].Message == "Order ID 286234131 not found"
