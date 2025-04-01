from typing import Any, Dict, List, Optional, Union

from ...client.http_client import HttpClient
from ...streaming.stream_manager import StreamManager
from ...ts_types.brokerage import HistoricalOrdersById, Account, AccountDetail


class BrokerageService:
    """
    Service for accessing TradeStation brokerage data

    This is a placeholder until the full implementation in a separate task.
    """

    def __init__(self, http_client: HttpClient, stream_manager: StreamManager):
        """
        Creates a new BrokerageService

        Args:
            http_client: The HttpClient to use for API requests
            stream_manager: The StreamManager to use for streaming
        """
        self.http_client = http_client
        self.stream_manager = stream_manager

    async def get_accounts(self) -> List[Account]:
        """
        Fetches brokerage account information for the authenticated user.

        This endpoint provides detailed account information including:
        - Account identifiers and types
        - Trading permissions and capabilities
        - Account status and details

        Request valid for Cash, Margin, Futures, and DVP account types.

        Returns:
            A list of Account objects containing:
            - AccountID: Unique identifier for the account
            - AccountType: Type of account (Cash, Margin, Futures, DVP)
            - Alias: User-specified nickname for the account (if set)
            - AltID: TradeStation account ID for accounts based in Japan (if applicable)
            - Currency: Account base currency
            - Status: Current account status (Active, Closed, etc.)
            - AccountDetail: Additional account details including:
              - IsStockLocateEligible: Whether account can use stock locate service
              - EnrolledInRegTProgram: Whether account is enrolled in RegT program
              - RequiresBuyingPowerWarning: Whether buying power warnings are required
              - DayTradingQualified: Whether account is qualified for day trading
              - OptionApprovalLevel: Level of option trading permissions (1-5)
              - PatternDayTrader: Whether account is flagged as a pattern day trader

        Raises:
            Exception: If the request fails due to network issues or API errors

        Example:
            ```python
            accounts = await brokerage_service.get_accounts()

            # Process account information
            for account in accounts:
                print(f"Account {account.AccountID}:")
                print(f"- Type: {account.AccountType}")
                print(f"- Status: {account.Status}")
                print("- Details:")
                if account.AccountDetail:
                    print(f"  - Option Level: {account.AccountDetail.OptionApprovalLevel}")
                    print(f"  - Day Trading: {'Yes' if account.AccountDetail.DayTradingQualified else 'No'}")
            ```
        """
        response = await self.http_client.get("/v3/brokerage/accounts")

        accounts = []
        for account_data in response["Accounts"]:
            # Process AccountDetail separately to handle validation correctly
            account_detail = None
            if "AccountDetail" in account_data and account_data["AccountDetail"]:
                account_detail = AccountDetail.model_validate(account_data["AccountDetail"])

            # Remove AccountDetail from the data to avoid validation error
            if "AccountDetail" in account_data:
                del account_data["AccountDetail"]

            # Create the Account object
            account = Account.model_validate(account_data)

            # Set the AccountDetail after validation
            account.AccountDetail = account_detail

            accounts.append(account)

        return accounts

    async def get_historical_orders_by_order_id(
        self, account_ids: str, order_ids: str, since: str
    ) -> HistoricalOrdersById:
        """
        Fetches Historical Orders for the given Accounts except open orders, filtered by given Order IDs prior to current date,
        sorted in descending order of time closed. Request valid for all account types.

        This endpoint provides historical order information for specific orders, including:
        - Order details (ID, type, status, timestamps)
        - Execution details (filled quantity, execution price)
        - Order legs for complex orders (spreads, multi-leg orders)
        - Order routing and venue information

        Args:
            account_ids: List of valid Account IDs in comma separated format (e.g. "61999124,68910124").
                        1 to 25 Account IDs can be specified. Recommended batch size is 10.
            order_ids: List of valid Order IDs in comma separated format (e.g. "123456789,286179863").
                      1 to 50 Order IDs can be specified.
            since: Historical orders since date (e.g. "2006-01-13", "01-13-2006", "2006/01/13", "01/13/2006").
                   Limited to 90 days prior to the current date.

        Returns:
            A HistoricalOrdersById object containing:
            - Orders: Array of historical order information, each containing:
                - AccountID: Account that placed the order
                - ClosedDateTime: When the order was closed/filled
                - Duration: Order duration (DAY, GTC, etc.)
                - Legs: Array of order legs, each containing:
                  - AssetType: Type of asset (STOCK, OPTION, etc.)
                  - BuyOrSell: Buy or Sell action
                  - ExecQuantity: Quantity that was executed
                  - ExecutionPrice: Price at which the order was executed
                  - OpenOrClose: Whether opening or closing a position
                  - QuantityOrdered: Original quantity ordered
                  - QuantityRemaining: Quantity still to be filled
                  - Symbol: Symbol being traded
                  - ExpirationDate: Option expiration date (for options)
                  - OptionType: Call or Put (for options)
                  - StrikePrice: Strike price (for options)
                  - Underlying: Underlying symbol (for options)
                - OpenedDateTime: When the order was placed
                - OrderID: Unique identifier for the order
                - OrderType: Type of order (Market, Limit, etc.)
                - Status: Current status of the order
                - StatusDescription: Detailed status description
                - LimitPrice: Limit price for limit orders
                - StopPrice: Stop price for stop orders
                - AdvancedOptions: Advanced order options including:
                  - TrailingStop: Whether trailing stop is enabled
                  - TrailingStopAmount: Amount for trailing stop
            - Errors: Optional array of errors that occurred, each containing:
                - AccountID: ID of the account that had an error
                - Error: Error code
                - Message: Detailed error message

        Raises:
            ValueError: If the date range exceeds 90 days
            Exception: If the request fails due to network issues or API errors
        """
        # Validate date range
        from datetime import datetime, timedelta

        # Parse the since date, supporting multiple formats
        try:
            since_date = datetime.strptime(since, "%Y-%m-%d")
        except ValueError:
            try:
                since_date = datetime.strptime(since, "%m-%d-%Y")
            except ValueError:
                try:
                    since_date = datetime.strptime(since, "%Y/%m/%d")
                except ValueError:
                    try:
                        since_date = datetime.strptime(since, "%m/%d/%Y")
                    except ValueError:
                        raise ValueError(
                            f"Invalid date format: {since}. Expected formats: YYYY-MM-DD, MM-DD-YYYY, YYYY/MM/DD, MM/DD/YYYY"
                        )

        ninety_days_ago = datetime.now() - timedelta(days=90)
        if since_date < ninety_days_ago:
            raise ValueError("Date range cannot exceed 90 days")

        response = await self.http_client.get(
            f"/v3/brokerage/accounts/{account_ids}/historicalorders/{order_ids}",
            params={"since": since},
        )

        # Handle both direct response and response with data attribute (for tests)
        if hasattr(response, "data"):
            return HistoricalOrdersById.model_validate(response.data)
        else:
            return HistoricalOrdersById.model_validate(response)
