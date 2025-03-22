# Streaming

The TradeStation API Python Wrapper provides robust support for real-time data streaming via WebSockets. This document explains how to use the streaming functionality.

## Overview

The streaming functionality is built around the `StreamManager` class, which handles:

- WebSocket connection establishment and management
- Authentication and token refreshing
- Automatic reconnection on disconnection
- Message parsing and distribution
- Subscription management

## Available Streams

The following data streams are available:

| Stream Type | Description | Service |
|-------------|-------------|---------|
| Quote | Real-time quote updates | Market Data |
| Bar | Price bar updates | Market Data |
| Trade | Time and sales data | Market Data |
| OrderStatus | Order status updates | Order Execution |
| PositionChange | Position updates | Brokerage |
| BalanceChange | Account balance updates | Brokerage |

## Basic Usage

The streaming functionality is accessed through the service classes. Here's a simple example of streaming quotes:

```python
import asyncio
from dotenv import load_dotenv
from src.client.tradestation_client import TradeStationClient

async def quote_callback(quote_data):
    """Process incoming quote data"""
    print(f"Quote update: {quote_data['Symbol']} - Last: {quote_data['Last']}")

async def main():
    # Load environment variables
    load_dotenv()
    
    # Create client
    client = TradeStationClient()
    
    try:
        # Subscribe to quote updates for multiple symbols
        subscription = await client.market_data.stream_quotes(
            symbols=["AAPL", "MSFT", "GOOGL"],
            callback=quote_callback
        )
        
        # Keep the stream running for 60 seconds
        print("Streaming started. Waiting for 60 seconds...")
        await asyncio.sleep(60)
        
        # Unsubscribe when done
        await subscription.unsubscribe()
        
    finally:
        # Close the client to release resources
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Stream Subscriptions

When you subscribe to a stream, the method returns a `Subscription` object that allows you to:

- Unsubscribe from the stream
- Add additional callbacks
- Check the subscription status
- Access the subscription ID

```python
# Create a subscription
subscription = await client.market_data.stream_quotes(["AAPL"], quote_callback)

# Add another callback
subscription.add_callback(another_callback)

# Check if subscription is active
if subscription.is_active():
    print("Subscription is active")

# Get the subscription ID
subscription_id = subscription.get_id()

# Unsubscribe when done
await subscription.unsubscribe()
```

## Available Streaming Methods

### Market Data Streaming

```python
# Quote streaming
subscription = await client.market_data.stream_quotes(
    symbols=["AAPL", "MSFT"],
    callback=quote_callback
)

# Bar streaming
subscription = await client.market_data.stream_bars(
    symbol="SPY",
    interval="1",  # 1-minute bars
    callback=bar_callback
)

# Time and sales streaming
subscription = await client.market_data.stream_time_and_sales(
    symbol="AAPL",
    callback=trade_callback
)
```

### Order Execution Streaming

```python
# Order status updates
subscription = await client.order_execution.stream_order_updates(
    callback=order_update_callback
)
```

### Brokerage Streaming

```python
# Position updates
subscription = await client.brokerage.stream_position_changes(
    callback=position_callback
)

# Balance updates
subscription = await client.brokerage.stream_balance_changes(
    callback=balance_callback
)
```

## Error Handling

The stream manager includes built-in error handling and reconnection logic:

- Automatic reconnection on disconnection
- Token refresh when authentication expires
- Backoff strategy for reconnection attempts
- Error event callbacks

You can handle stream errors by adding an error callback:

```python
def error_callback(error):
    print(f"Stream error: {error}")

subscription = await client.market_data.stream_quotes(
    symbols=["AAPL"],
    callback=quote_callback,
    error_callback=error_callback
)
```

## Advanced Usage

### Managing Multiple Streams

You can subscribe to multiple streams simultaneously:

```python
# Subscribe to multiple streams
quote_subscription = await client.market_data.stream_quotes(
    symbols=["AAPL", "MSFT"],
    callback=quote_callback
)

bar_subscription = await client.market_data.stream_bars(
    symbol="SPY",
    interval="1",
    callback=bar_callback
)

# When done with all streams
await quote_subscription.unsubscribe()
await bar_subscription.unsubscribe()

# Or close all active streams at once
client.close_all_streams()
```

### Custom Stream Processing

For advanced use cases, you can create custom stream processing logic:

```python
async def custom_processor(data):
    # Custom processing logic
    processed_data = process_data(data)
    
    # Update your application state
    update_app_state(processed_data)
    
    # Maybe save to database
    await save_to_db(processed_data)

# Use your custom processor as a callback
subscription = await client.market_data.stream_quotes(
    symbols=["AAPL"],
    callback=custom_processor
)
```

## Performance Considerations

- The library limits the number of concurrent streams to avoid overwhelming the client's resources or hitting API rate limits
- Processing callbacks should be lightweight to avoid blocking the message processing loop
- For intensive processing, consider offloading work to a separate thread or process

## Cleanup

Always close your streams and the client when done:

```python
# Unsubscribe from all active streams
client.close_all_streams()

# Close the client to release resources
await client.close()
``` 