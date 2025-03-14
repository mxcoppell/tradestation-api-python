"""
Example of retrieving symbol details using the TradeStation API.

This script demonstrates how to fetch detailed information about symbols
from the TradeStation API, including stocks, futures, and other asset types.
"""

import asyncio
import os
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
    client = TradeStationClient()

    # Alternative initialization options:
    # 1. Explicitly specify some parameters:
    # client = TradeStationClient(environment="Simulation")
    #
    # 2. Using a dictionary for configuration:
    # client = TradeStationClient({
    #     "client_id": "your_client_id",
    #     "client_secret": "your_client_secret",
    #     "refresh_token": "your_refresh_token",
    #     "environment": "simulation"  # case-insensitive
    # })
    #
    # 3. Using a ClientConfig object:
    # from src.ts_types.config import ClientConfig
    # config = ClientConfig(
    #     client_id="your_client_id",
    #     client_secret="your_client_secret",
    #     refresh_token="your_refresh_token",
    #     environment="simulation"
    # )
    # client = TradeStationClient(config)

    try:
        print("\n=== TradeStation API Symbol Details Example ===")
        print("\nImportant API Notes:")
        print("1. The API may interpret symbols differently between environments")
        print("2. In Simulation mode, the API may return test data not matching your request")
        print("3. In some cases, the API breaks symbols into individual characters")
        print("4. Your account permissions determine which symbols are accessible")
        print("\nDebugging Tips:")
        print("- Check status codes for requests (2xx means success)")
        print("- Verify you have appropriate permissions for requested symbols")
        print("- Try individual symbols rather than comma-separated lists")
        print("- Consult the TradeStation API documentation for expected formats")
        print("- Use debug=True when initializing the client for verbose logging")
        print("  Example: client = TradeStationClient(debug=True)")
        print("\n" + "=" * 50 + "\n")

        # Example 1: Get details for a single stock
        print("\nExample 1: Get details for a single stock")
        print("----------------------------------------------")

        # Using a simple stock symbol
        symbol = "MSFT"  # Microsoft
        print(f"Requesting symbol: {symbol}")

        response = await client.market_data.get_symbol_details(symbol)

        # Check status code when available (for additional debugging)
        if hasattr(response, "_status_code"):
            print(f"Status Code: {response._status_code}")

        # Handle the response
        print_symbol_response(response)

        # Example 2: Try a futures contract
        print("\nExample 2: Get details for a futures contract")
        print("----------------------------------------------")

        future_symbol = "ESM24"  # E-mini S&P 500 Future June 2024
        print(f"Requesting symbol: {future_symbol}")

        response = await client.market_data.get_symbol_details(future_symbol)

        # Check status code when available
        if hasattr(response, "_status_code"):
            print(f"Status Code: {response._status_code}")

        # Handle the response
        print_symbol_response(response)

        # Example 3: Get details for a forex pair
        print("\nExample 3: Get details for a forex pair")
        print("----------------------------------------------")

        forex_symbol = "EUR/USD"
        print(f"Requesting symbol: {forex_symbol}")

        response = await client.market_data.get_symbol_details(forex_symbol)

        # Check status code when available
        if hasattr(response, "_status_code"):
            print(f"Status Code: {response._status_code}")

        # Handle the response
        print_symbol_response(response)

        print("\n=== End of Example ===")
        print("Note: If you received individual letter symbols (like 'S', 'M', etc.)")
        print("instead of the requested symbols, this is likely due to:")
        print("1. Using the Simulation environment which returns test data")
        print("2. The API parsing the requested symbol in an unexpected way")
        print("3. Limitations in your API account permissions")
        print("\nContact TradeStation support if you need assistance with API access.")

    except Exception as e:
        print(f"\nError occurred: {type(e).__name__}: {e}")
        # Re-raise the exception to see the full traceback
        raise

    finally:
        # Properly close client resources
        if hasattr(client, "http_client") and hasattr(client.http_client, "close"):
            await client.http_client.close()
        if hasattr(client, "stream_manager") and hasattr(client.stream_manager, "close"):
            await client.stream_manager.close()


def print_symbol_response(response):
    """
    Print the symbol details response in a formatted way.

    Args:
        response: The API response object
    """
    # Handle the response
    if hasattr(response, "Symbols"):
        symbols = response.Symbols
        if symbols:
            print(f"\nFound {len(symbols)} symbol(s):")
            for symbol in symbols:
                print(f"\n{symbol.Symbol} ({symbol.AssetType}):")
                print(f"  Description: {symbol.Description}")
                print(f"  Exchange: {symbol.Exchange}")
                print(f"  Currency: {symbol.Currency}")

                if hasattr(symbol, "PriceFormat") and symbol.PriceFormat:
                    print(
                        f"  Price Format: {symbol.PriceFormat.Format} "
                        f"({symbol.PriceFormat.Decimals} decimals, "
                        f"increment {symbol.PriceFormat.Increment})"
                    )

                if hasattr(symbol, "ExpirationDate") and symbol.ExpirationDate:
                    print(f"  Expiration: {symbol.ExpirationDate}")
                if hasattr(symbol, "FutureType") and symbol.FutureType:
                    print(f"  Type: {symbol.FutureType}")

                # Additional attributes if available
                if hasattr(symbol, "Country") and symbol.Country:
                    print(f"  Country: {symbol.Country}")
                if hasattr(symbol, "RolloverOne") and symbol.RolloverOne:
                    print(f"  Rollover 1: {symbol.RolloverOne}")

                print("  " + "-" * 40)
        else:
            print("No symbols found in the response")
    else:
        print(f"Unexpected response format: {response}")

    # Print errors if any
    if hasattr(response, "Errors") and response.Errors:
        print("\nErrors:")
        for error in response.Errors:
            print(f"  {error.Symbol}: {error.Message}")


if __name__ == "__main__":
    asyncio.run(main())
