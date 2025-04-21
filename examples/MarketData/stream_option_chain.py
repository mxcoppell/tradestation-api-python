#!/usr/bin/env python
"""
Example demonstrating how to stream option chain data using the TradeStation API Python wrapper.

This example shows how to:
1. Connect to the TradeStation API and authenticate
2. Retrieve available option expirations for a symbol
3. Stream real-time option chain updates using Server-Sent Events (SSE)
4. Process and display incoming option chain data and heartbeats
"""

import asyncio
import signal
import json
from dotenv import load_dotenv
from tradestation.client.tradestation_client import TradeStationClient

# Load environment variables from .env file
load_dotenv()

# Flag to indicate if the example is still running
running = True


def handle_signal(sig, frame):
    """Handle interrupt signals to gracefully stop streaming."""
    global running
    print("\nReceived signal to stop streaming. Closing...")
    running = False


# Register signal handlers for Ctrl+C and termination
signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)


async def handle_chain_data(data: dict):
    """Processes and prints option chain data or heartbeats."""
    if "Delta" in data:
        print("\nOption Update:")
        print(f"Strikes: {data['Strikes']}")
        print(f"Side: {data['Side']}")
        print(f"Last: {data['Last']}")
        print(f"Bid: {data['Bid']}")
        print(f"Ask: {data['Ask']}")
        print(f"Volume: {data['Volume']}")
        print(f"Open Interest: {data['DailyOpenInterest']}")
        print("\nGreeks:")
        print(f"  Delta: {data['Delta']}")
        print(f"  Gamma: {data['Gamma']}")
        print(f"  Theta: {data['Theta']}")
        print(f"  Vega: {data['Vega']}")
        print(f"  Rho: {data['Rho']}")
        print("\nProbabilities:")
        print(f"  ITM: {data['ProbabilityITM']}")
        print(f"  OTM: {data['ProbabilityOTM']}")
        print(f"  BE: {data['ProbabilityBE']}")
        print("-" * 60)
    elif "Heartbeat" in data:
        print(f"Heartbeat: {data['Timestamp']}")
    else:
        print(f"Received error/unknown data: {data}")


async def main():
    """Run the example to demonstrate streaming option chain data."""
    global running
    client = None
    stream_reader = None

    try:
        # Initialize the TradeStation client
        client = TradeStationClient()

        # Step 1: Retrieve option expirations for the symbol
        symbol = "MSFT"
        print(f"\nFetching available expirations for {symbol}...")
        expirations = await client.market_data.get_option_expirations(symbol)
        # Use first expiration
        expiration_date = expirations.Expirations[0].Date
        print(f"Using expiration date: {expiration_date}\n")

        # Step 2: Start streaming the option chain for the symbol
        params = {
            "expiration": expiration_date,
            "strikeProximity": 5,
            "enableGreeks": "true",
        }
        print(f"Starting option chain stream for {symbol} with params: {params}")
        print("Press Ctrl+C to stop streaming\n")

        # Get the stream reader
        stream_reader = await client.market_data.stream_option_chain(symbol, params=params)

        # Read and process stream line by line
        while running:
            try:
                line = await asyncio.wait_for(stream_reader.readline(), timeout=1.0)
                if not line:
                    print("Stream closed by server.")
                    break
                line_str = line.strip().decode("utf-8")
                if not line_str:
                    continue
                # Remove SSE data prefix if present
                if line_str.startswith("data: "):
                    line_str = line_str[len("data: ") :]
                # Skip SSE event lines
                if line_str.startswith("event:"):
                    continue
                try:
                    data = json.loads(line_str)
                    await handle_chain_data(data)
                except json.JSONDecodeError:
                    print(f"Could not parse JSON line: {line_str}")
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Error reading from stream: {e}")
                break

    except Exception as e:
        print(f"Setup/Error: {e}")
    finally:
        print("\nCleaning up resources...")
        if client:
            await client.http_client.close()
        print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
