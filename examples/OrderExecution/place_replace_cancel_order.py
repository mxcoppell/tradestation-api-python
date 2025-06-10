#!/usr/bin/env python
"""
Example demonstrating placing a single limit order, querying it, replacing it
with a new price, querying again, cancelling it, and querying a final time
using the TradeStation API.

This example shows how to:
1. Initialize the TradeStation client.
2. Fetch available brokerage accounts (specifically looking for a margin account).
3. Get a quote for a symbol (COST).
4. Calculate an initial limit price (5% below last).
5. Place a single Limit Buy order (GTC).
6. Extract the OrderID from the placement response.
7. Query orders for the account to find the newly placed order.
8. Calculate a new limit price (6% below last).
9. Replace the original order with the new limit price.
10. Query orders again to see the status of the replaced order (potentially new OrderID).
11. Cancel the active order using its latest OrderID.
12. Query orders a final time to verify the cancellation status.

NOTE: This script places, replaces, and cancels real orders in the specified environment (SIM/LIVE).
      Ensure you have sufficient buying power and understand the implications.

Usage:
    python examples/OrderExecution/place_replace_cancel_order.py

Requirements:
    - A valid TradeStation account with brokerage services and a margin account.
    - API credentials (CLIENT_ID, REFRESH_TOKEN) and ENVIRONMENT in a .env file.
    - Correct account permissions and market conditions for the specified order.
    - Sufficient buying power for the order.
"""

import asyncio
from decimal import Decimal, ROUND_DOWN
from dotenv import load_dotenv
from typing import List, Optional, Dict
import aiohttp
from pydantic import ValidationError
import traceback

# Import the client
from tradestation.client import TradeStationClient

# Import necessary types
from tradestation.ts_types.brokerage import Account, Order, Orders
from tradestation.ts_types.market_data import Quote, QuoteSnapshot
from tradestation.ts_types.order_execution import (
    OrderRequest,
    OrderReplaceRequest,
    TimeInForce,
    OrderType,
    OrderSide,
    OrderDuration,
    OrderResponse,
    CancelOrderResponse,
    OrderReplaceTimeInForce,
    ReplaceOrderResponse,
)


async def find_margin_account(client: TradeStationClient) -> Optional[str]:
    """Fetches accounts and returns the ID of the first margin account found."""
    print("--- 1. Fetching Accounts ---")
    try:
        accounts: List[Account] = await client.brokerage.get_accounts()
        if not accounts:
            print("ERROR: No brokerage accounts found.")
            return None
        for account in accounts:
            # Margin accounts typically end with 'M' or contain 'MARGIN'
            # Adjust if your account ID format differs
            if account.AccountType == "Margin" or account.AccountID.endswith("M"):
                print(f"Found Margin Account ID: {account.AccountID}")
                return account.AccountID
        print("ERROR: No margin account found.")
        return None
    except aiohttp.ClientResponseError as e:
        print(f"HTTP ERROR fetching accounts: Status={e.status}, Message='{e.message}'")
        return None
    except Exception as e:
        print(f"ERROR fetching accounts: {e}")
        traceback.print_exc()
        return None


async def get_last_price(client: TradeStationClient, symbol: str) -> Optional[Decimal]:
    """Gets the last price for a symbol from quote snapshots."""
    print(f"--- 2. Fetching Quote for {symbol} ---")
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
    except aiohttp.ClientResponseError as e:
        print(f"HTTP ERROR fetching quote for {symbol}: Status={e.status}, Message='{e.message}'")
        return None
    except Exception as e:
        print(f"ERROR fetching quote for {symbol}: {e}")
        traceback.print_exc()
        return None


def calculate_prices(last_price: Decimal) -> Dict[str, str]:
    """Calculates limit prices based on percentages below the last price."""
    print("--- 3. Calculating Order Prices ---")
    limit_price_5_pct = (last_price * Decimal("0.95")).quantize(
        Decimal("0.01"), rounding=ROUND_DOWN
    )
    limit_price_6_pct = (last_price * Decimal("0.94")).quantize(
        Decimal("0.01"), rounding=ROUND_DOWN
    )

    print(f"  Initial Limit Price (5% below {last_price}): {limit_price_5_pct}")
    print(f"  Replacement Limit Price (6% below {last_price}): {limit_price_6_pct}")

    return {
        "limit_5": str(limit_price_5_pct),
        "limit_6": str(limit_price_6_pct),
    }


