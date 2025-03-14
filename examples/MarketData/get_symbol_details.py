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


async def main():
    """
    Run the example to demonstrate fetching symbol details.
    """
    # Load environment variables from .env file
    load_dotenv()

    # Initialize the client without any parameters
    # This will automatically load configuration from environment variables:
    # - CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN from .env
    # - ENVIRONMENT from .env (case-insensitive, defaults to "Live")
    client = TradeStationClient(debug=False)  # Set debug=False to disable debug output

    # Alternative initialization options:
    # 1. Explicitly specify some parameters:
    # client = TradeStationClient(environment="Simulation", debug=True)
    #
    # 2. Using a dictionary for configuration:
    # client = TradeStationClient({
    #     "client_id": "your_client_id",
    #     "client_secret": "your_client_secret",
    #     "refresh_token": "your_refresh_token",
    #     "environment": "simulation"  # case-insensitive
    # }, debug=False)
    #
    # 3. Using a ClientConfig object:
    # from src.ts_types.config import ClientConfig
    # config = ClientConfig(
    #     client_id="your_client_id",
    #     client_secret="your_client_secret",
    #     refresh_token="your_refresh_token",
    #     environment="simulation"
    # )
    # client = TradeStationClient(config, debug=False)

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
