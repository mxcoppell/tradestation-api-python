#!/usr/bin/env python
"""
Example demonstrating placing a group OCO order, querying it, cancelling it,
and querying again using the TradeStation API.

This example shows how to:
1. Initialize the TradeStation client.
2. Fetch available brokerage accounts (specifically looking for a margin account).
3. Get a quote for a symbol (MSFT).
4. Calculate limit and stop prices based on the quote (5%, 6%, 7% below last).
5. Place a group OCO (One-Cancels-Other) order with two legs:
   - Leg 1: Limit Buy order (GTC)
   - Leg 2: Stop Limit Buy order (GTC)
6. Extract the OrderIDs from the placement response.
7. Query orders for the account to find the newly placed group orders.
8. Cancel the placed orders using their OrderIDs.
9. Query orders again to verify the cancellation status.

NOTE: This script places and cancels real orders in the specified environment (SIM/LIVE).
      Ensure you have sufficient buying power and understand the implications.

Usage:
    python examples/OrderExecution/place_and_cancel_group_order.py

Requirements:
    - A valid TradeStation account with brokerage services and a margin account.
    - API credentials (CLIENT_ID, REFRESH_TOKEN) and ENVIRONMENT in a .env file.
    - Correct account permissions and market conditions for the specified order.
    - Sufficient buying power for the order.
"""

import asyncio
import traceback
from decimal import ROUND_DOWN, Decimal
from typing import Dict, List, Optional

import aiohttp
from dotenv import load_dotenv
from pydantic import ValidationError

# Import the client
from tradestation.client import TradeStationClient

# Import necessary types
from tradestation.ts_types.brokerage import Account, Order, Orders
from tradestation.ts_types.market_data import Quote, QuoteSnapshot
from tradestation.ts_types.order_execution import (
    CancelOrderResponse,
    GroupOrderRequest,
    GroupOrderResponse,
    OrderDuration,
    OrderRequest,
    OrderSide,
    OrderType,
    TimeInForce,
)


async def find_margin_account(client: TradeStationClient) -> Optional[str]:
    """Fetches accounts and returns the ID of the first margin account found."""
    print("\n--- 1. Fetching Accounts ---")
    try:
        accounts: List[Account] = await client.brokerage.get_accounts()
        if not accounts:
            print("ERROR: No brokerage accounts found.")
            return None
        for account in accounts:
            if account.AccountID.endswith("M"):
                print(f"Found Margin Account ID: {account.AccountID}")
                return account.AccountID
        print("ERROR: No margin account (AccountID ending with 'M') found.")
        return None
    except Exception as e:
        print(f"ERROR fetching accounts: {e}")
        return None


async def get_last_price(client: TradeStationClient, symbol: str) -> Optional[Decimal]:
    """Gets the last price for a symbol from quote snapshots."""
    print(f"\n--- 2. Fetching Quote for {symbol} ---")
    try:
        quotes_response: QuoteSnapshot = await client.market_data.get_quote_snapshots([symbol])
        if quotes_response.Quotes and len(quotes_response.Quotes) > 0:
            quote = quotes_response.Quotes[0]
            if quote.Last:
                last_price = Decimal(quote.Last)
                print(f"  Last price for {symbol}: {last_price}")
                return last_price
            else:
                print(f"  No 'Last' price found in quote for {symbol}.")
                return None
        elif quotes_response.Errors:
            print(f"  Errors fetching quote for {symbol}: {quotes_response.Errors}")
            return None
        else:
            print(f"  No quote data returned for {symbol}.")
            return None
    except Exception as e:
        print(f"ERROR fetching quote for {symbol}: {e}")
        return None


def calculate_prices(last_price: Decimal) -> Dict[str, str]:
    """Calculates limit and stop prices based on percentages below the last price."""
    print("\n--- 3. Calculating Order Prices ---")
    limit_price_5_pct = (last_price * Decimal("0.95")).quantize(
        Decimal("0.01"), rounding=ROUND_DOWN
    )
    stop_price_6_pct = (last_price * Decimal("0.94")).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
    limit_price_7_pct = (last_price * Decimal("0.93")).quantize(
        Decimal("0.01"), rounding=ROUND_DOWN
    )

    print(f"  Limit Price (5% below {last_price}): {limit_price_5_pct}")
    print(f"  Stop Price (6% below {last_price}): {stop_price_6_pct}")
    print(f"  Stop Limit Price (7% below {last_price}): {limit_price_7_pct}")

    return {
        "limit_5": str(limit_price_5_pct),
        "stop_6": str(stop_price_6_pct),
        "limit_7": str(limit_price_7_pct),
    }


