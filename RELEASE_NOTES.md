# Release Notes: v1.2.0

## Overview

This release focuses on improving error handling throughout the TradeStation API Python wrapper. It introduces a comprehensive exception hierarchy, more specific error types, and better error reporting to enhance developer experience when dealing with API errors.

## New Features

### Enhanced Exception Hierarchy

- Added base `TradeStationAPIError` class with consistent properties:
  - Status code
  - Request ID
  - Original exception
  - Response data

- New specialized exception types:
  - `TradeStationAuthError`: For authentication failures (401, 403)
  - `TradeStationRateLimitError`: For rate limit issues (429) with retry_after support
  - `TradeStationResourceNotFoundError`: For resources not found (404)
  - `TradeStationValidationError`: For validation failures (400) with detailed validation errors
  - `TradeStationNetworkError`: For network connectivity issues
  - `TradeStationServerError`: For server-side errors (5xx)
  - `TradeStationTimeoutError`: For request timeouts
  - `TradeStationStreamError`: For streaming-specific errors

### Improved Client Implementation

- Updated HTTP client to use the new exception system throughout all request methods
- Fixed error handling in the `create_stream` method
- Enhanced error details and context in exception messages
- Added helper functions for mapping HTTP status codes to appropriate exceptions
- Improved handling of aiohttp exceptions

### Documentation and Examples

- Added comprehensive documentation on error handling in `docs/error_handling.md`
- Created example file `examples/QuickStart/error_handling.py` demonstrating:
  - Proper exception handling patterns
  - Retry logic with exponential backoff
  - Stream error handling
  - Context-specific error handling
- Updated method docstrings in `TradeStationClient` to include exception information

## Bug Fixes

- Fixed validation error handling to properly extract field-level errors
- Fixed redundant error handling in stream creation
- Addressed potential issues with the random module in retry examples

## Upgrading

This release maintains backward compatibility with existing code while providing more specific exception types for improved error handling. Projects using previous versions will continue to work, but can now take advantage of the enhanced error handling capabilities.

To leverage the new features, update your error handling to catch specific exception types:

```python
try:
    quotes = await client.market_data.get_quote_snapshots("MSFT,AAPL")
except TradeStationValidationError as e:
    # Handle validation errors with e.validation_errors
except TradeStationAuthError as e:
    # Handle authentication issues
except TradeStationRateLimitError as e:
    # Use e.retry_after for smart retries
except TradeStationAPIError as e:
    # Fall back for other API errors
``` 