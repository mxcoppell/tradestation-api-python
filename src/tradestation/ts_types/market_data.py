from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field


class MarketFlags(BaseModel):
    """
    Flags related to market conditions for a symbol.
    """

    IsBats: bool
    IsDelayed: bool
    IsHalted: bool
    IsHardToBorrow: bool


class Quote(BaseModel):
    """
    Quote data for a financial instrument.
    """

    Symbol: str
    Ask: str
    AskSize: str
    Bid: str
    BidSize: str
    Close: str
    DailyOpenInterest: str
    High: str
    Low: str
    High52Week: Optional[str] = None
    High52WeekTimestamp: Optional[str] = None
    Last: str
    MinPrice: Optional[str] = None
    MaxPrice: Optional[str] = None
    FirstNoticeDate: Optional[str] = None
    LastTradingDate: Optional[str] = None
    Low52Week: Optional[str] = None
    Low52WeekTimestamp: Optional[str] = None
    MarketFlags: MarketFlags
    NetChange: str
    NetChangePct: str
    Open: str
    PreviousClose: str
    PreviousVolume: str
    Restrictions: Optional[List[str]] = None
    TickSizeTier: str
    TradeTime: str
    Volume: str
    LastSize: str
    LastVenue: str
    VWAP: str


class QuoteError(BaseModel):
    """
    Error information for a symbol quote request.
    """

    Symbol: str
    Error: str


class QuoteSnapshot(BaseModel):
    """
    Response containing multiple quote data and any errors.
    """

    Quotes: List[Quote]
    Errors: List[QuoteError]


# Valid time units for bar intervals
BarUnit = Literal["Minute", "Daily", "Weekly", "Monthly"]

# US stock market session templates for extended trading hours
SessionTemplate = Literal["USEQPre", "USEQPost", "USEQPreAndPost", "USEQ24Hour", "Default"]

# Bar status types
BarStatus = Literal["Open", "Closed"]


class Bar(BaseModel):
    """
    Represents a single price bar with OHLC and volume data
    """

    # The closing price of the current bar
    Close: str
    # A trade made at a price less than the previous trade price or at a price equal to the previous trade price
    DownTicks: int
    # Volume traded on downticks. A tick is considered a downtick if the previous tick was a downtick or the price is lower than the previous tick
    DownVolume: int
    # The Epoch time
    Epoch: int
    # The high price of the current bar
    High: str
    # Conveys that all historical bars in the request have been delivered
    IsEndOfHistory: bool
    # Set when there is data in the bar and the data is being built in "real time" from a trade
    IsRealtime: bool
    # The low price of the current bar
    Low: str
    # The open price of the current bar
    Open: str
    # The total number of open contracts (futures/options)
    OpenInterest: str
    # ISO8601 formatted timestamp
    TimeStamp: str
    # Total number of trades in the bar
    TotalTicks: int
    # Total volume for the bar
    TotalVolume: str
    # Number of trades with no price change
    UnchangedTicks: Optional[int] = None
    # Volume of trades with no price change
    UnchangedVolume: Optional[int] = None
    # Number of trades that moved the price up
    UpTicks: int
    # Volume of trades that moved the price up
    UpVolume: int
    # Status of the bar
    BarStatus: BarStatus


class BarsResponse(BaseModel):
    """
    Contains a list of barchart data
    """

    # Array of price bars
    Bars: List[Bar]


class BarHistoryParams(BaseModel):
    """
    Parameters for requesting historical bars
    """

    # Default: 1. Interval that each bar will consist of.
    # For minute bars, the number of minutes aggregated in a single bar.
    # For bar units other than minute, value must be 1.
    # For unit Minute the max allowed Interval is 1440.
    interval: Optional[str] = None

    # Default: Daily. The unit of time for each bar interval.
    # Valid values are: Minute, Daily, Weekly, Monthly.
    unit: Optional[BarUnit] = None

    # Default: 1. Number of bars back to fetch.
    # Maximum of 57,600 bars for intraday requests.
    # No limit for daily, weekly, or monthly bars.
    # Mutually exclusive with firstdate.
    barsback: Optional[int] = None

    # The first date to fetch bars from.
    # Format: YYYY-MM-DD or ISO8601 (e.g. 2020-04-20T18:00:00Z)
    # Mutually exclusive with barsback.
    firstdate: Optional[str] = None

    # The last date to fetch bars to. Defaults to current time.
    # Format: YYYY-MM-DD or ISO8601 (e.g. 2020-04-20T18:00:00Z)
    # Mutually exclusive with startdate (deprecated).
    lastdate: Optional[str] = None

    # US stock market session template for extended trading hours.
    # Ignored for non-US equity symbols.
    sessiontemplate: Optional[SessionTemplate] = None


