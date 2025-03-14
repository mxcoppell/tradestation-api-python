"""
HttpClient module for handling HTTP requests to the TradeStation API.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Union

import aiohttp
from aiohttp import ClientResponse, ClientSession, ClientError, ClientTimeout

from src.ts_types.config import ClientConfig
from src.utils.rate_limiter import RateLimiter
from src.utils.token_manager import TokenManager


class HttpClient:
    """
    HTTP client for making requests to the TradeStation API.
    Handles authentication, rate limiting, and response processing.
    """

    def __init__(self, config: Union[Dict[str, Any], "ClientConfig"] = None):
        """
        Initialize the HttpClient with the specified configuration.

        Args:
            config: Configuration settings for the client (dict or ClientConfig object)
        """
        from src.ts_types.config import ClientConfig

        # Convert config to ClientConfig if it's a dict
        if config is not None and not isinstance(config, ClientConfig):
            config = ClientConfig(**config)

        self.token_manager = TokenManager(config)
        self.rate_limiter = RateLimiter()
        self._session: Optional[ClientSession] = None

        # Determine base URL based on environment
        if config and config.environment and config.environment.lower() == "simulation":
            self.base_url = "https://sim.api.tradestation.com"
            print(f"Using Simulation environment (base URL: {self.base_url})")
        else:
            self.base_url = "https://api.tradestation.com"
            print(f"Using Live environment (base URL: {self.base_url})")

    async def _ensure_session(self) -> ClientSession:
        """
        Ensure a session exists and create one if it doesn't.

        Returns:
            Active client session
        """
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(headers={"Content-Type": "application/json"})
        return self._session

    async def _prepare_request(self, url: str) -> Dict[str, str]:
        """
        Prepare request headers with authentication token.

        Args:
            url: The endpoint URL for rate limiting

        Returns:
            Headers dictionary with authentication
        """
        # Wait for rate limiting slot
        await self.rate_limiter.wait_for_slot(url)

        # Get valid token (will refresh if needed)
        token = await self.token_manager.get_valid_access_token()

        return {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    async def _process_response(self, response: ClientResponse, url: str) -> None:
        """
        Process response headers for rate limiting information.

        Args:
            response: The response from the API
            url: The endpoint URL
        """
        self.rate_limiter.update_limits(url, dict(response.headers))

    def get_refresh_token(self) -> Optional[str]:
        """
        Gets the current refresh token.

        Returns:
            The current refresh token or None if none is available
        """
        return self.token_manager.get_refresh_token()

    async def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a GET request to the specified endpoint.

        Args:
            url: The endpoint URL
            params: Query parameters

        Returns:
            Response data as dictionary
        """
        session = await self._ensure_session()
        headers = await self._prepare_request(url)

        full_url = f"{self.base_url}{url}"

        # Debug print
        print(f"Making GET request to: {full_url}")
        print(f"Headers: {headers}")

        try:
            async with session.get(full_url, params=params, headers=headers) as response:
                if response is None:
                    raise ValueError("Response object is None")

                # Debug print
                print(f"Response status: {response.status}")

                # Process response headers for rate limiting
                await self._process_response(response, url)

                # Handle HTTP errors
                if response.status >= 400:
                    error_text = await response.text()
                    print(f"Error response: {error_text}")
                    response.raise_for_status()  # This will raise an appropriate HTTPError

                # Get JSON response
                return await response.json()
        except Exception as e:
            print(f"Request error: {str(e)}")
            raise

    async def post(
        self, url: str, data: Any = None, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a POST request to the specified endpoint.

        Args:
            url: The endpoint URL
            data: Request body data
            params: Query parameters

        Returns:
            Response data as dictionary
        """
        session = await self._ensure_session()
        headers = await self._prepare_request(url)

        full_url = f"{self.base_url}{url}"
        async with session.post(full_url, json=data, params=params, headers=headers) as response:
            await self._process_response(response, url)
            await response.raise_for_status()
            return await response.json()

    async def put(
        self, url: str, data: Any = None, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a PUT request to the specified endpoint.

        Args:
            url: The endpoint URL
            data: Request body data
            params: Query parameters

        Returns:
            Response data as dictionary
        """
        session = await self._ensure_session()
        headers = await self._prepare_request(url)

        full_url = f"{self.base_url}{url}"
        async with session.put(full_url, json=data, params=params, headers=headers) as response:
            await self._process_response(response, url)
            await response.raise_for_status()
            return await response.json()

    async def delete(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a DELETE request to the specified endpoint.

        Args:
            url: The endpoint URL
            params: Query parameters

        Returns:
            Response data as dictionary
        """
        session = await self._ensure_session()
        headers = await self._prepare_request(url)

        full_url = f"{self.base_url}{url}"
        async with session.delete(full_url, params=params, headers=headers) as response:
            await self._process_response(response, url)
            await response.raise_for_status()
            return await response.json()

    async def create_stream(
        self, url: str, params: Optional[Dict[str, Any]] = None
    ) -> aiohttp.StreamReader:
        """
        Create a stream for streaming endpoints.

        Args:
            url: The endpoint URL
            params: Query parameters

        Returns:
            Stream reader for reading the stream data
        """
        session = await self._ensure_session()
        headers = await self._prepare_request(url)

        full_url = f"{self.base_url}{url}"
        response = await session.get(
            full_url,
            params=params,
            headers=headers,
            timeout=None,  # Streaming connections need no timeout
        )

        await self._process_response(response, url)
        await response.raise_for_status()

        return response.content

    async def close(self) -> None:
        """
        Close the HTTP client and clean up resources.
        """
        if self._session:
            await self._session.close()
            self._session = None
            print("HTTP client session closed")
