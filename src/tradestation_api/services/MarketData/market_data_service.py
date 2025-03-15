from typing import Any, Dict, List, Optional, Union

from src.client.http_client import HttpClient
from src.streaming.stream_manager import StreamManager
from src.ts_types.market_data import SymbolDetailsResponse, SymbolNames


class MarketDataService:
    """
    Service for accessing TradeStation market data
    """

    def __init__(self, http_client: HttpClient, stream_manager: StreamManager):
        """
        Creates a new MarketDataService

        Args:
            http_client: The HttpClient to use for API requests
            stream_manager: The StreamManager to use for streaming
        """
        self.http_client = http_client
        self.stream_manager = stream_manager

    async def get_symbol_details(self, symbols: List[str]) -> SymbolDetailsResponse:
        """
        Gets detailed information about one or more symbols.

        Args:
            symbols: List of symbols to get details for

        Returns:
            SymbolDetailsResponse containing details for each symbol and any errors

        Raises:
            Exception: If the API request fails
        """
        if not symbols:
            raise ValueError("At least one symbol must be provided")

        # Join symbols with commas for the API request
        symbols_param = ",".join(symbols)

        # Make the API request - Note: per OpenAPI spec, the endpoint doesn't have a '/details' suffix
        response = await self.http_client.get(f"/v3/marketdata/symbols/{symbols_param}")

        # Parse the response into the SymbolDetailsResponse model
        return SymbolDetailsResponse.model_validate(response)

    async def get_crypto_symbol_names(self) -> SymbolNames:
        """
        Fetches crypto Symbol Names for all available symbols, i.e., BTCUSD, ETHUSD, LTCUSD and BCHUSD.
        Note that while data can be obtained for these symbols, they cannot be traded.

        Returns:
            SymbolNames containing a list of available crypto symbol names

        Raises:
            Exception: If the API request fails
        """
        # Make the API request
        response = await self.http_client.get("/v3/marketdata/symbollists/cryptopairs/symbolnames")

        # Parse the response into the SymbolNames model
        return SymbolNames.model_validate(response)
