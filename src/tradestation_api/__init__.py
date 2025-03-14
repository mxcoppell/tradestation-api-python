"""TradeStation API Python Wrapper

A Python client library for the TradeStation API. This library provides a Pythonic interface
to interact with TradeStation's API, allowing developers to easily integrate trading applications
with TradeStation.
"""

__version__ = "0.1.0"

# Main client
from .client.tradestation_client import TradeStationClient

# Types
from .ts_types.config import ClientConfig

# Market Data Types
from .ts_types.market_data import (
    Quote,
    Bar,
    BarHistoryParams,
    OptionChain,
    OptionGreeks,
    OptionQuote,
    MarketDepthQuote,
    SymbolDetail,
)

# Order Types
from .ts_types.order_execution import (
    OrderType,
    OrderDuration,
    OrderStatus,
    OrderSide,
    OrderRequest,
    OrderResponse,
    MarketActivationRule,
    TimeActivationRule,
    AdvancedOptions,
)

# Brokerage Types
from .ts_types.brokerage import (
    Account,
    AccountType,
    TradingType,
    MarginType,
    Balance,
    BalanceDetail,
    CurrencyDetail,
    Balances,
    BalanceError,
    Positions,
    PositionResponse,
    PositionError,
    Activity,
    ActivityType,
    StreamOrderErrorResponse,
)

# Services
from .services.MarketData.market_data_service import MarketDataService
from .services.OrderExecution.order_execution_service import OrderExecutionService
from .services.Brokerage.brokerage_service import BrokerageService

__all__ = [
    # Main client
    "TradeStationClient",
    # Types
    "ClientConfig",
    # Market Data Types
    "Quote",
    "Bar",
    "BarHistoryParams",
    "OptionChain",
    "OptionGreeks",
    "OptionQuote",
    "MarketDepthQuote",
    "SymbolDetail",
    # Order Types
    "OrderType",
    "OrderDuration",
    "OrderStatus",
    "OrderSide",
    "OrderRequest",
    "OrderResponse",
    "MarketActivationRule",
    "TimeActivationRule",
    "AdvancedOptions",
    # Brokerage Types
    "Account",
    "AccountType",
    "TradingType",
    "MarginType",
    "Balance",
    "BalanceDetail",
    "CurrencyDetail",
    "Balances",
    "BalanceError",
    "Positions",
    "PositionResponse",
    "PositionError",
    "Activity",
    "ActivityType",
    "StreamOrderErrorResponse",
    # Services
    "MarketDataService",
    "OrderExecutionService",
    "BrokerageService",
]
