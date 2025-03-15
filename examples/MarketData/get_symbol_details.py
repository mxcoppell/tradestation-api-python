"""
Example of retrieving symbol details using the TradeStation API.

This script demonstrates how to fetch detailed information about various symbol types
from the TradeStation API, including stocks, futures, options, and indices.

Note that the 'ENVIRONMENT' variable in your .env file determines which API endpoint is used:
- "Live" uses api.tradestation.com (production)
- "Simulation" uses sim.api.tradestation.com (test environment)
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

        # Example 1: Stock Symbol
        print("Example 1: Stock Symbol (MSFT)")
        print("---------------------------------")
        symbol = "MSFT"
        print(f"Requesting details for: {symbol}")
        response = await client.market_data.get_symbol_details(symbol)
        print_symbol_response(response)

        # Example 2: Futures Contract
        print("\nExample 2: Futures Contract (ESM24)")
        print("---------------------------------")
        symbol = "ESM24"  # E-mini S&P 500 Future June 2024
        print(f"Requesting details for: {symbol}")
        response = await client.market_data.get_symbol_details(symbol)
        print_symbol_response(response)

        # Example 3: Options Contract
        print("\nExample 3: Options Contract (TSLA 270115P270)")
        print("---------------------------------")
        symbol = "TSLA 270115P270"  # Tesla Put Option
        print(f"Requesting details for: {symbol}")
        response = await client.market_data.get_symbol_details(symbol)
        print_symbol_response(response)

        # Example 4: Continuous Futures Symbol
        print("\nExample 4: Continuous Futures (@S)")
        print("---------------------------------")
        symbol = "@S"  # Continuous Soybean Futures
        print(f"Requesting details for: {symbol}")
        response = await client.market_data.get_symbol_details(symbol)
        print_symbol_response(response)

        # Example 5: Index Symbol
        print("\nExample 5: Index Symbol ($SPX.X)")
        print("---------------------------------")
        symbol = "$SPX.X"  # S&P 500 Index
        print(f"Requesting details for: {symbol}")
        response = await client.market_data.get_symbol_details(symbol)
        print_symbol_response(response)

        # Example 6: Multiple Symbols in One Request
        print("\nExample 6: Multiple Symbols in One Request")
        print("---------------------------------")
        # You can request up to 50 symbols in a single API call
        symbols = ["MSFT", "ESM24", "TSLA 270115P270", "@S", "$SPX.X"]
        print(f"Requesting details for multiple symbols: {symbols}")
        response = await client.market_data.get_symbol_details(symbols)
        print_symbol_response(response)

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
    if not hasattr(response, "Symbols") or not response.Symbols:
        print("No symbols found in the response")
        return

    print(f"Found {len(response.Symbols)} symbol(s):")

    for symbol in response.Symbols:
        print(f"\n• {symbol.Symbol} ({symbol.AssetType}):")
        print_symbol_details(symbol)

    # Print errors if any
    if hasattr(response, "Errors") and response.Errors:
        print("\nErrors:")
        for error in response.Errors:
            print(f"  {error.Symbol}: {error.Message}")


def print_symbol_details(symbol):
    """Print details for a single symbol."""
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


if __name__ == "__main__":
    asyncio.run(main())
