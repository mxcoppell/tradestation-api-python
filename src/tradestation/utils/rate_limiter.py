import asyncio
import time
from typing import Dict, List, Optional, TypedDict, Union


class RateLimit(TypedDict):
    limit: int
    remaining: int
    resetTime: int


class RateLimiter:
    """
    Manages API rate limits for the TradeStation API.

    This class tracks request counts, enforces limits, and handles throttling
    to prevent 429 Too Many Requests errors from the API.
    """

    def __init__(self, default_limit: int = 120) -> None:
        """
        Initialize the RateLimiter with default rate limit settings.

        Args:
            default_limit: Default number of requests allowed per minute. Defaults to 120.
        """
        self._limits: Dict[str, RateLimit] = {}
        self._queues: Dict[str, List[asyncio.Future]] = {}
        self.default_limit = default_limit

    def update_limits(self, endpoint: str, headers: Dict[str, Union[str, int]]) -> None:
        """
        Update rate limit information based on response headers.

        Args:
            endpoint: The API endpoint being accessed.
            headers: Response headers containing rate limit information.
        """
        limit = int(headers.get("x-ratelimit-limit", self.default_limit))
        remaining = int(headers.get("x-ratelimit-remaining", 0))
        reset_time = int(headers.get("x-ratelimit-reset", 0)) * 1000  # Convert to milliseconds

        self._limits[endpoint] = {"limit": limit, "remaining": remaining, "resetTime": reset_time}

    async def wait_for_slot(self, endpoint: str) -> None:
        """
        Wait for a rate limit slot to become available.

        This method will block until a rate limit slot becomes available
        for the specified endpoint.

        Args:
            endpoint: The API endpoint to check rate limits for.
        """
        queue = self._queues.get(endpoint, [])
        self._queues[endpoint] = queue

        current_limit = self._limits.get(endpoint)
        if not current_limit or current_limit["remaining"] > 0:
            return

        loop = asyncio.get_running_loop()
        wait_future = loop.create_future()

        time_to_reset = current_limit["resetTime"] - int(time.time() * 1000)
        if time_to_reset > 0:
            # Wait for reset time
            await asyncio.sleep(time_to_reset / 1000)  # Convert to seconds

        queue.append(wait_future)

        if len(queue) == 1:
            # This is the first request in the queue
            self._limits[endpoint] = {
                **current_limit,
                "remaining": current_limit["limit"],
                "resetTime": int(time.time() * 1000) + 60000,  # Reset in 1 minute
            }
            wait_future.set_result(None)
        else:
            # Wait for the previous request
            previous_future = queue[-2]
            await previous_future
            wait_future.set_result(None)

        # Clean up the queue
        queue.remove(wait_future)
        if len(queue) == 0:
            self._queues.pop(endpoint, None)

    def get_rate_limit(self, endpoint: str) -> Optional[RateLimit]:
        """
        Get current rate limit information for an endpoint.

        Args:
            endpoint: The API endpoint to get rate limits for.

        Returns:
            Rate limit information or None if not available.
        """
        return self._limits.get(endpoint)
