#!/usr/bin/env python
"""
Example demonstrating how to get option expirations for a symbol using the TradeStation API.

This example shows how to:
1. Create a TradeStationClient
2. Get option expirations for a symbol
3. Filter option expirations by strike price
"""

import asyncio
import os
from dotenv import load_dotenv

from tradestation.client import TradeStationClient


async def main():
    # Load environment variables from .env file
    load_dotenv()

    # Create TradeStationClient (configuration loaded from environment variables)
    client = TradeStationClient()

    try:
        # Get all option expirations for AAPL
        print("\nGetting option expirations for AAPL:")
        expirations = await client.market_data.get_option_expirations("AAPL")

        # Print the expirations
        print(f"Found {len(expirations.Expirations)} expirations:")
        for expiration in expirations.Expirations:
            print(f"  {expiration.Date} - {expiration.Type}")

        # Get option expirations for MSFT at strike price 400
        print("\nGetting option expirations for MSFT at strike price 400:")
        msft_expirations = await client.market_data.get_option_expirations("MSFT", 400)

        # Print the expirations
        print(f"Found {len(msft_expirations.Expirations)} expirations:")
        for expiration in msft_expirations.Expirations:
            print(f"  {expiration.Date} - {expiration.Type}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the client
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
