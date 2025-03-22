import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch

from src.client.http_client import HttpClient
from src.streaming.stream_manager import StreamManager
from src.services.MarketData.market_data_service import MarketDataService
from src.ts_types.market_data import RiskRewardAnalysis, RiskRewardAnalysisInput, RiskRewardLeg


@pytest.fixture
def mock_http_client():
    mock = AsyncMock(spec=HttpClient)
    return mock


@pytest.fixture
def mock_stream_manager():
    mock = AsyncMock(spec=StreamManager)
    return mock


@pytest.fixture
def market_data_service(mock_http_client, mock_stream_manager):
    return MarketDataService(mock_http_client, mock_stream_manager)


@pytest.fixture
def mock_input():
    return {
        "SpreadPrice": "0.24",
        "Legs": [
            {
                "Symbol": "AAPL 240119C150",
                "Ratio": 1,
                "OpenPrice": "3.50",
                "TargetPrice": "5.00",
                "StopPrice": "2.00"
            },
            {
                "Symbol": "AAPL 240119C152.5",
                "Ratio": -1,
                "OpenPrice": "2.00",
                "TargetPrice": "1.00",
                "StopPrice": "3.00"
            },
            {
                "Symbol": "AAPL 240119C155",
                "Ratio": -1,
                "OpenPrice": "1.00",
                "TargetPrice": "0.50",
                "StopPrice": "1.50"
            },
            {
                "Symbol": "AAPL 240119C157.5",
                "Ratio": 1,
                "OpenPrice": "0.50",
                "TargetPrice": "1.00",
                "StopPrice": "0.25"
            }
        ]
    }


@pytest.fixture
def mock_response():
    return {
        "SpreadPrice": "0.24",
        "MaxGain": "2.76",
        "MaxLoss": "0.24",
        "RiskRewardRatio": "11.5",
        "Commission": "0.00",
        "Legs": [
            {
                "Symbol": "AAPL 240119C150",
                "Ratio": 1,
                "OpenPrice": "3.50",
                "TargetPrice": "5.00",
                "StopPrice": "2.00"
            },
            {
                "Symbol": "AAPL 240119C152.5",
                "Ratio": -1,
                "OpenPrice": "2.00",
                "TargetPrice": "1.00",
                "StopPrice": "3.00"
            },
            {
                "Symbol": "AAPL 240119C155",
                "Ratio": -1,
                "OpenPrice": "1.00",
                "TargetPrice": "0.50",
                "StopPrice": "1.50"
            },
            {
                "Symbol": "AAPL 240119C157.5",
                "Ratio": 1,
                "OpenPrice": "0.50",
                "TargetPrice": "1.00",
                "StopPrice": "0.25"
            }
        ]
    }


class TestGetOptionRiskReward:
    """
    Tests for the get_option_risk_reward method of MarketDataService
    """

    @pytest.mark.asyncio
    async def test_analyze_risk_reward_for_butterfly_spread(self, market_data_service, mock_http_client, mock_input, mock_response):
        # Configure the mock to return the expected response
        mock_http_client.post.return_value = mock_response
        
        # Call the method being tested
        result = await market_data_service.get_option_risk_reward(mock_input)
        
        # Verify the result
        assert isinstance(result, RiskRewardAnalysis)
        assert result.SpreadPrice == mock_response["SpreadPrice"]
        assert result.MaxGain == mock_response["MaxGain"]
        assert result.MaxLoss == mock_response["MaxLoss"]
        assert result.RiskRewardRatio == mock_response["RiskRewardRatio"]
        assert result.Commission == mock_response["Commission"]
        
        # Verify the HTTP client was called correctly
        mock_http_client.post.assert_called_with(
            "/v3/marketdata/options/riskreward",
            data=mock_input
        )

    @pytest.mark.asyncio
    async def test_handle_empty_legs_array(self, market_data_service, mock_http_client):
        # Create invalid input with empty legs array
        invalid_input = {
            "SpreadPrice": "0.24",
            "Legs": []
        }
        
        # Test that an exception is raised
        with pytest.raises(ValueError, match="At least one leg is required"):
            await market_data_service.get_option_risk_reward(invalid_input)
        
        # Verify the HTTP client was not called
        mock_http_client.post.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_legs_with_different_expiration_dates(self, market_data_service, mock_http_client):
        # Create invalid input with different expiration dates
        error_message = "All legs must have the same expiration date"
        invalid_input = {
            "SpreadPrice": "0.24",
            "Legs": [
                {
                    "Symbol": "AAPL 240119C150",
                    "Ratio": 1,
                    "OpenPrice": "3.50",
                    "TargetPrice": "5.00",
                    "StopPrice": "2.00"
                },
                {
                    "Symbol": "AAPL 240216C152.5",
                    "Ratio": -1,
                    "OpenPrice": "2.00",
                    "TargetPrice": "1.00",
                    "StopPrice": "3.00"
                }
            ]
        }
        
        # Configure the mock to return an error response
        mock_http_client.post.return_value = {
            "Error": "INVALID_EXPIRATION",
            "Message": error_message
        }
        
        # Test that an exception is raised
        with pytest.raises(Exception, match=error_message):
            await market_data_service.get_option_risk_reward(invalid_input)
        
        # Verify the HTTP client was called correctly
        mock_http_client.post.assert_called_with(
            "/v3/marketdata/options/riskreward",
            data=invalid_input
        )

    @pytest.mark.asyncio
    async def test_handle_invalid_symbols(self, market_data_service, mock_http_client):
        # Create invalid input with invalid symbol
        error_message = "Invalid option symbol format"
        invalid_input = {
            "SpreadPrice": "0.24",
            "Legs": [
                {
                    "Symbol": "INVALID",
                    "Ratio": 1,
                    "OpenPrice": "0.00",
                    "TargetPrice": "0.00",
                    "StopPrice": "0.00"
                }
            ]
        }
        
        # Configure the mock to return an error response
        mock_http_client.post.return_value = {
            "Error": "INVALID_SYMBOL",
            "Message": error_message
        }
        
        # Test that an exception is raised
        with pytest.raises(Exception, match=error_message):
            await market_data_service.get_option_risk_reward(invalid_input)
        
        # Verify the HTTP client was called correctly
        mock_http_client.post.assert_called_with(
            "/v3/marketdata/options/riskreward",
            data=invalid_input
        )

    @pytest.mark.asyncio
    async def test_handle_network_errors(self, market_data_service, mock_http_client, mock_input):
        # Configure the mock to raise an exception
        error_message = "Network error"
        mock_http_client.post.side_effect = Exception(error_message)
        
        # Test that the exception is propagated
        with pytest.raises(Exception, match=error_message):
            await market_data_service.get_option_risk_reward(mock_input)
        
        # Verify the HTTP client was called correctly
        mock_http_client.post.assert_called_with(
            "/v3/marketdata/options/riskreward",
            data=mock_input
        ) 