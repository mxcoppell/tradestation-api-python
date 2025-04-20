import asyncio
import os
import random  # Import random to pick a random order

from dotenv import load_dotenv

# Import the specific client class
from src.client.tradestation_client import TradeStationClient


# Helper function to print order details cleanly
def print_order_details(order, prefix=""):
    print(f"{prefix}Order ID: {order.OrderID}")
    print(f"{prefix}  Account ID: {order.AccountID}")
    print(f"{prefix}  Status: {order.Status} ({order.StatusDescription})")
    print(f"{prefix}  Opened: {order.OpenedDateTime}")
    print(f"{prefix}  Type: {order.OrderType}")
    print(f"{prefix}  Duration: {order.Duration}")
    if order.Legs:
        for leg in order.Legs:
            print(
                f"{prefix}    Leg: {leg.Symbol} ({leg.AssetType}) - {leg.BuyOrSell} {leg.QuantityOrdered} @ Exec: {leg.ExecQuantity or 'N/A'} ({leg.OpenOrClose})"
            )
    print(f"{prefix}---")


async def main() -> None:
    # Load environment variables from .env file
    load_dotenv()

    # Check if required environment variables are likely set (optional but good practice)
    if not os.getenv("CLIENT_ID") or not os.getenv("REFRESH_TOKEN") or not os.getenv("ENVIRONMENT"):
        print(
            "Warning: Ensure CLIENT_ID, REFRESH_TOKEN, and ENVIRONMENT are set in your .env file or environment."
        )
        # Depending on client implementation, it might raise an error later if missing
        return  # Stop execution if required variables are missing

    # Initialize TradeStation client directly
    # It will implicitly use environment variables for credentials and environment
    client = TradeStationClient()

    print("TradeStation Client Initialized. Authentication will occur on first API call.")

    try:
        # --- Step 1: Fetch brokerage accounts to get account IDs ---
        print("Fetching accounts...")
        accounts = await client.brokerage.get_accounts()
        if not accounts:
            print("No brokerage accounts found.")
            return

        all_account_ids_list = [acc.AccountID for acc in accounts]
        all_account_ids_str = ",".join(all_account_ids_list)
        print(f"Found account IDs: {all_account_ids_str}")

        # --- Step 2: Fetch current orders to get a sample OrderID ---
        print(f"Fetching current orders for all accounts: {all_account_ids_str}")
        orders_response = await client.brokerage.get_orders(
            account_ids=all_account_ids_str,
        )

        # Check for errors in the response
        if hasattr(orders_response, "Errors") and orders_response.Errors:
            print("Errors encountered while fetching orders:")
            for error in orders_response.Errors:
                print(f"  Account ID: {error.AccountID} - Error: {error.Error} ({error.Message})")
            # Optionally, decide if you want to stop if there are errors
            # return

        # Extract a valid OrderID to use for the get_order_by_id call
        target_order_id = None
        if orders_response.Orders:
            print("Found Current Orders:")
            # Just print the first few to keep output manageable
            for order in orders_response.Orders[:5]:
                print_order_details(order, prefix="  ")
            if len(orders_response.Orders) > 5:
                print("  ... and more.")

            # Pick a random order ID from the list
            target_order = random.choice(orders_response.Orders)
            target_order_id = target_order.OrderID
            print(f"Selected Order ID for detailed fetch: {target_order_id}")
        else:
            print("No current orders found. Cannot proceed to fetch by OrderID.")
            return

        # --- Step 3: Fetch a specific order using the selected OrderID ---
        if target_order_id:
            print(
                f"Fetching details for specific Order ID: {target_order_id} across accounts: {all_account_ids_str}"
            )
            # The API expects a comma-separated string of account IDs and order IDs
            order_detail_response = await client.brokerage.get_orders_by_order_id(
                account_ids=all_account_ids_str,  # Pass all accounts where the order might be
                order_ids=target_order_id,  # Pass the single target order ID as a string
            )

            # Print the detailed order information
            # The response structure might be slightly different, adjust printing as needed
            # It might return a list of orders even when fetching one ID
            if order_detail_response.Orders:
                print("Detailed Order Information:")
                # Assuming it returns a list, even if just one item
                for order in order_detail_response.Orders:
                    print_order_details(order, prefix="  ")
            else:
                print(f"Could not retrieve details for Order ID: {target_order_id}")

            # Handle potential errors specifically for the get_order_by_id call
            if hasattr(order_detail_response, "Errors") and order_detail_response.Errors:
                print("Errors encountered while fetching specific order:")
                for error in order_detail_response.Errors:
                    # Error structure might differ, adjust accordingly
                    print(
                        f"  Error: {error.Error} ({error.Message}) for OrderID: {target_order_id}"
                    )  # Assuming Error has these fields

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # Optionally add traceback for debugging
        import traceback

        traceback.print_exc()

    finally:
        # Ensure the session is closed
        if "client" in locals() and client:
            await client.close()
            print("Client session closed.")
        else:
            print("Client was not initialized, skipping close.")


if __name__ == "__main__":
    # Ensure the .env file is present and contains the required variables
    if not os.path.exists(".env"):
        print(
            "Error: .env file not found. Please create one with CLIENT_ID, REFRESH_TOKEN, and ENVIRONMENT."
        )
    elif (
        not os.getenv("CLIENT_ID") or not os.getenv("REFRESH_TOKEN") or not os.getenv("ENVIRONMENT")
    ):
        # Double-check after attempting load_dotenv in main
        pass  # Already handled inside main, but good to check here too if needed.
    else:
        asyncio.run(main())
