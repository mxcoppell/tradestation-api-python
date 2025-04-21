#!/usr/bin/env python
"""
Example demonstrating how to retrieve the list of available activation triggers
using the TradeStation API.

Activation triggers define the conditions (based on price movements like Bid, Ask, Last)
that can be used to activate conditional orders (e.g., stop orders).

This example shows how to:
1. Initialize the TradeStation client.
2. Call the `get_activation_triggers` endpoint using the client.
3. Process and display the list of available triggers.

Usage:
    python get_activation_triggers.py

Requirements:
    - A valid TradeStation account.
    - API credentials (CLIENT_ID, REFRESH_TOKEN) and ENVIRONMENT in a .env file.
"""

import asyncio
import os
from dotenv import load_dotenv
import aiohttp
from pydantic import ValidationError

# Import the client
from tradestation.client.tradestation_client import TradeStationClient

# Import necessary types
from tradestation.ts_types.order_execution import ActivationTriggers, ActivationTrigger


async def main():
    """Main function to demonstrate fetching activation triggers."""
    load_dotenv()
    ts_client = TradeStationClient()

    try:
        # --- 1. Get Activation Triggers using the client method ---
        print("\nFetching Activation Triggers...")
        # This method doesn't require specific account IDs or request bodies
        activation_triggers_response: ActivationTriggers = (
            await ts_client.order_execution.get_activation_triggers()
        )

        # --- 2. Process and Display Activation Triggers ---
        print("\nAvailable Activation Triggers:")

        if activation_triggers_response and activation_triggers_response.ActivationTriggers:
            if not activation_triggers_response.ActivationTriggers:
                print("  No activation triggers found.")
            else:
                for trigger in activation_triggers_response.ActivationTriggers:
                    if isinstance(trigger, ActivationTrigger):
                        # Print details on separate lines with indentation
                        print(f"  - Trigger:")
                        print(f"      Key:         {trigger.Key}")
                        print(f"      Name:        {trigger.Name}")
                        print(f"      Description: {trigger.Description}")
                    else:
                        print(f"  - Unexpected item type in triggers list: {trigger}")
        else:
            print("  Unexpected response format or empty response.")
            if hasattr(activation_triggers_response, "model_dump_json"):
                print(f"    Raw Response: {activation_triggers_response.model_dump_json(indent=2)}")
            else:
                print(f"    Raw Response: {activation_triggers_response}")

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
