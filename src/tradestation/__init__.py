"""TradeStation API Python Wrapper

A comprehensive Python wrapper for TradeStation WebAPI v3, providing type-safe access
to TradeStation's brokerage, order execution, and market data services.
"""

from .client import HttpClient, TradeStationClient
from .services import BrokerageService, MarketDataService, OrderExecutionService
from .utils.exceptions import (
    TradeStationAPIError,
    TradeStationAuthError,
    TradeStationNetworkError,
    TradeStationRateLimitError,
    TradeStationResourceNotFoundError,
    TradeStationServerError,
    TradeStationStreamError,
    TradeStationTimeoutError,
    TradeStationValidationError,
)

__version__ = "1.2.0"
__all__ = [
    "TradeStationClient",
    "HttpClient",
    "MarketDataService",
    "BrokerageService",
    "OrderExecutionService",
    # Exception classes
    "TradeStationAPIError",
    "TradeStationAuthError",
    "TradeStationRateLimitError",
    "TradeStationResourceNotFoundError",
    "TradeStationValidationError",
    "TradeStationNetworkError",
    "TradeStationServerError",
    "TradeStationTimeoutError",
    "TradeStationStreamError",
]
