from unittest.mock import AsyncMock, MagicMock

import pytest

from tradestation.client.http_client import HttpClient
from tradestation.services.Brokerage.brokerage_service import BrokerageService
from tradestation.streaming.stream_manager import StreamManager
from tradestation.ts_types.brokerage import (
    Balance,
    BalanceDetail,
    BalanceError,
    Balances,
    CurrencyDetail,
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


class TestGetBalances:
    """Tests for the get_balances method in BrokerageService"""

    @pytest.mark.asyncio
    async def test_get_balances_success(self, brokerage_service, http_client_mock):
        """Test successful retrieval of account balances"""
        # Mock response data
        mock_response = {
            "Balances": [
                {
                    "AccountID": "123456",
                    "AccountType": "Margin",
                    "BuyingPower": "20000.00",
                    "CashBalance": "10000.00",
                    "Commission": "0.00",
                    "Equity": "15000.00",
                    "MarketValue": "5000.00",
                    "TodaysProfitLoss": "500.00",
                    "UnclearedDeposit": "0.00",
                    "BalanceDetail": {
                        "CostOfPositions": "4500.00",
                        "DayTradeExcess": "0.00",
                        "DayTradeMargin": "0.00",
                        "DayTradeOpenOrderMargin": "0.00",
                        "DayTrades": "0",
                        "InitialMargin": "2500.00",
                        "MaintenanceMargin": "1250.00",
                        "MaintenanceRate": "0.25",
                        "MarginRequirement": "2500.00",
                        "UnrealizedProfitLoss": "500.00",
                        "UnsettledFunds": "0.00",
                    },
                },
                {
                    "AccountID": "789012",
                    "AccountType": "Futures",
                    "BuyingPower": "50000.00",
                    "CashBalance": "30000.00",
                    "Commission": "10.50",
                    "Equity": "35000.00",
                    "MarketValue": "5000.00",
                    "TodaysProfitLoss": "-200.00",
                    "CurrencyDetails": [
                        {
                            "Currency": "USD",
                            "BODOpenTradeEquity": "0.00",
                            "CashBalance": "30000.00",
                            "Commission": "10.50",
                            "MarginRequirement": "1000.00",
                            "NonTradeDebit": "0.00",
                            "NonTradeNetBalance": "0.00",
                            "OptionValue": "0.00",
                            "RealTimeUnrealizedGains": "-200.00",
                            "TodayRealTimeTradeEquity": "-200.00",
                            "TradeEquity": "5000.00",
                        }
                    ],
                },
            ]
        }

        # Configure mock
        http_client_mock.get.return_value = mock_response

        # Call the method
        balances = await brokerage_service.get_balances("123456,789012")

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with(
            "/v3/brokerage/accounts/123456,789012/balances"
        )

        # Verify the result
        assert isinstance(balances, Balances)
        assert len(balances.Balances) == 2
        assert balances.Errors is None

        # Verify first account balance
        assert isinstance(balances.Balances[0], Balance)
        assert balances.Balances[0].AccountID == "123456"
        assert balances.Balances[0].AccountType == "Margin"
        assert balances.Balances[0].BuyingPower == "20000.00"
        assert balances.Balances[0].CashBalance == "10000.00"
        assert balances.Balances[0].Commission == "0.00"
        assert balances.Balances[0].Equity == "15000.00"
        assert balances.Balances[0].MarketValue == "5000.00"
        assert balances.Balances[0].TodaysProfitLoss == "500.00"
        assert balances.Balances[0].UnclearedDeposit == "0.00"
        assert balances.Balances[0].CurrencyDetails is None

        # Verify first account balance details
        assert isinstance(balances.Balances[0].BalanceDetail, BalanceDetail)
        assert balances.Balances[0].BalanceDetail.CostOfPositions == "4500.00"
        assert balances.Balances[0].BalanceDetail.DayTradeExcess == "0.00"
        assert balances.Balances[0].BalanceDetail.DayTradeMargin == "0.00"
        assert balances.Balances[0].BalanceDetail.DayTradeOpenOrderMargin == "0.00"
        assert balances.Balances[0].BalanceDetail.DayTrades == "0"
        assert balances.Balances[0].BalanceDetail.InitialMargin == "2500.00"
        assert balances.Balances[0].BalanceDetail.MaintenanceMargin == "1250.00"
        assert balances.Balances[0].BalanceDetail.MaintenanceRate == "0.25"
        assert balances.Balances[0].BalanceDetail.MarginRequirement == "2500.00"
        assert balances.Balances[0].BalanceDetail.UnrealizedProfitLoss == "500.00"
        assert balances.Balances[0].BalanceDetail.UnsettledFunds == "0.00"

        # Verify second account balance
        assert isinstance(balances.Balances[1], Balance)
        assert balances.Balances[1].AccountID == "789012"
        assert balances.Balances[1].AccountType == "Futures"
        assert balances.Balances[1].BuyingPower == "50000.00"
        assert balances.Balances[1].CashBalance == "30000.00"
        assert balances.Balances[1].Commission == "10.50"
        assert balances.Balances[1].Equity == "35000.00"
        assert balances.Balances[1].MarketValue == "5000.00"
        assert balances.Balances[1].TodaysProfitLoss == "-200.00"
        assert balances.Balances[1].BalanceDetail is None

        # Verify second account currency details
        assert isinstance(balances.Balances[1].CurrencyDetails, list)
        assert len(balances.Balances[1].CurrencyDetails) == 1
        assert isinstance(balances.Balances[1].CurrencyDetails[0], CurrencyDetail)
        assert balances.Balances[1].CurrencyDetails[0].Currency == "USD"
        assert balances.Balances[1].CurrencyDetails[0].BODOpenTradeEquity == "0.00"
        assert balances.Balances[1].CurrencyDetails[0].CashBalance == "30000.00"
        assert balances.Balances[1].CurrencyDetails[0].Commission == "10.50"
        assert balances.Balances[1].CurrencyDetails[0].MarginRequirement == "1000.00"
        assert balances.Balances[1].CurrencyDetails[0].NonTradeDebit == "0.00"
        assert balances.Balances[1].CurrencyDetails[0].NonTradeNetBalance == "0.00"
        assert balances.Balances[1].CurrencyDetails[0].OptionValue == "0.00"
        assert balances.Balances[1].CurrencyDetails[0].RealTimeUnrealizedGains == "-200.00"
        assert balances.Balances[1].CurrencyDetails[0].TodayRealTimeTradeEquity == "-200.00"
        assert balances.Balances[1].CurrencyDetails[0].TradeEquity == "5000.00"

    @pytest.mark.asyncio
    async def test_get_balances_with_errors(self, brokerage_service, http_client_mock):
        """Test retrieval of account balances with partial errors"""
        # Mock response with errors
        mock_response = {
            "Balances": [
                {
                    "AccountID": "123456",
                    "AccountType": "Margin",
                    "BuyingPower": "20000.00",
                    "CashBalance": "10000.00",
                    "Equity": "15000.00",
                    "MarketValue": "5000.00",
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
        balances = await brokerage_service.get_balances("123456,789012")

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with(
            "/v3/brokerage/accounts/123456,789012/balances"
        )

        # Verify the result
        assert isinstance(balances, Balances)
        assert len(balances.Balances) == 1
        assert isinstance(balances.Errors, list)
        assert len(balances.Errors) == 1

        # Verify the successful account balance
        assert balances.Balances[0].AccountID == "123456"
        assert balances.Balances[0].AccountType == "Margin"
        assert balances.Balances[0].BuyingPower == "20000.00"
        assert balances.Balances[0].CashBalance == "10000.00"
        assert balances.Balances[0].Equity == "15000.00"
        assert balances.Balances[0].MarketValue == "5000.00"

        # Verify the error
        assert isinstance(balances.Errors[0], BalanceError)
        assert balances.Errors[0].AccountID == "789012"
        assert balances.Errors[0].Error == "AccountInactive"
        assert balances.Errors[0].Message == "The account is not active or does not exist"

    @pytest.mark.asyncio
    async def test_get_balances_empty_response(self, brokerage_service, http_client_mock):
        """Test handling of empty balances list"""
        # Mock empty response
        http_client_mock.get.return_value = {"Balances": []}

        # Call the method
        balances = await brokerage_service.get_balances("123456")

        # Verify the result
        assert isinstance(balances, Balances)
        assert len(balances.Balances) == 0

    @pytest.mark.asyncio
    async def test_get_balances_missing_optional_fields(self, brokerage_service, http_client_mock):
        """Test handling of balances with missing optional fields"""
        # Mock response with minimal fields
        mock_response = {
            "Balances": [
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
        balances = await brokerage_service.get_balances("123456")

        # Verify the result
        assert isinstance(balances, Balances)
        assert len(balances.Balances) == 1
        assert balances.Balances[0].AccountID == "123456"
        assert balances.Balances[0].AccountType == "Cash"
        assert balances.Balances[0].BuyingPower is None
        assert balances.Balances[0].CashBalance is None
        assert balances.Balances[0].BalanceDetail is None
        assert balances.Balances[0].CurrencyDetails is None

    @pytest.mark.asyncio
    async def test_get_balances_api_error(self, brokerage_service, http_client_mock):
        """Test handling of API errors"""
        # Configure mock to raise an exception
        http_client_mock.get.side_effect = Exception("API Error")

        # Call the method and expect the exception to be raised
        with pytest.raises(Exception, match="API Error"):
            await brokerage_service.get_balances("123456")

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with("/v3/brokerage/accounts/123456/balances")
