# TradeStation API Python Wrapper

A Python client library for the TradeStation API. This library provides a Pythonic interface to interact with TradeStation's API, allowing developers to easily integrate trading applications with TradeStation.

## Features

- **Authentication**: Simplified OAuth workflow with auto-refresh capabilities
- **Market Data**: Access real-time and historical price data, quotes, symbols, and more
- **Brokerage**: Retrieve accounts, positions, balances, and orders
- **Order Execution**: Place, modify, and cancel orders
- **Streaming**: Real-time data streaming with WebSocket support
- **Rate Limiting**: Built-in rate limit handling to prevent API throttling

## Requirements

- Python 3.11+
- TradeStation account
- TradeStation API credentials (Client ID and Secret)

## Installation

```bash
# Install with Poetry (recommended)
poetry install

# Or with pip
pip install tradestation-api-python  # Coming soon
```

## Quick Start

```python
import asyncio
from dotenv import load_dotenv
from src.client.tradestation_client import TradeStationClient

async def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Create a client using environment variables
    # Requires CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN in .env
    client = TradeStationClient()
    
    try:
        # Get quote for a symbol
        quote = await client.market_data.get_quotes(["AAPL"])
        print(f"AAPL: ${quote.Quotes[0].Last}")
        
        # Get account balances
        accounts = await client.brokerage.get_accounts()
        print(f"Found {len(accounts.Accounts)} accounts")
        
    finally:
        # Always close the client when done
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

See the `examples` directory for more comprehensive examples.

## Project Structure

```
.
├── docs/                 # API documentation
├── examples/             # Example scripts
│   ├── Brokerage/        # Account and order history examples
│   ├── MarketData/       # Price, quote, and symbol examples
│   └── OrderExecution/   # Order placement and management examples
└── src/                  # Source code
    ├── client/           # Main client implementation
    ├── services/         # API service implementations
    │     ├── Brokerage/
    │     ├── MarketData/
    │     └── OrderExecution/
    ├── streaming/        # WebSocket streaming implementation
    ├── ts_types/         # Type definitions
    └── utils/            # Utility functions and helpers
```

## Authentication

The library supports OAuth authentication using refresh tokens. You can provide credentials in several ways:

1. Environment variables:
   - `CLIENT_ID`: Your TradeStation API client ID
   - `CLIENT_SECRET`: Your TradeStation API client secret
   - `REFRESH_TOKEN`: Your refresh token
   - `ENVIRONMENT`: Either "Live" or "Simulation"

2. Configuration dictionary:
   ```python
   client = TradeStationClient({
       "client_id": "your_client_id",
       "client_secret": "your_client_secret",
       "refresh_token": "your_refresh_token",
       "environment": "Live"  # or "Simulation"
   })
   ```

3. Direct parameters:
   ```python
   client = TradeStationClient(
       refresh_token="your_refresh_token",
       environment="Live"  # Credentials loaded from environment
   )
   ```

## Documentation

See the following resources for more information:

- [Authentication](docs/authentication.md) - Coming soon
- [Market Data](docs/market_data.md) - Coming soon
- [Brokerage](docs/brokerage.md) - Coming soon
- [Order Execution](docs/order_execution.md) - Coming soon
- [Streaming](docs/streaming.md) - Coming soon
- [Rate Limiting](docs/rate_limiting.md) - Coming soon

## License

MIT 