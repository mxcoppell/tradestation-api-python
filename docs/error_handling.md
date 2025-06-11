# Error Handling in the TradeStation API Python Wrapper

This guide explains how to handle errors and exceptions when working with the TradeStation API Python wrapper.

## Exception Hierarchy

The library provides a comprehensive set of exception classes to handle different types of errors that can occur when interacting with the TradeStation API:

```
TradeStationAPIError (base exception)
├── TradeStationAuthError               # Authentication failures (401, 403)
├── TradeStationRateLimitError          # Rate limit exceeded (429)
├── TradeStationResourceNotFoundError   # Resource not found (404)
├── TradeStationValidationError         # Invalid request parameters (400)
├── TradeStationNetworkError            # Network connectivity issues
├── TradeStationServerError             # Server-side errors (5xx)
├── TradeStationTimeoutError            # Request timeouts
└── TradeStationStreamError             # WebSocket streaming issues
```

## Exception Properties

All exception classes inherit from the base `TradeStationAPIError` class, which provides the following properties:

- `message`: A descriptive error message
- `status_code`: The HTTP status code (if applicable)
- `request_id`: The API request ID for troubleshooting with TradeStation support
- `response`: The full response content (if available)
- `original_error`: The original exception that caused this error (if any)

Some specific exception types provide additional properties:

- `TradeStationRateLimitError.retry_after`: Suggested time in seconds to wait before retrying
- `TradeStationValidationError.validation_errors`: Dictionary of validation errors
- `TradeStationResourceNotFoundError.resource`: The resource that was not found

## Basic Error Handling

Here's a basic pattern for handling exceptions:

```python
from tradestation import TradeStationClient
from tradestation import (
    TradeStationAPIError,
    TradeStationAuthError,
    TradeStationRateLimitError,
    TradeStationValidationError,
    TradeStationNetworkError
)

async def basic_error_handling():
    client = TradeStationClient()
    
    try:
        # Make an API call
        quotes = await client.market_data.get_quotes("AAPL,MSFT")
        print(f"Got quotes successfully")
        
    except TradeStationAuthError as e:
        print(f"Authentication failed: {e}")
        # You might want to refresh tokens or prompt for re-login
        
    except TradeStationRateLimitError as e:
        print(f"Rate limit exceeded: {e}")
        if e.retry_after:
            print(f"Try again after {e.retry_after} seconds")
            
    except TradeStationValidationError as e:
        print(f"Invalid request parameters: {e}")
        if e.validation_errors:
            print(f"Validation details: {e.validation_errors}")
            
    except TradeStationResourceNotFoundError as e:
        print(f"Resource not found: {e}")
        
    except TradeStationNetworkError as e:
        print(f"Network error: {e}")
        
    except TradeStationServerError as e:
        print(f"Server error: {e}")
        
    except TradeStationTimeoutError as e:
        print(f"Request timed out: {e}")
        
    except TradeStationStreamError as e:
        print(f"Streaming error: {e}")
        
    except TradeStationAPIError as e:
        # Catch-all for any other API errors
        print(f"API error: {e}")
        
    except Exception as e:
        # Catch any other unexpected errors
        print(f"Unexpected error: {e}")
        
    finally:
        # Always clean up resources
        await client.close()
```

## Advanced Error Handling with Retries

For transient errors like network issues, timeouts, or rate limits, implementing retry logic can improve resilience:

