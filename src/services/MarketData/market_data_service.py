from typing import Any, Dict, List, Optional, Union

from ...client.http_client import HttpClient
from ...streaming.stream_manager import StreamManager
from ...ts_types.market_data import SymbolDetailsResponse, QuoteSnapshot, SymbolNames, Expirations


class MarketDataService:
    """
    Service for accessing TradeStation market data

    This is a placeholder until the full implementation in a separate task.
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

    async def get_symbol_details(self, symbols: Union[str, List[str]]) -> SymbolDetailsResponse:
        """
        Gets detailed information about one or more symbols.

        Args:
            symbols: A symbol string or list of symbol strings to get details for.
                     If a string containing multiple symbols, they should be comma-separated.

        Returns:
            SymbolDetailsResponse containing details for each symbol and any errors

        Raises:
            Exception: If the API request fails
        """
        if not symbols:
            raise ValueError("At least one symbol must be provided")

        # Handle single string vs list of strings
        if isinstance(symbols, str):
            # Already a comma-separated string or single symbol
            symbols_param = symbols
        else:
            # Join symbols list with commas for the API request
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

    async def get_quote_snapshots(self, symbols: Union[str, List[str]]) -> QuoteSnapshot:
        """
        Fetches a full snapshot of the latest Quote for the given Symbols.
        For realtime Quote updates, users should use the Quote Stream endpoint.

        The Quote Snapshot endpoint provides the latest price data for one or more symbols.
        This includes:
        - Current prices (Last, Ask, Bid)
        - Daily statistics (Open, High, Low, Close)
        - Volume information
        - 52-week high/low data
        - Market flags (delayed, halted, etc.)

        Args:
            symbols: List of valid symbols or a string of comma-separated symbols.
                    For example: ["MSFT", "BTCUSD"] or "MSFT,BTCUSD".
                    No more than 100 symbols per request.

        Returns:
            A QuoteSnapshot containing both successful quotes and any errors.
            The response includes:
            - Quotes: Array of successful quote data
            - Errors: Array of any errors for invalid symbols

        Raises:
            ValueError: If more than 100 symbols are requested
            Exception: If the request fails due to network issues or invalid authentication

        Example:
            ```python
            snapshot = await market_data.get_quote_snapshots(["MSFT", "BTCUSD"])
            print(snapshot.Quotes)
            # [
            #   {
            #     "Symbol": "MSFT",
            #     "Open": "213.65",
            #     "High": "215.77",
            #     "Low": "205.48",
            #     "PreviousClose": "214.46",
            #     "Last": "212.85",
            #     "Ask": "212.87",
            #     "AskSize": "300",
            #     "Bid": "212.85",
            #     "BidSize": "200",
            #     ...
            #   }
            # ]
            print(snapshot.Errors)  # Any errors for invalid symbols
            ```
        """
        # Convert to list if string
        if isinstance(symbols, str):
            # If comma-separated, split it; otherwise, put the single symbol in a list
            if "," in symbols:
                symbols_list = symbols.split(",")
            else:
                symbols_list = [symbols]
        else:
            symbols_list = symbols

        # Validate maximum symbols
        if len(symbols_list) > 100:
            raise ValueError("Too many symbols")

        # Join symbols with commas and make the request
        response = await self.http_client.get(f"/v3/marketdata/quotes/{','.join(symbols_list)}")

        # Ensure 'Errors' field exists in the response to meet model requirements
        if "Errors" not in response:
            response["Errors"] = []

        # Parse the response into the QuoteSnapshot model
        return QuoteSnapshot.model_validate(response)

    async def get_option_expirations(
        self, underlying: str, strike_price: Optional[float] = None
    ) -> Expirations:
        """
        Get the available expiration dates for option contracts on the specified underlying symbol.
        This endpoint returns a list of expiration dates available for option trading, which can be
        filtered by strike price.

        Args:
            underlying: The symbol for the underlying security (stock or index).
                       Must be a valid equity or index symbol. For example: 'AAPL', 'MSFT', 'SPX', etc.
            strike_price: Optional. The strike price to filter expirations.
                         Must be a positive number.

        Returns:
            A Promise that resolves to an Expirations object containing:
            - Expirations: Array of expiration date objects, each with:
              - Date: The expiration date in ISO8601 format
              - Type: The type of expiration (Monthly, Weekly, Quarterly)

        Raises:
            ValueError: If the underlying symbol is not provided
            ValueError: If the strike price is not a positive number
            Exception: If the request fails due to network issues
            Exception: If the request fails due to invalid authentication

        Example:
            ```python
            # Get all expirations for AAPL
            expirations = await market_data.get_option_expirations('AAPL')
            print(expirations.Expirations)
            # [
            #   { "Date": "2024-01-19T00:00:00Z", "Type": "Monthly" },
            #   { "Date": "2024-01-26T00:00:00Z", "Type": "Weekly" },
            #   { "Date": "2024-02-16T00:00:00Z", "Type": "Monthly" }
            # ]

            # Get expirations for MSFT at strike price 400
            msft_expirations = await market_data.get_option_expirations('MSFT', 400)
            ```
        """
        if not underlying:
            raise ValueError("Underlying symbol is required")

        if strike_price is not None and strike_price <= 0:
            raise ValueError("Strike price must be a positive number")

        params: Dict[str, Any] = {}
        if strike_price is not None:
            params["strikePrice"] = strike_price

        # Make the API request
        response = await self.http_client.get(
            f"/v3/marketdata/options/expirations/{underlying}", params=params
        )

        # Parse the response into the Expirations model
        return Expirations.model_validate(response)
