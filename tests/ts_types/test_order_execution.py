"""Tests for the order execution types."""

import json
from datetime import datetime, timezone

import pytest

from src.ts_types.order_execution import (
    ActivationTrigger,
    ActivationTriggers,
    AdvancedOptions,
    CancelOrderResponse,
    GroupOrderConfirmationResponse,
    GroupOrderRequest,
    GroupOrderResponse,
    GroupOrderResponseError,
    GroupOrderResponseSuccess,
    GroupOrderType,
    GroupOrderConfirmationDetail,
    MarketActivationRule,
    OrderConfirmationResponse,
    OrderDuration,
    OrderLeg,
    OrderReplaceAdvancedOptions,
    OrderReplaceRequest,
    OrderReplaceTimeInForce,
    OrderReplaceTrailingStop,
    OrderRequest,
    OrderResponse,
    OrderResponseError,
    OrderResponseSuccess,
    OrderSide,
    OrderStatus,
    OrderType,
    OSO,
    Route,
    Routes,
    RoutesResponse,
    TimeActivationRule,
    TimeInForce,
    TrailingStop,
)


class TestOrderExecutionTypes:
    """Test class for order execution types."""

    def test_order_type_enum(self):
        """Test the OrderType enum."""
        assert OrderType.MARKET.value == "Market"
        assert OrderType.LIMIT.value == "Limit"
        assert OrderType.STOP_MARKET.value == "StopMarket"
        assert OrderType.STOP_LIMIT.value == "StopLimit"

    def test_order_duration_enum(self):
        """Test the OrderDuration enum."""
        assert OrderDuration.DAY.value == "DAY"
        assert OrderDuration.DYP.value == "DYP"
        assert OrderDuration.GTC.value == "GTC"
        assert OrderDuration.ONE_MINUTE.value == "1"
        assert OrderDuration.ONE_MINUTE_ALT.value == "1 MIN"

    def test_order_status_enum(self):
        """Test the OrderStatus enum."""
        assert OrderStatus.ACK.value == "ACK"
        assert OrderStatus.FLL.value == "FLL"
        assert OrderStatus.CAN.value == "CAN"
        assert OrderStatus.REJ.value == "REJ"

    def test_order_side_enum(self):
        """Test the OrderSide enum."""
        assert OrderSide.BUY.value == "BUY"
        assert OrderSide.SELL.value == "SELL"
        assert OrderSide.BUY_TO_COVER.value == "BUYTOCOVER"
        assert OrderSide.SELL_SHORT.value == "SELLSHORT"

    def test_market_activation_rule(self):
        """Test the MarketActivationRule model."""
        rule = MarketActivationRule(
            RuleType="Price", Symbol="AAPL", Predicate="Gt", TriggerKey="SBA", Price="150.00"
        )
        assert rule.RuleType == "Price"
        assert rule.Symbol == "AAPL"
        assert rule.Predicate == "Gt"
        assert rule.TriggerKey == "SBA"
        assert rule.Price == "150.00"
        assert rule.LogicOperator is None

        rule_with_logic = MarketActivationRule(
            RuleType="Price",
            Symbol="AAPL",
            Predicate="Gt",
            TriggerKey="SBA",
            Price="150.00",
            LogicOperator="And",
        )
        assert rule_with_logic.LogicOperator == "And"

    def test_time_activation_rule(self):
        """Test the TimeActivationRule model."""
        rule = TimeActivationRule(TimeUtc="2023-07-15T14:30:00Z")
        assert rule.TimeUtc == "2023-07-15T14:30:00Z"

    def test_trailing_stop(self):
        """Test the TrailingStop model."""
        ts = TrailingStop(Amount=2.5, IsPercentage=False)
        assert ts.Amount == 2.5
        assert ts.IsPercentage is False
        assert ts.Percent is None

        ts_with_percent = TrailingStop(Amount=0.0, IsPercentage=True, Percent=5.0)
        assert ts_with_percent.Amount == 0.0
        assert ts_with_percent.IsPercentage is True
        assert ts_with_percent.Percent == 5.0

    def test_advanced_options(self):
        """Test the AdvancedOptions model."""
        ts_dict = {"Amount": 2.5, "IsPercentage": False}
        rule = MarketActivationRule(
            RuleType="Price", Symbol="AAPL", Predicate="Gt", TriggerKey="SBA", Price="150.00"
        )
        time_rule = TimeActivationRule(TimeUtc="2023-07-15T14:30:00Z")

        options = AdvancedOptions(
            TrailingStop=ts_dict,
            MarketActivationRules=[rule],
            TimeActivationRules=[time_rule],
            CommissionFee=1.99,
            DoNotReduceFlag=True,
            AllOrNone=False,
            MinimumQuantity=100,
        )

        assert options.TrailingStop["Amount"] == 2.5
        assert options.TrailingStop["IsPercentage"] is False
        assert len(options.MarketActivationRules) == 1
        assert options.MarketActivationRules[0] == rule
        assert len(options.TimeActivationRules) == 1
        assert options.TimeActivationRules[0] == time_rule
        assert options.CommissionFee == 1.99
        assert options.DoNotReduceFlag is True
        assert options.AllOrNone is False
        assert options.MinimumQuantity == 100

    def test_order_leg(self):
        """Test the OrderLeg model."""
        leg = OrderLeg(Symbol="AAPL", Quantity=100, TradeAction=OrderSide.BUY)
        assert leg.Symbol == "AAPL"
        assert leg.Quantity == 100
        assert leg.TradeAction == OrderSide.BUY

    def test_time_in_force(self):
        """Test the TimeInForce model."""
        tif = TimeInForce(Duration=OrderDuration.DAY)
        assert tif.Duration == OrderDuration.DAY
        assert tif.ExpirationDate is None

        tif_with_expiration = TimeInForce(Duration=OrderDuration.GTD, ExpirationDate="2023-07-15")
        assert tif_with_expiration.Duration == OrderDuration.GTD
        assert tif_with_expiration.ExpirationDate == "2023-07-15"

    def test_order_request(self):
        """Test the OrderRequest model."""
        tif = TimeInForce(Duration=OrderDuration.DAY)

        order = OrderRequest(
            AccountID="12345",
            Symbol="AAPL",
            Quantity="100",
            OrderType=OrderType.LIMIT,
            TradeAction=OrderSide.BUY,
            TimeInForce=tif,
            Route="INET",
            LimitPrice="150.00",
        )

        assert order.AccountID == "12345"
        assert order.Symbol == "AAPL"
        assert order.Quantity == "100"
        assert order.OrderType == OrderType.LIMIT
        assert order.TradeAction == OrderSide.BUY
        assert order.TimeInForce == tif
        assert order.Route == "INET"
        assert order.LimitPrice == "150.00"
        assert order.StopPrice is None
        assert order.AdvancedOptions is None

    def test_order_response_success(self):
        """Test the OrderResponseSuccess model."""
        success = OrderResponseSuccess(OrderID="ORD123456", Message="Order placed successfully")
        assert success.OrderID == "ORD123456"
        assert success.Message == "Order placed successfully"

    def test_order_response_error(self):
        """Test the OrderResponseError model."""
        error = OrderResponseError(
            OrderID="ORD123456", Error="INVALID_PRICE", Message="The price specified is invalid"
        )
        assert error.OrderID == "ORD123456"
        assert error.Error == "INVALID_PRICE"
        assert error.Message == "The price specified is invalid"

    def test_order_response(self):
        """Test the OrderResponse model."""
        success = OrderResponseSuccess(OrderID="ORD123456", Message="Order placed successfully")

        response = OrderResponse(Orders=[success])
        assert len(response.Orders) == 1
        assert response.Orders[0] == success
        assert response.Errors is None

        error = OrderResponseError(
            OrderID="ORD789012", Error="INVALID_PRICE", Message="The price specified is invalid"
        )

        response_with_error = OrderResponse(Orders=[success], Errors=[error])
        assert len(response_with_error.Orders) == 1
        assert response_with_error.Orders[0] == success
        assert len(response_with_error.Errors) == 1
        assert response_with_error.Errors[0] == error

    def test_cancel_order_response(self):
        """Test the CancelOrderResponse model."""
        response = CancelOrderResponse(OrderID="ORD123456")
        assert response.OrderID == "ORD123456"
        assert response.Error is None
        assert response.Message is None

        response_with_error = CancelOrderResponse(
            OrderID="ORD123456",
            Error="ORDER_ALREADY_FILLED",
            Message="Cannot cancel an order that has already been filled",
        )
        assert response_with_error.OrderID == "ORD123456"
        assert response_with_error.Error == "ORDER_ALREADY_FILLED"
        assert response_with_error.Message == "Cannot cancel an order that has already been filled"

    def test_order_replace_trailing_stop(self):
        """Test the OrderReplaceTrailingStop model."""
        ts = OrderReplaceTrailingStop(Amount="2.50")
        assert ts.Amount == "2.50"
        assert ts.Percent is None

        ts_with_percent = OrderReplaceTrailingStop(Percent="5.0")
        assert ts_with_percent.Amount is None
        assert ts_with_percent.Percent == "5.0"

    def test_order_replace_advanced_options(self):
        """Test the OrderReplaceAdvancedOptions model."""
        ts = OrderReplaceTrailingStop(Amount="2.50")

        options = OrderReplaceAdvancedOptions(TrailingStop=ts)
        assert options.TrailingStop == ts

    def test_order_replace_time_in_force(self):
        """Test the OrderReplaceTimeInForce model."""
        tif = OrderReplaceTimeInForce(Duration=OrderDuration.DAY)
        assert tif.Duration == OrderDuration.DAY

    def test_order_replace_request(self):
        """Test the OrderReplaceRequest model."""
        replace_request = OrderReplaceRequest(Quantity="150", LimitPrice="155.00")
        assert replace_request.Quantity == "150"
        assert replace_request.LimitPrice == "155.00"
        assert replace_request.StopPrice is None
        assert replace_request.OrderType is None
        assert replace_request.TimeInForce is None
        assert replace_request.AdvancedOptions is None

        tif = OrderReplaceTimeInForce(Duration=OrderDuration.DAY)

        ts = OrderReplaceTrailingStop(Amount="2.50")

        options = OrderReplaceAdvancedOptions(TrailingStop=ts)

        complete_replace = OrderReplaceRequest(
            Quantity="150",
            LimitPrice="155.00",
            StopPrice="160.00",
            OrderType=OrderType.STOP_LIMIT,
            TimeInForce=tif,
            AdvancedOptions=options,
        )

        assert complete_replace.Quantity == "150"
        assert complete_replace.LimitPrice == "155.00"
        assert complete_replace.StopPrice == "160.00"
        assert complete_replace.OrderType == OrderType.STOP_LIMIT
        assert complete_replace.TimeInForce == tif
        assert complete_replace.AdvancedOptions == options

    def test_order_confirmation_response(self):
        """Test the OrderConfirmationResponse model."""
        response = OrderConfirmationResponse(
            Route="INET", Duration="DAY", Account="12345", SummaryMessage="Order confirmed"
        )
        assert response.Route == "INET"
        assert response.Duration == "DAY"
        assert response.Account == "12345"
        assert response.SummaryMessage == "Order confirmed"
        assert response.EstimatedPrice is None
        assert response.EstimatedPriceDisplay is None
        assert response.EstimatedCommission is None
        assert response.EstimatedCommissionDisplay is None
        assert response.InitialMarginDisplay is None
        assert response.ProductCurrency is None
        assert response.AccountCurrency is None

        complete_response = OrderConfirmationResponse(
            Route="INET",
            Duration="DAY",
            Account="12345",
            SummaryMessage="Order confirmed",
            EstimatedPrice="150.00",
            EstimatedPriceDisplay="$150.00",
            EstimatedCommission="1.99",
            EstimatedCommissionDisplay="$1.99",
            InitialMarginDisplay="$0.00",
            ProductCurrency="USD",
            AccountCurrency="USD",
        )

        assert complete_response.EstimatedPrice == "150.00"
        assert complete_response.EstimatedPriceDisplay == "$150.00"
        assert complete_response.EstimatedCommission == "1.99"
        assert complete_response.EstimatedCommissionDisplay == "$1.99"
        assert complete_response.InitialMarginDisplay == "$0.00"
        assert complete_response.ProductCurrency == "USD"
        assert complete_response.AccountCurrency == "USD"

    def test_group_order_type_enum(self):
        """Test the GroupOrderType enum."""
        assert GroupOrderType.BRK.value == "BRK"
        assert GroupOrderType.OCO.value == "OCO"
        assert GroupOrderType.NORMAL.value == "NORMAL"

    def test_group_order_request(self):
        """Test the GroupOrderRequest model."""
        tif = TimeInForce(Duration=OrderDuration.DAY)

        order1 = OrderRequest(
            AccountID="12345",
            Symbol="AAPL",
            Quantity="100",
            OrderType=OrderType.LIMIT,
            TradeAction=OrderSide.BUY,
            TimeInForce=tif,
            Route="INET",
            LimitPrice="150.00",
        )

        order2 = OrderRequest(
            AccountID="12345",
            Symbol="AAPL",
            Quantity="100",
            OrderType=OrderType.STOP_MARKET,
            TradeAction=OrderSide.SELL,
            TimeInForce=tif,
            Route="INET",
            StopPrice="140.00",
        )

        group_order = GroupOrderRequest(Type="OCO", Orders=[order1, order2])

        assert group_order.Type == "OCO"
        assert len(group_order.Orders) == 2
        assert group_order.Orders[0] == order1
        assert group_order.Orders[1] == order2

    def test_activation_trigger(self):
        """Test the ActivationTrigger model."""
        trigger = ActivationTrigger(
            Key="SBA",
            Name="Stock Bid Ask",
            Description="Triggers when the stock bid or ask meets the condition",
        )
        assert trigger.Key == "SBA"
        assert trigger.Name == "Stock Bid Ask"
        assert trigger.Description == "Triggers when the stock bid or ask meets the condition"

    def test_activation_triggers(self):
        """Test the ActivationTriggers model."""
        trigger = ActivationTrigger(
            Key="SBA",
            Name="Stock Bid Ask",
            Description="Triggers when the stock bid or ask meets the condition",
        )

        triggers = ActivationTriggers(ActivationTriggers=[trigger])

        assert len(triggers.ActivationTriggers) == 1
        assert triggers.ActivationTriggers[0] == trigger

    def test_route(self):
        """Test the Route model."""
        route = Route(Id="INET", Name="INET", AssetTypes=["STOCK", "STOCKOPTION"])
        assert route.Id == "INET"
        assert route.Name == "INET"
        assert route.AssetTypes == ["STOCK", "STOCKOPTION"]

    def test_routes(self):
        """Test the Routes model."""
        route = Route(Id="INET", Name="INET", AssetTypes=["STOCK", "STOCKOPTION"])

        routes = Routes(Routes=[route])

        assert len(routes.Routes) == 1
        assert routes.Routes[0] == route

    def test_group_order_response_success(self):
        """Test the GroupOrderResponseSuccess model."""
        success = GroupOrderResponseSuccess(
            OrderID="ORD123456", Message="Order placed successfully"
        )
        assert success.OrderID == "ORD123456"
        assert success.Message == "Order placed successfully"

    def test_group_order_response_error(self):
        """Test the GroupOrderResponseError model."""
        error = GroupOrderResponseError(
            OrderID="ORD123456", Error="INVALID_PRICE", Message="The price specified is invalid"
        )
        assert error.OrderID == "ORD123456"
        assert error.Error == "INVALID_PRICE"
        assert error.Message == "The price specified is invalid"

    def test_group_order_response(self):
        """Test the GroupOrderResponse model."""
        success = GroupOrderResponseSuccess(
            OrderID="ORD123456", Message="Order placed successfully"
        )

        response = GroupOrderResponse(Orders=[success])
        assert len(response.Orders) == 1
        assert response.Orders[0] == success
        assert response.Errors is None

        error = GroupOrderResponseError(
            OrderID="ORD789012", Error="INVALID_PRICE", Message="The price specified is invalid"
        )

        response_with_error = GroupOrderResponse(Orders=[success], Errors=[error])
        assert len(response_with_error.Orders) == 1
        assert response_with_error.Orders[0] == success
        assert len(response_with_error.Errors) == 1
        assert response_with_error.Errors[0] == error

    def test_group_order_confirmation_response(self):
        """Test the GroupOrderConfirmationResponse model."""
        # Use the new GroupOrderConfirmationDetail model for the items
        # Adjust the mock data to match the fields in GroupOrderConfirmationDetail
        detail1 = GroupOrderConfirmationDetail(
            OrderConfirmID="CONFIRM1",
            SummaryMessage="First leg confirmed",
            EstimatedCost="100.00",
            # Add other relevant fields if needed for assertion
        )
        detail2 = GroupOrderConfirmationDetail(
            OrderConfirmID="CONFIRM2",
            SummaryMessage="Second leg confirmed",
            EstimatedCost="200.00",
        )
        error = GroupOrderResponseError(
            OrderID="ERROR1", Error="Some Error", Message="Something went wrong"
        )

        # Initialize with Confirmations list using the new detail model
        response = GroupOrderConfirmationResponse(Confirmations=[detail1, detail2], Errors=[error])

        assert len(response.Confirmations) == 2
        assert response.Confirmations[0].OrderConfirmID == "CONFIRM1"
        assert response.Confirmations[0].SummaryMessage == "First leg confirmed"
        assert response.Confirmations[1].OrderConfirmID == "CONFIRM2"
        assert response.Confirmations[1].SummaryMessage == "Second leg confirmed"
        assert len(response.Errors) == 1
        assert response.Errors[0].OrderID == "ERROR1"

        # Test with empty Confirmations
        response_no_confirm = GroupOrderConfirmationResponse(Confirmations=[], Errors=[error])
        assert len(response_no_confirm.Confirmations) == 0
        assert len(response_no_confirm.Errors) == 1

        # Test with empty Errors
        response_no_error = GroupOrderConfirmationResponse(Confirmations=[detail1])
        assert len(response_no_error.Confirmations) == 1
        assert response_no_error.Errors is None

    def test_routes_response(self):
        """Test the RoutesResponse model."""
        route = Route(Id="INET", Name="INET", AssetTypes=["STOCK", "STOCKOPTION"])

        response = RoutesResponse(Routes=[route])

        assert len(response.Routes) == 1
        assert response.Routes[0] == route

    def test_oso(self):
        """Test the OSO model."""
        tif = TimeInForce(Duration=OrderDuration.DAY)

        order1 = OrderRequest(
            AccountID="12345",
            Symbol="AAPL",
            Quantity="100",
            OrderType=OrderType.LIMIT,
            TradeAction=OrderSide.BUY,
            TimeInForce=tif,
            Route="INET",
            LimitPrice="150.00",
        )

        order2 = OrderRequest(
            AccountID="12345",
            Symbol="AAPL",
            Quantity="100",
            OrderType=OrderType.STOP_MARKET,
            TradeAction=OrderSide.SELL,
            TimeInForce=tif,
            Route="INET",
            StopPrice="140.00",
        )

        oso = OSO(Type="BRK", Orders=[order1, order2])

        assert oso.Type == "BRK"
        assert len(oso.Orders) == 2
        assert oso.Orders[0] == order1
        assert oso.Orders[1] == order2
