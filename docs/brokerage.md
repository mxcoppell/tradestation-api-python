# Brokerage Service 💼

This service provides access to account information, balances, positions, and order history.

## Setup

First, ensure you have an initialized `TradeStationClient`:

```python
import asyncio
from dotenv import load_dotenv
from tradestation.client import TradeStationClient

# Load environment variables
load_dotenv()

# Create the client
client = TradeStationClient()

# Access the brokerage service
brokerage = client.brokerage

# --- Your code using brokerage methods goes here ---

# Remember to close the client when finished
async def main():
    # ... use brokerage methods ...
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Methods

### `get_accounts()`

Fetches brokerage account information for the authenticated user, including account types, status, and trading permissions.

*   **Parameters:** None
*   **Returns:** `List[Account]` containing detailed information for each accessible account.
*   **Example:** (See `examples/Brokerage/get_accounts.py`)
    ```python
    accounts = await brokerage.get_accounts()
    for account in accounts:
        print(f"Account ID: {account.AccountID}, Type: {account.AccountType}, Status: {account.Status}")
        if account.AccountDetail:
            print(f"  Option Level: {account.AccountDetail.OptionApprovalLevel}, PDT: {account.AccountDetail.PatternDayTrader}")
    ```

### `get_balances(account_ids)`

Fetches the current brokerage account balances for one or more specified accounts (up to 25).

*   **Parameters:**
    *   `account_ids` (`str`): A comma-separated string of account IDs (e.g., "123456,789012").
*   **Returns:** `Balances` object containing balance details for each requested account.
*   **Example:** (See `examples/Brokerage/get_balances.py`)
    ```python
    # First, get account IDs
    accounts_response = await brokerage.get_accounts()
    if not accounts_response:
        print("No accounts found.")
        # Handle error or exit
    account_id_list = [acc.AccountID for acc in accounts_response]
    account_ids_str = ",".join(account_id_list)

    balances_data = await brokerage.get_balances(account_ids_str)
    for balance in balances_data.Balances:
        print(f"Account {balance.AccountID}: Cash Balance=${balance.CashBalance}, Equity=${balance.Equity}, Buying Power=${balance.BuyingPower}")
    ```

### `get_balances_bod(account_ids)`

Fetches the beginning-of-day brokerage account balances for one or more specified accounts (up to 25).

*   **Parameters:**
    *   `account_ids` (`str`): A comma-separated string of account IDs.
*   **Returns:** `BalancesBOD` object containing beginning-of-day balance details.
*   **Example:** (See `examples/Brokerage/get_balances_bod.py`)
    ```python
    # (Get account_ids_str as shown in get_balances example)
    bod_balances = await brokerage.get_balances_bod(account_ids_str)
    for bod_balance in bod_balances.Balances:
        print(f"Account {bod_balance.AccountID} (BOD): Cash Balance=${bod_balance.BODCashBalance}, Equity=${bod_balance.BODEquity}")
    ```

### `get_positions(account_ids, symbol=None)`

Fetches current positions for one or more specified accounts (up to 25). Can optionally filter by symbol.

*   **Parameters:**
    *   `account_ids` (`str`): A comma-separated string of account IDs.
    *   `symbol` (`Optional[str]`): Optional symbol to filter positions.
*   **Returns:** `Positions` object containing position details for each requested account.
*   **Example:** (See `examples/Brokerage/get_positions.py`)
    ```python
    # (Get account_ids_str as shown in get_balances example)
    positions_data = await brokerage.get_positions(account_ids_str)
    print("Positions:")
    for position in positions_data.Positions:
        print(f"- Account {position.AccountID}: {position.Quantity} {position.Symbol} @ Avg Price {position.AveragePrice}, P/L: {position.UnrealizedProfitLoss}")

    # Filter by symbol
    # aapl_positions = await brokerage.get_positions(account_ids_str, symbol="AAPL")
    ```

### `get_orders(account_ids, page_size=None, next_token=None)`

Fetches *currently open* orders for the specified accounts (up to 25). Use `get_historical_orders` for filled/cancelled orders.

*   **Parameters:**
    *   `account_ids` (`str`): A comma-separated string of account IDs.
    *   `page_size` (`Optional[int]`): Number of orders per page (default/max 500).
    *   `next_token` (`Optional[str]`): Token from previous response for pagination.
*   **Returns:** `Orders` object containing the list of open orders and a `NextToken` if more pages exist.
*   **Example:** (See `examples/Brokerage/get_orders.py`)
    ```python
    # (Get account_ids_str as shown in get_balances example)
    open_orders = await brokerage.get_orders(account_ids_str)
    print("Open Orders:")
    if open_orders.Orders:
        for order in open_orders.Orders:
            print(f"- ID: {order.OrderID}, Symbol: {order.Legs[0].Symbol}, Action: {order.Legs[0].BuyOrSell}, Qty: {order.Legs[0].QuantityOrdered}, Type: {order.OrderType}, Status: {order.Status}")
    else:
        print("No open orders found.")
    # Handle pagination using open_orders.NextToken if needed
    ```

### `get_orders_by_order_id(account_ids, order_ids)`

Fetches specific *currently open* orders by their IDs for the specified accounts.

*   **Parameters:**
    *   `account_ids` (`str`): A comma-separated string of account IDs (1-25).
    *   `order_ids` (`str`): A comma-separated string of order IDs (1-50). Do not include dashes (e.g., "123456789").
*   **Returns:** `OrdersById` object containing the details of the requested open orders.
*   **Example:** (See `examples/Brokerage/get_order_by_id.py`)
    ```python
    # Assume open_order_id holds an ID from a previous get_orders() call
    # (Get account_ids_str as shown in get_balances example)
    # if open_order_id:
    #     order_detail = await brokerage.get_orders_by_order_id(account_ids_str, open_order_id)
    #     if order_detail.Orders:
    #         print(f"Details for Order {open_order_id}: {order_detail.Orders[0]}")
    #     else:
    #         print(f"Could not find open order {open_order_id}")
    ```

### `get_historical_orders(account_ids, since, page_size=None, next_token=None)`

Fetches historical (filled, cancelled, rejected) orders for the specified accounts (up to 25) within the last 90 days.

*   **Parameters:**
    *   `account_ids` (`str`): A comma-separated string of account IDs.
    *   `since` (`str`): Start date for fetching orders (YYYY-MM-DD or other supported formats). Max 90 days ago.
    *   `page_size` (`Optional[int]`): Number of orders per page (default/max 500).
    *   `next_token` (`Optional[str]`): Token from previous response for pagination.
*   **Returns:** `HistoricalOrders` object containing historical orders and a `NextToken`.
*   **Example:** (See `examples/Brokerage/get_historical_orders.py`)
    ```python
    from datetime import datetime, timedelta
    # (Get account_ids_str as shown in get_balances example)
    ninety_days_ago = (datetime.now() - timedelta(days=89)).strftime("%Y-%m-%d")

    hist_orders = await brokerage.get_historical_orders(account_ids_str, since=ninety_days_ago)
    print(f"Historical Orders since {ninety_days_ago}:")
    if hist_orders.Orders:
        for order in hist_orders.Orders:
             print(f"- ID: {order.OrderID}, Symbol: {order.Legs[0].Symbol}, Status: {order.Status}, Closed: {order.ClosedDateTime}")
    else:
        print("No historical orders found in the last 90 days.")
    # Handle pagination using hist_orders.NextToken if needed
    ```

### `get_historical_orders_by_order_id(account_ids, order_ids, since)`

Fetches specific historical orders by their IDs for the specified accounts within the last 90 days.

*   **Parameters:**
    *   `account_ids` (`str`): A comma-separated string of account IDs (1-25).
    *   `order_ids` (`str`): A comma-separated string of order IDs (1-50). Do not include dashes.
    *   `since` (`str`): Start date (max 90 days ago).
*   **Returns:** `HistoricalOrdersById` object containing details of the requested historical orders.
*   **Example:** (See `examples/Brokerage/get_historical_orders_by_order_id.py`)
    ```python
    # Assume closed_order_id holds an ID from a previous historical order
    # (Get account_ids_str as shown in get_balances example)
    # ninety_days_ago = (datetime.now() - timedelta(days=89)).strftime("%Y-%m-%d")
    # if closed_order_id:
    #    hist_order_detail = await brokerage.get_historical_orders_by_order_id(
    #        account_ids_str, closed_order_id, since=ninety_days_ago
    #    )
    #    if hist_order_detail.Orders:
    #        print(f"Details for Historical Order {closed_order_id}: {hist_order_detail.Orders[0]}")
    #    else:
    #        print(f"Could not find historical order {closed_order_id}")
    ```

---

## Streaming Methods

These methods provide real-time updates for orders and positions via Server-Sent Events (SSE). Use the general streaming example from `market_data.md` as a template for processing the `aiohttp.StreamReader`.

### `stream_orders(account_ids)`

Streams real-time updates for *all orders* (open, filled, cancelled, etc.) across the specified accounts.

*   **Parameters:**
    *   `account_ids` (`str`): Comma-separated string of account IDs (1-25).
*   **Returns:** `aiohttp.StreamReader` yielding JSON data for `OrderStream`, `Heartbeat`, or `StreamErrorResponse`.
*   **Example:** (See `examples/Brokerage/stream_orders.py`)

### `stream_orders_by_order_id(account_ids, order_ids)`

Streams real-time updates for *specific orders* identified by their IDs across the specified accounts.

*   **Parameters:**
    *   `account_ids` (`str`): Comma-separated string of account IDs (1-25).
    *   `order_ids` (`str`): Comma-separated string of order IDs (1-50). Do not include dashes.
*   **Returns:** `aiohttp.StreamReader` yielding JSON data for `OrderStream`, `Heartbeat`, or `StreamErrorResponse`.
*   **Example:** (See `examples/Brokerage/stream_orders.py` - Adapt symbol list for specific IDs)

### `stream_positions(account_ids, changes=False)`

Streams real-time position updates for the specified accounts.

*   **Parameters:**
    *   `account_ids` (`str`): Comma-separated string of account IDs (1-25).
    *   `changes` (`bool`): If `True`, streams only *changes* to positions. If `False` (default), streams the full position data periodically.
*   **Returns:** `aiohttp.StreamReader` yielding JSON data for `PositionStream`, `Heartbeat`, or `StreamErrorResponse`.
*   **Example:** (See `examples/Brokerage/stream_positions.py`) 