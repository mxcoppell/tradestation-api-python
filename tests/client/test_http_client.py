"""
Tests for the HttpClient class.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
from aiohttp import ClientResponse, StreamReader

from tradestation.client.http_client import HttpClient
from tradestation.ts_types.config import ClientConfig
from tradestation.utils.rate_limiter import RateLimiter
from tradestation.utils.token_manager import TokenManager


@pytest.fixture
def mock_token_manager():
    """Fixture for a mock TokenManager."""
    token_manager = MagicMock(spec=TokenManager)
    token_manager.get_valid_access_token = AsyncMock(return_value="test-token")
    token_manager.get_refresh_token = MagicMock(return_value="test-refresh-token")
    return token_manager


@pytest.fixture
def mock_rate_limiter():
    """Fixture for a mock RateLimiter."""
    rate_limiter = MagicMock(spec=RateLimiter)
    rate_limiter.wait_for_slot = AsyncMock()
    rate_limiter.update_limits = MagicMock()
    return rate_limiter


@pytest.fixture
def mock_response():
    """Fixture for a mock aiohttp response."""
    response = AsyncMock(spec=ClientResponse)
    response.status = 200
    response.headers = {"X-RateLimit-Remaining": "100"}
    response.json = AsyncMock(return_value={"data": "test"})
    response.raise_for_status = AsyncMock()
    return response


@pytest.fixture
def mock_stream_response():
    """Fixture for a mock aiohttp streaming response."""
    response = AsyncMock(spec=ClientResponse)
    response.status = 200
    response.headers = {"X-RateLimit-Remaining": "100"}
    response.content = AsyncMock(spec=StreamReader)
    response.raise_for_status = MagicMock()
    return response


@pytest.fixture
def mock_client_session():
    """Fixture for a mock aiohttp ClientSession."""
    session = AsyncMock(spec=aiohttp.ClientSession)
    return session


class TestHttpClient:
    """Test cases for the HttpClient class."""

    @pytest.fixture(autouse=True)
    def setup(self, mock_token_manager, mock_rate_limiter, monkeypatch):
        """Setup test environment before each test."""
        # Patch the TokenManager and RateLimiter classes
        monkeypatch.setattr(
            "tradestation.client.http_client.TokenManager", MagicMock(return_value=mock_token_manager)
        )
        monkeypatch.setattr(
            "tradestation.client.http_client.RateLimiter", MagicMock(return_value=mock_rate_limiter)
        )

        # Store references to the mocks
        self.token_manager = mock_token_manager
        self.rate_limiter = mock_rate_limiter

    @pytest.mark.parametrize(
        "environment,expected_base_url",
        [
            ("Simulation", "https://sim.api.tradestation.com"),
            ("Live", "https://api.tradestation.com"),
            (None, "https://api.tradestation.com"),
        ],
    )
    def test_init_sets_correct_base_url(self, environment, expected_base_url):
        """Test that constructor sets the correct base URL based on environment."""
        config = None
        if environment:
            config = ClientConfig(environment=environment)

        client = HttpClient(config)
        assert client.base_url == expected_base_url

    @pytest.mark.asyncio
    async def test_ensure_session_creates_new_session_if_none_exists(self):
        """Test _ensure_session creates a new session if none exists."""
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session

            client = HttpClient()
            result = await client._ensure_session()

            assert result == mock_session
            mock_session_class.assert_called_once()

    @pytest.mark.asyncio
    async def test_ensure_session_reuses_existing_session(self, mock_client_session):
        """Test _ensure_session reuses an existing session."""
        client = HttpClient()
        client._session = mock_client_session
        mock_client_session.closed = False

        result = await client._ensure_session()

        assert result == mock_client_session

    @pytest.mark.asyncio
    async def test_prepare_request_gets_token_and_waits_for_slot(self):
        """Test _prepare_request gets token and waits for rate limit slot."""
        client = HttpClient()
        headers = await client._prepare_request("/test")

        self.rate_limiter.wait_for_slot.assert_called_once_with("/test")
        self.token_manager.get_valid_access_token.assert_called_once()
        assert headers == {
            "Content-Type": "application/json",
            "Authorization": "Bearer test-token",
        }

    @pytest.mark.asyncio
    async def test_process_response_updates_rate_limits(self, mock_response):
        """Test _process_response updates rate limits with response headers."""
        client = HttpClient()
        await client._process_response(mock_response, "/test")

        self.rate_limiter.update_limits.assert_called_once_with(
            "/test", dict(mock_response.headers)
        )

    def test_get_refresh_token_returns_token_from_manager(self):
        """Test get_refresh_token returns the token from TokenManager."""
        client = HttpClient()
        result = client.get_refresh_token()

        self.token_manager.get_refresh_token.assert_called_once()
        assert result == "test-refresh-token"

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "method,method_name",
        [
            ("get", "get"),
            ("post", "post"),
            ("put", "put"),
            ("delete", "delete"),
        ],
    )
    async def test_http_methods(self, method, method_name, mock_client_session, mock_response):
        """Test HTTP methods make the correct requests and process responses."""
        # Setup
        client = HttpClient()
        client._ensure_session = AsyncMock(return_value=mock_client_session)
        client._prepare_request = AsyncMock(return_value={"Authorization": "Bearer test-token"})
        client._process_response = AsyncMock()

        # Set response status to 200 so raise_for_status is not called
        mock_response.status = 200

        session_method = getattr(mock_client_session, method_name)
        session_method.return_value.__aenter__.return_value = mock_response

        # Execute the method being tested
        http_method = getattr(client, method)
        if method in ["post", "put"]:
            result = await http_method("/test", data={"key": "value"})
        else:
            result = await http_method("/test")

        # Assertions for setup and method call
        client._ensure_session.assert_called_once()
        client._prepare_request.assert_called_once_with("/test")

        # Assertions for the correct session method
        if method in ["post", "put"]:
            session_method.assert_called_once()
            # Extract the call arguments (will be different based on the method)
            call_args = session_method.call_args[1]
            assert "json" in call_args
            assert call_args["json"] == {"key": "value"}
        else:
            session_method.assert_called_once()

        # Common assertions for all methods
        client._process_response.assert_called_once_with(mock_response, "/test")
        # Since status is 200, raise_for_status should not be called
        mock_response.raise_for_status.assert_not_awaited()
        mock_response.json.assert_awaited_once()
        assert result == {"data": "test"}

    @pytest.mark.asyncio
    async def test_create_stream(self, mock_stream_response):
        """Test create_stream creates and returns a stream."""
        # Setup
        client = HttpClient()

        # Create a specific mock session for this test
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_stream_response)

        # Set up the mocks
        client._ensure_session = AsyncMock(return_value=mock_session)
        client._prepare_request = AsyncMock(return_value={"Authorization": "Bearer test-token"})
        client._process_response = AsyncMock()

        # Execute
        result = await client.create_stream("/test")

        # Assertions
        client._ensure_session.assert_awaited_once()
        client._prepare_request.assert_awaited_once_with("/test")
        mock_session.get.assert_awaited_once_with(
            "https://api.tradestation.com/test",
            params=None,
            headers={"Authorization": "Bearer test-token"},
            timeout=None,
        )
        client._process_response.assert_awaited_once_with(mock_stream_response, "/test")
        mock_stream_response.raise_for_status.assert_called_once()
        assert result == mock_stream_response.content

    @pytest.mark.asyncio
    async def test_close(self, mock_client_session):
        """Test close closes the session if it exists and is open."""
        client = HttpClient()
        client._session = mock_client_session
        mock_client_session.closed = False

        await client.close()

        mock_client_session.close.assert_awaited_once()
