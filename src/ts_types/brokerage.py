from typing import List, Optional, Union, Literal, ForwardRef
from pydantic import BaseModel, Field


class AccountDetail(BaseModel):
    """
    Contains detailed account information
    """

    # Indicates if the account is eligible for stock locate
    IsStockLocateEligible: bool
    # Indicates if the account is enrolled in RegT program
    EnrolledInRegTProgram: bool
    # Indicates if buying power warning is required
    RequiresBuyingPowerWarning: bool
    # Indicates if the account is qualified for day trading
    DayTradingQualified: bool
    # The option approval level for the account
    OptionApprovalLevel: int
    # Indicates if the account is flagged as a pattern day trader
    PatternDayTrader: bool


class Account(BaseModel):
    """
    Contains brokerage account information for individual brokerage accounts.
    """

    # The unique identifier for the account
    AccountID: str
    # The type of the TradeStation Account. Valid values are: Cash, Margin, Futures, and DVP
    AccountType: Literal["Cash", "Margin", "Futures", "DVP"]
    # A user specified name that identifies a TradeStation account. Omits if not set
    Alias: Optional[str] = None
    # TradeStation account ID for accounts based in Japan. Omits if not set
    AltID: Optional[str] = None
    # Currency associated with this account
    Currency: str
    # Status of a specific account:
    # - Active
    # - Closed
    # - Closing Transaction Only
    # - Margin Call - Closing Transactions Only
    # - Inactive
    # - Liquidating Transactions Only
    # - Restricted
    # - 90 Day Restriction-Closing Transaction Only
    Status: str
    # Detailed account information
    AccountDetail: Optional["AccountDetail"] = None

    model_config = {"arbitrary_types_allowed": True}


# Type definitions
AccountType = Literal["Cash", "Margin", "Futures", "Crypto"]
TradingType = Literal["Equities", "Options", "Futures", "Forex", "Crypto"]
AccountStatus = Literal["Active", "Closed", "Suspended"]
MarginType = Literal["Reg T", "Portfolio Margin"]


class BalanceDetail(BaseModel):
    """
    Contains real-time balance information that varies according to account type.
    """

    CostOfPositions: Optional[str] = None
    DayTradeExcess: Optional[str] = None
    DayTradeMargin: Optional[str] = None
    DayTradeOpenOrderMargin: Optional[str] = None
    DayTrades: Optional[str] = None
    InitialMargin: Optional[str] = None
    MaintenanceMargin: Optional[str] = None
    MaintenanceRate: Optional[str] = None
    MarginRequirement: Optional[str] = None
    UnrealizedProfitLoss: Optional[str] = None
    UnsettledFunds: Optional[str] = None


class CurrencyDetail(BaseModel):
    """
    Contains currency-specific balance information (only applies to futures).
    """

    Currency: str
    BODOpenTradeEquity: Optional[str] = None
    CashBalance: Optional[str] = None
    Commission: Optional[str] = None
    MarginRequirement: Optional[str] = None
    NonTradeDebit: Optional[str] = None
    NonTradeNetBalance: Optional[str] = None
    OptionValue: Optional[str] = None
    RealTimeUnrealizedGains: Optional[str] = None
    TodayRealTimeTradeEquity: Optional[str] = None
    TradeEquity: Optional[str] = None


class Balance(BaseModel):
    """
    Contains realtime balance information for a single account.
    """

    AccountID: str
    AccountType: Optional[str] = None
    BalanceDetail: Optional["BalanceDetail"] = None
    BuyingPower: Optional[str] = None
    CashBalance: Optional[str] = None
    Commission: Optional[str] = None
    CurrencyDetails: Optional[List["CurrencyDetail"]] = None
    Equity: Optional[str] = None
    MarketValue: Optional[str] = None
    TodaysProfitLoss: Optional[str] = None
    UnclearedDeposit: Optional[str] = None

    model_config = {"arbitrary_types_allowed": True}


class BalanceError(BaseModel):
    """
    Contains error details for partial success responses.
    """

    AccountID: str
    Error: str
    Message: str


