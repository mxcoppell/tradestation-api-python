import pytest
from pydantic import ValidationError

from tradestation.ts_types import (
    AggregatedQuoteData,
    Bar,
    BarHistoryParams,
    BarsResponse,
    BarStreamParams,
    Heartbeat,
    MarketDepthAggregate,
    MarketDepthParams,
    MarketDepthQuote,
    MarketDepthQuoteData,
    MarketFlags,
    OptionChain,
    OptionChainParams,
    OptionGreeks,
    OptionQuote,
    OptionQuoteLeg,
    OptionQuoteParams,
    PriceFormat,
    QuantityFormat,
    Quote,
    QuoteError,
    QuoteSnapshot,
    QuoteStream,
    Spread,
    SpreadLeg,
    StreamErrorResponse,
    SymbolDetail,
    SymbolDetailsErrorResponse,
    SymbolDetailsResponse,
)


class TestMarketFlags:
    def test_create_valid(self):
        """Test creating a valid market flags object."""
        flags = MarketFlags(
            IsBats=True,
            IsDelayed=False,
            IsHalted=False,
            IsHardToBorrow=True,
        )
        assert flags.IsBats is True
        assert flags.IsDelayed is False
        assert flags.IsHalted is False
        assert flags.IsHardToBorrow is True

    def test_missing_fields(self):
        """Test that all fields are required."""
        with pytest.raises(ValidationError):
            MarketFlags(IsBats=True, IsDelayed=False, IsHalted=False)


class TestQuote:
    def test_create_valid(self):
        """Test creating a valid quote object."""
        market_flags = MarketFlags(
            IsBats=True,
            IsDelayed=False,
            IsHalted=False,
            IsHardToBorrow=True,
        )

        quote = Quote(
            Symbol="AAPL",
            Ask="150.50",
            AskSize="100",
            Bid="150.40",
            BidSize="200",
            Close="149.80",
            DailyOpenInterest="0",
            High="151.00",
            Low="149.50",
            High52Week="165.00",
            High52WeekTimestamp="2023-01-15T10:30:00Z",
            Last="150.45",
            Low52Week="130.00",
            Low52WeekTimestamp="2022-07-15T14:45:00Z",
            MarketFlags=market_flags,
            NetChange="0.65",
            NetChangePct="0.43",
            Open="149.75",
            PreviousClose="149.80",
            PreviousVolume="45000000",
            TickSizeTier="0",
            TradeTime="2023-04-15T16:00:00Z",
            Volume="35000000",
            LastSize="100",
            LastVenue="NYSE",
            VWAP="150.23",
        )

        assert quote.Symbol == "AAPL"
        assert quote.Ask == "150.50"
        assert quote.AskSize == "100"
        assert quote.Last == "150.45"
        assert quote.MarketFlags.IsBats is True
        assert quote.MarketFlags.IsHardToBorrow is True
        assert quote.Restrictions is None

    def test_optional_fields(self):
        """Test optional fields in quote object."""
        market_flags = MarketFlags(
            IsBats=True, IsDelayed=False, IsHalted=False, IsHardToBorrow=True
        )

        quote = Quote(
            Symbol="AAPL",
            Ask="150.50",
            AskSize="100",
            Bid="150.40",
            BidSize="200",
            Close="149.80",
            DailyOpenInterest="0",
            High="151.00",
            Low="149.50",
            High52Week="165.00",
            High52WeekTimestamp="2023-01-15T10:30:00Z",
            Last="150.45",
            MinPrice="100.00",
            MaxPrice="200.00",
            FirstNoticeDate="2023-04-20",
            LastTradingDate="2023-05-20",
            Low52Week="130.00",
            Low52WeekTimestamp="2022-07-15T14:45:00Z",
            MarketFlags=market_flags,
            NetChange="0.65",
            NetChangePct="0.43",
            Open="149.75",
            PreviousClose="149.80",
            PreviousVolume="45000000",
            Restrictions=["PDT", "Margin"],
            TickSizeTier="0",
            TradeTime="2023-04-15T16:00:00Z",
            Volume="35000000",
            LastSize="100",
            LastVenue="NYSE",
            VWAP="150.23",
        )

        assert quote.MinPrice == "100.00"
        assert quote.MaxPrice == "200.00"
        assert quote.FirstNoticeDate == "2023-04-20"
        assert quote.LastTradingDate == "2023-05-20"
        assert quote.Restrictions == ["PDT", "Margin"]


