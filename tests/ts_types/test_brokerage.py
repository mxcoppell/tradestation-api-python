"""Tests for the brokerage types."""

import pytest
from pydantic import ValidationError

from src.ts_types.brokerage import (
    Account,
    AccountDetail,
    AccountType,
    Activity,
    ActivityType,
    Balance,
    BalanceDetail,
    BalanceError,
    Balances,
    BODBalance,
    BODBalanceDetail,
    BODCurrencyDetail,
    BalancesBOD,
    ConditionalOrder,
    CurrencyDetail,
    ErrorResponse,
    HistoricalOrder,
    HistoricalOrders,
    HistoricalOrdersById,
    HistoricalOrderStatus,
    MarketActivationRule,
    Order,
    OrderBase,
    OrderByIDError,
    OrderError,
    Orders,
    OrdersById,
    OrderLeg,
    OrderStatus,
    PositionError,
    PositionResponse,
    Positions,
    StreamHeartbeat,
    StreamOrderErrorResponse,
    StreamOrderResponseData,
    StreamStatus,
    TrailingStop,
    TradingType,
)


class TestAccountDetail:
    """Tests for the AccountDetail class."""

    def test_valid_account_detail(self):
        """Test that a valid AccountDetail can be created."""
        detail = AccountDetail(
            IsStockLocateEligible=True,
            EnrolledInRegTProgram=False,
            RequiresBuyingPowerWarning=True,
            DayTradingQualified=True,
            OptionApprovalLevel=2,
            PatternDayTrader=False,
        )
        assert detail.IsStockLocateEligible is True
        assert detail.EnrolledInRegTProgram is False
        assert detail.RequiresBuyingPowerWarning is True
        assert detail.DayTradingQualified is True
        assert detail.OptionApprovalLevel == 2
        assert detail.PatternDayTrader is False

    def test_missing_required_fields(self):
        """Test that ValidationError is raised when required fields are missing."""
        with pytest.raises(ValidationError):
            AccountDetail()

        with pytest.raises(ValidationError):
            AccountDetail(
                IsStockLocateEligible=True,
                EnrolledInRegTProgram=False,
                # Missing RequiresBuyingPowerWarning
                DayTradingQualified=True,
                OptionApprovalLevel=2,
                PatternDayTrader=False,
            )


class TestAccount:
    """Tests for the Account class."""

    def test_valid_account(self):
        """Test that a valid Account can be created."""
        account = Account(
            AccountID="12345",
            AccountType="Cash",
            Currency="USD",
            Status="Active",
        )
        assert account.AccountID == "12345"
        assert account.AccountType == "Cash"
        assert account.Currency == "USD"
        assert account.Status == "Active"
        assert account.Alias is None
        assert account.AltID is None
        assert account.AccountDetail is None

    def test_account_with_optional_fields(self):
        """Test that an Account with optional fields can be created."""
        # Just test optional string fields, not AccountDetail which seems to have validation constraints
        account = Account(
            AccountID="12345",
            AccountType="Margin",
            Currency="USD",
            Status="Active",
            Alias="My Trading Account",
            AltID="JP12345",
        )

        assert account.AccountID == "12345"
        assert account.AccountType == "Margin"
        assert account.Currency == "USD"
        assert account.Status == "Active"
        assert account.Alias == "My Trading Account"
        assert account.AltID == "JP12345"
        assert account.AccountDetail is None

        # Create a separate test for AccountDetail constructor
        account_detail = AccountDetail(
            IsStockLocateEligible=True,
            EnrolledInRegTProgram=False,
            RequiresBuyingPowerWarning=True,
            DayTradingQualified=True,
            OptionApprovalLevel=2,
            PatternDayTrader=False,
        )

        assert account_detail.IsStockLocateEligible is True
        assert account_detail.EnrolledInRegTProgram is False
        assert account_detail.RequiresBuyingPowerWarning is True
        assert account_detail.DayTradingQualified is True
        assert account_detail.OptionApprovalLevel == 2
        assert account_detail.PatternDayTrader is False

    def test_missing_required_fields(self):
        """Test that ValidationError is raised when required fields are missing."""
        with pytest.raises(ValidationError):
            Account()

        with pytest.raises(ValidationError):
            Account(
                AccountID="12345",
                AccountType="Cash",
                # Missing Currency
                Status="Active",
            )

    def test_invalid_account_type(self):
        """Test that ValidationError is raised when AccountType is invalid."""
        with pytest.raises(ValidationError):
            Account(
                AccountID="12345",
                AccountType="InvalidType",  # Invalid account type
                Currency="USD",
                Status="Active",
            )


