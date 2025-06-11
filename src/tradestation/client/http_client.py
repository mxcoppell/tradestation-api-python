"""
HttpClient module for handling HTTP requests to the TradeStation API.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union

import aiohttp
from aiohttp import ClientResponse, ClientSession

from ..ts_types.config import ClientConfig
from ..utils.rate_limiter import RateLimiter
from ..utils.token_manager import TokenManager
from ..utils.exceptions import (
    TradeStationAPIError,
    TradeStationAuthError,
    TradeStationNetworkError,
    TradeStationRateLimitError,
    TradeStationResourceNotFoundError,
    TradeStationServerError,
    TradeStationTimeoutError,
    TradeStationValidationError,
    map_http_error,
    handle_request_exception,
)


class HttpClient:
    """
    HTTP client for making requests to the TradeStation API.
    Handles authentication, rate limiting, and response processing.
    """

    def __init__(self, config: Union[Dict[str, Any], "ClientConfig"] = None, debug: bool = False):
        """
        Initialize the HttpClient with the specified configuration.

        Args:
            config: Configuration settings for the client (dict or ClientConfig object)
            debug: Whether to print debug messages
        """
        from ..ts_types.config import ClientConfig

        self.debug = debug

        # Convert config to ClientConfig if it's a dict
        if config is not None and not isinstance(config, ClientConfig):
            config = ClientConfig(**config)

        self.token_manager = TokenManager(config)
        self.rate_limiter = RateLimiter()
        self._session: Optional[ClientSession] = None

        # Determine base URL based on environment
        if config and config.environment and config.environment.lower() == "simulation":
            self.base_url = "https://sim.api.tradestation.com"
            if self.debug:
                print(f"Using Simulation environment (base URL: {self.base_url})")
        else:
            self.base_url = "https://api.tradestation.com"
            if self.debug:
                print(f"Using Live environment (base URL: {self.base_url})")

    def _debug_print(self, message: str) -> None:
        """Print a debug message if debug mode is enabled."""
        if self.debug:
            print(message)

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

        try:
            # Get valid token (will refresh if needed)
            token = await self.token_manager.get_valid_access_token()
        except Exception as e:
            # Convert to proper authentication error
            raise TradeStationAuthError(
                message=f"Failed to obtain valid access token: {str(e)}",
                original_error=e
            ) from e

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

    async def _handle_response(self, response: ClientResponse) -> Dict[str, Any]:
        """
        Handle API response and parse the JSON data or raise appropriate exceptions.
        
        Args:
            response: The response from the API
            
        Returns:
            Parsed JSON response data
            
        Raises:
            TradeStationAPIError: When an API error occurs
        """
        # Debug print
        self._debug_print(f"Response status: {response.status}")
        
        # Handle HTTP errors
        if response.status >= 400:
            # Attempt to parse error response body
            try:
                error_data = await response.json()
                self._debug_print(f"Error response: {error_data}")
            except:
                # If response is not valid JSON, use text
                error_text = await response.text()
                self._debug_print(f"Error response text: {error_text}")
                error_data = {"error": error_text}
            
            # Extract request ID from headers if available
            request_id = response.headers.get("X-Request-ID") or response.headers.get("Request-ID")
            if request_id:
                error_data["request_id"] = request_id
                
            # Map HTTP status to appropriate exception and raise
            raise map_http_error(response.status, error_data)
            
        # Get JSON response
        try:
            return await response.json()
        except (json.JSONDecodeError, aiohttp.ContentTypeError) as e:
            # Handle JSON parsing errors
            self._debug_print(f"JSON parsing error: {str(e)}")
            raise TradeStationAPIError(
                message=f"Invalid JSON response from API: {str(e)}",
                status_code=response.status,
                original_error=e
            ) from e

    async def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a GET request to the specified endpoint.

        Args:
            url: The endpoint URL
            params: Query parameters

        Returns:
            Response data as dictionary
            
        Raises:
            TradeStationAuthError: When authentication fails
            TradeStationRateLimitError: When rate limits are exceeded
            TradeStationResourceNotFoundError: When the requested resource doesn't exist
            TradeStationValidationError: When the request is invalid
            TradeStationNetworkError: When network connectivity issues occur
            TradeStationServerError: When server errors occur
            TradeStationTimeoutError: When the request times out
            TradeStationAPIError: For other API errors
        """
        session = await self._ensure_session()
        headers = await self._prepare_request(url)

        full_url = f"{self.base_url}{url}"

        # Debug print
        self._debug_print(f"Making GET request to: {full_url}")
        self._debug_print(f"Headers: {headers}")

        try:
            async with session.get(full_url, params=params, headers=headers) as response:
                if response is None:
                    raise TradeStationAPIError("Response object is None")

                # Process response headers for rate limiting
                await self._process_response(response, url)

                # Handle the response and return the data
                return await self._handle_response(response)
                
        except aiohttp.ClientError as e:
            # Convert aiohttp exceptions to our custom exceptions
            self._debug_print(f"Request error: {str(e)}")
            raise handle_request_exception(e) from e
        except TradeStationAPIError:
            # Re-raise our own exceptions
            raise
        except Exception as e:
            # Handle unexpected exceptions
            self._debug_print(f"Unexpected error: {str(e)}")
            raise TradeStationAPIError(
                message=f"Unexpected error during GET request: {str(e)}",
                original_error=e
            ) from e

    async def post(self, url: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a POST request to the specified endpoint.

        Args:
            url: The endpoint URL
            data: JSON body to send

        Returns:
            Response data as dictionary
            
        Raises:
            TradeStationAuthError: When authentication fails
            TradeStationRateLimitError: When rate limits are exceeded
            TradeStationResourceNotFoundError: When the requested resource doesn't exist
            TradeStationValidationError: When the request is invalid
            TradeStationNetworkError: When network connectivity issues occur
            TradeStationServerError: When server errors occur
            TradeStationTimeoutError: When the request times out
            TradeStationAPIError: For other API errors
        """
        session = await self._ensure_session()
        headers = await self._prepare_request(url)

        full_url = f"{self.base_url}{url}"

        # Debug print
        self._debug_print(f"Making POST request to: {full_url}")
        self._debug_print(f"Data: {data}")

        try:
            async with session.post(full_url, json=data, headers=headers) as response:
                # Process response headers for rate limiting
                await self._process_response(response, url)

                # Handle the response and return the data
                return await self._handle_response(response)
                
        except aiohttp.ClientError as e:
            # Convert aiohttp exceptions to our custom exceptions
            self._debug_print(f"Request error: {str(e)}")
            raise handle_request_exception(e) from e
        except TradeStationAPIError:
            # Re-raise our own exceptions
            raise
        except Exception as e:
            # Handle unexpected exceptions
            self._debug_print(f"Unexpected error: {str(e)}")
            raise TradeStationAPIError(
                message=f"Unexpected error during POST request: {str(e)}",
                original_error=e
            ) from e

    async def put(self, url: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a PUT request to the specified endpoint.

        Args:
            url: The endpoint URL
            data: JSON body to send

        Returns:
            Response data as dictionary
            
        Raises:
            TradeStationAuthError: When authentication fails
            TradeStationRateLimitError: When rate limits are exceeded
            TradeStationResourceNotFoundError: When the requested resource doesn't exist
            TradeStationValidationError: When the request is invalid
            TradeStationNetworkError: When network connectivity issues occur
            TradeStationServerError: When server errors occur
            TradeStationTimeoutError: When the request times out
            TradeStationAPIError: For other API errors
        """
        session = await self._ensure_session()
        headers = await self._prepare_request(url)

        full_url = f"{self.base_url}{url}"

        # Debug print
        self._debug_print(f"Making PUT request to: {full_url}")
        self._debug_print(f"Data: {data}")

        try:
            async with session.put(full_url, json=data, headers=headers) as response:
                # Process response headers for rate limiting
                await self._process_response(response, url)

                # Handle the response and return the data
                return await self._handle_response(response)
                
        except aiohttp.ClientError as e:
            # Convert aiohttp exceptions to our custom exceptions
            self._debug_print(f"Request error: {str(e)}")
            raise handle_request_exception(e) from e
        except TradeStationAPIError:
            # Re-raise our own exceptions
            raise
        except Exception as e:
            # Handle unexpected exceptions
            self._debug_print(f"Unexpected error: {str(e)}")
            raise TradeStationAPIError(
                message=f"Unexpected error during PUT request: {str(e)}",
                original_error=e
            ) from e

    async def delete(self, url: str) -> Dict[str, Any]:
        """
        Make a DELETE request to the specified endpoint.

        Args:
            url: The endpoint URL

        Returns:
            Response data as dictionary
            
        Raises:
            TradeStationAuthError: When authentication fails
            TradeStationRateLimitError: When rate limits are exceeded
            TradeStationResourceNotFoundError: When the requested resource doesn't exist
            TradeStationValidationError: When the request is invalid
            TradeStationNetworkError: When network connectivity issues occur
            TradeStationServerError: When server errors occur
            TradeStationTimeoutError: When the request times out
            TradeStationAPIError: For other API errors
        """
        session = await self._ensure_session()
        headers = await self._prepare_request(url)

        full_url = f"{self.base_url}{url}"

        # Debug print
        self._debug_print(f"Making DELETE request to: {full_url}")

        try:
            async with session.delete(full_url, headers=headers) as response:
                # Process response headers for rate limiting
                await self._process_response(response, url)

                # Handle the response and return the data
                return await self._handle_response(response)
                
        except aiohttp.ClientError as e:
            # Convert aiohttp exceptions to our custom exceptions
            self._debug_print(f"Request error: {str(e)}")
            raise handle_request_exception(e) from e
        except TradeStationAPIError:
            # Re-raise our own exceptions
            raise
        except Exception as e:
            # Handle unexpected exceptions
            self._debug_print(f"Unexpected error: {str(e)}")
            raise TradeStationAPIError(
                message=f"Unexpected error during DELETE request: {str(e)}",
                original_error=e
            ) from e

    async def create_stream(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> aiohttp.StreamReader:
        """
        Create a stream for streaming endpoints.

        Args:
            url: The endpoint URL
            params: Query parameters
            headers: Optional custom headers to include in the request

        Returns:
            Stream reader for reading the stream data
            
        Raises:
            TradeStationAuthError: When authentication fails
            TradeStationRateLimitError: When rate limits are exceeded
            TradeStationResourceNotFoundError: When the requested resource doesn't exist
            TradeStationValidationError: When the request is invalid
            TradeStationNetworkError: When network connectivity issues occur
            TradeStationServerError: When server errors occur
            TradeStationStreamError: When streaming-specific errors occur
            TradeStationAPIError: For other API errors
        """
        session = await self._ensure_session()

        # Prepare base headers with authentication
        try:
            base_headers = await self._prepare_request(url)
        except TradeStationAuthError:
            # Re-raise authentication errors
            raise
        except Exception as e:
            # Convert other errors during header preparation
            self._debug_print(f"Error preparing request headers: {str(e)}")
            raise TradeStationAPIError(
                message=f"Failed to prepare request headers: {str(e)}",
                original_error=e
            ) from e

        # Merge custom headers with base headers, prioritizing custom headers
        final_headers = base_headers.copy()
        if headers:
            final_headers.update(headers)

        full_url = f"{self.base_url}{url}"

        # Debug print
        self._debug_print(f"Making GET stream request to: {full_url}")
        self._debug_print(f"Headers: {final_headers}")

        try:
            response = await session.get(
                full_url,
                params=params,
                headers=final_headers,
                timeout=None,
            )

            await self._process_response(response, url)
            
            # Call raise_for_status to check for HTTP errors
            response.raise_for_status()
            
            return response.content
            
        except aiohttp.ClientError as e:
            # Convert aiohttp exceptions to our custom exceptions
            self._debug_print(f"Stream request error: {str(e)}")
            raise handle_request_exception(e) from e
        except TradeStationAPIError:
            # Re-raise our own exceptions
            raise
        except Exception as e:
            # Handle unexpected exceptions
            self._debug_print(f"Unexpected error during stream request: {str(e)}")
            raise TradeStationStreamError(
                message=f"Unexpected error creating stream: {str(e)}",
                original_error=e
            ) from e

    async def close(self) -> None:
        """
        Close the HTTP client and clean up resources.
        """
        if self._session:
            await self._session.close()
            self._session = None
            self._debug_print("HTTP client session closed")
