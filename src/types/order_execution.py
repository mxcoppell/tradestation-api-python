"""
Order execution types for the TradeStation API Python wrapper.

This module defines all the data structures related to order execution functionality from the TradeStation API.
"""

from enum import Enum
from typing import List, Optional, Union, Literal

from pydantic import BaseModel, Field


class OrderType(str, Enum):
    """Type of order to place."""

    MARKET = "Market"
    LIMIT = "Limit"
    STOP_MARKET = "StopMarket"
    STOP_LIMIT = "StopLimit"


class OrderDuration(str, Enum):
    """Time in force settings for an order."""

    DAY = "DAY"  # Day, valid until the end of the regular trading session
    DYP = "DYP"  # Day Plus; valid until the end of the extended trading session
    GTC = "GTC"  # Good till canceled
    GCP = "GCP"  # Good till canceled plus
    GTD = "GTD"  # Good through date
    GDP = "GDP"  # Good through date plus
    OPG = "OPG"  # At the opening; only valid for listed stocks at the opening session Price
    CLO = "CLO"  # On Close; orders that target the closing session of an exchange
    IOC = "IOC"  # Immediate or Cancel; filled immediately or canceled, partial fills are accepted
    FOK = "FOK"  # Fill or Kill; orders are filled entirely or canceled, partial fills are not accepted
    ONE_MINUTE = "1"  # 1 minute; expires after the 1 minute
    ONE_MINUTE_ALT = "1 MIN"  # 1 minute; expires after the 1 minute
    THREE_MINUTES = "3"  # 3 minutes; expires after the 3 minutes
    THREE_MINUTES_ALT = "3 MIN"  # 3 minutes; expires after the 3 minutes
    FIVE_MINUTES = "5"  # 5 minutes; expires after the 5 minutes
    FIVE_MINUTES_ALT = "5 MIN"  # 5 minutes; expires after the 5 minutes


class OrderStatus(str, Enum):
    """Status of an order."""

    ACK = "ACK"  # Received
    ASS = "ASS"  # Option Assignment
    BRC = "BRC"  # Bracket Canceled
    BRF = "BRF"  # Bracket Filled
    BRO = "BRO"  # Broken
    CHG = "CHG"  # Change
    CND = "CND"  # Condition Met
    COR = "COR"  # Fill Corrected
    DIS = "DIS"  # Dispatched
    DOA = "DOA"  # Dead
    DON = "DON"  # Queued
    ECN = "ECN"  # Expiration Cancel Request
    EXE = "EXE"  # Option Exercise
    FPR = "FPR"  # Partial Fill (Alive)
    LAT = "LAT"  # Too Late to Cancel
    OPN = "OPN"  # Sent
    OSO = "OSO"  # OSO Order
    OTHER = "OTHER"  # OrderStatus not mapped
    PLA = "PLA"  # Sending
    REC = "REC"  # Big Brother Recall Request
    RJC = "RJC"  # Cancel Request Rejected
    RPD = "RPD"  # Replace Pending
    RSN = "RSN"  # Replace Sent
    STP = "STP"  # Stop Hit
    STT = "STT"  # OrderStatus Message
    SUS = "SUS"  # Suspended
    UCN = "UCN"  # Cancel Sent
    CAN = "CAN"  # Canceled
    EXP = "EXP"  # Expired
    OUT = "OUT"  # UROut
    RJR = "RJR"  # Change Request Rejected
    SCN = "SCN"  # Big Brother Recall
    TSC = "TSC"  # Trade Server Canceled
    UCH = "UCH"  # Replaced
    REJ = "REJ"  # Rejected
    FLL = "FLL"  # Filled
    FLP = "FLP"  # Partial Fill (UROut)


class OrderSide(str, Enum):
    """Buy/Sell action for an order."""

    BUY = "BUY"  # equities and futures
    SELL = "SELL"  # equities and futures
    BUY_TO_COVER = "BUYTOCOVER"  # equities
    SELL_SHORT = "SELLSHORT"  # equities
    BUY_TO_OPEN = "BUYTOOPEN"  # options
    BUY_TO_CLOSE = "BUYTOCLOSE"  # options
    SELL_TO_OPEN = "SELLTOOPEN"  # options
    SELL_TO_CLOSE = "SELLTOCLOSE"  # options


class MarketActivationRule(BaseModel):
    """Market Activation Rule for conditional orders."""

    RuleType: Literal["Price"]
    Symbol: str
    Predicate: Literal["Gt", "Lt", "Eq"]
    TriggerKey: str
    Price: str
    LogicOperator: Optional[Literal["And", "Or"]] = None

    model_config = {"arbitrary_types_allowed": True}


