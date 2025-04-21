# Let's Get Started! 🚀

This guide will zip you through setting up the TradeStation API Python Wrapper. No sweat!

## Step 1: Installation

You have two easy options to get the TradeStation API Python Wrapper:

### Option A: Install from PyPI (Recommended)

The easiest way to get started is by installing the package directly from PyPI:

```bash
pip install tradestation-api-python
```

### Option B: Get the Source Code

If you'd like to contribute or modify the code:

```bash
# Clone the project
git clone https://github.com/mxcoppell/tradestation-api-python.git
# Hop into the new directory
cd tradestation-api-python
```

## Step 2: Install Dependencies (If using Option B)

If you cloned the repository, install the necessary Python packages. We recommend using Poetry:

```bash
# Let Poetry work its magic
poetry install
```

If you prefer pip, that works too:

```bash
# Or use pip if that's your jam
pip install -e .
```

✨ Ta-da! Installation complete. ✨

## Step 3: Your Secret Keys 🔑

The API needs to know who you are. Let's set up your credentials securely.

1.  **Copy the Sample:** Find the `.env.sample` file in the project folder and make a copy named `.env`:
    ```bash
    cp .env.sample .env
    ```
2.  **Fill in the Blanks:** Open the new `.env` file with your favorite text editor. You'll need to add your details from the [TradeStation Developer Portal](https://developer.tradestation.com/):
    ```dotenv
    # Mandatory stuff!
    CLIENT_ID=your_super_secret_client_id
    REFRESH_TOKEN=your_very_secret_refresh_token
    ENVIRONMENT=Simulation # Use 'Simulation' to practice, 'Live' for real trading!
    ```
    **Important:** Keep this `.env` file private! Don't commit it to Git.

## Let's Code! Basic Examples

Time for the fun part – making things happen!

### Creating Your API Client

Think of this as your remote control for TradeStation.

```python
import asyncio
from dotenv import load_dotenv
from tradestation.client.tradestation_client import TradeStationClient

# This loads the secrets from your .env file
load_dotenv()

# Create the client - it magically finds your .env settings! 🪄
client = TradeStationClient()

# You *can* also set things directly, but .env is usually easier:
# client = TradeStationClient(
#     refresh_token="your_refresh_token",
#     environment="Simulation"
# )

print("Client created! Ready to connect to TradeStation.")

# Remember to close the client when you're all done
# We'll show this in the examples below
```

### Asking for Prices (Quote Snapshots)

Want to know the latest price for a stock (or a few)?

```python
# (Keep the imports and load_dotenv() from the previous example)

async def get_some_quotes():
    print("\n--- Getting Stock Quotes ---")
    client = TradeStationClient() # Creates a new client instance
    try:
        # Pick your stocks!
        symbols = ["AAPL", "MSFT", "GOOGL"]
        symbols_str = ",".join(symbols)
        print(f"Asking for prices for: {symbols_str}")

        # Make the API call using the client
        quotes_response = await client.market_data.get_quote_snapshots(symbols_str)

        # Basic error check
        if hasattr(quotes_response, "Errors") and quotes_response.Errors:
            print(f"Oops! Error getting quotes: {quotes_response.Errors}")
            return

        if not quotes_response.Quotes:
            print("Hmm, didn't get any quotes back.")
            return

        # Let's make the output pretty!
        print("\nSymbol   Last      Bid       Ask       Change     Volume")
        print("--------------------------------------------------------------")
        for quote in quotes_response.Quotes:
            # Safely get attributes, providing 'N/A' if missing
            symbol = getattr(quote, 'Symbol', 'N/A')
            last = getattr(quote, 'Last', 'N/A')
            bid = getattr(quote, 'Bid', 'N/A')
            ask = getattr(quote, 'Ask', 'N/A')
            change = getattr(quote, 'NetChange', 'N/A')
            volume = getattr(quote, 'Volume', 'N/A')

            # Nicely format the change (+/-)
            change_str = "N/A"
            if change != 'N/A':
                try:
                    change_val = float(change)
                    change_str = f"{change_val:+.2f}" # Shows + sign
                except ValueError:
                    change_str = change # Keep original if not a number

            print(f"{symbol:<8} {last:<9} {bid:<9} {ask:<9} {change_str:<10} {volume}")

    except Exception as e:
        print(f"Something went wrong: {e}")
    finally:
        print("Closing the client connection.")
        await client.close()

if __name__ == "__main__":
    asyncio.run(get_some_quotes())

```

### Checking Your Account(s)