class OptionGreeks(BaseModel):
    """
    Option Greek values for option contracts.
    """

    Delta: float
    Gamma: float
    Theta: float
    Vega: float
    Rho: float
    ImpliedVolatility: float


class OptionChain(BaseModel):
    """
    Data structure containing option chain information.
    """

    UnderlyingSymbol: str
    Expirations: List[str]
    Strikes: List[float]
    Greeks: OptionGreeks


class OptionQuote(Quote):
    """
    Quote data for an option contract, extending the base Quote model.
    """

    StrikePrice: float
    ExpirationDate: str
    Type: Literal["Call", "Put"]
    Greeks: OptionGreeks


class MarketDepthQuoteData(BaseModel):
    """
    Data for a single market depth quote level.
    """

    TimeStamp: str
    Side: Literal["Bid", "Ask"]
    Price: str
    Size: str
    OrderCount: int
    Name: str


class MarketDepthQuote(BaseModel):
    """
    Full market depth quote data with bids and asks.
    """

    Bids: List[MarketDepthQuoteData]
    Asks: List[MarketDepthQuoteData]


class MarketDepthParams(BaseModel):
    """
    Parameters for market depth queries.
    """

    maxlevels: Optional[int] = None  # Default: 20


# Asset types for symbols
AssetType = Literal["STOCK", "FUTURE", "STOCKOPTION", "INDEXOPTION", "FOREX", "CRYPTO", "INDEX"]
# Option types
CallPut = Literal["Call", "Put", "CALL", "PUT"]


class PriceFormat(BaseModel):
    """
    Format information for price display and increments.
    """

    Format: Literal["Decimal", "Fraction", "SubFraction"]
    Decimals: Optional[str] = None
    Fraction: Optional[str] = None
    SubFraction: Optional[str] = None
    IncrementStyle: Literal["Simple", "Schedule"]
    Increment: Optional[str] = None
    PointValue: str


class QuantityFormat(BaseModel):
    """
    Format information for quantity display and increments.
    """

    Format: Literal["Decimal"]
    Decimals: str
    IncrementStyle: Literal["Simple"]
    Increment: str
    MinimumTradeQuantity: str


class SymbolDetail(BaseModel):
    """
    Detailed information about a trading symbol.
    """

    AssetType: AssetType
    Country: str
    Currency: str
    Description: str
    Exchange: str
    ExpirationDate: Optional[str] = None
    FutureType: Optional[str] = None
    OptionType: Optional[CallPut] = None
    PriceFormat: PriceFormat
    QuantityFormat: QuantityFormat
    Root: str
    StrikePrice: Optional[str] = None
    Symbol: str
    Underlying: Optional[str] = None


class SymbolDetailsErrorResponse(BaseModel):
    """
    Error response for symbol details request.
    """

    Symbol: str
    Message: str


class SymbolDetailsResponse(BaseModel):
    """
    Response containing symbol details and any errors.
    """

    Symbols: List[SymbolDetail]
    Errors: List[SymbolDetailsErrorResponse]


class Heartbeat(BaseModel):
    """
    Heartbeat message for stream connections.
    """

    Heartbeat: int
    Timestamp: str


class StreamErrorResponse(BaseModel):
    """
    Error response for stream connections.
    """

    Error: str
    Message: str


class QuoteStream(BaseModel):
    """
    Quote data for streaming.
    """

    Symbol: str
    Ask: str
    AskSize: str
    Bid: str
    BidSize: str
    Close: str
    DailyOpenInterest: str
    High: str
    Low: str
    High52Week: str
    High52WeekTimestamp: str
    Last: str
    MinPrice: Optional[str] = None
    MaxPrice: Optional[str] = None
    FirstNoticeDate: Optional[str] = None
    LastTradingDate: Optional[str] = None
    Low52Week: str
    Low52WeekTimestamp: str
    MarketFlags: MarketFlags
    NetChange: str
    NetChangePct: str
    Open: str
    PreviousClose: str
    PreviousVolume: str
    TickSizeTier: str
    TradeTime: str
    Volume: str
    Error: Optional[str] = None


class BarStreamParams(BaseModel):
    """
    Parameters for streaming bar data
    """

    # Default: 1. Interval that each bar will consist of.
    # For minute bars, the number of minutes aggregated in a single bar.
    # For bar units other than minute, value must be 1.
    interval: Optional[str] = None

    # Default: Daily. Unit of time for each bar interval.
    # Valid values are: minute, daily, weekly, and monthly.
    unit: Optional[BarUnit] = None

    # The bars back - the max value is 57600.
    barsback: Optional[int] = None

    # US stock market session template for extended trading hours.
    # Ignored for non-US equity symbols.
    sessiontemplate: Optional[SessionTemplate] = None


