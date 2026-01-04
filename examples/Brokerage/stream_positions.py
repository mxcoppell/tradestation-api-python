"""
Example script for streaming positions using the TradeStation API.

This script demonstrates how to connect to the TradeStation API,
authenticate, and subscribe to the position stream for specified accounts.
It prints out position update events as they are received.

Usage:
- Ensure you have a valid .env file with your CLIENT_ID, REFRESH_TOKEN,
  and ENVIRONMENT (simulation or live).
- Run the script from the project root directory:
  poetry run python examples/Brokerage/stream_positions.py
"""

import asyncio
import json
import os
import signal
from pathlib import Path
from typing import List

from dotenv import load_dotenv  # type: ignore

# Use the client directly
from tradestation.client import TradeStationClient
from tradestation.ts_types.brokerage import Account  # Use Account type for fetching

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


async def main():
    """
    Main function to stream positions.
    """
    global running  # Declare access to the global flag
    ts_client = None
    stream_reader = None

    # Load environment variables from .env file
    load_dotenv()

    # Initialize the TradeStation client
    # Client handles auth using environment variables
    ts_client = TradeStationClient()

    try:
        # Fetch available accounts
        print("Fetching accounts...")
        accounts: List[Account] = await ts_client.brokerage.get_accounts()
        if not accounts or not isinstance(accounts, list):
            print("No accounts found or invalid format received.")
            return

        # Concatenate all fetched account IDs
        all_account_ids = [acc.AccountID for acc in accounts]
        account_ids_str = ",".join(all_account_ids)
        print(f"Using account ID(s): {account_ids_str}")

        # Start streaming positions
        print(f"\nStarting position stream for account(s): {account_ids_str}...")
        print("Press Ctrl+C to stop streaming\n")
        # Call the stream_positions method
        stream_reader = await ts_client.brokerage.stream_positions(account_ids_str)

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

                    # Process based on data type - check for common position keys
                    # Note: There isn't a specific Pydantic model for streamed positions yet,
                    # so we print the raw dictionary.
                    if "PositionID" in data and "Symbol" in data and "Quantity" in data:
                        print(f"Received Position Update: {json.dumps(data, indent=2)}")
                    elif "Heartbeat" in data:  # Handle heartbeat
                        print(f"Heartbeat received: {data.get('Timestamp')}")
                    elif data.get("StreamStatus") == "EndSnapshot":  # Handle snapshot end
                        print(
                            "--- Initial Position Snapshot Complete --- Real-time updates follow ---"
                        )
                    elif "Error" in data:  # Handle stream errors
                        print(
                            f"Stream Error: {data.get('Message', 'Unknown error')} ({data['Error']})"
                        )
                        if data.get("Error") == "GoAway":  # Check specific error types if needed
                            running = False
                    else:
                        # Print any other messages received for debugging
                        print(f"Received Other Data: {data}")

                except json.JSONDecodeError:
                    print(f"Received non-JSON line: {line_str}")
                except Exception as parse_error:
                    print(f"Error parsing stream data: {parse_error}\nData: {line_str}")

            except asyncio.TimeoutError:
                # Timeout occurred, loop continues to check `running` flag
                continue
            except Exception as inner_error:
                # Handle errors during line processing
                print(f"Error processing stream line: {str(inner_error)}")
                # Optionally, break or implement retry logic
                break

    except Exception as e:
        print(f"\nAn error occurred during setup or streaming: {e}")
        import traceback

        traceback.print_exc()
    finally:
        print("\nCleaning up resources...")
        # Ensure the client session is closed properly
        if ts_client:
            await ts_client.http_client.close()
        print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
