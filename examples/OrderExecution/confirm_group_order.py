#!/usr/bin/env python
"""
Example demonstrating how to get confirmation details (quotes) for a potential group order
using the TradeStation API.

This example shows how to:
1. Initialize the TradeStation client.
2. Fetch available brokerage accounts (specifically looking for a margin account).
3. Construct a sample Group Order request (e.g., OCO).
4. Call the `confirm_group_order` endpoint using the client.
5. Process and display the confirmation results using the corrected Pydantic models.

Note: This endpoint provides confirmation details (quotes) for a *potential* order group.
It does not place the order.

Usage:
    python confirm_group_order.py

Requirements:
    - A valid TradeStation account with brokerage services and a margin account.
    - API credentials (CLIENT_ID, REFRESH_TOKEN) and ENVIRONMENT in a .env file.
    - Correct account permissions and market conditions for the specified order.
"""

import asyncio
import os
from dotenv import load_dotenv
from typing import List
import aiohttp
from pydantic import ValidationError

# Import the client
from src.client.tradestation_client import TradeStationClient

# Import necessary types from the order execution definitions
from src.ts_types.order_execution import (
    GroupOrderRequest,
    OrderRequest,
    TimeInForce,
    OrderType,
    OrderSide,
    OrderDuration,
    GroupOrderConfirmationResponse,
    GroupOrderConfirmationDetail,  # Import the new detail model
)
from src.ts_types.brokerage import Account


async def main():
    """Main function to demonstrate confirming a group order."""
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

        # --- 2. Construct Sample OCO Group Order Request ---
        print("\nConstructing sample OCO order request for MSFT...")
        # Use the Pydantic model directly for the request object
        oco_group_request = GroupOrderRequest(
            Type="OCO",
            Orders=[
                OrderRequest(
                    AccountID=margin_account_id,
                    Symbol="MSFT",
                    Quantity="1",
                    OrderType=OrderType.LIMIT,
                    LimitPrice="380.00",
                    TradeAction=OrderSide.BUY,
                    TimeInForce=TimeInForce(Duration=OrderDuration.DAY),
                    Route="Intelligent",
                ),
                OrderRequest(
                    AccountID=margin_account_id,
                    Symbol="MSFT",
                    Quantity="1",
                    OrderType=OrderType.STOP_LIMIT,
                    StopPrice="375.00",
                    LimitPrice="374.50",
                    TradeAction=OrderSide.BUY,
                    TimeInForce=TimeInForce(Duration=OrderDuration.DAY),
                    Route="Intelligent",
                ),
            ],
        )

        # --- 3. Confirm the OCO Group Order using the client method ---
        print("\nConfirming OCO Order Group via client (getting quote details)...")
        # Use the standard client call now that models are corrected
        oco_confirmation: GroupOrderConfirmationResponse = (
            await ts_client.order_execution.confirm_group_order(request=oco_group_request)
        )

        # --- 4. Process and Display OCO Confirmation Results ---
        print("\nOCO Group Confirmation Details:")
        if oco_confirmation.Confirmations:
            print("  Confirmed Order Details:")
            # Iterate through the GroupOrderConfirmationDetail objects
            for detail in oco_confirmation.Confirmations:
                print(f"    - ConfirmID: {detail.OrderConfirmID}")
                print(f"      Summary: {detail.SummaryMessage}")
                print(
                    f"      Est. Cost: {detail.EstimatedCost}, Est. Commission: {detail.EstimatedCommission}"
                )
        if oco_confirmation.Errors:
            print("  Errors:")
            for error in oco_confirmation.Errors:
                print(
                    f"    - OrderID: {error.OrderID}, Error: {error.Error}, Message: {error.Message}"
                )
        # Optional: Print full parsed response
        # print("\nParsed Confirmation Response:")
        # print(oco_confirmation.model_dump_json(indent=2))

    except aiohttp.ClientResponseError as e:
        print(f"\nHTTP ERROR occurred: Status={e.status}, Message='{e.message}'")
        print(f"  Request URL: {e.request_info.url}")
        # Add logic to attempt reading response body if possible
        try:
            error_body = await e.text()  # Or e.json() if appropriate
            print(f"  Response Body: {error_body}")
        except Exception as body_e:
            print(f"  (Could not read error response body: {body_e})")

    except ValidationError as ve:
        # This shouldn't happen now, but keep for safety
        print(f"\nPydantic Validation FAILED (This shouldn't happen after model correction!):")
        print(ve)
    except AttributeError as e:
        print(f"ERROR: Could not find necessary method or attribute: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        # import traceback
        # traceback.print_exc()
    finally:
        await ts_client.close()
        print("\nClient session closed.")


if __name__ == "__main__":
    asyncio.run(main())
