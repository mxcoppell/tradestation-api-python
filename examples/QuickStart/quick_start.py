import asyncio
import json
import os

from dotenv import load_dotenv

from tradestation.client import TradeStationClient

# Load environment variables from .env file (default)
load_dotenv()

"""
This example demonstrates how to:
1. Set up a TradeStation client with proper authentication
2. Make API requests with automatic rate limiting
3. Get symbol definition for AAPL
4. Handle the response and potential errors

Required environment variables (.env):
- CLIENT_ID: Your TradeStation API client ID (Mandatory)
- REFRESH_TOKEN: Your TradeStation refresh token (Mandatory)
- ENVIRONMENT: 'Simulation' or 'Live' (Mandatory)
"""


def format_table_row(columns, widths):
    """Format a row of data with proper column widths."""
    row = ""
    for i, col in enumerate(columns):
        row += str(col).ljust(widths[i]) + " "
    return row


class SymbolEncoder(json.JSONEncoder):
    """Custom JSON encoder for symbol objects to clean up the output."""

    def default(self, obj):
        if hasattr(obj, "__dict__"):
            # Filter out internal model fields and methods
            cleaned_dict = {}
            for key, value in obj.__dict__.items():
                if not key.startswith("_") and key not in [
                    "model_config",
                    "model_fields",
                    "model_computed_fields",
                    "model_fields_set",
                ]:
                    cleaned_dict[key] = value
            return cleaned_dict
        return super().default(obj)


async def main():
    try:
        print("Verifying environment variables...")
        print(f"CLIENT_ID: {os.getenv('CLIENT_ID') if os.getenv('CLIENT_ID') else '✗ (not set)'}")
        print(
            f"REFRESH_TOKEN: {os.getenv('REFRESH_TOKEN') if os.getenv('REFRESH_TOKEN') else '✗ (not set)'}"
        )
        print(f"ENVIRONMENT: {os.getenv('ENVIRONMENT') or 'not set (using Simulation default)'}")

        # Initialize the TradeStation client
        # The client will automatically:
        # - Load credentials from environment variables
        # - Handle authentication using refresh token
        # - Manage rate limiting
        client = TradeStationClient()

        # Get symbol definition for AAPL
        print("\nFetching symbol definition for AAPL...")
        response = await client.market_data.get_symbol_details("AAPL")

        # Check for errors
        if hasattr(response, "Errors") and response.Errors and len(response.Errors) > 0:
            print("Errors:", response.Errors)
            return

        # Get the symbol details (first item in the array)
        symbol = response.Symbols[0]

        # Display the results in a structured format using JSON
        print("\nSymbol Details:")
        print("=" * 60)

        # Build symbol info dictionary for better display
        symbol_info = {
            "Symbol": symbol.Symbol,
            "AssetType": symbol.AssetType,
            "Description": symbol.Description,
            "Exchange": symbol.Exchange,
            "Country": symbol.Country,
            "Currency": symbol.Currency,
        }

        # Print symbol info as JSON
        print(json.dumps(symbol_info, indent=2))

        # Display price and quantity formatting
        print("\nFormatting Rules:")
        print("=" * 60)

        # Create a table for the formatting rules
        headers = [
            "Format Type",
            "Format",
            "Decimals",
            "Increment Style",
            "Increment",
            "Min Quantity",
        ]
        widths = [15, 12, 12, 18, 12, 15]

        print(format_table_row(headers, widths))
        print("-" * (sum(widths) + len(widths) - 1))

        # Price format row
        price_row = [
            "Price",
            symbol.PriceFormat.Format,
            symbol.PriceFormat.Decimals,
            symbol.PriceFormat.IncrementStyle,
            symbol.PriceFormat.Increment,
            "",  # No min quantity for price
        ]
        print(format_table_row(price_row, widths))

        # Quantity format row
        quantity_row = [
            "Quantity",
            symbol.QuantityFormat.Format,
            symbol.QuantityFormat.Decimals,
            "",  # No increment style for quantity
            symbol.QuantityFormat.Increment,
            symbol.QuantityFormat.MinimumTradeQuantity,
        ]
        print(format_table_row(quantity_row, widths))

        print("")

        # Example of formatting a price using the symbol's price format
        example_price = 123.456789
        print("\nPrice Formatting Example:")
        print("=" * 60)

        print(f"Raw Price: {example_price}")
        if symbol.PriceFormat.Format == "Decimal" and symbol.PriceFormat.Decimals:
            formatted_price = f"{example_price:.{int(symbol.PriceFormat.Decimals)}f}"
            print(
                f"Formatted Price: {formatted_price} (using {symbol.PriceFormat.Decimals} decimals)"
            )

        # Full symbol details as JSON
        print("\nComplete Symbol Definition:")
        print("=" * 60)

        # Extract key format information into clean objects
        price_format = {
            "Format": symbol.PriceFormat.Format,
            "Decimals": symbol.PriceFormat.Decimals,
            "IncrementStyle": symbol.PriceFormat.IncrementStyle,
            "Increment": symbol.PriceFormat.Increment,
            "PointValue": (
                symbol.PriceFormat.PointValue if hasattr(symbol.PriceFormat, "PointValue") else None
            ),
        }

        quantity_format = {
            "Format": symbol.QuantityFormat.Format,
            "Decimals": symbol.QuantityFormat.Decimals,
            "IncrementStyle": (
                symbol.QuantityFormat.IncrementStyle
                if hasattr(symbol.QuantityFormat, "IncrementStyle")
                else None
            ),
            "Increment": symbol.QuantityFormat.Increment,
            "MinimumTradeQuantity": symbol.QuantityFormat.MinimumTradeQuantity,
        }

        # Build clean symbol dictionary
        clean_symbol = {
            "Symbol": symbol.Symbol,
            "Root": symbol.Root,
            "AssetType": symbol.AssetType,
            "Description": symbol.Description,
            "Exchange": symbol.Exchange,
            "Country": symbol.Country,
            "Currency": symbol.Currency,
            "PriceFormat": price_format,
            "QuantityFormat": quantity_format,
        }

        # Print with nice formatting
        print(json.dumps(clean_symbol, indent=2))

    except Exception as error:
        # Handle any errors that occur during the request
        print(f"Error: {str(error)}")
        import traceback

        print(f"Stack trace: {traceback.format_exc()}")
    finally:
        # Close the client to clean up resources
        if "client" in locals():
            await client.close()


# Run the example
if __name__ == "__main__":
    asyncio.run(main())