class TimeActivationRule(BaseModel):
    """Time Activation Rule for scheduled orders."""

    TimeUtc: str

    model_config = {"arbitrary_types_allowed": True}


class TrailingStop(BaseModel):
    """Trailing stop settings."""

    Amount: float
    IsPercentage: bool
    Percent: Optional[float] = None  # For backward compatibility with API examples

    model_config = {"arbitrary_types_allowed": True}


class AdvancedOptions(BaseModel):
    """Advanced options for order placement."""

    TrailingStop: Optional[Union[TrailingStop, dict]] = None
    MarketActivationRules: Optional[List[MarketActivationRule]] = None
    TimeActivationRules: Optional[List[TimeActivationRule]] = None
    CommissionFee: Optional[float] = None
    DoNotReduceFlag: Optional[bool] = None
    AllOrNone: Optional[bool] = None
    MinimumQuantity: Optional[int] = None

    model_config = {"arbitrary_types_allowed": True}


class OrderLeg(BaseModel):
    """Order leg for multi-leg orders (options spreads, covered stock)."""

    Symbol: str
    Quantity: int
    TradeAction: OrderSide

    model_config = {"arbitrary_types_allowed": True}


class TimeInForce(BaseModel):
    """Time in force settings."""

    Duration: OrderDuration
    ExpirationDate: Optional[str] = None

    model_config = {"arbitrary_types_allowed": True}


class OrderRequest(BaseModel):
    """Request to place a new order."""

    AccountID: str
    Symbol: str
    Quantity: str
    OrderType: OrderType
    TradeAction: OrderSide
    TimeInForce: TimeInForce
    Route: str
    LimitPrice: Optional[str] = None
    StopPrice: Optional[str] = None
    AdvancedOptions: Optional[AdvancedOptions] = None

    model_config = {"arbitrary_types_allowed": True}


class OrderResponseSuccess(BaseModel):
    """Successful order response."""

    OrderID: str
    Message: str

    model_config = {"arbitrary_types_allowed": True}


class OrderResponseError(BaseModel):
    """Error order response."""

    OrderID: str
    Error: str
    Message: str

    model_config = {"arbitrary_types_allowed": True}


class OrderResponse(BaseModel):
    """Response from placing an order (POST /orders)."""

    Orders: Optional[List[OrderResponseSuccess]] = None
    Errors: Optional[List[OrderResponseError]] = None

    model_config = {"arbitrary_types_allowed": True}


class CancelOrderResponse(BaseModel):
    """Response from canceling an order (DELETE /orders/{id})."""

    OrderID: str
    Error: Optional[str] = None
    Message: Optional[str] = None

    model_config = {"arbitrary_types_allowed": True}


class OrderReplaceTrailingStop(BaseModel):
    """Trailing stop settings for order replacement."""

    Amount: Optional[str] = None
    Percent: Optional[str] = None

    model_config = {"arbitrary_types_allowed": True}


class OrderReplaceAdvancedOptions(BaseModel):
    """Advanced options for order replacement."""

    TrailingStop: Optional[OrderReplaceTrailingStop] = None

    model_config = {"arbitrary_types_allowed": True}


class OrderReplaceTimeInForce(BaseModel):
    """Time in force settings for order replacement."""

    Duration: OrderDuration

    model_config = {"arbitrary_types_allowed": True}


class OrderReplaceRequest(BaseModel):
    """
    Request to replace an existing order.
    You cannot update an order that has been filled.
    Valid for Cash, Margin, Futures, and DVP account types.

    Examples:

    Limit Order:
    {
      "Quantity": "10",
      "LimitPrice": "132.52"
    }

    Stop Market Order:
    {
      "Quantity": "10",
      "StopPrice": "50.60"
    }

    Stop Limit Order:
    {
      "Quantity": "10",
      "LimitPrice": "200.00",
      "StopPrice": "215.00"
    }

    Trailing Stop (Amount):
    {
      "Quantity": "10",
      "AdvancedOptions": {
        "TrailingStop": {
          "Amount": "2.11"
        }
      }
    }

    Trailing Stop (Percent):
    {
      "Quantity": "10",
      "AdvancedOptions": {
        "TrailingStop": {
          "Percent": "5.0"
        }
      }
    }

    Convert to Market:
    {
      "OrderType": "Market"
    }
    """

    Quantity: Optional[str] = None
    LimitPrice: Optional[str] = None
    StopPrice: Optional[str] = None
    OrderType: Optional[Union[OrderType, str]] = None
    TimeInForce: Optional[Union[OrderReplaceTimeInForce, dict]] = None
    AdvancedOptions: Optional[Union[OrderReplaceAdvancedOptions, dict]] = None

    model_config = {"arbitrary_types_allowed": True}


