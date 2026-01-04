import asyncio

from dotenv import load_dotenv

from tradestation.client import TradeStationClient

# Load environment variables from .env file
load_dotenv()


async def main():
    """
    Main function to demonstrate getting beginning of day (BOD) account balances.
    Initializes the client, fetches accounts, and then retrieves and prints BOD balances for each account.
    """

    # Initialize the TradeStation client
    # Rely on client internal logic to read env vars loaded by load_dotenv()
    client = TradeStationClient()

    try:
        # Get accounts first to get the account IDs
        print("\nGetting accounts...")
        accounts = await client.brokerage.get_accounts()

        if accounts:
            print(f"Found {len(accounts)} account(s).")

            # --- Get Beginning of Day Balances for a single account ---
            account_id = accounts[0].AccountID
            print(f"\n--- Fetching BOD balance for Account ID: {account_id} ---")
            bod_balance_response = await client.brokerage.get_balances_bod(account_id)

            if bod_balance_response and bod_balance_response.BODBalances:
                for balance in bod_balance_response.BODBalances:
                    print(f"Account: {balance.AccountID}")
                    print(f"Account Type: {balance.AccountType or 'N/A'}")

                    # Display BOD balance details if available
                    if balance.BalanceDetail:
                        print("\nBOD Balance Details:")
                        detail = balance.BalanceDetail
                        # Display properties that exist in the BOD BalanceDetail object
                        # Adjust these based on the actual available properties in the Python model
                        print(f"  Account Balance: ${detail.AccountBalance or 'N/A'}")
                        print(
                            f"  Cash Available To Withdraw: ${detail.CashAvailableToWithdraw or 'N/A'}"
                        )
                        print(f"  Day Trades: {detail.DayTrades or 'N/A'}")
                        print(f"  Equity: ${detail.Equity or 'N/A'}")
                        print(f"  Net Cash: ${detail.NetCash or 'N/A'}")
            else:
                print(f"Could not retrieve BOD balance details for account {account_id}.")
            print("---")

            # --- Get Beginning of Day Balances for multiple accounts (if available) ---
            if len(accounts) > 1:
                # Example: Take first two accounts
                account_ids_list = [acc.AccountID for acc in accounts[:2]]
                account_ids_str = ",".join(account_ids_list)
                print(f"\n--- Fetching BOD balances for Account IDs: {account_ids_str} ---")

                # NOTE: The API likely expects a comma-separated string for multiple accounts,
                # similar to the TS example. Verify this assumption with API docs or testing.
                # Passing the string directly here.
                multi_bod_balance_response = await client.brokerage.get_balances_bod(
                    account_ids_str
                )

                if multi_bod_balance_response and multi_bod_balance_response.BODBalances:
                    for balance in multi_bod_balance_response.BODBalances:
                        print(f"\nAccount: {balance.AccountID}")
                        print(f"Account Type: {balance.AccountType or 'N/A'}")

                        # Display BOD balance details if available
                        if balance.BalanceDetail:
                            print("\nBOD Balance Details:")
                            detail = balance.BalanceDetail
                            print(f"  Account Balance: ${detail.AccountBalance or 'N/A'}")
                            print(
                                f"  Cash Available To Withdraw: ${detail.CashAvailableToWithdraw or 'N/A'}"
                            )
                            print(f"  Equity: ${detail.Equity or 'N/A'}")
                            print(f"  Net Cash: ${detail.NetCash or 'N/A'}")
                        print("---")
                else:
                    print(f"Could not retrieve BOD balance details for accounts {account_ids_str}.")
                print("---")

        else:
            print("No accounts found. Cannot fetch BOD balances.")

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
