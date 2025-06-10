import asyncio
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv

# Import the specific client class
from tradestation.client import TradeStationClient


async def main() -> None:
    # Load environment variables from .env file
    load_dotenv()

    # Check if required environment variables are likely set (optional but good practice)
    if not os.getenv("CLIENT_ID") or not os.getenv("REFRESH_TOKEN") or not os.getenv("ENVIRONMENT"):
        print(
            "Warning: Ensure CLIENT_ID, REFRESH_TOKEN, and ENVIRONMENT are set in your .env file or environment."
        )
        # Depending on client implementation, it might raise an error later if missing

    # Initialize TradeStation client directly
    # It will implicitly use environment variables for credentials and environment
    client = TradeStationClient()

    print("TradeStation Client Initialized. Authentication will occur on first API call.")

    try:
        # Fetch brokerage accounts to get account IDs
        print("Fetching accounts...")
        # Use the new client variable 'client'
        accounts = await client.brokerage.get_accounts()
        if not accounts:
            print("No brokerage accounts found.")
            return

        # Select the first account ID for the example
        # NOTE: Replace with specific account IDs if needed
        account_id = accounts[0].AccountID
        print(f"Using account ID: {account_id}")

        # Define the date range for historical orders (up to 90 days prior)
        # Example: Get orders from the last 30 days
        since_date = (datetime.now() - timedelta(days=89)).strftime("%Y-%m-%d")
        print(f"Fetching historical orders since: {since_date}")

        # Fetch historical orders
        # The API handles pagination internally if page_size is not provided
        # Use the new client variable 'client'
        historical_orders_response = await client.brokerage.get_historical_orders(
            account_ids=account_id,
            since=since_date,
            # page_size=50  # Optional: Specify page size for manual pagination
        )

        # Print the fetched historical orders
        print("\nHistorical Orders:")
        if historical_orders_response.Orders:
            for order in historical_orders_response.Orders:
                print(f"  Order ID: {order.OrderID}")
                print(f"    Account ID: {order.AccountID}")
                print(f"    Status: {order.Status} ({order.StatusDescription})")
                print(f"    Opened: {order.OpenedDateTime}")
                print(f"    Closed: {order.ClosedDateTime}")
                print(f"    Type: {order.OrderType}")
                print(f"    Duration: {order.Duration}")
                if order.Legs:
                    for leg in order.Legs:
                        print(
                            f"      Leg: {leg.Symbol} ({leg.AssetType}) - {leg.BuyOrSell} {leg.QuantityOrdered} @ Exec: {leg.ExecQuantity or 'N/A'} ({leg.OpenOrClose})"
                        )
                print("---")
        else:
            print("No historical orders found for the specified period.")

        # Handle potential errors
        if historical_orders_response.Errors:
            print("\nErrors encountered:")
            for error in historical_orders_response.Errors:
                print(f"  Account ID: {error.AccountID} - Error: {error.Error} ({error.Message})")

    except Exception as e:
        print(f"\nAn error occurred: {e}")
        # Optionally add traceback for debugging
        import traceback

        traceback.print_exc()

    finally:
        # Ensure the session is closed
        # Use the new client variable 'client'
        # Add check if client exists before closing
        if "client" in locals() and client:
            await client.close()
            print("\nClient session closed.")
        else:
            print("\nClient was not initialized, skipping close.")


if __name__ == "__main__":
    asyncio.run(main())
