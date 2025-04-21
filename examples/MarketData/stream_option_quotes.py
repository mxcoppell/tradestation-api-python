#!/usr/bin/env python
"""
Example demonstrating how to stream specific option quotes using the TradeStation API Python wrapper.

This example shows how to:
1. Connect to the TradeStation API and authenticate
2. Define a list of specific option contract symbols
3. Stream real-time quote updates for these options using Server-Sent Events (SSE)
4. Process and display incoming option quote data and heartbeats
"""

import asyncio
import signal
import json
import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from tradestation.client.tradestation_client import TradeStationClient

# Correct the import path for OptionQuoteParams and OptionQuoteLeg
from tradestation.ts_types.market_data import OptionQuoteParams, OptionQuoteLeg

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


async def handle_quote_data(data: Dict[str, Any]):
    """Processes and prints option quote data with structure and includes all other fields."""
    # Check if it's a spread quote update (contains Greeks/Legs)
    if "Delta" in data and "Legs" in data:
        print("\nOption Spread Quote Update:")

        # Keep track of keys printed in the structured section
        printed_keys = set()

        # Extract symbols from legs for clarity
        leg_symbols = [leg.get("Symbol", "N/A") for leg in data.get("Legs", [])]
        print(f"Spread Legs: {', '.join(leg_symbols)}")
        printed_keys.add("Legs")

        # Check and print Timestamp if available
        if "Timestamp" in data:
            print(f"Timestamp: {data['Timestamp']}")
            printed_keys.add("Timestamp")

        print("\n  Market Data:")
        market_keys = [
            "Last",
            "Bid",
            "BidSize",
            "Ask",
            "AskSize",
            "Volume",
            "DailyOpenInterest",
            "NetChange",
            "NetChangePct",
        ]
        for key in market_keys:
            if key in data:
                if key == "Bid":
                    print(f"    Bid: {data[key]} (Size: {data.get('BidSize', 'N/A')})")
                elif key == "Ask":
                    print(f"    Ask: {data[key]} (Size: {data.get('AskSize', 'N/A')})")
                elif key == "NetChange":
                    print(f"    Net Change: {data[key]} ({data.get('NetChangePct', 'N/A')}%)")
                # Avoid double printing Size/Pct
                elif key not in ["BidSize", "AskSize", "NetChangePct"]:
                    print(f"    {key}: {data[key]}")
                printed_keys.add(key)

        print("\n  Greeks:")
        greek_keys = ["Delta", "Gamma", "Theta", "Vega", "Rho"]
        for key in greek_keys:
            if key in data:
                print(f"    {key}: {data[key]}")
                printed_keys.add(key)

        print("\n  Volatility & Value:")
        vol_value_keys = [
            "ImpliedVolatility",
            "IntrinsicValue",
            "ExtrinsicValue",
            "TheoreticalValue",
        ]
        for key in vol_value_keys:
            if key in data:
                print(f"    {key}: {data[key]}")
                printed_keys.add(key)

        # --- Print Any Remaining Fields ---
        print("\n  Other Received Fields:")
        other_fields_found = False
        for key, value in data.items():
            if key not in printed_keys:
                print(f"    {key}: {value}")
                other_fields_found = True
        if not other_fields_found:
            print("    (No other fields)")

        print("-" * 60)

    elif "Heartbeat" in data:
        print(f"Heartbeat: {data.get('Timestamp', 'N/A')}")
    elif "Error" in data:
        print(f"Received Error: {data.get('Error', 'Unknown error')} - {data.get('Message', '')}")
    else:
        # Keep this for genuinely unexpected formats
        print(f"Received Unrecognized Data Format: {data}")


async def main():
    """Run the example to demonstrate streaming option quote data."""
    global running
    client = None
    stream_reader = None

    try:
        # Initialize the TradeStation client
        # Assumes .env file has CLIENT_ID, REFRESH_TOKEN, ENVIRONMENT
        client = TradeStationClient()

        # Step 1: Define the specific option symbols to stream
        # Example option symbols - replace with valid symbols you have access to
        # Format typically: UNDERLYING YYMMDD[C/P]STRIKEPRICE (e.g., MSFT 251219C500)
        option_symbols: List[str] = [
            "MSFT 251219C500",  # Example MSFT Call
            "AAPL 251219P180",  # Example AAPL Put
            # Add more specific option contract symbols here
        ]
        # Create OptionQuoteLeg objects for each symbol
        option_legs: List[OptionQuoteLeg] = [
            OptionQuoteLeg(Symbol=symbol) for symbol in option_symbols
        ]
        # Create OptionQuoteParams object
        stream_params = OptionQuoteParams(legs=option_legs)

        print(f"\nPreparing to stream quotes for symbols: {', '.join(option_symbols)}")

        # Step 2: Start streaming quotes for the specified symbols
        print("Starting option quote stream...")
        print("Press Ctrl+C to stop streaming\n")

        # Get the stream reader using stream_option_quotes
        # Pass the OptionQuoteParams object
        stream_reader = await client.market_data.stream_option_quotes(params=stream_params)

        # Read and process stream line by line
        while running:
            try:
                # Wait for a line from the stream with a timeout
                line = await asyncio.wait_for(stream_reader.readline(), timeout=1.0)

                # Check if the stream was closed
                if not line:
                    print("Stream closed by server.")
                    break

                # Decode the line from bytes to string and remove leading/trailing whitespace
                line_str = line.strip().decode("utf-8")

                # Skip empty lines
                if not line_str:
                    continue

                # Handle Server-Sent Events (SSE) format
                # Remove 'data: ' prefix if present
                if line_str.startswith("data: "):
                    line_str = line_str[len("data: ") :]
                # Skip comment lines (starting with ':') or event type lines
                elif line_str.startswith(":") or line_str.startswith("event:"):
                    continue

                # Attempt to parse the line as JSON
                try:
                    data = json.loads(line_str)
                    # Process the received data (quote update, heartbeat, or error)
                    await handle_quote_data(data)
                except json.JSONDecodeError:
                    # Log if the line is not valid JSON (and not an SSE comment/event)
                    print(f"Could not parse JSON line: {line_str}")

            except asyncio.TimeoutError:
                # No data received within the timeout period, continue loop to check 'running' flag
                continue
            except Exception as e:
                # Handle other exceptions during stream reading
                print(f"Error reading from stream: {e}")
                break

    except Exception as e:
        # Handle setup errors (e.g., authentication, initial connection)
        print(f"An error occurred during setup or streaming: {e}")
        import traceback

        traceback.print_exc()  # Print full traceback for debugging
    finally:
        # Cleanup resources
        print("\nCleaning up resources...")
        if client and hasattr(client, "http_client"):
            await client.close()  # Use the client's close method if available
            print("Client session closed.")
        else:
            print("Client or http_client not available for cleanup.")

        print("Stream example finished.")


if __name__ == "__main__":
    # Ensure necessary environment variables are set
    required_vars = ["CLIENT_ID", "REFRESH_TOKEN", "ENVIRONMENT"]
    if not all(os.getenv(k) for k in required_vars):
        print("Error: Required environment variables for TradeStation authentication are not set.")
        print("Please create a .env file or set environment variables for:")
        print(", ".join(required_vars))
    else:
        # Run the main asynchronous function
        asyncio.run(main())
