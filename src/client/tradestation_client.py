from typing import Optional, Dict, Any, Union, cast, Literal
import os

from ..ts_types.config import ClientConfig
from .http_client import HttpClient
from ..utils.stream_manager import StreamManager

# Remove this import to avoid circular dependency
# from src.services.MarketData.market_data_service import MarketDataService


class TradeStationClient:
    """
    Main client for TradeStation API interactions
    """

    def __init__(
        self,
        config: Union[Dict[str, Any], "ClientConfig"] = None,
        refresh_token: Optional[str] = None,
        environment: Optional[str] = None,
        debug: bool = False,
    ):
        """
        Initialize a new TradeStationClient with the provided configuration.

        Args:
            config: Dictionary or ClientConfig object with configuration options.
            refresh_token: A refresh token to initialize the client with.
            environment: Either "Live" or "Simulation".
            debug: Whether to print debug messages.
        """
        from src.ts_types.config import ClientConfig

        # Import here to avoid circular dependency
        from src.services.MarketData.market_data_service import MarketDataService
        from src.services.OrderExecution.order_execution_service import OrderExecutionService
        from src.services.Brokerage.brokerage_service import BrokerageService

        if config is None:
            config = {}

        # Convert ClientConfig to dict if needed
        if isinstance(config, ClientConfig):
            config_dict = config.model_dump()
        else:
            config_dict = config

        # Load from environment if not in config
        if not config_dict.get("client_id"):
            config_dict["client_id"] = os.environ.get("CLIENT_ID")

        # Override config with parameters if provided
        if refresh_token:
            config_dict["refresh_token"] = refresh_token
        elif not config_dict.get("refresh_token"):
            config_dict["refresh_token"] = os.environ.get("REFRESH_TOKEN")

        # Get environment from parameter, config, or environment variable
        if environment:
            # Normalize environment to proper case
            environment = "Simulation" if environment.lower() == "simulation" else "Live"
            config_dict["environment"] = environment
        elif config_dict.get("environment"):
            # Normalize environment in config_dict to proper case
            env = config_dict["environment"]
            config_dict["environment"] = "Simulation" if env.lower() == "simulation" else "Live"
        else:
            env = os.environ.get("ENVIRONMENT")
            if not env:
                raise ValueError(
                    "Environment must be specified either in config or ENVIRONMENT env var"
                )
            # Normalize environment to proper case
            config_dict["environment"] = "Simulation" if env.lower() == "simulation" else "Live"

        self.http_client = HttpClient(config_dict, debug=debug)
        self.stream_manager = StreamManager(config_dict, debug=debug)

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

    async def close(self):
        """Close the client and release resources."""
        if hasattr(self, "http_client") and hasattr(self.http_client, "close"):
            await self.http_client.close()
        if hasattr(self, "stream_manager") and hasattr(self.stream_manager, "close"):
            await self.stream_manager.close()
