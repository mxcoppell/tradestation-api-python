import asyncio
import os
from dotenv import load_dotenv

from src.tradestation_api import TradeStationClient

# Load environment variables from .env file
load_dotenv()


async def main():
    # Initialize the TradeStation client with refresh token from environment variables
    client = TradeStationClient()

    try:
        # Example 1: Get details for a single stock
        msft_details = await client.market_data.get_symbol_details(['MSFT'])
        print('\nDetails for MSFT:')
        msft_symbol = msft_details.Symbols[0]
        print(f"Asset Type: {msft_symbol.AssetType}")
        print(f"Description: {msft_symbol.Description}")
        print(f"Exchange: {msft_symbol.Exchange}")
        print(f"Currency: {msft_symbol.Currency}")
        print('Price Format:', {
            'format': msft_symbol.PriceFormat.Format,
            'decimals': msft_symbol.PriceFormat.Decimals or 'N/A',
            'increment': msft_symbol.PriceFormat.Increment
        })

        # Example 2: Get details for multiple symbols of different types
        symbols = [
            'MSFT',              # Stock
            'MSFT 240119C400',   # Option
            'ESH24',             # Future
            'EUR/USD',           # Forex
            'BTCUSD'            # Crypto
        ]
        details = await client.market_data.get_symbol_details(symbols)

        # Process successful results
        print('\nDetails for Multiple Symbols:')
        for symbol in details.Symbols:
            print(f"\n{symbol.Symbol} ({symbol.AssetType}):")
            print(f"Description: {symbol.Description}")
            print(f"Exchange: {symbol.Exchange}")
            print(f"Price Format: {symbol.PriceFormat.Format} ({symbol.PriceFormat.Decimals or 'N/A'} decimals)")

            # Asset-specific properties
            if symbol.AssetType == 'STOCKOPTION':
                print(f"Expiration: {symbol.ExpirationDate}")
                print(f"Strike: {symbol.StrikePrice}")
                print(f"Type: {symbol.OptionType}")
            elif symbol.AssetType == 'FUTURE':
                print(f"Expiration: {symbol.ExpirationDate}")
                print(f"Type: {symbol.FutureType}")
            print('---')

        # Handle any errors
        if details.Errors:
            print('\nErrors:')
            for error in details.Errors:
                print(f"{error.Symbol}: {error.Message}")

        # Example 3: Format prices using symbol details
        stock = details.Symbols[0]
        price = 123.456

        print('\nPrice Formatting Example:')
        if stock.PriceFormat.Format == 'Decimal':
            if stock.PriceFormat.Decimals:
                print(f"Formatted Price: {price:.{int(stock.PriceFormat.Decimals)}f}")
            else:
                print('Decimal format specified but no decimals provided')
        elif stock.PriceFormat.Format == 'Fraction':
            if stock.PriceFormat.Fraction:
                whole = int(price)
                fraction = price - whole
                denominator = int(stock.PriceFormat.Fraction)
                numerator = round(fraction * denominator)
                print(f"Formatted Price: {whole} {numerator}/{denominator}")
            else:
                print('Fraction format specified but no denominator provided')
        elif stock.PriceFormat.Format == 'SubFraction':
            if stock.PriceFormat.Fraction and stock.PriceFormat.SubFraction:
                whole = int(price)
                fraction = price - whole
                denominator = int(stock.PriceFormat.Fraction)
                sub_fraction = int(stock.PriceFormat.SubFraction)
                main_fraction = int(fraction * denominator)
                sub_fraction_value = round(((fraction - (main_fraction / denominator)) * sub_fraction * denominator) / (sub_fraction / 10))
                print(f"Formatted Price: {whole}'{main_fraction}.{sub_fraction_value}")
            else:
                print('SubFraction format specified but missing fraction or subfraction values')

    except Exception as error:
        print('Error:', error)


if __name__ == "__main__":
    asyncio.run(main())