class Balances(BaseModel):
    """
    Contains a collection of realtime balance information.
    """

    Balances: List[Balance]
    Errors: Optional[List["BalanceError"]] = None

    model_config = {"arbitrary_types_allowed": True}


class BODBalanceDetail(BaseModel):
    """
    Contains beginning of day balance information that varies according to account type.
    """

    AccountBalance: Optional[str] = None
    CashAvailableToWithdraw: Optional[str] = None
    DayTrades: Optional[str] = None
    DayTradingMarginableBuyingPower: Optional[str] = None
    Equity: Optional[str] = None
    NetCash: Optional[str] = None
    OptionBuyingPower: Optional[str] = None
    OptionValue: Optional[str] = None
    OvernightBuyingPower: Optional[str] = None


class BODCurrencyDetail(BaseModel):
    """
    Contains currency-specific beginning of day balance information (only applies to futures).
    """

    Currency: str
    AccountMarginRequirement: Optional[str] = None
    AccountOpenTradeEquity: Optional[str] = None
    AccountSecurities: Optional[str] = None
    CashBalance: Optional[str] = None
    MarginRequirement: Optional[str] = None


class BODBalance(BaseModel):
    """
    Contains beginning of day balance information for a single account.
    """

    AccountID: str
    AccountType: Optional[str] = None
    BalanceDetail: Optional["BODBalanceDetail"] = None
    CurrencyDetails: Optional[List["BODCurrencyDetail"]] = None

    model_config = {"arbitrary_types_allowed": True}


class BalancesBOD(BaseModel):
    """
    Contains a collection of beginning of day balance information.
    """

    BODBalances: List[BODBalance]
    Errors: Optional[List["BalanceError"]] = None

    model_config = {"arbitrary_types_allowed": True}


class PositionError(BaseModel):
    """
    Error information for position requests.
    """

    # The AccountID of the error, may contain multiple Account IDs in comma separated format
    AccountID: str
    # The Error
    Error: str
    # The error message
    Message: str


class PositionResponse(BaseModel):
    """
    Position represents a position that is returned for an Account.
    """

    # The unique identifier for the account
    AccountID: str
    # Indicates the asset type of the position
    AssetType: Literal["STOCK", "STOCKOPTION", "FUTURE", "INDEXOPTION", "UNKNOWN"]
    # The average price of the position currently held
    AveragePrice: str
    # The highest price a prospective buyer is prepared to pay at a particular time for a trading unit of a given symbol
    Bid: str
    # The price at which a security, futures contract, or other financial instrument is offered for sale
    Ask: str
    # The currency conversion rate that is used in order to convert from the currency of the symbol to the currency of the account
    ConversionRate: str
    # (Futures) DayTradeMargin used on open positions. Currently only calculated for futures positions. Other asset classes will have a 0 for this value
    DayTradeRequirement: str
    # The UTC formatted expiration date of the future or option symbol, in the country the contract is traded in. The time portion of the value should be ignored
    ExpirationDate: Optional[str] = None
    # Only applies to future and option positions. The margin account balance denominated in the symbol currency required for entering a position on margin
    InitialRequirement: str
    # The margin account balance denominated in the account currency required for maintaining a position on margin
    MaintenanceMargin: str
    # The last price at which the symbol traded
    Last: str
    # Specifies if the position is Long or Short
    LongShort: Literal["Long", "Short"]
    # Only applies to equity and option positions. The MarkToMarketPrice value is the weighted average of the previous close price for the position quantity held overnight and the purchase price of the position quantity opened during the current market session. This value is used to calculate TodaysProfitLoss
    MarkToMarketPrice: str
    # The actual market value denominated in the symbol currency of the open position. This value is updated in real-time
    MarketValue: str
    # A unique identifier for the position
    PositionID: str
    # The number of shares or contracts for a particular position. This value is negative for short positions
    Quantity: str
    # Symbol of the position
    Symbol: str
    # Time the position was entered
    Timestamp: str
    # Only applies to equity and option positions. This value will be included in the payload to convey the unrealized profit or loss denominated in the account currency on the position held, calculated using the MarkToMarketPrice
    TodaysProfitLoss: str
    # The total cost denominated in the account currency of the open position
    TotalCost: str
    # The unrealized profit or loss denominated in the symbol currency on the position held, calculated based on the average price of the position
    UnrealizedProfitLoss: str
    # The unrealized profit or loss on the position expressed as a percentage of the initial value of the position
    UnrealizedProfitLossPercent: str
    # The unrealized profit or loss denominated in the account currency divided by the number of shares, contracts or units held
    UnrealizedProfitLossQty: str


