"""
Test suite for the stream_positions method in the Brokerage Service.
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp

from src.services.Brokerage.brokerage_service import BrokerageService
from src.ts_types.brokerage import PositionResponse, StreamStatus, PositionError
from src.ts_types.market_data import Heartbeat


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
        json.dumps({"Symbol": "AAPL", "Quantity": 100}).encode("utf-8"),  # Simplified Position
        json.dumps({"Heartbeat": 1, "Timestamp": "2023-01-01T00:01:00Z"}).encode("utf-8"),
        b"",
    ]
    mock.readline.side_effect = mock_data
    return mock


class TestStreamPositions:
    """Test cases for stream_positions."""

    @pytest.mark.asyncio
    async def test_stream_with_default_parameters(
        self, brokerage_service, mock_http_client, mock_stream_reader
    ):
        """Test streaming positions with default changes=False."""
        # Arrange
        account_ids = "ACC1"
        expected_endpoint = f"/v3/brokerage/stream/accounts/{account_ids}/positions"
        expected_params = {"changes": "false"}  # Default
        expected_headers = {"Accept": "application/vnd.tradestation.streams.v2+json"}
        mock_http_client.create_stream.return_value = mock_stream_reader

        # Act
        result = await brokerage_service.stream_positions(account_ids)

        # Assert
        mock_http_client.create_stream.assert_called_once_with(
            expected_endpoint,
            params=expected_params,
            headers=expected_headers,
        )
        assert result == mock_stream_reader

    @pytest.mark.asyncio
    async def test_stream_with_changes_true(
        self, brokerage_service, mock_http_client, mock_stream_reader
    ):
        """Test streaming positions with changes=True."""
        # Arrange
        account_ids = "ACC2,ACC3"
        expected_endpoint = f"/v3/brokerage/stream/accounts/{account_ids}/positions"
        expected_params = {"changes": "true"}
        expected_headers = {"Accept": "application/vnd.tradestation.streams.v2+json"}
        mock_http_client.create_stream.return_value = mock_stream_reader

        # Act
        result = await brokerage_service.stream_positions(account_ids, changes=True)

        # Assert
        mock_http_client.create_stream.assert_called_once_with(
            expected_endpoint,
            params=expected_params,
            headers=expected_headers,
        )
        assert result == mock_stream_reader

    @pytest.mark.asyncio
    async def test_stream_too_many_account_ids(self, brokerage_service):
        """Test ValueError is raised for too many account IDs."""
        account_ids = ",".join([f"ACC{i}" for i in range(26)])  # 26 IDs
        with pytest.raises(ValueError, match="Maximum of 25 accounts allowed per request"):
            await brokerage_service.stream_positions(account_ids)

    # Remove or adapt tests that rely on WebSocketStream specific features
