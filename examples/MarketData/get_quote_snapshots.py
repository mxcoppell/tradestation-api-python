"""
Example of retrieving quote snapshots using the TradeStation API.

This script demonstrates how to fetch real-time quote information for various symbols
from the TradeStation API, including stocks, futures, options, and indices.

Note that the 'ENVIRONMENT' variable in your .env file determines which API endpoint is used:
- "Live" uses api.tradestation.com (production)
- "Simulation" uses sim.api.tradestation.com (test environment)
"""

import asyncio
import os
import json
from dotenv import load_dotenv

from src.client.tradestation_client import TradeStationClient


async def main():
    """Run the example to demonstrate fetching quote snapshots."""
    # Load environment variables from .env file
    load_dotenv()

    # Create TradeStationClient (configuration loaded from environment variables)
    client = TradeStationClient()

    try:
        print("\n=== Quote Snapshots API Example ===\n")

        # Example 1: Stock Symbol
        print("Example 1: Stock Symbol (MSFT)")
        print("---------------------------------")
        symbol = "MSFT"  # Simple string
        print(f"Requesting quote snapshot for: {symbol}")

        # Debug: Use the HTTP client to see raw response
        response_data = await client.http_client.get(f"/v3/marketdata/quotes/{symbol}")
        print("Raw API response:")
        print(json.dumps(response_data, indent=2))

        response = await client.market_data.get_quote_snapshots(symbol)
        print_quote_response(response)

        # Example 2: Futures Contract
        print("\nExample 2: Futures Contract (ESM24)")
        print("---------------------------------")
        symbol = "ESM24"  # E-mini S&P 500 Future June 2024
        print(f"Requesting quote snapshot for: {symbol}")
        response = await client.market_data.get_quote_snapshots(symbol)
        print_quote_response(response)

        # Example 3: Options Contract
        print("\nExample 3: Options Contract (TSLA 270115P270)")
        print("---------------------------------")
        symbol = "TSLA 270115P270"  # Tesla Put Option
        print(f"Requesting quote snapshot for: {symbol}")
        response = await client.market_data.get_quote_snapshots(symbol)
        print_quote_response(response)

        # Example 4: Continuous Futures Symbol
        print("\nExample 4: Continuous Futures (@S)")
        print("---------------------------------")
        symbol = "@S"  # Continuous Soybean Futures
        print(f"Requesting quote snapshot for: {symbol}")
        response = await client.market_data.get_quote_snapshots(symbol)
        print_quote_response(response)

        # Example 5: Index Symbol
        print("\nExample 5: Index Symbol ($SPX.X)")
        print("---------------------------------")
        symbol = "$SPX.X"  # S&P 500 Index
        print(f"Requesting quote snapshot for: {symbol}")
        response = await client.market_data.get_quote_snapshots(symbol)
        print_quote_response(response)

        # Example 6: Multiple Symbols in One Request
        print("\nExample 6: Multiple Symbols in One Request")
        print("---------------------------------")
        # You can request up to 100 symbols in a single API call
        # Demonstrate two ways to pass multiple symbols:

        # Option 1: Comma-separated string
        symbols_str = "MSFT,AAPL,GOOGL"
        print(f"Requesting quote snapshots for symbols (comma-string): {symbols_str}")
        response = await client.market_data.get_quote_snapshots(symbols_str)
        print_quote_response(response)

        # Option 2: List of symbols
        symbols_list = ["AMZN", "META"]
        print(f"Requesting quote snapshots for symbols (list): {symbols_list}")
        response = await client.market_data.get_quote_snapshots(symbols_list)
        print_quote_response(response)

    except Exception as e:
        print(f"\nError occurred: {e}")
        raise

    finally:
        # Properly close the client
        await client.close()


def print_quote_response(response):
    """Print the quote snapshots response in a formatted way."""
    if not hasattr(response, "Quotes") or not response.Quotes:
        print("No quotes found in the response")
        return

    print(f"Found {len(response.Quotes)} quote(s):")

    for quote in response.Quotes:
        print(f"\n• {quote.Symbol}:")
        print_quote_details(quote)

    # Print errors if any
    if hasattr(response, "Errors") and response.Errors:
        print("\nErrors:")
        for error in response.Errors:
            print(f"  {error.Symbol}: {error.Error}")


def print_quote_details(quote):
    """Print details for a single quote."""
    print(f"  Last: {quote.Last}")
    print(f"  Change: {quote.NetChange} ({quote.NetChangePct}%)")
    print(f"  Bid: {quote.Bid} x {quote.BidSize}")
    print(f"  Ask: {quote.Ask} x {quote.AskSize}")
    print(f"  Volume: {quote.Volume}")

    # Show daily range
    print(f"  Daily Range: {quote.Low} - {quote.High}")
    print(f"  Open: {quote.Open}")
    print(f"  Previous Close: {quote.PreviousClose}")

    # Show 52-week range if available
    if hasattr(quote, "High52Week") and quote.High52Week:
        print(f"  52-Week Range: {quote.Low52Week} - {quote.High52Week}")

    # Show trade information
    if hasattr(quote, "TradeTime") and quote.TradeTime:
        print(f"  Last Trade: {quote.TradeTime}")

    # Show market flags
    if hasattr(quote, "MarketFlags") and quote.MarketFlags:
        flags = []
        if quote.MarketFlags.IsDelayed:
            flags.append("Delayed")
        if quote.MarketFlags.IsHalted:
            flags.append("Halted")
        if quote.MarketFlags.IsBats:
            flags.append("BATS")
        if quote.MarketFlags.IsHardToBorrow:
            flags.append("Hard to Borrow")

        if flags:
            print(f"  Market Flags: {', '.join(flags)}")


if __name__ == "__main__":
    asyncio.run(main())
