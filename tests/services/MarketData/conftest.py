import pytest
from unittest.mock import AsyncMock, MagicMock

from src.services.MarketData.market_data_service import MarketDataService


@pytest.fixture
def http_client_mock():
    """Create a mock HTTP client for testing."""
    mock = AsyncMock()
    return mock


@pytest.fixture
def stream_manager_mock():
    """Create a mock stream manager for testing."""
    mock = MagicMock()
    return mock


@pytest.fixture
def market_data_service(http_client_mock, stream_manager_mock):
    """Create a MarketDataService instance with mock dependencies."""
    return MarketDataService(http_client_mock, stream_manager_mock)
