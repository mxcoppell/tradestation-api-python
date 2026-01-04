#!/usr/bin/env python
"""
Example demonstrating how to get confirmation details (quote) for a potential single order
using the TradeStation API.

This example shows how to:
1. Initialize the TradeStation client.
2. Fetch available brokerage accounts (specifically looking for a margin account).
3. Construct a sample Order request (e.g., a limit buy).
4. Call the `confirm_order` endpoint using the client.
5. Process and display the confirmation result.

Note: This endpoint provides confirmation details (quote) for a *potential* order.
It does not place the order.

Usage:
    python confirm_order.py

Requirements:
    - A valid TradeStation account with brokerage services and a margin account.
    - API credentials (CLIENT_ID, REFRESH_TOKEN) and ENVIRONMENT in a .env file.
    - Correct account permissions and market conditions for the specified order.
"""

import asyncio
import os
from typing import List

import aiohttp
from dotenv import load_dotenv
from pydantic import ValidationError

# Import the client
from tradestation.client import TradeStationClient
from tradestation.ts_types.brokerage import Account

# Import necessary types from the order execution definitions
from tradestation.ts_types.order_execution import (
    GroupOrderResponseError,  # Use group error model if errors come in that structure
)
from tradestation.ts_types.order_execution import (
    OrderResponseError,  # Keep regular error model just in case
)
from tradestation.ts_types.order_execution import (  # Use the group confirmation models as the structure seems similar
    GroupOrderConfirmationDetail,
    GroupOrderConfirmationResponse,
    OrderDuration,
    OrderRequest,
    OrderSide,
    OrderType,
    TimeInForce,
)


async def main():
    """Main function to demonstrate confirming a single order."""
    load_dotenv()
    ts_client = TradeStationClient()
    margin_account_id = None

    try:
        # --- 1. Fetch Accounts and Find Margin Account ---
        print("\nFetching accounts...")
        accounts: List[Account] = await ts_client.brokerage.get_accounts()
        if not accounts:
            print("ERROR: No brokerage accounts found.")
            return
        for account in accounts:
            if account.AccountID.endswith("M"):
                margin_account_id = account.AccountID
                break
        if not margin_account_id:
            print("ERROR: No margin account (AccountID ending with 'M') found.")
            return
        print(f"Using Margin Account ID: {margin_account_id}")

        # --- 2. Construct Sample Order Request ---
        print("\nConstructing sample limit buy order request for MSFT...")
        # Use the Pydantic model directly for the request object
        order_request = OrderRequest(
            AccountID=margin_account_id,
            Symbol="MSFT",
            Quantity="1",
            OrderType=OrderType.LIMIT,
            LimitPrice="380.00",
            TradeAction=OrderSide.BUY,
            TimeInForce=TimeInForce(Duration=OrderDuration.DAY),
            Route="Intelligent",
        )

        # --- 3. Confirm the Order using the client method ---
        print("\nConfirming Order via client (getting quote details)...")
        # Expecting a response structure similar to GroupOrderConfirmationResponse
        order_confirmation = await ts_client.order_execution.confirm_order(request=order_request)

        # --- 4. Process and Display Confirmation Result ---
        print("\nOrder Confirmation Details:")

        # Check if the response is the expected GroupOrderConfirmationResponse structure
        if isinstance(order_confirmation, GroupOrderConfirmationResponse):
            if order_confirmation.Confirmations:
                print("  Confirmed Order Details:")
                # Expecting only one detail for a single order confirmation
                if len(order_confirmation.Confirmations) == 1:
                    detail = order_confirmation.Confirmations[0]
                    if isinstance(detail, GroupOrderConfirmationDetail):
                        print(f"    - ConfirmID: {getattr(detail, 'OrderConfirmID', 'N/A')}")
                        print(f"      Summary: {getattr(detail, 'SummaryMessage', 'N/A')}")
                        print(
                            f"      Est. Price: {getattr(detail, 'EstimatedPrice', 'N/A')}"
                            f", Est. Cost: {getattr(detail, 'EstimatedCost', 'N/A')}"
                            f", Est. Commission: {getattr(detail, 'EstimatedCommission', 'N/A')}"
                        )
                    else:
                        print(f"    - Unexpected item type in Confirmations list: {detail}")
                else:
                    print(
                        f"  WARNING: Expected 1 confirmation detail, but found {len(order_confirmation.Confirmations)}"
                    )
                    # Optionally print all details if needed
                    # for i, detail in enumerate(order_confirmation.Confirmations):
                    #     print(f"    Detail {i+1}: {detail.model_dump_json()}")

            if order_confirmation.Errors:
                print("  Errors found in confirmation response:")
                for error in order_confirmation.Errors:
                    # Assuming errors follow GroupOrderResponseError structure
                    if isinstance(error, GroupOrderResponseError):
                        print(
                            f"    - OrderID: {error.OrderID}, Error: {error.Error}, Message: {error.Message}"
                        )
                    else:
                        print(f"    - Unexpected error format within Errors list: {error}")

        # Fallback for completely unexpected structures or direct error responses
        else:
            print("  Unexpected response type or structure.")
            # Attempt to handle potential direct OrderResponseError structure if applicable
            if hasattr(order_confirmation, "model_dump_json"):
                print(f"    Raw Response: {order_confirmation.model_dump_json(indent=2)}")
            else:
                print(f"    Raw Response: {order_confirmation}")

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
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        await ts_client.close()
        print("\nClient session closed.")


if __name__ == "__main__":
    asyncio.run(main())
