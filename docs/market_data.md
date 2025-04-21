# Market Data Service 📊

This service provides access to real-time and historical market data, including quotes, price bars, options data, and symbol information.

## Setup

First, ensure you have an initialized `TradeStationClient`:

```python
import asyncio
from dotenv import load_dotenv
from tradestation.client import TradeStationClient

# Load environment variables
load_dotenv()

# Create the client
client = TradeStationClient()

# Access the market data service
market_data = client.market_data

# --- Your code using market_data methods goes here ---

# Remember to close the client when finished
async def main():
    # ... use market_data methods ...
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Methods

### `get_symbol_details(symbols)`

Gets detailed information about one or more symbols.

*   **Parameters:**
    *   `symbols` (`Union[str, List[str]]`): A single symbol string, a comma-separated string of symbols, or a list of symbol strings.
*   **Returns:** `SymbolDetailsResponse` containing details for each symbol and any errors.
*   **Example:** (See `examples/MarketData/get_symbol_details.py`)
    ```python
    details = await market_data.get_symbol_details(["AAPL", "MSFT", "INVALID"])
    for symbol_info in details.Symbols:
        print(f"Symbol: {symbol_info.Name}, Description: {symbol_info.Description}, Type: {symbol_info.AssetType}")
    for error in details.Errors:
        print(f"Error getting details for {error.Symbol}: {error.Error}")
    ```

### `get_crypto_symbol_names()`

Fetches crypto Symbol Names for all available symbols (e.g., BTCUSD, ETHUSD). Note: These symbols cannot be traded via this API.

*   **Parameters:** None
*   **Returns:** `SymbolNames` containing a list of available crypto symbol names.
*   **Example:** (See `examples/MarketData/get_crypto_symbol_names.py`)
    ```python
    crypto_names = await market_data.get_crypto_symbol_names()
    print("Available Crypto Symbols:")
    for symbol in crypto_names.SymbolNames:
        print(f"- {symbol}")
    ```

### `get_quote_snapshots(symbols)`

Fetches a full snapshot of the latest Quote for the given Symbols (up to 100). For realtime updates, use `stream_quotes`.

*   **Parameters:**
    *   `symbols` (`Union[str, List[str]]`): A single symbol string, a comma-separated string of symbols, or a list of symbol strings (max 100).
*   **Returns:** `QuoteSnapshot` containing successful quotes and any errors.
*   **Example:** (See `examples/MarketData/get_quote_snapshots.py`)
    ```python
    snapshot = await market_data.get_quote_snapshots(["MSFT", "BTCUSD"])
    for quote in snapshot.Quotes:
        print(f"{quote.Symbol}: Last={quote.Last}, Bid={quote.Bid}, Ask={quote.Ask}, Volume={quote.Volume}")
    for error in snapshot.Errors:
        print(f"Error getting quote for {error.Symbol}: {error.Error}")
    ```

### `get_option_expirations(underlying, strike_price=None)`

Get the available expiration dates for option contracts on the specified underlying symbol.

*   **Parameters:**
    *   `underlying` (`str`): The symbol for the underlying security (e.g., 'AAPL', 'SPX').
    *   `strike_price` (`Optional[float]`): Optional strike price to filter expirations.
*   **Returns:** `Expirations` containing a list of expiration dates.
*   **Example:** (See `examples/MarketData/get_option_expirations.py`)
    ```python
    expirations = await market_data.get_option_expirations("AAPL")
    print(f"Expirations for AAPL: {expirations.Expirations}")

    expirations_at_strike = await market_data.get_option_expirations("MSFT", strike_price=300.0)
    print(f"Expirations for MSFT at $300 strike: {expirations_at_strike.Expirations}")
    ```

### `get_option_spread_types()`

Fetches all valid spread types for complex option orders.

*   **Parameters:** None
*   **Returns:** `SpreadTypes` containing a list of valid spread type names.
*   **Example:** (See `examples/MarketData/get_option_spreadtypes.py`)
    ```python
    spread_types = await market_data.get_option_spread_types()
    print("Available Option Spread Types:")
    for spread_type in spread_types.SpreadTypes:
        print(f"- {spread_type}")
    ```

### `get_option_strikes(underlying, expiration=None, spread_type=None, options=None)`

Get the available strike prices for option contracts on the specified underlying symbol.

*   **Parameters:**
    *   `underlying` (`str`): The symbol for the underlying security.
    *   `expiration` (`Optional[str]`): Optional expiration date (YYYY-MM-DD) to filter strikes.
    *   `spread_type` (`Optional[str]`): Optional spread type to filter strikes.
    *   `options` (`Optional[Dict[str, str]]`): Optional dictionary for future parameters.
*   **Returns:** `Strikes` containing a list of strike prices.
*   **Example:** (See `examples/MarketData/get_option_strikes.py`)
    ```python
    # Get all strikes for AAPL
    all_strikes = await market_data.get_option_strikes("AAPL")
    print(f"First 10 strikes for AAPL: {all_strikes.Strikes[:10]}")

    # Get strikes for a specific expiration
    expiration_date = "2025-06-20" # Find a valid date first using get_option_expirations
    strikes_for_expiry = await market_data.get_option_strikes("AAPL", expiration=expiration_date)
    print(f"Strikes for AAPL expiring {expiration_date}: {strikes_for_expiry.Strikes}")
    ```

### `get_option_risk_reward(analysis)`

Provides risk/reward analysis for one or more options legs.

*   **Parameters:**
    *   `analysis` (`Union[Dict[str, Any], RiskRewardAnalysisInput]`): A dictionary or `RiskRewardAnalysisInput` object containing the legs for analysis.
*   **Returns:** `RiskRewardAnalysisResult` containing the calculated risk/reward profile.
*   **Example:** (See `examples/MarketData/get_option_risk_reward.py`)
    ```python
    # Define the analysis input (e.g., a single call option leg)
    analysis_input = {
        "Legs": [
            {
                "Symbol": "AAPL",  # Replace with a specific option symbol if needed
                "BuyOrSell": "BUY",
                "Quantity": 1,
                "ExpirationDate": "2025-12-19", # Use valid expiration
                "StrikePrice": 200,
                "OptionType": "CALL"
            }
        ]
    }
    risk_reward = await market_data.get_option_risk_reward(analysis_input)
    print("Risk/Reward Analysis:")
    # Process risk_reward.Profiles, risk_reward.Greeks, etc.
    if risk_reward.Profiles:
      print(f"- Max Profit: {risk_reward.Profiles[0].MaxProfit}")
      print(f"- Max Loss: {risk_reward.Profiles[0].MaxLoss}")
    if risk_reward.Greeks:
      print(f"- Delta: {risk_reward.Greeks[0].Delta}")
      print(f"- Gamma: {risk_reward.Greeks[0].Gamma}")
    ```

### `get_bar_history(symbol, params=None)`

Fetches historical price bars for a specified symbol.

*   **Parameters:**
    *   `symbol` (`str`): The symbol to fetch bars for (e.g., "MSFT", "BTCUSD", "@ES").
    *   `params` (`Optional[Dict[str, Any]]`): A dictionary of parameters to control the bar data:
        *   `interval` (`str`): Bar interval size (e.g., 1, 5, 10, 30). Required.
        *   `unit` (`str`): Bar interval unit ("Minute", "Daily", "Weekly", "Monthly"). Required.
        *   `barsback` (`Optional[int]`): Number of bars to return (max 500).
        *   `firstdate` (`Optional[str]`): Start date/time (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ).
        *   `lastdate` (`Optional[str]`): End date/time (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ).
        *   `sessiontemplate` (`Optional[str]`): Session template (e.g., "USEQPre", "USEQPost", "Default"). Defaults based on symbol type.
*   **Returns:** `BarsResponse` containing the list of bars. Returns empty list if no bars found (e.g., outside market hours).
*   **Example:** (See `examples/MarketData/get_bars.py`)
    ```python
    # Get last 5 daily bars for SPY
    daily_params = {"interval": "1", "unit": "Daily", "barsback": 5}
    daily_bars = await market_data.get_bar_history("SPY", daily_params)
    print("SPY Daily Bars:")
    for bar in daily_bars.Bars:
        print(f"  {bar.TimeStamp}: O={bar.Open} H={bar.High} L={bar.Low} C={bar.Close} V={bar.TotalVolume}")

    # Get 1-minute bars for MSFT for a specific period (adjust dates/times)
    # minute_params = {
    #     "interval": "1", "unit": "Minute",
    #     "firstdate": "2024-04-20T13:30:00Z", # UTC time
    #     "lastdate": "2024-04-20T13:35:00Z"
    # }
    # minute_bars = await market_data.get_bar_history("MSFT", minute_params)
    # print("\nMSFT 1-Minute Bars:")
    # for bar in minute_bars.Bars:
    #     print(f"  {bar.TimeStamp}: Close={bar.Close}")
    ```

---

## Streaming Methods

These methods provide real-time data updates via Server-Sent Events (SSE). You receive an `aiohttp.StreamReader` object to process the incoming data.

**General Streaming Example:**

```python
import asyncio
import json
import signal

