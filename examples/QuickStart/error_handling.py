#!/usr/bin/env python
"""
Example demonstrating error handling with the TradeStation API Python wrapper.

This example shows:
1. How to catch and handle specific exception types
2. Retry patterns for transient errors
3. Handling validation errors
4. Authentication error recovery
5. Best practices for error handling
"""

import asyncio
import logging
import random
import sys
import time
from typing import Any, Awaitable, Callable, Dict, Optional, TypeVar

from tradestation import (
    TradeStationAPIError,
    TradeStationAuthError,
    TradeStationClient,
    TradeStationNetworkError,
    TradeStationRateLimitError,
    TradeStationResourceNotFoundError,
    TradeStationServerError,
    TradeStationStreamError,
    TradeStationTimeoutError,
    TradeStationValidationError,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# TypeVar for generic retry function
T = TypeVar("T")


# Retry decorator for async functions
async def retry_async(
    func: Callable[..., Awaitable[T]],
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    retryable_exceptions: tuple = (
        TradeStationRateLimitError,
        TradeStationNetworkError,
        TradeStationServerError,
        TradeStationTimeoutError,
    ),
) -> T:
    """
    Retry an async function with exponential backoff.

    Args:
        func: The async function to retry
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        retryable_exceptions: Tuple of exceptions that should trigger retry

    Returns:
        The result of the function call

    Raises:
        The last exception encountered if all retries fail
    """
    attempt = 0
    last_exception = None

    while attempt < max_attempts:
        try:
            return await func()
        except retryable_exceptions as e:
            attempt += 1
            last_exception = e

            # Get retry_after from RateLimitError if available
            if isinstance(e, TradeStationRateLimitError) and e.retry_after:
                delay = min(e.retry_after, max_delay)
            else:
                # Exponential backoff with jitter
                delay = min(
                    base_delay * (2 ** (attempt - 1)) * (0.5 + 0.5 * random.random()), max_delay
                )

            logger.warning(
                f"Attempt {attempt}/{max_attempts} failed with {e.__class__.__name__}: {str(e)}. "
                f"Retrying in {delay:.2f} seconds..."
            )

            await asyncio.sleep(delay)

    # If we get here, all retries failed
    if last_exception:
        logger.error(f"All {max_attempts} retry attempts failed. Last error: {str(last_exception)}")
        raise last_exception

    # This should not happen, but just in case
    raise RuntimeError("Retry logic failed with no exception")


async def handle_quote_request(client: TradeStationClient, symbols: str) -> Dict[str, Any]:
    """
    Example function that handles quote requests with proper error handling.

    Args:
        client: TradeStationClient instance
        symbols: Comma-separated symbols to get quotes for

    Returns:
        Quote data for the requested symbols
    """
    try:
        # Use the retry decorator for the API call
        quotes = await retry_async(lambda: client.market_data.get_quote_snapshots(symbols))
        return quotes
    except TradeStationValidationError as e:
        # Handle validation errors (e.g., invalid symbols)
        logger.error(f"Validation error: {str(e)}")
        if e.validation_errors:
            logger.error(f"Validation details: {e.validation_errors}")
        return {"error": "Invalid request parameters", "details": str(e)}
    except TradeStationResourceNotFoundError as e:
        # Handle not found errors
        logger.error(f"Resource not found: {str(e)}")
        return {"error": "Resource not found", "details": str(e)}
    except TradeStationAuthError as e:
        # Handle authentication errors
        logger.error(f"Authentication error: {str(e)}")
        # You might want to attempt token refresh here
        return {"error": "Authentication failed", "details": str(e)}
    except TradeStationAPIError as e:
        # Catch any other API errors
        logger.error(f"API error: {str(e)}")
        if e.status_code:
            logger.error(f"Status code: {e.status_code}")
        if e.request_id:
            logger.error(f"Request ID: {e.request_id}")
        return {"error": "API error occurred", "details": str(e)}
    except Exception as e:
        # Catch unexpected errors
        logger.exception(f"Unexpected error: {str(e)}")
        return {"error": "Unexpected error", "details": str(e)}


async def handle_streaming(client: TradeStationClient, symbols: str) -> None:
    """
    Example function demonstrating error handling with streaming data.

    Args:
        client: TradeStationClient instance
        symbols: Comma-separated symbols for streaming quotes
    """
    stream_id = None

    try:
        # Define callback that handles its own errors
        def quote_callback(data):
            try:
                # Process quote data
                print(f"Quote received: {data}")
            except Exception as e:
                # Ensure callback errors are caught and don't crash the stream
                logger.error(f"Error in quote callback: {str(e)}")

        # Start stream with retry
        async def start_stream():
            return await client.market_data.stream_quotes(symbols, quote_callback)

        stream_id = await retry_async(start_stream)

        # Keep stream alive for demo purposes
        await asyncio.sleep(30)

    except TradeStationStreamError as e:
        logger.error(f"Stream error: {str(e)}")
    except TradeStationValidationError as e:
        logger.error(f"Validation error: {str(e)}")
    except TradeStationAuthError as e:
        logger.error(f"Authentication error: {str(e)}")
    except TradeStationAPIError as e:
        logger.error(f"API error: {str(e)}")
    except Exception as e:
        logger.exception(f"Unexpected error: {str(e)}")
    finally:
        # Always clean up resources
        if stream_id:
            try:
                await client.market_data.disconnect_stream(stream_id)
                logger.info(f"Stream {stream_id} disconnected")
            except Exception as e:
                logger.error(f"Error disconnecting stream: {str(e)}")


async def main():
    """Main example function demonstrating error handling patterns."""
    client = None

    try:
        # Initialize client with error handling
        try:
            # Create client with potential for auth errors
            client = TradeStationClient(debug=True)
            logger.info("Client initialized successfully")
        except TradeStationAuthError as e:
            logger.error(f"Authentication failed: {str(e)}")
            sys.exit(1)
        except ValueError as e:
            logger.error(f"Invalid configuration: {str(e)}")
            sys.exit(1)

        # Example 1: Handle quote request with retries
        logger.info("Example 1: Fetching quotes with retry logic")
        quotes_result = await handle_quote_request(client, "MSFT,AAPL,AMZN")
        logger.info(f"Quotes result: {quotes_result}")

        # Example 2: Intentional error to demonstrate validation error handling
        logger.info("Example 2: Demonstrating validation error handling")
        try:
            invalid_result = await client.market_data.get_quote_snapshots("")
        except TradeStationValidationError as e:
            logger.info(f"Caught expected validation error: {str(e)}")

        # Example 3: Stream handling with error management
        logger.info("Example 3: Demonstrating streaming error handling")
        await handle_streaming(client, "MSFT")

    except Exception as e:
        logger.exception(f"Unhandled exception: {str(e)}")
    finally:
        # Always clean up resources
        if client:
            try:
                await client.close()
                logger.info("Client closed successfully")
            except Exception as e:
                logger.error(f"Error closing client: {str(e)}")


if __name__ == "__main__":
    # Add SIGINT handler to gracefully exit on Ctrl+C
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting due to keyboard interrupt")
        sys.exit(0)
