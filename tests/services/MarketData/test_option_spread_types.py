from unittest.mock import AsyncMock

import pytest

from tradestation.ts_types.market_data import SpreadTypes


class TestOptionSpreadTypes:
    """Tests for the option spread types functionality in MarketDataService."""

    @pytest.mark.asyncio
    async def test_get_option_spread_types_success(self, market_data_service, http_client_mock):
        """Test successful retrieval of option spread types."""
        # Mock response data
        mock_response = {
            "SpreadTypes": [
                {"Name": "Single", "StrikeInterval": False, "ExpirationInterval": False},
                {"Name": "Vertical", "StrikeInterval": True, "ExpirationInterval": False},
                {"Name": "Calendar", "StrikeInterval": False, "ExpirationInterval": True},
                {"Name": "Butterfly", "StrikeInterval": True, "ExpirationInterval": False},
            ]
        }

        # Configure mock
        http_client_mock.get.return_value = mock_response

        # Call the method
        result = await market_data_service.get_option_spread_types()

        # Verify the result
        assert isinstance(result, SpreadTypes)
        assert len(result.SpreadTypes) == 4

        # Verify specific spread types
        assert result.SpreadTypes[0].Name == "Single"
        assert result.SpreadTypes[0].StrikeInterval == False
        assert result.SpreadTypes[0].ExpirationInterval == False

        assert result.SpreadTypes[1].Name == "Vertical"
        assert result.SpreadTypes[1].StrikeInterval == True
        assert result.SpreadTypes[1].ExpirationInterval == False

        assert result.SpreadTypes[2].Name == "Calendar"
        assert result.SpreadTypes[2].StrikeInterval == False
        assert result.SpreadTypes[2].ExpirationInterval == True

        # Verify the API call
        http_client_mock.get.assert_called_once_with("/v3/marketdata/options/spreadtypes")

    @pytest.mark.asyncio
    async def test_get_option_spread_types_empty_response(
        self, market_data_service, http_client_mock
    ):
        """Test handling of empty spread types response."""
        # Mock an empty response
        mock_response = {"SpreadTypes": []}

        # Configure mock
        http_client_mock.get.return_value = mock_response

        # Call the method
        result = await market_data_service.get_option_spread_types()

        # Verify the result
        assert isinstance(result, SpreadTypes)
        assert len(result.SpreadTypes) == 0

        # Verify the API call
        http_client_mock.get.assert_called_once_with("/v3/marketdata/options/spreadtypes")

    @pytest.mark.asyncio
    async def test_get_option_spread_types_network_error(
        self, market_data_service, http_client_mock
    ):
        """Test handling network errors for get_option_spread_types."""
        # Configure mock to raise an exception
        http_client_mock.get.side_effect = Exception("Network error")

        # Call the method and expect an exception
        with pytest.raises(Exception, match="Network error"):
            await market_data_service.get_option_spread_types()

        # Verify the API call attempt
        http_client_mock.get.assert_called_once_with("/v3/marketdata/options/spreadtypes")
