#!/usr/bin/env python
"""
Example demonstrating how to stream real-time bar data using the TradeStation API Python wrapper.

This example shows how to:
1. Connect to the TradeStation API and authenticate
2. Stream 1-minute bars for MSFT including pre and post market data
3. Process the incoming bar data and heartbeats using StreamReader
"""

import asyncio
import json
import signal

from dotenv import load_dotenv

from tradestation.client import TradeStationClient

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


async def handle_bar_data(data):
    """Processes and prints the bar data."""
    if "TimeStamp" in data:
        print("\nNew Bar:")
        print(f"Time: {data['TimeStamp']}")
        print(f"Open: {data['Open']}")
        print(f"High: {data['High']}")
        print(f"Low: {data['Low']}")
        print(f"Close: {data['Close']}")
        print(f"Volume: {data['TotalVolume']}")
        print("---")
    elif "Heartbeat" in data:
        print(f"Heartbeat: {data['Timestamp']}")
    else:
        print(f"Error: {data.get('Message', 'Unknown error')}")


async def main():
    """Run the example to demonstrate streaming bars data with StreamReader."""
    global running
    client = None
    stream_reader = None

    try:
        # Initialize the TradeStation client
        client = TradeStationClient()

        # Define the parameters for the 1-minute bars
        symbol = "MSFT"
        params = {
            "unit": "Minute",
            "interval": "1",
            "sessiontemplate": "USEQPreAndPost",  # Include pre and post market data
        }

        print(f"\nStreaming 1-Minute Bars for {symbol} using SSE:")
        print("Press Ctrl+C to stop streaming\n")

        # Get the StreamReader for the bars stream
        stream_reader = await client.market_data.stream_bars(symbol, params)

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

                try:
                    # Parse the JSON data from the line
                    data = json.loads(line_str)
                    await handle_bar_data(data)

                except json.JSONDecodeError:
                    print(f"Received non-JSON line: {line_str}")

            except asyncio.TimeoutError:
                # Timeout occurred, loop continues to check `running` flag
                continue
            except Exception as inner_error:
                print(f"Error processing stream line: {str(inner_error)}")
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