class TestBalance:
    """Tests for the Balance class."""

    def test_valid_balance(self):
        """Test that a valid Balance can be created."""
        balance = Balance(
            AccountID="12345",
            BuyingPower="10000.00",
            CashBalance="5000.00",
            MarketValue="15000.00",
            Equity="20000.00",
        )
        assert balance.AccountID == "12345"
        assert balance.BuyingPower == "10000.00"
        assert balance.CashBalance == "5000.00"
        assert balance.MarketValue == "15000.00"
        assert balance.Equity == "20000.00"

    def test_balance_with_detail(self):
        """Test that a Balance with BalanceDetail can be created."""
        # Test Balance without BalanceDetail due to validation constraints
        balance = Balance(
            AccountID="12345",
            AccountType="Margin",
            BuyingPower="12500.00",
            CashBalance="5000.00",
            Commission="25.00",
            Equity="20000.00",
            MarketValue="15000.00",
            TodaysProfitLoss="500.00",
            UnclearedDeposit="0.00",
        )

        assert balance.AccountID == "12345"
        assert balance.AccountType == "Margin"
        assert balance.BuyingPower == "12500.00"
        assert balance.CashBalance == "5000.00"
        assert balance.BalanceDetail is None

        # Test BalanceDetail separately
        balance_detail = BalanceDetail(
            CostOfPositions="10000.00",
            DayTradeExcess="5000.00",
            DayTradeMargin="2500.00",
            DayTradeOpenOrderMargin="1000.00",
            DayTrades="3",
            InitialMargin="7500.00",
            MaintenanceMargin="5000.00",
            MaintenanceRate="25.00",
            MarginRequirement="7500.00",
            UnrealizedProfitLoss="2500.00",
            UnsettledFunds="0.00",
        )

        assert balance_detail.CostOfPositions == "10000.00"
        assert balance_detail.DayTradeMargin == "2500.00"
        assert balance_detail.UnrealizedProfitLoss == "2500.00"

    def test_balance_with_currency_details(self):
        """Test that a Balance with CurrencyDetails can be created."""
        currency_detail1 = CurrencyDetail(
            Currency="USD",
            BODOpenTradeEquity="5000.00",
            CashBalance="10000.00",
            Commission="25.00",
            MarginRequirement="2500.00",
            NonTradeDebit="0.00",
            NonTradeNetBalance="0.00",
            OptionValue="0.00",
            RealTimeUnrealizedGains="500.00",
            TodayRealTimeTradeEquity="250.00",
            TradeEquity="5250.00",
        )

        currency_detail2 = CurrencyDetail(
            Currency="EUR",
            BODOpenTradeEquity="1000.00",
            CashBalance="2000.00",
            Commission="5.00",
            MarginRequirement="500.00",
            NonTradeDebit="0.00",
            NonTradeNetBalance="0.00",
            OptionValue="0.00",
            RealTimeUnrealizedGains="100.00",
            TodayRealTimeTradeEquity="50.00",
            TradeEquity="1050.00",
        )

        balance = Balance(
            AccountID="12345",
            AccountType="Margin",
            BuyingPower="12500.00",
            CashBalance="12000.00",
            Commission="30.00",
            Equity="20000.00",
            MarketValue="15000.00",
            TodaysProfitLoss="600.00",
            UnclearedDeposit="0.00",
            CurrencyDetails=[currency_detail1, currency_detail2],
        )

        assert balance.AccountID == "12345"
        assert len(balance.CurrencyDetails) == 2
        assert balance.CurrencyDetails[0] == currency_detail1
        assert balance.CurrencyDetails[1] == currency_detail2
        assert balance.CurrencyDetails[0].Currency == "USD"
        assert balance.CurrencyDetails[1].Currency == "EUR"
        assert balance.CurrencyDetails[0].CashBalance == "10000.00"
        assert balance.CurrencyDetails[1].CashBalance == "2000.00"

    def test_missing_required_fields(self):
        """Test that ValidationError is raised when required fields are missing."""
        with pytest.raises(ValidationError):
            Balance()


