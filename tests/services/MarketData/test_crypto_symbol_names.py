import pytest

from src.ts_types.market_data import SymbolNames


class TestCryptoSymbolNames:
    """Tests for the crypto symbol names functionality in MarketDataService."""

    @pytest.mark.asyncio
    async def test_get_crypto_symbol_names(self, market_data_service, http_client_mock):
        """Test getting crypto symbol names."""
        # Arrange
        mock_response = {"SymbolNames": ["BTCUSD", "ETHUSD", "LTCUSD", "BCHUSD"]}
        http_client_mock.get.return_value = mock_response

        # Act
        result = await market_data_service.get_crypto_symbol_names()

        # Assert
        http_client_mock.get.assert_called_once_with(
            "/v3/marketdata/symbollists/cryptopairs/symbolnames"
        )
        assert isinstance(result, SymbolNames)
        assert result.SymbolNames == ["BTCUSD", "ETHUSD", "LTCUSD", "BCHUSD"]
