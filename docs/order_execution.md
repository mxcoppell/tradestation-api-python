# Order Execution Service 📈

This service allows you to place, modify, cancel, and confirm orders for various asset types.

## Setup

First, ensure you have an initialized `TradeStationClient`:

```python
import asyncio
from dotenv import load_dotenv
from tradestation.client import TradeStationClient
from tradestation.ts_types.order_execution import OrderRequest, OrderReplaceRequest, GroupOrderRequest # etc.

# Load environment variables
load_dotenv()

# Create the client
client = TradeStationClient()

# Access the order execution service
order_execution = client.order_execution

# --- Your code using order_execution methods goes here ---

# Remember to close the client when finished
async def main():
    # --- Get account ID first ---
    accounts = await client.brokerage.get_accounts()
    if not accounts:
        print("No accounts found. Cannot proceed.")
        await client.close()
        return
    # Use the first available account ID for examples
    account_id = accounts[0].AccountID
    print(f"Using Account ID: {account_id}")

    # --- Place order example ---
    # try:
    #     market_order = OrderRequest(
    #         AccountID=account_id,
    #         Symbol="F",
    #         Quantity="1",
    #         OrderType="Market",
    #         TradeAction="BUY",
    #         TimeInForce={"Duration": "DAY"},
    #         Route="Intelligent"
    #     )
    #     order_response = await order_execution.place_order(market_order)
    #     print(f"Order placed: {order_response}")
    # except Exception as e:
    #     print(f"Error placing order: {e}")

    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

**Note:** Many examples require an `AccountID`. You can retrieve this using the `BrokerageService.get_accounts()` method.

---

## Methods

### `place_order(request)`

Places a single order (Market, Limit, Stop Market, Stop Limit).

*   **Parameters:**
    *   `request` (`OrderRequest`): An `OrderRequest` object containing all necessary order parameters (AccountID, Symbol, Quantity, OrderType, TradeAction, TimeInForce, Route, etc.).
*   **Returns:** `OrderResponse` containing the OrderID and status.
*   **Example:** (See `examples/OrderExecution/place_and_cancel_order.py`)
    ```python
    # (Requires account_id)
    market_order = OrderRequest(
        AccountID=account_id,
        Symbol="F", # Example symbol
        Quantity="1",
        OrderType="Market",
        TradeAction="BUY",
        TimeInForce={"Duration": "DAY"},
        Route="Intelligent"
    )
    try:
        order_response = await order_execution.place_order(market_order)
        print(f"Market Order Response: {order_response}")
        # Store order_response.Orders[0].OrderID for cancellation/replacement
    except Exception as e:
        print(f"Error placing order: {e}")
    ```

### `replace_order(order_id, request)`

Replaces an existing, open order with new parameters.

*   **Parameters:**
    *   `order_id` (`str`): The ID of the order to replace (without dashes).
    *   `request` (`OrderReplaceRequest`): An `OrderReplaceRequest` object containing the modified order parameters (e.g., new Quantity, LimitPrice).
*   **Returns:** `ReplaceOrderResponse` containing the new OrderID and status.
*   **Example:** (See `examples/OrderExecution/place_replace_cancel_order.py`)
    ```python
    # Assume limit_order_id is the ID of an existing open limit order
    # (Requires account_id)
    replace_request = OrderReplaceRequest(
        AccountID=account_id,
        Symbol="MSFT", # Must match original order
        Quantity="15", # New quantity
        OrderType="Limit", # Must match original order
        LimitPrice="295.00", # New limit price
        TradeAction="BUY", # Must match original order
        TimeInForce={"Duration": "GTC"},
        Route="Intelligent"
    )
    try:
        replace_response = await order_execution.replace_order(limit_order_id, replace_request)
        print(f"Replace Order Response: {replace_response}")
    except Exception as e:
        print(f"Error replacing order {limit_order_id}: {e}")
    ```

### `confirm_order(request)`

Creates an Order Confirmation *without* placing the order. Returns estimated cost and commission.

*   **Parameters:**
    *   `request` (`OrderRequest`): The order request details to confirm.
*   **Returns:** `GroupOrderConfirmationResponse` containing estimated cost and commission.
*   **Example:** (See `examples/OrderExecution/confirm_order.py`)
    ```python
    # (Requires account_id)
    order_to_confirm = OrderRequest(
        AccountID=account_id,
        Symbol="AAPL",
        Quantity="10",
        OrderType="Limit",
        LimitPrice="180.00",
        TradeAction="BUY",
        TimeInForce={"Duration": "DAY"},
        Route="Intelligent"
    )
    try:
        confirmation = await order_execution.confirm_order(order_to_confirm)
        print("Order Confirmation Details:")
        if confirmation.Confirmations:
            conf = confirmation.Confirmations[0]
            print(f"- Estimated Cost: {conf.EstimatedCost}")
            print(f"- Commission: {conf.CommissionFee}")
            print(f"- Buying Power Effect: {conf.BuyingPowerEffect}")
        else:
            print("Could not get confirmation details.")
    except Exception as e:
        print(f"Error confirming order: {e}")
    ```

### `cancel_order(order_id)`

Sends a cancellation request for an open order.

*   **Parameters:**
    *   `order_id` (`str`): The ID of the order to cancel (without dashes).
*   **Returns:** `CancelOrderResponse` containing the OrderID and cancellation status.
*   **Example:** (See `examples/OrderExecution/place_and_cancel_order.py`)
    ```python
    # Assume market_order_id contains the ID from a placed order
    # if market_order_id:
    #     try:
    #         # Allow time for order to potentially reach exchange
    #         await asyncio.sleep(2)
    #         cancel_response = await order_execution.cancel_order(market_order_id)
    #         print(f"Cancel Order Response: {cancel_response}")
    #     except Exception as e:
    #         print(f"Error cancelling order {market_order_id}: {e}")
    ```

### `confirm_group_order(request)`

Creates an Order Confirmation for a group order (OCO or Bracket) *without* placing it. Returns estimated costs for each order in the group.

*   **Parameters:**
    *   `request` (`GroupOrderRequest`): A `GroupOrderRequest` object containing the `Type` ("OCO" or "BRK") and a list of `Orders` (each an `OrderRequest`).
*   **Returns:** `GroupOrderConfirmationResponse` containing confirmations for each order in the group.
*   **Example:** (See `examples/OrderExecution/confirm_group_order.py`)
    ```python
    # (Requires account_id)
    oco_order1 = OrderRequest(...)
    oco_order2 = OrderRequest(...)
    group_request = GroupOrderRequest(
        Type="OCO",
        Orders=[oco_order1, oco_order2]
    )
    try:
        group_confirmation = await order_execution.confirm_group_order(group_request)
        print("Group Order Confirmation Details:")
        for conf in group_confirmation.Confirmations:
            print(f"- Order Est Cost: {conf.EstimatedCost}, Commission: {conf.CommissionFee}")
    except Exception as e:
        print(f"Error confirming group order: {e}")
    ```

### `place_group_order(request)`

Places a group order (OCO or Bracket).

*   **Parameters:**
    *   `request` (`GroupOrderRequest`): The group order request containing `Type` and `Orders`.
*   **Returns:** `GroupOrderResponse` containing responses for each individual order placed within the group.
*   **Example:** (See `examples/OrderExecution/place_and_cancel_group_order.py`)
    ```python
    # (Requires account_id)
    # Build bracket_order_entry, bracket_order_profit, bracket_order_stoploss as OrderRequest objects
    bracket_request = GroupOrderRequest(
        Type="BRK",
        Orders=[bracket_order_entry, bracket_order_profit, bracket_order_stoploss]
    )
    try:
        group_response = await order_execution.place_group_order(bracket_request)
        print("Place Group Order Response:")
        for order_resp in group_response.Orders:
            print(f"- OrderID: {order_resp.OrderID}, Status: {order_resp.Status}")
        # Store order IDs if needed for cancellation
    except Exception as e:
        print(f"Error placing group order: {e}")
    ```

### `get_routes()`

Returns a list of valid routes that can be specified when placing an order.

*   **Parameters:** None
*   **Returns:** `Routes` object containing a list of available routes.
*   **Example:** (See `examples/OrderExecution/get_routes.py`)
    ```python
    routes_response = await order_execution.get_routes()
    print("Available Routes:")
    for route in routes_response.Routes:
        print(f"- ID: {route.Id}, Name: {route.Name}, AssetTypes: {route.AssetTypes}")
    ```

### `get_activation_triggers()`

Gets a list of activation triggers that can be used when placing advanced orders (e.g., conditional orders).

*   **Parameters:** None
*   **Returns:** `ActivationTriggers` object containing a list of available triggers.
*   **Example:** (See `examples/OrderExecution/get_activation_triggers.py`)
    ```python
    triggers_response = await order_execution.get_activation_triggers()
    print("Available Activation Triggers:")
    for trigger in triggers_response.ActivationTriggers:
        print(f"- Name: {trigger.Name}, DisplayName: {trigger.DisplayName}")
    ```

---

**Important Considerations:**

*   **Order IDs:** When cancelling or replacing orders, ensure you provide the `OrderID` *without* any dashes.
*   **Group Orders:** Bracket orders placed via `place_group_order` cannot be updated as a single transaction; each leg must be replaced individually using `replace_order`.
*   **Error Handling:** Always wrap API calls in `try...except` blocks to handle potential API errors (e.g., invalid parameters, rate limits, non-cancellable orders).
*   **Account ID:** Most methods require a valid `AccountID`. Retrieve this using `BrokerageService.get_accounts()`. 