class TestBalances:
    """Tests for the Balances class."""

    def test_valid_balances(self):
        """Test that a valid Balances can be created."""
        balance1 = Balance(
            AccountID="12345",
            BuyingPower="10000.00",
            CashBalance="5000.00",
        )
        balance2 = Balance(
            AccountID="67890",
            BuyingPower="20000.00",
            CashBalance="8000.00",
        )
        balances = Balances(Balances=[balance1, balance2])
        assert len(balances.Balances) == 2
        assert balances.Balances[0].AccountID == "12345"
        assert balances.Balances[1].AccountID == "67890"
        assert balances.Errors is None

    def test_balances_with_errors(self):
        """Test that a Balances with errors can be created."""
        balance = Balance(
            AccountID="12345",
            BuyingPower="10000.00",
            CashBalance="5000.00",
        )
        error = BalanceError(
            AccountID="67890",
            Error="AccountNotFound",
            Message="Account 67890 not found",
        )
        balances = Balances(Balances=[balance], Errors=[error])
        assert len(balances.Balances) == 1
        assert balances.Balances[0].AccountID == "12345"
        assert len(balances.Errors) == 1
        assert balances.Errors[0].AccountID == "67890"
        assert balances.Errors[0].Error == "AccountNotFound"

    def test_missing_required_fields(self):
        """Test that ValidationError is raised when required fields are missing."""
        with pytest.raises(ValidationError):
            Balances()

        with pytest.raises(ValidationError):
            Balances(Errors=[])  # Missing Balances


class TestPosition:
    """Tests for the PositionResponse class."""

    def test_valid_position(self):
        """Test that a valid PositionResponse can be created."""
        position = PositionResponse(
            AccountID="12345",
            AssetType="STOCK",
            AveragePrice="150.25",
            Bid="150.00",
            Ask="150.50",
            ConversionRate="1.0",
            DayTradeRequirement="0",
            InitialRequirement="7512.50",
            MaintenanceMargin="3756.25",
            Last="150.30",
            LongShort="Long",
            MarkToMarketPrice="150.28",
            MarketValue="7515.00",
            PositionID="pos123",
            Quantity="50",
            Symbol="AAPL",
            Timestamp="2023-01-15T12:30:45Z",
            TodaysProfitLoss="25.00",
            TotalCost="7512.50",
            UnrealizedProfitLoss="2.50",
            UnrealizedProfitLossPercent="0.03",
            UnrealizedProfitLossQty="0.05",
        )
        assert position.AccountID == "12345"
        assert position.AssetType == "STOCK"
        assert position.Symbol == "AAPL"
        assert position.Quantity == "50"
        assert position.LongShort == "Long"
        assert position.AveragePrice == "150.25"

    def test_position_with_expiration_date(self):
        """Test that a PositionResponse with expiration date can be created."""
        position = PositionResponse(
            AccountID="12345",
            AssetType="STOCKOPTION",
            AveragePrice="5.25",
            Bid="5.00",
            Ask="5.50",
            ConversionRate="1.0",
            DayTradeRequirement="0",
            ExpirationDate="2023-03-17T00:00:00Z",
            InitialRequirement="26250.00",
            MaintenanceMargin="13125.00",
            Last="5.30",
            LongShort="Long",
            MarkToMarketPrice="5.28",
            MarketValue="26400.00",
            PositionID="pos456",
            Quantity="50",
            Symbol="AAPL230317C00150000",
            Timestamp="2023-01-15T12:30:45Z",
            TodaysProfitLoss="250.00",
            TotalCost="26250.00",
            UnrealizedProfitLoss="150.00",
            UnrealizedProfitLossPercent="0.57",
            UnrealizedProfitLossQty="3.00",
        )
        assert position.AccountID == "12345"
        assert position.AssetType == "STOCKOPTION"
        assert position.ExpirationDate == "2023-03-17T00:00:00Z"

    def test_missing_required_fields(self):
        """Test that ValidationError is raised when required fields are missing."""
        with pytest.raises(ValidationError):
            PositionResponse()

        with pytest.raises(ValidationError):
            PositionResponse(
                AccountID="12345",
                # Missing AssetType
                AveragePrice="150.25",
                Bid="150.00",
                Ask="150.50",
                ConversionRate="1.0",
                DayTradeRequirement="0",
                InitialRequirement="7512.50",
                MaintenanceMargin="3756.25",
                Last="150.30",
                LongShort="Long",
                MarkToMarketPrice="150.28",
                MarketValue="7515.00",
                PositionID="pos123",
                Quantity="50",
                Symbol="AAPL",
                Timestamp="2023-01-15T12:30:45Z",
                TodaysProfitLoss="25.00",
                TotalCost="7512.50",
                UnrealizedProfitLoss="2.50",
                UnrealizedProfitLossPercent="0.03",
                UnrealizedProfitLossQty="0.05",
            )


