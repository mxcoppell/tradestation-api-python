"""
TradeStation API Client
"""

from typing import Optional, Dict, Any

from src.ts_types.config import ClientConfig


class TradeStationClient:
    """
    Main client for TradeStation API interactions
    """

    def __init__(self, config: Optional[ClientConfig] = None):
        """
        Creates a new TradeStationClient instance

        Args:
            config: Optional configuration object. If not provided, values will be read from environment variables
        """
        self.config = config

    def get_refresh_token(self) -> Optional[str]:
        """
        Gets the current refresh token

        Returns:
            The current refresh token or None if none is available
        """
        return self.config.refresh_token if self.config else None
