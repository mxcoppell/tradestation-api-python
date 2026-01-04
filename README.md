# TradeStation API Python Wrapper 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/tradestation-api-python.svg)](https://badge.fury.io/py/tradestation-api-python)

Hey there, Trader! 👋 Ready to connect your Python apps to the TradeStation universe? This library makes it easy-peasy.

Think of it as your friendly Pythonic remote control for TradeStation's API. Build trading bots, analyze data, manage your account – all with clean, asynchronous Python code.

## What Can You Do? ✨

*   **Log In Easily:** Handles the tricky OAuth 2.0 stuff (including token refreshes) so you don't have to.
*   **Market Pulse:** Grab real-time quotes, historical price bars, symbol details, and more.
*   **Account Access:** Check your balances, see your positions, and review order history.
*   **Trade Time:** Place, change, or cancel orders programmatically.
*   **Live Streams:** Get data beamed straight to you with WebSocket support.
*   **Plays Nicely:** Built-in rate limiting helps you avoid getting timed out by the API.

## What You'll Need 📋

*   Python 3.11 or newer (Gotta have that async power!)
*   A TradeStation Account (Real or Simulated)
*   Your TradeStation API Credentials (Client ID & Refresh Token - get these from the [Developer Portal](https://developer.tradestation.com/))

## Get It Installed! 💻

Open your terminal and let's get this library installed.

```bash
# Option 1: Install directly from PyPI (Easiest 🌟)
pip install tradestation-api-python

# Option 2: Clone the project (for developers)
git clone https://github.com/mxcoppell/tradestation-api-python.git
cd tradestation-api-python

# Then install using Poetry (Recommended for development ✨)
poetry install

# OR: Use pip if you prefer
# pip install -e .
```

## Quick Start: Your First API Call! 🚀

Let's fetch a stock quote right now!

1.  **Set up your secrets:** Copy `.env.sample` to `.env` and fill in your `CLIENT_ID`, `REFRESH_TOKEN`, and `ENVIRONMENT` (`Live` or `Simulation`).
    ```bash
    cp .env.sample .env
    # Now edit .env with your details!
    ```
2.  **Run this Python code:**

```python
import asyncio
import os
from dotenv import load_dotenv
from tradestation import TradeStationClient

async def get_a_quote():
    # Load secrets from .env file
    load_dotenv()
    print(f"Using Environment: {os.getenv('ENVIRONMENT')}")

    # Create the client (it reads your .env automatically!)
    client = TradeStationClient()

    try:
        print("Asking TradeStation for an AAPL quote...")
        # Use the market data service to get a quote snapshot
        quote_response = await client.market_data.get_quote_snapshots("AAPL")

        if quote_response and quote_response.Quotes:
            aapl_price = quote_response.Quotes[0].Last
            print(f"----> Got it! AAPL last price: ${aapl_price}")
        else:
            print("Hmm, couldn't get the quote. Error:", getattr(quote_response, 'Errors', 'Unknown error'))

    except Exception as e:
        print(f"Whoops! Something went wrong: {e}")
    finally:
        print("Closing the connection.")
        # Always close the client when you're finished!
        await client.close()

if __name__ == "__main__":
    asyncio.run(get_a_quote())
```

Want more? Check out the `examples/QuickStart` directory for scripts you can run immediately!

## Project Peek 👀

Curious how it's organized?

```
.
├── docs/                 # You are here! (Hopefully useful docs)
├── examples/             # Ready-to-run example scripts!
│   ├── QuickStart/       # Start here!
│   ├── Brokerage/        # Account & order history examples
│   ├── MarketData/       # Price, quote, & symbol examples
│   └── OrderExecution/   # Placing & managing orders examples
└── src/                  # The heart of the library
    └── tradestation/     # The importable package
        ├── client/       # The main TradeStationClient
        ├── services/     # API sections (MarketData, Brokerage, etc.)
        ├── streaming/    # WebSocket streaming code
        ├── ts_types/     # Data models (Pydantic types)
        └── utils/        # Helpers (Auth, Rate Limiting, etc.)
```

## Error Handling 🛡️

This library provides a comprehensive exception system to help you handle API errors gracefully:

### Exception Hierarchy

```
TradeStationAPIError (base exception)
├── TradeStationAuthError           # Authentication failures (401, 403)
├── TradeStationRateLimitError      # Rate limit exceeded (429)
├── TradeStationResourceNotFoundError # Resource not found (404)
├── TradeStationValidationError     # Invalid request parameters (400)
├── TradeStationNetworkError        # Network connectivity issues
├── TradeStationServerError         # Server-side errors (5xx)
├── TradeStationTimeoutError        # Request timeouts
└── TradeStationStreamError         # WebSocket streaming issues
```

### Using Exception Handling

```python
from tradestation import TradeStationClient
from tradestation import (
    TradeStationAPIError,
    TradeStationAuthError,
    TradeStationRateLimitError,
    TradeStationValidationError,
    TradeStationNetworkError
)

async def handle_with_care():
    client = TradeStationClient()
    
    try:
        quotes = await client.market_data.get_quotes("AAPL,MSFT")
        print(f"Success! Got quotes for {len(quotes)} symbols")
        
    except TradeStationAuthError as e:
        print(f"Authentication failed: {e}")
        # Handle credential refresh or re-login
        
    except TradeStationRateLimitError as e:
        print(f"Rate limit hit: {e}")
        if hasattr(e, 'retry_after') and e.retry_after:
            print(f"Try again in {e.retry_after} seconds")
            
    except TradeStationValidationError as e:
        print(f"Invalid request: {e}")
        if e.validation_errors:
            print(f"Validation details: {e.validation_errors}")
            
    except TradeStationNetworkError as e:
        print(f"Network issue: {e}")
        # Implement retry with backoff
        
    except TradeStationAPIError as e:
        # Catch-all for any other API errors
        print(f"API error: {e}")
        if e.status_code:
            print(f"Status code: {e.status_code}")
        if e.request_id:
            print(f"Request ID: {e.request_id}")
```

### Implementing Retries

For transient errors like rate limits, network issues, or server errors, you might want to implement retry logic:

```python
import asyncio
import random

async def retry_with_backoff(func, max_attempts=3):
    attempt = 0
    while attempt < max_attempts:
        try:
            return await func()
        except (TradeStationRateLimitError, TradeStationNetworkError, 
                TradeStationServerError, TradeStationTimeoutError) as e:
            attempt += 1
            if attempt >= max_attempts:
                raise  # Re-raise if we've hit max attempts
                
            # Calculate backoff delay (with jitter)
            if isinstance(e, TradeStationRateLimitError) and e.retry_after:
                delay = e.retry_after
            else:
                # Exponential backoff with jitter
                delay = (2 ** attempt) * (0.5 + 0.5 * random.random())
                
            print(f"Retrying in {delay:.2f} seconds...")
            await asyncio.sleep(delay)
```

For a complete error handling example, check out the `examples/QuickStart/error_handling.py` file.

## Logging In (Authentication) 🔒

The library needs your API keys to talk to TradeStation. The easiest way is the `.env` file (shown in Quick Start).

### OAuth Client Types

The library supports both **public** and **confidential** OAuth clients:
- **Public clients** (default): No client secret needed - just provide `CLIENT_ID` and `REFRESH_TOKEN`
- **Confidential clients**: Require a `CLIENT_SECRET` for enhanced security in server-side applications

Other ways to provide credentials:

1.  **Environment Variables:** Set `CLIENT_ID`, `REFRESH_TOKEN`, `ENVIRONMENT` (and optionally `CLIENT_SECRET`) directly in your system.
2.  **Python Dictionary:**
    ```python
    # Public client (no secret)
    client = TradeStationClient({
        "client_id": "your_id",
        "refresh_token": "your_token",
        "environment": "Simulation"
    })
    
    # Confidential client (with secret)
    client = TradeStationClient({
        "client_id": "your_id",
        "client_secret": "your_secret",  # Optional - only for confidential clients
        "refresh_token": "your_token",
        "environment": "Simulation"
    })
    ```
3.  **Direct Parameters:**
    ```python
    client = TradeStationClient(
        refresh_token="your_token",
        environment="Live" # CLIENT_ID and CLIENT_SECRET (if needed) can be in env or config
    )
    ```

See [Authentication Guide](docs/authentication.md) for the full scoop on public vs. confidential clients.

## Dive Deeper (Documentation) 📚

Ready for more details?

*   [🚀 Quick Start Guide](https://github.com/mxcoppell/tradestation-api-python/blob/main/docs/quick_start.md)
*   [🔑 Authentication](https://github.com/mxcoppell/tradestation-api-python/blob/main/docs/authentication.md)
*   [📊 Market Data](https://github.com/mxcoppell/tradestation-api-python/blob/main/docs/market_data.md)
*   [💼 Brokerage](https://github.com/mxcoppell/tradestation-api-python/blob/main/docs/brokerage.md)
*   [📈 Order Execution](https://github.com/mxcoppell/tradestation-api-python/blob/main/docs/order_execution.md)
*   [⚡ Streaming Data](https://github.com/mxcoppell/tradestation-api-python/blob/main/docs/streaming.md)
*   [🚦 Rate Limiting](https://github.com/mxcoppell/tradestation-api-python/blob/main/docs/rate_limiting.md)
*   [🛡️ Error Handling](https://github.com/mxcoppell/tradestation-api-python/blob/main/docs/error_handling.md)

## Contributing 🤝

Got ideas or found a bug? Feel free to open an issue or submit a pull request!

## License 📜

This project is licensed under the MIT License - see the LICENSE file for details.

---

Happy Trading! 🎉 