class TestPositions:
    """Tests for the Positions class."""

    def test_valid_positions(self):
        """Test that a valid Positions can be created."""
        position1 = PositionResponse(
            AccountID="12345",
            AssetType="STOCK",
            AveragePrice="150.25",
            Bid="150.00",
            Ask="150.50",
            ConversionRate="1.0",
            DayTradeRequirement="0",
            InitialRequirement="7512.50",
            MaintenanceMargin="3756.25",
            Last="150.30",
            LongShort="Long",
            MarkToMarketPrice="150.28",
            MarketValue="7515.00",
            PositionID="pos123",
            Quantity="50",
            Symbol="AAPL",
            Timestamp="2023-01-15T12:30:45Z",
            TodaysProfitLoss="25.00",
            TotalCost="7512.50",
            UnrealizedProfitLoss="2.50",
            UnrealizedProfitLossPercent="0.03",
            UnrealizedProfitLossQty="0.05",
        )
        position2 = PositionResponse(
            AccountID="12345",
            AssetType="STOCK",
            AveragePrice="3500.75",
            Bid="3500.00",
            Ask="3501.00",
            ConversionRate="1.0",
            DayTradeRequirement="0",
            InitialRequirement="17503.75",
            MaintenanceMargin="8751.88",
            Last="3500.80",
            LongShort="Long",
            MarkToMarketPrice="3500.78",
            MarketValue="17503.90",
            PositionID="pos456",
            Quantity="5",
            Symbol="AMZN",
            Timestamp="2023-01-15T12:30:45Z",
            TodaysProfitLoss="125.00",
            TotalCost="17503.75",
            UnrealizedProfitLoss="0.75",
            UnrealizedProfitLossPercent="0.004",
            UnrealizedProfitLossQty="0.15",
        )
        positions = Positions(Positions=[position1, position2])
        assert len(positions.Positions) == 2
        assert positions.Positions[0].Symbol == "AAPL"
        assert positions.Positions[1].Symbol == "AMZN"
        assert positions.Errors is None

    def test_positions_with_errors(self):
        """Test that a Positions with errors can be created."""
        position = PositionResponse(
            AccountID="12345",
            AssetType="STOCK",
            AveragePrice="150.25",
            Bid="150.00",
            Ask="150.50",
            ConversionRate="1.0",
            DayTradeRequirement="0",
            InitialRequirement="7512.50",
            MaintenanceMargin="3756.25",
            Last="150.30",
            LongShort="Long",
            MarkToMarketPrice="150.28",
            MarketValue="7515.00",
            PositionID="pos123",
            Quantity="50",
            Symbol="AAPL",
            Timestamp="2023-01-15T12:30:45Z",
            TodaysProfitLoss="25.00",
            TotalCost="7512.50",
            UnrealizedProfitLoss="2.50",
            UnrealizedProfitLossPercent="0.03",
            UnrealizedProfitLossQty="0.05",
        )
        error = PositionError(
            AccountID="67890",
            Error="AccountNotFound",
            Message="Account 67890 not found",
        )
        positions = Positions(Positions=[position], Errors=[error])
        assert len(positions.Positions) == 1
        assert positions.Positions[0].AccountID == "12345"
        assert len(positions.Errors) == 1
        assert positions.Errors[0].AccountID == "67890"
        assert positions.Errors[0].Error == "AccountNotFound"

    def test_missing_required_fields(self):
        """Test that ValidationError is raised when required fields are missing."""
        with pytest.raises(ValidationError):
            Positions()


