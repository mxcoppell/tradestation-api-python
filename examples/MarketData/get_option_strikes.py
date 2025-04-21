import asyncio
import os

# import sys # Removed sys.path manipulation
# from pathlib import Path # Removed sys.path manipulation
from dotenv import load_dotenv

# Adjust path to include src directory - REMOVED
# current_dir = Path(__file__).parent
# project_root = current_dir.parent.parent
# sys.path.insert(0, str(project_root / "src"))

# Direct import from src directory structure
from tradestation.client.tradestation_client import TradeStationClient

# Corrected import path and class name for ApiError
from tradestation.ts_types.config import ApiError


# Load environment variables from .env file
# Ensure your .env file has CLIENT_ID, REFRESH_TOKEN, ENVIRONMENT defined.
load_dotenv()


async def main():
    """
    Main asynchronous function to demonstrate fetching option strikes.
    """
    # Instantiate the TradeStation client
    # The client automatically handles authentication using environment variables
    # Use TradeStationClient instead of TradeStation
    ts = TradeStationClient()

    # Define the underlying symbol for which to fetch option strikes
    symbol = "AAPL"  # Example symbol

    print(f"Fetching option strikes for symbol: {symbol}")

    try:
        # Call the get_option_strikes method from the market data service
        strikes = await ts.market_data.get_option_strikes(symbol)

        # Print the fetched strikes
        if strikes:
            print("\nSuccessfully fetched option strikes:")
            # Iterate through the list of strikes (assuming it's a list of numbers or strings)
            for strike in strikes:
                print(f" - {strike}")
        else:
            print("\nNo option strikes found for the specified symbol.")

    except ApiError as e:
        # Handle potential API errors
        print(f"\nError fetching option strikes: {e}")
    except Exception as e:
        # Handle other potential exceptions
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        # Ensure the client session is closed
        if ts and hasattr(ts, "http_client"):
            await ts.http_client.close()


if __name__ == "__main__":
    # Run the main asynchronous function
    # Ensure you have credentials set in your .env file or environment variables
    # Required: CLIENT_ID, REFRESH_TOKEN, ENVIRONMENT
    required_vars = [
        "CLIENT_ID",
        "REFRESH_TOKEN",
        "ENVIRONMENT",
    ]
    if not all(os.getenv(k) for k in required_vars):
        print("Error: Required environment variables for TradeStation authentication are not set.")
        print("Please create a .env file or set environment variables for:")
        print(", ".join(required_vars))
    else:
        asyncio.run(main())