```python
import asyncio
import random
from typing import Callable, TypeVar, Awaitable

from tradestation import (
    TradeStationRateLimitError,
    TradeStationNetworkError,
    TradeStationServerError,
    TradeStationTimeoutError
)

T = TypeVar('T')

async def retry_with_backoff(
    func: Callable[[], Awaitable[T]],
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    retryable_exceptions=(
        TradeStationRateLimitError,
        TradeStationNetworkError,
        TradeStationServerError,
        TradeStationTimeoutError
    )
) -> T:
    """
    Retry an async function with exponential backoff.
    
    Args:
        func: Async function to retry
        max_attempts: Maximum number of attempts
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
            
            # Check if we've reached max attempts
            if attempt >= max_attempts:
                break
                
            # Calculate delay with RateLimitError handling
            if isinstance(e, TradeStationRateLimitError) and e.retry_after:
                delay = min(e.retry_after, max_delay)
            else:
                # Exponential backoff with jitter to prevent thundering herd
                jitter = random.random() * 0.5 + 0.5  # 0.5-1.0 random value
                delay = min(base_delay * (2 ** (attempt - 1)) * jitter, max_delay)
            
            print(f"Attempt {attempt}/{max_attempts} failed: {e}")
            print(f"Retrying in {delay:.2f} seconds...")
            
            await asyncio.sleep(delay)
    
    # If we get here, all retries failed
    if last_exception:
        print(f"All {max_attempts} retry attempts failed")
        raise last_exception
    
    raise RuntimeError("Retry logic failed with no exception")
```

### Using the Retry Function

```python
async def get_quotes_with_retry(client, symbols):
    return await retry_with_backoff(
        lambda: client.market_data.get_quotes(symbols)
    )

# Usage
try:
    quotes = await get_quotes_with_retry(client, "AAPL,MSFT,AMZN")
    print(f"Got quotes after retries: {quotes}")
except Exception as e:
    print(f"Failed even with retries: {e}")
```

## Handling Streaming Errors

Streaming connections may encounter various errors. Here's a pattern for handling them:

```python
async def handle_streaming_errors(client, symbols):
    stream_id = None
    
    try:
        # Define callback with its own error handling
        def quote_callback(data):
            try:
                print(f"Quote received: {data}")
            except Exception as e:
                # Never let callback errors crash the stream
                print(f"Error in callback: {e}")
        
        # Start stream
        stream_id = await client.market_data.stream_quotes(symbols, quote_callback)
        
        # Keep stream alive
        await asyncio.sleep(60)  # Run for 60 seconds
        
    except TradeStationAuthError as e:
        print(f"Authentication error: {e}")
        # Handle auth refresh
        
    except TradeStationStreamError as e:
        print(f"Stream error: {e}")
        # Consider reconnection logic
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        
    finally:
        # Always clean up stream resources
        if stream_id:
            try:
                await client.market_data.disconnect_stream(stream_id)
                print(f"Stream {stream_id} disconnected")
            except Exception as e:
                print(f"Error closing stream: {e}")
```

## Best Practices

1. **Always catch specific exceptions first**: Catch the most specific exception types before more general ones.

2. **Include a catch-all for unexpected errors**: Always include a general `Exception` catch at the end to prevent crashes.

3. **Use context information**: Extract the `status_code`, `request_id`, etc. from exceptions for better diagnostics.

4. **Implement retry logic for transient errors**: Use exponential backoff with jitter for rate limits, network issues, and server errors.

5. **Log all errors**: Log errors with their context information for troubleshooting.

6. **Clean up resources in finally blocks**: Always close clients and streams in `finally` blocks.

7. **Handle validation errors gracefully**: Parse and present validation errors to help users fix their inputs.

8. **Implement fallback mechanisms**: For critical operations, have fallback mechanisms when API calls fail.

## Complete Example

For a complete example showing error handling best practices, check the `examples/QuickStart/error_handling.py` file in the repository.

## Error Handling during Client Initialization

Handle errors that can occur during client initialization:

```python
try:
    client = TradeStationClient(environment="Simulation")
except TradeStationAuthError as e:
    print(f"Authentication failed: {e}")
    # Handle auth errors
except ValueError as e:
    print(f"Invalid configuration: {e}")
    # Handle configuration errors
except Exception as e:
    print(f"Unexpected error during initialization: {e}")
```

## Working with TradeStation Support

When contacting TradeStation support about API issues, provide the following information from exceptions:

- The exception type (e.g., `TradeStationAuthError`)
- The status code (`e.status_code`)
- The request ID (`e.request_id`)
- The error message (`str(e)`)
- Any validation errors for validation exceptions (`e.validation_errors`)

This information will help TradeStation support diagnose and resolve the issue more quickly. 