class Positions(BaseModel):
    """
    Contains a collection of positions for the requested accounts.
    """

    # Array of positions
    Positions: List[PositionResponse]
    # Array of errors that occurred during the request
    Errors: Optional[List["PositionError"]] = None

    model_config = {"arbitrary_types_allowed": True}


# Activity type enum
ActivityType = Literal[
    "Trade", "Dividend", "Interest", "Transfer", "Fee", "Journal", "Deposit", "Withdrawal"
]


class Activity(BaseModel):
    """
    Represents an account activity record.
    """

    AccountID: str
    ActivityType: ActivityType
    Symbol: Optional[str] = None
    Description: str
    Amount: float
    TradeDate: Optional[str] = None
    SettleDate: Optional[str] = None
    TransactionID: str
    OrderID: Optional[str] = None


class ActivityFilter(BaseModel):
    """
    Filter for querying account activity.
    """

    startDate: Optional[str] = None
    endDate: Optional[str] = None
    activityType: Optional[List[ActivityType]] = None
    symbol: Optional[str] = None
    pageSize: Optional[int] = None
    pageNumber: Optional[int] = None


class ErrorResponse(BaseModel):
    """
    Contains error details when a request fails.
    """

    # Error Title, can be any of:
    # - BadRequest
    # - Unauthorized
    # - Forbidden
    # - TooManyRequests
    # - InternalServerError
    # - NotImplemented
    # - ServiceUnavailable
    # - GatewayTimeout
    Error: str
    # The description of the error
    Message: str


class MarketActivationRule(BaseModel):
    """
    Market activation rule for conditional orders.
    """

    # Type of rule (e.g., "Price")
    RuleType: str
    # Symbol the rule is based on
    Symbol: str
    # Predicate for the rule (e.g., "gt" for greater than)
    Predicate: str
    # Key used for triggering
    TriggerKey: str
    # Price level for the rule
    Price: str


class TrailingStop(BaseModel):
    """
    Trailing stop information for orders.
    """

    # Amount of the trailing stop
    Amount: Optional[str] = None
    # Type of trailing stop
    AmountType: Optional[str] = None


class OrderLeg(BaseModel):
    """
    Represents a leg in a multi-leg order.
    """

    # The type of asset (e.g., "STOCK", "OPTION")
    AssetType: str
    # Buy or sell action
    BuyOrSell: Literal["Buy", "Sell"]
    # Quantity that has been executed
    ExecQuantity: str
    # Price at which the order was executed
    ExecutionPrice: Optional[str] = None
    # Expiration date for options
    ExpirationDate: Optional[str] = None
    # Whether the position is being opened or closed
    OpenOrClose: Optional[Literal["Open", "Close"]] = None
    # Type of option (CALL or PUT)
    OptionType: Optional[str] = None
    # Total quantity ordered
    QuantityOrdered: str
    # Quantity still remaining to be filled
    QuantityRemaining: str
    # Strike price for options
    StrikePrice: Optional[str] = None
    # The symbol being traded
    Symbol: str
    # The underlying symbol for options
    Underlying: Optional[str] = None


