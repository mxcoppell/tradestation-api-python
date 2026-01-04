from unittest.mock import AsyncMock, MagicMock

import pytest

from tradestation.client.http_client import HttpClient
from tradestation.services.OrderExecution.order_execution_service import OrderExecutionService
from tradestation.streaming.stream_manager import StreamManager


@pytest.fixture
def http_client_mock():
    """Create a mock HTTP client for testing"""
    mock = AsyncMock(spec=HttpClient)
    return mock


@pytest.fixture
def stream_manager_mock():
    """Create a mock stream manager for testing"""
    mock = MagicMock(spec=StreamManager)
    return mock


@pytest.fixture
def order_execution_service(http_client_mock, stream_manager_mock):
    """Create an OrderExecutionService instance with mock dependencies"""
    return OrderExecutionService(http_client_mock, stream_manager_mock)