See what accounts you have access to.

```python
# (Keep the imports and load_dotenv())

async def check_accounts():
    print("\n--- Checking Accounts ---")
    client = TradeStationClient()
    try:
        accounts_response = await client.brokerage.get_accounts()

        if not accounts_response.Accounts:
            print("No accounts found.")
            return

        print(f"Found {len(accounts_response.Accounts)} account(s):")
        for account in accounts_response.Accounts:
            print("------------------------------")
            print(f" ID:     {account.AccountID}")
            print(f" Name:   {getattr(account, 'Alias', 'N/A')}") # Use getattr for safety
            print(f" Type:   {account.AccountType}")
            print(f" Status: {account.Status}")

        # Let's peek at the balances for the first account
        first_account_id = accounts_response.Accounts[0].AccountID
        print(f"\nFetching balances for account {first_account_id}...")
        balances_response = await client.brokerage.get_balances(first_account_id)

        # Displaying the first balance entry for simplicity
        if balances_response.Balances:
            balance = balances_response.Balances[0]
            print(f" Cash Balance: ${balance.CashBalance}")
            print(f" Buying Power: ${balance.BuyingPower}")
        else:
            print("No balance information found.")

    except Exception as e:
        print(f"Something went wrong: {e}")
    finally:
        print("Closing the client connection.")
        await client.close()

if __name__ == "__main__":
    asyncio.run(check_accounts())
```

### Time Traveling for Prices (Historical Data)

Get past price data (like daily or minute bars).

```python
# (Keep imports, load_dotenv())
from datetime import datetime, timedelta

async def get_history():
    print("\n--- Getting Historical Bars ---")
    client = TradeStationClient()
    try:
        # Example: Get daily bars for SPY for the last 5 trading days
        print("Fetching last 5 daily bars for SPY...")
        daily_bars_response = await client.market_data.get_bar_history("SPY", {
            "unit": "Daily",
            "barsback": 5
        })

        if daily_bars_response.Bars:
            print("Date        Open    Close   Volume")
            print("-------------------------------------")
            for bar in daily_bars_response.Bars:
                # Format the timestamp nicely
                dt_obj = datetime.fromisoformat(bar.TimeStamp.replace("Z", "+00:00"))
                date_str = dt_obj.strftime("%Y-%m-%d")
                # Format volume with commas
                volume_str = f"{int(float(bar.TotalVolume)):,}"
                print(f"{date_str}  {bar.Open:<7} {bar.Close:<7} {volume_str}")
        else:
            print("Could not retrieve daily bars.")

        # Example: Get 1-minute bars for AAPL for a small window yesterday
        # (Note: Adjust times based on market hours and data availability)
        # yesterday = datetime.now() - timedelta(days=1)
        # start_time = yesterday.strftime("%Y-%m-%dT14:30:00Z") # ~9:30 AM ET in UTC
        # end_time = yesterday.strftime("%Y-%m-%dT14:35:00Z")   # ~9:35 AM ET in UTC
        # print(f"\nFetching 1-min bars for AAPL between {start_time} and {end_time}...")
        # minute_bars = await client.market_data.get_bar_history("AAPL", {
        #     "unit": "Minute",
        #     "interval": "1",
        #     "firstdate": start_time,
        #     "lastdate": end_time,
        # })
        # print(f"Retrieved {len(minute_bars.Bars)} 1-minute bars.")

    except Exception as e:
        print(f"Something went wrong: {e}")
    finally:
        print("Closing the client connection.")
        await client.close()

if __name__ == "__main__":
    asyncio.run(get_history())
```

### Live Action Prices! (Streaming)

Want prices updated *instantly*? Let's stream!