# Define the order status literals
HistoricalOrderStatus = Literal[
    # Open statuses
    "ACK",  # Received
    "ASS",  # Option Assignment
    "BRC",  # Bracket Canceled
    "BRF",  # Bracket Filled
    "BRO",  # Broken
    "CHG",  # Change
    "CND",  # Condition Met
    "COR",  # Fill Corrected
    "DIS",  # Dispatched
    "DOA",  # Dead
    "DON",  # Queued
    "ECN",  # Expiration Cancel Request
    "EXE",  # Option Exercise
    "FPR",  # Partial Fill (Alive)
    "LAT",  # Too Late to Cancel
    "OPN",  # Sent
    "OSO",  # OSO Order
    "OTHER",  # OrderStatus not mapped
    "PLA",  # Sending
    "REC",  # Big Brother Recall Request
    "RJC",  # Cancel Request Rejected
    "RPD",  # Replace Pending
    "RSN",  # Replace Sent
    "STP",  # Stop Hit
    "STT",  # OrderStatus Message
    "SUS",  # Suspended
    "UCN",  # Cancel Sent
    # Canceled statuses
    "CAN",  # Canceled
    "EXP",  # Expired
    "OUT",  # UROut
    "RJR",  # Change Request Rejected
    "SCN",  # Big Brother Recall
    "TSC",  # Trade Server Canceled
    # Rejected status
    "REJ",  # Rejected
    # Filled statuses
    "FLL",  # Filled
    "FLP",  # Partial Fill (UROut)
]

# For current orders, use the same status literals
OrderStatus = HistoricalOrderStatus


class OrderBase(BaseModel):
    """
    Base order information shared by all order types.
    """

    # The account ID associated with the order
    AccountID: str
    # The commission fee for the order
    CommissionFee: Optional[str] = None
    # The currency of the order
    Currency: Optional[str] = None
    # The duration of the order (e.g., "DAY", "GTC")
    Duration: Optional[str] = None
    # The good till date for GTD orders
    GoodTillDate: Optional[str] = None
    # The legs of the order for multi-leg orders
    Legs: Optional[List["OrderLeg"]] = None
    # Market activation rules for conditional orders
    MarketActivationRules: Optional[List["MarketActivationRule"]] = None
    # The unique identifier for the order
    OrderID: str
    # The date and time when the order was opened
    OpenedDateTime: Optional[str] = None
    # The type of order (e.g., "Market", "Limit")
    OrderType: Optional[str] = None
    # The price used for buying power calculations
    PriceUsedForBuyingPower: Optional[str] = None
    # The routing destination for the order
    Routing: Optional[str] = None
    # Advanced options string for complex orders
    AdvancedOptions: Optional[str] = None

    model_config = {"arbitrary_types_allowed": True}


class ConditionalOrder(BaseModel):
    """
    Represents a conditional order relationship.
    """

    # The relationship type (e.g., "OCO" for One-Cancels-Other)
    Relationship: str
    # The ID of the related order
    OrderID: str


class HistoricalOrder(OrderBase):
    """
    Historical order information extending the base order.
    """

    # The date and time when the order was closed/filled
    ClosedDateTime: Optional[str] = None
    # The status of the historical order
    Status: Optional[HistoricalOrderStatus] = None
    # Description of the order status
    StatusDescription: Optional[str] = None
    # The stop price for stop and stop-limit orders
    StopPrice: Optional[str] = None
    # Trailing stop information
    TrailingStop: Optional["TrailingStop"] = None
    # Only applies to equities. Will contain a value if the order has received a routing fee
    UnbundledRouteFee: Optional[str] = None
    # Conditional orders associated with this order
    ConditionalOrders: Optional[List["ConditionalOrder"]] = None

    model_config = {"arbitrary_types_allowed": True}


class OrderError(BaseModel):
    """
    Error information for order requests.
    """

    # The account ID associated with the error
    AccountID: str
    # The type of error that occurred
    Error: str
    # Detailed error message
    Message: str


class HistoricalOrders(BaseModel):
    """
    Contains a collection of historical orders for the requested accounts.
    """

    # Array of historical orders
    Orders: List[HistoricalOrder]
    # Array of errors that occurred during the request
    Errors: Optional[List["OrderError"]] = None
    # Token for paginated results to retrieve the next page
    NextToken: Optional[str] = None

    model_config = {"arbitrary_types_allowed": True}


class OrderByIDError(BaseModel):
    """
    Error information for order by ID requests.
    """

    # The AccountID of the error, may contain multiple Account IDs in comma separated format
    AccountID: str
    # The OrderID of the error
    OrderID: str
    # The Error
    Error: str
    # The error message
    Message: str


