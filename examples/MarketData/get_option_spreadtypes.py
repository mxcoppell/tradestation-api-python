import asyncio
import os
from dotenv import load_dotenv
from tradestation import TradeStation

# Load environment variables from .env file
load_dotenv()

# Ensure your .env file has TRADESTATION_CLIENT_ID, TRADESTATION_CLIENT_SECRET,
# and TRADESTATION_REFRESH_TOKEN populated.
# You can obtain a refresh token using the provided (or manually run) authentication flow.


async def main():
    """
    Example demonstrating how to fetch available option spread types
    using the TradeStation API.
    """
    # Create a TradeStation client instance
    # Authentication details are typically handled internally by the client
    # using environment variables or a provided configuration.
    ts = TradeStation()

    print("Attempting to fetch option spread types...")

    try:
        # Call the get_option_spread_types method from the MarketData service
        spread_types = await ts.market_data.get_option_spread_types()

        # Check if the response contains spread types
        if spread_types:
            print("Successfully retrieved option spread types:")
            # Iterate through the list of spread types and print each one
            for spread_type in spread_types:
                print(f"- {spread_type}")
        else:
            # Handle cases where the API returns an empty list or null response
            print("No option spread types were returned.")

    except Exception as e:
        # Catch any exceptions that occur during the API call
        # This could include network issues, authentication errors, or API errors
        print(f"An error occurred: {e}")


# Run the asynchronous main function
if __name__ == "__main__":
    asyncio.run(main())
