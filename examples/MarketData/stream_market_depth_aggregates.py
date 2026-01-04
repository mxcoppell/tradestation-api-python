import asyncio
import logging
import os

from dotenv import load_dotenv

from tradestation.client import TradeStationClient
from tradestation.ts_types.market_data import MarketDepthAggregate

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


async def stream_market_depth_aggregates(
    ts_client: TradeStationClient, symbol: str, max_levels: int = 5
):
    """
    Starts streaming aggregated market depth data for a single symbol.

    Args:
        ts_client: An authenticated TradeStation client instance.
        symbol: The symbol to stream market depth data for.
        max_levels: The maximum number of price levels to receive (default is 5).

    Returns:
        The stream object which can be used to manage the stream (e.g., unsubscribe).
    """
    logger.info(
        f"Starting aggregated market depth stream for symbol: {symbol} with max levels: {max_levels}"
    )
    params = {"maxlevels": max_levels}
    try:
        stream = await ts_client.market_data.stream_market_depth_aggregates(
            symbol=symbol, params=params
        )
        logger.info(
            f"Successfully obtained stream reader for aggregated market depth for {symbol}."
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

    # Initialize the TradeStation client
    client = TradeStationClient()

    # --- Symbol and Stream Configuration ---
    # Define the symbol to stream
    # Replace with the symbol you are interested in
    symbol_to_stream = "MSFT"
    # Define the maximum number of price levels (optional, defaults to 5)
    max_depth_levels = 5

    # --- Start Streaming ---
    # Start the market depth aggregate stream
    stream_reader = None
    try:
        stream_reader = await stream_market_depth_aggregates(
            client, symbol_to_stream, max_depth_levels
        )

        # --- Process the Stream ---
        logger.info(f"Processing stream for {symbol_to_stream}. Press Ctrl+C to stop.")
        while True:
            logger.info(
                "Stream processing loop not fully implemented yet. Running placeholder sleep."
            )
            await asyncio.sleep(5)

    except asyncio.CancelledError:
        logger.info("Stream cancelled by user (Ctrl+C).")
    except Exception as e:
        logger.error(f"An error occurred during streaming: {e}")
    finally:
        # --- Clean Up ---
        if stream_reader:
            logger.info(f"Closing stream connection for {symbol_to_stream}...")
        else:
            logger.warning("No active stream reader to clean up.")

        # Close the TradeStation client session properly
        await client.http_client.close()
        logger.info("TradeStation client session closed.")


if __name__ == "__main__":
    # Run the main asynchronous function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Script interrupted by user.")
    except Exception as e:
        logger.error(f"Script failed: {e}", exc_info=True)
