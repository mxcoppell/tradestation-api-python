from typing import Any, Dict, List, Optional, Union

from ...client.http_client import HttpClient
from ...streaming.stream_manager import StreamManager
from ...ts_types.brokerage import (
    HistoricalOrdersById,
    Account,
    AccountDetail,
    Balances,
    BalancesBOD,
    HistoricalOrders,
    Orders,
)


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

    async def get_balances(self, account_ids: str) -> Balances:
        """
        Fetches the brokerage account Balances for one or more given accounts.
        Request valid for Cash, Margin, Futures, and DVP account types.

        Args:
            account_ids: List of valid Account IDs in comma separated format (e.g. "61999124,68910124").
                        1 to 25 Account IDs can be specified. Recommended batch size is 10.

        Returns:
            A Balances object containing:
            - Balances: Array of balance information for each account, including:
                - AccountID: Unique identifier for the account
                - AccountType: Type of account (Cash, Margin, Futures, DVP)
                - BuyingPower: Available buying power
                - CashBalance: Current cash balance
                - Commission: Total commissions
                - Equity: Total account equity
                - MarketValue: Total market value of positions
                - TodaysProfitLoss: Profit/loss for the current day
                - UnclearedDeposit: Amount of uncleared deposits
                - BalanceDetail: Additional balance details including:
                  - CostOfPositions: Total cost basis of positions
                  - DayTradeExcess: Excess day trading buying power
                  - DayTradeMargin: Day trading margin requirement
                  - DayTradeOpenOrderMargin: Open order margin for day trades
                  - DayTrades: Number of day trades
                  - InitialMargin: Initial margin requirement
                  - MaintenanceMargin: Maintenance margin requirement
                  - MaintenanceRate: Maintenance margin rate
                  - MarginRequirement: Total margin requirement
                  - UnrealizedProfitLoss: Unrealized P/L
                  - UnsettledFunds: Amount of unsettled funds
                - CurrencyDetails: Array of currency-specific details (for Futures accounts):
                  - Currency: Currency code (e.g., USD)
                  - BODOpenTradeEquity: Beginning of day open trade equity
                  - CashBalance: Cash balance in this currency
                  - Commission: Commissions in this currency
                  - MarginRequirement: Margin requirement in this currency
                  - NonTradeDebit: Non-trade related debits
                  - NonTradeNetBalance: Net balance of non-trade activity
                  - OptionValue: Value of options
                  - RealTimeUnrealizedGains: Real-time unrealized gains/losses
                  - TodayRealTimeTradeEquity: Today's real-time trade equity
                  - TradeEquity: Total trade equity
            - Errors: Optional array of errors that occurred, each containing:
                - AccountID: ID of the account that had an error
                - Error: Error code
                - Message: Detailed error message

        Raises:
            Exception: If the request fails due to network issues or API errors

        Example:
            ```python
            # Get balances for a single account
            single_balance = await brokerage_service.get_balances("123456789")
            print(single_balance.Balances[0].CashBalance)

            # Get balances for multiple accounts
            multi_balances = await brokerage_service.get_balances("123456789,987654321")
            for balance in multi_balances.Balances:
                print(f"Account {balance.AccountID}: Cash Balance = {balance.CashBalance}")
            ```
        """
        response = await self.http_client.get(f"/v3/brokerage/accounts/{account_ids}/balances")

        # Handle response.data vs direct response for tests
        data = response.data if hasattr(response, "data") else response

        # Process response data to model
        balances_list = []
        for balance_data in data["Balances"]:
            # Process BalanceDetail separately
            balance_detail = None
            if "BalanceDetail" in balance_data and balance_data["BalanceDetail"]:
                from ...ts_types.brokerage import BalanceDetail

                balance_detail = BalanceDetail.model_validate(balance_data["BalanceDetail"])
                del balance_data["BalanceDetail"]

            # Process CurrencyDetails separately if needed
            currency_details = None
            if "CurrencyDetails" in balance_data and balance_data["CurrencyDetails"]:
                from ...ts_types.brokerage import CurrencyDetail

                currency_details = [
                    CurrencyDetail.model_validate(currency_detail)
                    for currency_detail in balance_data["CurrencyDetails"]
                ]
                del balance_data["CurrencyDetails"]

            # Create the Balance object
            from ...ts_types.brokerage import Balance

            balance = Balance.model_validate(balance_data)

            # Add back the processed fields
            balance.BalanceDetail = balance_detail
            balance.CurrencyDetails = currency_details

            balances_list.append(balance)

        # Create the Balances object
        from ...ts_types.brokerage import Balances

        result = Balances(Balances=balances_list)

        # Add errors if present
        if "Errors" in data and data["Errors"]:
            from ...ts_types.brokerage import BalanceError

            result.Errors = [BalanceError.model_validate(error) for error in data["Errors"]]

        return result

    async def get_balances_bod(self, account_ids: str) -> BalancesBOD:
        """
        Fetches the Beginning of Day Balances for the given Accounts.
        Request valid for Cash, Margin, Futures, and DVP account types.

        Beginning of Day (BOD) balances represent the account balances at market open,
        providing a baseline for tracking intraday changes. This is particularly useful for:
        - Calculating intraday P/L
        - Monitoring trading activity impact
        - Determining day trading buying power
        - Analyzing overnight position impact

        Args:
            account_ids: List of valid Account IDs in comma separated format (e.g. "61999124,68910124").
                        1 to 25 Account IDs can be specified. Recommended batch size is 10.

        Returns:
            A BalancesBOD object containing:
            - BODBalances: Array of beginning of day balance information for each account, including:
                - AccountID: Unique identifier for the account
                - AccountType: Type of account (Cash, Margin, Futures, DVP)
                - BalanceDetail: Additional balance details including:
                  - AccountBalance: Total account balance at market open
                  - CashAvailableToWithdraw: Amount available for withdrawal
                  - DayTrades: Number of day trades at market open
                  - DayTradingMarginableBuyingPower: Available day trading buying power
                  - Equity: Total account equity at market open
                  - NetCash: Net cash balance
                  - OptionBuyingPower: Available buying power for options
                  - OptionValue: Total value of option positions
                  - OvernightBuyingPower: Available buying power for overnight positions
                - CurrencyDetails: Array of currency-specific details (for Futures accounts):
                  - Currency: Currency code (e.g., USD)
                  - AccountMarginRequirement: Margin requirement for the account
                  - AccountOpenTradeEquity: Open trade equity at market open
                  - AccountSecurities: Value of securities in the account
                  - CashBalance: Cash balance in this currency
                  - MarginRequirement: Margin requirement in this currency
            - Errors: Optional array of errors that occurred, each containing:
                - AccountID: ID of the account that had an error
                - Error: Error code
                - Message: Detailed error message

        Raises:
            Exception: If the request fails due to network issues or API errors

        Example:
            ```python
            # Get BOD balances for a single account
            single_bod = await brokerage_service.get_balances_bod("123456789")
            print(single_bod.BODBalances[0].BalanceDetail.AccountBalance)

            # Get BOD balances for multiple accounts
            multi_bod = await brokerage_service.get_balances_bod("123456789,987654321")
            for balance in multi_bod.BODBalances:
                print(f"Account {balance.AccountID}:")
                print(f"  Equity: {balance.BalanceDetail.Equity}")
                print(f"  Net Cash: {balance.BalanceDetail.NetCash}")
            ```
        """
        response = await self.http_client.get(f"/v3/brokerage/accounts/{account_ids}/bodbalances")

        # Handle both direct response and response with data attribute (for tests)
        if hasattr(response, "data"):
            return BalancesBOD.model_validate(response.data)
        else:
            return BalancesBOD.model_validate(response)

    async def get_historical_orders(
        self,
        account_ids: str,
        since: str,
        page_size: Optional[int] = None,
        next_token: Optional[str] = None,
        test_mode: bool = False,
    ) -> HistoricalOrders:
        """
        Fetches Historical Orders for the given Accounts except open orders, sorted in descending order of time closed.
        Request valid for all account types.

        This endpoint provides historical order information including:
        - Order details (ID, type, status, timestamps)
        - Execution details (filled quantity, execution price)
        - Order legs for complex orders (spreads, multi-leg orders)
        - Order routing and venue information

        Args:
            account_ids: List of valid Account IDs in comma separated format (e.g. "61999124,68910124").
                        1 to 25 Account IDs can be specified. Recommended batch size is 10.
            since: Historical orders since date (e.g. "2006-01-13", "01-13-2006", "2006/01/13", "01/13/2006").
                   Limited to 90 days prior to the current date.
            page_size: Optional. The number of requests returned per page when paginating responses.
                      If not provided, results will not be paginated and a maximum of 600 orders is returned.
                      Must be between 1 and 600.
            next_token: Optional. An encrypted token for paginated results to retrieve the next page.
                       This is returned with paginated results and has a lifetime of 1 hour.
            test_mode: Optional. Set to True to bypass date validation for testing purposes.

        Returns:
            A HistoricalOrders object containing:
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
            - NextToken: Optional token for retrieving the next page of results
            - Errors: Optional array of errors that occurred, each containing:
                - AccountID: ID of the account that had an error
                - Error: Error code
                - Message: Detailed error message

        Raises:
            ValueError: If more than 25 account IDs are specified
            ValueError: If the date range exceeds 90 days
            ValueError: If pageSize is outside the valid range (1-600)
            Exception: If the request fails due to network issues or API errors

        Example:
            ```python
            # Get historical orders for a single account
            orders = await brokerage_service.get_historical_orders(
                "123456789",
                "2024-01-01"
            )

            # Get historical orders for multiple accounts with pagination
            paginated_orders = await brokerage_service.get_historical_orders(
                "123456789,987654321",
                "2024-01-01",
                100
            )

            # Get next page using the nextToken
            if paginated_orders.NextToken:
                next_page = await brokerage_service.get_historical_orders(
                    "123456789,987654321",
                    "2024-01-01",
                    100,
                    paginated_orders.NextToken
                )
            ```
        """
        # Validate maximum accounts
        if len(account_ids.split(",")) > 25:
            raise ValueError("Maximum of 25 accounts allowed per request")

        # Validate date range (skip in test mode)
        if not test_mode:
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

        # Validate pageSize
        if page_size is not None and (page_size < 1 or page_size > 600):
            raise ValueError("Page size must be between 1 and 600")

        params = {"since": since}
        if page_size is not None:
            params["pageSize"] = page_size
        if next_token is not None:
            params["nextToken"] = next_token

        response = await self.http_client.get(
            f"/v3/brokerage/accounts/{account_ids}/historicalorders", params=params
        )

        # Handle both direct response and response with data attribute (for tests)
        if hasattr(response, "data"):
            return HistoricalOrders.model_validate(response.data)
        else:
            return HistoricalOrders.model_validate(response)

    async def get_orders(
        self,
        account_ids: str,
        page_size: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> "Orders":
        """
        Fetches today's orders and open orders for the given Accounts, sorted in descending order of time placed for open and time executed for closed.
        Request valid for all account types.

        Args:
            account_ids: List of valid Account IDs in comma separated format (e.g. "61999124,68910124").
                        1 to 25 Account IDs can be specified. Recommended batch size is 10.
            page_size: Optional. The number of requests returned per page when paginating responses.
                      If not provided, results will not be paginated and a maximum of 600 orders is returned.
                      Must be between 1 and 600.
            next_token: Optional. An encrypted token with a lifetime of 1 hour for use with paginated order responses.
                       This is returned with paginated results and used in only the subsequent request which will return
                       a new nextToken until there are fewer returned orders than the requested pageSize.

        Returns:
            An Orders object containing:
            - Orders: Array of order information, each containing:
                - AccountID: Account that placed the order
                - OrderID: Unique identifier for the order
                - Status: Current status of the order (e.g., "OPN", "FLL", "FPR")
                - StatusDescription: Detailed status description (e.g., "Sent", "Filled", "Partial Fill (Alive)")
                - OrderType: Type of order (Market, Limit, etc.)
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
                - LimitPrice: Limit price for limit orders
                - StopPrice: Stop price for stop orders
            - NextToken: Optional token for retrieving the next page of results
            - Errors: Optional array of errors that occurred, each containing:
                - AccountID: ID of the account that had an error
                - Error: Error code
                - Message: Detailed error message

        Raises:
            ValueError: If more than 25 account IDs are specified
            ValueError: If pageSize is outside the valid range (1-600)
            Exception: If the request fails due to network issues or API errors

        Example:
            ```python
            # Get orders for a single account
            orders = await brokerage_service.get_orders("123456789")

            # Get orders for multiple accounts with pagination
            paginated_orders = await brokerage_service.get_orders(
                "123456789,987654321",
                100
            )

            # Get next page using the nextToken
            if paginated_orders.NextToken:
                next_page = await brokerage_service.get_orders(
                    "123456789,987654321",
                    100,
                    paginated_orders.NextToken
                )
            ```
        """
        # Validate maximum accounts
        if len(account_ids.split(",")) > 25:
            raise ValueError("Maximum of 25 accounts allowed per request")

        # Validate pageSize
        if page_size is not None and (page_size < 1 or page_size > 600):
            raise ValueError("Page size must be between 1 and 600")

        params = {}
        if page_size is not None:
            params["pageSize"] = page_size
        if next_token is not None:
            params["nextToken"] = next_token

        response = await self.http_client.get(
            f"/v3/brokerage/accounts/{account_ids}/orders", params=params
        )

        # Handle both direct response and response with data attribute (for tests)
        if hasattr(response, "data"):
            from ...ts_types.brokerage import Orders

            return Orders.model_validate(response.data)
        else:
            from ...ts_types.brokerage import Orders

            return Orders.model_validate(response)