```python
# (Keep imports, load_dotenv())
import signal
import json

# --- Signal Handling (for stopping gently) ---
running = True # Our loop controller
def stop_running(sig, frame):
    global running
    print("\nSignal caught! Telling the stream to stop...")
    running = False
signal.signal(signal.SIGINT, stop_running) # Catch Ctrl+C
signal.signal(signal.SIGTERM, stop_running)
# ---------------------------------------------

async def process_live_quote(quote_data):
    """This function gets called for each new quote."""
    symbol = quote_data.get("Symbol", "N/A")
    last = quote_data.get("Last", "N/A")
    print(f"--> {symbol}: {last}") # Simple print for the example

async def stream_some_quotes():
    global running
    print("\n--- Streaming Live Quotes ---")
    client = None
    stream_reader = None

    try:
        client = TradeStationClient()
        symbols = ["AAPL", "MSFT"]
        symbols_str = ",".join(symbols)
        print(f"Starting stream for: {symbols_str}. Press Ctrl+C to stop.")

        # Get the stream reader object
        stream_reader = await client.market_data.stream_quotes(symbols_str)

        # Loop until 'running' becomes False (e.g., by Ctrl+C)
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
                    if "Symbol" in data: # It's likely a quote
                        await process_live_quote(data)
                    # Add checks for Heartbeat or Error messages if needed
                except json.JSONDecodeError:
                    # print(f"Non-JSON line: {line_str}") # Optional: Log non-JSON
                    pass # Ignore non-JSON lines for this example

            except asyncio.TimeoutError:
                # Just means no data in the last second, loop again to check 'running'
                continue
            except Exception as e:
                if running: print(f"Error during stream: {e}")
                running = False # Stop on errors

    except Exception as e:
        print(f"Error setting up stream: {e}")
    finally:
        print("\nCleaning up stream resources...")
        if client:
            await client.close() # Close client (also handles stream closure)
        print("Stream stopped.")

if __name__ == "__main__":
    asyncio.run(stream_some_quotes())
```

### Let's (Almost) Place an Order! ⚠️

Ready to buy or sell? Here's how you *would* structure an order.
**Warning:** The actual sending part is commented out by default to prevent accidents!

```python
# (Keep imports, load_dotenv())

async def prepare_an_order():
    print("\n--- Preparing a Sample Order (Not Sending!) ---")
    client = TradeStationClient()
    try:
        # First, find an account ID to use
        accounts = await client.brokerage.get_accounts()
        if not accounts.Accounts:
            print("Can't place an order without an account!")
            return
        account_id = accounts.Accounts[0].AccountID
        print(f"Using Account ID: {account_id}")

        # Build the order details
        order_details = {
            "AccountID": account_id,
            "Symbol": "AAPL",
            "Quantity": 1,          # Buy 1 share
            "OrderType": "Market",  # At the current market price
            "TradeAction": "BUY",   # We want to buy
            "TimeInForce": {
                "Duration": "DAY"   # Good for today's trading session
            },
            "Route": "Intelligent" # Let TradeStation choose the best route
        }

        print("\nOrder we would send:")
        print(json.dumps(order_details, indent=2))

        # --- !!! DANGER ZONE !!! --- #
        # Uncomment the block below ONLY if you want to send a REAL order!
        '''
        print("\nSENDING ORDER NOW!")
        order_confirmation = await client.order_execution.place_order(order_details)
        print("Order Sent! Confirmation:")
        if order_confirmation.Orders:
            print(f" Order ID: {order_confirmation.Orders[0].OrderID}")
        else:
            print(json.dumps(order_confirmation, indent=2))
        '''
        # --- !!! END DANGER ZONE !!! --- #

    except Exception as e:
        print(f"Something went wrong: {e}")
    finally:
        print("Closing the client connection.")
        await client.close()

if __name__ == "__main__":
    asyncio.run(prepare_an_order())
```

## What's Next? 🤔

You've got the basics! Now you can explore more:

*   **Deeper Market Data:** Options chains, Level II data, time & sales...
*   **Order Superpowers:** Change orders, cancel them, use fancy order types.
*   **Portfolio Power:** Keep track of your positions and performance.
*   **Become a Stream Master:** Stream bars, order updates, account changes.
*   **Build Your Bot:** Create your own automated trading strategies!

## Uh Oh? Quick Fixes! 😵‍💫

Running into trouble? Check these common culprits:

*   **Auth Annoyances:**
    *   Double-check your Client ID in `.env`.
    *   Is your Refresh Token still valid? They can expire!
    *   Did you give your API key the right permissions on the dev portal?
*   **Hitting the Limit (Rate Limiting):**
    *   The client tries to be polite, but if you see errors, try asking for more data in one go (like multiple symbols at once).
    *   Maybe cache data you ask for often.
*   **Connection Chaos:**
    *   Is your internet okay?
    *   Is TradeStation's API having a nap? (Check their status page if available).
    *   Are you using the right `ENVIRONMENT` (`Live` or `Simulation`) in your `.env` file?

## More Code Adventures! 🗺️

Want more examples? Head over to the `examples/` directory in the project:

*   `examples/QuickStart`: You'll find the code used in this guide here!
*   Look for other folders like `examples/MarketData`, `examples/Brokerage`, etc. (if they exist) for more focused examples.

Happy Coding! 🎉 