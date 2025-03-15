"""
Example of retrieving symbol details using the TradeStation API.

This script demonstrates how to fetch detailed information about symbols
from the TradeStation API, including stocks, futures, and options.
"""

import asyncio
import os
from dotenv import load_dotenv

from src.client.tradestation_client import TradeStationClient


async def main():
    """Run the example to demonstrate fetching symbol details."""
    # Load environment variables from .env file
    load_dotenv()

    # Initialize the client using environment variables
    client = TradeStationClient()

    try:
        print("\n=== Symbol Details API Example ===\n")

        # Example 1: Get details for a single stock
        print("Example 1: Single Stock Symbol")
        print("---------------------------------")

        symbol = "MSFT"  # Microsoft
        print(f"Requesting: {symbol}")

        response = await client.market_data.get_symbol_details(symbol)
        print_symbol_response(response)

        # Example 2: Get details for a futures contract
        print("\nExample 2: Futures Contract")
        print("---------------------------------")

        future_symbol = "ESM24"  # E-mini S&P 500 Future June 2024
        print(f"Requesting: {future_symbol}")

        response = await client.market_data.get_symbol_details(future_symbol)
        print_symbol_response(response)

        # Example 3: Get details for an options contract
        print("\nExample 3: Options Contract")
        print("---------------------------------")

        option_symbol = "TSLA 270115P270"  # Tesla Put Option
        print(f"Requesting: {option_symbol}")

        response = await client.market_data.get_symbol_details(option_symbol)
        print_symbol_response(response)

        # Example 4: Multiple symbols in one request
        print("\nExample 4: Multiple Symbols")
        print("---------------------------------")

        symbols = "MSFT,AAPL,SPY,QQQ"
        print(f"Requesting: {symbols}")

        response = await client.market_data.get_symbol_details(symbols)
        print_symbol_response(response)

        print("\nNote: If using Simulation mode, results may vary from what's expected.")

    except Exception as e:
        print(f"\nError occurred: {e}")
        raise

    finally:
        # Properly close client resources
        if hasattr(client, "http_client") and hasattr(client.http_client, "close"):
            await client.http_client.close()
        if hasattr(client, "stream_manager") and hasattr(client.stream_manager, "close"):
            await client.stream_manager.close()


def print_symbol_response(response):
    """Print the symbol details response in a formatted way."""
    if hasattr(response, "Symbols") and response.Symbols:
        print(f"Found {len(response.Symbols)} symbol(s):")

        for symbol in response.Symbols:
            print(f"\n• {symbol.Symbol} ({symbol.AssetType}):")
            print(f"  Description: {symbol.Description}")
            print(f"  Exchange: {symbol.Exchange}")
            print(f"  Currency: {symbol.Currency}")

            # Show asset-type specific details
            if hasattr(symbol, "ExpirationDate") and symbol.ExpirationDate:
                print(f"  Expiration: {symbol.ExpirationDate}")
            if hasattr(symbol, "StrikePrice") and symbol.StrikePrice:
                print(f"  Strike Price: {symbol.StrikePrice}")
            if hasattr(symbol, "OptionType") and symbol.OptionType:
                print(f"  Option Type: {symbol.OptionType}")
            if hasattr(symbol, "Root") and symbol.Root:
                print(f"  Root: {symbol.Root}")

            # Show price formatting info
            if hasattr(symbol, "PriceFormat") and symbol.PriceFormat:
                print(
                    f"  Price Format: {symbol.PriceFormat.Format} "
                    f"(increment: {symbol.PriceFormat.Increment})"
                )
    else:
        print("No symbols found in the response")

    # Print errors if any
    if hasattr(response, "Errors") and response.Errors:
        print("\nErrors:")
        for error in response.Errors:
            print(f"  {error.Symbol}: {error.Message}")


if __name__ == "__main__":
    asyncio.run(main())