async def place_limit_buy_order(
    client: TradeStationClient, account_id: str, symbol: str, quantity: str, limit_price: str
) -> Optional[str]:
    """Places a single limit buy order and returns the OrderID if successful."""
    print(f"--- 4. Placing Limit Buy Order for {quantity} {symbol} at {limit_price} ---")
    order_request = OrderRequest(
        AccountID=account_id,
        Symbol=symbol,
        Quantity=quantity,
        OrderType=OrderType.LIMIT,
        LimitPrice=limit_price,
        TradeAction=OrderSide.BUY,
        TimeInForce=TimeInForce(Duration=OrderDuration.GTC),  # Good Till Cancelled
        Route="Intelligent",
    )

    try:
        response: OrderResponse = await client.order_execution.place_order(request=order_request)
        print("  Full Place Order Response:")
        print(response.model_dump_json(indent=2))

        if response.Errors:
            for error in response.Errors:
                print(f"  ERROR placing order: {error.Message} (OrderID: {error.OrderID})")
            print("  Order placement failed.")
            return None

        if response.Orders and len(response.Orders) > 0:
            # Assuming the first order in the list is the one we placed
            placed_order = response.Orders[0]
            if placed_order.OrderID:
                print(f"  Order Placed Successfully! OrderID: {placed_order.OrderID}")
                return placed_order.OrderID
            else:
                print("  ERROR: Order confirmation received, but no OrderID found.")
                return None
        else:
            print("  ERROR: Order confirmation received, but no Orders list found.")
            return None

    except aiohttp.ClientResponseError as e:
        print(f"HTTP ERROR placing order: Status={e.status}, Message='{e.message}'")
        try:
            error_body = await e.text()
            print(f"  Response Body: {error_body}")
        except Exception as body_e:
            print(f"  (Could not read error response body: {body_e})")
        return None
    except ValidationError as ve:
        print(f"Pydantic Validation FAILED during order placement:")
        print(ve)
        return None
    except Exception as e:
        print(f"Unexpected ERROR placing order: {type(e).__name__} - {e}")
        traceback.print_exc()
        return None


async def query_and_find_order(
    client: TradeStationClient,
    account_id: str,
    target_order_id: str,
    query_description: str,
) -> Optional[Order]:
    """Queries orders for the account and returns the specific order if found."""
    print(f"--- {query_description} (Looking for {target_order_id}) ---")
    if not target_order_id:
        print("  No Order ID provided to query.")
        return None

    try:
        orders_response: Orders = await client.brokerage.get_orders(
            account_ids=account_id, page_size=50  # Adjust page size if needed
        )

        if orders_response.Errors:
            print("  Errors reported while querying orders:")
            for error in orders_response.Errors:
                print(f"    - Account {error.AccountID}: {error.Error} - {error.Message}")
            # Continue searching even if there are errors for other accounts

        if not orders_response.Orders:
            print(f"  No orders found or returned for account {account_id}.")
            return None

        actual_orders_list = orders_response.Orders
        print(
            f"  Found {len(actual_orders_list)} total orders for account {account_id}. Searching for {target_order_id}..."
        )

        for order in actual_orders_list:
            if order.OrderID == target_order_id:
                print(f"  FOUND OrderID: {order.OrderID}")
                # Display key details
                symbol = order.Legs[0].Symbol if order.Legs else "N/A"
                action = (
                    f"{order.Legs[0].AssetType} {order.Legs[0].BuyOrSell}" if order.Legs else "N/A"
                )
                qty_ord = order.Legs[0].QuantityOrdered if order.Legs else "N/A"
                qty_fill = order.Legs[0].QuantityOrdered if order.Legs else "N/A"
                print(
                    f"    Symbol: {symbol}, Action: {action}, Qty: {qty_ord} (Filled: {qty_fill})"
                )
                print(
                    f"    Type: {order.OrderType}, Status: {order.StatusDescription} ({order.Status})"
                )
                if order.LimitPrice:
                    print(f"    Limit Price: {order.LimitPrice}")
                if order.StopPrice:
                    print(f"    Stop Price: {order.StopPrice}")
                return order  # Return the found order object

        print(f"  WARNING: Did not find target OrderID {target_order_id} in the retrieved orders.")
        return None

    except aiohttp.ClientResponseError as e:
        print(f"HTTP ERROR querying orders: Status={e.status}, Message='{e.message}'")
        return None
    except ValidationError as ve:
        print(f"Pydantic Validation FAILED querying orders:")
        print(ve)
        return None
    except Exception as e:
        print(f"Unexpected ERROR querying orders: {type(e).__name__} - {e}")
        traceback.print_exc()
        return None


