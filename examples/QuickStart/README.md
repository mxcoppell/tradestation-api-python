# QuickStart Examples

This directory contains quick-start examples that demonstrate the basic usage of the TradeStation API Python wrapper.

## Available Examples

1. **quick_start.py** - Basic setup, symbol details retrieval, and pretty JSON output.
2. **multi_symbol_quotes.py** - Fetching quotes for multiple symbols, displayed in a clean table and detailed JSON format.
3. **stream_quotes.py** - Streaming real-time quote updates via HTTP Server-Sent Events (SSE) with proper cancellation handling.

## What You'll Learn

1. How to set up a TradeStationClient with proper authentication.
2. How to make API requests with automatic rate limiting.
3. How to fetch various types of market data (symbol details, quotes).
4. How to establish HTTP SSE streaming connections for real-time data.
5. How to process streaming data line by line.
6. How to handle API responses and potential errors.
7. How to properly clean up resources.

## Prerequisites

- Python 3.8 or later
- A TradeStation account with API access
- API credentials (client ID, refresh token)

## Setup

1. Create a `.env` file in the root directory of the project with your TradeStation API credentials:

```
CLIENT_ID=your_client_id
REFRESH_TOKEN=your_refresh_token
ENVIRONMENT=Simulation  # or 'Live' for production
```

> **Note**: You can get your refresh token by running the `get_refresh_token.sh` script in the root directory.

2. Install the required dependencies:

```bash
poetry install
```

## Running the Examples

### Basic Symbol Details Example

```bash
poetry run python examples/QuickStart/quick_start.py
```

This example:
- Fetches detailed information about AAPL stock.
- Displays key symbol information and formatting rules in clean JSON and table formats.
- Shows how to use price and quantity formatting.
- Provides the complete symbol definition as clean JSON.

### Multi-Symbol Quotes Example

```bash
poetry run python examples/QuickStart/multi_symbol_quotes.py
```

This example:
- Fetches real-time quotes for multiple symbols.
- Displays quote data in a clean, aligned table format.
- Shows detailed quote information for the first symbol as clean JSON.

### Streaming Quotes Example

```bash
poetry run python examples/QuickStart/stream_quotes.py
```

This example:
- Establishes a real-time streaming connection using HTTP Server-Sent Events (SSE).
- Continuously processes and displays incoming quote data line by line.
- Handles heartbeats and potential stream errors.
- Demonstrates proper signal handling for graceful termination (Ctrl+C).
- Shows resource cleanup.

## Key Concepts

### Client Initialization

The TradeStationClient will automatically:
- Load credentials from environment variables
- Handle authentication using your refresh token
- Manage rate limiting for API requests

```python
from src.client.tradestation_client import TradeStationClient

client = TradeStationClient()
```

### API Requests

The client has service objects for different categories of API endpoints:

- `client.market_data` - Market data services
- `client.brokerage` - Brokerage account services
- `client.order_execution` - Order execution services

Examples:
```python
# Get symbol details
symbol_details = await client.market_data.get_symbol_details('AAPL')

# Get quotes for multiple symbols
quotes = await client.market_data.get_quote_snapshots("AAPL,MSFT,SPY")
```

### Streaming Data (HTTP SSE)

For real-time data like quotes, TradeStation uses Server-Sent Events over HTTP. The client provides a `StreamReader` to process this.

```python
import json

# Start a streaming connection
stream_reader = await client.market_data.stream_quotes("AAPL,MSFT,GOOG")

# Process streaming data line by line
while True:
    line = await stream_reader.readline()
    if not line:
        break # Stream closed
    try:
        data = json.loads(line.strip().decode('utf-8'))
        if 'Symbol' in data and 'Last' in data: # Process quote
            print(f"Quote: {data.get('Symbol')} Last: {data.get('Last')}")
        elif 'Heartbeat' in data: # Process heartbeat
            print(f"Heartbeat: {data.get('Timestamp')}")
        elif 'Error' in data: # Process error
            print(f"Error: {data.get('Message')}")
            break # Or handle error appropriately
    except json.JSONDecodeError:
        # Handle non-JSON lines if necessary
        pass 
    except Exception as e:
        # Handle other processing errors
        print(f"Error processing line: {e}")
        break

# HttpClient cleanup handles the underlying connection
```

### Error Handling

Always wrap API calls in try/except blocks to handle potential errors:

```python
try:
    response = await client.market_data.get_symbol_details('AAPL')
except Exception as error:
    print(f"Error: {str(error)}")
finally:
    # Clean up resources (closes underlying HTTP session)
    if client:
        await client.http_client.close()
```

## Next Steps

After mastering these examples, explore the other examples in the `examples` directory:

- `MarketData` - Additional examples for fetching various market data
- `Brokerage` - Examples for working with accounts and positions
- `OrderExecution` - Examples for placing and managing orders

## Conclusion

These QuickStart examples provide an introduction to the core functionality of the TradeStation API Python wrapper. They demonstrate:

1. **Basic API Access** - Making simple requests to get market data.
2. **Multiple Symbol Data** - Working with multiple symbols efficiently.
3. **Real-time Streaming (SSE)** - Setting up and managing HTTP streaming connections.

By exploring these examples, you should now understand how to authenticate with the TradeStation API, fetch market data, and establish real-time data streams. The Python wrapper handles the complex authentication, rate limiting, and connection management, allowing you to focus on your trading strategies and applications.

For more advanced use cases, check the other example directories or refer to the official TradeStation API documentation for details on available endpoints and data structures. 