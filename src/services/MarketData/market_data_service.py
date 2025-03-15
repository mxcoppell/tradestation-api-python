from typing import Any, Dict, List, Optional, Union

from ...client.http_client import HttpClient
from ...streaming.stream_manager import StreamManager
from ...ts_types.market_data import SymbolDetailsResponse, QuoteSnapshot, SymbolNames, Expirations, BarsResponse


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

    async def get_bar_history(self, symbol: str, params: Dict[str, Any] = None) -> BarsResponse:
        """
        Fetches marketdata bars for the given symbol, interval, and timeframe.
        The maximum amount of intraday bars a user can fetch is 57,600 per request.
        This is calculated either by the amount of barsback or bars within a timeframe requested.

        Args:
            symbol: The valid symbol string.
            params: Parameters for the bar history request
                interval: Default: 1. Interval that each bar will consist of - for minute bars, the number of minutes
                          aggregated in a single bar. For bar units other than minute, value must be 1.
                          For unit Minute the max allowed Interval is 1440.
                unit: Default: Daily. The unit of time for each bar interval.
                      Valid values are: Minute, Daily, Weekly, Monthly.
                barsback: Default: 1. Number of bars back to fetch. The maximum number of intraday bars back
                          that a user can query is 57,600. There is no limit on daily, weekly, or monthly bars.
                          This parameter is mutually exclusive with firstdate.
                firstdate: The first date formatted as YYYY-MM-DD or 2020-04-20T18:00:00Z.
                           This parameter is mutually exclusive with barsback.
                lastdate: Defaults to current timestamp. The last date formatted as YYYY-MM-DD or 2020-04-20T18:00:00Z.
                          This parameter is mutually exclusive with startdate and should be used instead of that parameter.
                sessiontemplate: United States (US) stock market session templates, that extend bars returned to include
                                those outside of the regular trading session. Ignored for non-US equity symbols.
                                Valid values are: USEQPre, USEQPost, USEQPreAndPost, USEQ24Hour, Default.

        Returns:
            BarsResponse containing an array of Bar objects.

        Raises:
            ValueError: If the interval is invalid for the specified unit
            ValueError: If the maximum number of intraday bars is exceeded
            ValueError: If mutually exclusive parameters are specified
            Exception: If the request fails due to network issues or invalid authentication

        Example:
            ```python
            # Get daily bars for the last 5 days
            bars = await market_data.get_bar_history('MSFT', {
                'unit': 'Daily',
                'barsback': 5
            })
            print(bars.Bars[0])
            # {
            #   "High": "218.32",
            #   "Low": "212.42",
            #   "Open": "214.02",
            #   "Close": "216.39",
            #   "TimeStamp": "2020-11-04T21:00:00Z",
            #   "TotalVolume": "42311777",
            #   "DownTicks": 231021,
            #   "DownVolume": 19575455,
            #   "OpenInterest": "0",
            #   "IsRealtime": false,
            #   "IsEndOfHistory": false,
            #   "TotalTicks": 460552,
            #   "UpTicks": 229531,
            #   "UpVolume": 22736321,
            #   "Epoch": 1604523600000,
            #   "BarStatus": "Closed"
            # }

            # Get 1-minute bars for a specific date range with extended hours
            bars = await market_data.get_bar_history('MSFT', {
                'unit': 'Minute',
                'interval': '1',
                'firstdate': '2024-01-01T14:30:00Z',
                'lastdate': '2024-01-01T21:00:00Z',
                'sessiontemplate': 'USEQPreAndPost'
            })
            ```
        """
        if not symbol:
            raise ValueError("Symbol is required")

        # Initialize params if not provided
        if params is None:
            params = {}

        # Validate interval for non-minute bars
        if (params.get("unit") and params["unit"] != "Minute" and 
                params.get("interval") and params["interval"] != "1"):
            raise ValueError("Interval must be 1 for non-minute bars")

        # Validate interval for minute bars
        if params.get("unit") == "Minute" and params.get("interval"):
            interval_num = int(params["interval"])
            if interval_num > 1440:
                raise ValueError("Maximum interval for minute bars is 1440")

        # Validate barsback for intraday
        if (params.get("unit") == "Minute" and params.get("barsback") and 
                params["barsback"] > 57600):
            raise ValueError("Maximum of 57,600 intraday bars allowed per request")

        # Validate mutually exclusive parameters
        if params.get("barsback") and params.get("firstdate"):
            raise ValueError("barsback and firstdate parameters are mutually exclusive")

        if params.get("lastdate") and "startdate" in params:
            raise ValueError("lastdate and startdate parameters are mutually exclusive. "
                            "startdate is deprecated, use lastdate instead")

        # Make the API request
        response = await self.http_client.get(
            f"/v3/marketdata/barcharts/{symbol}", params=params
        )

        # Parse the response into the BarsResponse model
        return BarsResponse.model_validate(response)
