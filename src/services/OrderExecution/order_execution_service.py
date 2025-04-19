from typing import Any, Dict, List, Optional, Union

from ...client.http_client import HttpClient
from ...streaming.stream_manager import StreamManager
from ...ts_types.order_execution import (
    CancelOrderResponse,
    ActivationTriggers,
    Routes,
    GroupOrderRequest,
    GroupOrderConfirmationResponse,
    OrderRequest,
    OrderConfirmationResponse,
)


class OrderExecutionService:
    """
    Service for executing orders through the TradeStation API

    This is a placeholder until the full implementation in a separate task.
    """

    def __init__(self, http_client: HttpClient, stream_manager: StreamManager):
        """
        Creates a new OrderExecutionService

        Args:
            http_client: The HttpClient to use for API requests
            stream_manager: The StreamManager to use for streaming
        """
        self.http_client = http_client
        self.stream_manager = stream_manager

    async def confirm_order(self, request: OrderRequest) -> OrderConfirmationResponse:
        """
        Creates an Order Confirmation without actually placing it.
        Returns estimated cost and commission information.

        Args:
            request: The order request to confirm

        Returns:
            Estimated cost and commission information for the order

        Raises:
            Exception: Will raise an error if:
                - The request is invalid (400)
                - The request is unauthorized (401)
                - The request is forbidden (403)
                - Rate limit is exceeded (429)
                - Service is unavailable (503)
                - Gateway timeout (504)
        """
        response = await self.http_client.post(
            "/v3/orderexecution/orderconfirm", request.model_dump(exclude_none=True)
        )
        return OrderConfirmationResponse(**response)

    async def cancel_order(self, order_id: str) -> CancelOrderResponse:
        """
        Sends a cancellation request to the relevant exchange.
        Valid for all account types.

        Args:
            order_id: Order ID for cancellation request. Equity, option or future orderIDs should not include dashes.
                     Example: Use "123456789" instead of "1-2345-6789"

        Returns:
            A promise that resolves to the cancel order response containing order ID and status

        Raises:
            Exception: Will raise an error if:
                - The order doesn't exist (404)
                - The order cannot be cancelled (400)
                - The request is unauthorized (401)
                - The request is forbidden (403)
                - Rate limit is exceeded (429)
                - Service is unavailable (503)
                - Gateway timeout (504)
        """
        response = await self.http_client.delete(f"/v3/orderexecution/orders/{order_id}")
        return CancelOrderResponse(**response)

    async def confirm_group_order(
        self, request: GroupOrderRequest
    ) -> GroupOrderConfirmationResponse:
        """
        Creates an Order Confirmation for a group order without actually placing it.
        Returns estimated cost and commission information for each order in the group.

        Valid for all account types and the following group types:
        - OCO (Order Cancels Order): If one order is filled/partially-filled, all others are cancelled
        - BRK (Bracket): Used to exit positions, combining stop and limit orders

        Note: When a group order is submitted, each sibling order is treated as individual.
        The system does not validate that each order has the same Quantity, and
        bracket orders cannot be updated as one transaction (must update each order separately).

        Args:
            request: The group order request containing type and array of orders

        Returns:
            Array of estimated cost and commission information for each order

        Raises:
            Exception: Will raise an error if:
                - The request is invalid (400)
                - The request is unauthorized (401)
                - The request is forbidden (403)
                - Rate limit is exceeded (429)
                - Service is unavailable (503)
                - Gateway timeout (504)
        """
        response = await self.http_client.post(
            "/v3/orderexecution/ordergroupconfirm", request.model_dump(exclude_none=True)
        )
        return GroupOrderConfirmationResponse(**response)

    async def get_routes(self) -> Routes:
        """
        Returns a list of valid routes that a client can specify when posting an order.
        Routes are used to specify where an order should be sent for execution.

        For Stocks and Options, if no route is specified in the order request,
        the route will default to 'Intelligent'.

        Returns:
            A promise that resolves to an object containing an array of available routes

        Raises:
            Exception: Will raise an error if:
                - The request is unauthorized (401)
                - The request is forbidden (403)
                - Bad request (400)

        Example:
            # Get available routes
            routes = await service.get_routes()
            print(routes.Routes)
            # Example output:
            # [
            #   {
            #     "Id": "AMEX",
            #     "AssetTypes": ["STOCK"],
            #     "Name": "AMEX"
            #   },
            #   {
            #     "Id": "ARCA",
            #     "AssetTypes": ["STOCK"],
            #     "Name": "ARCX"
            #   }
            # ]
        """
        response = await self.http_client.get("/v3/orderexecution/routes")
        return Routes(**response)
