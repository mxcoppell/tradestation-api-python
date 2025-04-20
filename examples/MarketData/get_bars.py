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
    # Initialize the TradeStation client; override Simulation env to Live for bar history examples
    env = os.getenv("ENVIRONMENT", "Simulation")
    if env.lower() == "simulation":
        print(
            "Warning: Simulation environment may not support bar history; using Live environment for this example."
        )
        client = TradeStationClient(environment="Live")
    else:
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

        # Example 2: Get 5-minute bars for MSFT (last trading day)
        print("\nExample 2: 5-Minute Bars for MSFT (last trading day)")
        five_minute_bars = await client.market_data.get_bar_history(
            "MSFT",
            {"unit": "Minute", "interval": "5", "barsback": 78},  # ~6.5 hours of 5-minute bars
        )
        for bar in five_minute_bars.Bars:
            print(f"Time: {bar.TimeStamp}")
            print(f"Open: {bar.Open}")
            print(f"High: {bar.High}")
            print(f"Low: {bar.Low}")
            print(f"Close: {bar.Close}")
            print(f"Volume: {bar.TotalVolume}")
            print("---")

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
