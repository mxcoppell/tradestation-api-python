import pytest
from unittest.mock import AsyncMock, MagicMock

from src.services.Brokerage.brokerage_service import BrokerageService
from src.streaming.stream_manager import StreamManager
from src.client.http_client import HttpClient
from src.utils.stream_manager import WebSocketStream


@pytest.fixture
def mock_brokerage_service():
    """Fixture to create a BrokerageService with mocked dependencies."""
    mock_http_client = AsyncMock(spec=HttpClient)
    mock_stream_manager = AsyncMock(spec=StreamManager)
    # Mock the create_stream method to return an AsyncMock that can be awaited
    mock_stream_manager.create_stream = AsyncMock(return_value=AsyncMock(spec=WebSocketStream))
    service = BrokerageService(mock_http_client, mock_stream_manager)
    return service, mock_stream_manager


@pytest.mark.asyncio
async def test_stream_orders_by_order_id_success(mock_brokerage_service):
    """Test successful call to stream_orders_by_order_id."""
    # Arrange
    brokerage_service, mock_stream_manager = mock_brokerage_service
    account_ids = "123456,789012"
    order_ids = "ORDER1,ORDER2"

    # Act
    stream = await brokerage_service.stream_orders_by_order_id(account_ids, order_ids)

    # Assert
    mock_stream_manager.create_stream.assert_called_once_with(
        f"/v3/brokerage/stream/accounts/{account_ids}/orders/{order_ids}",
        {},
        {"headers": {"Accept": "application/vnd.tradestation.streams.v3+json"}},
    )
    assert isinstance(stream, AsyncMock)  # Check if it returned the mocked stream object


@pytest.mark.asyncio
async def test_stream_orders_by_order_id_max_accounts_exceeded(mock_brokerage_service):
    """Test ValueError when max account IDs are exceeded."""
    # Arrange
    brokerage_service, _ = mock_brokerage_service
    account_ids = ",".join([f"ACC{i}" for i in range(26)])  # 26 account IDs
    order_ids = "ORDER1"

    # Act & Assert
    with pytest.raises(ValueError, match=r"Maximum number of account IDs \(25\) exceeded."):
        await brokerage_service.stream_orders_by_order_id(account_ids, order_ids)


@pytest.mark.asyncio
async def test_stream_orders_by_order_id_max_orders_exceeded(mock_brokerage_service):
    """Test ValueError when max order IDs are exceeded."""
    # Arrange
    brokerage_service, _ = mock_brokerage_service
    account_ids = "123456"
    order_ids = ",".join([f"ORD{i}" for i in range(51)])  # 51 order IDs

    # Act & Assert
    with pytest.raises(ValueError, match=r"Maximum number of order IDs \(50\) exceeded."):
        await brokerage_service.stream_orders_by_order_id(account_ids, order_ids)


@pytest.mark.asyncio
async def test_stream_orders_by_order_id_single_ids(mock_brokerage_service):
    """Test successful call with single account and order ID."""
    # Arrange
    brokerage_service, mock_stream_manager = mock_brokerage_service
    account_ids = "987654"
    order_ids = "SINGLEORDER"

    # Act
    stream = await brokerage_service.stream_orders_by_order_id(account_ids, order_ids)

    # Assert
    mock_stream_manager.create_stream.assert_called_once_with(
        f"/v3/brokerage/stream/accounts/{account_ids}/orders/{order_ids}",
        {},
        {"headers": {"Accept": "application/vnd.tradestation.streams.v3+json"}},
    )
    assert isinstance(stream, AsyncMock)
