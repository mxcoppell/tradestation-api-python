import asyncio
import json
from dotenv import load_dotenv
from tradestation.client import TradeStationClient

# Load environment variables from .env file (default)
load_dotenv()

"""
This example demonstrates how to:
1. Set up a TradeStation client with proper authentication
2. Fetch quote snapshots for multiple symbols at once
3. Display the results in a structured way
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


def format_price(price, color=True):
    """Format a price value with optional color."""
    if not price or price == "N/A":
        return "N/A"

    return price


def format_change(change, color=True):
    """Format a change value with color."""
    if not change or change == "N/A":
        return "N/A"

    try:
        value = float(change)
        if color:
            if value > 0:
                return f"+{change}"
            elif value < 0:
                return f"{change}"
        return change
    except ValueError:
        return change


class CustomEncoder(json.JSONEncoder):
    """Handle non-serializable objects for JSON encoding."""

    def default(self, obj):
        # Convert objects to their string representation if they're not JSON serializable
        try:
            return str(obj)
        except:
            return f"[Object of type {type(obj).__name__}]"


async def main():
    client = None
    try:
        # Initialize the TradeStation client
        client = TradeStationClient()

        # Define multiple symbols to get quotes for
        symbols = ["AAPL", "SPY", "MSFT"]

        # Get quotes for multiple symbols
        print(f"\nFetching quotes for {', '.join(symbols)}...\n")
        response = await client.market_data.get_quote_snapshots(",".join(symbols))

        # Check for errors
        if hasattr(response, "Errors") and response.Errors and len(response.Errors) > 0:
            print("Errors:", response.Errors)
            return

        # Get the first quote to examine its structure
        if not response.Quotes:
            print("No quotes received")
            return

        # Define table format
        headers = ["Symbol", "Last", "Bid", "Ask", "Net Change", "Volume"]
        widths = [10, 12, 12, 12, 15, 15]

        # Print table header
        print(format_table_row(headers, widths))
        print("-" * (sum(widths) + len(widths) - 1))

        # Display the quotes
        for quote in response.Quotes:
            # Format the output for each quote using the correct attribute names
            symbol = quote.Symbol
            last = getattr(quote, "Last", "N/A")
            bid = getattr(quote, "Bid", "N/A")  # Using Bid instead of BidPrice
            ask = getattr(quote, "Ask", "N/A")  # Using Ask instead of AskPrice
            change = getattr(quote, "NetChange", "N/A")
            change_fmt = format_change(change)
            volume = getattr(quote, "Volume", "N/A")

            row_data = [symbol, last, bid, ask, change_fmt, volume]
            print(format_table_row(row_data, widths))

        print("")

        # Show additional quote details for the first symbol in pretty JSON format
        if response.Quotes:
            first_quote = response.Quotes[0]
            print(f"\nDetailed information for {first_quote.Symbol}:")
            print("=" * 60)

            # Print key information in a readable format
            print("{")

            # Get all attributes of the quote object
            attrs_to_display = []

            for attr_name in dir(first_quote):
                # Skip private attributes, methods, and model-related attributes
                if (
                    attr_name.startswith("_")
                    or callable(getattr(first_quote, attr_name))
                    or attr_name
                    in ["model_config", "model_fields", "model_computed_fields", "model_fields_set"]
                ):
                    continue

                # Get the attribute value
                attr_value = getattr(first_quote, attr_name)
                if attr_value is not None:
                    attrs_to_display.append((attr_name, attr_value))

            # Sort attributes alphabetically for better readability
            attrs_to_display.sort(key=lambda x: x[0])

            # Print each attribute on a separate line with proper indentation
            for i, (attr_name, attr_value) in enumerate(attrs_to_display):
                # Format the attribute value
                if isinstance(attr_value, str):
                    formatted_value = f'"{attr_value}"'
                elif attr_name == "MarketFlags":
                    # Handle MarketFlags object specially
                    mf_str = str(attr_value)

                    # Format the MarketFlags as a simple dictionary
                    formatted_value = "{\n"

                    # Extract flag names and values using attribute access if available
                    if hasattr(attr_value, "IsBats"):
                        formatted_value += f'      "IsBats": {attr_value.IsBats},\n'
                    if hasattr(attr_value, "IsDelayed"):
                        formatted_value += f'      "IsDelayed": {attr_value.IsDelayed},\n'
                    if hasattr(attr_value, "IsHalted"):
                        formatted_value += f'      "IsHalted": {attr_value.IsHalted},\n'
                    if hasattr(attr_value, "IsHardToBorrow"):
                        formatted_value += f'      "IsHardToBorrow": {attr_value.IsHardToBorrow}\n'

                    formatted_value += "    }"
                else:
                    formatted_value = str(attr_value)

                # Add comma for all but the last element
                comma = "," if i < len(attrs_to_display) - 1 else ""

                # Print with proper indentation
                print(f'  "{attr_name}": {formatted_value}{comma}')

            print("}")

    except Exception as error:
        # Handle any errors that occur during the request
        print(f"Error: {str(error)}")
        import traceback

        print(f"Stack trace: {traceback.format_exc()}")
    finally:
        # Close the client to clean up resources
        if client:
            await client.http_client.close()


# Run the example
if __name__ == "__main__":
    asyncio.run(main())
