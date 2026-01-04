import asyncio
import json
import os
import signal

from dotenv import load_dotenv

from tradestation.client import TradeStationClient

# Load environment variables from .env file (default)
load_dotenv()

"""
Market Data Example: Stream Quotes
-----------------------------------

This script demonstrates how to establish a real-time stream for quote updates
for specified symbols using the TradeStation API via the `tradestation-api-python` library.

Functionality Demonstrated:
1. Initialization of the TradeStationClient.
2. Using the `market_data.stream_quotes` method to get an SSE stream reader.
3. Asynchronously reading and processing Server-Sent Events (SSE) line by line.
4. Parsing JSON data received from the stream.
5. Handling different message types (Quote, Heartbeat, Error).
6. Graceful shutdown using signal handling (Ctrl+C).
7. Proper resource cleanup.

Requirements:
- A valid `.env` file in the project root with:
    - `CLIENT_ID`: Your TradeStation Application Key.
    - `REFRESH_TOKEN`: Your TradeStation Refresh Token.
    - `ENVIRONMENT`: Either 'Simulation' or 'Live'.

Usage:
Run this script from the project root directory:
`poetry run python examples/MarketData/stream_quotes.py`

Note: Ensure your environment variables are correctly set before running.
"""

# Global flag to control the main loop, allowing for graceful shutdown
running = True


def handle_signal(sig, frame):
    """Signal handler to initiate graceful shutdown."""
    global running
    print("Interrupt signal received. Stopping stream...")
    running = False


# Register the signal handler for SIGINT (Ctrl+C) and SIGTERM
signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)


async def process_quote_update(data):
    """Processes and prints a single quote update from the stream."""
    # Extract relevant fields from the quote data
    symbol = data.get("Symbol", "N/A")
    last = data.get("Last", "N/A")
    bid = data.get("Bid", "N/A")
    ask = data.get("Ask", "N/A")
    net_change = data.get("NetChange", "N/A")

    # Format NetChange for display
    change_str = net_change
    try:
        change_val = float(net_change)
        if change_val > 0:
            change_str = f"+{net_change}"  # Add '+' for positive changes
    except (ValueError, TypeError):
        pass  # Keep original string if conversion fails or value is None

    print(f"{symbol:<7} | Last: {last:<9} | Bid: {bid:<9} | Ask: {ask:<9} | Change: {change_str}")


async def main():
    """Main function to set up and run the quote stream."""
    global running
    client = None
    stream_reader = None

    try:
        # --- Step 1: Initialize the Client ---
        # The client handles authentication and provides access to API services.
        client = TradeStationClient()
        print("TradeStation Client Initialized.")

        # --- Step 2: Define Symbols and Start Stream ---
        # Define the stock symbols for which to stream quotes.
        symbols_to_stream = ["MSFT", "AAPL", "GOOG", "TSLA"]
        symbols_param = ",".join(symbols_to_stream)

        print(f"Attempting to stream quotes for: {symbols_param}")
        print("Press Ctrl+C to stop.")

        # Request the stream reader from the MarketData service.
        # This initiates the SSE connection.
        stream_reader = await client.market_data.stream_quotes(symbols_param)
        print("Quote stream connection established. Waiting for data...")
        print("Symbol  | Last      | Bid       | Ask       | Change")
        print("--------|-----------|-----------|-----------|---------")

        # --- Step 3: Process the Stream ---
        # Loop indefinitely, reading and processing data line by line.
        while running:
            try:
                # Read one line from the stream with a timeout.
                # The timeout prevents blocking indefinitely and allows checking the `running` flag.
                line = await asyncio.wait_for(stream_reader.readline(), timeout=1.0)

                # If the line is empty, the server might have closed the connection.
                if not line:
                    print("Stream connection closed by server.")
                    running = False
                    break

                # Decode the raw bytes into a UTF-8 string and remove leading/trailing whitespace.
                line_str = line.strip().decode("utf-8")

                # Skip empty lines that might occur.
                if not line_str:
                    continue

                # --- Step 4: Parse and Handle Data ---
                try:
                    # Attempt to parse the line as JSON.
                    data = json.loads(line_str)

                    # Handle different message types based on expected keys.
                    if "Symbol" in data and "Last" in data:
                        # Process regular quote updates.
                        await process_quote_update(data)
                    elif "Heartbeat" in data:
                        # Process heartbeat messages to keep the connection alive.
                        print(f"Heartbeat received: {data.get('Timestamp', 'N/A')}")
                        # pass # Often noisy, uncomment to see heartbeats
                    elif "Error" in data:
                        # Process error messages sent through the stream.
                        error_msg = data.get("Message", "Unknown error")
                        error_code = data.get("Error", "N/A")
                        print(f"Stream Error Received: {error_msg} (Code: {error_code})")
                        # If the server sends a 'GoAway' error, stop the stream.
                        if error_code == "GoAway":
                            print("Server requested disconnection (GoAway). Stopping stream.")
                            running = False
                    else:
                        # Handle any unrecognized data format.
                        print(f"Received unknown data format: {line_str}")

                except json.JSONDecodeError:
                    # Handle lines that are not valid JSON.
                    print(f"Received non-JSON line from stream: {line_str}")
                except Exception as proc_err:
                    print(f"Error processing data line: {proc_err}")
                    # Decide whether to continue or stop based on the error
                    # running = False # Optionally stop on processing errors

            except asyncio.TimeoutError:
                # This is expected when no data is received within the timeout period.
                # Continue the loop to check the `running` flag again.
                continue
            except ConnectionError as conn_err:
                print(f"Stream connection error: {conn_err}")
                running = False  # Stop if the connection is lost
            except Exception as read_err:
                # Handle unexpected errors during stream reading.
                print(f"Unexpected error reading stream: {read_err}")
                running = False
                break  # Exit the loop on critical read errors

    except Exception as setup_error:
        # Handle errors during the initial setup (client init, stream request).
        print(f"Error setting up the quote stream: {setup_error}")
        import traceback

        print(f"Traceback: {traceback.format_exc()}")
    finally:
        # --- Step 5: Cleanup ---
        # This block ensures resources are released even if errors occur.
        print("Initiating cleanup...")
        # The stream_reader itself doesn't need explicit closing with aiohttp's SSEClient.
        # Closing the underlying HttpClient handles the connection closure.
        if client and client.http_client:
            await client.http_client.close()
            print("HTTP Client closed.")
        else:
            print("No active HTTP Client to close.")
        print("Cleanup complete. Exiting.")


# --- Entry Point ---
if __name__ == "__main__":
    # Run the asynchronous main function using asyncio's event loop runner.
    asyncio.run(main())
