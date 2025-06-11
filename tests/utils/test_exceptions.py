"""
Tests for the TradeStation API exception hierarchy.
"""

import unittest
import aiohttp
from unittest.mock import Mock, patch

from tradestation.utils.exceptions import (
    TradeStationAPIError,
    TradeStationAuthError,
    TradeStationRateLimitError,
    TradeStationResourceNotFoundError,
    TradeStationValidationError,
    TradeStationNetworkError,
    TradeStationServerError,
    TradeStationTimeoutError,
    TradeStationStreamError,
    map_http_error,
    handle_request_exception,
)


class TestExceptions(unittest.TestCase):
    """Test cases for the TradeStation API exception classes."""

    def test_base_error(self):
        """Test the base TradeStationAPIError class."""
        # Create error with minimal info
        error = TradeStationAPIError("An error occurred")
        self.assertEqual(str(error), "An error occurred")
        self.assertIsNone(error.status_code)
        self.assertIsNone(error.request_id)
        self.assertIsNone(error.response)
        
        # Create error with full context
        error = TradeStationAPIError(
            message="API error",
            status_code=500,
            request_id="req-123",
            response={"error": "server_error"}
        )
        self.assertEqual(str(error), "API error (Status: 500) (Request ID: req-123)")
        self.assertEqual(error.status_code, 500)
        self.assertEqual(error.request_id, "req-123")
        self.assertEqual(error.response, {"error": "server_error"})

    def test_auth_error(self):
        """Test the TradeStationAuthError class."""
        # Test with default message
        error = TradeStationAuthError()
        self.assertIn("Authentication failed", str(error))
        
        # Test with custom message and parameters
        error = TradeStationAuthError(
            message="Invalid client ID",
            status_code=401,
            request_id="req-auth-123"
        )
        self.assertIn("Invalid client ID", str(error))
        self.assertEqual(error.status_code, 401)
        self.assertEqual(error.request_id, "req-auth-123")

    def test_rate_limit_error(self):
        """Test the TradeStationRateLimitError class."""
        # Test with retry_after information
        error = TradeStationRateLimitError(retry_after=30)
        self.assertIn("API rate limit exceeded", str(error))
        self.assertIn("Retry after 30 seconds", str(error))
        self.assertEqual(error.retry_after, 30)
        
        # Test without retry_after
        error = TradeStationRateLimitError()
        self.assertIn("API rate limit exceeded", str(error))
        self.assertIsNone(error.retry_after)

    def test_resource_not_found_error(self):
        """Test the TradeStationResourceNotFoundError class."""
        # Test with resource information
        error = TradeStationResourceNotFoundError(resource="/v3/marketdata/quotes")
        self.assertIn("The requested resource was not found", str(error))
        self.assertIn("Resource: /v3/marketdata/quotes", str(error))
        self.assertEqual(error.resource, "/v3/marketdata/quotes")
        
        # Test without resource
        error = TradeStationResourceNotFoundError()
        self.assertIn("The requested resource was not found", str(error))
        self.assertIsNone(error.resource)

    def test_validation_error(self):
        """Test the TradeStationValidationError class."""
        # Test with validation errors
        validation_errors = {"symbol": "Invalid symbol format"}
        error = TradeStationValidationError(validation_errors=validation_errors)
        self.assertIn("The request was invalid", str(error))
        self.assertIn("Validation errors: {'symbol': 'Invalid symbol format'}", str(error))
        self.assertEqual(error.validation_errors, validation_errors)
        
        # Test without validation errors
        error = TradeStationValidationError()
        self.assertIn("The request was invalid", str(error))
        self.assertIsNone(error.validation_errors)

    def test_network_error(self):
        """Test the TradeStationNetworkError class."""
        # Test with original error
        original = ConnectionError("Connection refused")
        error = TradeStationNetworkError(original_error=original)
        self.assertIn("Network error occurred", str(error))
        self.assertIn("Original error: Connection refused", str(error))
        self.assertEqual(error.original_error, original)
        
        # Test without original error
        error = TradeStationNetworkError()
        self.assertIn("Network error occurred", str(error))
        self.assertIsNone(error.original_error)

    def test_map_http_error(self):
        """Test mapping HTTP status codes to appropriate exceptions."""
        # Test 400 - Validation Error
        error = map_http_error(400, {"error": "Invalid request"})
        self.assertIsInstance(error, TradeStationValidationError)
        self.assertEqual(error.status_code, 400)
        
        # Test 401 - Auth Error
        error = map_http_error(401, {"error": "Unauthorized"})
        self.assertIsInstance(error, TradeStationAuthError)
        self.assertEqual(error.status_code, 401)
        
        # Test 403 - Auth Error
        error = map_http_error(403, {"error": "Forbidden"})
        self.assertIsInstance(error, TradeStationAuthError)
        self.assertEqual(error.status_code, 403)
        
        # Test 404 - Resource Not Found Error
        error = map_http_error(404, {"error": "Not found"})
        self.assertIsInstance(error, TradeStationResourceNotFoundError)
        self.assertEqual(error.status_code, 404)
        
        # Test 429 - Rate Limit Error
        error = map_http_error(429, {"error": "Too many requests", "retry_after": 30})
        self.assertIsInstance(error, TradeStationRateLimitError)
        self.assertEqual(error.status_code, 429)
        self.assertEqual(error.retry_after, 30)
        
        # Test 500 - Server Error
        error = map_http_error(500, {"error": "Internal server error"})
        self.assertIsInstance(error, TradeStationServerError)
        self.assertEqual(error.status_code, 500)
        
        # Test other status code - Generic API Error
        error = map_http_error(418, {"error": "I'm a teapot"})
        self.assertIsInstance(error, TradeStationAPIError)
        self.assertEqual(error.status_code, 418)
        
        # Test message extraction from different response formats
        error = map_http_error(400, {"error_description": "Detailed error"})
        # Test that the message contains the extracted error description
        self.assertIn("Detailed error", str(error))
        
        error = map_http_error(400, {"error": "Basic error"})
        self.assertIn("Basic error", str(error))
        
        error = map_http_error(400, {"message": "Message format"})
        self.assertIn("Message format", str(error))

    def test_handle_request_exception(self):
        """Test converting aiohttp exceptions to TradeStation exceptions."""
        # Test ClientResponseError
        resp_error = aiohttp.ClientResponseError(
            request_info=Mock(),
            history=(),
            status=401,
            message="Unauthorized",
        )
        error = handle_request_exception(resp_error)
        self.assertIsInstance(error, TradeStationAuthError)
        
        # Test ClientConnectorError
        connector_error = aiohttp.ClientConnectorError(Mock(), OSError())
        error = handle_request_exception(connector_error)
        self.assertIsInstance(error, TradeStationNetworkError)
        
        # Test ClientOSError
        os_error = aiohttp.ClientOSError()
        error = handle_request_exception(os_error)
        self.assertIsInstance(error, TradeStationNetworkError)
        
        # Test ServerDisconnectedError
        disconnected_error = aiohttp.ServerDisconnectedError()
        error = handle_request_exception(disconnected_error)
        self.assertIsInstance(error, TradeStationNetworkError)
        self.assertIn("Server disconnected unexpectedly", str(error))
        
        # Test ClientPayloadError
        payload_error = aiohttp.ClientPayloadError()
        error = handle_request_exception(payload_error)
        self.assertIsInstance(error, TradeStationAPIError)
        self.assertIn("Error processing server response payload", str(error))
        
        # Test ClientTimeout
        timeout_error = aiohttp.ClientTimeout()
        error = handle_request_exception(timeout_error)
        self.assertIsInstance(error, TradeStationTimeoutError)
        
        # Test generic exception
        generic_error = ValueError("Random error")
        error = handle_request_exception(generic_error)
        self.assertIsInstance(error, TradeStationAPIError)
        self.assertIn("Unexpected error", str(error))


if __name__ == "__main__":
    unittest.main() 