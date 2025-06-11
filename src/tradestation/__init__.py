"""TradeStation API Python Wrapper

A comprehensive Python wrapper for TradeStation WebAPI v3, providing type-safe access
to TradeStation's brokerage, order execution, and market data services.
"""

from .client import TradeStationClient, HttpClient
from .services import MarketDataService, BrokerageService, OrderExecutionService
from .utils.exceptions import (
    TradeStationAPIError,
    TradeStationAuthError,
    TradeStationRateLimitError,
    TradeStationResourceNotFoundError,
    TradeStationValidationError,
    TradeStationNetworkError,
    TradeStationServerError,
    TradeStationTimeoutError,
    TradeStationStreamError,
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