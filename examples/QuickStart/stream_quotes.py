import os
import asyncio
import signal
import json
from dotenv import load_dotenv
from tradestation.client import TradeStationClient

# Load environment variables from .env file (default)
load_dotenv()

"""
This example demonstrates how to:
1. Set up a TradeStation client with proper authentication
2. Create a real-time streaming connection for quotes using HTTP SSE
3. Process and display the streaming data line by line
4. Handle the cancellation and cleanup

Required environment variables (.env):
- CLIENT_ID: Your TradeStation API client ID (Mandatory)
- REFRESH_TOKEN: Your TradeStation refresh token (Mandatory)
- ENVIRONMENT: 'Simulation' or 'Live' (Mandatory)
"""

# Flag to indicate if we're still running
running = True


def handle_signal(sig, frame):
    """Handle interrupt signals to gracefully exit the program."""
    global running
    print("\nReceived signal to stop streaming. Closing...")
    running = False


# Set up signal handling for clean exit on Ctrl+C
signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)


async def process_quote(data):
    """Process and display a quote update."""
    # Format and display the quote update
    symbol = data.get("Symbol", "N/A")
    last = data.get("Last", "N/A")
    bid = data.get("Bid", "N/A")  # Correct field name is Bid
    ask = data.get("Ask", "N/A")  # Correct field name is Ask
    net_change = data.get("NetChange", "N/A")

    # Color the change based on whether it's positive or negative
    change_str = ""
    if net_change != "N/A":
        try:
            change_val = float(net_change)
            if change_val > 0:
                change_str = f"+{net_change}"
            else:
                change_str = f"{net_change}"
        except ValueError:
            change_str = net_change  # Keep original string if conversion fails

    print(f"{symbol:<6} Last: {last:<8} Bid: {bid:<8} Ask: {ask:<8} Change: {change_str}")


async def main():
    global running  # Declare access to the global flag
    client = None
    stream_reader = None

    try:
        # Initialize the TradeStation client
        client = TradeStationClient()

        # Define symbols to stream quotes for
        symbols = ["AAPL", "MSFT", "GOOG"]
        symbols_str = ",".join(symbols)

        print(f"Starting quote stream for {symbols_str}...")
        print("Press Ctrl+C to stop streaming\n")

        # Use the correct market_data service method to get the stream reader
        stream_reader = await client.market_data.stream_quotes(symbols_str)

        # Process the stream line by line
        while running:
            try:
                # Read a line from the stream with a timeout to allow checking the running flag
                line = await asyncio.wait_for(stream_reader.readline(), timeout=1.0)

                if not line:
                    print("Stream closed by server.")
                    break

                line_str = line.strip().decode("utf-8")  # Decode bytes to string

                if not line_str:  # Skip empty lines
                    continue

                try:
                    # Parse the JSON data from the line
                    data = json.loads(line_str)

                    # Process based on data type
                    if "Symbol" in data and "Last" in data:  # Likely a quote update
                        await process_quote(data)
                    elif "Heartbeat" in data:  # Handle heartbeat
                        print(f"Heartbeat received: {data['Timestamp']}")
                    elif "Error" in data:  # Handle stream errors
                        print(f"Stream Error: {data['Message']} ({data['Error']})")
                        if data["Error"] == "GoAway":  # Stop if server indicates shutdown
                            running = False
                    else:
                        print(f"Unknown data format: {data}")

                except json.JSONDecodeError:
                    print(f"Received non-JSON line: {line_str}")

            except asyncio.TimeoutError:
                # Timeout occurred, loop continues to check `running` flag
                continue
            except Exception as inner_error:
                # Handle errors during line processing
                print(f"Error processing stream line: {str(inner_error)}")
                # Optionally, break or implement retry logic
                break

    except Exception as error:
        # Handle any errors that occur during setup or overall streaming
        print(f"Stream setup error: {str(error)}")
        import traceback

        print(f"Stack trace: {traceback.format_exc()}")
    finally:
        # Clean up resources
        print("\nCleaning up resources...")
        # StreamReader doesn't have an explicit close, rely on HttpClient.close()
        if client:
            await client.http_client.close()
        print("Done!")


# Run the example
if __name__ == "__main__":
    asyncio.run(main())