async def place_oco_group_order(
    client: TradeStationClient, account_id: str, symbol: str, quantity: str, prices: Dict[str, str]
) -> List[str]:
    """Places an OCO group order and returns the OrderIDs if successful."""
    print(f"\n--- 4. Placing OCO Group Order for {quantity} {symbol} ---")
    order_ids = []
    oco_group_request = GroupOrderRequest(
        Type="OCO",
        Orders=[
            # Leg 1: Limit Buy 5% below last
            OrderRequest(
                AccountID=account_id,
                Symbol=symbol,
                Quantity=quantity,
                OrderType=OrderType.LIMIT,
                LimitPrice=prices["limit_5"],
                TradeAction=OrderSide.BUY,
                TimeInForce=TimeInForce(Duration=OrderDuration.GTC),  # Good Till Cancelled
                Route="Intelligent",
            ),
            # Leg 2: Stop Limit Buy 7% below last, Stop at 6% below last
            OrderRequest(
                AccountID=account_id,
                Symbol=symbol,
                Quantity=quantity,
                OrderType=OrderType.STOP_LIMIT,
                StopPrice=prices["stop_6"],
                LimitPrice=prices["limit_7"],
                TradeAction=OrderSide.BUY,
                TimeInForce=TimeInForce(Duration=OrderDuration.GTC),  # Good Till Cancelled
                Route="Intelligent",
            ),
        ],
    )

    try:
        response: GroupOrderResponse = await client.order_execution.place_group_order(
            request=oco_group_request
        )

        print(f"  Full Place Group Order Response:\n{response.model_dump_json(indent=2)}")

        # Simplified: Check for top-level errors first
        if response.Errors:
            for error in response.Errors:
                print(
                    f"  TOP LEVEL ERROR placing group order: {error.Error} - {error.Message} (OrderID: {error.OrderID})"
                )
            print("  Group order placement failed due to top-level errors.")
            return []

        # Extract OrderIDs from successful placements in the Orders list
        if response.Orders:
            for order_resp in response.Orders:
                # Directly check for OrderID which indicates success for this leg
                if order_resp.OrderID:
                    print(f"  Order Leg Placed Successfully! OrderID: {order_resp.OrderID}")
                    order_ids.append(order_resp.OrderID)
                else:
                    # This path shouldn't normally be hit if no top-level errors, but log just in case
                    print(
                        f"  WARNING: Received an item in Orders list without an OrderID: {order_resp}"
                    )

        # Final check: ensure we got the expected number of IDs if no errors
        if not order_ids:
            print(
                "  ERROR: Group order placement reported no top-level errors, but no OrderIDs were extracted."
            )
            return []

        if len(order_ids) != len(oco_group_request.Orders):
            print(
                f"  WARNING: Placed {len(order_ids)} orders, but requested {len(oco_group_request.Orders)}. Check response carefully."
            )
            # Proceeding with the IDs we got

        return order_ids

    except aiohttp.ClientResponseError as e:
        print(f"HTTP ERROR placing group order: Status={e.status}, Message='{e.message}'")
        try:
            error_body = await e.text()
            print(f"  Response Body: {error_body}")
        except Exception as body_e:
            print(f"  (Could not read error response body: {body_e})")
        return []
    except ValidationError as ve:
        print(f"Pydantic Validation FAILED during group order placement:")
        print(ve)
        return []
    except Exception as e:
        print(f"Unexpected ERROR placing group order: {type(e).__name__} - {e}")
        traceback.print_exc()
        return []


