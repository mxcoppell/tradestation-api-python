import pytest

from tradestation.ts_types.order_execution import (
    GroupOrderConfirmationResponse,
    GroupOrderRequest,
    OrderDuration,
    OrderRequest,
    OrderSide,
    OrderType,
    TimeInForce,
)


class TestConfirmGroupOrder:
    """Tests for the confirm_group_order method in OrderExecutionService"""

    @pytest.mark.asyncio
    async def test_confirm_bracket_order(self, order_execution_service, http_client_mock):
        """Test confirmation of a bracket order"""
        # Mock response data - Use "Confirmations" key
        mock_response = {
            "Confirmations": [
                {"OrderID": "ORDER123", "Message": "Order confirmed"},
                {"OrderID": "ORDER124", "Message": "Order confirmed"},
                {"OrderID": "ORDER125", "Message": "Order confirmed"},
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
        result = await order_execution_service.confirm_group_order(request)

        # Verify the API was called correctly
        http_client_mock.post.assert_called_once_with(
            "/v3/orderexecution/ordergroupconfirm", request.model_dump(exclude_none=True)
        )

        # Verify the result - Access "Confirmations" field
        assert isinstance(result, GroupOrderConfirmationResponse)
        assert len(result.Confirmations) == 3
        assert result.Confirmations[0].OrderID == "ORDER123"
        assert result.Confirmations[0].Message == "Order confirmed"
        assert result.Confirmations[1].OrderID == "ORDER124"
        assert result.Confirmations[1].Message == "Order confirmed"
        assert result.Confirmations[2].OrderID == "ORDER125"
        assert result.Confirmations[2].Message == "Order confirmed"
        assert result.Errors is None

    @pytest.mark.asyncio
    async def test_confirm_oco_order(self, order_execution_service, http_client_mock):
        """Test confirmation of an OCO order"""
        # Mock response data - Use "Confirmations" key
        mock_response = {
            "Confirmations": [
                {"OrderID": "ORDER123", "Message": "Order confirmed"},
                {"OrderID": "ORDER124", "Message": "Order confirmed"},
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
        result = await order_execution_service.confirm_group_order(request)

        # Verify the API was called correctly
        http_client_mock.post.assert_called_once_with(
            "/v3/orderexecution/ordergroupconfirm", request.model_dump(exclude_none=True)
        )

        # Verify the result - Access "Confirmations" field
        assert isinstance(result, GroupOrderConfirmationResponse)
        assert len(result.Confirmations) == 2
        assert result.Confirmations[0].OrderID == "ORDER123"
        assert result.Confirmations[0].Message == "Order confirmed"
        assert result.Confirmations[1].OrderID == "ORDER124"
        assert result.Confirmations[1].Message == "Order confirmed"
        assert result.Errors is None

    @pytest.mark.asyncio
    async def test_confirm_group_order_validation_errors(
        self, order_execution_service, http_client_mock
    ):
        """Test validation errors when confirming a group order"""
        # Mock response with errors - Use "Confirmations" key (can be empty)
        mock_response = {
            "Confirmations": [],
            "Errors": [
                {
                    "OrderID": "ORDER123",
                    "Error": "INVALID_QUANTITY",
                    "Message": "Quantity must be positive",
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
                    Quantity="-100",
                    OrderType=OrderType.MARKET,
                    TradeAction=OrderSide.BUY,
                    TimeInForce=TimeInForce(Duration=OrderDuration.DAY),
                    Route="Intelligent",
                )
            ],
        )

        # Call the method
        result = await order_execution_service.confirm_group_order(request)

        # Verify the API was called correctly
        http_client_mock.post.assert_called_once_with(
            "/v3/orderexecution/ordergroupconfirm", request.model_dump(exclude_none=True)
        )

        # Verify the result - Access "Confirmations" field
        assert isinstance(result, GroupOrderConfirmationResponse)
        assert len(result.Confirmations) == 0
        assert len(result.Errors) == 1
        assert result.Errors[0].OrderID == "ORDER123"
        assert result.Errors[0].Error == "INVALID_QUANTITY"
        assert result.Errors[0].Message == "Quantity must be positive"

    @pytest.mark.asyncio
    async def test_confirm_group_order_network_error(
        self, order_execution_service, http_client_mock
    ):
        """Test network error handling when confirming a group order"""
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
            await order_execution_service.confirm_group_order(request)

        # Verify the API was called correctly
        http_client_mock.post.assert_called_once_with(
            "/v3/orderexecution/ordergroupconfirm", request.model_dump(exclude_none=True)
        )

    @pytest.mark.asyncio
    async def test_confirm_group_order_unauthorized(
        self, order_execution_service, http_client_mock
    ):
        """Test unauthorized error handling when confirming a group order"""
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
            await order_execution_service.confirm_group_order(request)

        # Verify the API was called correctly
        http_client_mock.post.assert_called_once_with(
            "/v3/orderexecution/ordergroupconfirm", request.model_dump(exclude_none=True)
        )