class SpreadLeg(BaseModel):
    """
    Information about a single leg in an option spread.
    """

    Symbol: str
    Ratio: int
    StrikePrice: str
    Expiration: str
    OptionType: Literal["Call", "Put"]


class Spread(BaseModel):
    """
    Comprehensive data about an option spread.
    """

    Delta: str
    Theta: str
    Gamma: str
    Rho: str
    Vega: str
    ImpliedVolatility: str
    IntrinsicValue: str
    ExtrinsicValue: str
    TheoreticalValue: str
    ProbabilityITM: str
    ProbabilityOTM: str
    ProbabilityBE: str
    ProbabilityITM_IV: str
    ProbabilityOTM_IV: str
    ProbabilityBE_IV: str
    TheoreticalValue_IV: str
    StandardDeviation: str
    DailyOpenInterest: int
    Ask: str
    Bid: str
    Mid: str
    AskSize: int
    BidSize: int
    Close: str
    High: str
    Last: str
    Low: str
    NetChange: str
    NetChangePct: str
    Open: str
    PreviousClose: str
    Volume: int
    Side: Literal["Call", "Put", "Both"]
    Strikes: List[str]
    Legs: List[SpreadLeg]


class OptionChainParams(BaseModel):
    """
    Parameters for option chain requests.
    """

    # Date on which the option contract expires; must be a valid expiration date.
    # Defaults to the next contract expiration date.
    # Format: YYYY-MM-DD or ISO8601 (e.g., "2024-01-19" or "2024-01-19T00:00:00Z")
    expiration: Optional[str] = None

    # Second contract expiration date required for Calendar and Diagonal spreads.
    # Format: YYYY-MM-DD or ISO8601 (e.g., "2024-01-19" or "2024-01-19T00:00:00Z")
    expiration2: Optional[str] = None

    # Specifies the number of spreads to display above and below the priceCenter.
    # Default: 5
    strikeProximity: Optional[int] = None

    # Specifies the name of the spread type to use.
    # Common values: "Single", "Vertical", "Calendar", "Butterfly", "Condor", "Straddle", "Strangle"
    # Default: "Single"
    spreadType: Optional[str] = None

    # The theoretical rate of return of an investment with zero risk.
    # Defaults to the current quote for $IRX.X.
    # The percentage rate should be specified as a decimal value between 0 and 1.
    # For example, to use 2% for the rate, pass in 0.02.
    riskFreeRate: Optional[float] = None

    # Specifies the strike price center.
    # Defaults to the last quoted price for the underlying security.
    priceCenter: Optional[float] = None

    # Specifies the desired interval between the strike prices in a spread.
    # Must be greater than or equal to 1.
    # A value of 1 uses consecutive strikes; a value of 2 skips one between strikes; and so on.
    # Default: 1
    strikeInterval: Optional[int] = None

    # Specifies whether or not greeks properties are returned.
    # Default: true
    enableGreeks: Optional[bool] = None

    # Filters the chain by intrinsic value:
    # - "ITM" (in-the-money): includes only spreads that have an intrinsic value greater than zero
    # - "OTM" (out-of-the-money): includes only spreads that have an intrinsic value equal to zero
    # - "All": includes all spreads regardless of intrinsic value
    # Default: "All"
    strikeRange: Optional[Literal["All", "ITM", "OTM"]] = None

    # Filters the spreads by a specific option type.
    # Valid values are "All", "Call", and "Put".
    # Default: "All"
    optionType: Optional[Literal["All", "Call", "Put"]] = None


class OptionQuoteLeg(BaseModel):
    """
    Information about a leg for an option quote request.
    """

    Symbol: str
    Ratio: Optional[int] = None  # Default: 1


class OptionQuoteParams(BaseModel):
    """
    Parameters for option quote requests.
    """

    legs: List[OptionQuoteLeg]
    riskFreeRate: Optional[float] = None
    enableGreeks: Optional[bool] = None  # Default: true


class AggregatedQuoteData(BaseModel):
    """
    Aggregated market depth data for a price level.
    """

    EarliestTime: str
    LatestTime: str
    Side: Literal["Bid", "Ask"]
    Price: str
    TotalSize: str
    BiggestSize: str
    SmallestSize: str
    NumParticipants: int
    TotalOrderCount: int


class MarketDepthAggregate(BaseModel):
    """
    Aggregated market depth for all price levels.
    """

    Bids: List[AggregatedQuoteData]
    Asks: List[AggregatedQuoteData]


class SymbolNames(BaseModel):
    """
    A collection of Symbol names.
    """

    # Array of symbol names
    SymbolNames: List[str]


class Expiration(BaseModel):
    """
    Represents a single option expiration date with its type
    """

    # The expiration date in ISO8601 format
    Date: str
    # The type of expiration (Monthly, Weekly, Quarterly)
    Type: Literal["Monthly", "Weekly", "Quarterly"]


