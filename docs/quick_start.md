# Quick Start Guide

This guide will help you get up and running with the TradeStation API Python Wrapper quickly.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mxcoppell/tradestation-api-python.git
   cd tradestation-api-python
   ```

2. Install the package using Poetry:
   ```bash
   poetry install
   ```

   Alternatively, you can use pip:
   ```bash
   pip install -e .
   ```

## Setting Up Credentials

1. Create a `.env` file in the project root by copying the sample file:
   ```bash
   cp .env.sample .env
   ```

2. Edit the `.env` file with your TradeStation API credentials:
   ```
   # Mandatory
   CLIENT_ID=your_client_id
   REFRESH_TOKEN=your_refresh_token
   ENVIRONMENT=Simulation # Or Live
   ```

## Basic Usage

### Creating a Client

```python
import asyncio
from dotenv import load_dotenv
from src.client.tradestation_client import TradeStationClient

# Load environment variables
load_dotenv()

# Create the client (automatically uses environment variables)
client = TradeStationClient()

# Or create with specific parameters
client = TradeStationClient(
    refresh_token="your_refresh_token",
    environment="Simulation"
)
```

### Getting Quote Data

```python
import asyncio
from dotenv import load_dotenv
from src.client.tradestation_client import TradeStationClient

async def main():
    load_dotenv()
    client = TradeStationClient()
    
    try:
        # Get quotes for a single symbol
        aapl_quote = await client.market_data.get_quotes(["AAPL"])
        print(f"AAPL Price: ${aapl_quote.Quotes[0].Last}")
        
        # Get quotes for multiple symbols
        quotes = await client.market_data.get_quotes(["MSFT", "GOOGL", "AMZN"])
        for quote in quotes.Quotes:
            print(f"{quote.Symbol}: ${quote.Last} ({quote.PercentChange}%)")
    finally:
        # Always close the client when done
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Getting Account Information

```python
import asyncio
from dotenv import load_dotenv
from src.client.tradestation_client import TradeStationClient

async def main():
    load_dotenv()
    client = TradeStationClient()
    
    try:
        # Get all accounts
        accounts = await client.brokerage.get_accounts()
        print(f"Found {len(accounts.Accounts)} accounts")
        
        # Print account information
        for account in accounts.Accounts:
            print(f"Account: {account.AccountID}")
            print(f"Name: {account.Alias}")
            print(f"Type: {account.AccountType}")
            print(f"Status: {account.Status}")
            print("-" * 30)
            
        # Get detailed balances for the first account
        if accounts.Accounts:
            account_id = accounts.Accounts[0].AccountID
            balances = await client.brokerage.get_balances(account_id)
            print(f"Cash Balance: ${balances.Balances[0].CashBalance}")
            print(f"Buying Power: ${balances.Balances[0].BuyingPower}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Getting Historical Data

```python
import asyncio
from dotenv import load_dotenv
from src.client.tradestation_client import TradeStationClient
from datetime import datetime, timedelta

async def main():
    load_dotenv()
    client = TradeStationClient()
    
    try:
        # Get daily bars for the last 10 days
        daily_bars = await client.market_data.get_bar_history("SPY", {
            "unit": "Daily",
            "barsback": 10
        })
        
        print(f"Retrieved {len(daily_bars.Bars)} daily bars for SPY")
        for bar in daily_bars.Bars:
            date = datetime.fromisoformat(bar.TimeStamp.replace("Z", "+00:00")).strftime("%Y-%m-%d")
            print(f"{date}: Open=${bar.Open}, Close=${bar.Close}, Volume={int(float(bar.TotalVolume)):,}")
            
        # Get 5-minute bars for a specific date range
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_str = yesterday.strftime("%Y-%m-%d")
        
        minute_bars = await client.market_data.get_bar_history("AAPL", {
            "unit": "Minute",
            "interval": "5",
            "firstdate": f"{yesterday_str}T14:30:00Z",  # 09:30 ET in UTC
            "lastdate": f"{yesterday_str}T21:00:00Z",   # 16:00 ET in UTC
        })
        
        print(f"\nRetrieved {len(minute_bars.Bars)} 5-minute bars for AAPL")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Streaming Real-time Data

```python
import asyncio
from dotenv import load_dotenv
from src.client.tradestation_client import TradeStationClient

async def quote_callback(quote_data):
    """Process incoming quote data"""
    print(f"Quote update: {quote_data['Symbol']} - Last: {quote_data['Last']}")

async def main():
    load_dotenv()
    client = TradeStationClient()
    
    try:
        # Subscribe to quote updates
        subscription = await client.market_data.stream_quotes(
            symbols=["AAPL", "MSFT", "GOOGL"],
            callback=quote_callback
        )
        
        # Keep the stream running for 60 seconds
        print("Streaming started. Waiting for 60 seconds...")
        await asyncio.sleep(60)
        
        # Unsubscribe when done
        await subscription.unsubscribe()
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Placing an Order

```python
import asyncio
from dotenv import load_dotenv
from src.client.tradestation_client import TradeStationClient

async def main():
    load_dotenv()
    client = TradeStationClient()
    
    try:
        # Get accounts to find the account ID
        accounts = await client.brokerage.get_accounts()
        if not accounts.Accounts:
            print("No accounts found")
            return
            
        account_id = accounts.Accounts[0].AccountID
        
        # Place a market order to buy 1 share of AAPL
        order_request = {
            "AccountID": account_id,
            "Symbol": "AAPL",
            "Quantity": 1,
            "OrderType": "Market",
            "TradeAction": "BUY",
            "TimeInForce": {
                "Duration": "DAY"
            },
            "Route": "Intelligent"
        }
        
        # Submit the order
        # Note: This is commented out to prevent accidental order submission
        # Uncomment to actually place an order
        """
        order_result = await client.order_execution.place_order(order_request)
        print("Order placed successfully")
        print(f"Order ID: {order_result.Orders[0].OrderID}")
        """
        
        # Instead, just print the order details
        print("Order request (not submitted):")
        print(f"Account: {order_request['AccountID']}")
        print(f"Symbol: {order_request['Symbol']}")
        print(f"Action: {order_request['TradeAction']} {order_request['Quantity']} shares")
        print(f"Order Type: {order_request['OrderType']}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Next Steps

After mastering the basics, explore these topics:

1. **Advanced Market Data**: Explore options chains, time & sales data, and more detailed quote information
2. **Order Management**: Learn how to modify orders, cancel orders, and work with complex order types
3. **Position Management**: Monitor positions, analyze performance, and manage risk
4. **Streaming Data**: Set up real-time data streams for quotes, bars, and order status updates
5. **Automated Trading**: Implement trading algorithms using the API

## Common Issues and Solutions

### Authentication Issues

If you encounter authentication errors:
- Verify your Client ID is correct
- Ensure your Refresh Token is valid and not expired
- Check that you have the required permissions for your API application

### Rate Limiting

If you hit rate limits:
- Batch requests when possible (e.g., request quotes for multiple symbols at once)
- Add appropriate error handling for rate limit exceptions
- Consider implementing caching for frequently accessed data

### Connection Issues

If you have connection problems:
- Check your internet connection
- Verify that the TradeStation API is operational
- Ensure you're using the correct environment (Live vs. Simulation)

## Example Scripts

For more examples, check the `examples` directory in the repository:
- `examples/MarketData`: Examples of retrieving quotes, bars, and symbol information
- `examples/Brokerage`: Examples of working with accounts, positions, and balances
- `examples/OrderExecution`: Examples of placing and managing orders 