async def query_and_display_orders(
    client: TradeStationClient,
    account_id: str,
    order_ids_to_find: List[str],
    query_description: str,
):
    """Queries orders for the account and displays status for specific OrderIDs."""
    print(f"\n--- {query_description} ---")
    if not order_ids_to_find:
        print("  No Order IDs provided to query.")
        return

    try:
        orders_response: Orders = await client.brokerage.get_orders(
            account_ids=account_id, page_size=200
        )

        if orders_response.Errors:
            print("  Errors reported while querying orders:")
            for error in orders_response.Errors:
                print(f"    - Account {error.AccountID}: {error.Error} - {error.Message}")

        if not orders_response.Orders:
            print(f"  No orders found or returned for account {account_id}.")
            return

        actual_orders_list = orders_response.Orders
        print(
            f"  Found {len(actual_orders_list)} total orders for account {account_id}. Searching for {order_ids_to_find}..."
        )

        found_count = 0
        for order in actual_orders_list:
            if order.OrderID in order_ids_to_find:
                found_count += 1
                print(f"  Found OrderID: {order.OrderID}")

                # CORRECTED: Access details from the first leg (order.Legs[0])
                symbol = "N/A"
                asset_action = "N/A N/A"
                quantity_info = "Ordered: N/A, Filled: N/A"

                if order.Legs and len(order.Legs) > 0:
                    first_leg = order.Legs[0]
                    symbol = first_leg.Symbol if hasattr(first_leg, "Symbol") else "N/A"
                    asset_type = first_leg.AssetType if hasattr(first_leg, "AssetType") else "N/A"
                    buy_sell = first_leg.BuyOrSell if hasattr(first_leg, "BuyOrSell") else "N/A"
                    asset_action = f"{asset_type} {buy_sell}"
                    qty_ordered = (
                        first_leg.QuantityOrdered
                        if hasattr(first_leg, "QuantityOrdered")
                        else "N/A"
                    )
                    qty_filled = (
                        first_leg.QuantityFilled if hasattr(first_leg, "QuantityFilled") else "N/A"
                    )
                    quantity_info = f"Ordered: {qty_ordered}, Filled: {qty_filled}"
                else:
                    print("    WARNING: Order has no legs or legs list is empty.")

                print(f"    Symbol: {symbol}, Action: {asset_action}")
                print(f"    Quantity: {quantity_info}")
                print(
                    f"    Type: {order.OrderType}, Status: {order.StatusDescription} ({order.Status})"
                )
                if order.LimitPrice:
                    print(f"    Limit Price: {order.LimitPrice}")
                if order.StopPrice:
                    print(f"    Stop Price: {order.StopPrice}")

        if found_count == 0:
            print(
                f"  WARNING: Did not find any of the target OrderIDs ({order_ids_to_find}) in the retrieved orders."
            )
        elif found_count < len(order_ids_to_find):
            print(
                f"  WARNING: Found {found_count} out of {len(order_ids_to_find)} target OrderIDs."
            )

    except aiohttp.ClientResponseError as e:
        print(f"HTTP ERROR querying orders: Status={e.status}, Message='{e.message}'")
    except ValidationError as ve:
        print(f"Pydantic Validation FAILED querying orders:")
        print(ve)
    except Exception as e:
        print(f"Unexpected ERROR querying orders: {type(e).__name__} - {e}")
        traceback.print_exc()