async def replace_order(
    client: TradeStationClient,
    original_order_id: str,
    account_id: str,
    symbol: str,
    quantity: str,
    new_limit_price: str,
) -> Optional[str]:
    """Replaces an existing order with a new limit price."""
    print(f"--- 6. Replacing Order {original_order_id} with new Limit Price {new_limit_price} ---")

    # Construct the request body ONLY with fields defined in OrderReplaceRequest model
    # and necessary for the change. Based on user test and model, only Quantity, OrderType,
    # and the new LimitPrice seem necessary for a price change.
    replace_request = OrderReplaceRequest(
        AccountID=account_id,  # Added back based on user test
        OrderID=original_order_id,  # Added back based on user test
        Quantity=quantity,  # Keep: Seems required for context
        OrderType=OrderType.LIMIT,  # Keep: Seems required for context
        LimitPrice=new_limit_price,  # Keep: The value being changed
    )

    try:
        # Expect the new, flatter response type
        response: ReplaceOrderResponse = await client.order_execution.replace_order(
            original_order_id,  # Pass as positional argument
            request=replace_request,  # Body of the request
        )
        print("  Full Replace Order Response:")
        print(response.model_dump_json(indent=2))

        # Updated logic: Check direct attributes of ReplaceOrderResponse
        if response.OrderID:
            print(
                f"  Order Replacement Request Successful! Message: '{response.Message}', OrderID: {response.OrderID}"
            )
            # If replace is successful, API usually keeps the same OrderID, but confirm from response
            return response.OrderID
        else:
            # Assuming if OrderID is missing, it failed. Check for an Error attribute if added to model.
            print(
                f"  ERROR: Order replacement failed or did not return OrderID. Response: {response.model_dump_json()}"
            )
            # Consider adding more specific error checks if the API/model provides details
            return None

    except aiohttp.ClientResponseError as e:
        print(
            f"HTTP ERROR replacing order {original_order_id}: Status={e.status}, Message='{e.message}'"
        )
        try:
            error_body = await e.text()
            print(f"  Response Body: {error_body}")
            # Check if error indicates it was already filled/cancelled
            if "order not found" in error_body.lower() or "invalid state" in error_body.lower():
                print("  (Error indicates original order already inactive, cannot replace)")
        except Exception as body_e:
            print(f"  (Could not read error response body: {body_e})")
        return None
    except ValidationError as ve:
        print(f"Pydantic Validation FAILED during order replacement:")
        print(ve)
        return None
    except Exception as e:
        print(f"Unexpected ERROR replacing order {original_order_id}: {type(e).__name__} - {e}")
        traceback.print_exc()
        return None


