#!/usr/bin/env python
"""
Example demonstrating how to get option risk/reward data using the TradeStation API.

This example shows how to:
1. Create a TradeStationClient
2. Get option risk/reward data for a specific option spread
"""

import asyncio
import os
from dotenv import load_dotenv
from typing import List, Dict, Any

from src.client.tradestation_client import TradeStationClient
from src.ts_types.market_data import RiskRewardAnalysisInput, RiskRewardLeg


async def main():
    # Load environment variables from .env file
    load_dotenv()

    # Create TradeStationClient (configuration loaded from environment variables)
    client = TradeStationClient()

    # Define the option spread to analyze (Example: AAPL Vertical Call Spread)
    spread_price = "1.50"  # Example spread price (difference between leg prices)
    legs_input: List[Dict[str, Any]] = [
        {
            "Symbol": "AAPL 241115C00170000",  # Buy AAPL Call, Nov 15 2024 Exp, $170 Strike
            "Ratio": 1,
            "OpenPrice": "3.50",  # Example price paid for this leg
            "TargetPrice": "5.00",  # Example target price
            "StopPrice": "2.00",  # Example stop price
        },
        {
            "Symbol": "AAPL 241115C00175000",  # Sell AAPL Call, Nov 15 2024 Exp, $175 Strike
            "Ratio": -1,
            "OpenPrice": "2.00",  # Example price received for this leg
            "TargetPrice": "1.00",  # Example target price
            "StopPrice": "3.00",  # Example stop price
        },
    ]

    # Construct the input object as a dictionary
    analysis_input: Dict[str, Any] = {"SpreadPrice": spread_price, "Legs": legs_input}

    try:
        print(f"\nGetting option risk/reward data for spread:")
        for leg in legs_input:
            print(f"  Leg: {leg['Symbol']}, Ratio: {leg['Ratio']}")

        # Call the get_option_risk_reward method with the dictionary input
        risk_reward_data = await client.market_data.get_option_risk_reward(analysis_input)

        # Print the risk/reward data
        print(f"\nRisk/Reward Analysis Results:")
        print(f"  Spread Price: {risk_reward_data.SpreadPrice}")
        print(f"  Maximum Gain: {risk_reward_data.MaxGain}")
        print(f"  Maximum Loss: {risk_reward_data.MaxLoss}")
        print(f"  Risk/Reward Ratio: {risk_reward_data.RiskRewardRatio}")
        print(f"  Estimated Commission: {risk_reward_data.Commission}")
        print(f"  Legs Details:")
        for leg in risk_reward_data.Legs:
            print(
                f"    Symbol: {leg.Symbol}, Ratio: {leg.Ratio}, Open: {leg.OpenPrice}, Target: {leg.TargetPrice}, Stop: {leg.StopPrice}"
            )

    except Exception as e:
        print(f"Error getting risk/reward data: {e}")
    finally:
        # Close the client session
        await client.close()


if __name__ == "__main__":
    # Ensure the event loop is managed correctly for async operations
    asyncio.run(main())
