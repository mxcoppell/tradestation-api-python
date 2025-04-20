import asyncio
import os
import logging

from dotenv import load_dotenv
from src.client.tradestation_client import TradeStationClient
from src.ts_types.market_data import MarketDepthAggregate

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def handle_market_depth_aggregate(data: MarketDepthAggregate):
    """
    Asynchronous callback function to handle incoming market depth aggregate data.

    This function is called each time a new market depth aggregate message is received
    from the TradeStation stream. It logs the received data.

    Args:
        data: A MarketDepthAggregate object containing the market depth data.
    """
    logger.info(f"Received market depth aggregate: {data}")
    # Example: Accessing specific fields
    # logger.info(f"Symbol: {data.symbol}, Bid Price: {data.bids[0].price if data.bids else 'N/A'}, Ask Price: {data.asks[0].price if data.asks else 'N/A'}")


async def stream_market_depth_aggregates(
    ts_client: TradeStationClient, symbols: list[str], max_levels: int = 5
):
    """
    Starts streaming aggregated market depth data for a list of symbols.

    Args:
        ts_client: An authenticated TradeStation client instance.
        symbols: A list of symbols to stream market depth data for.
        max_levels: The maximum number of price levels to receive (default is 5).

    Returns:
        The stream object which can be used to manage the stream (e.g., unsubscribe).
    """
    logger.info(
        f"Starting aggregated market depth stream for symbols: {symbols} with max levels: {max_levels}"
    )
    try:
        # Subscribe to the market depth aggregate stream
        stream = await ts_client.market_data.stream_market_depth_aggregates(
            symbols=symbols, max_levels=max_levels, callback=handle_market_depth_aggregate
        )
        logger.info(
            f"Successfully subscribed to aggregated market depth stream. Stream ID: {stream.stream_id}"
        )
        return stream
    except AttributeError:
        logger.error(
            "Could not find 'stream_market_depth_aggregates' method. Check TradeStationClient structure."
        )
        raise
    except Exception as e:
        logger.error(f"Failed to subscribe to aggregated market depth stream: {e}")
        raise


async def main():
    """
    Main asynchronous function to set up the TradeStation client and start the stream.
    """
    # --- Authentication Setup ---
    # Retrieve credentials from environment variables
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    paper_trade = (
        os.getenv("PAPER_TRADE", "true").lower() == "true"
    )  # Default to paper trading if not set

    if not client_id or not client_secret:
        logger.error("CLIENT_ID and CLIENT_SECRET must be set in the .env file.")
        return

    # --- Initialize TradeStation Client ---
    # Create an instance of the TradeStation client
    # The client handles authentication and token management automatically.
    logger.info("Initializing TradeStation client...")
    ts_client = TradeStationClient(
        client_id=client_id,
        client_secret=client_secret,
        paper_trade=paper_trade,
    )

    # --- Symbol and Stream Configuration ---
    # Define the symbols to stream
    # Replace with the symbols you are interested in
    symbols_to_stream = ["MSFT", "AAPL"]
    # Define the maximum number of price levels (optional, defaults to 5)
    max_depth_levels = 5

    # --- Start Streaming ---
    # Start the market depth aggregate stream
    stream = None
    try:
        stream = await stream_market_depth_aggregates(
            ts_client, symbols_to_stream, max_depth_levels
        )

        # --- Keep the Stream Alive ---
        # Keep the script running to receive stream updates.
        # You can implement more sophisticated logic here to stop the stream based on conditions.
        logger.info("Stream started. Press Ctrl+C to stop.")
        while True:
            await asyncio.sleep(1)  # Keep the event loop running

    except asyncio.CancelledError:
        logger.info("Stream cancelled by user (Ctrl+C).")
    except Exception as e:
        logger.error(f"An error occurred during streaming: {e}")
    finally:
        # --- Clean Up ---
        # Unsubscribe from the stream when done or if an error occurs
        if stream:
            logger.info(f"Unsubscribing from stream ID: {stream.stream_id}...")
            logger.info("Unsubscribe mechanism needs verification based on stream object type.")
        else:
            logger.warning("No active stream to unsubscribe from.")

        # Close the TradeStation client session properly
        await ts_client.http_client.close()
        logger.info("TradeStation client session closed.")


if __name__ == "__main__":
    # Run the main asynchronous function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Script interrupted by user.")
    except Exception as e:
        logger.error(f"Script failed: {e}", exc_info=True)