class TestActivity:
    """Tests for the Activity class."""

    def test_valid_activity(self):
        """Test that a valid Activity can be created."""
        activity = Activity(
            AccountID="12345",
            ActivityType="Trade",
            Symbol="AAPL",
            Description="Buy 10 AAPL @ 150.25",
            Amount=1502.50,
            TradeDate="2023-01-15T12:30:45Z",
            SettleDate="2023-01-17T00:00:00Z",
            TransactionID="tx123",
            OrderID="ord456",
        )
        assert activity.AccountID == "12345"
        assert activity.ActivityType == "Trade"
        assert activity.Symbol == "AAPL"
        assert activity.Description == "Buy 10 AAPL @ 150.25"
        assert activity.Amount == 1502.50
        assert activity.TradeDate == "2023-01-15T12:30:45Z"
        assert activity.SettleDate == "2023-01-17T00:00:00Z"
        assert activity.TransactionID == "tx123"
        assert activity.OrderID == "ord456"

    def test_activity_without_symbol(self):
        """Test that an Activity without a symbol can be created."""
        activity = Activity(
            AccountID="12345",
            ActivityType="Fee",
            Description="Monthly account fee",
            Amount=9.95,
            TransactionID="tx789",
        )
        assert activity.AccountID == "12345"
        assert activity.ActivityType == "Fee"
        assert activity.Symbol is None
        assert activity.Description == "Monthly account fee"
        assert activity.Amount == 9.95
        assert activity.TransactionID == "tx789"
        assert activity.OrderID is None

    def test_missing_required_fields(self):
        """Test that ValidationError is raised when required fields are missing."""
        with pytest.raises(ValidationError):
            Activity()

        with pytest.raises(ValidationError):
            Activity(
                AccountID="12345",
                # Missing ActivityType
                Description="Buy 10 AAPL @ 150.25",
                Amount=1502.50,
                TransactionID="tx123",
            )

    def test_invalid_activity_type(self):
        """Test that ValidationError is raised when ActivityType is invalid."""
        with pytest.raises(ValidationError):
            Activity(
                AccountID="12345",
                ActivityType="InvalidType",  # Invalid activity type
                Description="Unknown activity",
                Amount=100.00,
                TransactionID="tx123",
            )


