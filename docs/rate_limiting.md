# Rate Limiting

The TradeStation API enforces rate limits to ensure fair usage and system stability. The TradeStation API Python Wrapper includes built-in rate limiting functionality to handle these limits gracefully.

## How API Rate Limits Work

TradeStation's API uses the following rate limiting approach:

1. Each endpoint has a specific rate limit (typically 120 requests per minute)
2. When you make a request, the API returns rate limit information in the response headers
3. If you exceed the rate limit, the API returns a 429 (Too Many Requests) error

The relevant headers include:

- `X-RateLimit-Limit`: The maximum number of requests allowed in the current time window
- `X-RateLimit-Remaining`: The number of requests remaining in the current time window
- `X-RateLimit-Reset`: The time (in seconds) when the rate limit window resets

## Automatic Rate Limiting

The client automatically manages rate limits for you:

1. It tracks rate limit information for each endpoint
2. When a limit is reached, it queues additional requests
3. It waits for the rate limit to reset before sending queued requests
4. It handles backoff and retry logic for rate limit errors

This behavior happens automatically and is transparent to your code.

## Example

When using the client, you don't need to manually handle rate limiting:

```python
import asyncio
from src.client.tradestation_client import TradeStationClient

async def main():
    client = TradeStationClient()
    
    try:
        # This will automatically respect rate limits
        for symbol in ["AAPL", "MSFT", "GOOGL", "AMZN", "FB", "TSLA"]:
            quote = await client.market_data.get_quotes([symbol])
            print(f"{symbol}: ${quote.Quotes[0].Last}")
            
            # No need to add delays - the client handles rate limiting
    finally:
        await client.close()

asyncio.run(main())
```

## Rate Limit Configuration

The default rate limit is set to 120 requests per minute, but the client adjusts this based on the actual limits returned by the API.

You can monitor the current rate limit status using the HTTP client:

```python
# Get the HTTP client from your TradeStation client
http_client = client.http_client

# Get the rate limiter
rate_limiter = http_client.rate_limiter

# Check rate limit for a specific endpoint
limit_info = rate_limiter.get_rate_limit("/v3/marketdata/quotes")
if limit_info:
    print(f"Limit: {limit_info['limit']}")
    print(f"Remaining: {limit_info['remaining']}")
    print(f"Reset time: {limit_info['resetTime']}")
```

## Rate Limiting Strategy

The library uses a sophisticated rate limiting strategy:

1. **Tracking**: Each endpoint's rate limit is tracked separately
2. **Queuing**: When a limit is reached, requests are queued
3. **Time-based reset**: Queued requests are processed after the rate limit resets
4. **Fairness**: Requests are processed in the order they were received

## Handling Rate Limit Exceptions

While the client tries to prevent rate limit errors, it's still possible to encounter them in certain scenarios (like when multiple client instances are used). When a rate limit error occurs, the client will:

1. Log the error
2. Wait for the appropriate reset time
3. Retry the request automatically (up to a configurable maximum number of times)

If you need to handle rate limit errors manually, you can catch exceptions:

```python
try:
    # Make API request
    response = await client.market_data.get_quotes(["AAPL"])
except Exception as e:
    if "429" in str(e):
        print("Rate limit exceeded, please try again later")
    else:
        print(f"Error: {e}")
```

## Performance Considerations

To optimize your application's performance with rate limits:

1. **Batch requests** when possible (e.g., request quotes for multiple symbols in one call)
2. **Cache responses** that don't change frequently
3. **Implement exponential backoff** for critical operations
4. **Monitor rate limit headers** to adjust your request patterns
5. **Prioritize important requests** in your application logic

## Advanced Rate Limiting

For advanced use cases, you might want to implement custom rate limiting logic. The `RateLimiter` class can be extended or replaced with a custom implementation:

```python
from src.utils.rate_limiter import RateLimiter

class CustomRateLimiter(RateLimiter):
    async def wait_for_slot(self, endpoint: str) -> None:
        # Custom implementation
        # ...
        
    # Override other methods as needed
```

## Best Practices

1. **Batch requests** when possible to reduce the number of API calls
2. **Cache responses** that don't change frequently
3. **Handle rate limit errors gracefully** in your application
4. **Don't make unnecessary requests** to avoid hitting rate limits
5. **Implement retry logic with exponential backoff** for critical operations
6. **Monitor your usage** to identify patterns and optimize your code 