class Expirations(BaseModel):
    """
    Response containing available option expiration dates
    """

    # Array of available expiration dates
    Expirations: List[Expiration]


class RiskRewardLeg(BaseModel):
    """
    Represents a leg in an option spread for risk/reward analysis.
    """

    # The option symbol (e.g., 'AAPL 240119C150')
    Symbol: str
    # Position ratio (positive for long, negative for short)
    Ratio: int
    # Option's opening price
    OpenPrice: str
    # Target price for profit taking
    TargetPrice: str
    # Stop price for loss protection
    StopPrice: str


class RiskRewardAnalysisInput(BaseModel):
    """
    Provides the required information to analyze the risk vs. reward of a potential option spread trade.
    """

    # The current price of the spread
    SpreadPrice: str
    # Array of legs in the option spread
    Legs: List[RiskRewardLeg]


class RiskRewardAnalysis(BaseModel):
    """
    Result of analyzing the risk vs. reward of a potential option spread trade.
    (NOTE: This model seems INCORRECT based on OpenAPI spec for /v3/marketdata/options/riskreward)
    """

    # The current price of the spread
    SpreadPrice: str
    # Maximum potential gain from the spread
    MaxGain: str
    # Maximum potential loss from the spread
    MaxLoss: str
    # Risk/Reward ratio (higher is better)
    RiskRewardRatio: str
    # Estimated commission costs
    Commission: str
    # The legs of the spread with their individual metrics
    Legs: List[RiskRewardLeg]


# NEW MODEL based on OpenAPI spec /v3/marketdata/options/riskreward response
class RiskRewardAnalysisResult(BaseModel):
    """
    Result of the risk/reward analysis from the TradeStation API.
    Matches the RiskRewardAnalysisResult schema in the OpenAPI spec.
    """

    MaxGainIsInfinite: bool
    AdjustedMaxGain: str
    MaxLossIsInfinite: bool
    AdjustedMaxLoss: str
    BreakevenPoints: List[str]


class SpreadType(BaseModel):
    """
    Represents an option spread type configuration.
    Each spread type defines whether it uses strike intervals and/or multiple expirations.
    """

    # The name of the spread type (e.g., 'Single', 'Butterfly', 'Calendar', etc.)
    Name: str
    # Whether the spread type uses strike intervals between legs
    StrikeInterval: bool
    # Whether the spread type can use multiple expiration dates
    ExpirationInterval: bool


class SpreadTypes(BaseModel):
    """
    Response from the Get Option Spread Types endpoint.
    Contains a list of available option spread types and their configurations.
    """

    # Array of available spread types and their configurations
    SpreadTypes: List[SpreadType]


class Strikes(BaseModel):
    """
    Response containing available strike prices for a specific spread type.
    """

    # Name of the spread type for these strikes
    SpreadType: str
    # Array of the strike prices for this spread type.
    # Each element in the Strikes array is an array of strike prices for a single spread.
    # For example, for a Butterfly spread, each inner array contains three strikes:
    # [["145", "150", "155"], ["150", "155", "160"]]
    Strikes: List[List[str]]


class OptionExpiration(BaseModel):
    """
    Detailed information about an option expiration date.
    """

    ExpirationDate: str
    DaysToExpiration: int
    IsWeekly: bool
    IsMonthlies: bool
    IsQuarterly: bool
    IsLeaps: bool
    StrikePrices: List[str]


class OptionExpirations(BaseModel):
    """
    Response containing option expiration dates.
    """

    Expirations: List[OptionExpiration]


class OptionRiskRewardRequest(BaseModel):
    """
    Request to analyze risk/reward for an option.
    """

    Symbol: str
    Quantity: int
    OpenPrice: str
    TargetPrice: str
    StopPrice: str


class OptionRiskReward(BaseModel):
    """
    Risk/reward analysis result for an option.
    """

    Symbol: str
    Quantity: int
    OpenPrice: str
    TargetPrice: str
    StopPrice: str
    MaxGain: str
    MaxLoss: str
    RiskRewardRatio: str
    Commission: str


# Define union types for stream responses
QuoteStreamResponse = Union[QuoteStream, Heartbeat, StreamErrorResponse]
BarStreamResponse = Union[Bar, Heartbeat, StreamErrorResponse]
OptionChainStreamResponse = Union[Spread, Heartbeat, StreamErrorResponse]
OptionQuoteStreamResponse = Union[Spread, Heartbeat, StreamErrorResponse]
MarketDepthStreamResponse = Union[MarketDepthQuote, Heartbeat, StreamErrorResponse]
MarketDepthAggregateStreamResponse = Union[MarketDepthAggregate, Heartbeat, StreamErrorResponse]
