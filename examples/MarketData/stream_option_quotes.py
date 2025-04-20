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
from src.client.tradestation_client import TradeStationClient

# Correct the import path for OptionQuoteParams and OptionQuoteLeg
from src.ts_types.market_data import OptionQuoteParams, OptionQuoteLeg

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
    """Processes and prints individual option quote data or heartbeats."""
    # Check if it's a quote update based on presence of common quote fields
    if "Symbol" in data and "Bid" in data and "Ask" in data:
        print("\nOption Quote Update:")
        print(f"Symbol: {data.get('Symbol', 'N/A')}")
        print(f"Timestamp: {data.get('Timestamp', 'N/A')}")
        print(f"Last: {data.get('Last', 'N/A')}")
        print(f"Bid: {data.get('Bid', 'N/A')}")
        print(f"Ask: {data.get('Ask', 'N/A')}")
        print(f"Volume: {data.get('Volume', 'N/A')}")
        print(
            f"Open Interest: {data.get('OpenInterest', 'N/A')}"
        )  # OpenInterest field name might vary
        print(f"Exchange: {data.get('Exchange', 'N/A')}")
        print("-" * 60)
    elif "Heartbeat" in data:
        print(f"Heartbeat: {data.get('Timestamp', 'N/A')}")
    elif "Error" in data:
        print(f"Received error: {data.get('Error', 'Unknown error')}")
    else:
        print(f"Received unknown data: {data}")


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