# --- Signal Handling (for stopping gently) ---
running = True
def stop_running(sig, frame):
    global running
    print("\nSignal caught! Telling the stream to stop...")
    running = False
signal.signal(signal.SIGINT, stop_running) # Catch Ctrl+C
signal.signal(signal.SIGTERM, stop_running)
# ---------------------------------------------

async def process_stream(stream_reader):
    global running
    print("Starting stream processing. Press Ctrl+C to stop.")
    while running:
        try:
            # Wait for a new line from the stream (max 1 second)
            line = await asyncio.wait_for(stream_reader.readline(), timeout=1.0)
            if not line: # Stream ended
                if running: print("Stream closed unexpectedly.")
                break

            # Decode and try to parse the line as JSON
            line_str = line.strip().decode("utf-8")
            if not line_str: continue # Skip empty lines

            try:
                data = json.loads(line_str)
                # --- Process different message types ---
                if "Symbol" in data and "Last" in data: # Likely a Quote
                    print(f"Quote {data.get('Symbol')}: Last={data.get('Last')}, Bid={data.get('Bid')}, Ask={data.get('Ask')}")
                elif "Timestamp" in data and "Close" in data: # Likely a Bar
                    print(f"Bar {data.get('Symbol')} ({data.get('Interval')}{data.get('Unit')}): Time={data.get('Timestamp')}, Close={data.get('Close')}")
                elif "Heartbeat" in data:
                    print(f"Heartbeat at {data.get('Timestamp')}")
                elif "Error" in data:
                    print(f"Stream Error: {data.get('Message')}")
                # Add more checks for Market Depth, Option Chain data etc.
                else:
                    print(f"Unknown data: {data}") # Log other messages
            except json.JSONDecodeError:
                # print(f"Non-JSON line: {line_str}") # Optional: Log non-JSON
                pass # Ignore non-JSON lines

        except asyncio.TimeoutError:
            continue # No data in the last second, check 'running' again
        except Exception as e:
            if running: print(f"Error during stream: {e}")
            running = False # Stop on errors

