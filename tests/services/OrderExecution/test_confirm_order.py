import pytest
from unittest.mock import patch

from tradestation.ts_types.order_execution import (
    OrderRequest,
    OrderType,
    OrderSide,
    TimeInForce,
    OrderDuration,
    GroupOrderConfirmationResponse,
    GroupOrderConfirmationDetail,
    GroupOrderResponseError,
)


class TestConfirmOrder:
    """Tests for the confirm_order method in OrderExecutionService"""

    @pytest.mark.asyncio
    async def test_confirm_simple_market_order(self, order_execution_service, http_client_mock):
        """Test confirmation of a simple market order"""
        # Mock response data (Wrapped in Group Structure)
        mock_confirmation_detail = {
            "Route": "Intelligent",
            "Duration": "Day",
            "AccountID": "123456",  # Changed Account to AccountID to match GroupOrderConfirmationDetail
            "SummaryMessage": "Buy 100 MSFT Market Day",
            "EstimatedPrice": "152.05",
            "EstimatedCost": "15205.00",  # Added EstimatedCost based on detail model
            "EstimatedCommission": "5.00",
            "OrderConfirmID": "confirm-123",  # Added OrderConfirmID based on detail model
            # Removed fields not in GroupOrderConfirmationDetail
            # "EstimatedPriceDisplay": "152.05",
            # "EstimatedCommissionDisplay": "5.00",
            # "InitialMarginDisplay": "7,602.50",
            # "ProductCurrency": "USD",
            # "AccountCurrency": "USD",
        }
        mock_response = {"Confirmations": [mock_confirmation_detail], "Errors": None}

        # Configure mock
        http_client_mock.post.return_value = mock_response

        # Create request
        request = OrderRequest(
            AccountID="123456",
            Symbol="MSFT",
            Quantity="100",
            OrderType=OrderType.MARKET,
            TradeAction=OrderSide.BUY,
            TimeInForce=TimeInForce(Duration=OrderDuration.DAY),
            Route="Intelligent",
        )

        # Call the method
        result = await order_execution_service.confirm_order(request)

        # Verify the API was called correctly
        http_client_mock.post.assert_called_once_with(
            "/v3/orderexecution/orderconfirm", request.model_dump(exclude_none=True)
        )

        # Verify the result
        assert isinstance(result, GroupOrderConfirmationResponse)
        assert result.Errors is None
        assert len(result.Confirmations) == 1
        detail = result.Confirmations[0]
        assert isinstance(detail, GroupOrderConfirmationDetail)
        assert detail.Route == "Intelligent"
        # assert detail.Duration == "Day" # Duration is in nested TimeInForce
        assert detail.AccountID == "123456"
        assert detail.SummaryMessage == "Buy 100 MSFT Market Day"
        assert detail.EstimatedPrice == "152.05"
        assert detail.EstimatedCost == "15205.00"
        assert detail.EstimatedCommission == "5.00"
        assert detail.OrderConfirmID == "confirm-123"

    @pytest.mark.asyncio
    async def test_confirm_limit_order(self, order_execution_service, http_client_mock):
        """Test confirmation of a limit order"""
        # Mock response data (Wrapped in Group Structure)
        mock_confirmation_detail = {
            "Route": "Intelligent",
            "Duration": "Day",
            "AccountID": "123456",
            "SummaryMessage": "Buy 100 MSFT Limit @ 150.00 Day",
            "EstimatedPrice": "150.00",
            "EstimatedCost": "15000.00",
            "EstimatedCommission": "5.00",
            "OrderConfirmID": "confirm-456",
        }
        mock_response = {"Confirmations": [mock_confirmation_detail], "Errors": None}

        # Configure mock
        http_client_mock.post.return_value = mock_response

        # Create request
        request = OrderRequest(
            AccountID="123456",
            Symbol="MSFT",
            Quantity="100",
            OrderType=OrderType.LIMIT,
            LimitPrice="150.00",
            TradeAction=OrderSide.BUY,
            TimeInForce=TimeInForce(Duration=OrderDuration.DAY),
            Route="Intelligent",
        )

        # Call the method
        result = await order_execution_service.confirm_order(request)

        # Verify the API was called correctly
        http_client_mock.post.assert_called_once_with(
            "/v3/orderexecution/orderconfirm", request.model_dump(exclude_none=True)
        )

        # Verify the result
        assert isinstance(result, GroupOrderConfirmationResponse)
        assert result.Errors is None
        assert len(result.Confirmations) == 1
        detail = result.Confirmations[0]
        assert isinstance(detail, GroupOrderConfirmationDetail)
        assert detail.Route == "Intelligent"
        assert detail.AccountID == "123456"
        assert detail.SummaryMessage == "Buy 100 MSFT Limit @ 150.00 Day"
        assert detail.EstimatedPrice == "150.00"
        assert detail.EstimatedCost == "15000.00"
        assert detail.EstimatedCommission == "5.00"
        assert detail.OrderConfirmID == "confirm-456"

    @pytest.mark.asyncio
    async def test_confirm_stop_order(self, order_execution_service, http_client_mock):
        """Test confirmation of a stop market order"""
        # Mock response data (Wrapped in Group Structure)
        mock_confirmation_detail = {
            "Route": "Intelligent",
            "Duration": "Day",
            "AccountID": "123456",
            "SummaryMessage": "Sell 100 MSFT Stop @ 155.00 Day",
            "EstimatedPrice": "155.00",
            "EstimatedCost": "-15500.00",  # Assuming cost is negative for sell
            "EstimatedCommission": "5.00",
            "OrderConfirmID": "confirm-789",
        }
        mock_response = {"Confirmations": [mock_confirmation_detail], "Errors": None}

        # Configure mock
        http_client_mock.post.return_value = mock_response

        # Create request
        request = OrderRequest(
            AccountID="123456",
            Symbol="MSFT",
            Quantity="100",
            OrderType=OrderType.STOP_MARKET,
            StopPrice="155.00",
            TradeAction=OrderSide.SELL,
            TimeInForce=TimeInForce(Duration=OrderDuration.DAY),
            Route="Intelligent",
        )

        # Call the method
        result = await order_execution_service.confirm_order(request)

        # Verify the API was called correctly
        http_client_mock.post.assert_called_once_with(
            "/v3/orderexecution/orderconfirm", request.model_dump(exclude_none=True)
        )

        # Verify the result
        assert isinstance(result, GroupOrderConfirmationResponse)
        assert result.Errors is None
        assert len(result.Confirmations) == 1
        detail = result.Confirmations[0]
        assert isinstance(detail, GroupOrderConfirmationDetail)
        assert detail.Route == "Intelligent"
        assert detail.AccountID == "123456"
        assert detail.SummaryMessage == "Sell 100 MSFT Stop @ 155.00 Day"
        assert detail.EstimatedPrice == "155.00"
        assert detail.EstimatedCost == "-15500.00"
        assert detail.EstimatedCommission == "5.00"
        assert detail.OrderConfirmID == "confirm-789"

    @pytest.mark.asyncio
    async def test_confirm_order_validation_errors(self, order_execution_service, http_client_mock):
        """Test handling of errors within the confirmation response"""
        # Mock response with validation error in the Errors list
        mock_error_detail = {
            "OrderID": "order-err-1",
            "Error": "InvalidParameter",
            "Message": "Quantity must be greater than 0",
        }
        mock_response = {
            "Confirmations": [],  # No confirmations in error case
            "Errors": [mock_error_detail],
        }

        # Configure mock
        http_client_mock.post.return_value = mock_response

        # Create request with invalid quantity
        request = OrderRequest(
            AccountID="123456",
            Symbol="MSFT",
            Quantity="-100",  # Invalid quantity
            OrderType=OrderType.MARKET,
            TradeAction=OrderSide.BUY,
            TimeInForce=TimeInForce(Duration=OrderDuration.DAY),
            Route="Intelligent",
        )

        # Call the method
        result = await order_execution_service.confirm_order(request)

        # Verify the API was called correctly
        http_client_mock.post.assert_called_once_with(
            "/v3/orderexecution/orderconfirm", request.model_dump(exclude_none=True)
        )

        # Verify the result contains the error
        assert isinstance(result, GroupOrderConfirmationResponse)
        assert len(result.Confirmations) == 0
        assert result.Errors is not None
        assert len(result.Errors) == 1
        error = result.Errors[0]
        assert isinstance(error, GroupOrderResponseError)
        assert error.OrderID == "order-err-1"
        assert error.Error == "InvalidParameter"
        assert error.Message == "Quantity must be greater than 0"

    @pytest.mark.asyncio
    async def test_confirm_order_network_error(self, order_execution_service, http_client_mock):
        """Test network error handling when confirming an order"""
        # Configure mock to raise an exception
        http_client_mock.post.side_effect = Exception("Network error")

        # Create request
        request = OrderRequest(
            AccountID="123456",
            Symbol="MSFT",
            Quantity="100",
            OrderType=OrderType.MARKET,
            TradeAction=OrderSide.BUY,
            TimeInForce=TimeInForce(Duration=OrderDuration.DAY),
            Route="Intelligent",
        )

        # Verify that the exception is raised
        with pytest.raises(Exception, match="Network error"):
            await order_execution_service.confirm_order(request)

        # Verify the API was called correctly
        http_client_mock.post.assert_called_once_with(
            "/v3/orderexecution/orderconfirm", request.model_dump(exclude_none=True)
        )

    @pytest.mark.asyncio
    async def test_confirm_order_unauthorized(self, order_execution_service, http_client_mock):
        """Test unauthorized error handling"""
        # Configure mock to raise a 401 Unauthorized error
        http_client_mock.post.side_effect = Exception(
            "Unauthorized"
        )  # Simplistic, real would be HTTPError

        # Create request
        request = OrderRequest(
            AccountID="123456",
            Symbol="MSFT",
            Quantity="100",
            OrderType=OrderType.MARKET,
            TradeAction=OrderSide.BUY,
            TimeInForce=TimeInForce(Duration=OrderDuration.DAY),
            Route="Intelligent",
        )

        # Verify that the exception is raised
        with pytest.raises(Exception, match="Unauthorized"):
            await order_execution_service.confirm_order(request)

        # Verify the API was called correctly
        http_client_mock.post.assert_called_once_with(
            "/v3/orderexecution/orderconfirm", request.model_dump(exclude_none=True)
        )
