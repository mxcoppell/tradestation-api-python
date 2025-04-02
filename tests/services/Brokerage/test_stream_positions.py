import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.client.http_client import HttpClient
from src.services.Brokerage.brokerage_service import BrokerageService
from src.streaming.stream_manager import StreamManager
from src.utils.stream_manager import WebSocketStream


@pytest.fixture
def http_client_mock():
    """Create a mock HTTP client for testing"""
    mock = AsyncMock(spec=HttpClient)
    return mock


@pytest.fixture
def stream_manager_mock():
    """Create a mock StreamManager for testing"""
    mock = MagicMock(spec=StreamManager)
    # Configure the create_stream method to return an AsyncMock WebSocketStream
    mock.create_stream = AsyncMock()
    return mock


@pytest.fixture
def mock_stream():
    """Create a mock WebSocketStream for testing"""
    mock = MagicMock(spec=WebSocketStream)
    return mock


@pytest.fixture
def brokerage_service(http_client_mock, stream_manager_mock):
    """Create a BrokerageService instance with mock dependencies"""
    return BrokerageService(http_client_mock, stream_manager_mock)


class TestStreamPositions:
    """Tests for the stream_positions method in BrokerageService"""

    @pytest.mark.asyncio
    async def test_stream_positions_for_single_account(
        self, brokerage_service, stream_manager_mock, mock_stream
    ):
        """Test streaming positions for a single account"""
        # Configure the mock stream manager to return our mock stream
        stream_manager_mock.create_stream.return_value = mock_stream

        # Call the method
        result = await brokerage_service.stream_positions("123456")

        # Verify the stream manager was called correctly
        stream_manager_mock.create_stream.assert_called_once_with(
            "/v3/brokerage/stream/accounts/123456/positions",
            {},
            {"headers": {"Accept": "application/vnd.tradestation.streams.v3+json"}},
        )

        # Verify the result is the mock stream
        assert result == mock_stream

    @pytest.mark.asyncio
    async def test_stream_positions_for_multiple_accounts(
        self, brokerage_service, stream_manager_mock, mock_stream
    ):
        """Test streaming positions for multiple accounts"""
        # Configure the mock stream manager to return our mock stream
        stream_manager_mock.create_stream.return_value = mock_stream

        # Call the method with multiple accounts
        result = await brokerage_service.stream_positions("123456,789012")

        # Verify the stream manager was called correctly with multiple accounts
        stream_manager_mock.create_stream.assert_called_once_with(
            "/v3/brokerage/stream/accounts/123456,789012/positions",
            {},
            {"headers": {"Accept": "application/vnd.tradestation.streams.v3+json"}},
        )

        # Verify the result is the mock stream
        assert result == mock_stream

    @pytest.mark.asyncio
    async def test_stream_positions_with_changes_parameter(
        self, brokerage_service, stream_manager_mock, mock_stream
    ):
        """Test streaming positions with changes parameter set to True"""
        # Configure the mock stream manager to return our mock stream
        stream_manager_mock.create_stream.return_value = mock_stream

        # Call the method with changes=True
        result = await brokerage_service.stream_positions("123456", True)

        # Verify the stream manager was called correctly with changes parameter
        stream_manager_mock.create_stream.assert_called_once_with(
            "/v3/brokerage/stream/accounts/123456/positions",
            {"changes": True},
            {"headers": {"Accept": "application/vnd.tradestation.streams.v3+json"}},
        )

        # Verify the result is the mock stream
        assert result == mock_stream

    @pytest.mark.asyncio
    async def test_stream_positions_with_changes_parameter_false(
        self, brokerage_service, stream_manager_mock, mock_stream
    ):
        """Test streaming positions with changes parameter set to False"""
        # Configure the mock stream manager to return our mock stream
        stream_manager_mock.create_stream.return_value = mock_stream

        # Call the method with changes=False
        result = await brokerage_service.stream_positions("123456", False)

        # Verify the stream manager was called correctly with changes parameter false
        # Note: We don't include changes=False in the parameters since it's the default
        stream_manager_mock.create_stream.assert_called_once_with(
            "/v3/brokerage/stream/accounts/123456/positions",
            {},
            {"headers": {"Accept": "application/vnd.tradestation.streams.v3+json"}},
        )

        # Verify the result is the mock stream
        assert result == mock_stream

    @pytest.mark.asyncio
    async def test_stream_positions_with_too_many_accounts(self, brokerage_service):
        """Test that an error is raised when too many accounts are specified"""
        # Create a string with 26 comma-separated account IDs (exceeding the limit of 25)
        too_many_accounts = ",".join([f"ACC{i}" for i in range(1, 27)])

        # Verify that a ValueError is raised
        with pytest.raises(ValueError, match="Maximum of 25 accounts allowed per request"):
            await brokerage_service.stream_positions(too_many_accounts)

    @pytest.mark.asyncio
    async def test_stream_positions_streaming_error(self, brokerage_service, stream_manager_mock):
        """Test handling of streaming errors"""
        # Configure the mock stream manager to raise an exception
        stream_manager_mock.create_stream.side_effect = ConnectionError(
            "Failed to establish streaming connection"
        )

        # Verify that the error is propagated
        with pytest.raises(ConnectionError, match="Failed to establish streaming connection"):
            await brokerage_service.stream_positions("123456")
