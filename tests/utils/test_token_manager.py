"""Tests for the TokenManager class."""

import asyncio
import json
import time
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from tradestation.ts_types.config import AuthResponse, ClientConfig
from tradestation.utils.token_manager import TokenManager


class MockResponse:
    """Mock aiohttp.ClientResponse for testing."""

    def __init__(self, status, json_data, text=""):
        self.status = status
        self._json_data = json_data
        self._text = text

    async def json(self):
        return self._json_data

    async def text(self):
        return self._text


class MockPostContextManager:
    """Mock for session.post that supports async context manager protocol."""

    def __init__(self, response):
        self.response = response

    async def __aenter__(self):
        return self.response

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class TestTokenManager:
    """Tests for TokenManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_config = ClientConfig(
            client_id="test-client-id",
            refresh_token="test-refresh-token",
        )

    @pytest.mark.asyncio
    async def test_refresh_access_token_success(self):
        """Test refreshing token successfully."""
        # Mock response data
        mock_data = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "token_type": "bearer",
            "expires_in": 3600,
        }

        # Create token manager
        token_manager = TokenManager(self.mock_config)

        # Update tokens directly with test data
        await token_manager._test_update_from_response_data(200, mock_data)

        # Verify tokens were updated correctly
        assert token_manager.has_valid_token() is True
        assert token_manager.get_refresh_token() == "new_refresh_token"

    @pytest.mark.asyncio
    async def test_refresh_token_same_refresh_token(self):
        """Test refreshing token with same refresh token returned."""
        # Mock response data
        mock_data = {
            "access_token": "new_access_token",
            "refresh_token": "test-refresh-token",  # Same refresh token
            "token_type": "bearer",
            "expires_in": 3600,
        }

        # Create token manager
        token_manager = TokenManager(self.mock_config)

        # Update tokens directly with test data
        await token_manager._test_update_from_response_data(200, mock_data)

        # Verify tokens were updated correctly
        assert token_manager.has_valid_token() is True
        assert token_manager.get_refresh_token() == "test-refresh-token"

    @pytest.mark.asyncio
    async def test_refresh_token_no_refresh_token_returned(self):
        """Test refreshing token without new refresh token returned."""
        # Mock response data
        mock_data = {
            "access_token": "new_access_token",
            "refresh_token": "",  # Empty refresh token
            "token_type": "bearer",
            "expires_in": 3600,
        }

        # Create token manager
        token_manager = TokenManager(self.mock_config)

        # Update tokens directly with test data
        await token_manager._test_update_from_response_data(200, mock_data)

        # Verify tokens were updated correctly
        assert token_manager.has_valid_token() is True
        assert (
            token_manager.get_refresh_token() == "test-refresh-token"
        )  # Original refresh token retained

    @pytest.mark.asyncio
    async def test_refresh_fails_with_error(self):
        """Test error handling when refresh fails."""
        # Create token manager
        token_manager = TokenManager(self.mock_config)

        # Patch the refresh method to raise an exception
        with patch.object(
            token_manager, "refresh_access_token", side_effect=aiohttp.ClientError("Refresh failed")
        ):
            # Call the method and verify it raises the expected error
            with pytest.raises(aiohttp.ClientError, match="Refresh failed"):
                await token_manager.refresh_access_token()

        assert token_manager.has_valid_token() is False

    @pytest.mark.asyncio
    async def test_refresh_fails_with_api_error(self):
        """Test handling API error response during refresh."""
        # Mock API error response
        mock_data = {
            "error": "invalid_grant",
            "error_description": "Invalid refresh token",
        }
        error_text = json.dumps(mock_data)

        # Create token manager
        token_manager = TokenManager(self.mock_config)

        # Update tokens directly with test data
        with pytest.raises(
            ValueError, match=f"Token refresh failed with status code 400: {error_text}"
        ):
            await token_manager._test_update_from_response_data(400, mock_data, error_text)

        assert token_manager.has_valid_token() is False

    def test_has_valid_token_no_token(self):
        """Test hasValidToken when no token exists."""
        token_manager = TokenManager(self.mock_config)
        assert token_manager.has_valid_token() is False

    @pytest.mark.asyncio
    async def test_has_valid_token_expired(self):
        """Test hasValidToken when token is expired."""
        # Mock response with token that expires immediately
        mock_data = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "token_type": "bearer",
            "expires_in": 0,  # Expired token
        }

        # Create token manager
        token_manager = TokenManager(self.mock_config)

        # Update tokens directly with test data
        await token_manager._test_update_from_response_data(200, mock_data)

        # Wait for token to expire
        await asyncio.sleep(0.1)

        # Check if token is valid
        assert token_manager.has_valid_token() is False

    @pytest.mark.asyncio
    async def test_get_valid_access_token(self):
        """Test getValidAccessToken returns token when valid."""
        # Mock response
        mock_data = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "token_type": "bearer",
            "expires_in": 3600,
        }

        # Create token manager
        token_manager = TokenManager(self.mock_config)

        # Update tokens directly with test data
        await token_manager._test_update_from_response_data(200, mock_data)

        # Patch the refresh method to verify it's not called
        with patch.object(token_manager, "refresh_access_token") as mock_refresh:
            # Get valid access token (should not trigger refresh)
            token = await token_manager.get_valid_access_token()

            # Verify refresh wasn't called
            mock_refresh.assert_not_called()

        # Assert token is correct
        assert token == "test_access_token"

    @pytest.mark.asyncio
    async def test_get_valid_access_token_refreshes_expiring(self):
        """Test getValidAccessToken refreshes when token is about to expire."""
        # First mock response with immediately expiring token
        initial_data = {
            "access_token": "initial_access_token",
            "refresh_token": "test_refresh_token",
            "token_type": "bearer",
            "expires_in": 0,  # Expires immediately
        }

        # Create token manager
        token_manager = TokenManager(self.mock_config)

        # Update tokens directly with test data
        await token_manager._test_update_from_response_data(200, initial_data)

        # Wait for token to expire
        await asyncio.sleep(0.1)

        # Now patch the refresh_access_token method to simulate a refresh
        with patch.object(
            token_manager, "refresh_access_token", new_callable=AsyncMock
        ) as mock_refresh:
            # Set up the mock to update the token
            async def refresh_side_effect():
                token_manager._access_token = "refreshed_access_token"
                token_manager._refresh_token = "new_refresh_token"
                token_manager._token_expiry = time.time() + 3600

            mock_refresh.side_effect = refresh_side_effect

            # Get valid token (should trigger refresh)
            token = await token_manager.get_valid_access_token()

            # Verify refresh was called
            mock_refresh.assert_called_once()

            # Assert token is refreshed
            assert token == "refreshed_access_token"
            assert token_manager.get_refresh_token() == "new_refresh_token"

    @pytest.mark.asyncio
    async def test_get_valid_access_token_no_refresh_token(self):
        """Test getValidAccessToken throws error when no refresh token available."""
        # Create token manager without refresh token
        token_manager = TokenManager(
            ClientConfig(
                client_id="test-client-id",
            )
        )

        # Assert error is raised
        with pytest.raises(ValueError, match="No refresh token available"):
            await token_manager.get_valid_access_token()

    def test_constructor_env_vars(self):
        """Test constructor using environment variables."""
        with patch.dict("os.environ", {"CLIENT_ID": "env-client-id"}):
            token_manager = TokenManager()
            assert token_manager._config.client_id == "env-client-id"

    def test_constructor_missing_credentials(self):
        """Test constructor raises error when credentials are missing."""
        # Mock environment variables without credentials
        with patch.dict("os.environ", {"CLIENT_ID": ""}):
            # Test with missing client_id
            with pytest.raises(ValueError, match="Client ID is required"):
                TokenManager(
                    ClientConfig(
                        client_id=None,
                    )
                )

    def test_constructor_with_client_secret_from_config(self):
        """Test constructor with client_secret from config."""
        config = ClientConfig(
            client_id="test-client-id",
            client_secret="test-client-secret",
            refresh_token="test-refresh-token",
        )
        token_manager = TokenManager(config)
        assert token_manager._config.client_id == "test-client-id"
        assert token_manager._config.client_secret == "test-client-secret"
        assert token_manager.get_refresh_token() == "test-refresh-token"

    def test_constructor_with_client_secret_from_env(self):
        """Test constructor with CLIENT_SECRET from environment variable."""
        with patch.dict(
            "os.environ", {"CLIENT_ID": "env-client-id", "CLIENT_SECRET": "env-client-secret"}
        ):
            token_manager = TokenManager()
            assert token_manager._config.client_id == "env-client-id"
            assert token_manager._config.client_secret == "env-client-secret"

    def test_constructor_without_client_secret(self):
        """Test constructor without client_secret (backward compatibility)."""
        config = ClientConfig(
            client_id="test-client-id",
            refresh_token="test-refresh-token",
        )
        token_manager = TokenManager(config)
        assert token_manager._config.client_id == "test-client-id"
        assert token_manager._config.client_secret is None
        assert token_manager.get_refresh_token() == "test-refresh-token"

    def test_constructor_client_secret_config_overrides_env(self):
        """Test that config client_secret takes precedence over environment variable."""
        with patch.dict(
            "os.environ", {"CLIENT_ID": "env-client-id", "CLIENT_SECRET": "env-client-secret"}
        ):
            config = ClientConfig(
                client_id="config-client-id",
                client_secret="config-client-secret",
                refresh_token="test-refresh-token",
            )
            token_manager = TokenManager(config)
            assert token_manager._config.client_id == "config-client-id"
            assert token_manager._config.client_secret == "config-client-secret"

    @pytest.mark.asyncio
    async def test_refresh_includes_client_secret_when_provided(self):
        """Test that refresh_access_token includes client_secret in request when provided."""
        config = ClientConfig(
            client_id="test-client-id",
            client_secret="test-client-secret",
            refresh_token="test-refresh-token",
        )
        token_manager = TokenManager(config)

        # Mock response data
        mock_data = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "token_type": "bearer",
            "expires_in": 3600,
        }

        # Mock the session post
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = mock_session_class.return_value.__aenter__.return_value
            mock_response = MockResponse(200, mock_data)
            # Create a mock that returns the MockPostContextManager when called
            mock_post = MagicMock(return_value=MockPostContextManager(mock_response))
            mock_session.post = mock_post

            await token_manager.refresh_access_token()

            # Verify that post was called with client_secret in data
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            data = call_args[1]["data"]

            assert data["grant_type"] == "refresh_token"
            assert data["client_id"] == "test-client-id"
            assert data["client_secret"] == "test-client-secret"
            assert data["refresh_token"] == "test-refresh-token"

    @pytest.mark.asyncio
    async def test_refresh_excludes_client_secret_when_not_provided(self):
        """Test that refresh_access_token does NOT include client_secret when not provided."""
        config = ClientConfig(
            client_id="test-client-id",
            refresh_token="test-refresh-token",
        )
        token_manager = TokenManager(config)

        # Mock response data
        mock_data = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "token_type": "bearer",
            "expires_in": 3600,
        }

        # Mock the session post
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = mock_session_class.return_value.__aenter__.return_value
            mock_response = MockResponse(200, mock_data)
            # Create a mock that returns the MockPostContextManager when called
            mock_post = MagicMock(return_value=MockPostContextManager(mock_response))
            mock_session.post = mock_post

            await token_manager.refresh_access_token()

            # Verify that post was called without client_secret in data
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            data = call_args[1]["data"]

            assert data["grant_type"] == "refresh_token"
            assert data["client_id"] == "test-client-id"
            assert "client_secret" not in data
            assert data["refresh_token"] == "test-refresh-token"
