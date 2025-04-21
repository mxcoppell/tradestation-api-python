import pytest

from tradestation.ts_types.market_data import Expirations


class TestOptionExpirations:
    """Tests for the option expirations functionality in MarketDataService."""

    @pytest.mark.asyncio
    async def test_get_option_expirations_without_strike_price(
        self, market_data_service, http_client_mock
    ):
        """Test getting option expirations without strike price."""
        # Arrange
        underlying = "MSFT"
        mock_response = {
            "Expirations": [
                {"Date": "2024-01-19T00:00:00Z", "Type": "Monthly"},
                {"Date": "2024-01-26T00:00:00Z", "Type": "Weekly"},
                {"Date": "2024-02-16T00:00:00Z", "Type": "Monthly"},
                {"Date": "2024-03-15T00:00:00Z", "Type": "Quarterly"},
            ]
        }
        http_client_mock.get.return_value = mock_response

        # Act
        result = await market_data_service.get_option_expirations(underlying)

        # Assert
        http_client_mock.get.assert_called_once_with(
            "/v3/marketdata/options/expirations/MSFT", params={}
        )
        assert isinstance(result, Expirations)
        assert len(result.Expirations) == 4
        assert result.Expirations[0].Date == "2024-01-19T00:00:00Z"
        assert result.Expirations[0].Type == "Monthly"
        assert result.Expirations[1].Type == "Weekly"
        assert result.Expirations[3].Type == "Quarterly"

    @pytest.mark.asyncio
    async def test_get_option_expirations_with_strike_price(
        self, market_data_service, http_client_mock
    ):
        """Test getting option expirations with strike price."""
        # Arrange
        underlying = "MSFT"
        strike_price = 400
        mock_response = {
            "Expirations": [
                {"Date": "2024-01-19T00:00:00Z", "Type": "Monthly"},
                {"Date": "2024-02-16T00:00:00Z", "Type": "Monthly"},
            ]
        }
        http_client_mock.get.return_value = mock_response

        # Act
        result = await market_data_service.get_option_expirations(underlying, strike_price)

        # Assert
        http_client_mock.get.assert_called_once_with(
            "/v3/marketdata/options/expirations/MSFT", params={"strikePrice": 400}
        )
        assert isinstance(result, Expirations)
        assert len(result.Expirations) == 2
        assert result.Expirations[0].Date == "2024-01-19T00:00:00Z"
        assert result.Expirations[0].Type == "Monthly"
        assert result.Expirations[1].Type == "Monthly"

    @pytest.mark.asyncio
    async def test_get_option_expirations_empty_list(self, market_data_service, http_client_mock):
        """Test handling empty expirations list."""
        # Arrange
        underlying = "MSFT"
        mock_response = {"Expirations": []}
        http_client_mock.get.return_value = mock_response

        # Act
        result = await market_data_service.get_option_expirations(underlying)

        # Assert
        http_client_mock.get.assert_called_once_with(
            "/v3/marketdata/options/expirations/MSFT", params={}
        )
        assert isinstance(result, Expirations)
        assert len(result.Expirations) == 0

    @pytest.mark.asyncio
    async def test_get_option_expirations_missing_underlying(self, market_data_service):
        """Test that an error is raised when no underlying symbol is provided."""
        # Act & Assert
        with pytest.raises(ValueError, match="Underlying symbol is required"):
            await market_data_service.get_option_expirations("")

    @pytest.mark.asyncio
    async def test_get_option_expirations_invalid_strike_price(self, market_data_service):
        """Test that an error is raised when strike price is not positive."""
        # Act & Assert
        with pytest.raises(ValueError, match="Strike price must be a positive number"):
            await market_data_service.get_option_expirations("MSFT", -1)

    @pytest.mark.asyncio
    async def test_get_option_expirations_network_error(
        self, market_data_service, http_client_mock
    ):
        """Test that network errors during option expirations fetch are raised."""
        # Arrange
        http_client_mock.get.side_effect = Exception("Network Error")

        # Act & Assert
        with pytest.raises(Exception, match="Network Error"):
            await market_data_service.get_option_expirations("MSFT")
