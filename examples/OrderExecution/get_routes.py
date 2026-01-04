#!/usr/bin/env python
"""
Example demonstrating how to retrieve the list of available order routes
using the TradeStation API.

Order routes define the different exchanges or execution venues available
for directing orders.

This example shows how to:
1. Initialize the TradeStation client.
2. Call the `get_routes` endpoint using the client.
3. Process and display the list of available routes.

Usage:
    python get_routes.py

Requirements:
    - A valid TradeStation account.
    - API credentials (CLIENT_ID, REFRESH_TOKEN) and ENVIRONMENT in a .env file.
"""

import asyncio
import os

import aiohttp
from dotenv import load_dotenv
from pydantic import ValidationError

# Import the client
from tradestation.client import TradeStationClient

# Import necessary types
from tradestation.ts_types.order_execution import Route, RoutesResponse


async def main():
    """Main function to demonstrate fetching order routes."""
    load_dotenv()
    ts_client = TradeStationClient()

    try:
        # --- 1. Get Order Routes using the client method ---
        print("\nFetching Order Routes...")
        # This method doesn't require specific account IDs or request bodies
        routes_response: RoutesResponse = await ts_client.order_execution.get_routes()

        # --- 2. Process and Display Order Routes ---
        print("\nAvailable Order Routes:")

        if routes_response and routes_response.Routes:
            if not routes_response.Routes:
                print("  No order routes found.")
            else:
                for route in routes_response.Routes:
                    if isinstance(route, Route):
                        # Print details on separate lines with indentation
                        print(f"  - Route:")
                        print(f"      Name:        {route.Name}")
                        print(f"      ID:          {route.Id}")
                        print(f"      Asset Types: {', '.join(route.AssetTypes)}")
                    else:
                        print(f"  - Unexpected item type in routes list: {route}")
        else:
            print("  Unexpected response format or empty response.")
            if hasattr(routes_response, "model_dump_json"):
                print(f"    Raw Response: {routes_response.model_dump_json(indent=2)}")
            else:
                print(f"    Raw Response: {routes_response}")

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
