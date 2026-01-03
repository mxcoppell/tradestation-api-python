#!/usr/bin/env python
"""
Example demonstrating how to fetch historical orders by order ID using the TradeStation API.

This example shows how to:
1. Initialize the TradeStation client
2. Fetch historical orders for specific order IDs
3. Process and display the order information

Usage:
    python get_historical_orders_by_order_id.py

Requirements:
    - A valid TradeStation account
    - API credentials in .env file
"""

import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

from tradestation.client import TradeStationClient


async def main():
    """Main function to demonstrate fetching historical orders by order ID."""
    # Load environment variables from .env file
    load_dotenv()

    # Initialize the TradeStation client
    client = TradeStationClient(debug=True)

    # Get account IDs from environment or use default
    account_ids = os.getenv("ACCOUNT_IDS", "")
    if not account_ids:
        print("No account IDs found in environment. Please set ACCOUNT_IDS in .env file.")
        return

    # Get order IDs from environment or use default
    order_ids = os.getenv("ORDER_IDS", "")
    if not order_ids:
        print("No order IDs found in environment. Please set ORDER_IDS in .env file.")
        return

    # Set the since date (30 days ago)
    since_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    try:
        # Fetch historical orders by order ID
        print(
            f"Fetching historical orders for account(s) {account_ids} and order(s) {order_ids} since {since_date}..."
        )
        historical_orders = await client.brokerage_service.get_historical_orders_by_order_id(
            account_ids=account_ids, order_ids=order_ids, since=since_date
        )

        # Process and display the results
        if historical_orders.Orders:
            print(f"Found {len(historical_orders.Orders)} historical orders:")
            for order in historical_orders.Orders:
                print(f"\nOrder ID: {order.OrderID}")
                print(f"  Account ID: {order.AccountID}")
                print(f"  Status: {order.Status} - {order.StatusDescription}")
                print(f"  Order Type: {order.OrderType}")
                print(f"  Opened: {order.OpenedDateTime}")
                print(
                    f"  Closed: {order.ClosedDateTime if hasattr(order, 'ClosedDateTime') else 'N/A'}"
                )

                if order.Legs:
                    print(f"  Legs ({len(order.Legs)}):")
                    for i, leg in enumerate(order.Legs, 1):
                        print(f"    Leg {i}:")
                        print(f"      Symbol: {leg.Symbol}")
                        print(f"      Action: {leg.BuyOrSell} {leg.OpenOrClose}")
                        print(
                            f"      Quantity: {leg.QuantityOrdered} (Filled: {leg.ExecQuantity}, Remaining: {leg.QuantityRemaining})"
                        )
                        print(f"      Execution Price: {leg.ExecutionPrice}")
        else:
            print("No historical orders found for the specified criteria.")

        # Check for errors
        if historical_orders.Errors:
            print("\nErrors:")
            for error in historical_orders.Errors:
                print(
                    f"  Account {error.AccountID}, Order {error.OrderID}: {error.Error} - {error.Message}"
                )

    except Exception as e:
        print(f"Error fetching historical orders: {e}")


if __name__ == "__main__":
    asyncio.run(main())
