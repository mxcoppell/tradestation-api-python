#!/usr/bin/env python
"""
Example demonstrating how to fetch bar history data using the TradeStation API.

This example shows how to:
1. Get daily bars for a stock
2. Get minute bars for a stock
3. Get bars for a specific date range
4. Format and display the bar data

Requirements:
- TradeStation API credentials in .env file
"""

import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

from src.client.tradestation_client import TradeStationClient
from src.ts_types.config import ClientConfig


async def main():
    """Run the bar history examples."""
    # Load environment variables
    load_dotenv()

    # Create client configuration from environment variables
    config = ClientConfig(
        client_id=os.getenv("CLIENT_ID", ""),
        client_secret=os.getenv("CLIENT_SECRET", ""),
        redirect_uri=os.getenv("REDIRECT_URI", ""),
        refresh_token=os.getenv("REFRESH_TOKEN", ""),
    )

    # Create TradeStation client
    client = TradeStationClient(config)

    # Example 1: Get daily bars for the last 5 days
    print("\n=== Example 1: Daily Bars for MSFT (Last 5 Days) ===")
    daily_bars = await client.market_data.get_bar_history("MSFT", {
        "unit": "Daily",
        "barsback": 5
    })
    
    print(f"Retrieved {len(daily_bars.Bars)} daily bars")
    
    # Display the bars in a table format
    print("\nDate       | Open    | High    | Low     | Close   | Volume")
    print("-" * 65)
    
    for bar in daily_bars.Bars:
        # Convert ISO timestamp to date
        date = datetime.fromisoformat(bar.TimeStamp.replace("Z", "+00:00")).strftime("%Y-%m-%d")
        print(f"{date} | {bar.Open:8} | {bar.High:8} | {bar.Low:8} | {bar.Close:8} | {int(bar.TotalVolume):,}")

    # Example 2: Get 5-minute bars for the last trading day
    print("\n=== Example 2: 5-Minute Bars for AAPL (Last 10 Bars) ===")
    minute_bars = await client.market_data.get_bar_history("AAPL", {
        "unit": "Minute",
        "interval": "5",
        "barsback": 10
    })
    
    print(f"Retrieved {len(minute_bars.Bars)} 5-minute bars")
    
    # Display the bars in a table format
    print("\nTime                | Open    | High    | Low     | Close   | Volume")
    print("-" * 75)
    
    for bar in minute_bars.Bars:
        # Convert ISO timestamp to readable time
        time = datetime.fromisoformat(bar.TimeStamp.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{time} | {bar.Open:8} | {bar.High:8} | {bar.Low:8} | {bar.Close:8} | {int(bar.TotalVolume):,}")

    # Example 3: Get 1-minute bars for a specific date range with extended hours
    # Calculate yesterday's date
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%d")
    
    print(f"\n=== Example 3: 1-Minute Bars for SPY with Date Range and Extended Hours ===")
    print(f"Date range: {yesterday_str} 09:30:00 to {yesterday_str} 10:00:00 ET")
    
    date_range_bars = await client.market_data.get_bar_history("SPY", {
        "unit": "Minute",
        "interval": "1",
        "firstdate": f"{yesterday_str}T14:30:00Z",  # 09:30 ET in UTC
        "lastdate": f"{yesterday_str}T15:00:00Z",   # 10:00 ET in UTC
        "sessiontemplate": "USEQPreAndPost"
    })
    
    print(f"Retrieved {len(date_range_bars.Bars)} 1-minute bars")
    
    # Display the bars in a table format
    print("\nTime                | Open    | High    | Low     | Close   | Volume")
    print("-" * 75)
    
    for bar in date_range_bars.Bars:
        # Convert ISO timestamp to readable time
        time = datetime.fromisoformat(bar.TimeStamp.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{time} | {bar.Open:8} | {bar.High:8} | {bar.Low:8} | {bar.Close:8} | {int(bar.TotalVolume):,}")

    # Close the client
    await client.close()


if __name__ == "__main__":
    asyncio.run(main()) 