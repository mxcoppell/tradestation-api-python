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

from src.client.http_client import HttpClient
from src.utils.stream_manager import StreamManager
from src.services.MarketData.market_data_service import MarketDataService


async def main():
    # Load environment variables from .env file
    load_dotenv()

    # Get environment from env var
    environment = os.environ.get("ENVIRONMENT", "Simulation")
    environment = "Simulation" if environment.lower() == "simulation" else "Live"

    # Create config dict
    config = {
        "client_id": os.environ.get("CLIENT_ID"),
        "client_secret": os.environ.get("CLIENT_SECRET"),
        "refresh_token": os.environ.get("REFRESH_TOKEN"),
        "environment": environment,
    }

    # Initialize HTTP client directly
    http_client = HttpClient(config)

    # Create a stream manager (not used for option expirations, but required by MarketDataService)
    stream_manager = StreamManager(config)

    # Initialize MarketDataService directly
    market_data = MarketDataService(http_client, stream_manager)

    try:
        # Get all option expirations for AAPL
        print("\nGetting option expirations for AAPL:")
        expirations = await market_data.get_option_expirations("AAPL")

        # Print the expirations
        print(f"Found {len(expirations.Expirations)} expirations:")
        for expiration in expirations.Expirations:
            print(f"  {expiration.Date} - {expiration.Type}")

        # Get option expirations for MSFT at strike price 400
        print("\nGetting option expirations for MSFT at strike price 400:")
        msft_expirations = await market_data.get_option_expirations("MSFT", 400)

        # Print the expirations
        print(f"Found {len(msft_expirations.Expirations)} expirations:")
        for expiration in msft_expirations.Expirations:
            print(f"  {expiration.Date} - {expiration.Type}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the HTTP client
        await http_client.close()


if __name__ == "__main__":
    asyncio.run(main())
