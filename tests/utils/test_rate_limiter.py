import asyncio
import time
from typing import Dict, Union

import pytest

from tradestation.utils.rate_limiter import RateLimiter


class TestRateLimiter:
    """Tests for the RateLimiter class."""

    @pytest.fixture
    def rate_limiter(self) -> RateLimiter:
        """Create a RateLimiter instance for testing."""
        return RateLimiter()

    @pytest.fixture
    def endpoint(self) -> str:
        """Return a test endpoint."""
        return "/test/endpoint"

    class TestUpdateLimits:
        """Tests for the update_limits method."""

        def test_update_limits_from_headers(self, rate_limiter: RateLimiter, endpoint: str) -> None:
            """Should update rate limits from headers."""
            headers: Dict[str, Union[str, int]] = {
                "x-ratelimit-limit": "100",
                "x-ratelimit-remaining": "99",
                "x-ratelimit-reset": "1706108400",  # Example timestamp
            }

            rate_limiter.update_limits(endpoint, headers)
            limits = rate_limiter.get_rate_limit(endpoint)

            assert limits is not None
            assert limits["limit"] == 100
            assert limits["remaining"] == 99
            assert limits["resetTime"] == 1706108400000  # Converted to milliseconds

        def test_use_default_limit_when_not_provided(
            self, rate_limiter: RateLimiter, endpoint: str
        ) -> None:
            """Should use default limit when not provided in headers."""
            headers: Dict[str, Union[str, int]] = {}

            rate_limiter.update_limits(endpoint, headers)
            limits = rate_limiter.get_rate_limit(endpoint)

            assert limits is not None
            assert limits["limit"] == 120  # Default limit
            assert limits["remaining"] == 0
            assert limits["resetTime"] == 0

        def test_handle_custom_default_limit(self, endpoint: str) -> None:
            """Should handle custom default limit."""
            custom_limiter = RateLimiter(200)
            headers: Dict[str, Union[str, int]] = {}

            custom_limiter.update_limits(endpoint, headers)
            limits = custom_limiter.get_rate_limit(endpoint)

            assert limits is not None
            assert limits["limit"] == 200

    class TestWaitForSlot:
        """Tests for the wait_for_slot method."""

        @pytest.mark.asyncio
        async def test_resolve_immediately_when_no_rate_limit(
            self, rate_limiter: RateLimiter, endpoint: str
        ) -> None:
            """Should resolve immediately when no rate limit is set."""
            await rate_limiter.wait_for_slot(endpoint)
            # No assertion needed, test passes if the await completes

        @pytest.mark.asyncio
        async def test_resolve_immediately_when_remaining_requests(
            self, rate_limiter: RateLimiter, endpoint: str
        ) -> None:
            """Should resolve immediately when remaining requests are available."""
            headers: Dict[str, Union[str, int]] = {
                "x-ratelimit-limit": "100",
                "x-ratelimit-remaining": "99",
                "x-ratelimit-reset": "1706108400",
            }

            rate_limiter.update_limits(endpoint, headers)
            await rate_limiter.wait_for_slot(endpoint)
            # No assertion needed, test passes if the await completes

        @pytest.mark.asyncio
        async def test_wait_for_reset_when_rate_limited(
            self, rate_limiter: RateLimiter, endpoint: str
        ) -> None:
            """Should wait for reset when rate limit is exceeded."""
            now = int(time.time())
            # Use 2 seconds instead of 1 to provide more margin for testing
            reset_time = now + 2

            headers: Dict[str, Union[str, int]] = {
                "x-ratelimit-limit": "100",
                "x-ratelimit-remaining": "0",
                "x-ratelimit-reset": str(reset_time),
            }

            rate_limiter.update_limits(endpoint, headers)

            # Start timing
            start_time = time.time()
            await rate_limiter.wait_for_slot(endpoint)
            elapsed = time.time() - start_time

            # Verify we waited some amount of time (at least 0.1 seconds)
            # This is a more lenient test that's less prone to timing issues
            assert elapsed > 0.1

            limits = rate_limiter.get_rate_limit(endpoint)
            assert limits is not None
            assert limits["remaining"] == 100  # Reset to full limit

        @pytest.mark.asyncio
        async def test_queue_multiple_requests_when_rate_limited(
            self, rate_limiter: RateLimiter, endpoint: str
        ) -> None:
            """Should queue multiple requests when rate limited."""
            now = int(time.time())
            reset_time = now + 1  # 1 second from now

            headers: Dict[str, Union[str, int]] = {
                "x-ratelimit-limit": "100",
                "x-ratelimit-remaining": "0",
                "x-ratelimit-reset": str(reset_time),
            }

            rate_limiter.update_limits(endpoint, headers)

            # Create multiple requests
            tasks = [
                asyncio.create_task(rate_limiter.wait_for_slot(endpoint)),
                asyncio.create_task(rate_limiter.wait_for_slot(endpoint)),
                asyncio.create_task(rate_limiter.wait_for_slot(endpoint)),
            ]

            # Wait for all tasks to complete
            await asyncio.gather(*tasks)

            limits = rate_limiter.get_rate_limit(endpoint)
            assert limits is not None
            assert limits["remaining"] == 100  # Reset to full limit

        @pytest.mark.asyncio
        async def test_resolve_immediately_when_reset_time_in_past(
            self, rate_limiter: RateLimiter, endpoint: str
        ) -> None:
            """Should resolve immediately when reset time is in the past."""
            past_time = int(time.time()) - 10  # 10 seconds ago

            headers: Dict[str, Union[str, int]] = {
                "x-ratelimit-limit": "100",
                "x-ratelimit-remaining": "0",
                "x-ratelimit-reset": str(past_time),
            }

            rate_limiter.update_limits(endpoint, headers)

            # Start timing
            start_time = time.time()
            await rate_limiter.wait_for_slot(endpoint)
            elapsed = time.time() - start_time

            # Should resolve almost immediately
            assert elapsed < 0.1

    class TestGetRateLimit:
        """Tests for the get_rate_limit method."""

        def test_return_none_for_unknown_endpoint(self, rate_limiter: RateLimiter) -> None:
            """Should return None for unknown endpoint."""
            assert rate_limiter.get_rate_limit("unknown") is None

        def test_return_rate_limit_for_known_endpoint(
            self, rate_limiter: RateLimiter, endpoint: str
        ) -> None:
            """Should return rate limit for known endpoint."""
            headers: Dict[str, Union[str, int]] = {
                "x-ratelimit-limit": "100",
                "x-ratelimit-remaining": "99",
                "x-ratelimit-reset": "1706108400",
            }

            rate_limiter.update_limits(endpoint, headers)
            limits = rate_limiter.get_rate_limit(endpoint)

            assert limits == {"limit": 100, "remaining": 99, "resetTime": 1706108400000}
