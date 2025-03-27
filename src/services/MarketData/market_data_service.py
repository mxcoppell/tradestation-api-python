from typing import Any, Dict, List, Optional, Union

from ...client.http_client import HttpClient
from ...streaming.stream_manager import StreamManager
from ...ts_types.market_data import (
    SymbolDetailsResponse,
    QuoteSnapshot,
    SymbolNames,
    Expirations,
    BarsResponse,
    SpreadTypes,
    Strikes,
)


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

    async def get_option_spread_types(self) -> SpreadTypes:
        """
        Get the available spread types for option chains.

        This endpoint returns a list of all available option spread types and their configurations.
        Each spread type defines whether it uses strike intervals and/or multiple expirations.
        This information can be used with the GetOptionStrikes and other option chain endpoints.

        Common spread types include:
        - Single (standard option contract)
        - Vertical (call/put spread with same expiration, different strikes)
        - Calendar (same strike, different expirations)
        - Straddle (call and put with same strike and expiration)
        - Strangle (call and put with different strikes, same expiration)
        - Butterfly and Condor (complex spreads with multiple legs)

        Returns:
            A SpreadTypes object containing:
            - SpreadTypes: Array of spread type objects, each with:
              - Name: The name of the spread type (e.g., "Vertical", "Calendar")
              - StrikeInterval: Whether the spread uses multiple strike prices
              - ExpirationInterval: Whether the spread uses multiple expiration dates

        Raises:
            Exception: If the request fails due to network issues
            Exception: If the request fails due to invalid authentication

        Example:
            ```python
            # Get all available option spread types
            spread_types = await market_data.get_option_spread_types()

            # Print the available spread types and their configurations
            for st in spread_types.SpreadTypes:
                print(f"{st.Name}: Uses strike intervals: {st.StrikeInterval}, Uses expiration intervals: {st.ExpirationInterval}")
            ```
        """
        # Make the API request
        response = await self.http_client.get("/v3/marketdata/options/spreadtypes")

        # Parse the response into the SpreadTypes model
        return SpreadTypes.model_validate(response)

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
        if (
            params.get("unit")
            and params["unit"] != "Minute"
            and params.get("interval")
            and params["interval"] != "1"
        ):
            raise ValueError("Interval must be 1 for non-minute bars")

        # Validate interval for minute bars
        if params.get("unit") == "Minute" and params.get("interval"):
            interval_num = int(params["interval"])
            if interval_num > 1440:
                raise ValueError("Maximum interval for minute bars is 1440")

        # Validate barsback for intraday
        if params.get("unit") == "Minute" and params.get("barsback") and params["barsback"] > 57600:
            raise ValueError("Maximum of 57,600 intraday bars allowed per request")

        # Validate mutually exclusive parameters
        if params.get("barsback") and params.get("firstdate"):
            raise ValueError("barsback and firstdate parameters are mutually exclusive")

        if params.get("lastdate") and "startdate" in params:
            raise ValueError(
                "lastdate and startdate parameters are mutually exclusive. "
                "startdate is deprecated, use lastdate instead"
            )

        # Make the API request
        response = await self.http_client.get(f"/v3/marketdata/barcharts/{symbol}", params=params)

        # Parse the response into the BarsResponse model
        return BarsResponse.model_validate(response)

    async def get_option_risk_reward(
        self, analysis: Union[Dict[str, Any], "RiskRewardAnalysisInput"]
    ) -> "RiskRewardAnalysis":
        """
        Calculates risk and reward metrics for an option spread strategy.

        This endpoint calculates key risk/reward metrics for one or more option legs, including:
        - Maximum profit potential
        - Maximum loss potential
        - Risk/Reward ratio
        - Commission costs

        Args:
            analysis: A RiskRewardAnalysisInput object or dict containing:
                     - SpreadPrice: The current price of the spread
                     - Legs: Array of legs, each with:
                       - Symbol: Option symbol string
                       - Ratio: Position ratio (positive for long, negative for short)
                       - OpenPrice: Option's opening price
                       - TargetPrice: Target price for profit taking
                       - StopPrice: Stop price for loss protection

        Returns:
            A RiskRewardAnalysis object containing the risk/reward metrics

        Raises:
            ValueError: If no legs are provided
            Exception: If the request fails due to network issues or invalid authentication
            Exception: If the API returns an error (e.g., invalid symbols, expiration date mismatch)

        Example:
            ```python
            # Analyze a vertical call spread
            analysis = await market_data.get_option_risk_reward({
                "SpreadPrice": "0.24",
                "Legs": [
                    {
                        "Symbol": "AAPL 240119C150",
                        "Ratio": 1,
                        "OpenPrice": "3.50",
                        "TargetPrice": "5.00",
                        "StopPrice": "2.00"
                    },
                    {
                        "Symbol": "AAPL 240119C152.5",
                        "Ratio": -1,
                        "OpenPrice": "2.00",
                        "TargetPrice": "1.00",
                        "StopPrice": "3.00"
                    }
                ]
            })

            # Access the risk/reward metrics
            print(f"Max Gain: {analysis.MaxGain}")
            print(f"Max Loss: {analysis.MaxLoss}")
            print(f"Risk/Reward Ratio: {analysis.RiskRewardRatio}")
            ```
        """
        # Validate legs
        if not analysis.get("Legs") or (hasattr(analysis, "Legs") and not analysis.Legs):
            raise ValueError("At least one leg is required")

        # Make the API request
        response = await self.http_client.post("/v3/marketdata/options/riskreward", data=analysis)

        # Check for errors in the response
        if "Error" in response:
            raise Exception(response.get("Message", "Unknown API error"))

        # Parse the response into the RiskRewardAnalysis model
        from ...ts_types.market_data import RiskRewardAnalysis

        return RiskRewardAnalysis.model_validate(response)

    async def get_option_strikes(
        self,
        underlying: str,
        expiration: Optional[str] = None,
        spread_type: Optional[str] = None,
        options: Optional[Dict[str, str]] = None,
    ) -> Strikes:
        """
        Get the available strike prices for option contracts on the specified underlying symbol.
        This endpoint returns a list of strike prices available for option trading, which can be
        filtered by expiration date and spread type.

        Args:
            underlying: The symbol for the underlying security (stock or index).
                       Must be a valid equity or index symbol. For example: 'AAPL', 'MSFT', 'SPX', etc.
            expiration: Optional. The expiration date to filter strikes.
                       Format: YYYY-MM-DD or ISO8601 (e.g., "2024-01-19" or "2024-01-19T00:00:00Z")
            spread_type: Optional. The type of spread to get strikes for.
                        Common values: "Single", "Vertical", "Calendar", "Butterfly", "Condor", etc.
            options: Optional. Additional options for specific spread types.
                    Currently supports:
                    - expiration2: Required for Calendar spreads, specifies the second expiration date.

        Returns:
            A Strikes object containing:
            - SpreadType: The name of the spread type
            - Strikes: Array of strike price arrays. Each inner array represents a valid spread combination.
                      For example, for a Butterfly spread: [["145", "150", "155"], ["150", "155", "160"]]

        Raises:
            ValueError: If the underlying symbol is not provided
            Exception: If the request fails due to network issues
            Exception: If the request fails due to invalid authentication

        Example:
            ```python
            # Get all strikes for AAPL
            strikes = await market_data.get_option_strikes('AAPL')

            # Get strikes for MSFT options expiring on Jan 19, 2024
            msft_strikes = await market_data.get_option_strikes('MSFT', '2024-01-19')

            # Get strikes for SPY butterfly spreads expiring on Jan 19, 2024
            butterfly_strikes = await market_data.get_option_strikes('SPY', '2024-01-19', 'Butterfly')
            ```
        """
        if not underlying:
            raise ValueError("Underlying symbol is required")

        params: Dict[str, str] = {}
        if expiration:
            params["expiration"] = expiration
        if spread_type:
            params["spreadType"] = spread_type
        if spread_type == "Calendar" and options and "expiration2" in options:
            params["expiration2"] = options["expiration2"]

        # Make the API request
        response = await self.http_client.get(
            f"/v3/marketdata/options/strikes/{underlying}", params=params
        )

        # Parse the response into the Strikes model
        return Strikes.model_validate(response)
