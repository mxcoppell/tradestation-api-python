import pytest

from src.ts_types.market_data import BarsResponse


class TestBarHistory:
    """Tests for the bar history functionality in MarketDataService."""

    @pytest.mark.asyncio
    async def test_get_bar_history_daily(self, market_data_service, http_client_mock):
        """Test getting daily bars."""
        # Arrange
        symbol = "MSFT"
        params = {"unit": "Daily", "barsback": 5}

        mock_response = {
            "Bars": [
                {
                    "High": "218.32",
                    "Low": "212.42",
                    "Open": "214.02",
                    "Close": "216.39",
                    "TimeStamp": "2024-01-19T21:00:00Z",
                    "TotalVolume": "42311777",
                    "DownTicks": 231021,
                    "DownVolume": 19575455,
                    "OpenInterest": "0",
                    "IsRealtime": False,
                    "IsEndOfHistory": False,
                    "TotalTicks": 460552,
                    "UpTicks": 229531,
                    "UpVolume": 22736321,
                    "Epoch": 1705694400000,
                    "BarStatus": "Closed",
                },
                {
                    "High": "219.52",
                    "Low": "214.42",
                    "Open": "215.82",
                    "Close": "218.59",
                    "TimeStamp": "2024-01-22T21:00:00Z",
                    "TotalVolume": "38221577",
                    "DownTicks": 210021,
                    "DownVolume": 18775455,
                    "OpenInterest": "0",
                    "IsRealtime": False,
                    "IsEndOfHistory": False,
                    "TotalTicks": 420552,
                    "UpTicks": 210531,
                    "UpVolume": 19446122,
                    "Epoch": 1705953600000,
                    "BarStatus": "Closed",
                },
            ]
        }

        http_client_mock.get.return_value = mock_response

        # Act
        result = await market_data_service.get_bar_history(symbol, params)

        # Assert
        http_client_mock.get.assert_called_once_with(
            f"/v3/marketdata/barcharts/{symbol}", params=params
        )
        assert len(result.Bars) == 2
        assert result.Bars[0].Close == "216.39"
        assert result.Bars[0].High == "218.32"
        assert result.Bars[0].Low == "212.42"
        assert result.Bars[0].Open == "214.02"
        assert result.Bars[0].TotalVolume == "42311777"
        assert result.Bars[0].BarStatus == "Closed"
        assert result.Bars[1].TimeStamp == "2024-01-22T21:00:00Z"

    @pytest.mark.asyncio
    async def test_get_bar_history_minute(self, market_data_service, http_client_mock):
        """Test getting minute bars."""
        # Arrange
        symbol = "MSFT"
        params = {"unit": "Minute", "interval": "5", "barsback": 2}

        mock_response = {
            "Bars": [
                {
                    "High": "388.45",
                    "Low": "388.10",
                    "Open": "388.45",
                    "Close": "388.24",
                    "TimeStamp": "2024-01-22T14:40:00Z",
                    "TotalVolume": "12345",
                    "DownTicks": 32,
                    "DownVolume": 6000,
                    "OpenInterest": "0",
                    "IsRealtime": False,
                    "IsEndOfHistory": False,
                    "TotalTicks": 64,
                    "UpTicks": 32,
                    "UpVolume": 6345,
                    "Epoch": 1705932000000,
                    "BarStatus": "Closed",
                },
                {
                    "High": "388.65",
                    "Low": "388.22",
                    "Open": "388.24",
                    "Close": "388.53",
                    "TimeStamp": "2024-01-22T14:45:00Z",
                    "TotalVolume": "15789",
                    "DownTicks": 42,
                    "DownVolume": 7500,
                    "OpenInterest": "0",
                    "IsRealtime": False,
                    "IsEndOfHistory": False,
                    "TotalTicks": 86,
                    "UpTicks": 44,
                    "UpVolume": 8289,
                    "Epoch": 1705932300000,
                    "BarStatus": "Closed",
                },
            ]
        }

        http_client_mock.get.return_value = mock_response

        # Act
        result = await market_data_service.get_bar_history(symbol, params)

        # Assert
        http_client_mock.get.assert_called_once_with(
            f"/v3/marketdata/barcharts/{symbol}", params=params
        )
        assert len(result.Bars) == 2
        assert result.Bars[0].TimeStamp == "2024-01-22T14:40:00Z"
        assert result.Bars[1].TimeStamp == "2024-01-22T14:45:00Z"
        assert result.Bars[0].Epoch == 1705932000000
        assert result.Bars[1].Epoch == 1705932300000
        assert result.Bars[0].BarStatus == "Closed"
        assert result.Bars[1].BarStatus == "Closed"

    @pytest.mark.asyncio
    async def test_get_bar_history_date_range(self, market_data_service, http_client_mock):
        """Test getting bars for a specific date range."""
        # Arrange
        symbol = "MSFT"
        params = {
            "unit": "Minute",
            "interval": "1",
            "firstdate": "2024-01-22T14:30:00Z",
            "lastdate": "2024-01-22T15:00:00Z",
            "sessiontemplate": "USEQPreAndPost",
        }

        mock_response = {
            "Bars": [
                {
                    "High": "388.45",
                    "Low": "388.10",
                    "Open": "388.45",
                    "Close": "388.24",
                    "TimeStamp": "2024-01-22T14:30:00Z",
                    "TotalVolume": "12345",
                    "DownTicks": 32,
                    "DownVolume": 6000,
                    "OpenInterest": "0",
                    "IsRealtime": False,
                    "IsEndOfHistory": False,
                    "TotalTicks": 64,
                    "UpTicks": 32,
                    "UpVolume": 6345,
                    "Epoch": 1705931400000,
                    "BarStatus": "Closed",
                },
                {
                    "High": "388.65",
                    "Low": "388.22",
                    "Open": "388.24",
                    "Close": "388.53",
                    "TimeStamp": "2024-01-22T15:00:00Z",
                    "TotalVolume": "15789",
                    "DownTicks": 42,
                    "DownVolume": 7500,
                    "OpenInterest": "0",
                    "IsRealtime": False,
                    "IsEndOfHistory": True,
                    "TotalTicks": 86,
                    "UpTicks": 44,
                    "UpVolume": 8289,
                    "Epoch": 1705933200000,
                    "BarStatus": "Closed",
                },
            ]
        }

        http_client_mock.get.return_value = mock_response

        # Act
        result = await market_data_service.get_bar_history(symbol, params)

        # Assert
        http_client_mock.get.assert_called_once_with(
            f"/v3/marketdata/barcharts/{symbol}", params=params
        )
        assert len(result.Bars) == 2
        assert result.Bars[0].TimeStamp == "2024-01-22T14:30:00Z"
        assert result.Bars[1].TimeStamp == "2024-01-22T15:00:00Z"
        assert result.Bars[0].IsEndOfHistory is False
        assert result.Bars[1].IsEndOfHistory is True

    @pytest.mark.asyncio
    async def test_get_bar_history_empty_symbol(self, market_data_service):
        """Test that an empty symbol raises a ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Symbol is required"):
            await market_data_service.get_bar_history("")

    @pytest.mark.asyncio
    async def test_get_bar_history_invalid_interval_non_minute(self, market_data_service):
        """Test that an invalid interval for non-minute bars raises a ValueError."""
        # Arrange
        params = {"unit": "Daily", "interval": "5"}

        # Act & Assert
        with pytest.raises(ValueError, match="Interval must be 1 for non-minute bars"):
            await market_data_service.get_bar_history("MSFT", params)

    @pytest.mark.asyncio
    async def test_get_bar_history_invalid_minute_interval(self, market_data_service):
        """Test that an invalid minute interval raises a ValueError."""
        # Arrange
        params = {"unit": "Minute", "interval": "1500"}  # Exceeds max of 1440

        # Act & Assert
        with pytest.raises(ValueError, match="Maximum interval for minute bars is 1440"):
            await market_data_service.get_bar_history("MSFT", params)

    @pytest.mark.asyncio
    async def test_get_bar_history_too_many_bars(self, market_data_service):
        """Test that too many requested intraday bars raises a ValueError."""
        # Arrange
        params = {"unit": "Minute", "barsback": 60000}  # Exceeds max of 57600

        # Act & Assert
        with pytest.raises(ValueError, match="Maximum of 57,600 intraday bars allowed per request"):
            await market_data_service.get_bar_history("MSFT", params)

    @pytest.mark.asyncio
    async def test_get_bar_history_mutually_exclusive_params(self, market_data_service):
        """Test that mutually exclusive parameters raise a ValueError."""
        # Arrange
        params = {"barsback": 10, "firstdate": "2024-01-22T14:30:00Z"}

        # Act & Assert
        with pytest.raises(
            ValueError, match="barsback and firstdate parameters are mutually exclusive"
        ):
            await market_data_service.get_bar_history("MSFT", params)

    @pytest.mark.asyncio
    async def test_get_bar_history_deprecated_param(self, market_data_service):
        """Test that deprecated 'startdate' parameter raises a ValueError when used with 'lastdate'."""
        # Arrange
        params = {"lastdate": "2024-01-22T15:00:00Z", "startdate": "2024-01-22T14:30:00Z"}

        # Act & Assert
        with pytest.raises(
            ValueError, match="lastdate and startdate parameters are mutually exclusive"
        ):
            await market_data_service.get_bar_history("MSFT", params)

    @pytest.mark.asyncio
    async def test_get_bar_history_none_params(self, market_data_service, http_client_mock):
        """Test getting bars with None params (should use defaults)."""
        # Arrange
        symbol = "MSFT"
        mock_response = {
            "Bars": [
                {
                    "High": "388.45",
                    "Low": "388.10",
                    "Open": "388.45",
                    "Close": "388.24",
                    "TimeStamp": "2024-01-22T14:40:00Z",
                    "TotalVolume": "12345",
                    "DownTicks": 32,
                    "DownVolume": 6000,
                    "OpenInterest": "0",
                    "IsRealtime": False,
                    "IsEndOfHistory": True,
                    "TotalTicks": 64,
                    "UpTicks": 32,
                    "UpVolume": 6345,
                    "Epoch": 1705932000000,
                    "BarStatus": "Closed",
                }
            ]
        }

        http_client_mock.get.return_value = mock_response

        # Act
        result = await market_data_service.get_bar_history(symbol, None)

        # Assert
        http_client_mock.get.assert_called_once_with(
            f"/v3/marketdata/barcharts/{symbol}", params={}
        )
        assert len(result.Bars) == 1

    @pytest.mark.asyncio
    async def test_get_bar_history_network_error(self, market_data_service, http_client_mock):
        """Test that network errors during bar history fetch are raised."""
        # Arrange
        http_client_mock.get.side_effect = Exception("Network Error")

        # Act & Assert
        with pytest.raises(Exception, match="Network Error"):
            await market_data_service.get_bar_history("MSFT")
