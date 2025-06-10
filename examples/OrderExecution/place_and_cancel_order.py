#!/usr/bin/env python
"""
Example demonstrating placing a limit order and then cancelling it using the TradeStation API.

This example shows how to:
1. Initialize the TradeStation client.
2. Fetch available brokerage accounts (specifically looking for a margin account).
3. Get a quote for a symbol (COST).
4. Calculate a limit price based on the quote (e.g., 20% below last).
5. Place a limit buy order.
6. Immediately attempt to cancel the placed order using the OrderID from the placement response.

NOTE: This example does not query the order status after cancellation because the
      `get_orders` functionality is not yet implemented in the OrderExecutionService.

Usage:
    python place_and_cancel_order.py

Requirements:
    - A valid TradeStation account with brokerage services and a margin account.
    - API credentials (CLIENT_ID, REFRESH_TOKEN) and ENVIRONMENT in a .env file.
    - Correct account permissions and market conditions for the specified order.
    - Sufficient buying power for the order.
    - Note: This script places and cancels a real order in the specified environment (SIM/LIVE).
"""

import asyncio
from decimal import Decimal, ROUND_DOWN
from dotenv import load_dotenv
from typing import List, Optional
import aiohttp
from pydantic import ValidationError

# Import the client
from tradestation.client import TradeStationClient

# Import necessary types
from tradestation.ts_types.brokerage import Account
from tradestation.ts_types.market_data import Quote, QuoteSnapshot
from tradestation.ts_types.order_execution import (
    OrderRequest,
    TimeInForce,
    OrderType,
    OrderSide,
    OrderDuration,
    OrderResponse,
    OrderResponseSuccess,
    OrderResponseError,
    CancelOrderResponse,
)


async def find_margin_account(client: TradeStationClient) -> Optional[str]:
    """Fetches accounts and returns the ID of the first margin account found."""
    print("\nFetching accounts...")
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
    print(f"\nFetching quote for {symbol}...")
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


def calculate_limit_price(last_price: Decimal, percentage_below: Decimal) -> str:
    """Calculates a limit price X% below the last price, rounded to 2 decimal places."""
    discount_factor = Decimal(1) - (percentage_below / Decimal(100))
    limit_price = (last_price * discount_factor).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
    print(f"  Calculated Limit Price ({percentage_below}% below {last_price}): {limit_price}")
    return str(limit_price)


async def place_limit_buy_order(
    client: TradeStationClient, account_id: str, symbol: str, quantity: str, limit_price: str
) -> Optional[str]:
    """Places a limit buy order and returns the OrderID if successful."""
    print(f"\nPlacing Limit Buy Order for {quantity} {symbol} @ {limit_price}...")
    order_request = OrderRequest(
        AccountID=account_id,
        Symbol=symbol,
        Quantity=quantity,
        OrderType=OrderType.LIMIT,
        LimitPrice=limit_price,
        TradeAction=OrderSide.BUY,
        TimeInForce=TimeInForce(Duration=OrderDuration.GTC),
        Route="Intelligent",
    )
    try:
        order_response: OrderResponse = await client.order_execution.place_order(
            request=order_request
        )

        # Pretty print the full response
        print(f"  Full Place Order Response:\n{order_response.model_dump_json(indent=2)}")

        if order_response.Errors:
            for error in order_response.Errors:
                print(
                    f"  ERROR placing order: {error.Error} - {error.Message} (OrderID: {error.OrderID})"
                )

        if order_response.Orders:
            for success_order in order_response.Orders:
                print(f"  Order Placed Successfully! OrderID: {success_order.OrderID}")
                return success_order.OrderID
            print("  OrderResponse contained an empty Orders list.")
            return None
        elif not order_response.Errors:
            print(f"  Unexpected response from place_order: {order_response}")
            return None
        else:
            return None

    except Exception as e:
        print(f"ERROR placing order: {e}")
        return None


# Removed find_order_in_account function as get_orders is not implemented