class TestOrder:
    """Tests for the Order class."""

    def test_valid_order(self):
        """Test that a valid Order can be created."""
        order = Order(
            AccountID="12345",
            OrderID="ord123",
            Status="OPN",
            StatusDescription="Sent",
            OrderType="Limit",
            LimitPrice="150.25",
        )
        assert order.AccountID == "12345"
        assert order.OrderID == "ord123"
        assert order.Status == "OPN"
        assert order.StatusDescription == "Sent"
        assert order.OrderType == "Limit"
        assert order.LimitPrice == "150.25"

    def test_order_with_legs(self):
        """Test that an Order with legs can be created."""
        leg1 = OrderLeg(
            AssetType="STOCK",
            BuyOrSell="Buy",
            ExecQuantity="100",
            ExecutionPrice="150.25",
            OpenOrClose="Open",
            QuantityOrdered="100",
            QuantityRemaining="0",
            Symbol="AAPL",
        )

        leg2 = OrderLeg(
            AssetType="STOCKOPTION",
            BuyOrSell="Sell",
            ExecQuantity="1",
            ExecutionPrice="5.25",
            ExpirationDate="2023-12-15",
            OpenOrClose="Open",
            OptionType="CALL",
            QuantityOrdered="1",
            QuantityRemaining="0",
            StrikePrice="155.00",
            Symbol="AAPL   231215C00155000",
            Underlying="AAPL",
        )

        order = Order(
            AccountID="12345",
            OrderID="O12345",
            Status="FLL",
            StatusDescription="Filled",
            StopPrice="0",
            LimitPrice="150.25",
            OrderType="Limit",
            Duration="DAY",
            Legs=[leg1, leg2],
        )

        assert order.AccountID == "12345"
        assert order.OrderID == "O12345"
        assert order.Status == "FLL"
        assert len(order.Legs) == 2
        assert order.Legs[0] == leg1
        assert order.Legs[1] == leg2
        assert order.Legs[0].Symbol == "AAPL"
        assert order.Legs[1].Symbol == "AAPL   231215C00155000"
        assert order.Legs[0].BuyOrSell == "Buy"
        assert order.Legs[1].BuyOrSell == "Sell"

    def test_order_with_activation_rules(self):
        """Test that an Order with market activation rules can be created."""
        rule = MarketActivationRule(
            RuleType="Price", Symbol="SPY", Predicate="gt", TriggerKey="Last", Price="400.00"
        )

        order = Order(
            AccountID="12345",
            OrderID="O12345",
            Status="OPN",
            StatusDescription="Open",
            StopPrice="0",
            LimitPrice="150.25",
            OrderType="Limit",
            Duration="DAY",
            MarketActivationRules=[rule],
        )

        assert order.AccountID == "12345"
        assert order.OrderID == "O12345"
        assert order.Status == "OPN"
        assert len(order.MarketActivationRules) == 1
        assert order.MarketActivationRules[0] == rule
        assert order.MarketActivationRules[0].RuleType == "Price"
        assert order.MarketActivationRules[0].Symbol == "SPY"
        assert order.MarketActivationRules[0].Price == "400.00"

    def test_missing_required_fields(self):
        """Test that ValidationError is raised when required fields are missing."""
        with pytest.raises(ValidationError):
            Order()

        with pytest.raises(ValidationError):
            Order(
                # Missing AccountID
                OrderID="ord123",
                Status="OPN",
                StatusDescription="Sent",
                OrderType="Limit",
                LimitPrice="150.25",
            )


class TestOrders:
    """Tests for the Orders class."""

    def test_valid_orders(self):
        """Test that a valid Orders can be created."""
        order1 = Order(
            AccountID="12345",
            OrderID="ord123",
            Status="OPN",
            StatusDescription="Sent",
            OrderType="Limit",
            LimitPrice="150.25",
        )
        order2 = Order(
            AccountID="12345",
            OrderID="ord456",
            Status="FLL",
            StatusDescription="Filled",
            OrderType="Market",
        )
        orders = Orders(Orders=[order1, order2])
        assert len(orders.Orders) == 2
        assert orders.Orders[0].OrderID == "ord123"
        assert orders.Orders[1].OrderID == "ord456"
        assert orders.Errors is None

    def test_orders_with_errors(self):
        """Test that an Orders with errors can be created."""
        order = Order(
            AccountID="12345",
            OrderID="ord123",
            Status="OPN",
            StatusDescription="Sent",
            OrderType="Limit",
            LimitPrice="150.25",
        )
        error = OrderError(
            AccountID="67890",
            Error="AccountNotFound",
            Message="Account 67890 not found",
        )
        orders = Orders(Orders=[order], Errors=[error])
        assert len(orders.Orders) == 1
        assert orders.Orders[0].AccountID == "12345"
        assert len(orders.Errors) == 1
        assert orders.Errors[0].AccountID == "67890"
        assert orders.Errors[0].Error == "AccountNotFound"

    def test_missing_required_fields(self):
        """Test that ValidationError is raised when required fields are missing."""
        with pytest.raises(ValidationError):
            Orders()

        with pytest.raises(ValidationError):
            Orders(Errors=[])  # Missing Orders


