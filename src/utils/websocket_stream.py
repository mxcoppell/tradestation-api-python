import asyncio
import json
from typing import Dict, List, Optional, Any, Callable, Awaitable
import aiohttp


class WebSocketStream:
    """
    Manages a WebSocket connection to the TradeStation API for streaming data.
    """

    def __init__(self, url: str, headers: Dict[str, str], debug: bool = False):
        """
        Initialize a WebSocket stream.

        Args:
            url: The WebSocket URL to connect to
            headers: Headers to send with the connection request
            debug: Whether to print debug messages
        """
        self.url = url
        self.headers = headers
        self.debug = debug
        self.session: Optional[aiohttp.ClientSession] = None
        self.ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self.is_connected = False
        self.callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
        self._task: Optional[asyncio.Task] = None

    def _debug_print(self, message: str) -> None:
        """Print a debug message if debug mode is enabled."""
        if self.debug:
            print(message)

    async def connect(self) -> None:
        """
        Establish a connection to the WebSocket endpoint.
        """
        if self.is_connected:
            return

        self.session = aiohttp.ClientSession()
        try:
            self.ws = await self.session.ws_connect(self.url, headers=self.headers)
            self.is_connected = True
            self._debug_print(f"Connected to WebSocket: {self.url}")

            # Start listening for messages if a callback is set
            if self.callback:
                self._start_listening()
        except Exception as e:
            await self.close()
            raise RuntimeError(f"Failed to connect to WebSocket: {e}")

    def _start_listening(self) -> None:
        """
        Start a background task to listen for messages.
        """
        if self._task is not None:
            return

        self._task = asyncio.create_task(self._listen_for_messages())

    async def _listen_for_messages(self) -> None:
        """
        Listen for messages on the WebSocket connection and process them.
        """
        if not self.ws or not self.callback:
            return

        try:
            async for msg in self.ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await self.callback(data)
                    except json.JSONDecodeError:
                        self._debug_print(f"Received non-JSON message: {msg.data}")
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    self._debug_print(
                        f"WebSocket connection closed with exception: {self.ws.exception()}"
                    )
                    break
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    self._debug_print("WebSocket connection closed")
                    break
        except Exception as e:
            self._debug_print(f"Error in WebSocket listener: {e}")
        finally:
            await self.close()

    async def send(self, data: Dict[str, Any]) -> None:
        """
        Send data to the WebSocket.

        Args:
            data: The data to send
        """
        if not self.is_connected or not self.ws:
            raise RuntimeError("WebSocket is not connected")

        await self.ws.send_json(data)

    def set_callback(self, callback: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
        """
        Set a callback function to process incoming messages.

        Args:
            callback: Async function that processes incoming messages
        """
        self.callback = callback

        # Start listening if we're already connected
        if self.is_connected:
            self._start_listening()

    async def close(self) -> None:
        """
        Close the WebSocket connection and clean up resources.
        """
        self.is_connected = False

        # Cancel the listening task if it exists
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

        # Close the WebSocket connection
        if self.ws:
            await self.ws.close()
            self.ws = None

        # Close the session
        if self.session:
            await self.session.close()
            self.session = None