async def cancel_order_by_id(client: TradeStationClient, order_id: str) -> bool:
    """Cancels an order by its ID."""
    print(f"\nAttempting to cancel OrderID: {order_id}...")
    try:
        # Add a slightly longer pause before cancelling
        print("  Waiting a few seconds before sending cancel request...")
        await asyncio.sleep(7)  # Increased wait time

        # Corrected: cancel_order returns a single CancelOrderResponse object, not a list
        response: CancelOrderResponse = await client.order_execution.cancel_order(order_id=order_id)

        # Process the single response object directly
        if response:
            # response = cancel_responses[0]  # No longer needed
            if response.OrderID == order_id:
                if not response.Error:
                    print(f"  Order {order_id} Cancellation Request Sent Successfully.")
                    # Note: This confirms the request was sent, not necessarily that the order is fully cancelled yet.
                    return True
                elif response.Error:
                    # Check for specific 'already cancelled' or 'filled' errors if needed
                    print(
                        f"  ERROR cancelling order {order_id}: {response.Error} - {response.Message}"
                    )
                    return False
                else:
                    print(f"  Order {order_id} cancellation status unclear in response: {response}")
                    return False
            else:
                print(
                    f"  Cancellation response OrderID ({response.OrderID}) doesn't match requested ({order_id})."
                )
                return False
        else:
            # This case might not be reachable if an exception is always raised on failure
            print(f"  No valid response received from cancel_order for OrderID {order_id}.")
            return False
    except aiohttp.ClientResponseError as e:
        # Catch HTTP errors specifically for cancellation
        print(
            f"HTTP ERROR during cancellation for {order_id}: Status={e.status}, Message='{e.message}'"
        )
        try:
            error_body = await e.text()
            print(f"  Response Body: {error_body}")
        except Exception as body_e:
            print(f"  (Could not read cancellation error response body: {body_e})")
        return False
    except Exception as e:
        print(f"ERROR cancelling order {order_id}: {type(e).__name__} - {e}")
        return False


async def main():
    """Main function to demonstrate placing and cancelling an order."""
    load_dotenv()
    ts_client = TradeStationClient()
    placed_order_id: Optional[str] = None
    margin_account_id: Optional[str] = None

    try:
        # --- 1. Find Margin Account ---
        margin_account_id = await find_margin_account(ts_client)
        if not margin_account_id:
            return

        # --- 2. Get Quote for COST ---
        symbol_to_trade = "COST"
        last_price = await get_last_price(ts_client, symbol_to_trade)
        if not last_price:
            print(f"Could not get last price for {symbol_to_trade}. Aborting.")
            return

        # --- 3. Calculate Limit Price ---
        # Use 5% below last price
        limit_price_str = calculate_limit_price(last_price, Decimal(5))

        # --- 4. Place Limit Buy Order ---
        order_quantity = "1"
        placed_order_id = await place_limit_buy_order(
            ts_client, margin_account_id, symbol_to_trade, order_quantity, limit_price_str
        )
        if not placed_order_id:
            print("Failed to place order. Aborting.")
            return

        # --- 5. Cancel the Order ---
        # (Removed query step)
        cancelled = await cancel_order_by_id(ts_client, placed_order_id)
        if cancelled:
            print(f"\nCancellation request for OrderID {placed_order_id} was sent.")
            print("NOTE: Order status cannot be verified as get_orders is not implemented.")
        else:
            print(f"\nFailed to send cancellation request for order {placed_order_id}.")
            print("Manual check required in TradeStation platform.")

        # --- Removed final query step ---

    except aiohttp.ClientResponseError as e:
        print(f"\nHTTP ERROR occurred: Status={e.status}, Message='{e.message}'")
        print(f"  Request URL: {e.request_info.url}")
        try:
            error_body = await e.text()
            print(f"  Response Body: {error_body}")
        except Exception as body_e:
            print(f"  (Could not read error response body: {body_e})")
    except ValidationError as ve:
        print(f"\nPydantic Validation FAILED:")
        print(ve)
    except AttributeError as e:
        print(f"ERROR: Could not find necessary method or attribute: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {type(e).__name__} - {e}")
        import traceback

        traceback.print_exc()
    finally:
        # Simplified finally block: only close client
        # No final cancellation attempt needed as it's done in the main flow now
        await ts_client.close()
        print("\nClient session closed.")


if __name__ == "__main__":
    asyncio.run(main())