async def cancel_orders(client: TradeStationClient, order_ids: List[str]) -> bool:
    """Attempts to cancel a list of orders by their IDs."""
    print(f"\n--- 6. Attempting to Cancel Orders: {order_ids} ---")
    if not order_ids:
        print("  No Order IDs provided to cancel.")
        return False

    all_cancelled_successfully = True
    print("  Waiting a few seconds before sending cancel requests...")
    await asyncio.sleep(5)  # Brief pause

    for order_id in order_ids:
        print(f"  Cancelling OrderID: {order_id}...")
        try:
            response: CancelOrderResponse = await client.order_execution.cancel_order(
                order_id=order_id
            )

            if response and response.OrderID == order_id:
                if not response.Error:
                    print(f"    Order {order_id}: Cancellation Request Sent Successfully.")
                elif response.Error:
                    # Check for specific 'already cancelled' or 'filled' errors if needed
                    # Example: Error code 'OrderNotFound' often means it was already cancelled/filled
                    if (
                        "filled" in response.Message.lower()
                        or "cancelled" in response.Message.lower()
                        or "rejected" in response.Message.lower()
                    ):
                        print(
                            f"    Order {order_id}: Already cancelled, filled, or rejected ({response.Error} - {response.Message}). Considered success for cleanup."
                        )
                    else:
                        print(
                            f"    Order {order_id}: ERROR cancelling: {response.Error} - {response.Message}"
                        )
                        all_cancelled_successfully = False
                else:
                    print(
                        f"    Order {order_id}: Cancellation status unclear in response: {response}"
                    )
                    all_cancelled_successfully = False  # Unclear state is not success
            else:
                print(
                    f"    Order {order_id}: Cancellation response OrderID mismatch or missing response."
                )
                all_cancelled_successfully = False

        except aiohttp.ClientResponseError as e:
            print(
                f"    Order {order_id}: HTTP ERROR during cancellation: Status={e.status}, Message='{e.message}'"
            )
            try:
                error_body = await e.text()
                print(f"      Response Body: {error_body}")
                # If error indicates it's already gone, treat as success for cleanup
                if (
                    "order not found" in error_body.lower()
                    or "already been processed" in error_body.lower()
                ):
                    print(
                        "      (Error indicates order already inactive, treating as cancellation success)"
                    )
                else:
                    all_cancelled_successfully = False
            except Exception:
                all_cancelled_successfully = False
        except Exception as e:
            print(f"    Order {order_id}: Unexpected ERROR cancelling: {type(e).__name__} - {e}")
            traceback.print_exc()
            all_cancelled_successfully = False

    if all_cancelled_successfully:
        print(
            "\nCancellation process completed. All orders were either cancelled or already inactive."
        )
    else:
        print(
            "\nWARNING: One or more orders may not have been successfully cancelled. Manual check required."
        )

    return all_cancelled_successfully


async def main():
    """Main function to demonstrate placing, querying, and cancelling a group order."""
    load_dotenv()
    ts_client = TradeStationClient()
    placed_order_ids: List[str] = []
    margin_account_id: Optional[str] = None

    try:
        # --- 1. Find Margin Account ---
        margin_account_id = await find_margin_account(ts_client)
        if not margin_account_id:
            return

        # --- 2. Get Quote for MSFT ---
        symbol_to_trade = "MSFT"
        last_price = await get_last_price(ts_client, symbol_to_trade)
        if not last_price:
            print(f"Could not get last price for {symbol_to_trade}. Aborting.")
            return

        # --- 3. Calculate Order Prices ---
        prices = calculate_prices(last_price)

        # --- 4. Place OCO Group Order ---
        order_quantity = "1"  # Use small quantity for example
        placed_order_ids = await place_oco_group_order(
            ts_client, margin_account_id, symbol_to_trade, order_quantity, prices
        )

        if not placed_order_ids:
            print("\nGroup order placement failed or returned no IDs. Aborting further steps.")
            return  # Don't proceed if placement failed

        # --- 5. Query Orders After Placement ---
        await query_and_display_orders(
            ts_client, margin_account_id, placed_order_ids, "5. Querying Orders After Placement"
        )

        # --- 6. Cancel the Orders ---
        await cancel_orders(ts_client, placed_order_ids)

        # Add a pause before final query to allow status update
        print("\nWaiting a few seconds for order status to update...")
        await asyncio.sleep(7)

        # --- 7. Query Orders After Cancellation Attempt ---
        await query_and_display_orders(
            ts_client,
            margin_account_id,
            placed_order_ids,
            "7. Querying Orders After Cancellation Attempt",
        )

        print("\nExample finished.")

    except Exception as e:
        print(f"\nAn unexpected error occurred in main: {type(e).__name__} - {e}")
        traceback.print_exc()
    finally:
        await ts_client.close()
        print("\nClient session closed.")


if __name__ == "__main__":
    # Make sure the event loop is managed correctly
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "Cannot run the event loop while another loop is running" in str(e):
            print("Detected running event loop. Attempting to attach.")
            # This might happen in environments like Jupyter notebooks
            loop = asyncio.get_event_loop()
            loop.create_task(main())
            # Note: In a script context, asyncio.run() is usually sufficient.
            # This fallback might not be necessary or fully correct depending on context.
        else:
            raise e  # Re-raise other runtime errors