class OrderConfirmationResponse(BaseModel):
    """Response from confirming an order."""

    Route: str
    Duration: str
    Account: str
    SummaryMessage: str
    EstimatedPrice: Optional[str] = None
    EstimatedPriceDisplay: Optional[str] = None
    EstimatedCommission: Optional[str] = None
    EstimatedCommissionDisplay: Optional[str] = None
    InitialMarginDisplay: Optional[str] = None
    ProductCurrency: Optional[str] = None
    AccountCurrency: Optional[str] = None

    model_config = {"arbitrary_types_allowed": True}


class GroupOrderType(str, Enum):
    """Type of group order."""

    BRK = "BRK"  # Bracket
    OCO = "OCO"  # One Cancels Other
    NORMAL = "NORMAL"  # Normal group


class GroupOrderRequest(BaseModel):
    """
    The request for placing a group trade.

    Type: The group order type. Valid values are:
    - BRK (Bracket): Bracket orders are used to exit an existing position. They are designed to
      limit loss and lock in profit by "bracketing" an order with a simultaneous stop and limit order.
    - OCO (Order Cancels Order): If one order is filled or partially-filled, all other orders
      in the group are cancelled.

    Orders: Array of orders in the group.
    For BRK orders: All orders must be for the same symbol and same side (all sell or all cover).
    For OCO orders: Orders can be for different symbols and sides.
    """

    Type: Literal["BRK", "OCO"]
    Orders: List[OrderRequest]

    model_config = {"arbitrary_types_allowed": True}


class ActivationTrigger(BaseModel):
    """
    The trigger type allows you to specify the type of tick, number, and pattern of ticks
    that will trigger a specific row of an activation rule.
    """

    Key: str = Field(
        ..., description="Value used in the `TriggerKey` property of `MarketActivationRules`"
    )
    Name: str = Field(..., description="The name of the trigger type")
    Description: str = Field(..., description="Description of how the trigger type works")

    model_config = {"arbitrary_types_allowed": True}


class ActivationTriggers(BaseModel):
    """
    Response type for the Get Activation Triggers endpoint.
    The trigger type allows you to specify the type of tick, number, and pattern of ticks
    that will trigger a specific row of an activation rule.
    """

    ActivationTriggers: List[ActivationTrigger]

    model_config = {"arbitrary_types_allowed": True}


class Route(BaseModel):
    """A route that can be specified when placing an order."""

    Id: str = Field(
        ...,
        description="The ID that must be sent in the optional Route property of a POST order request",
    )
    Name: str = Field(..., description="The name of the route")
    AssetTypes: List[str] = Field(
        ..., description="The asset types this route can be used for (STOCK, OPTION, FUTURE, etc.)"
    )

    model_config = {"arbitrary_types_allowed": True}


class Routes(BaseModel):
    """
    Response type for the Get Routes endpoint.
    Contains a list of valid routes that a client can specify when posting an order.
    """

    Routes: List[Route]

    model_config = {"arbitrary_types_allowed": True}


class GroupOrderResponseSuccess(BaseModel):
    """Successful group order response item."""

    OrderID: str
    Message: str

    model_config = {"arbitrary_types_allowed": True}


class GroupOrderResponseError(BaseModel):
    """Error group order response item."""

    OrderID: str
    Error: str
    Message: str

    model_config = {"arbitrary_types_allowed": True}


class GroupOrderResponse(BaseModel):
    """Response from placing a group order."""

    Orders: List[GroupOrderResponseSuccess]
    Errors: Optional[List[GroupOrderResponseError]] = None

    model_config = {"arbitrary_types_allowed": True}


class GroupOrderConfirmationResponse(BaseModel):
    """Response from confirming a group order."""

    Orders: List[GroupOrderResponseSuccess]
    Errors: Optional[List[GroupOrderResponseError]] = None

    model_config = {"arbitrary_types_allowed": True}


class RoutesResponse(BaseModel):
    """Response from the Routes endpoint."""

    Routes: List[Route]

    model_config = {"arbitrary_types_allowed": True}


class OSO(BaseModel):
    """One-Sends-Other (OSO) order group."""

    Type: Literal["NORMAL", "BRK", "OCO"]
    Orders: List[OrderRequest]

    model_config = {"arbitrary_types_allowed": True}
