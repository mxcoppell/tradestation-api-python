import asyncio
import os
from datetime import datetime, timedelta  # Keep datetime/timedelta in case needed later

from dotenv import load_dotenv

# Import the specific client class
from src.client.tradestation_client import TradeStationClient


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

        # Get all account IDs
        all_account_ids_list = [acc.AccountID for acc in accounts]
        all_account_ids_str = ",".join(all_account_ids_list)
        print(f"Found account IDs: {all_account_ids_str}")

        # Fetch current orders (no date range needed for get_orders)
        print(f"Fetching current orders for all accounts: {all_account_ids_str}")

        # Fetch current orders for all selected accounts
        # The API requires a comma-separated string of account IDs
        orders_response = await client.brokerage.get_orders(
            account_ids=all_account_ids_str,  # Pass the comma-separated string
        )

        # Print the fetched orders
        print("\nCurrent Orders:")
        if orders_response.Orders:
            # Group orders by account ID for cleaner printing (optional but nice)
            orders_by_account = {}
            for order in orders_response.Orders:
                if order.AccountID not in orders_by_account:
                    orders_by_account[order.AccountID] = []
                orders_by_account[order.AccountID].append(order)

            if not orders_by_account:
                print("No current orders found across all accounts.")
            else:
                for acc_id, orders_list in orders_by_account.items():
                    print(f"\n--- Orders for Account ID: {acc_id} ---")
                    for order in orders_list:
                        print(f"  Order ID: {order.OrderID}")
                        # Account ID is already printed above for the group
                        # print(f"    Account ID: {order.AccountID}")
                        print(f"    Status: {order.Status} ({order.StatusDescription})")
                        print(f"    Opened: {order.OpenedDateTime}")
                        # Current orders won't have a ClosedDateTime typically
                        # print(f"    Closed: {order.ClosedDateTime}")
                        print(f"    Type: {order.OrderType}")
                        print(f"    Duration: {order.Duration}")
                        if order.Legs:
                            for leg in order.Legs:
                                print(
                                    f"      Leg: {leg.Symbol} ({leg.AssetType}) - {leg.BuyOrSell} {leg.QuantityOrdered} @ Exec: {leg.ExecQuantity or 'N/A'} ({leg.OpenOrClose})"
                                )
                        print("---")
        else:
            print("No current orders found across all accounts.")

        # Handle potential errors (structure might differ slightly for get_orders, adjust if needed)
        # Assuming the OrdersResponse structure includes an Errors field similar to HistoricalOrdersResponse
        if hasattr(orders_response, "Errors") and orders_response.Errors:
            print("\nErrors encountered:")
            for error in orders_response.Errors:
                print(f"  Account ID: {error.AccountID} - Error: {error.Error} ({error.Message})")

    except Exception as e:
        print("\nAn error occurred: {e}")
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
