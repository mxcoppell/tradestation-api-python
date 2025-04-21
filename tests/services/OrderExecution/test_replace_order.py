import pytest
from src.ts_types.order_execution import (
    OrderReplaceRequest,
    ReplaceOrderResponse,
    OrderType,
    OrderDuration,
    OrderReplaceTimeInForce,
    OrderReplaceAdvancedOptions,
    OrderReplaceTrailingStop,
)


class TestReplaceOrder:
    """Tests for the replace_order method in OrderExecutionService"""

    @pytest.mark.asyncio
    async def test_replace_order_quantity_success(self, order_execution_service, http_client_mock):
        """Test successful replacement of an order's quantity"""
        # Create order replace request - change quantity only
        request = OrderReplaceRequest(Quantity="20")

        # Mock response data - FLAT structure for successful replace
        mock_response = {"OrderID": "ORDER123", "Message": "Order replaced successfully"}

        # Configure mock
        http_client_mock.put.return_value = mock_response

        # Call the method
        result = await order_execution_service.replace_order("ORDER123", request)

        # Verify the API was called correctly
        http_client_mock.put.assert_called_once_with(
            "/v3/orderexecution/orders/ORDER123",
            {"Quantity": "20"},
        )

        # Verify the result - check against ReplaceOrderResponse
        assert isinstance(result, ReplaceOrderResponse)
        assert result.OrderID == "ORDER123"
        assert result.Message == "Order replaced successfully"

    @pytest.mark.asyncio
    async def test_replace_limit_price_success(self, order_execution_service, http_client_mock):
        """Test successful replacement of a limit order's price"""
        # Create order replace request - change limit price only
        request = OrderReplaceRequest(LimitPrice="155.50")

        # Mock response data - FLAT structure
        mock_response = {"OrderID": "ORDER456", "Message": "Limit price updated successfully"}

        # Configure mock
        http_client_mock.put.return_value = mock_response

        # Call the method
        result = await order_execution_service.replace_order("ORDER456", request)

        # Verify the API was called correctly
        http_client_mock.put.assert_called_once_with(
            "/v3/orderexecution/orders/ORDER456",
            {"LimitPrice": "155.50"},
        )

        # Verify the result - check against ReplaceOrderResponse
        assert isinstance(result, ReplaceOrderResponse)
        assert result.OrderID == "ORDER456"
        assert result.Message == "Limit price updated successfully"

    @pytest.mark.asyncio
    async def test_replace_stop_price_success(self, order_execution_service, http_client_mock):
        """Test successful replacement of a stop order's price"""
        # Create order replace request - change stop price only
        request = OrderReplaceRequest(StopPrice="705.25")

        # Mock response data - FLAT structure
        mock_response = {"OrderID": "ORDER789", "Message": "Stop price updated successfully"}

        # Configure mock
        http_client_mock.put.return_value = mock_response

        # Call the method
        result = await order_execution_service.replace_order("ORDER789", request)

        # Verify the API was called correctly
        http_client_mock.put.assert_called_once_with(
            "/v3/orderexecution/orders/ORDER789",
            {"StopPrice": "705.25"},
        )

        # Verify the result - check against ReplaceOrderResponse
        assert isinstance(result, ReplaceOrderResponse)
        assert result.OrderID == "ORDER789"
        assert result.Message == "Stop price updated successfully"

    @pytest.mark.asyncio
    async def test_replace_order_type_success(self, order_execution_service, http_client_mock):
        """Test successful replacement of an order's type"""
        # Create order replace request - change order type to Market
        request = OrderReplaceRequest(OrderType=OrderType.MARKET)

        # Mock response data - FLAT structure
        mock_response = {
            "OrderID": "ORDER123",
            "Message": "Order type changed to Market successfully",
        }

        # Configure mock
        http_client_mock.put.return_value = mock_response

        # Call the method
        result = await order_execution_service.replace_order("ORDER123", request)

        # Verify the API was called correctly
        http_client_mock.put.assert_called_once_with(
            "/v3/orderexecution/orders/ORDER123",
            {"OrderType": "Market"},
        )

        # Verify the result - check against ReplaceOrderResponse
        assert isinstance(result, ReplaceOrderResponse)
        assert result.OrderID == "ORDER123"
        assert result.Message == "Order type changed to Market successfully"

    @pytest.mark.asyncio
    async def test_replace_time_in_force_success(self, order_execution_service, http_client_mock):
        """Test successful replacement of an order's time in force"""
        # Create order replace request - change time in force
        request = OrderReplaceRequest(
            TimeInForce=OrderReplaceTimeInForce(Duration=OrderDuration.GTC)
        )

        # Mock response data - FLAT structure
        mock_response = {"OrderID": "ORDER123", "Message": "Time in force updated successfully"}

        # Configure mock
        http_client_mock.put.return_value = mock_response

        # Call the method
        result = await order_execution_service.replace_order("ORDER123", request)

        # Verify the API was called correctly
        http_client_mock.put.assert_called_once_with(
            "/v3/orderexecution/orders/ORDER123",
            {"TimeInForce": {"Duration": "GTC"}},
        )

        # Verify the result - check against ReplaceOrderResponse
        assert isinstance(result, ReplaceOrderResponse)
        assert result.OrderID == "ORDER123"
        assert result.Message == "Time in force updated successfully"

    @pytest.mark.asyncio
    async def test_replace_trailing_stop_amount_success(
        self, order_execution_service, http_client_mock
    ):
        """Test successful replacement of an order's trailing stop amount"""
        # Create order replace request - add trailing stop with amount
        request = OrderReplaceRequest(
            AdvancedOptions=OrderReplaceAdvancedOptions(
                TrailingStop=OrderReplaceTrailingStop(Amount="2.50")
            )
        )

        # Mock response data - FLAT structure
        mock_response = {
            "OrderID": "ORDER123",
            "Message": "Trailing stop amount updated successfully",
        }

        # Configure mock
        http_client_mock.put.return_value = mock_response

        # Call the method
        result = await order_execution_service.replace_order("ORDER123", request)

        # Verify the API was called correctly
        http_client_mock.put.assert_called_once_with(
            "/v3/orderexecution/orders/ORDER123",
            {"AdvancedOptions": {"TrailingStop": {"Amount": "2.50"}}},
        )

        # Verify the result - check against ReplaceOrderResponse
        assert isinstance(result, ReplaceOrderResponse)
        assert result.OrderID == "ORDER123"
        assert result.Message == "Trailing stop amount updated successfully"

    @pytest.mark.asyncio
    async def test_replace_trailing_stop_percent_success(
        self, order_execution_service, http_client_mock
    ):
        """Test successful replacement of an order's trailing stop percentage"""
        # Create order replace request - add trailing stop with percentage
        request = OrderReplaceRequest(
            AdvancedOptions=OrderReplaceAdvancedOptions(
                TrailingStop=OrderReplaceTrailingStop(Percent="5.0")
            )
        )

        # Mock response data - FLAT structure
        mock_response = {
            "OrderID": "ORDER123",
            "Message": "Trailing stop percentage updated successfully",
        }

        # Configure mock
        http_client_mock.put.return_value = mock_response

        # Call the method
        result = await order_execution_service.replace_order("ORDER123", request)

        # Verify the API was called correctly
        http_client_mock.put.assert_called_once_with(
            "/v3/orderexecution/orders/ORDER123",
            {"AdvancedOptions": {"TrailingStop": {"Percent": "5.0"}}},
        )

        # Verify the result - check against ReplaceOrderResponse
        assert isinstance(result, ReplaceOrderResponse)
        assert result.OrderID == "ORDER123"
        assert result.Message == "Trailing stop percentage updated successfully"

    @pytest.mark.asyncio
    async def test_replace_multiple_parameters_success(
        self, order_execution_service, http_client_mock
    ):
        """Test successful replacement of multiple order parameters"""
        # Create order replace request - change quantity and limit price
        request = OrderReplaceRequest(Quantity="15", LimitPrice="160.75")

        # Mock response data - FLAT structure
        mock_response = {"OrderID": "ORDER123", "Message": "Order parameters updated successfully"}

        # Configure mock
        http_client_mock.put.return_value = mock_response

        # Call the method
        result = await order_execution_service.replace_order("ORDER123", request)

        # Verify the API was called correctly
        http_client_mock.put.assert_called_once_with(
            "/v3/orderexecution/orders/ORDER123",
            {"Quantity": "15", "LimitPrice": "160.75"},
        )

        # Verify the result - check against ReplaceOrderResponse
        assert isinstance(result, ReplaceOrderResponse)
        assert result.OrderID == "ORDER123"
        assert result.Message == "Order parameters updated successfully"

    @pytest.mark.asyncio
    async def test_replace_order_error(self, order_execution_service, http_client_mock):
        """Test error handling when replacing an order"""
        # Create order replace request
        request = OrderReplaceRequest(Quantity="20")

        # Mock response data with error - Assuming flat structure for error too?
        # TODO: Need to confirm the exact error response structure for a failed PUT /orders/{id}.
        # Assuming for now it might still return a flat structure but with an error message,
        # or maybe it raises an HTTPError (tested separately). Let's mock a successful-looking
        # structure but with an error message, anticipating the Pydantic model might evolve.
        # Alternatively, mock an HTTPError.
        mock_response = {
            "OrderID": "ORDER123",  # May or may not be present on error
            "Message": "Cannot replace an order that has already been filled",
            # "Error": "ORDER_ALREADY_FILLED" # Add if API returns an error code field
        }

        # Configure mock
        http_client_mock.put.return_value = mock_response

        # Call the method
        result = await order_execution_service.replace_order("ORDER123", request)

        # Verify the result - check against ReplaceOrderResponse structure
        assert isinstance(result, ReplaceOrderResponse)
        assert result.OrderID == "ORDER123"
        assert "Cannot replace" in result.Message  # Check for error in message

    @pytest.mark.asyncio
    async def test_replace_order_network_error(self, order_execution_service, http_client_mock):
        """Test network error handling when replacing an order"""
        # Create order replace request
        request = OrderReplaceRequest(Quantity="20")

        # Configure mock to raise exception
        http_client_mock.put.side_effect = Exception("Network error")

        # Verify the exception is propagated
        with pytest.raises(Exception, match="Network error"):
            await order_execution_service.replace_order("ORDER123", request)

        # Verify the API was called correctly
        http_client_mock.put.assert_called_once_with(
            "/v3/orderexecution/orders/ORDER123",
            {"Quantity": "20"},
        )

    @pytest.mark.asyncio
    async def test_replace_order_unauthorized(self, order_execution_service, http_client_mock):
        """Test unauthorized error handling when replacing an order"""
        # Create order replace request
        request = OrderReplaceRequest(Quantity="20")

        # Configure mock to raise unauthorized exception
        http_client_mock.put.side_effect = Exception("Unauthorized")

        # Verify the exception is propagated
        with pytest.raises(Exception, match="Unauthorized"):
            await order_execution_service.replace_order("ORDER123", request)

        # Verify the API was called correctly
        http_client_mock.put.assert_called_once_with(
            "/v3/orderexecution/orders/ORDER123",
            {"Quantity": "20"},
        )

    @pytest.mark.asyncio
    async def test_replace_order_rate_limit(self, order_execution_service, http_client_mock):
        """Test rate limit error handling when replacing an order"""
        # Create order replace request
        request = OrderReplaceRequest(Quantity="20")

        # Configure mock to raise rate limit exception
        http_client_mock.put.side_effect = Exception("Rate limit exceeded")

        # Verify the exception is propagated
        with pytest.raises(Exception, match="Rate limit exceeded"):
            await order_execution_service.replace_order("ORDER123", request)

        # Verify the API was called correctly
        http_client_mock.put.assert_called_once_with(
            "/v3/orderexecution/orders/ORDER123",
            {"Quantity": "20"},
        )

    @pytest.mark.asyncio
    async def test_replace_order_service_unavailable(
        self, order_execution_service, http_client_mock
    ):
        """Test service unavailable error handling when replacing an order"""
        # Create order replace request
        request = OrderReplaceRequest(Quantity="20")

        # Configure mock to raise service unavailable exception
        http_client_mock.put.side_effect = Exception("Service unavailable")

        # Verify the exception is propagated
        with pytest.raises(Exception, match="Service unavailable"):
            await order_execution_service.replace_order("ORDER123", request)

        # Verify the API was called correctly
        http_client_mock.put.assert_called_once_with(
            "/v3/orderexecution/orders/ORDER123",
            {"Quantity": "20"},
        )

    @pytest.mark.asyncio
    async def test_replace_order_gateway_timeout(self, order_execution_service, http_client_mock):
        """Test gateway timeout error handling when replacing an order"""
        # Create order replace request
        request = OrderReplaceRequest(Quantity="20")

        # Configure mock to raise gateway timeout exception
        http_client_mock.put.side_effect = Exception("Gateway timeout")

        # Verify the exception is propagated
        with pytest.raises(Exception, match="Gateway timeout"):
            await order_execution_service.replace_order("ORDER123", request)

        # Verify the API was called correctly
        http_client_mock.put.assert_called_once_with(
            "/v3/orderexecution/orders/ORDER123",
            {"Quantity": "20"},
        )
