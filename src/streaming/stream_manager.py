"""
StreamManager for handling WebSocket streaming connections to the TradeStation API.
This module provides functionality for establishing and maintaining WebSocket connections,
handling events and messages, and parsing streaming data.
"""

import asyncio
import json
import logging
from typing import Any, Callable, Dict, List, Optional, Set, Union, cast
from urllib.parse import urljoin

import aiohttp
from pydantic import ValidationError

from ts_types.config import ClientConfig
from ts_types.market_data import Heartbeat, StreamErrorResponse
from utils.token_manager import TokenManager


logger = logging.getLogger(__name__)


class StreamManager:
    """
    Manages WebSocket streaming connections to the TradeStation API.
    Handles connection lifecycle, message processing, and event callbacks.
    """

    # Base URL for TradeStation streaming endpoints
    _BASE_URL = "https://api.tradestation.com"

    # WebSocket heartbeat interval in seconds (used to detect connection health)
    _HEARTBEAT_INTERVAL = 30

    # Maximum reconnection attempts before giving up
    _MAX_RECONNECT_ATTEMPTS = 5

    # Delay between reconnection attempts (in seconds)
    _RECONNECT_DELAY = 2

    def __init__(
        self, token_manager: Optional[TokenManager] = None, config: Optional[ClientConfig] = None
    ) -> None:
        """
        Initialize a new StreamManager.

        Args:
            token_manager: Optional TokenManager instance for authentication.
                           If not provided, a new one will be created.
            config: Optional configuration with settings like client ID and secret.
                    If not provided, values are read from environment variables.

        Raises:
            ValueError: If credentials are invalid or missing when creating a TokenManager.
        """
        self._token_manager = token_manager or TokenManager(config)
        self._connections: Dict[str, Dict[str, Any]] = {}
        self._active_streams: Set[str] = set()
        self._connect_lock = asyncio.Lock()
        self._shutdown_event = asyncio.Event()
        self._max_concurrent_streams = config.max_concurrent_streams if config else 10
        self._subscription_callbacks: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}
        self._reconnection_tasks: Dict[str, asyncio.Task] = {}
        self._message_processing_tasks: Dict[str, asyncio.Task] = {}

    async def connect_stream(self, stream_uri: str, stream_id: str) -> None:
        """
        Establish a WebSocket connection to a streaming endpoint.

        Args:
            stream_uri: The URI path for the streaming endpoint.
            stream_id: A unique identifier for this stream connection.

        Raises:
            ValueError: If the maximum number of concurrent streams is reached.
            ConnectionError: If the connection cannot be established.
        """
        async with self._connect_lock:
            if stream_id in self._connections and self._connections[stream_id].get("active", False):
                logger.debug(f"Stream {stream_id} is already connected")
                return

            if len(self._active_streams) >= self._max_concurrent_streams:
                raise ValueError(
                    f"Maximum concurrent streams limit reached ({self._max_concurrent_streams})"
                )

            try:
                # Get a valid access token for authentication
                access_token = await self._token_manager.get_valid_access_token()

                # Construct the full URL for the WebSocket connection
                full_url = urljoin(self._BASE_URL, stream_uri)
                headers = {"Authorization": f"Bearer {access_token}"}

                # Create WebSocket connection
                session = aiohttp.ClientSession()
                ws = await session.ws_connect(
                    full_url, headers=headers, heartbeat=self._HEARTBEAT_INTERVAL
                )

                # Store connection details
                self._connections[stream_id] = {
                    "websocket": ws,
                    "session": session,
                    "active": True,
                    "uri": stream_uri,
                    "last_heartbeat": asyncio.get_event_loop().time(),
                }

                self._active_streams.add(stream_id)

                # Start message processing for this connection
                task = asyncio.create_task(self._process_messages(stream_id))
                self._message_processing_tasks[stream_id] = task
                logger.info(f"Stream {stream_id} connected successfully")

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.error(f"Failed to connect stream {stream_id}: {str(e)}")
                raise ConnectionError(f"Failed to connect to stream: {str(e)}")

    async def disconnect_stream(self, stream_id: str) -> None:
        """
        Disconnect a specific stream connection.

        Args:
            stream_id: The identifier of the stream to disconnect.
        """
        if stream_id not in self._connections:
            logger.debug(f"Stream {stream_id} is not connected")
            return

        connection = self._connections[stream_id]
        if not connection.get("active", False):
            logger.debug(f"Stream {stream_id} is already disconnected")
            return

        # Cancel any active reconnection task
        if stream_id in self._reconnection_tasks:
            self._reconnection_tasks[stream_id].cancel()
            del self._reconnection_tasks[stream_id]

        # Cancel any message processing task
        if stream_id in self._message_processing_tasks:
            self._message_processing_tasks[stream_id].cancel()
            del self._message_processing_tasks[stream_id]

        # Mark as inactive before closing to prevent reconnection attempts
        connection["active"] = False

        # Close the WebSocket and session
        try:
            await connection["websocket"].close()
            await connection["session"].close()
            logger.info(f"Stream {stream_id} disconnected successfully")
        except Exception as e:
            logger.error(f"Error while disconnecting stream {stream_id}: {str(e)}")
        finally:
            if stream_id in self._active_streams:
                self._active_streams.remove(stream_id)

            # Clean up subscription callbacks
            if stream_id in self._subscription_callbacks:
                del self._subscription_callbacks[stream_id]

    async def disconnect_all(self) -> None:
        """
        Disconnect all active streams and clean up resources.
        """
        self._shutdown_event.set()

        # Make a copy of the active streams set before iterating
        active_streams = list(self._active_streams)
        for stream_id in active_streams:
            await self.disconnect_stream(stream_id)

        # Cancel all remaining tasks
        for task_dict in [self._reconnection_tasks, self._message_processing_tasks]:
            for task in list(task_dict.values()):
                if not task.done():
                    task.cancel()
            task_dict.clear()

        # Reset state
        self._active_streams.clear()
        self._connections.clear()
        self._subscription_callbacks.clear()
        logger.info("All streams disconnected")

    def add_message_callback(
        self, stream_id: str, callback: Callable[[Dict[str, Any]], None]
    ) -> None:
        """
        Add a callback function to process messages from a specific stream.

        Args:
            stream_id: The identifier of the stream to subscribe to.
            callback: A function that takes a message dictionary and processes it.
        """
        if stream_id not in self._subscription_callbacks:
            self._subscription_callbacks[stream_id] = []

        self._subscription_callbacks[stream_id].append(callback)
        logger.debug(f"Added callback for stream {stream_id}")

    def remove_message_callback(
        self, stream_id: str, callback: Callable[[Dict[str, Any]], None]
    ) -> None:
        """
        Remove a specific callback function from a stream's callbacks.

        Args:
            stream_id: The identifier of the stream.
            callback: The callback function to remove.
        """
        if stream_id in self._subscription_callbacks:
            try:
                self._subscription_callbacks[stream_id].remove(callback)
                logger.debug(f"Removed callback from stream {stream_id}")
            except ValueError:
                logger.debug(f"Callback not found for stream {stream_id}")

    async def _process_messages(self, stream_id: str) -> None:
        """
        Process incoming WebSocket messages for a specific stream.

        Args:
            stream_id: The identifier of the stream to process messages for.
        """
        if stream_id not in self._connections:
            logger.error(f"Cannot process messages for non-existent stream {stream_id}")
            return

        connection = self._connections[stream_id]
        ws = connection["websocket"]

        try:
            while connection.get("active", False) and not self._shutdown_event.is_set():
                try:
                    # Wait for a message with a timeout
                    message = await asyncio.wait_for(
                        ws.receive(), timeout=self._HEARTBEAT_INTERVAL * 1.5
                    )

                    # Check message type
                    if message.type == aiohttp.WSMsgType.TEXT:
                        await self._handle_text_message(stream_id, message.data)
                    elif message.type == aiohttp.WSMsgType.BINARY:
                        logger.debug(f"Received binary message on stream {stream_id}")
                    elif message.type in (
                        aiohttp.WSMsgType.CLOSED,
                        aiohttp.WSMsgType.ERROR,
                        aiohttp.WSMsgType.CLOSING,
                    ):
                        logger.warning(f"WebSocket closing for stream {stream_id}: {message.data}")
                        break
                    else:
                        logger.warning(
                            f"Unknown message type on stream {stream_id}: {message.type}"
                        )

                except asyncio.TimeoutError:
                    logger.warning(f"Heartbeat timeout for stream {stream_id}")
                    break
                except asyncio.CancelledError:
                    logger.debug(f"Message processing for stream {stream_id} was cancelled")
                    return

        except Exception as e:
            logger.error(f"Error processing messages for stream {stream_id}: {str(e)}")
        finally:
            # If this wasn't a planned disconnection, attempt to reconnect
            if connection.get("active", False) and not self._shutdown_event.is_set():
                logger.info(f"Connection lost for stream {stream_id}, attempting to reconnect")
                task = asyncio.create_task(self._attempt_reconnection(stream_id))
                self._reconnection_tasks[stream_id] = task
            else:
                logger.debug(f"Message processing ended for stream {stream_id}")

    async def _handle_text_message(self, stream_id: str, data: str) -> None:
        """
        Process a text WebSocket message.

        Args:
            stream_id: The identifier of the stream that received the message.
            data: The raw text data of the message.
        """
        try:
            # Parse the JSON message
            message = json.loads(data)

            # Update last heartbeat time if this is a heartbeat message
            if "Heartbeat" in message:
                try:
                    heartbeat = Heartbeat.model_validate(message)
                    if stream_id in self._connections:
                        self._connections[stream_id][
                            "last_heartbeat"
                        ] = asyncio.get_event_loop().time()
                    logger.debug(
                        f"Heartbeat received for stream {stream_id}: {heartbeat.Timestamp}"
                    )
                    return
                except ValidationError:
                    logger.warning(f"Invalid heartbeat format for stream {stream_id}: {data}")

            # Check for error messages
            if "Error" in message:
                try:
                    error = StreamErrorResponse.model_validate(message)
                    logger.error(f"Stream error for {stream_id}: {error.Error} - {error.Message}")
                    return
                except ValidationError:
                    logger.warning(f"Invalid error format for stream {stream_id}: {data}")

            # Process message through callbacks
            if stream_id in self._subscription_callbacks:
                for callback in self._subscription_callbacks[stream_id]:
                    try:
                        callback(message)
                    except Exception as e:
                        logger.error(f"Error in callback for stream {stream_id}: {str(e)}")

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in message for stream {stream_id}: {data}")
        except Exception as e:
            logger.error(f"Error handling message for stream {stream_id}: {str(e)}")

    async def _attempt_reconnection(self, stream_id: str) -> None:
        """
        Attempt to reconnect a dropped stream.

        Args:
            stream_id: The identifier of the stream to reconnect.
        """
        if stream_id not in self._connections:
            logger.error(f"Cannot reconnect non-existent stream {stream_id}")
            return

        connection = self._connections[stream_id]
        if not connection.get("active", False) or self._shutdown_event.is_set():
            logger.debug(f"Not reconnecting inactive stream {stream_id}")
            return

        # Clear any existing reconnection task
        if stream_id in self._reconnection_tasks:
            self._reconnection_tasks[stream_id].cancel()

        # Create a new reconnection task
        task = asyncio.create_task(self._reconnect_with_backoff(stream_id))
        self._reconnection_tasks[stream_id] = task

    async def _reconnect_with_backoff(self, stream_id: str) -> None:
        """
        Implement exponential backoff reconnection strategy.

        Args:
            stream_id: The identifier of the stream to reconnect.
        """
        if stream_id not in self._connections:
            return

        connection = self._connections[stream_id]
        uri = connection.get("uri")

        if not uri:
            logger.error(f"Missing URI for stream {stream_id}, cannot reconnect")
            return

        # Clean up old connection resources
        try:
            if "websocket" in connection:
                await connection["websocket"].close()
            if "session" in connection:
                await connection["session"].close()
        except Exception as e:
            logger.debug(f"Error closing old connection for {stream_id}: {str(e)}")

        # Maintain the connection as active but remove from active streams set
        connection["active"] = True
        if stream_id in self._active_streams:
            self._active_streams.remove(stream_id)

        # Attempt reconnection with exponential backoff
        delay = self._RECONNECT_DELAY
        for attempt in range(1, self._MAX_RECONNECT_ATTEMPTS + 1):
            try:
                logger.info(
                    f"Reconnection attempt {attempt}/{self._MAX_RECONNECT_ATTEMPTS} for stream {stream_id}"
                )

                # Wait before attempting reconnection
                await asyncio.sleep(delay)

                # Attempt to reconnect
                await self.connect_stream(uri, stream_id)

                # If we get here, reconnection was successful
                logger.info(f"Successfully reconnected stream {stream_id}")
                return

            except Exception as e:
                logger.error(
                    f"Reconnection attempt {attempt} failed for stream {stream_id}: {str(e)}"
                )
                delay = min(delay * 2, 30)  # Exponential backoff with 30 second cap

        # If we get here, all reconnection attempts failed
        logger.error(
            f"Failed to reconnect stream {stream_id} after {self._MAX_RECONNECT_ATTEMPTS} attempts"
        )
        # Mark as inactive since we're giving up
        connection["active"] = False
        if stream_id in self._reconnection_tasks:
            del self._reconnection_tasks[stream_id]

    def is_connected(self, stream_id: str) -> bool:
        """
        Check if a specific stream is currently connected.

        Args:
            stream_id: The identifier of the stream to check.

        Returns:
            bool: True if the stream is connected, False otherwise.
        """
        return (
            stream_id in self._connections
            and self._connections[stream_id].get("active", False)
            and stream_id in self._active_streams
        )

    def get_connection_status(self) -> Dict[str, bool]:
        """
        Get the connection status of all streams.

        Returns:
            Dict[str, bool]: A dictionary mapping stream IDs to their connection status.
        """
        return {stream_id: self.is_connected(stream_id) for stream_id in self._connections}
