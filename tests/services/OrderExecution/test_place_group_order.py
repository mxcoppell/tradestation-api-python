import pytest
from src.ts_types.order_execution import (
    GroupOrderRequest,
    GroupOrderResponse,
    OrderType,
    OrderSide,
    TimeInForce,
    OrderDuration,
    OrderRequest,
)


class TestPlaceGroupOrder:
    """Tests for the place_group_order method in OrderExecutionService"""

    @pytest.mark.asyncio
    async def test_place_bracket_order(self, order_execution_service, http_client_mock):
        """Test placing a bracket order"""
        # Mock response data
        mock_response = {
            "Orders": [
                {"OrderID": "ORDER123", "Message": "Entry order placed successfully"},
                {"OrderID": "ORDER124", "Message": "Profit target order placed"},
                {"OrderID": "ORDER125", "Message": "Stop loss order placed"},
            ]
        }

        # Configure mock
        http_client_mock.post.return_value = mock_response

        # Create request
        request = GroupOrderRequest(
            Type="BRK",
            Orders=[
                OrderRequest(
                    AccountID="123456",
                    Symbol="MSFT",
                    Quantity="100",
                    OrderType=OrderType.MARKET,
                    TradeAction=OrderSide.BUY,
                    TimeInForce=TimeInForce(Duration=OrderDuration.DAY),
                    Route="Intelligent",
                ),
                OrderRequest(
                    AccountID="123456",
                    Symbol="MSFT",
                    Quantity="100",
                    OrderType=OrderType.LIMIT,
                    TradeAction=OrderSide.SELL,
                    TimeInForce=TimeInForce(Duration=OrderDuration.GTC),
                    Route="Intelligent",
                    LimitPrice="160",
                ),
                OrderRequest(
                    AccountID="123456",
                    Symbol="MSFT",
                    Quantity="100",
                    OrderType=OrderType.STOP_MARKET,
                    TradeAction=OrderSide.SELL,
                    TimeInForce=TimeInForce(Duration=OrderDuration.GTC),
                    Route="Intelligent",
                    StopPrice="145",
                ),
            ],
        )

        # Call the method
        result = await order_execution_service.place_group_order(request)

        # Verify the API was called correctly
        http_client_mock.post.assert_called_once_with(
            "/v3/orderexecution/ordergroups", request.model_dump(exclude_none=True)
        )

        # Verify the result
        assert isinstance(result, GroupOrderResponse)
        assert len(result.Orders) == 3
        assert result.Orders[0].OrderID == "ORDER123"
        assert result.Orders[0].Message == "Entry order placed successfully"
        assert result.Orders[1].OrderID == "ORDER124"
        assert result.Orders[1].Message == "Profit target order placed"
        assert result.Orders[2].OrderID == "ORDER125"
        assert result.Orders[2].Message == "Stop loss order placed"
        assert result.Errors is None

    @pytest.mark.asyncio
    async def test_place_oco_order(self, order_execution_service, http_client_mock):
        """Test placing an OCO order"""
        # Mock response data
        mock_response = {
            "Orders": [
                {"OrderID": "ORDER123", "Message": "Limit order placed"},
                {"OrderID": "ORDER124", "Message": "Stop order placed"},
            ]
        }

        # Configure mock
        http_client_mock.post.return_value = mock_response

        # Create request
        request = GroupOrderRequest(
            Type="OCO",
            Orders=[
                OrderRequest(
                    AccountID="123456",
                    Symbol="MSFT",
                    Quantity="100",
                    OrderType=OrderType.LIMIT,
                    TradeAction=OrderSide.SELL,
                    TimeInForce=TimeInForce(Duration=OrderDuration.GTC),
                    Route="Intelligent",
                    LimitPrice="160",
                ),
                OrderRequest(
                    AccountID="123456",
                    Symbol="MSFT",
                    Quantity="100",
                    OrderType=OrderType.STOP_MARKET,
                    TradeAction=OrderSide.SELL,
                    TimeInForce=TimeInForce(Duration=OrderDuration.GTC),
                    Route="Intelligent",
                    StopPrice="145",
                ),
            ],
        )

        # Call the method
        result = await order_execution_service.place_group_order(request)

        # Verify the API was called correctly
        http_client_mock.post.assert_called_once_with(
            "/v3/orderexecution/ordergroups", request.model_dump(exclude_none=True)
        )

        # Verify the result
        assert isinstance(result, GroupOrderResponse)
        assert len(result.Orders) == 2
        assert result.Orders[0].OrderID == "ORDER123"
        assert result.Orders[0].Message == "Limit order placed"
        assert result.Orders[1].OrderID == "ORDER124"
        assert result.Orders[1].Message == "Stop order placed"
        assert result.Errors is None

    @pytest.mark.asyncio
    async def test_place_group_order_validation_errors(
        self, order_execution_service, http_client_mock
    ):
        """Test validation errors when placing a group order"""
        # Mock response with errors
        mock_response = {
            "Orders": [],
            "Errors": [
                {
                    "OrderID": "ORDER123",
                    "Error": "INVALID_QUANTITY",
                    "Message": "Invalid order: Quantity must be greater than 0",
                }
            ],
        }

        # Configure mock
        http_client_mock.post.return_value = mock_response

        # Create request
        request = GroupOrderRequest(
            Type="BRK",
            Orders=[
                OrderRequest(
                    AccountID="123456",
                    Symbol="MSFT",
                    Quantity="-100",  # Invalid quantity
                    OrderType=OrderType.MARKET,
                    TradeAction=OrderSide.BUY,
                    TimeInForce=TimeInForce(Duration=OrderDuration.DAY),
                    Route="Intelligent",
                )
            ],
        )

        # Call the method
        result = await order_execution_service.place_group_order(request)

        # Verify the API was called correctly
        http_client_mock.post.assert_called_once_with(
            "/v3/orderexecution/ordergroups", request.model_dump(exclude_none=True)
        )

        # Verify the result
        assert isinstance(result, GroupOrderResponse)
        assert len(result.Orders) == 0
        assert len(result.Errors) == 1
        assert result.Errors[0].OrderID == "ORDER123"
        assert result.Errors[0].Error == "INVALID_QUANTITY"
        assert result.Errors[0].Message == "Invalid order: Quantity must be greater than 0"

    @pytest.mark.asyncio
    async def test_place_group_order_network_error(self, order_execution_service, http_client_mock):
        """Test network error handling when placing a group order"""
        # Configure mock to raise exception
        http_client_mock.post.side_effect = Exception("Network error")

        # Create request
        request = GroupOrderRequest(
            Type="BRK",
            Orders=[
                OrderRequest(
                    AccountID="123456",
                    Symbol="MSFT",
                    Quantity="100",
                    OrderType=OrderType.MARKET,
                    TradeAction=OrderSide.BUY,
                    TimeInForce=TimeInForce(Duration=OrderDuration.DAY),
                    Route="Intelligent",
                )
            ],
        )

        # Verify the exception is propagated
        with pytest.raises(Exception, match="Network error"):
            await order_execution_service.place_group_order(request)

        # Verify the API was called correctly
        http_client_mock.post.assert_called_once_with(
            "/v3/orderexecution/ordergroups", request.model_dump(exclude_none=True)
        )

    @pytest.mark.asyncio
    async def test_place_group_order_unauthorized(self, order_execution_service, http_client_mock):
        """Test unauthorized error handling when placing a group order"""
        # Configure mock to raise unauthorized exception
        http_client_mock.post.side_effect = Exception("Unauthorized")

        # Create request
        request = GroupOrderRequest(
            Type="BRK",
            Orders=[
                OrderRequest(
                    AccountID="123456",
                    Symbol="MSFT",
                    Quantity="100",
                    OrderType=OrderType.MARKET,
                    TradeAction=OrderSide.BUY,
                    TimeInForce=TimeInForce(Duration=OrderDuration.DAY),
                    Route="Intelligent",
                )
            ],
        )

        # Verify the exception is propagated
        with pytest.raises(Exception, match="Unauthorized"):
            await order_execution_service.place_group_order(request)

        # Verify the API was called correctly
        http_client_mock.post.assert_called_once_with(
            "/v3/orderexecution/ordergroups", request.model_dump(exclude_none=True)
        )
