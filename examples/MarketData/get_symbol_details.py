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
from decimal import Decimal, ROUND_HALF_UP
from dotenv import load_dotenv
from tradestation.client.tradestation_client import TradeStationClient

# Load environment variables from .env file
load_dotenv()


async def main():
    """
    Main asynchronous function to demonstrate fetching symbol details.
    """
    # Initialize the TradeStation client
    # The client automatically handles authentication using environment variables:
    # CLIENT_ID, REFRESH_TOKEN, ENVIRONMENT
    client = TradeStationClient()

    try:
        # --- Example 1: Get details for a single stock ---
        print("\n--- Example 1: Get details for MSFT ---")
        msft_details = await client.market_data.get_symbol_details("MSFT")

        if msft_details.Errors:
            print(f"Error fetching MSFT details: {msft_details.Errors[0].Message}")
        elif msft_details.Symbols:
            msft_symbol = msft_details.Symbols[0]
            print(f"Asset Type: {msft_symbol.AssetType}")
            print(f"Description: {msft_symbol.Description}")
            print(f"Exchange: {msft_symbol.Exchange}")
            print(f"Currency: {msft_symbol.Currency}")
            if msft_symbol.PriceFormat:
                print(
                    "Price Format:",
                    {
                        "format": msft_symbol.PriceFormat.Format,
                        "decimals": (
                            msft_symbol.PriceFormat.Decimals
                            if msft_symbol.PriceFormat.Decimals is not None
                            else "N/A"
                        ),
                        "increment": msft_symbol.PriceFormat.Increment,
                    },
                )
        else:
            print("No symbols found for MSFT.")

        # --- Example 2: Get details for multiple symbols of different types ---
        print("\n--- Example 2: Get details for multiple symbols ---")
        symbols_to_fetch = [
            "MSFT",  # Stock
            "MSFT 240119C400",  # Option (Example, might be expired)
            "ESH24",  # Future (Example, might be expired)
            "EUR/USD",  # Forex
            "BTCUSD",  # Crypto
            "INVALID_SYMBOL",  # Example of an invalid symbol
        ]
        multi_details = await client.market_data.get_symbol_details(symbols_to_fetch)

        # Process successful results
        print("\nDetails for Multiple Symbols:")
        if multi_details.Symbols:
            for symbol in multi_details.Symbols:
                print(f"\n{symbol.Symbol} ({symbol.AssetType}):")
                print(f"Description: {symbol.Description}")
                print(f"Exchange: {symbol.Exchange}")
                if symbol.PriceFormat:
                    decimals_str = (
                        symbol.PriceFormat.Decimals
                        if symbol.PriceFormat.Decimals is not None
                        else "N/A"
                    )
                    print(f"Price Format: {symbol.PriceFormat.Format} ({decimals_str} decimals)")
                else:
                    print("Price Format: N/A")

                # Asset-specific properties
                if symbol.AssetType == "STOCKOPTION":
                    print(f"Expiration: {symbol.ExpirationDate}")
                    print(f"Strike: {symbol.StrikePrice}")
                    print(f"Type: {symbol.OptionType}")
                elif symbol.AssetType == "FUTURE":
                    print(f"Expiration: {symbol.ExpirationDate}")
                    print(f"Type: {symbol.FutureType}")
                print("---")
        else:
            print("No symbols successfully retrieved.")

        # Handle any errors
        if multi_details.Errors:
            print("\nErrors encountered:")
            for error in multi_details.Errors:
                print(f"{error.Symbol}: {error.Message}")

        # --- Example 3: Format prices using symbol details ---
        # Using MSFT details fetched earlier
        print("\n--- Example 3: Price Formatting Example (using MSFT details) ---")
        if msft_details.Symbols and msft_details.Symbols[0].PriceFormat:
            stock_format = msft_details.Symbols[0].PriceFormat
            price = Decimal("123.456")  # Use Decimal for precision
            print(f"Original Price: {price}")

            try:
                if stock_format.Format == "Decimal":
                    if stock_format.Decimals is not None:
                        # Quantize to the specified number of decimal places
                        quantizer = Decimal("1." + "0" * int(stock_format.Decimals))
                        formatted_price = price.quantize(quantizer, rounding=ROUND_HALF_UP)
                        print(f"Formatted Decimal Price: {formatted_price}")
                    else:
                        print("Decimal format specified but no decimals provided.")
                elif stock_format.Format == "Fraction":
                    if stock_format.Fraction is not None:
                        denominator = Decimal(stock_format.Fraction)
                        whole = int(price)
                        fractional_part = price - whole
                        # Round numerator to nearest whole number
                        numerator = round(fractional_part * denominator)
                        print(
                            f"Formatted Fraction Price: {whole} {int(numerator)}/{int(denominator)}"
                        )
                    else:
                        print("Fraction format specified but no denominator provided.")
                elif stock_format.Format == "SubFraction":
                    if stock_format.Fraction is not None and stock_format.SubFraction is not None:
                        denominator = Decimal(stock_format.Fraction)
                        sub_denominator_part = Decimal(
                            stock_format.SubFraction
                        )  # e.g., 2 for 1/2 of 1/32
                        sub_fraction_digits = len(
                            str(int(sub_denominator_part))
                        )  # How many digits for the sub-fraction part

                        whole = int(price)
                        fractional_part = price - whole  # e.g., 0.456

                        # Calculate the main fraction part (e.g., which 32nd)
                        main_numerator_decimal = (
                            fractional_part * denominator
                        )  # e.g., 0.456 * 32 = 14.592
                        main_numerator_whole = int(main_numerator_decimal)  # e.g., 14

                        # Calculate the sub-fraction part (e.g., the .592 part)
                        remainder_decimal = (
                            main_numerator_decimal - main_numerator_whole
                        )  # e.g., 0.592
                        # Convert remainder relative to the sub-fraction denominator (e.g., 0.592 * 2 = 1.184)
                        sub_numerator_decimal = remainder_decimal * sub_denominator_part
                        # Round the sub-numerator (e.g., round(1.184) = 1)
                        sub_numerator_rounded = round(sub_numerator_decimal)

                        print(
                            f"Formatted SubFraction Price: {whole}'{main_numerator_whole}.{int(sub_numerator_rounded):0{sub_fraction_digits}d}"
                        )
                    else:
                        print(
                            "SubFraction format specified but missing fraction or subfraction values."
                        )
                else:
                    print(f"Unsupported Price Format: {stock_format.Format}")
            except Exception as fmt_error:
                print(f"Error formatting price: {fmt_error}")
                print(f"Price Format Details: {stock_format}")
        else:
            print("Could not get price format for MSFT to demonstrate formatting.")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback

        traceback.print_exc()  # Print full traceback for debugging
    finally:
        # Ensure the client session is closed gracefully
        if "client" in locals() and client:
            print("\nClosing client session...")
            await client.close()
            print("Client session closed.")


if __name__ == "__main__":
    # Ensure the event loop is managed correctly
    try:
        asyncio.run(main())
    except RuntimeError as e:
        # Handle cases where an event loop might already be running (e.g., in Jupyter)
        if "Cannot run the event loop while another loop is running" in str(e):
            print("Detected running event loop. Attempting to attach.")
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(main())
            else:
                # This case should ideally not happen if loop.is_running() was false
                # but provides a fallback.
                print("Event loop found but not running. Starting main task.")
                loop.run_until_complete(main())
        else:
            raise  # Re-raise other RuntimeError exceptions
