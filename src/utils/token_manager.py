"""Token management utilities for the TradeStation API."""

import asyncio
import os
import time
from typing import Any, Dict, Optional, TypedDict, cast

import aiohttp
from pydantic import ValidationError

from ts_types.config import ApiError, AuthResponse, ClientConfig


class TokenManager:
    """
    Manages authentication tokens for the TradeStation API.
    Handles token refresh, validation, and storage.
    """

    # 5 minutes in seconds
    _REFRESH_THRESHOLD = 5 * 60
    # Token endpoint
    _TOKEN_URL = "https://signin.tradestation.com/oauth/token"

    def __init__(self, config: Optional[ClientConfig] = None) -> None:
        """
        Initialize the TokenManager with client credentials.

        Args:
            config: Optional configuration with client ID, secret, and refresh token.
                   If not provided, values are read from environment variables.

        Raises:
            ValueError: If client ID and client secret are not provided and not in environment.
        """
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._token_expiry: Optional[float] = None
        self._refreshing: Optional[asyncio.Lock] = asyncio.Lock()

        # Get credentials from config or environment
        client_id = config.client_id if config else None
        client_secret = config.client_secret if config else None

        if not client_id:
            client_id = os.environ.get("CLIENT_ID")
        if not client_secret:
            client_secret = os.environ.get("CLIENT_SECRET")

        if not client_id or not client_secret:
            raise ValueError("Client ID and Client Secret are required")

        # Store configuration
        self._config = ClientConfig(
            client_id=client_id,
            client_secret=client_secret,
            max_concurrent_streams=config.max_concurrent_streams if config else None,
            environment=config.environment if config else None,
        )

        # Set initial refresh token if provided in config
        if config and config.refresh_token:
            self._refresh_token = config.refresh_token

    def _should_refresh_token(self) -> bool:
        """
        Determine if the token should be refreshed based on expiry time.

        Returns:
            True if token is expired or about to expire, False otherwise.
        """
        if not self._token_expiry:
            return True
        # Refresh if less than REFRESH_THRESHOLD seconds remaining
        return time.time() >= (self._token_expiry - self._REFRESH_THRESHOLD)

    async def get_valid_access_token(self) -> str:
        """
        Gets a valid access token, refreshing it if necessary.
        This is the main method that should be used to get an access token.

        Returns:
            A valid access token

        Raises:
            ValueError: If unable to get a valid token
        """
        if self._should_refresh_token():
            if self._refresh_token:
                await self.refresh_access_token()
            else:
                raise ValueError(
                    "No refresh token available. You must provide a refresh token in the client configuration."
                )

        return self._get_access_token()

    async def refresh_access_token(self) -> None:
        """
        Refreshes the access token using the refresh token.
        If the response includes a new refresh token, it will be stored for future use.

        Raises:
            ValueError: If refresh fails or no refresh token is available
        """
        if not self._refresh_token:
            raise ValueError("No refresh token available")

        # If already refreshing, wait for that to complete
        async with self._refreshing:
            refresh_token = self._refresh_token  # Capture current refresh token

            data = {
                "grant_type": "refresh_token",
                "client_id": self._config.client_id,
                "client_secret": self._config.client_secret,
                "refresh_token": refresh_token,
            }

            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self._TOKEN_URL, data=data, headers=headers
                    ) as response:
                        await self._process_token_response(response)
            except aiohttp.ClientError as e:
                raise ValueError(f"Token refresh request failed: {str(e)}")

    async def _process_token_response(self, response: aiohttp.ClientResponse) -> None:
        """
        Process the token response from the API.
        Extracted to a separate method to make testing easier.

        Args:
            response: The response from the token endpoint

        Raises:
            ValueError: If the response indicates an error
        """
        if response.status == 200:
            try:
                # Parse the response JSON
                response_data = await response.json()
                auth_response = AuthResponse.model_validate(response_data)
                self._update_tokens(auth_response)
            except ValidationError as e:
                raise ValueError(f"Invalid auth response format: {e}")
        else:
            try:
                # Parse error response
                error_data = await response.json()
                api_error = ApiError.model_validate(error_data)
                error_msg = api_error.error_description or api_error.error
                raise ValueError(f"Token refresh failed: {error_msg}")
            except (ValueError, ValidationError):
                # If we can't parse the error, use the status code
                error_text = await response.text()
                raise ValueError(
                    f"Token refresh failed with status code {response.status}: {error_text}"
                )

    def _update_tokens(self, auth_response: AuthResponse) -> None:
        """
        Update the tokens based on the authentication response.

        Args:
            auth_response: Authentication response containing new tokens
        """
        self._access_token = auth_response.access_token

        # Update refresh token only if a new one is provided
        if auth_response.refresh_token:
            self._refresh_token = auth_response.refresh_token

        self._token_expiry = time.time() + auth_response.expires_in

    def get_refresh_token(self) -> Optional[str]:
        """
        Returns the current refresh token.

        Returns:
            The current refresh token or None if none is available
        """
        return self._refresh_token

    def _get_access_token(self) -> str:
        """
        Returns the current access token.

        Returns:
            The current access token

        Raises:
            ValueError: If no access token is available
        """
        if not self._access_token:
            raise ValueError("No access token available")
        return self._access_token

    def is_token_expired(self) -> bool:
        """
        Check if the current token is expired.

        Returns:
            True if the token is expired or doesn't exist, False otherwise
        """
        return bool(self._token_expiry is None or time.time() >= self._token_expiry)

    def has_valid_token(self) -> bool:
        """
        Check if there is a valid (not expired) access token.

        Returns:
            True if there is a valid access token, False otherwise
        """
        return bool(self._access_token and not self.is_token_expired())

    # For testing purposes only
    async def _test_update_from_response_data(
        self, status: int, data: Dict[str, Any], error_text: str = ""
    ) -> None:
        """
        Update tokens directly from response data for testing.
        This method should only be used in tests.

        Args:
            status: HTTP status code
            data: Response data
            error_text: Error text for non-200 responses

        Raises:
            ValueError: If the response indicates an error
        """

        class MockResponse:
            def __init__(self, status: int, data: Dict[str, Any], error_text: str):
                self.status = status
                self._data = data
                self._error_text = error_text

            async def json(self):
                return self._data

            async def text(self):
                return self._error_text

        await self._process_token_response(MockResponse(status, data, error_text))
