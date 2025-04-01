import pytest
from unittest.mock import AsyncMock, MagicMock

from src.client.http_client import HttpClient
from src.services.Brokerage.brokerage_service import BrokerageService
from src.streaming.stream_manager import StreamManager
from src.ts_types.brokerage import (
    BalancesBOD,
    BODBalance,
    BODBalanceDetail,
    BODCurrencyDetail,
    BalanceError,
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


class TestGetBalancesBOD:
    """Tests for the get_balances_bod method in BrokerageService"""

    @pytest.mark.asyncio
    async def test_get_balances_bod_success(self, brokerage_service, http_client_mock):
        """Test successful retrieval of beginning of day account balances"""
        # Mock response data
        mock_response = {
            "BODBalances": [
                {
                    "AccountID": "123456",
                    "AccountType": "Margin",
                    "BalanceDetail": {
                        "AccountBalance": "10000.00",
                        "CashAvailableToWithdraw": "5000.00",
                        "DayTrades": "0",
                        "DayTradingMarginableBuyingPower": "20000.00",
                        "Equity": "15000.00",
                        "NetCash": "5000.00",
                        "OptionBuyingPower": "10000.00",
                        "OptionValue": "0.00",
                        "OvernightBuyingPower": "10000.00",
                    },
                },
                {
                    "AccountID": "789012",
                    "AccountType": "Futures",
                    "CurrencyDetails": [
                        {
                            "Currency": "USD",
                            "AccountMarginRequirement": "1000.00",
                            "AccountOpenTradeEquity": "2000.00",
                            "AccountSecurities": "5000.00",
                            "CashBalance": "30000.00",
                            "MarginRequirement": "1000.00",
                        }
                    ],
                },
            ]
        }

        # Configure mock
        http_client_mock.get.return_value = mock_response

        # Call the method
        balances = await brokerage_service.get_balances_bod("123456,789012")

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with(
            "/v3/brokerage/accounts/123456,789012/bodbalances"
        )

        # Verify the result
        assert isinstance(balances, BalancesBOD)
        assert len(balances.BODBalances) == 2
        assert balances.Errors is None

        # Verify first account balance
        assert isinstance(balances.BODBalances[0], BODBalance)
        assert balances.BODBalances[0].AccountID == "123456"
        assert balances.BODBalances[0].AccountType == "Margin"
        assert balances.BODBalances[0].CurrencyDetails is None

        # Verify first account balance details
        assert isinstance(balances.BODBalances[0].BalanceDetail, BODBalanceDetail)
        assert balances.BODBalances[0].BalanceDetail.AccountBalance == "10000.00"
        assert balances.BODBalances[0].BalanceDetail.CashAvailableToWithdraw == "5000.00"
        assert balances.BODBalances[0].BalanceDetail.DayTrades == "0"
        assert balances.BODBalances[0].BalanceDetail.DayTradingMarginableBuyingPower == "20000.00"
        assert balances.BODBalances[0].BalanceDetail.Equity == "15000.00"
        assert balances.BODBalances[0].BalanceDetail.NetCash == "5000.00"
        assert balances.BODBalances[0].BalanceDetail.OptionBuyingPower == "10000.00"
        assert balances.BODBalances[0].BalanceDetail.OptionValue == "0.00"
        assert balances.BODBalances[0].BalanceDetail.OvernightBuyingPower == "10000.00"

        # Verify second account balance
        assert isinstance(balances.BODBalances[1], BODBalance)
        assert balances.BODBalances[1].AccountID == "789012"
        assert balances.BODBalances[1].AccountType == "Futures"
        assert balances.BODBalances[1].BalanceDetail is None

        # Verify second account currency details
        assert isinstance(balances.BODBalances[1].CurrencyDetails, list)
        assert len(balances.BODBalances[1].CurrencyDetails) == 1
        assert isinstance(balances.BODBalances[1].CurrencyDetails[0], BODCurrencyDetail)
        assert balances.BODBalances[1].CurrencyDetails[0].Currency == "USD"
        assert balances.BODBalances[1].CurrencyDetails[0].AccountMarginRequirement == "1000.00"
        assert balances.BODBalances[1].CurrencyDetails[0].AccountOpenTradeEquity == "2000.00"
        assert balances.BODBalances[1].CurrencyDetails[0].AccountSecurities == "5000.00"
        assert balances.BODBalances[1].CurrencyDetails[0].CashBalance == "30000.00"
        assert balances.BODBalances[1].CurrencyDetails[0].MarginRequirement == "1000.00"

    @pytest.mark.asyncio
    async def test_get_balances_bod_with_errors(self, brokerage_service, http_client_mock):
        """Test retrieval of beginning of day account balances with partial errors"""
        # Mock response with errors
        mock_response = {
            "BODBalances": [
                {
                    "AccountID": "123456",
                    "AccountType": "Margin",
                    "BalanceDetail": {
                        "AccountBalance": "10000.00",
                        "Equity": "15000.00",
                        "NetCash": "5000.00",
                    },
                }
            ],
            "Errors": [
                {
                    "AccountID": "789012",
                    "Error": "AccountInactive",
                    "Message": "The account is not active or does not exist",
                }
            ],
        }

        # Configure mock
        http_client_mock.get.return_value = mock_response

        # Call the method
        balances = await brokerage_service.get_balances_bod("123456,789012")

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with(
            "/v3/brokerage/accounts/123456,789012/bodbalances"
        )

        # Verify the result
        assert isinstance(balances, BalancesBOD)
        assert len(balances.BODBalances) == 1
        assert isinstance(balances.Errors, list)
        assert len(balances.Errors) == 1

        # Verify the successful account balance
        assert balances.BODBalances[0].AccountID == "123456"
        assert balances.BODBalances[0].AccountType == "Margin"
        assert balances.BODBalances[0].BalanceDetail.AccountBalance == "10000.00"
        assert balances.BODBalances[0].BalanceDetail.Equity == "15000.00"
        assert balances.BODBalances[0].BalanceDetail.NetCash == "5000.00"

        # Verify the error
        assert isinstance(balances.Errors[0], BalanceError)
        assert balances.Errors[0].AccountID == "789012"
        assert balances.Errors[0].Error == "AccountInactive"
        assert balances.Errors[0].Message == "The account is not active or does not exist"

    @pytest.mark.asyncio
    async def test_get_balances_bod_empty_response(self, brokerage_service, http_client_mock):
        """Test handling of empty BOD balances list"""
        # Mock empty response
        http_client_mock.get.return_value = {"BODBalances": []}

        # Call the method
        balances = await brokerage_service.get_balances_bod("123456")

        # Verify the result
        assert isinstance(balances, BalancesBOD)
        assert len(balances.BODBalances) == 0

    @pytest.mark.asyncio
    async def test_get_balances_bod_missing_optional_fields(
        self, brokerage_service, http_client_mock
    ):
        """Test handling of BOD balances with missing optional fields"""
        # Mock response with minimal fields
        mock_response = {
            "BODBalances": [
                {
                    "AccountID": "123456",
                    "AccountType": "Cash",
                    # Many optional fields missing
                }
            ]
        }

        # Configure mock
        http_client_mock.get.return_value = mock_response

        # Call the method
        balances = await brokerage_service.get_balances_bod("123456")

        # Verify the result
        assert isinstance(balances, BalancesBOD)
        assert len(balances.BODBalances) == 1
        assert balances.BODBalances[0].AccountID == "123456"
        assert balances.BODBalances[0].AccountType == "Cash"
        assert balances.BODBalances[0].BalanceDetail is None
        assert balances.BODBalances[0].CurrencyDetails is None

    @pytest.mark.asyncio
    async def test_get_balances_bod_api_error(self, brokerage_service, http_client_mock):
        """Test handling of API errors"""
        # Configure mock to raise an exception
        http_client_mock.get.side_effect = Exception("API Error")

        # Call the method and verify exception is raised
        with pytest.raises(Exception) as exc_info:
            await brokerage_service.get_balances_bod("123456")

        # Verify the exception message
        assert "API Error" in str(exc_info.value)
