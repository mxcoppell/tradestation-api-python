import asyncio
from dotenv import load_dotenv
from tradestation.client.tradestation_client import TradeStationClient

# Load environment variables from .env file
load_dotenv()


async def main():
    """
    Main function to demonstrate getting account balances.
    Initializes the client, fetches accounts, and then retrieves and prints balances for each account.
    """

    # Initialize the TradeStation client
    # Rely on client internal logic to read env vars loaded by load_dotenv()
    client = TradeStationClient()

    try:
        # Authenticate the client
        # await client.authenticate()
        # print("Authentication successful.")

        # Get accounts first to get the account IDs
        print("\nGetting accounts...")
        accounts = await client.brokerage.get_accounts()

        if accounts:
            print(f"Found {len(accounts)} account(s).")
            # Get balances for all accounts
            print("\nGetting Balances for All Accounts:")

            # Process each account
            for account in accounts:
                account_id = account.AccountID
                print(f"\n--- Fetching balance for Account ID: {account_id} ---")
                balance_response = await client.brokerage.get_balances(account_id)

                if balance_response and balance_response.Balances:
                    account_balance = balance_response.Balances[0]

                    print(f"Account: {account_balance.AccountID}")
                    print(f"Account Type: {account_balance.AccountType or 'N/A'}")

                    # Display basic balance information
                    print("Balance Information:")
                    print(f"  Cash Balance: ${account_balance.CashBalance or 'N/A'}")
                    print(f"  Equity: ${account_balance.Equity or 'N/A'}")
                    print(f"  Market Value: ${account_balance.MarketValue or 'N/A'}")
                    print(f"  Buying Power: ${account_balance.BuyingPower or 'N/A'}")
                    print(f"  Today's P/L: ${account_balance.TodaysProfitLoss or 'N/A'}")

                    # Display balance details if available
                    if account_balance.BalanceDetail:
                        print("\nBalance Details:")
                        detail = account_balance.BalanceDetail
                        # Only display properties that exist in the BalanceDetail object
                        if detail.MarginRequirement is not None:
                            print(f"  Margin Requirement: ${detail.MarginRequirement}")
                        if detail.DayTradeMargin is not None:
                            print(f"  Day Trade Margin: ${detail.DayTradeMargin}")
                        if detail.UnsettledFunds is not None:
                            print(f"  Unsettled Funds: ${detail.UnsettledFunds}")

                    # Display currency details if available
                    if account_balance.CurrencyDetails:
                        print("\nCurrency Details:")
                        for currency in account_balance.CurrencyDetails:
                            print(f"  {currency.Currency}:")
                            if currency.CashBalance is not None:
                                print(f"    Cash Balance: ${currency.CashBalance}")
                            if currency.MarginRequirement is not None:
                                print(f"    Margin Requirement: ${currency.MarginRequirement}")
                            if currency.NonTradeDebit is not None:
                                print(f"    Non-Trade Debit: ${currency.NonTradeDebit}")
                            if currency.TradeEquity is not None:
                                print(f"    Trade Equity: ${currency.TradeEquity}")
                else:
                    print(f"Could not retrieve balance details for account {account_id}.")
                print("---")
        else:
            print("No accounts found. Cannot fetch balances.")

    except Exception as e:
        # Catch any exceptions during the process
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()  # Print full traceback for debugging
    finally:
        # Ensure the client session is closed using the client's close method
        if "client" in locals() and client:  # Check if client was successfully initialized
            await client.close()
            print("\nClient session closed.")


if __name__ == "__main__":
    # Run the main async function
    asyncio.run(main())
