import pytest
from unittest.mock import AsyncMock, MagicMock

from src.client.http_client import HttpClient
from src.services.Brokerage.brokerage_service import BrokerageService
from src.streaming.stream_manager import StreamManager
from src.ts_types.brokerage import Positions, PositionResponse, PositionError


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


class TestGetPositions:
    """Tests for the get_positions method in BrokerageService"""

    @pytest.mark.asyncio
    async def test_get_positions_for_all_accounts(self, brokerage_service, http_client_mock):
        """Test successful retrieval of positions for multiple accounts"""
        # Mock response data
        mock_response = {
            "Positions": [
                {
                    "AccountID": "123456",
                    "AssetType": "STOCK",
                    "AveragePrice": "150.00",
                    "Bid": "152.00",
                    "Ask": "152.10",
                    "ConversionRate": "1.00",
                    "DayTradeRequirement": "0.00",
                    "InitialRequirement": "7500.00",
                    "MaintenanceMargin": "3750.00",
                    "Last": "152.05",
                    "LongShort": "Long",
                    "MarkToMarketPrice": "152.05",
                    "MarketValue": "15205.00",
                    "PositionID": "POS123",
                    "Quantity": "100",
                    "Symbol": "MSFT",
                    "Timestamp": "2024-01-19T12:00:00Z",
                    "TodaysProfitLoss": "205.00",
                    "TotalCost": "15000.00",
                    "UnrealizedProfitLoss": "205.00",
                    "UnrealizedProfitLossPercent": "1.37",
                    "UnrealizedProfitLossQty": "2.05",
                },
                {
                    "AccountID": "789012",
                    "AssetType": "STOCKOPTION",
                    "AveragePrice": "2.50",
                    "Bid": "2.75",
                    "Ask": "2.80",
                    "ConversionRate": "1.00",
                    "DayTradeRequirement": "0.00",
                    "ExpirationDate": "2024-02-16",
                    "InitialRequirement": "250.00",
                    "MaintenanceMargin": "250.00",
                    "Last": "2.78",
                    "LongShort": "Long",
                    "MarkToMarketPrice": "2.78",
                    "MarketValue": "278.00",
                    "PositionID": "POS456",
                    "Quantity": "1",
                    "Symbol": "MSFT 240216C155",
                    "Timestamp": "2024-01-19T12:00:00Z",
                    "TodaysProfitLoss": "28.00",
                    "TotalCost": "250.00",
                    "UnrealizedProfitLoss": "28.00",
                    "UnrealizedProfitLossPercent": "11.20",
                    "UnrealizedProfitLossQty": "28.00",
                },
            ]
        }

        # Configure mock
        http_client_mock.get.return_value = mock_response

        # Call the method
        result = await brokerage_service.get_positions("123456,789012")

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with(
            "/v3/brokerage/accounts/123456,789012/positions", params={}
        )

        # Verify the result
        assert isinstance(result, Positions)
        assert len(result.Positions) == 2

        # Verify first position
        assert result.Positions[0].AccountID == "123456"
        assert result.Positions[0].AssetType == "STOCK"
        assert result.Positions[0].AveragePrice == "150.00"
        assert result.Positions[0].Bid == "152.00"
        assert result.Positions[0].Ask == "152.10"
        assert result.Positions[0].LongShort == "Long"
        assert result.Positions[0].Symbol == "MSFT"
        assert result.Positions[0].Quantity == "100"
        assert result.Positions[0].MarketValue == "15205.00"
        assert result.Positions[0].UnrealizedProfitLoss == "205.00"

        # Verify second position
        assert result.Positions[1].AccountID == "789012"
        assert result.Positions[1].AssetType == "STOCKOPTION"
        assert result.Positions[1].Symbol == "MSFT 240216C155"
        assert result.Positions[1].ExpirationDate == "2024-02-16"

    @pytest.mark.asyncio
    async def test_get_positions_with_symbol_filter(self, brokerage_service, http_client_mock):
        """Test retrieval of positions filtered by symbol"""
        # Mock response data
        mock_response = {
            "Positions": [
                {
                    "AccountID": "123456",
                    "AssetType": "STOCK",
                    "AveragePrice": "150.00",
                    "Bid": "152.00",
                    "Ask": "152.10",
                    "ConversionRate": "1.00",
                    "DayTradeRequirement": "0.00",
                    "InitialRequirement": "7500.00",
                    "MaintenanceMargin": "3750.00",
                    "Last": "152.05",
                    "LongShort": "Long",
                    "MarkToMarketPrice": "152.05",
                    "MarketValue": "15205.00",
                    "PositionID": "POS123",
                    "Quantity": "100",
                    "Symbol": "MSFT",
                    "Timestamp": "2024-01-19T12:00:00Z",
                    "TodaysProfitLoss": "205.00",
                    "TotalCost": "15000.00",
                    "UnrealizedProfitLoss": "205.00",
                    "UnrealizedProfitLossPercent": "1.37",
                    "UnrealizedProfitLossQty": "2.05",
                }
            ]
        }

        # Configure mock
        http_client_mock.get.return_value = mock_response

        # Call the method with symbol filter
        result = await brokerage_service.get_positions("123456", "MSFT")

        # Verify the API was called correctly with symbol parameter
        http_client_mock.get.assert_called_once_with(
            "/v3/brokerage/accounts/123456/positions", params={"symbol": "MSFT"}
        )

        # Verify the result
        assert isinstance(result, Positions)
        assert len(result.Positions) == 1
        assert result.Positions[0].Symbol == "MSFT"

    @pytest.mark.asyncio
    async def test_get_positions_with_wildcard_symbol(self, brokerage_service, http_client_mock):
        """Test retrieval of positions with wildcard symbol filter"""
        # Mock response data
        mock_response = {
            "Positions": [
                {
                    "AccountID": "123456",
                    "AssetType": "STOCKOPTION",
                    "AveragePrice": "2.50",
                    "Bid": "2.75",
                    "Ask": "2.80",
                    "ConversionRate": "1.00",
                    "DayTradeRequirement": "0.00",
                    "ExpirationDate": "2024-02-16",
                    "InitialRequirement": "250.00",
                    "MaintenanceMargin": "250.00",
                    "Last": "2.78",
                    "LongShort": "Long",
                    "MarkToMarketPrice": "2.78",
                    "MarketValue": "278.00",
                    "PositionID": "POS456",
                    "Quantity": "1",
                    "Symbol": "MSFT 240216C155",
                    "Timestamp": "2024-01-19T12:00:00Z",
                    "TodaysProfitLoss": "28.00",
                    "TotalCost": "250.00",
                    "UnrealizedProfitLoss": "28.00",
                    "UnrealizedProfitLossPercent": "11.20",
                    "UnrealizedProfitLossQty": "28.00",
                }
            ]
        }

        # Configure mock
        http_client_mock.get.return_value = mock_response

        # Call the method with wildcard symbol filter
        result = await brokerage_service.get_positions("123456", "MSFT *")

        # Verify the API was called correctly with symbol parameter containing wildcard
        http_client_mock.get.assert_called_once_with(
            "/v3/brokerage/accounts/123456/positions", params={"symbol": "MSFT *"}
        )

        # Verify the result
        assert isinstance(result, Positions)
        assert len(result.Positions) == 1
        assert result.Positions[0].Symbol == "MSFT 240216C155"

    @pytest.mark.asyncio
    async def test_get_positions_empty_response(self, brokerage_service, http_client_mock):
        """Test handling of empty positions list"""
        # Mock empty response
        http_client_mock.get.return_value = {"Positions": []}

        # Call the method
        result = await brokerage_service.get_positions("123456")

        # Verify the result
        assert isinstance(result, Positions)
        assert len(result.Positions) == 0

    @pytest.mark.asyncio
    async def test_get_positions_error_response(self, brokerage_service, http_client_mock):
        """Test handling of response with errors"""
        # Mock response with error
        mock_response = {
            "Positions": [],
            "Errors": [
                {"AccountID": "INVALID", "Error": "INVALID_ACCOUNT", "Message": "Account not found"}
            ],
        }

        # Configure mock
        http_client_mock.get.return_value = mock_response

        # Call the method
        result = await brokerage_service.get_positions("INVALID")

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with(
            "/v3/brokerage/accounts/INVALID/positions", params={}
        )

        # Verify the result
        assert isinstance(result, Positions)
        assert len(result.Positions) == 0
        assert result.Errors is not None
        assert len(result.Errors) == 1
        assert result.Errors[0].AccountID == "INVALID"
        assert result.Errors[0].Error == "INVALID_ACCOUNT"
        assert result.Errors[0].Message == "Account not found"

    @pytest.mark.asyncio
    async def test_get_positions_api_error(self, brokerage_service, http_client_mock):
        """Test handling of API errors"""
        # Configure mock to raise an exception
        http_client_mock.get.side_effect = Exception("API Error")

        # Call the method and expect the exception to be raised
        with pytest.raises(Exception, match="API Error"):
            await brokerage_service.get_positions("123456")

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with(
            "/v3/brokerage/accounts/123456/positions", params={}
        )

    @pytest.mark.asyncio
    async def test_get_positions_validation_errors(self, brokerage_service):
        """Test input validation errors"""
        # Test too many accounts
        with pytest.raises(ValueError) as excinfo:
            too_many_accounts = ",".join([str(i) for i in range(1, 27)])  # 26 accounts
            await brokerage_service.get_positions(too_many_accounts)
        assert "Maximum of 25 accounts allowed per request" in str(excinfo.value)
