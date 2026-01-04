import pytest

from tradestation.ts_types.order_execution import (
    OrderDuration,
    OrderRequest,
    OrderResponse,
    OrderResponseError,
    OrderResponseSuccess,
    OrderSide,
    OrderType,
    TimeInForce,
)


class TestPlaceOrder:
    """Tests for the place_order method in OrderExecutionService"""

    @pytest.mark.asyncio
    async def test_place_order_success(self, order_execution_service, http_client_mock):
        """Test successful placement of a simple market order"""
        # Create market order request
        request = OrderRequest(
            AccountID="ACCT123",
            Symbol="MSFT",
            Quantity="10",
            OrderType=OrderType.MARKET,
            TradeAction=OrderSide.BUY,
            TimeInForce=TimeInForce(Duration=OrderDuration.DAY),
            Route="Intelligent",
        )

        # Mock response data
        mock_response = {
            "Orders": [{"OrderID": "ORDER123", "Message": "Order placed successfully"}]
        }

        # Configure mock
        http_client_mock.post.return_value = mock_response

        # Call the method
        result = await order_execution_service.place_order(request)

        # Verify the API was called correctly
        http_client_mock.post.assert_called_once_with(
            "/v3/orderexecution/orders",
            {
                "AccountID": "ACCT123",
                "Symbol": "MSFT",
                "Quantity": "10",
                "OrderType": "Market",
                "TradeAction": "BUY",
                "TimeInForce": {"Duration": "DAY"},
                "Route": "Intelligent",
            },
        )

        # Verify the result
        assert isinstance(result, OrderResponse)
        assert isinstance(result.Orders, list)
        assert len(result.Orders) == 1
        assert isinstance(result.Orders[0], OrderResponseSuccess)
        assert result.Orders[0].OrderID == "ORDER123"
        assert result.Orders[0].Message == "Order placed successfully"
        assert result.Errors is None

    @pytest.mark.asyncio
    async def test_place_limit_order_success(self, order_execution_service, http_client_mock):
        """Test successful placement of a limit order"""
        # Create limit order request
        request = OrderRequest(
            AccountID="ACCT123",
            Symbol="AAPL",
            Quantity="5",
            OrderType=OrderType.LIMIT,
            TradeAction=OrderSide.BUY,
            TimeInForce=TimeInForce(Duration=OrderDuration.GTC),
            Route="Intelligent",
            LimitPrice="150.25",
        )

        # Mock response data
        mock_response = {
            "Orders": [{"OrderID": "ORDER456", "Message": "Limit order placed successfully"}]
        }

        # Configure mock
        http_client_mock.post.return_value = mock_response

        # Call the method
        result = await order_execution_service.place_order(request)

        # Verify the API was called correctly
        http_client_mock.post.assert_called_once_with(
            "/v3/orderexecution/orders",
            {
                "AccountID": "ACCT123",
                "Symbol": "AAPL",
                "Quantity": "5",
                "OrderType": "Limit",
                "TradeAction": "BUY",
                "TimeInForce": {"Duration": "GTC"},
                "Route": "Intelligent",
                "LimitPrice": "150.25",
            },
        )

        # Verify the result
        assert isinstance(result, OrderResponse)
        assert isinstance(result.Orders, list)
        assert len(result.Orders) == 1
        assert result.Orders[0].OrderID == "ORDER456"
        assert result.Orders[0].Message == "Limit order placed successfully"

    @pytest.mark.asyncio
    async def test_place_stop_market_order_success(self, order_execution_service, http_client_mock):
        """Test successful placement of a stop market order"""
        # Create stop market order request
        request = OrderRequest(
            AccountID="ACCT123",
            Symbol="TSLA",
            Quantity="2",
            OrderType=OrderType.STOP_MARKET,
            TradeAction=OrderSide.SELL,
            TimeInForce=TimeInForce(Duration=OrderDuration.DAY),
            Route="Intelligent",
            StopPrice="700.50",
        )

        # Mock response data
        mock_response = {
            "Orders": [{"OrderID": "ORDER789", "Message": "Stop market order placed successfully"}]
        }

        # Configure mock
        http_client_mock.post.return_value = mock_response

        # Call the method
        result = await order_execution_service.place_order(request)

        # Verify the API was called correctly
        http_client_mock.post.assert_called_once_with(
            "/v3/orderexecution/orders",
            {
                "AccountID": "ACCT123",
                "Symbol": "TSLA",
                "Quantity": "2",
                "OrderType": "StopMarket",
                "TradeAction": "SELL",
                "TimeInForce": {"Duration": "DAY"},
                "Route": "Intelligent",
                "StopPrice": "700.50",
            },
        )

        # Verify the result
        assert isinstance(result, OrderResponse)
        assert isinstance(result.Orders, list)
        assert len(result.Orders) == 1
        assert result.Orders[0].OrderID == "ORDER789"
        assert result.Orders[0].Message == "Stop market order placed successfully"

    @pytest.mark.asyncio
    async def test_place_order_partial_error(self, order_execution_service, http_client_mock):
        """Test placement of an order with partial error response"""
        # Create order request
        request = OrderRequest(
            AccountID="ACCT123",
            Symbol="MSFT",
            Quantity="10",
            OrderType=OrderType.MARKET,
            TradeAction=OrderSide.BUY,
            TimeInForce=TimeInForce(Duration=OrderDuration.DAY),
            Route="Intelligent",
        )

        # Mock response data with both success and errors
        mock_response = {
            "Orders": [{"OrderID": "ORDER123", "Message": "Order partially processed"}],
            "Errors": [
                {
                    "OrderID": "ORDER123",
                    "Error": "PARTIAL_EXECUTION",
                    "Message": "Order was only partially executed",
                }
            ],
        }

        # Configure mock
        http_client_mock.post.return_value = mock_response

        # Call the method
        result = await order_execution_service.place_order(request)

        # Verify the API was called correctly
        http_client_mock.post.assert_called_once_with(
            "/v3/orderexecution/orders",
            {
                "AccountID": "ACCT123",
                "Symbol": "MSFT",
                "Quantity": "10",
                "OrderType": "Market",
                "TradeAction": "BUY",
                "TimeInForce": {"Duration": "DAY"},
                "Route": "Intelligent",
            },
        )

        # Verify the result
        assert isinstance(result, OrderResponse)
        assert isinstance(result.Orders, list)
        assert len(result.Orders) == 1
        assert result.Orders[0].OrderID == "ORDER123"
        assert result.Orders[0].Message == "Order partially processed"

        assert isinstance(result.Errors, list)
        assert len(result.Errors) == 1
        assert isinstance(result.Errors[0], OrderResponseError)
        assert result.Errors[0].OrderID == "ORDER123"
        assert result.Errors[0].Error == "PARTIAL_EXECUTION"
        assert result.Errors[0].Message == "Order was only partially executed"

    @pytest.mark.asyncio
    async def test_place_order_validation_error(self, order_execution_service, http_client_mock):
        """Test order validation error handling"""
        # Create order request
        request = OrderRequest(
            AccountID="ACCT123",
            Symbol="INVALID",
            Quantity="10",
            OrderType=OrderType.MARKET,
            TradeAction=OrderSide.BUY,
            TimeInForce=TimeInForce(Duration=OrderDuration.DAY),
            Route="Intelligent",
        )

        # Mock response data with only errors
        mock_response = {
            "Orders": [],
            "Errors": [
                {
                    "OrderID": "",
                    "Error": "INVALID_SYMBOL",
                    "Message": "The symbol INVALID is not valid",
                }
            ],
        }

        # Configure mock
        http_client_mock.post.return_value = mock_response

        # Call the method
        result = await order_execution_service.place_order(request)

        # Verify the API was called correctly
        http_client_mock.post.assert_called_once_with(
            "/v3/orderexecution/orders",
            {
                "AccountID": "ACCT123",
                "Symbol": "INVALID",
                "Quantity": "10",
                "OrderType": "Market",
                "TradeAction": "BUY",
                "TimeInForce": {"Duration": "DAY"},
                "Route": "Intelligent",
            },
        )

        # Verify the result
        assert isinstance(result, OrderResponse)
        assert isinstance(result.Orders, list)
        assert len(result.Orders) == 0

        assert isinstance(result.Errors, list)
        assert len(result.Errors) == 1
        assert isinstance(result.Errors[0], OrderResponseError)
        assert result.Errors[0].OrderID == ""
        assert result.Errors[0].Error == "INVALID_SYMBOL"
        assert result.Errors[0].Message == "The symbol INVALID is not valid"

    @pytest.mark.asyncio
    async def test_place_order_network_error(self, order_execution_service, http_client_mock):
        """Test network error handling when placing an order"""
        # Create order request
        request = OrderRequest(
            AccountID="ACCT123",
            Symbol="MSFT",
            Quantity="10",
            OrderType=OrderType.MARKET,
            TradeAction=OrderSide.BUY,
            TimeInForce=TimeInForce(Duration=OrderDuration.DAY),
            Route="Intelligent",
        )

        # Configure mock to raise exception
        http_client_mock.post.side_effect = Exception("Network error")

        # Verify the exception is propagated
        with pytest.raises(Exception, match="Network error"):
            await order_execution_service.place_order(request)

        # Verify the API was called correctly
        http_client_mock.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_place_order_unauthorized(self, order_execution_service, http_client_mock):
        """Test unauthorized error handling when placing an order"""
        # Create order request
        request = OrderRequest(
            AccountID="ACCT123",
            Symbol="MSFT",
            Quantity="10",
            OrderType=OrderType.MARKET,
            TradeAction=OrderSide.BUY,
            TimeInForce=TimeInForce(Duration=OrderDuration.DAY),
            Route="Intelligent",
        )

        # Configure mock to raise unauthorized exception
        http_client_mock.post.side_effect = Exception("Unauthorized")

        # Verify the exception is propagated
        with pytest.raises(Exception, match="Unauthorized"):
            await order_execution_service.place_order(request)

        # Verify the API was called correctly
        http_client_mock.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_place_order_rate_limit(self, order_execution_service, http_client_mock):
        """Test rate limit error handling when placing an order"""
        # Create order request
        request = OrderRequest(
            AccountID="ACCT123",
            Symbol="MSFT",
            Quantity="10",
            OrderType=OrderType.MARKET,
            TradeAction=OrderSide.BUY,
            TimeInForce=TimeInForce(Duration=OrderDuration.DAY),
            Route="Intelligent",
        )

        # Configure mock to raise rate limit exception
        http_client_mock.post.side_effect = Exception("Rate limit exceeded")

        # Verify the exception is propagated
        with pytest.raises(Exception, match="Rate limit exceeded"):
            await order_execution_service.place_order(request)

        # Verify the API was called correctly
        http_client_mock.post.assert_called_once()
