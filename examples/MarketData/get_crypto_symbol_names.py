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

from tradestation.client import TradeStationClient


async def main():
    """Run the example to demonstrate fetching crypto symbol names."""
    # Load environment variables from .env file
    load_dotenv()

    # Create TradeStationClient (configuration loaded from environment variables)
    client = TradeStationClient()

    try:
        print("\n=== Crypto Symbol Names API Example ===\n")

        print("Requesting available crypto symbol names...")
        response = await client.market_data.get_crypto_symbol_names()

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
        # Close the client
        await client.close()


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
