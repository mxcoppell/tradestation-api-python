import asyncio
from typing import Dict, List, Optional, Union, Any

from ..ts_types.config import ClientConfig
from .websocket_stream import WebSocketStream


class StreamManager:
    def __init__(self, config: Union[Dict[str, Any], ClientConfig], debug: bool = False):
        """
        Initialize StreamManager with configuration.

        Args:
            config: Configuration settings (dict or ClientConfig object)
            debug: Whether to print debug messages
        """
        # Convert config to ClientConfig if it's a dict
        if not isinstance(config, ClientConfig):
            config = ClientConfig(**config)

        self.max_concurrent_streams = config.max_concurrent_streams or 10
        self.active_streams: Dict[str, WebSocketStream] = {}
        self.debug = debug

    async def create_stream(self, url: str, headers: Dict[str, str]) -> WebSocketStream:
        """
        Create a new websocket stream.

        Args:
            url: The URL to connect to
            headers: Headers to send with the connection request

        Returns:
            The created WebSocketStream
        """
        if len(self.active_streams) >= self.max_concurrent_streams:
            raise ValueError(
                f"Maximum number of concurrent streams ({self.max_concurrent_streams}) reached"
            )

        stream = WebSocketStream(url, headers, debug=self.debug)
        await stream.connect()

        # Store the stream with a unique ID
        stream_id = str(len(self.active_streams) + 1)
        self.active_streams[stream_id] = stream

        return stream

    async def close_stream(self, stream_id: str) -> None:
        """
        Close a specific stream.

        Args:
            stream_id: The ID of the stream to close
        """
        if stream_id in self.active_streams:
            stream = self.active_streams.pop(stream_id)
            await stream.close()

    async def close_all_streams(self) -> None:
        """
        Close all active streams.
        """
        for stream_id in list(self.active_streams.keys()):
            await self.close_stream(stream_id)

    async def close(self) -> None:
        """
        Close all streams and clean up resources.
        """
        await self.close_all_streams()
