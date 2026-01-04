import pytest

from tradestation.ts_types.order_execution import CancelOrderResponse


class TestCancelOrder:
    """Tests for the cancel_order method in OrderExecutionService"""

    @pytest.mark.asyncio
    async def test_cancel_order_success(self, order_execution_service, http_client_mock):
        """Test successful cancellation of an order"""
        # Mock response data
        mock_response = {"OrderID": "ORDER123", "Message": "Order cancelled successfully"}

        # Configure mock
        http_client_mock.delete.return_value = mock_response

        # Call the method
        result = await order_execution_service.cancel_order("ORDER123")

        # Verify the API was called correctly
        http_client_mock.delete.assert_called_once_with("/v3/orderexecution/orders/ORDER123")

        # Verify the result
        assert isinstance(result, CancelOrderResponse)
        assert result.OrderID == "ORDER123"
        assert result.Message == "Order cancelled successfully"
        assert result.Error is None

    @pytest.mark.asyncio
    async def test_cancel_order_not_found(self, order_execution_service, http_client_mock):
        """Test order not found error when cancelling an order"""
        # Mock response with error
        mock_response = {
            "OrderID": "ORDER123",
            "Error": "ORDER_NOT_FOUND",
            "Message": "Order not found",
        }

        # Configure mock
        http_client_mock.delete.return_value = mock_response

        # Call the method
        result = await order_execution_service.cancel_order("ORDER123")

        # Verify the API was called correctly
        http_client_mock.delete.assert_called_once_with("/v3/orderexecution/orders/ORDER123")

        # Verify the result
        assert isinstance(result, CancelOrderResponse)
        assert result.OrderID == "ORDER123"
        assert result.Error == "ORDER_NOT_FOUND"
        assert result.Message == "Order not found"

    @pytest.mark.asyncio
    async def test_cancel_order_network_error(self, order_execution_service, http_client_mock):
        """Test network error handling when cancelling an order"""
        # Configure mock to raise exception
        http_client_mock.delete.side_effect = Exception("Network error")

        # Verify the exception is propagated
        with pytest.raises(Exception, match="Network error"):
            await order_execution_service.cancel_order("ORDER123")

        # Verify the API was called correctly
        http_client_mock.delete.assert_called_once_with("/v3/orderexecution/orders/ORDER123")

    @pytest.mark.asyncio
    async def test_cancel_order_unauthorized(self, order_execution_service, http_client_mock):
        """Test unauthorized error handling when cancelling an order"""
        # Configure mock to raise unauthorized exception
        http_client_mock.delete.side_effect = Exception("Unauthorized")

        # Verify the exception is propagated
        with pytest.raises(Exception, match="Unauthorized"):
            await order_execution_service.cancel_order("ORDER123")

        # Verify the API was called correctly
        http_client_mock.delete.assert_called_once_with("/v3/orderexecution/orders/ORDER123")

    @pytest.mark.asyncio
    async def test_cancel_order_rate_limit(self, order_execution_service, http_client_mock):
        """Test rate limit error handling when cancelling an order"""
        # Configure mock to raise rate limit exception
        http_client_mock.delete.side_effect = Exception("Rate limit exceeded")

        # Verify the exception is propagated
        with pytest.raises(Exception, match="Rate limit exceeded"):
            await order_execution_service.cancel_order("ORDER123")

        # Verify the API was called correctly
        http_client_mock.delete.assert_called_once_with("/v3/orderexecution/orders/ORDER123")

    @pytest.mark.asyncio
    async def test_cancel_order_service_unavailable(
        self, order_execution_service, http_client_mock
    ):
        """Test service unavailable error handling when cancelling an order"""
        # Configure mock to raise service unavailable exception
        http_client_mock.delete.side_effect = Exception("Service unavailable")

        # Verify the exception is propagated
        with pytest.raises(Exception, match="Service unavailable"):
            await order_execution_service.cancel_order("ORDER123")

        # Verify the API was called correctly
        http_client_mock.delete.assert_called_once_with("/v3/orderexecution/orders/ORDER123")

    @pytest.mark.asyncio
    async def test_cancel_order_gateway_timeout(self, order_execution_service, http_client_mock):
        """Test gateway timeout error handling when cancelling an order"""
        # Configure mock to raise gateway timeout exception
        http_client_mock.delete.side_effect = Exception("Gateway timeout")

        # Verify the exception is propagated
        with pytest.raises(Exception, match="Gateway timeout"):
            await order_execution_service.cancel_order("ORDER123")

        # Verify the API was called correctly
        http_client_mock.delete.assert_called_once_with("/v3/orderexecution/orders/ORDER123")
