"""
Test suite for the stream_orders_by_order_id method in BrokerageService.
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock
import aiohttp

from tradestation.services.Brokerage.brokerage_service import BrokerageService


@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client with mocked create_stream."""
    client = AsyncMock()
    client.create_stream = AsyncMock()
    return client


@pytest.fixture
def mock_stream_manager():  # Keep for service init
    return AsyncMock()


@pytest.fixture
def brokerage_service(mock_http_client, mock_stream_manager):
    """Fixture to create a BrokerageService with mocked dependencies."""
    return BrokerageService(mock_http_client, mock_stream_manager)


@pytest.fixture
def mock_stream_reader():
    """Create a mock StreamReader for SSE."""
    mock = AsyncMock(spec=aiohttp.StreamReader)
    # Simulate readline yielding data and then None
    mock_data = [
        json.dumps({"OrderID": "ORDER1", "Status": "Filled"}).encode("utf-8"),
        json.dumps({"Heartbeat": 1}).encode("utf-8"),
        b"",
    ]
    mock.readline.side_effect = mock_data
    return mock


@pytest.mark.asyncio
async def test_stream_orders_by_order_id_success(
    brokerage_service, mock_http_client, mock_stream_reader
):
    """Test successful streaming of orders by order ID."""
    # Arrange
    account_ids = "ACC123"
    order_ids = "ORDER1,ORDER2"
    expected_endpoint = f"/v3/brokerage/stream/accounts/{account_ids}/orders/{order_ids}"
    expected_headers = {"Accept": "application/vnd.tradestation.streams.v2+json"}
    mock_http_client.create_stream.return_value = mock_stream_reader

    # Act
    result = await brokerage_service.stream_orders_by_order_id(account_ids, order_ids)

    # Assert
    mock_http_client.create_stream.assert_called_once_with(
        expected_endpoint, params=None, headers=expected_headers
    )
    assert result == mock_stream_reader


@pytest.mark.asyncio
async def test_stream_orders_by_order_id_single_order(
    brokerage_service, mock_http_client, mock_stream_reader
):
    """Test streaming a single order by ID."""
    # Arrange
    account_ids = "ACC456"
    order_ids = "ORDER3"
    expected_endpoint = f"/v3/brokerage/stream/accounts/{account_ids}/orders/{order_ids}"
    expected_headers = {"Accept": "application/vnd.tradestation.streams.v2+json"}
    mock_http_client.create_stream.return_value = mock_stream_reader

    # Act
    result = await brokerage_service.stream_orders_by_order_id(account_ids, order_ids)

    # Assert
    mock_http_client.create_stream.assert_called_once_with(
        expected_endpoint, params=None, headers=expected_headers
    )
    assert result == mock_stream_reader


@pytest.mark.asyncio
async def test_stream_orders_by_order_id_api_error(brokerage_service, mock_http_client):
    """Test handling of API error during stream creation."""
    # Arrange
    account_ids = "ACC789"
    order_ids = "ORDER4"
    mock_http_client.create_stream.side_effect = aiohttp.ClientResponseError(
        MagicMock(), (), status=404, message="Not Found"
    )

    # Act & Assert
    with pytest.raises(aiohttp.ClientResponseError):
        await brokerage_service.stream_orders_by_order_id(account_ids, order_ids)

    # Ensure create_stream was still called
    expected_endpoint = f"/v3/brokerage/stream/accounts/{account_ids}/orders/{order_ids}"
    expected_headers = {"Accept": "application/vnd.tradestation.streams.v2+json"}
    mock_http_client.create_stream.assert_called_once_with(
        expected_endpoint, params=None, headers=expected_headers
    )
