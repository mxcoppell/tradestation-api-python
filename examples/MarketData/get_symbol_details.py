"""
Example of retrieving symbol details using the TradeStation API.

This script demonstrates how to fetch detailed information about symbols
from the TradeStation API, including stocks, futures, and other asset types.
"""

import asyncio
import os
from pprint import pprint
from dotenv import load_dotenv

from src.client.tradestation_client import TradeStationClient
from src.ts_types.config import ClientConfig


async def main():
    """
    Run the example to demonstrate fetching symbol details.
    """
    # Load environment variables from .env file
    load_dotenv()

    # Create a ClientConfig object with credentials from environment variables
    config = ClientConfig(
        client_id=os.environ.get("CLIENT_ID"),
        client_secret=os.environ.get("CLIENT_SECRET"),
        refresh_token=os.environ.get("REFRESH_TOKEN"),
        # ClientConfig will automatically normalize the environment value
        environment=os.environ.get("ENVIRONMENT", "Live"),
    )

    # Initialize the client with the ClientConfig object
    client = TradeStationClient(config=config)

    try:
        # Example 1: Get details for a single stock
        print("\nExample 1: Get details for a single stock")
        response = await client.market_data.get_symbol_details("MSFT")
        print(f"Raw Response:\n{response}")

        if response and "Symbols" in response:
            symbols = response.get("Symbols", [])
            if symbols:
                for symbol in symbols:
                    print(f"\n{symbol['Symbol']} ({symbol['AssetType']}):")
                    print(f"Description: {symbol['Description']}")
                    print(f"Exchange: {symbol['Exchange']}")
                    print(
                        f"Price Format: {symbol['PriceFormat']['Format']} ({symbol['PriceFormat']['Decimals']} decimals)"
                    )
                    if symbol["ExpirationDate"]:
                        print(f"Expiration: {symbol['ExpirationDate']}")
                    if symbol["FutureType"]:
                        print(f"Type: {symbol['FutureType']}")
                    print("---")
            else:
                print("No symbols found in the response")

        # Show any errors
        if response and "Errors" in response:
            for error in response.get("Errors", []):
                print(f"Error for symbol {error['Symbol']}: {error['Message']}")

        # Example 2: Get details for multiple symbols of different types
        print("\nExample 2: Get details for multiple symbols of different types")
        symbols = "MSFT,MSFT 240621C400,ESM24,EUR/USD,BTCUSD"
        response = await client.market_data.get_symbol_details(symbols)
        print(f"\nRaw Response for multiple symbols:\n{response}")

        if response and "Symbols" in response:
            symbols = response.get("Symbols", [])
            if symbols:
                for symbol in symbols:
                    print(f"\n{symbol['Symbol']} ({symbol['AssetType']}):")
                    print(f"Description: {symbol['Description']}")
                    print(f"Exchange: {symbol['Exchange']}")
                    print(
                        f"Price Format: {symbol['PriceFormat']['Format']} ({symbol['PriceFormat']['Decimals']} decimals)"
                    )
                    if symbol["ExpirationDate"]:
                        print(f"Expiration: {symbol['ExpirationDate']}")
                    if symbol["FutureType"]:
                        print(f"Type: {symbol['FutureType']}")
                    print("---")

        # Show any errors
        if response and "Errors" in response:
            print("\nErrors:")
            for error in response.get("Errors", []):
                print(f"{error['Symbol']}: {error['Message']}")

    finally:
        # Properly close client resources
        if hasattr(client, "http_client") and hasattr(client.http_client, "close"):
            await client.http_client.close()
        if hasattr(client, "stream_manager") and hasattr(client.stream_manager, "close"):
            await client.stream_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