async def cancel_single_order(client: TradeStationClient, order_id: str) -> bool:
    """Attempts to cancel a single order by its ID."""
    print(f"--- 8. Attempting to Cancel Order: {order_id} ---")
    if not order_id:
        print("  No Order ID provided to cancel.")
        return False

    print("  Waiting a few seconds before sending cancel request...")
    await asyncio.sleep(3)  # Brief pause

    try:
        response: CancelOrderResponse = await client.order_execution.cancel_order(order_id=order_id)
        print("  Full Cancel Order Response:")
        print(response.model_dump_json(indent=2))

        if response and response.OrderID == order_id:
            if not response.Error:
                print(f"    Order {order_id}: Cancellation Request Sent Successfully.")
                return True
            elif response.Error:
                # Check for specific 'already cancelled' or 'filled' errors
                if (
                    "filled" in response.Message.lower()
                    or "cancelled" in response.Message.lower()
                    or "rejected" in response.Message.lower()
                    or "not found" in response.Error.lower()  # Often indicates already inactive
                ):
                    print(
                        f"    Order {order_id}: Already cancelled, filled, or rejected ({response.Error} - {response.Message}). Considered success for cleanup."
                    )
                    return True  # Treat as success if already inactive
                else:
                    print(
                        f"    Order {order_id}: ERROR cancelling: {response.Error} - {response.Message}"
                    )
                    return False
            else:
                # Should not happen if response.OrderID matched and response.Error exists
                print(f"    Order {order_id}: Cancellation status unclear in response: {response}")
                return False
        elif response and response.Errors:  # Handle list of errors
            for error in response.Errors:
                print(
                    f"    Order {order_id}: ERROR cancelling: {error.Message} (Error Code: {error.Error})"
                )
                # Check if the error indicates it's already inactive
                if (
                    "filled" in error.Message.lower()
                    or "cancelled" in error.Message.lower()
                    or "rejected" in error.Message.lower()
                    or "not found" in error.Error.lower()
                ):
                    print(
                        "      (Error indicates order already inactive, treating as cancellation success)"
                    )
                    return True  # Treat as success
            return False  # If any error wasn't an "already inactive" type
        else:
            print(
                f"    Order {order_id}: Cancellation response OrderID mismatch ({response.OrderID if response else 'N/A'}) or missing/malformed response."
            )
            return False

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
                or e.status == 404  # Not Found likely means it's gone
            ):
                print(
                    "      (Error indicates order already inactive, treating as cancellation success)"
                )
                return True
            else:
                return False
        except Exception:
            return False
    except ValidationError as ve:
        print(f"    Order {order_id}: Pydantic Validation FAILED during cancellation:")
        print(ve)
        return False
    except Exception as e:
        print(f"    Order {order_id}: Unexpected ERROR cancelling: {type(e).__name__} - {e}")
        traceback.print_exc()
        return False


