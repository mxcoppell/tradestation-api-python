import os
import pytest
from unittest.mock import MagicMock, patch

from src.client.tradestation_client import TradeStationClient
from src.client.http_client import HttpClient
from src.streaming.stream_manager import StreamManager
from src.services.MarketData.market_data_service import MarketDataService
from src.services.OrderExecution.order_execution_service import OrderExecutionService
from src.services.Brokerage.brokerage_service import BrokerageService
from src.ts_types.config import ClientConfig


class TestTradeStationClient:
    @pytest.fixture
    def config(self):
        return {
            "client_id": "test-client-id",
            "client_secret": "test-client-secret",
            "refresh_token": "test-refresh-token",
            "environment": "Simulation",
        }

    @pytest.fixture
    def mock_http_client(self):
        mock = MagicMock(spec=HttpClient)
        mock.get_refresh_token.return_value = "test-refresh-token"
        return mock

    @pytest.fixture
    def mock_stream_manager(self):
        mock = MagicMock(spec=StreamManager)
        mock.close_all_streams = MagicMock()
        return mock

    @pytest.fixture
    def mock_services(self):
        return {
            "market_data": MagicMock(spec=MarketDataService),
            "order_execution": MagicMock(spec=OrderExecutionService),
            "brokerage": MagicMock(spec=BrokerageService),
        }

    @pytest.fixture(autouse=True)
    def save_env(self):
        """Save and restore environment variables for each test"""
        old_env = os.environ.copy()
        yield
        os.environ.clear()
        os.environ.update(old_env)

    def test_constructor_creates_services(
        self, config, mock_http_client, mock_stream_manager, mock_services
    ):
        with (
            patch(
                "src.client.tradestation_client.HttpClient", return_value=mock_http_client
            ) as mock_http_client_cls,
            patch(
                "src.client.tradestation_client.StreamManager", return_value=mock_stream_manager
            ) as mock_stream_manager_cls,
            patch(
                "src.services.MarketData.market_data_service.MarketDataService",
                return_value=mock_services["market_data"],
            ) as mock_market_data_cls,
            patch(
                "src.services.OrderExecution.order_execution_service.OrderExecutionService",
                return_value=mock_services["order_execution"],
            ) as mock_order_execution_cls,
            patch(
                "src.services.Brokerage.brokerage_service.BrokerageService",
                return_value=mock_services["brokerage"],
            ) as mock_brokerage_cls,
        ):

            client = TradeStationClient(config)

            # Check HttpClient created with correct config
            assert isinstance(client.http_client, MagicMock)

            # Check StreamManager created with correct args
            assert mock_stream_manager_cls.call_count == 1
            assert mock_stream_manager_cls.call_args[0][0] == mock_http_client

            # Check services created with correct args
            assert mock_market_data_cls.call_count == 1
            assert mock_order_execution_cls.call_count == 1
            assert mock_brokerage_cls.call_count == 1

            # Check services attached to client
            assert client.market_data == mock_services["market_data"]
            assert client.order_execution == mock_services["order_execution"]
            assert client.brokerage == mock_services["brokerage"]

    def test_normalizes_environment_value(self, config):
        # Test with lowercase 'simulation'
        config_lower = {**config, "environment": "simulation"}

        with (
            patch("src.client.tradestation_client.HttpClient") as mock_http_client,
            patch("src.client.tradestation_client.StreamManager"),
            patch("src.services.MarketData.market_data_service.MarketDataService"),
            patch("src.services.OrderExecution.order_execution_service.OrderExecutionService"),
            patch("src.services.Brokerage.brokerage_service.BrokerageService"),
        ):

            client = TradeStationClient(config_lower)

            # Check the config was normalized
            # Extract kwargs from the HttpClient constructor call
            call_kwargs = mock_http_client.call_args[1]
            assert call_kwargs["environment"] == "Simulation"

    def test_throws_error_when_environment_not_specified(self, config):
        # Create config without environment
        invalid_config = {k: v for k, v in config.items() if k != "environment"}

        # Clear the environment variable if it exists
        if "ENVIRONMENT" in os.environ:
            del os.environ["ENVIRONMENT"]

        with pytest.raises(ValueError) as excinfo:
            TradeStationClient(invalid_config)

        assert "Environment must be specified" in str(excinfo.value)

    def test_get_refresh_token(self, config, mock_http_client, mock_stream_manager, mock_services):
        with (
            patch("src.client.tradestation_client.HttpClient", return_value=mock_http_client),
            patch("src.client.tradestation_client.StreamManager", return_value=mock_stream_manager),
            patch(
                "src.services.MarketData.market_data_service.MarketDataService",
                return_value=mock_services["market_data"],
            ),
            patch(
                "src.services.OrderExecution.order_execution_service.OrderExecutionService",
                return_value=mock_services["order_execution"],
            ),
            patch(
                "src.services.Brokerage.brokerage_service.BrokerageService",
                return_value=mock_services["brokerage"],
            ),
        ):

            client = TradeStationClient(config)

            # Test returns refresh token
            mock_http_client.get_refresh_token.return_value = "test-refresh-token"
            refresh_token = client.get_refresh_token()
            assert refresh_token == "test-refresh-token"
            assert mock_http_client.get_refresh_token.call_count == 1

            # Test returns None
            mock_http_client.get_refresh_token.reset_mock()
            mock_http_client.get_refresh_token.return_value = None
            refresh_token = client.get_refresh_token()
            assert refresh_token is None
            assert mock_http_client.get_refresh_token.call_count == 1

    def test_close_all_streams(self, config, mock_http_client, mock_stream_manager, mock_services):
        with (
            patch("src.client.tradestation_client.HttpClient", return_value=mock_http_client),
            patch("src.client.tradestation_client.StreamManager", return_value=mock_stream_manager),
            patch(
                "src.services.MarketData.market_data_service.MarketDataService",
                return_value=mock_services["market_data"],
            ),
            patch(
                "src.services.OrderExecution.order_execution_service.OrderExecutionService",
                return_value=mock_services["order_execution"],
            ),
            patch(
                "src.services.Brokerage.brokerage_service.BrokerageService",
                return_value=mock_services["brokerage"],
            ),
        ):

            client = TradeStationClient(config)

            client.close_all_streams()
            assert mock_stream_manager.close_all_streams.call_count == 1
