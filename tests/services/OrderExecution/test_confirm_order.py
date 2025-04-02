import pytest
from unittest.mock import patch

from src.ts_types.order_execution import (
    OrderRequest,
    OrderType,
    OrderSide,
    TimeInForce,
    OrderDuration,
    OrderConfirmationResponse,
)


class TestConfirmOrder:
    """Tests for the confirm_order method in OrderExecutionService"""

    @pytest.mark.asyncio
    async def test_confirm_simple_market_order(self, order_execution_service, http_client_mock):
        """Test confirmation of a simple market order"""
        # Mock response data
        mock_response = {
            "Route": "Intelligent",
            "Duration": "Day",
            "Account": "123456",
            "SummaryMessage": "Buy 100 MSFT Market Day",
            "EstimatedPrice": "152.05",
            "EstimatedPriceDisplay": "152.05",
            "EstimatedCommission": "5.00",
            "EstimatedCommissionDisplay": "5.00",
            "InitialMarginDisplay": "7,602.50",
            "ProductCurrency": "USD",
            "AccountCurrency": "USD",
        }

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
        assert isinstance(result, OrderConfirmationResponse)
        assert result.Route == "Intelligent"
        assert result.Duration == "Day"
        assert result.Account == "123456"
        assert result.SummaryMessage == "Buy 100 MSFT Market Day"
        assert result.EstimatedPrice == "152.05"
        assert result.EstimatedPriceDisplay == "152.05"
        assert result.EstimatedCommission == "5.00"
        assert result.EstimatedCommissionDisplay == "5.00"
        assert result.InitialMarginDisplay == "7,602.50"
        assert result.ProductCurrency == "USD"
        assert result.AccountCurrency == "USD"

    @pytest.mark.asyncio
    async def test_confirm_limit_order(self, order_execution_service, http_client_mock):
        """Test confirmation of a limit order"""
        # Mock response data
        mock_response = {
            "Route": "Intelligent",
            "Duration": "Day",
            "Account": "123456",
            "SummaryMessage": "Buy 100 MSFT Limit @ 150.00 Day",
            "EstimatedPrice": "150.00",
            "EstimatedPriceDisplay": "150.00",
            "EstimatedCommission": "5.00",
            "EstimatedCommissionDisplay": "5.00",
            "InitialMarginDisplay": "7,500.00",
            "ProductCurrency": "USD",
            "AccountCurrency": "USD",
        }

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
        assert isinstance(result, OrderConfirmationResponse)
        assert result.Route == "Intelligent"
        assert result.Duration == "Day"
        assert result.Account == "123456"
        assert result.SummaryMessage == "Buy 100 MSFT Limit @ 150.00 Day"
        assert result.EstimatedPrice == "150.00"
        assert result.EstimatedPriceDisplay == "150.00"
        assert result.EstimatedCommission == "5.00"
        assert result.EstimatedCommissionDisplay == "5.00"
        assert result.InitialMarginDisplay == "7,500.00"
        assert result.ProductCurrency == "USD"
        assert result.AccountCurrency == "USD"

    @pytest.mark.asyncio
    async def test_confirm_stop_order(self, order_execution_service, http_client_mock):
        """Test confirmation of a stop market order"""
        # Mock response data
        mock_response = {
            "Route": "Intelligent",
            "Duration": "Day",
            "Account": "123456",
            "SummaryMessage": "Sell 100 MSFT Stop @ 155.00 Day",
            "EstimatedPrice": "155.00",
            "EstimatedPriceDisplay": "155.00",
            "EstimatedCommission": "5.00",
            "EstimatedCommissionDisplay": "5.00",
            "InitialMarginDisplay": "0.00",
            "ProductCurrency": "USD",
            "AccountCurrency": "USD",
        }

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
        assert isinstance(result, OrderConfirmationResponse)
        assert result.Route == "Intelligent"
        assert result.Duration == "Day"
        assert result.Account == "123456"
        assert result.SummaryMessage == "Sell 100 MSFT Stop @ 155.00 Day"
        assert result.EstimatedPrice == "155.00"
        assert result.EstimatedPriceDisplay == "155.00"
        assert result.EstimatedCommission == "5.00"
        assert result.EstimatedCommissionDisplay == "5.00"
        assert result.InitialMarginDisplay == "0.00"
        assert result.ProductCurrency == "USD"
        assert result.AccountCurrency == "USD"

    @pytest.mark.asyncio
    async def test_confirm_order_validation_errors(self, order_execution_service, http_client_mock):
        """Test validation errors when confirming an order"""
        # Mock response with validation error
        mock_response = {
            "Route": "Intelligent",
            "Duration": "Day",
            "Account": "123456",
            "SummaryMessage": "Invalid order: Quantity must be greater than 0",
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

        # Verify the result
        assert isinstance(result, OrderConfirmationResponse)
        assert result.Route == "Intelligent"
        assert result.Duration == "Day"
        assert result.Account == "123456"
        assert result.SummaryMessage == "Invalid order: Quantity must be greater than 0"
        assert result.EstimatedPrice is None
        assert result.EstimatedPriceDisplay is None
        assert result.EstimatedCommission is None
        assert result.EstimatedCommissionDisplay is None
        assert result.InitialMarginDisplay is None

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

        # Verify that the exception is propagated
        with pytest.raises(Exception, match="Network error"):
            await order_execution_service.confirm_order(request)

        # Verify the API was called correctly
        http_client_mock.post.assert_called_once_with(
            "/v3/orderexecution/orderconfirm", request.model_dump(exclude_none=True)
        )

    @pytest.mark.asyncio
    async def test_confirm_order_unauthorized(self, order_execution_service, http_client_mock):
        """Test unauthorized error handling when confirming an order"""
        # Configure mock to raise an unauthorized exception
        http_client_mock.post.side_effect = Exception("Unauthorized")

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

        # Verify that the exception is propagated
        with pytest.raises(Exception, match="Unauthorized"):
            await order_execution_service.confirm_order(request)

        # Verify the API was called correctly
        http_client_mock.post.assert_called_once_with(
            "/v3/orderexecution/orderconfirm", request.model_dump(exclude_none=True)
        )
