import pathlib
import sys
from unittest.mock import AsyncMock, MagicMock

import pytest

# Add project root to the Python path to allow 'from tradestation.' imports
project_root = (
    pathlib.Path(__file__).resolve().parents[3]
)  # tests/services/MarketData -> tests/services -> tests -> root
sys.path.insert(0, str(project_root))

from tradestation.client.http_client import HttpClient
from tradestation.services.MarketData.market_data_service import MarketDataService
from tradestation.streaming.stream_manager import StreamManager


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
