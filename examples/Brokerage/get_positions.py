"""
Example script for fetching brokerage positions using the TradeStation API.

This script demonstrates how to:
- Initialize the TradeStation client.
- Fetch positions for specified account(s).
- Print the details of each position.
"""

import asyncio
import os
from dotenv import load_dotenv

# Import the TradeStation client
from tradestation.client import TradeStationClient


async def main():
    """
    Main asynchronous function to fetch and display positions.
    """
    # Load environment variables from .env file
    load_dotenv()

    # Validate required environment variables are present (client will handle actual values)
    if not os.getenv("CLIENT_ID") or not os.getenv("REFRESH_TOKEN"):
        print("Error: CLIENT_ID and REFRESH_TOKEN must be set in the .env file.")
        return

    print("Initializing TradeStation client...")
    # Initialize the TradeStation client
    # Authentication (token refresh) happens automatically if needed on the first API call
    # It will use environment variables CLIENT_ID, REFRESH_TOKEN, ENVIRONMENT if not passed explicitly
    ts_client = TradeStationClient()

    try:
        print("Fetching account IDs...")
        # First, get account IDs (required for subsequent calls)
        # Access services via the client instance (e.g., ts_client.brokerage)
        accounts = await ts_client.brokerage.get_accounts()
        if not accounts:
            print("No brokerage accounts found.")
            await ts_client.close()  # Ensure client cleanup
            return

        # Collect all account IDs
        all_account_ids = [acc.AccountID for acc in accounts]
        account_ids_str = ",".join(all_account_ids)
        print(f"Found Account IDs: {account_ids_str}")

        # Fetch positions for all accounts
        print(f"Fetching positions for accounts: {account_ids_str}...")
        positions_response = await ts_client.brokerage.get_positions(account_ids=account_ids_str)

        # Check for errors in the response
        if positions_response.Errors:
            print("\nErrors encountered while fetching positions:")
            for error in positions_response.Errors:
                print(f"- Account {error.AccountID}: {error.Message} ({error.Error})")

        # Print the positions found
        if positions_response.Positions:
            print(f"\nFound {len(positions_response.Positions)} positions:")
            for position in positions_response.Positions:
                print("--- Position --- ")
                print(f"  Account ID: {position.AccountID}")
                print(f"  Symbol: {position.Symbol}")
                print(f"  Asset Type: {position.AssetType}")
                print(f"  Quantity: {position.Quantity}")
                print(f"  Average Price: {position.AveragePrice}")
                print(f"  Last Price: {position.Last}")
                print(f"  Market Value: {position.MarketValue}")
                print(f"  Total Cost: {position.TotalCost}")
                print(f"  Today's P/L: {position.TodaysProfitLoss}")
                print(f"  Unrealized P/L: {position.UnrealizedProfitLoss}")
                print(f"  Unrealized P/L %: {position.UnrealizedProfitLossPercent}")
                print(f"  Long/Short: {position.LongShort}")
                # Add more fields as needed (e.g., for options)
                if position.AssetType == "OPTION":
                    print(f"  Expiration: {position.ExpirationDate}")
                    print(f"  Type: {position.OptionType}")
                    print(f"  Strike: {position.StrikePrice}")
                    print(f"  Underlying: {position.Underlying}")
        else:
            # Only print this if no errors occurred for any relevant account
            # Note: This check might need refinement if errors occur for *some* accounts
            # but positions are successfully retrieved for others.
            # For simplicity, we check if there are *any* positions at all.
            if not positions_response.Errors:
                print("\nNo open positions found for any of the specified accounts.")

    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        # Ensure the client session is closed
        await ts_client.close()


# Run the main function using asyncio
if __name__ == "__main__":
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("Error: .env file not found. Please create it with your credentials.")
        print("See .env.example for required variables (CLIENT_ID, REFRESH_TOKEN, ENVIRONMENT).")
    else:
        # Check if required variables are set
        load_dotenv()
        if not os.getenv("CLIENT_ID") or not os.getenv("REFRESH_TOKEN"):
            print("Error: CLIENT_ID and REFRESH_TOKEN must be set in the .env file.")
        else:
            asyncio.run(main())