async def main_stream():
    client = TradeStationClient()
    stream_reader = None
    try:
        # --- Replace with specific stream method call ---
        # Example: stream_reader = await client.market_data.stream_quotes("AAPL,MSFT")
        stream_reader = await client.market_data.stream_bars("SPY", {"interval": "1", "unit": "Minute"})
        # -----------------------------------------------

        if stream_reader:
            await process_stream(stream_reader)
        else:
            print("Failed to get stream reader.")

    except Exception as e:
        print(f"Error setting up stream: {e}")
    finally:
        print("\nCleaning up stream resources...")
        if client:
            await client.close() # Closes client and associated stream
        print("Stream stopped.")

# if __name__ == "__main__":
#     load_dotenv()
#     asyncio.run(main_stream())
```

### `stream_quotes(symbols)`

Streams Quote changes for one or more symbols (up to 100).

*   **Parameters:**
    *   `symbols` (`Union[str, List[str]]`): Symbols to stream (max 100).
*   **Returns:** `aiohttp.StreamReader` yielding JSON data for `QuoteStream`, `Heartbeat`, or `StreamErrorResponse`.
*   **Example:** (See `examples/MarketData/stream_quotes.py` and general example above)

### `stream_bars(symbol, params=None)`

Streams Bar updates for a specified symbol.

*   **Parameters:**
    *   `symbol` (`str`): The symbol to stream bars for.
    *   `params` (`Optional[Dict[str, Any]]`): Dictionary of parameters:
        *   `interval` (`str`): Bar interval size (e.g., 1, 5). Required.
        *   `unit` (`str`): Bar interval unit ("Minute"). Required.
        *   `sessiontemplate` (`Optional[str]`): Session template (e.g., "USEQPreAndPost"). Defaults based on symbol type.
*   **Returns:** `aiohttp.StreamReader` yielding JSON data for `BarStream`, `Heartbeat`, or `StreamErrorResponse`.
*   **Example:** (See `examples/MarketData/stream_bars.py` and general example above)

### `stream_market_depth_quotes(symbol, params=None)`

Streams Market Depth quote updates (Level II) for a specified symbol.

*   **Parameters:**
    *   `symbol` (`str`): The symbol to stream market depth for.
    *   `params` (`Optional[Dict[str, Any]]`): Dictionary of parameters:
        *   `levels` (`Optional[int]`): Number of depth levels (1-20, default 1).
*   **Returns:** `aiohttp.StreamReader` yielding JSON data for `MarketDepthQuoteStream`, `Heartbeat`, or `StreamErrorResponse`.
*   **Example:** (See `examples/MarketData/stream_market_depth.py`)

### `stream_market_depth_aggregates(symbol, params=None)`

Streams aggregated Market Depth updates for a specified symbol. Provides summed volume at price levels.

*   **Parameters:**
    *   `symbol` (`str`): The symbol to stream aggregated depth for.
    *   `params` (`Optional[Dict[str, Any]]`): Dictionary of parameters:
        *   `levels` (`Optional[int]`): Number of depth levels (1-20, default 1).
*   **Returns:** `aiohttp.StreamReader` yielding JSON data for `MarketDepthAggregateStream`, `Heartbeat`, or `StreamErrorResponse`.
*   **Example:** (See `examples/MarketData/stream_market_depth_aggregates.py`)

### `stream_option_chain(underlying, params=None)`

Streams real-time updates for an entire option chain based on the underlying symbol.

*   **Parameters:**
    *   `underlying` (`str`): The underlying symbol (e.g., "AAPL").
    *   `params` (`Optional[Dict[str, Any]]`): Dictionary of parameters:
        *   `expiration` (`Optional[str]`): Filter by expiration date (YYYY-MM-DD).
        *   `strikePrice` (`Optional[float]`): Filter by strike price.
        *   `optionType` (`Optional[str]`): Filter by "CALL" or "PUT".
        *   `strikeRange` (`Optional[str]`): Filter by strike range ("ITM", "OTM", "NTM", "ALL", default "ALL").
        *   `expirationRange` (`Optional[str]`): Filter by expiration range ("NEAR", "ALL", default "ALL").
        *   `date` (`Optional[str]`): Filter by date (MMDD).
        *   `month` (`Optional[str]`): Filter by month (e.g., "JAN").
        *   `year` (`Optional[str]`): Filter by year (YY).
        *   `root` (`Optional[str]`): Filter by option root.
*   **Returns:** `aiohttp.StreamReader` yielding JSON data for `OptionChainQuoteStream`, `Heartbeat`, or `StreamErrorResponse`.
*   **Example:** (See `examples/MarketData/stream_option_chain.py`)

### `stream_option_quotes(params)`

Streams Quote changes for specific option contracts defined by legs.

*   **Parameters:**
    *   `params` (`OptionQuoteParams`): An `OptionQuoteParams` object specifying the option legs to stream. Each leg requires `Symbol`, `BuyOrSell`, `Quantity`, `ExpirationDate`, `StrikePrice`, and `OptionType`.
*   **Returns:** `aiohttp.StreamReader` yielding JSON data for `OptionQuoteStream`, `Heartbeat`, or `StreamErrorResponse`.
*   **Example:** (See `examples/MarketData/stream_option_quotes.py`) 