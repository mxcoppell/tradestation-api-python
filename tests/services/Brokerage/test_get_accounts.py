import pytest
from unittest.mock import AsyncMock, MagicMock

from src.client.http_client import HttpClient
from src.services.Brokerage.brokerage_service import BrokerageService
from src.streaming.stream_manager import StreamManager
from src.ts_types.brokerage import Account, AccountDetail


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


class TestGetAccounts:
    """Tests for the get_accounts method in BrokerageService"""

    @pytest.mark.asyncio
    async def test_get_accounts_success(self, brokerage_service, http_client_mock):
        """Test successful retrieval of accounts"""
        # Mock response data
        mock_response = {
            "Accounts": [
                {
                    "AccountID": "123456",
                    "AccountType": "Margin",
                    "Alias": "Main Trading",
                    "Currency": "USD",
                    "Status": "Active",
                    "AccountDetail": {
                        "IsStockLocateEligible": False,
                        "EnrolledInRegTProgram": True,
                        "RequiresBuyingPowerWarning": False,
                        "DayTradingQualified": True,
                        "OptionApprovalLevel": 3,
                        "PatternDayTrader": False,
                    },
                },
                {
                    "AccountID": "789012",
                    "AccountType": "Cash",
                    "Currency": "USD",
                    "Status": "Active",
                    "AccountDetail": {
                        "IsStockLocateEligible": False,
                        "EnrolledInRegTProgram": False,
                        "RequiresBuyingPowerWarning": True,
                        "DayTradingQualified": False,
                        "OptionApprovalLevel": 1,
                        "PatternDayTrader": False,
                    },
                },
            ]
        }

        # Configure mock
        http_client_mock.get.return_value = mock_response

        # Call the method
        accounts = await brokerage_service.get_accounts()

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with("/v3/brokerage/accounts")

        # Verify the result
        assert len(accounts) == 2

        # Verify first account
        assert isinstance(accounts[0], Account)
        assert accounts[0].AccountID == "123456"
        assert accounts[0].AccountType == "Margin"
        assert accounts[0].Alias == "Main Trading"
        assert accounts[0].Currency == "USD"
        assert accounts[0].Status == "Active"

        # Verify first account details
        assert isinstance(accounts[0].AccountDetail, AccountDetail)
        assert accounts[0].AccountDetail.IsStockLocateEligible is False
        assert accounts[0].AccountDetail.EnrolledInRegTProgram is True
        assert accounts[0].AccountDetail.RequiresBuyingPowerWarning is False
        assert accounts[0].AccountDetail.DayTradingQualified is True
        assert accounts[0].AccountDetail.OptionApprovalLevel == 3
        assert accounts[0].AccountDetail.PatternDayTrader is False

        # Verify second account
        assert isinstance(accounts[1], Account)
        assert accounts[1].AccountID == "789012"
        assert accounts[1].AccountType == "Cash"
        assert accounts[1].Alias is None  # No alias provided
        assert accounts[1].Currency == "USD"
        assert accounts[1].Status == "Active"

        # Verify second account details
        assert isinstance(accounts[1].AccountDetail, AccountDetail)
        assert accounts[1].AccountDetail.IsStockLocateEligible is False
        assert accounts[1].AccountDetail.EnrolledInRegTProgram is False
        assert accounts[1].AccountDetail.RequiresBuyingPowerWarning is True
        assert accounts[1].AccountDetail.DayTradingQualified is False
        assert accounts[1].AccountDetail.OptionApprovalLevel == 1
        assert accounts[1].AccountDetail.PatternDayTrader is False

    @pytest.mark.asyncio
    async def test_get_accounts_empty_response(self, brokerage_service, http_client_mock):
        """Test handling of empty accounts list"""
        # Mock empty response
        http_client_mock.get.return_value = {"Accounts": []}

        # Call the method
        accounts = await brokerage_service.get_accounts()

        # Verify the result
        assert len(accounts) == 0
        assert isinstance(accounts, list)

    @pytest.mark.asyncio
    async def test_get_accounts_missing_account_detail(self, brokerage_service, http_client_mock):
        """Test handling of accounts without AccountDetail"""
        # Mock response with missing AccountDetail
        mock_response = {
            "Accounts": [
                {
                    "AccountID": "123456",
                    "AccountType": "Futures",
                    "Currency": "USD",
                    "Status": "Active",
                    # No AccountDetail provided
                }
            ]
        }

        # Configure mock
        http_client_mock.get.return_value = mock_response

        # Call the method
        accounts = await brokerage_service.get_accounts()

        # Verify the result
        assert len(accounts) == 1
        assert isinstance(accounts[0], Account)
        assert accounts[0].AccountID == "123456"
        assert accounts[0].AccountType == "Futures"
        assert accounts[0].AccountDetail is None

    @pytest.mark.asyncio
    async def test_get_accounts_api_error(self, brokerage_service, http_client_mock):
        """Test handling of API errors"""
        # Configure mock to raise an exception
        http_client_mock.get.side_effect = Exception("API Error")

        # Call the method and expect the exception to be raised
        with pytest.raises(Exception, match="API Error"):
            await brokerage_service.get_accounts()

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with("/v3/brokerage/accounts")
