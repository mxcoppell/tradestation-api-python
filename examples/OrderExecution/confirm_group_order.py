#!/usr/bin/env python
"""
Example demonstrating how to get confirmation details (quotes) for a potential group order
using the TradeStation API.

This example shows how to:
1. Initialize the TradeStation client.
2. Fetch available brokerage accounts.
3. Construct a sample Group Order request (e.g., OCO or BRK).
4. Call the `confirm_group_order` endpoint to get quote details for the proposed group order.
5. Process and display the confirmation results (e.g., estimated costs, messages).

Note: This endpoint provides confirmation details (quotes) for a *potential* order group.
It does not place the order. The actual order placement happens via a different endpoint
(e.g., `place_group_order`).

Usage:
    python confirm_group_order.py

Requirements:
    - A valid TradeStation account with brokerage services enabled.
    - API credentials (CLIENT_ID, REFRESH_TOKEN) and ENVIRONMENT in a .env file.
    - Correct account permissions and market conditions for the specified order.
"""

import asyncio
import os
from dotenv import load_dotenv
from typing import List
import aiohttp  # Import aiohttp for the exception type

# Import the client
from src.client.tradestation_client import TradeStationClient

# Removed incorrect exception import
# from src.client.exceptions import HTTPException

# Import necessary types from the order execution definitions
from src.ts_types.order_execution import (
    GroupOrderRequest,
    OrderRequest,
    TimeInForce,
    OrderType,
    OrderSide,
    OrderDuration,
    GroupOrderConfirmationResponse,
)
from src.ts_types.brokerage import Account  # Assuming Account type is here


async def main():
    """Main function to demonstrate confirming a group order."""
    # Load environment variables from .env file
    load_dotenv()

    # Initialize the TradeStation client
    ts_client = TradeStationClient()

    try:
        # --- 1. Fetch Accounts ---
        # We need an account ID to specify in the order request.
        print("\nFetching accounts...")
        accounts: List[Account] = await ts_client.brokerage.get_accounts()

        if not accounts:
            print("No brokerage accounts found.")
            return

        # Use the first available account ID
        account_id = accounts[0].AccountID
        print(f"Using Account ID: {account_id}")

        # --- 2. Construct Sample OCO Group Order Request ---
        # IMPORTANT: The values below (symbol, prices, quantity) are examples.
        # They might need adjustment based on your account permissions, market conditions,
        # and the specific environment (simulation vs. live).
        print("\nConstructing sample OCO order request for MSFT...")
        oco_group_request = GroupOrderRequest(
            Type="OCO",
            Orders=[
                OrderRequest(
                    AccountID=account_id,
                    Symbol="MSFT",
                    Quantity="1",
                    OrderType=OrderType.LIMIT,
                    LimitPrice="380.00",  # Adjust price as needed
                    TradeAction=OrderSide.BUY,
                    TimeInForce=TimeInForce(Duration=OrderDuration.DAY),
                    Route="Intelligent",  # Verify route validity
                ),
                OrderRequest(
                    AccountID=account_id,
                    Symbol="MSFT",
                    Quantity="1",
                    OrderType=OrderType.STOP_LIMIT,
                    StopPrice="375.00",  # Adjust price as needed
                    LimitPrice="374.50",  # Adjust price as needed
                    TradeAction=OrderSide.BUY,
                    TimeInForce=TimeInForce(Duration=OrderDuration.DAY),
                    Route="Intelligent",  # Verify route validity
                ),
            ],
        )

        # --- 3. Confirm the OCO Group Order ---
        print("\nConfirming OCO Order Group (getting quote details)...")
        oco_confirmation: GroupOrderConfirmationResponse = (
            await ts_client.order_execution.confirm_group_order(request=oco_group_request)
        )

        # --- 4. Process and Display OCO Confirmation Results ---
        print("\nOCO Group Confirmation Details:")
        if oco_confirmation.Orders:
            print("  Confirmed Orders:")
            for order_confirm in oco_confirmation.Orders:
                # Note: The response object here is GroupOrderResponseSuccess inside the list
                print(f"    - OrderID: {order_confirm.OrderID}, Message: {order_confirm.Message}")
        if oco_confirmation.Errors:
            print("  Errors:")
            for error in oco_confirmation.Errors:
                # Note: The response object here is GroupOrderResponseError inside the list
                print(
                    f"    - OrderID: {error.OrderID}, Error: {error.Error}, Message: {error.Message}"
                )
        # Display the full response object for more details if needed
        # print("\nRaw OCO Confirmation Response:")
        # print(oco_confirmation.model_dump_json(indent=2))

        # --- Example 2: Construct and Confirm a Bracket Order ---
        # (Similar structure can be followed for BRK type based on TS example)
        # print("\nConfirming Bracket Order Group for AAPL...")
        # bracket_group_request = GroupOrderRequest(Type="BRK", Orders=[...])
        # bracket_confirmation = await ts_client.order_execution.confirm_group_order(request=bracket_group_request)
        # print("Bracket Group Confirmation Details:", bracket_confirmation.model_dump_json(indent=2))

    except aiohttp.ClientResponseError as e:
        print(
            f"\nHTTP ERROR occurred during confirmation: Status={e.status}, Message='{e.message}'"
        )
        print("  Potential causes:")
        print(
            "    - Invalid parameters in the request (check prices, quantity, symbol, route). Verify Route is valid."
        )
        print("    - Insufficient permissions/funds for the account or instrument.")
        print("    - Attempting confirmation outside market hours or when the market is closed.")
        print(
            "    - Issues specific to the simulation environment (e.g., symbol availability, different rules)."
        )
        print(f"  Request URL: {e.request_info.url}")
        print(f"  Request Headers: {e.request_info.headers}")
        print(f"  Response Headers: {e.headers}")
    except AttributeError as e:
        print(f"ERROR: Could not find necessary method or attribute: {e}")
        print(
            "       Please ensure the brokerage and order_execution services/methods are implemented correctly."
        )
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        # import traceback
        # traceback.print_exc()
    finally:
        # --- 5. Close Client Session ---
        await ts_client.close()
        print("\nClient session closed.")


if __name__ == "__main__":
    asyncio.run(main())
