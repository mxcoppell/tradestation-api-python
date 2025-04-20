#!/usr/bin/env python
"""
Example demonstrating how to get option risk/reward data using the TradeStation API.

This example shows how to:
1. Create a TradeStationClient
2. Get option risk/reward data for a specific option spread using the structure defined in the OpenAPI spec
"""

import asyncio
import os
from dotenv import load_dotenv
from typing import List, Dict, Any

from src.client.tradestation_client import TradeStationClient

# Note: The Pydantic models RiskRewardAnalysisInput/RiskRewardLeg in ts_types are INCORRECT for this endpoint.
# We are using a dictionary matching the OpenAPI spec instead.
# from src.ts_types.market_data import RiskRewardAnalysisInput, RiskRewardLeg
# from src.ts_types.market_data import RiskRewardAnalysis # The old response model IS incorrect
from src.ts_types.market_data import RiskRewardAnalysisResult  # The CORRECT response model


async def main():
    # Load environment variables from .env file
    load_dotenv()

    # Create TradeStationClient (configuration loaded from environment variables)
    client = TradeStationClient()

    # Define the option spread to analyze based on OpenAPI spec
    # Using data provided by user
    spread_price = 0.13  # OpenAPI spec defines this as number, not string
    legs_input: List[Dict[str, Any]] = [
        {"Symbol": "AAPL 261218C185", "Quantity": 1, "TradeAction": "BUY"},  # Positive for BUY
        {
            "Symbol": "AAPL 261218P180",
            "Quantity": 1,  # Positive for SELL (Quantity is absolute, action determines direction)
            "TradeAction": "SELL",
        },
    ]

    # Construct the input object as a dictionary matching OpenAPI spec
    analysis_input: Dict[str, Any] = {"SpreadPrice": spread_price, "Legs": legs_input}

    try:
        print(f"\nGetting option risk/reward data for spread:")
        for leg in legs_input:
            print(f"  Leg: {leg['Symbol']}, Action: {leg['TradeAction']}, Qty: {leg['Quantity']}")

        # Call the get_option_risk_reward method with the dictionary input
        # This method internally calls http_client.post(..., data=analysis_input)
        risk_reward_data = await client.market_data.get_option_risk_reward(analysis_input)

        # Print the risk/reward data - Assuming RiskRewardAnalysis response model is correct
        # Need to verify the actual fields in RiskRewardAnalysis based on OpenAPI response schema
        print(
            f"\nRisk/Reward Analysis Results (verify fields based on RiskRewardAnalysisResult schema):"
        )
        # Accessing fields based on the OpenAPI schema for RiskRewardAnalysisResult
        print(f"  Max Gain Infinite: {risk_reward_data.MaxGainIsInfinite}")
        print(f"  Adjusted Max Gain: {risk_reward_data.AdjustedMaxGain}")
        print(f"  Max Loss Infinite: {risk_reward_data.MaxLossIsInfinite}")
        print(f"  Adjusted Max Loss: {risk_reward_data.AdjustedMaxLoss}")
        print(f"  Breakeven Points: {risk_reward_data.BreakevenPoints}")

        # The original RiskRewardAnalysis model had different fields, let's comment those out
        # print(f"  Spread Price: {risk_reward_data.SpreadPrice}")
        # print(f"  Maximum Gain: {risk_reward_data.MaxGain}")
        # print(f"  Maximum Loss: {risk_reward_data.MaxLoss}")
        # print(f"  Risk/Reward Ratio: {risk_reward_data.RiskRewardRatio}")
        # print(f"  Estimated Commission: {risk_reward_data.Commission}")
        # print(f"  Legs Details:")
        # for leg in risk_reward_data.Legs: # Legs are NOT part of the response schema
        #     print(f"    Symbol: {leg.Symbol}, Ratio: {leg.Ratio}, Open: {leg.OpenPrice}, Target: {leg.TargetPrice}, Stop: {leg.StopPrice}")

    except Exception as e:
        print(f"Error getting risk/reward data: {e}")
    finally:
        # Close the client session
        await client.close()


if __name__ == "__main__":
    # Ensure the event loop is managed correctly for async operations
    asyncio.run(main())
