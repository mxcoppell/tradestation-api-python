"""
Test suite for the stream_orders method in the Brokerage Service.
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp

from src.services.Brokerage.brokerage_service import BrokerageService
from src.ts_types.brokerage import Order, StreamStatus, Heartbeat, StreamOrderErrorResponse


@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client with mocked create_stream."""
    client = AsyncMock()
    client.create_stream = AsyncMock()
    return client


@pytest.fixture
def brokerage_service(mock_http_client):
    """Create a BrokerageService with mock http_client."""
    mock_stream_manager = AsyncMock()  # Keep if needed elsewhere
    return BrokerageService(mock_http_client, mock_stream_manager)


@pytest.fixture
def mock_stream_reader():
    """Create a mock StreamReader for SSE."""
    mock = AsyncMock(spec=aiohttp.StreamReader)
    # Simulate readline yielding JSON data
    mock_data = [
        json.dumps({"OrderID": "123", "Status": "Filled"}).encode("utf-8"),  # Simplified Order
        json.dumps({"Heartbeat": 1, "Timestamp": "2023-01-01T00:01:00Z"}).encode("utf-8"),
        b"",
    ]
    mock.readline.side_effect = mock_data
    return mock


class TestStreamOrders:
    """Test cases for stream_orders."""

    @pytest.mark.asyncio
    async def test_stream_with_valid_parameters(
        self, brokerage_service, mock_http_client, mock_stream_reader
    ):
        """Test streaming with valid account IDs."""
        # Arrange
        account_ids = "ACC1,ACC2"
        expected_endpoint = f"/v3/brokerage/stream/accounts/{account_ids}/orders"
        expected_headers = {"Accept": "application/vnd.tradestation.streams.v2+json"}
        mock_http_client.create_stream.return_value = mock_stream_reader

        # Act
        result = await brokerage_service.stream_orders(account_ids)

        # Assert
        mock_http_client.create_stream.assert_called_once_with(
            expected_endpoint,
            params=None,
            headers=expected_headers,
        )
        assert result == mock_stream_reader

    @pytest.mark.asyncio
    async def test_stream_too_many_account_ids(self, brokerage_service):
        """Test ValueError is raised for too many account IDs."""
        account_ids = ",".join([f"ACC{i}" for i in range(26)])  # 26 IDs
        with pytest.raises(ValueError, match="Maximum of 25 accounts allowed per request"):
            await brokerage_service.stream_orders(account_ids)

    # Remove or adapt tests that rely on WebSocketStream specific features