class TestBar:
    def test_create_valid(self):
        """Test creating a valid bar object."""
        bar = Bar(
            Close="150.50",
            DownTicks=120,
            DownVolume=15000,
            Epoch=1681574400,
            High="151.00",
            IsEndOfHistory=False,
            IsRealtime=True,
            Low="149.50",
            Open="149.75",
            OpenInterest="0",
            TimeStamp="2023-04-15T16:00:00Z",
            TotalTicks=350,
            TotalVolume="35000",
            UpTicks=230,
            UpVolume=20000,
            BarStatus="Closed",
        )

        assert bar.Close == "150.50"
        assert bar.DownTicks == 120
        assert bar.Epoch == 1681574400
        assert bar.IsRealtime is True
        assert bar.OpenInterest == "0"
        assert bar.TotalTicks == 350
        assert bar.BarStatus == "Closed"

    def test_optional_fields(self):
        """Test optional fields in bar object."""
        bar = Bar(
            Close="150.50",
            DownTicks=120,
            DownVolume=15000,
            Epoch=1681574400,
            High="151.00",
            IsEndOfHistory=False,
            IsRealtime=True,
            Low="149.50",
            Open="149.75",
            OpenInterest="0",
            TimeStamp="2023-04-15T16:00:00Z",
            TotalTicks=350,
            TotalVolume="35000",
            UnchangedTicks=10,
            UnchangedVolume=1000,
            UpTicks=230,
            UpVolume=20000,
            BarStatus="Closed",
        )

        assert bar.UnchangedTicks == 10
        assert bar.UnchangedVolume == 1000

    def test_bar_status_validation(self):
        """Test bar status validation."""
        # Valid status
        Bar(
            Close="150.50",
            DownTicks=120,
            DownVolume=15000,
            Epoch=1681574400,
            High="151.00",
            IsEndOfHistory=False,
            IsRealtime=True,
            Low="149.50",
            Open="149.75",
            OpenInterest="0",
            TimeStamp="2023-04-15T16:00:00Z",
            TotalTicks=350,
            TotalVolume="35000",
            UpTicks=230,
            UpVolume=20000,
            BarStatus="Open",
        )

        # Invalid status
        with pytest.raises(ValidationError):
            Bar(
                Close="150.50",
                DownTicks=120,
                DownVolume=15000,
                Epoch=1681574400,
                High="151.00",
                IsEndOfHistory=False,
                IsRealtime=True,
                Low="149.50",
                Open="149.75",
                OpenInterest="0",
                TimeStamp="2023-04-15T16:00:00Z",
                TotalTicks=350,
                TotalVolume="35000",
                UpTicks=230,
                UpVolume=20000,
                BarStatus="Invalid",
            )


class TestOptionGreeks:
    def test_create_valid(self):
        """Test creating a valid option greeks object."""
        greeks = OptionGreeks(
            Delta=0.65,
            Gamma=0.03,
            Theta=-0.15,
            Vega=0.10,
            Rho=0.08,
            ImpliedVolatility=0.25,
        )

        assert greeks.Delta == 0.65
        assert greeks.Gamma == 0.03
        assert greeks.Theta == -0.15
        assert greeks.Vega == 0.10
        assert greeks.Rho == 0.08
        assert greeks.ImpliedVolatility == 0.25


class TestSymbolDetail:
    def test_create_stock(self):
        """Test creating a valid stock symbol detail."""
        price_format = PriceFormat(
            Format="Decimal",
            Decimals="2",
            IncrementStyle="Simple",
            Increment="0.01",
            PointValue="1.0",
        )

        quantity_format = QuantityFormat(
            Format="Decimal",
            Decimals="0",
            IncrementStyle="Simple",
            Increment="1",
            MinimumTradeQuantity="1",
        )

        symbol_detail = SymbolDetail(
            AssetType="STOCK",
            Country="US",
            Currency="USD",
            Description="APPLE INC",
            Exchange="NASDAQ",
            PriceFormat=price_format,
            QuantityFormat=quantity_format,
            Root="AAPL",
            Symbol="AAPL",
        )

        assert symbol_detail.AssetType == "STOCK"
        assert symbol_detail.Country == "US"
        assert symbol_detail.Currency == "USD"
        assert symbol_detail.Description == "APPLE INC"
        assert symbol_detail.Exchange == "NASDAQ"
        assert symbol_detail.PriceFormat.Format == "Decimal"
        assert symbol_detail.QuantityFormat.MinimumTradeQuantity == "1"
        assert symbol_detail.Root == "AAPL"
        assert symbol_detail.Symbol == "AAPL"
        assert symbol_detail.ExpirationDate is None
        assert symbol_detail.OptionType is None

    def test_create_option(self):
        """Test creating a valid option symbol detail."""
        price_format = PriceFormat(
            Format="Decimal",
            Decimals="2",
            IncrementStyle="Simple",
            Increment="0.01",
            PointValue="100.0",
        )

        quantity_format = QuantityFormat(
            Format="Decimal",
            Decimals="0",
            IncrementStyle="Simple",
            Increment="1",
            MinimumTradeQuantity="1",
        )

        symbol_detail = SymbolDetail(
            AssetType="STOCKOPTION",
            Country="US",
            Currency="USD",
            Description="APPLE INC $150 CALL",
            Exchange="OPRA",
            ExpirationDate="2023-06-16",
            OptionType="Call",
            PriceFormat=price_format,
            QuantityFormat=quantity_format,
            Root="AAPL",
            StrikePrice="150.00",
            Symbol="AAPL230616C150",
            Underlying="AAPL",
        )

        assert symbol_detail.AssetType == "STOCKOPTION"
        assert symbol_detail.ExpirationDate == "2023-06-16"
        assert symbol_detail.OptionType == "Call"
        assert symbol_detail.StrikePrice == "150.00"
        assert symbol_detail.Underlying == "AAPL"


class TestStreamResponses:
    def test_heartbeat(self):
        """Test creating a heartbeat message."""
        heartbeat = Heartbeat(Heartbeat=12345, Timestamp="2023-04-15T16:00:00Z")
        assert heartbeat.Heartbeat == 12345
        assert heartbeat.Timestamp == "2023-04-15T16:00:00Z"

    def test_stream_error(self):
        """Test creating a stream error response."""
        error = StreamErrorResponse(Error="ConnectionError", Message="Connection was lost")
        assert error.Error == "ConnectionError"
        assert error.Message == "Connection was lost"