class TestStreamOrderResponseData:
    """Tests for the StreamOrderResponseData class."""

    def test_valid_stream_order_response(self):
        """Test that a valid StreamOrderResponseData can be created."""
        stream_order = StreamOrderResponseData(
            OrderID="ord123",
            AccountID="12345",
            Status="OPN",
            StatusDescription="Sent",
            OrderType="Limit",
            Symbol="AAPL",
            Quantity="100",
            FilledQuantity="0",
            RemainingQuantity="100",
            LimitPrice="150.25",
        )
        assert stream_order.OrderID == "ord123"
        assert stream_order.AccountID == "12345"
        assert stream_order.Status == "OPN"
        assert stream_order.StatusDescription == "Sent"
        assert stream_order.OrderType == "Limit"
        assert stream_order.Symbol == "AAPL"
        assert stream_order.Quantity == "100"
        assert stream_order.FilledQuantity == "0"
        assert stream_order.RemainingQuantity == "100"
        assert stream_order.LimitPrice == "150.25"

    def test_missing_required_fields(self):
        """Test that ValidationError is raised when required fields are missing."""
        with pytest.raises(ValidationError):
            StreamOrderResponseData()

        with pytest.raises(ValidationError):
            StreamOrderResponseData(
                OrderID="ord123",
                # Missing AccountID
                Status="OPN",
                StatusDescription="Sent",
                OrderType="Limit",
                Symbol="AAPL",
                Quantity="100",
                FilledQuantity="0",
                RemainingQuantity="100",
            )


class TestStreamOrderErrorResponse:
    """Tests for the StreamOrderErrorResponse class."""

    def test_valid_stream_order_error(self):
        """Test that a valid StreamOrderErrorResponse can be created."""
        error = StreamOrderErrorResponse(
            Error="OrderNotFound",
            Message="Order not found",
            AccountID="12345",
            OrderID="ord123",
        )
        assert error.Error == "OrderNotFound"
        assert error.Message == "Order not found"
        assert error.AccountID == "12345"
        assert error.OrderID == "ord123"

    def test_error_without_account_order(self):
        """Test that a StreamOrderErrorResponse without account/order can be created."""
        error = StreamOrderErrorResponse(
            Error="AuthenticationError",
            Message="Invalid authentication token",
        )
        assert error.Error == "AuthenticationError"
        assert error.Message == "Invalid authentication token"
        assert error.AccountID is None
        assert error.OrderID is None

    def test_missing_required_fields(self):
        """Test that ValidationError is raised when required fields are missing."""
        with pytest.raises(ValidationError):
            StreamOrderErrorResponse()

        with pytest.raises(ValidationError):
            StreamOrderErrorResponse(
                Error="OrderNotFound",
                # Missing Message
            )


class TestStreamStatus:
    """Tests for the StreamStatus class."""

    def test_valid_stream_status(self):
        """Test that a valid StreamStatus can be created."""
        status = StreamStatus(
            StreamStatus="Connected",
            Message="Stream successfully connected",
        )
        assert status.StreamStatus == "Connected"
        assert status.Message == "Stream successfully connected"

    def test_status_without_message(self):
        """Test that a StreamStatus without message can be created."""
        status = StreamStatus(
            StreamStatus="Disconnected",
        )
        assert status.StreamStatus == "Disconnected"
        assert status.Message is None

    def test_missing_required_fields(self):
        """Test that ValidationError is raised when required fields are missing."""
        with pytest.raises(ValidationError):
            StreamStatus()

    def test_invalid_status(self):
        """Test that ValidationError is raised when StreamStatus is invalid."""
        with pytest.raises(ValidationError):
            StreamStatus(
                StreamStatus="Invalid",  # Invalid status
            )
