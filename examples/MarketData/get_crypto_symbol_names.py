"""
Example of retrieving crypto symbol names using the TradeStation API.

This script demonstrates how to fetch the list of available cryptocurrency symbols
from the TradeStation API. These symbols can be used for market data requests,
but note that they cannot be traded directly.

Note that the 'ENVIRONMENT' variable in your .env file determines which API endpoint is used:
- "Live" uses api.tradestation.com (production)
- "Simulation" uses sim.api.tradestation.com (test environment)
"""

import asyncio
import os
from dotenv import load_dotenv

from src.client.http_client import HttpClient
from src.utils.stream_manager import WebSocketStream
from src.services.MarketData.market_data_service import MarketDataService


class MinimalStreamManager:
    """A minimal implementation of StreamManager for this example."""

    def __init__(self):
        pass

    async def close(self):
        """Dummy close method."""
        pass


async def main():
    """Run the example to demonstrate fetching crypto symbol names."""
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

    # Create a minimal stream manager
    stream_manager = MinimalStreamManager()

    # Initialize MarketDataService directly
    market_data_service = MarketDataService(http_client, stream_manager)

    try:
        print("\n=== Crypto Symbol Names API Example ===\n")

        print("Requesting available crypto symbol names...")
        response = await market_data_service.get_crypto_symbol_names()

        # Print the response
        print("\nAvailable Crypto Symbols:")
        print("-----------------------")
        for symbol in response.SymbolNames:
            print(f"- {symbol}")

        print(
            "\nNote: While data can be obtained for these symbols, they cannot be traded directly."
        )

        # Example of how to use these symbols
        print("\nExample: How to use these symbols")
        print("-------------------------------")
        print("You can use these symbols with other market data methods, such as:")
        print("- get_symbol_details()")
        print("- get_quote_snapshots()")
        print("- stream_quotes()")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the HTTP client
        await http_client.close()


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
