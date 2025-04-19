import pytest
from src.ts_types.order_execution import (
    OrderReplaceRequest,
    OrderResponse,
    OrderType,
    OrderDuration,
    OrderReplaceTimeInForce,
    OrderReplaceAdvancedOptions,
    OrderReplaceTrailingStop,
    OrderResponseSuccess,
    OrderResponseError,
)


class TestReplaceOrder:
    """Tests for the replace_order method in OrderExecutionService"""

    @pytest.mark.asyncio
    async def test_replace_order_quantity_success(self, order_execution_service, http_client_mock):
        """Test successful replacement of an order's quantity"""
        # Create order replace request - change quantity only
        request = OrderReplaceRequest(Quantity="20")

        # Mock response data
        mock_response = {
            "Orders": [{"OrderID": "ORDER123", "Message": "Order replaced successfully"}]
        }

        # Configure mock
        http_client_mock.put.return_value = mock_response

        # Call the method
        result = await order_execution_service.replace_order("ORDER123", request)

        # Verify the API was called correctly
        http_client_mock.put.assert_called_once_with(
            "/v3/orderexecution/orders/ORDER123",
            {"Quantity": "20"},
        )

        # Verify the result
        assert isinstance(result, OrderResponse)
        assert isinstance(result.Orders, list)
        assert len(result.Orders) == 1
        assert isinstance(result.Orders[0], OrderResponseSuccess)
        assert result.Orders[0].OrderID == "ORDER123"
        assert result.Orders[0].Message == "Order replaced successfully"
        assert result.Errors is None

    @pytest.mark.asyncio
    async def test_replace_limit_price_success(self, order_execution_service, http_client_mock):
        """Test successful replacement of a limit order's price"""
        # Create order replace request - change limit price only
        request = OrderReplaceRequest(LimitPrice="155.50")

        # Mock response data
        mock_response = {
            "Orders": [{"OrderID": "ORDER456", "Message": "Limit price updated successfully"}]
        }

        # Configure mock
        http_client_mock.put.return_value = mock_response

        # Call the method
        result = await order_execution_service.replace_order("ORDER456", request)

        # Verify the API was called correctly
        http_client_mock.put.assert_called_once_with(
            "/v3/orderexecution/orders/ORDER456",
            {"LimitPrice": "155.50"},
        )

        # Verify the result
        assert isinstance(result, OrderResponse)
        assert isinstance(result.Orders, list)
        assert len(result.Orders) == 1
        assert result.Orders[0].OrderID == "ORDER456"
        assert result.Orders[0].Message == "Limit price updated successfully"

    @pytest.mark.asyncio
    async def test_replace_stop_price_success(self, order_execution_service, http_client_mock):
        """Test successful replacement of a stop order's price"""
        # Create order replace request - change stop price only
        request = OrderReplaceRequest(StopPrice="705.25")

        # Mock response data
        mock_response = {
            "Orders": [{"OrderID": "ORDER789", "Message": "Stop price updated successfully"}]
        }

        # Configure mock
        http_client_mock.put.return_value = mock_response

        # Call the method
        result = await order_execution_service.replace_order("ORDER789", request)

        # Verify the API was called correctly
        http_client_mock.put.assert_called_once_with(
            "/v3/orderexecution/orders/ORDER789",
            {"StopPrice": "705.25"},
        )

        # Verify the result
        assert isinstance(result, OrderResponse)
        assert isinstance(result.Orders, list)
        assert len(result.Orders) == 1
        assert result.Orders[0].OrderID == "ORDER789"
        assert result.Orders[0].Message == "Stop price updated successfully"

    @pytest.mark.asyncio
    async def test_replace_order_type_success(self, order_execution_service, http_client_mock):
        """Test successful replacement of an order's type"""
        # Create order replace request - change order type to Market
        request = OrderReplaceRequest(OrderType=OrderType.MARKET)

        # Mock response data
        mock_response = {
            "Orders": [
                {"OrderID": "ORDER123", "Message": "Order type changed to Market successfully"}
            ]
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

        # Verify the result
        assert isinstance(result, OrderResponse)
        assert isinstance(result.Orders, list)
        assert len(result.Orders) == 1
        assert result.Orders[0].OrderID == "ORDER123"
        assert result.Orders[0].Message == "Order type changed to Market successfully"

    @pytest.mark.asyncio
    async def test_replace_time_in_force_success(self, order_execution_service, http_client_mock):
        """Test successful replacement of an order's time in force"""
        # Create order replace request - change time in force
        request = OrderReplaceRequest(
            TimeInForce=OrderReplaceTimeInForce(Duration=OrderDuration.GTC)
        )

        # Mock response data
        mock_response = {
            "Orders": [{"OrderID": "ORDER123", "Message": "Time in force updated successfully"}]
        }

        # Configure mock
        http_client_mock.put.return_value = mock_response

        # Call the method
        result = await order_execution_service.replace_order("ORDER123", request)

        # Verify the API was called correctly
        http_client_mock.put.assert_called_once_with(
            "/v3/orderexecution/orders/ORDER123",
            {"TimeInForce": {"Duration": "GTC"}},
        )

        # Verify the result
        assert isinstance(result, OrderResponse)
        assert isinstance(result.Orders, list)
        assert len(result.Orders) == 1
        assert result.Orders[0].OrderID == "ORDER123"
        assert result.Orders[0].Message == "Time in force updated successfully"

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

        # Mock response data
        mock_response = {
            "Orders": [
                {"OrderID": "ORDER123", "Message": "Trailing stop amount updated successfully"}
            ]
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

        # Verify the result
        assert isinstance(result, OrderResponse)
        assert isinstance(result.Orders, list)
        assert len(result.Orders) == 1
        assert result.Orders[0].OrderID == "ORDER123"
        assert result.Orders[0].Message == "Trailing stop amount updated successfully"

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

        # Mock response data
        mock_response = {
            "Orders": [
                {"OrderID": "ORDER123", "Message": "Trailing stop percentage updated successfully"}
            ]
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

        # Verify the result
        assert isinstance(result, OrderResponse)
        assert isinstance(result.Orders, list)
        assert len(result.Orders) == 1
        assert result.Orders[0].OrderID == "ORDER123"
        assert result.Orders[0].Message == "Trailing stop percentage updated successfully"

    @pytest.mark.asyncio
    async def test_replace_multiple_parameters_success(
        self, order_execution_service, http_client_mock
    ):
        """Test successful replacement of multiple order parameters"""
        # Create order replace request - change quantity and limit price
        request = OrderReplaceRequest(Quantity="15", LimitPrice="160.75")

        # Mock response data
        mock_response = {
            "Orders": [{"OrderID": "ORDER123", "Message": "Order parameters updated successfully"}]
        }

        # Configure mock
        http_client_mock.put.return_value = mock_response

        # Call the method
        result = await order_execution_service.replace_order("ORDER123", request)

        # Verify the API was called correctly
        http_client_mock.put.assert_called_once_with(
            "/v3/orderexecution/orders/ORDER123",
            {"Quantity": "15", "LimitPrice": "160.75"},
        )

        # Verify the result
        assert isinstance(result, OrderResponse)
        assert isinstance(result.Orders, list)
        assert len(result.Orders) == 1
        assert result.Orders[0].OrderID == "ORDER123"
        assert result.Orders[0].Message == "Order parameters updated successfully"

    @pytest.mark.asyncio
    async def test_replace_order_error(self, order_execution_service, http_client_mock):
        """Test error handling when replacing an order"""
        # Create order replace request
        request = OrderReplaceRequest(Quantity="20")

        # Mock response data with error
        mock_response = {
            "Errors": [
                {
                    "OrderID": "ORDER123",
                    "Error": "ORDER_ALREADY_FILLED",
                    "Message": "Cannot replace an order that has already been filled",
                }
            ]
        }

        # Configure mock
        http_client_mock.put.return_value = mock_response

        # Call the method
        result = await order_execution_service.replace_order("ORDER123", request)

        # Verify the API was called correctly
        http_client_mock.put.assert_called_once_with(
            "/v3/orderexecution/orders/ORDER123",
            {"Quantity": "20"},
        )

        # Verify the result
        assert isinstance(result, OrderResponse)
        assert result.Orders is None
        assert isinstance(result.Errors, list)
        assert len(result.Errors) == 1
        assert isinstance(result.Errors[0], OrderResponseError)
        assert result.Errors[0].OrderID == "ORDER123"
        assert result.Errors[0].Error == "ORDER_ALREADY_FILLED"
        assert result.Errors[0].Message == "Cannot replace an order that has already been filled"

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
