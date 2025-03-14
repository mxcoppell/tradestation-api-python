from typing import Optional, Dict, Any, Union, cast, Literal
import os

from ..ts_types.config import ClientConfig
from .http_client import HttpClient
from ..streaming.stream_manager import StreamManager
from ..services.MarketData.market_data_service import MarketDataService
from ..services.OrderExecution.order_execution_service import OrderExecutionService
from ..services.Brokerage.brokerage_service import BrokerageService


class TradeStationClient:
    """
    Main client for TradeStation API interactions
    """

    def __init__(self, config: Optional[ClientConfig] = None):
        """
        Creates a new TradeStationClient instance

        Args:
            config: Optional configuration object. If not provided, values will be read from environment variables

        Example:
            # Using environment variables (CLIENT_ID and CLIENT_SECRET must be set)
            client = TradeStationClient(
                refresh_token='your_refresh_token',
                environment='Simulation'  # or 'Live'
            )

            # Using explicit configuration
            client = TradeStationClient({
                'client_id': 'your_client_id',
                'client_secret': 'your_client_secret',
                'refresh_token': 'your_refresh_token',
                'environment': 'Simulation'  # or 'Live'
            })

        Raises:
            ValueError: If environment is not specified either in config or ENVIRONMENT env var
        """
        # If config is None, initialize it as an empty dict
        if config is None:
            config = {}

        # Get environment from config or env var
        environment = config.get("environment") or os.environ.get("ENVIRONMENT")

        # Normalize environment to proper case
        if environment:
            environment = "Simulation" if environment.lower() == "simulation" else "Live"
        else:
            raise ValueError(
                "Environment must be specified either in config or ENVIRONMENT env var"
            )

        # Get refresh token from config or env var
        refresh_token = config.get("refresh_token") or os.environ.get("REFRESH_TOKEN")

        # Create final config with normalized environment and refresh token
        final_config = {**config, "environment": environment, "refresh_token": refresh_token}

        self.http_client = HttpClient(**final_config)
        self.stream_manager = StreamManager(self.http_client, final_config)

        # Initialize services
        self.market_data = MarketDataService(self.http_client, self.stream_manager)
        self.order_execution = OrderExecutionService(self.http_client, self.stream_manager)
        self.brokerage = BrokerageService(self.http_client, self.stream_manager)

    def get_refresh_token(self) -> Optional[str]:
        """
        Gets the current refresh token

        Returns:
            The current refresh token or None if none is available
        """
        return self.http_client.get_refresh_token()

    def close_all_streams(self) -> None:
        """
        Closes all active streams
        """
        self.stream_manager.close_all_streams()
