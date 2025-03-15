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

    # Get environment from env var
    environment = os.environ.get("ENVIRONMENT", "Simulation")
    environment = "Simulation" if environment.lower() == "simulation" else "Live"

    # Create TradeStationClient with environment variables
    client = TradeStationClient(
        refresh_token=os.environ.get("REFRESH_TOKEN"), environment=environment
    )

    try:
        print("\n=== Symbol Details API Example ===\n")

        # Example 1: Stock Symbol
        print("Example 1: Stock Symbol (MSFT)")
        print("---------------------------------")
        symbol = "MSFT"
        print(f"Requesting details for: {symbol}")
        response = await client.market_data.get_symbol_details([symbol])
        print_symbol_response(response)

        # Example 2: Futures Contract
        print("\nExample 2: Futures Contract (ESM24)")
        print("---------------------------------")
        symbol = "ESM24"  # E-mini S&P 500 Future June 2024
        print(f"Requesting details for: {symbol}")
        response = await client.market_data.get_symbol_details([symbol])
        print_symbol_response(response)

        # Example 3: Options Contract
        print("\nExample 3: Options Contract (TSLA 270115P270)")
        print("---------------------------------")
        symbol = "TSLA 270115P270"  # Tesla Put Option
        print(f"Requesting details for: {symbol}")
        response = await client.market_data.get_symbol_details([symbol])
        print_symbol_response(response)

        # Example 4: Continuous Future
        print("\nExample 4: Continuous Future (@ES)")
        print("---------------------------------")
        symbol = "@ES"  # E-mini S&P 500 Continuous Future
        print(f"Requesting details for: {symbol}")
        response = await client.market_data.get_symbol_details([symbol])
        print_symbol_response(response)

        # Example 5: Multiple Symbols
        print("\nExample 5: Multiple Symbols (MSFT, AAPL, GOOGL)")
        print("---------------------------------")
        symbols = ["MSFT", "AAPL", "GOOGL"]
        print(f"Requesting details for: {symbols}")
        response = await client.market_data.get_symbol_details(symbols)
        print_symbol_response(response)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the client
        await client.close()


def print_symbol_response(response):
    """Print the symbol details response in a human-readable format."""
    if response.Symbols:
        for symbol in response.Symbols:
            print_symbol_details(symbol)
    else:
        print("No symbols found in response.")

    if response.Errors:
        print("\nErrors:")
        for error in response.Errors:
            print(f"  • {error.Symbol}: {error.Message}")


def print_symbol_details(symbol):
    """Print details for a single symbol."""
    print(f"• {symbol.Symbol} ({symbol.AssetType}):")
    print(f"  Description: {symbol.Description}")
    print(f"  Exchange: {symbol.Exchange}")
    print(f"  Country: {symbol.Country}")
    print(f"  Currency: {symbol.Currency}")
    print(f"  Root: {symbol.Root}")

    # Special handling for options
    if hasattr(symbol, "StrikePrice") and symbol.StrikePrice:
        print(f"  Strike Price: {symbol.StrikePrice}")
    if hasattr(symbol, "ExpirationDate") and symbol.ExpirationDate:
        print(f"  Expiration Date: {symbol.ExpirationDate}")
    if hasattr(symbol, "ExerciseStyle") and symbol.ExerciseStyle:
        print(f"  Exercise Style: {symbol.ExerciseStyle}")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
