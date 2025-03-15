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
        print_symbol_response(response, requested_symbol=symbol)

        # Example 2: Get details for a futures contract
        print("\nExample 2: Futures Contract")
        print("---------------------------------")

        future_symbol = "ESM24"  # E-mini S&P 500 Future June 2024
        print(f"Requesting: {future_symbol}")

        response = await client.market_data.get_symbol_details(future_symbol)
        print_symbol_response(response, requested_symbol=future_symbol)

        # Example 3: Get details for an options contract
        print("\nExample 3: Options Contract")
        print("---------------------------------")

        option_symbol = "TSLA 270115P270"  # Tesla Put Option
        print(f"Requesting: {option_symbol}")

        response = await client.market_data.get_symbol_details(option_symbol)
        print_symbol_response(response, requested_symbol=option_symbol)

        # Example 4: Multiple symbols in one request
        print("\nExample 4: Multiple Symbols")
        print("---------------------------------")

        symbols = "MSFT,AAPL,SPY,QQQ"
        requested_symbols = symbols.split(",")
        print(f"Requesting: {symbols}")

        response = await client.market_data.get_symbol_details(symbols)
        print_symbol_response(response, requested_symbols=requested_symbols)

        print("\nNote: In Simulation mode, the API may return data that doesn't match")
        print("the requested symbols. This example filters responses to show only")
        print("exact symbol matches when possible.")

    except Exception as e:
        print(f"\nError occurred: {e}")
        raise

    finally:
        # Properly close client resources
        if hasattr(client, "http_client") and hasattr(client.http_client, "close"):
            await client.http_client.close()
        if hasattr(client, "stream_manager") and hasattr(client.stream_manager, "close"):
            await client.stream_manager.close()


def print_symbol_response(response, requested_symbol=None, requested_symbols=None):
    """Print the symbol details response in a formatted way."""
    if not hasattr(response, "Symbols") or not response.Symbols:
        print("No symbols found in the response")
        return

    # Check if we're in simulation mode by looking at the returned symbols
    is_simulation = False
    if requested_symbol and len(response.Symbols) > 1:
        # In simulation mode, a single symbol request returns multiple symbols
        matching_symbols = [
            s for s in response.Symbols if s.Symbol.upper() == requested_symbol.upper()
        ]
        if not matching_symbols and all(len(s.Symbol) == 1 for s in response.Symbols):
            is_simulation = True

    # For single symbol requests
    if requested_symbol and not is_simulation:
        # Try to find exact match
        matching_symbols = [
            s for s in response.Symbols if s.Symbol.upper() == requested_symbol.upper()
        ]

        if matching_symbols:
            print(f"Details for {requested_symbol}:")
            for symbol in matching_symbols:
                print_symbol_details(symbol)
        else:
            print(f"No exact match found for {requested_symbol}")
            print("API returned:")
            for symbol in response.Symbols:
                print(f"- {symbol.Symbol} ({symbol.AssetType})")

    # For multiple symbols requests
    elif requested_symbols and not is_simulation:
        matching_count = 0
        for req_symbol in requested_symbols:
            matching = [s for s in response.Symbols if s.Symbol.upper() == req_symbol.upper()]
            if matching:
                matching_count += 1
                print(f"\nDetails for {req_symbol}:")
                for symbol in matching:
                    print_symbol_details(symbol)

        if matching_count == 0:
            print("No exact matches found for any requested symbols")
            print("API returned:")
            for symbol in response.Symbols:
                print(f"- {symbol.Symbol} ({symbol.AssetType})")

    # If simulation mode or no specific symbol filtering
    else:
        if is_simulation:
            print("Running in Simulation mode. API is returning test data.")

        print(f"API returned {len(response.Symbols)} symbol(s):")
        for symbol in response.Symbols:
            print(f"\n• {symbol.Symbol} ({symbol.AssetType}):")
            print_symbol_details(symbol, indent="  ")

    # Print errors if any
    if hasattr(response, "Errors") and response.Errors:
        print("\nErrors:")
        for error in response.Errors:
            print(f"  {error.Symbol}: {error.Message}")


def print_symbol_details(symbol, indent=""):
    """Print details for a single symbol."""
    print(f"{indent}Description: {symbol.Description}")
    print(f"{indent}Exchange: {symbol.Exchange}")
    print(f"{indent}Currency: {symbol.Currency}")

    # Show asset-type specific details
    if hasattr(symbol, "ExpirationDate") and symbol.ExpirationDate:
        print(f"{indent}Expiration: {symbol.ExpirationDate}")
    if hasattr(symbol, "StrikePrice") and symbol.StrikePrice:
        print(f"{indent}Strike Price: {symbol.StrikePrice}")
    if hasattr(symbol, "OptionType") and symbol.OptionType:
        print(f"{indent}Option Type: {symbol.OptionType}")
    if hasattr(symbol, "Root") and symbol.Root:
        print(f"{indent}Root: {symbol.Root}")

    # Show price formatting info
    if hasattr(symbol, "PriceFormat") and symbol.PriceFormat:
        print(
            f"{indent}Price Format: {symbol.PriceFormat.Format} "
            f"(increment: {symbol.PriceFormat.Increment})"
        )


if __name__ == "__main__":
    asyncio.run(main())