class HistoricalOrdersById(BaseModel):
    """
    Contains a collection of historical orders for specific order IDs.
    """

    # Array of historical orders
    Orders: List[HistoricalOrder]
    # Array of errors that occurred during the request
    Errors: Optional[List["OrderByIDError"]] = None

    model_config = {"arbitrary_types_allowed": True}


class Order(OrderBase):
    """
    Contains order information for today's orders and open orders.
    """

    # The status of the order
    Status: Optional[OrderStatus] = None
    # Description of the status
    StatusDescription: Optional[str] = None
    # The stop price for StopLimit and StopMarket orders
    StopPrice: Optional[str] = None
    # Trailing stop information
    TrailingStop: Optional["TrailingStop"] = None
    # Only applies to equities. Will contain a value if the order has received a routing fee
    UnbundledRouteFee: Optional[str] = None
    # The limit price for this order
    LimitPrice: Optional[str] = None


class Orders(BaseModel):
    """
    Contains a collection of today's orders and open orders.
    """

    # Array of orders
    Orders: List[Order]
    # Array of errors that occurred during the request
    Errors: Optional[List["OrderError"]] = None
    # Token for paginated results to retrieve the next page
    NextToken: Optional[str] = None

    model_config = {"arbitrary_types_allowed": True}


class OrdersById(BaseModel):
    """
    Contains a collection of today's orders and open orders for specific order IDs.
    """

    # Array of orders
    Orders: List[Order]
    # Array of errors that occurred during the request
    Errors: Optional[List["OrderByIDError"]] = None

    model_config = {"arbitrary_types_allowed": True}


class StreamOrderErrorResponse(BaseModel):
    """
    Stream error response.
    """

    # The type of error
    Error: str
    # The error message
    Message: str
    # The account ID associated with the error
    AccountID: Optional[str] = None
    # The order ID associated with the error
    OrderID: Optional[str] = None


class StreamOrderResponseData(BaseModel):
    """
    Response data for order streams.
    """

    # The unique identifier for the order
    OrderID: str
    # The account ID associated with the order
    AccountID: str
    # The status of the order
    Status: OrderStatus
    # Description of the order status
    StatusDescription: str
    # The type of order (e.g., "Market", "Limit")
    OrderType: str
    # The symbol being traded
    Symbol: str
    # Total quantity ordered
    Quantity: str
    # Quantity that has been filled
    FilledQuantity: str
    # Quantity remaining to be filled
    RemainingQuantity: str
    # The commission fee for the order
    CommissionFee: Optional[str] = None
    # The currency of the order
    Currency: Optional[str] = None
    # The duration of the order (e.g., "DAY", "GTC")
    Duration: Optional[str] = None
    # The good till date for GTD orders
    GoodTillDate: Optional[str] = None
    # The legs of the order for multi-leg orders
    Legs: Optional[List["OrderLeg"]] = None
    # Market activation rules for conditional orders
    MarketActivationRules: Optional[List["MarketActivationRule"]] = None
    # The date and time when the order was opened
    OpenedDateTime: Optional[str] = None
    # The price used for buying power calculations
    PriceUsedForBuyingPower: Optional[str] = None
    # The routing destination for the order
    Routing: Optional[str] = None
    # Advanced options string for complex orders
    AdvancedOptions: Optional[str] = None
    # The stop price for stop and stop-limit orders
    StopPrice: Optional[str] = None
    # The limit price for limit orders
    LimitPrice: Optional[str] = None
    # Only applies to equities. Will contain a value if the order has received a routing fee
    UnbundledRouteFee: Optional[str] = None

    model_config = {"arbitrary_types_allowed": True}


# StreamOrderResponse can be either StreamOrderResponseData or StreamOrderErrorResponse
# This will be handled through Union types when used in functions


class StreamStatus(BaseModel):
    """
    Stream status update.
    """

    # The status of the stream
    StreamStatus: Literal["Connected", "Disconnected"]
    # Additional status message
    Message: Optional[str] = None


class StreamHeartbeat(BaseModel):
    """
    Stream heartbeat.
    """

    # Heartbeat timestamp
    Heartbeat: str
