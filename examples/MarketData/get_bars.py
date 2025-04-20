#!/usr/bin/env python
"""
Example demonstrating how to fetch bar history data using the TradeStation API Python wrapper.

This example shows how to:
1. Get daily bars for MSFT (last 5 days)
2. Get 1-minute bars for MSFT with extended hours for a specific date range
3. Get weekly bars for MSFT (last month)
"""

import asyncio
import os
from dotenv import load_dotenv
from src.client.tradestation_client import TradeStationClient

# Load environment variables from .env file
load_dotenv()


async def main():
    # Initialize the TradeStation client with refresh token from environment variables
    client = TradeStationClient()

    try:
        # Example 1: Get daily bars for the last 5 days
        daily_bars = await client.market_data.get_bar_history(
            "MSFT", {"unit": "Daily", "barsback": 5}
        )
        print("\nDaily Bars for MSFT:")
        for bar in daily_bars.Bars:
            print(f"Date: {bar.TimeStamp}")
            print(f"Open: {bar.Open}")
            print(f"High: {bar.High}")
            print(f"Low: {bar.Low}")
            print(f"Close: {bar.Close}")
            print(f"Volume: {bar.TotalVolume}")
            print("---")

        # Example 2: Get 1-minute bars for a specific date range with extended hours
        try:
            minute_bars = await client.market_data.get_bar_history(
                "MSFT",
                {
                    "unit": "Minute",
                    "interval": "1",
                    "firstdate": "2024-01-01T14:30:00Z",
                    "lastdate": "2024-01-01T21:00:00Z",
                    "sessiontemplate": "USEQPreAndPost",
                },
            )
            print("\n1-Minute Bars for MSFT with Extended Hours:")
            for bar in minute_bars.Bars:
                print(f"Time: {bar.TimeStamp}")
                print(f"Close: {bar.Close}")
                print(f"Volume: {bar.TotalVolume}")
                print("---")
        except Exception as e:
            print(f"Error fetching 1-minute bars with extended hours: {e}")

        # Example 3: Get weekly bars for the last month
        weekly_bars = await client.market_data.get_bar_history(
            "MSFT", {"unit": "Weekly", "barsback": 4}
        )
        print("\nWeekly Bars for MSFT:")
        for bar in weekly_bars.Bars:
            print(f"Week of: {bar.TimeStamp}")
            print(f"Open: {bar.Open}")
            print(f"High: {bar.High}")
            print(f"Low: {bar.Low}")
            print(f"Close: {bar.Close}")
            print(f"Volume: {bar.TotalVolume}")
            print("---")

    except Exception as error:
        print(f"Error: {error}")
    finally:
        # Always close the client to clean up resources
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