async def main():
    """Main function to demonstrate placing, replacing, and cancelling an order."""
    load_dotenv()
    ts_client = TradeStationClient()
    initial_order_id: Optional[str] = None
    current_order_id: Optional[str] = None  # Track the potentially new ID after replace
    margin_account_id: Optional[str] = None
    symbol_to_trade = "COST"
    order_quantity = "1"  # Use small quantity for example

    try:
        # --- 1. Find Margin Account ---
        margin_account_id = await find_margin_account(ts_client)
        if not margin_account_id:
            return

        # --- 2. Get Quote ---
        last_price = await get_last_price(ts_client, symbol_to_trade)
        if not last_price:
            print(f"Could not get last price for {symbol_to_trade}. Aborting.")
            return

        # --- 3. Calculate Order Prices ---
        prices = calculate_prices(last_price)
        initial_limit_price = prices["limit_5"]
        replacement_limit_price = prices["limit_6"]

        # --- 4. Place Initial Limit Buy Order ---
        initial_order_id = await place_limit_buy_order(
            ts_client, margin_account_id, symbol_to_trade, order_quantity, initial_limit_price
        )
        current_order_id = initial_order_id  # Initially, the current ID is the initial ID

        if not current_order_id:
            print("Initial order placement failed or returned no ID. Aborting further steps.")
            return  # Don't proceed if placement failed

        print("Waiting a few seconds for order to register...")
        await asyncio.sleep(5)

        # --- 5. Query Order After Placement ---
        placed_order = await query_and_find_order(
            ts_client, margin_account_id, current_order_id, "5. Querying Order After Placement"
        )
        if not placed_order:
            print(f"Could not find placed order {current_order_id}. Aborting replace/cancel.")
            return
        # Check if order is already filled or in a non-replaceable state
        if placed_order.Status not in ["OPN", "ACK", "DON", "CND"]:
            print(
                f"Order {current_order_id} is in status '{placed_order.StatusDescription}' and cannot be replaced or cancelled. Aborting."
            )
            return

        # --- 6. Replace the Order ---
        new_order_id_after_replace = await replace_order(
            client=ts_client,
            original_order_id=current_order_id,  # ID to replace
            account_id=margin_account_id,
            symbol=symbol_to_trade,
            quantity=order_quantity,
            new_limit_price=replacement_limit_price,
        )

        if new_order_id_after_replace:
            # new_order_id_after_replace now directly contains the OrderID from ReplaceOrderResponse
            print(
                f"Order replacement seems successful. The active OrderID is {new_order_id_after_replace}"
            )
            current_order_id = new_order_id_after_replace  # Update the ID to track
        elif new_order_id_after_replace is None:
            # Replace failed, but maybe because original was filled/cancelled. Query again.
            print(
                "Order replacement failed or didn't return a new ID. Querying status of original ID."
            )
            # Keep current_order_id as initial_order_id and proceed to query/cancel check
            pass  # Fall through to query #7

        print("Waiting a few seconds for replacement status to update...")
        await asyncio.sleep(7)

        # --- 7. Query Order After Replacement Attempt ---
        # Query using the *current* active order ID (might be original or new one)
        replaced_order_check = await query_and_find_order(
            ts_client,
            margin_account_id,
            current_order_id,
            "7. Querying Order After Replacement Attempt",
        )
        if not replaced_order_check:
            # If the *current* ID isn't found, maybe the original was filled/cancelled before replace could happen
            # Or maybe the replace *did* work but the query failed / ID changed unexpectedly?
            # Let's try querying the initial ID if it's different
            if current_order_id != initial_order_id:
                print(
                    f"Could not find current OrderID {current_order_id}. Checking initial OrderID {initial_order_id}..."
                )
                initial_order_check = await query_and_find_order(
                    ts_client,
                    margin_account_id,
                    initial_order_id,
                    "7b. Querying Initial Order After Replacement Attempt",
                )
                if initial_order_check and initial_order_check.Status not in [
                    "OPN",
                    "RECEIVED",
                    "CONDITIONAL",
                ]:
                    print(
                        f"Initial order {initial_order_id} found with status '{initial_order_check.StatusDescription}'. Cannot cancel."
                    )
                    current_order_id = None  # Mark as nothing to cancel
                elif initial_order_check:
                    print(
                        f"Found initial order {initial_order_id} still active? Unexpected. Attempting to cancel it."
                    )
                    current_order_id = (
                        initial_order_id  # Reset current ID to initial for cancellation attempt
                    )
                else:
                    print(
                        f"Neither current ({current_order_id}) nor initial ({initial_order_id}) order found after replace attempt. Cannot cancel."
                    )
                    current_order_id = None  # Mark as nothing to cancel
            else:
                # Current ID is same as initial, and it wasn't found
                print(
                    f"Could not find order {current_order_id} after replace attempt. Cannot cancel."
                )
                current_order_id = None  # Mark as nothing to cancel

        elif replaced_order_check.Status not in ["OPN", "ACK", "DON", "CND"]:
            # Found the current order, but it's already inactive
            print(
                f"Order {current_order_id} found with status '{replaced_order_check.StatusDescription}'. Cannot cancel."
            )
            current_order_id = None  # Mark as nothing to cancel

        # If current_order_id is still valid, proceed to cancel
        if current_order_id:
            # --- 8. Cancel the Active Order ---
            await cancel_single_order(ts_client, current_order_id)

            print("Waiting a few seconds for cancellation status to update...")
            await asyncio.sleep(7)

            # --- 9. Query Order After Cancellation Attempt ---
            await query_and_find_order(
                ts_client,
                margin_account_id,
                current_order_id,  # Query the ID we attempted to cancel
                "9. Querying Order After Cancellation Attempt",
            )
        else:
            print("--- 8 & 9 Skipped: No active order ID found to cancel/query ---")

        print("Example finished.")

    except Exception as e:
        print(f"An unexpected error occurred in main: {type(e).__name__} - {e}")
        traceback.print_exc()
    finally:
        await ts_client.close()
        print("Client session closed.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "Cannot run the event loop while another loop is running" in str(e):
            print("Detected running event loop. Attempting to attach.")
            loop = asyncio.get_event_loop()
            loop.create_task(main())
        else:
            raise e
