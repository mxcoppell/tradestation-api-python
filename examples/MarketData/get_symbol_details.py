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
from src.tradestation import TradeStationClient  # Adjust import based on your project structure

# Load environment variables from .env file
load_dotenv()


async def main():
    """
    Main asynchronous function to demonstrate fetching symbol details.
    """
    # Initialize the TradeStation client
    # The client automatically handles authentication using environment variables:
    # TRADESTATION_CLIENT_ID, TRADESTATION_CLIENT_SECRET, TRADESTATION_PAPER_ACCOUNT, TRADESTATION_REFRESH_TOKEN
    client = TradeStationClient()

    try:
        # --- Example 1: Get details for a single stock ---
        print("\n--- Example 1: Get details for MSFT ---")
        msft_details = await client.market_data.get_symbol_details("MSFT")

        if msft_details.errors:
            print(f"Error fetching MSFT details: {msft_details.errors[0].message}")
        elif msft_details.symbols:
            msft_symbol = msft_details.symbols[0]
            print(f"Asset Type: {msft_symbol.asset_type}")
            print(f"Description: {msft_symbol.description}")
            print(f"Exchange: {msft_symbol.exchange}")
            print(f"Currency: {msft_symbol.currency}")
            if msft_symbol.price_format:
                print(
                    "Price Format:",
                    {
                        "format": msft_symbol.price_format.format,
                        "decimals": (
                            msft_symbol.price_format.decimals
                            if msft_symbol.price_format.decimals is not None
                            else "N/A"
                        ),
                        "increment": msft_symbol.price_format.increment,
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
        if multi_details.symbols:
            for symbol in multi_details.symbols:
                print(f"\n{symbol.symbol} ({symbol.asset_type}):")
                print(f"Description: {symbol.description}")
                print(f"Exchange: {symbol.exchange}")
                if symbol.price_format:
                    decimals_str = (
                        symbol.price_format.decimals
                        if symbol.price_format.decimals is not None
                        else "N/A"
                    )
                    print(f"Price Format: {symbol.price_format.format} ({decimals_str} decimals)")
                else:
                    print("Price Format: N/A")

                # Asset-specific properties
                if symbol.asset_type == "STOCKOPTION":
                    print(f"Expiration: {symbol.expiration_date}")
                    print(f"Strike: {symbol.strike_price}")
                    print(f"Type: {symbol.option_type}")
                elif symbol.asset_type == "FUTURE":
                    print(f"Expiration: {symbol.expiration_date}")
                    print(f"Type: {symbol.future_type}")
                print("---")
        else:
            print("No symbols successfully retrieved.")

        # Handle any errors
        if multi_details.errors:
            print("\nErrors encountered:")
            for error in multi_details.errors:
                print(f"{error.symbol}: {error.message}")

        # --- Example 3: Format prices using symbol details ---
        # Using MSFT details fetched earlier
        print("\n--- Example 3: Price Formatting Example (using MSFT details) ---")
        if msft_details.symbols and msft_details.symbols[0].price_format:
            stock_format = msft_details.symbols[0].price_format
            price = Decimal("123.456")  # Use Decimal for precision
            print(f"Original Price: {price}")

            try:
                if stock_format.format == "Decimal":
                    if stock_format.decimals is not None:
                        # Quantize to the specified number of decimal places
                        quantizer = Decimal("1." + "0" * int(stock_format.decimals))
                        formatted_price = price.quantize(quantizer, rounding=ROUND_HALF_UP)
                        print(f"Formatted Decimal Price: {formatted_price}")
                    else:
                        print("Decimal format specified but no decimals provided.")
                elif stock_format.format == "Fraction":
                    if stock_format.fraction is not None:
                        denominator = Decimal(stock_format.fraction)
                        whole = int(price)
                        fractional_part = price - whole
                        # Round numerator to nearest whole number
                        numerator = round(fractional_part * denominator)
                        print(
                            f"Formatted Fraction Price: {whole} {int(numerator)}/{int(denominator)}"
                        )
                    else:
                        print("Fraction format specified but no denominator provided.")
                elif stock_format.format == "SubFraction":
                    if stock_format.fraction is not None and stock_format.sub_fraction is not None:
                        denominator = Decimal(stock_format.fraction)
                        sub_denominator_part = Decimal(
                            stock_format.sub_fraction
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
                    print(f"Unsupported Price Format: {stock_format.format}")
            except Exception as fmt_error:
                print(f"Error formatting price: {fmt_error}")
                print(f"Price Format Details: {stock_format}")
        else:
            print("Could not get price format for MSFT to demonstrate formatting.")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback

        traceback.print_exc()  # Print full traceback for debugging


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
