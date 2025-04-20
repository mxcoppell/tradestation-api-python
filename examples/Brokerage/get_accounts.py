#!/usr/bin/env python
"""
Example demonstrating how to fetch all brokerage accounts using the TradeStation API.

This example shows how to:
1. Initialize the TradeStation client
2. Fetch all brokerage accounts
3. Process and display account information

Usage:
    python get_accounts.py

Requirements:
    - A valid TradeStation account
    - API credentials in .env file (run `get_refresh_token.sh` to populate REFRESH_TOKEN)
"""

import asyncio
from dotenv import load_dotenv

from src.client.tradestation_client import TradeStationClient


async def main():
    """Main function to demonstrate fetching all brokerage accounts."""
    # Load environment variables from .env file
    load_dotenv()

    # Initialize the TradeStation client
    client = TradeStationClient(debug=True)

    try:
        # Get all accounts
        print("\nGetting All Accounts:")
        accounts = await client.brokerage.get_accounts()

        # Process and display the results
        if accounts:
            for account in accounts:
                print(f"\nAccount: {account.AccountID}")
                print(f"Type: {account.AccountType}")
                if account.Alias:
                    print(f"Alias: {account.Alias}")
                print(f"Currency: {account.Currency}")
                print(f"Status: {account.Status}")

                if account.AccountDetail:
                    print("\nAccount Details:")
                    print(f"  Option Level: {account.AccountDetail.OptionApprovalLevel}")
                    print(
                        f"  Day Trading Qualified: {'Yes' if account.AccountDetail.DayTradingQualified else 'No'}"
                    )
                    print(
                        f"  Pattern Day Trader: {'Yes' if account.AccountDetail.PatternDayTrader else 'No'}"
                    )
                    print(
                        f"  Stock Locate Eligible: {'Yes' if account.AccountDetail.IsStockLocateEligible else 'No'}"
                    )
                    print(
                        f"  Reg T Program: {'Yes' if account.AccountDetail.EnrolledInRegTProgram else 'No'}"
                    )
                    print(
                        f"  Buying Power Warning: {'Yes' if account.AccountDetail.RequiresBuyingPowerWarning else 'No'}"
                    )
                print("---")
        else:
            print("No accounts found.")

    except Exception as e:
        print(f"Error fetching accounts: {e}")


if __name__ == "__main__":
    asyncio.run(main())
