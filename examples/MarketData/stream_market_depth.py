#!/usr/bin/env python
"""
Example demonstrating how to stream real-time market depth data (Level II)
using the TradeStation API Python wrapper.

This example shows how to:
1. Connect to the TradeStation API and authenticate
2. Stream Level II market depth for MSFT
3. Process the incoming market depth updates (Bids/Asks) and heartbeats using StreamReader
"""

import asyncio
import signal
import json
from dotenv import load_dotenv
from src.client.tradestation_client import TradeStationClient

# Load environment variables from .env file
load_dotenv()

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


async def handle_market_depth_data(data):
    """Processes and prints the market depth data."""
    if "Symbol" in data:
        print("\nMarket Depth Update:")
        print(f"Symbol: {data['Symbol']}")
        if "Bids" in data and data["Bids"]:
            print("Bids:")
            for bid in data["Bids"]:
                print(f"  Price: {bid['Price']}, Size: {bid['Size']}, Time: {bid['Time']}")
        if "Asks" in data and data["Asks"]:
            print("Asks:")
            for ask in data["Asks"]:
                print(f"  Price: {ask['Price']}, Size: {ask['Size']}, Time: {ask['Time']}")
        print("---")
    elif "Heartbeat" in data:
        print(f"Heartbeat: {data['Timestamp']}")
    else:
        print(f"Error/Unknown: {data}")


async def main():
    """Run the example to demonstrate streaming market depth data with StreamReader."""
    global running
    client = None
    stream_reader = None

    try:
        # Initialize the TradeStation client
        client = TradeStationClient()

        # Define the symbol for the market depth stream
        symbol = "MSFT"

        print(f"\nStreaming Market Depth (Level II) for {symbol} using SSE:")
        print("Press Ctrl+C to stop streaming\n")

        # Get the StreamReader for the market depth stream
        stream_reader = await client.market_data.stream_market_depth_quotes(symbol)

        # Process the stream line by line
        while running:
            try:
                # Read a line from the stream with a timeout
                line = await asyncio.wait_for(stream_reader.readline(), timeout=1.0)

                if not line:
                    print("Stream closed by server.")
                    break

                line_str = line.strip().decode("utf-8")  # Decode bytes to string

                if not line_str:  # Skip empty lines
                    continue

                # SSE streams often send 'data: ' prefix, remove it if present
                if line_str.startswith("data: "):
                    line_str = line_str[len("data: ") :]

                # Skip lines that are just event types like 'event: HeartBeat'
                if line_str.startswith("event:"):
                    continue

                try:
                    # Parse the JSON data from the line
                    data = json.loads(line_str)
                    await handle_market_depth_data(data)

                except json.JSONDecodeError:
                    # Sometimes heartbeats might not be JSON, handle gracefully
                    if "Heartbeat" in line_str:
                        # Assuming heartbeat format might be simpler or just text
                        # For now, just print it if it's not JSON
                        print(f"Received non-JSON heartbeat line: {line_str}")
                    else:
                        print(f"Received non-JSON line: {line_str}")

            except asyncio.TimeoutError:
                # Timeout occurred, loop continues to check `running` flag
                continue
            except Exception as inner_error:
                print(f"Error processing stream line: {str(inner_error)}")
                import traceback

                traceback.print_exc()
                break

    except Exception as error:
        print(f"Stream setup error: {error}")
        import traceback

        traceback.print_exc()
    finally:
        print("\nCleaning up resources...")
        if client:
            # HttpClient.close() handles closing the session and implicitly the stream reader
            await client.http_client.close()
        print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
