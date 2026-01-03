"""
TradeStation API exception hierarchy.

This module defines a comprehensive set of exceptions for the TradeStation API
to provide more specific and actionable error handling.
"""

from typing import Any, Dict, Optional
import aiohttp


class TradeStationAPIError(Exception):
    """Base exception for all TradeStation API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        request_id: Optional[str] = None,
        response: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        """
        Initialize the exception with context information.

        Args:
            message: Error message
            status_code: HTTP status code
            request_id: API request ID for troubleshooting
            response: Full response content
            original_error: Original exception that caused this error
        """
        self.status_code = status_code
        self.request_id = request_id
        self.response = response
        self.original_error = original_error

        # Create a detailed error message
        detailed_message = message
        if status_code:
            detailed_message += f" (Status: {status_code})"
        if request_id:
            detailed_message += f" (Request ID: {request_id})"

        super().__init__(detailed_message)


class TradeStationAuthError(TradeStationAPIError):
    """Raised when authentication fails (401, 403 errors)."""

    def __init__(
        self,
        message: str = "Authentication failed. Please check your credentials or refresh your tokens.",
        **kwargs,
    ):
        super().__init__(message, **kwargs)


class TradeStationRateLimitError(TradeStationAPIError):
    """Raised when hitting rate limits (429 errors)."""

    def __init__(
        self,
        message: str = "API rate limit exceeded. Please reduce request frequency.",
        retry_after: Optional[int] = None,
        **kwargs,
    ):
        self.retry_after = retry_after

        # Add retry information if available
        if retry_after:
            message += f" Retry after {retry_after} seconds."

        super().__init__(message, **kwargs)


class TradeStationResourceNotFoundError(TradeStationAPIError):
    """Raised when a resource is not found (404 errors)."""

    def __init__(
        self,
        message: str = "The requested resource was not found.",
        resource: Optional[str] = None,
        **kwargs,
    ):
        self.resource = resource

        if resource:
            message += f" Resource: {resource}"

        super().__init__(message, **kwargs)


class TradeStationValidationError(TradeStationAPIError):
    """Raised when request validation fails (400 errors)."""

    def __init__(
        self,
        message: str = "The request was invalid or improperly formatted.",
        validation_errors: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        self.validation_errors = validation_errors

        # Move validation_errors to message only if it contains relevant info
        # and not just what we've already extracted from the API response
        if validation_errors and not message.endswith(str(validation_errors)):
            message += f" Validation errors: {validation_errors}"

        super().__init__(message, **kwargs)


class TradeStationNetworkError(TradeStationAPIError):
    """Raised when network connectivity issues occur."""

    def __init__(
        self,
        message: str = "Network error occurred. Please check your internet connection.",
        original_error: Optional[Exception] = None,
        **kwargs,
    ):
        if original_error and not message.endswith(str(original_error)):
            message += f" Original error: {str(original_error)}"

        super().__init__(message, original_error=original_error, **kwargs)


class TradeStationServerError(TradeStationAPIError):
    """Raised when server errors occur (5xx errors)."""

    def __init__(self, message: str = "Server error occurred. Please try again later.", **kwargs):
        super().__init__(message, **kwargs)


class TradeStationTimeoutError(TradeStationAPIError):
    """Raised when requests time out."""

    def __init__(self, message: str = "Request timed out. Please try again later.", **kwargs):
        super().__init__(message, **kwargs)


class TradeStationStreamError(TradeStationAPIError):
    """Raised when errors occur with streaming connections."""

    def __init__(self, message: str = "Error in streaming connection.", **kwargs):
        super().__init__(message, **kwargs)


# Mapping of HTTP status codes to exception classes
def map_http_error(
    status_code: int, response_data: Optional[Dict[str, Any]] = None
) -> TradeStationAPIError:
    """
    Map an HTTP status code to the appropriate exception class.

    Args:
        status_code: HTTP status code from the response
        response_data: Optional response data with error details

    Returns:
        An appropriate TradeStationAPIError subclass instance
    """
    error_message = "An error occurred with the TradeStation API."
    if response_data and isinstance(response_data, dict):
        # Extract error details from response if available
        if "error_description" in response_data:
            error_message = response_data["error_description"]
        elif "error" in response_data:
            error_message = response_data["error"]
        elif "message" in response_data:
            error_message = response_data["message"]

    # Extract request ID if available
    request_id = None
    if response_data and isinstance(response_data, dict) and "request_id" in response_data:
        request_id = response_data["request_id"]

    # Map status code to appropriate exception
    if status_code == 400:
        # Extract only validation-specific fields, not the entire response
        validation_errors = None
        if response_data and isinstance(response_data, dict):
            # Look for common validation error field names
            for field in ["errors", "validation_errors", "field_errors", "validationErrors"]:
                if field in response_data:
                    validation_errors = response_data[field]
                    break

            # If no specific validation field found but the response has a details field
            # that contains field-level errors, use that
            if validation_errors is None and "details" in response_data:
                if isinstance(response_data["details"], dict) and any(
                    k
                    for k in response_data["details"].keys()
                    if k not in ["message", "error", "error_description", "request_id"]
                ):
                    validation_errors = response_data["details"]

        return TradeStationValidationError(
            message=error_message,
            status_code=status_code,
            request_id=request_id,
            response=response_data,
            # Pass only specific validation errors, not the entire response
            validation_errors=validation_errors,
        )
    elif status_code in (401, 403):
        return TradeStationAuthError(
            message=error_message,
            status_code=status_code,
            request_id=request_id,
            response=response_data,
        )
    elif status_code == 404:
        return TradeStationResourceNotFoundError(
            message=error_message,
            status_code=status_code,
            request_id=request_id,
            response=response_data,
        )
    elif status_code == 429:
        retry_after = None
        if response_data and isinstance(response_data, dict) and "retry_after" in response_data:
            retry_after = response_data["retry_after"]

        return TradeStationRateLimitError(
            message=error_message,
            status_code=status_code,
            request_id=request_id,
            response=response_data,
            retry_after=retry_after,
        )
    elif 500 <= status_code < 600:
        return TradeStationServerError(
            message=error_message,
            status_code=status_code,
            request_id=request_id,
            response=response_data,
        )
    else:
        # Default case for other status codes
        return TradeStationAPIError(
            message=error_message,
            status_code=status_code,
            request_id=request_id,
            response=response_data,
        )


def handle_request_exception(exc: Exception) -> TradeStationAPIError:
    """
    Convert aiohttp exceptions to TradeStation exceptions.

    Args:
        exc: The original exception

    Returns:
        An appropriate TradeStationAPIError subclass
    """
    if isinstance(exc, aiohttp.ClientResponseError):
        # Map HTTP errors based on status code
        status_code = getattr(exc, "status", None)
        return map_http_error(status_code, None)
    elif isinstance(exc, aiohttp.ClientConnectorError):
        return TradeStationNetworkError(original_error=exc)
    elif isinstance(exc, aiohttp.ClientOSError):
        return TradeStationNetworkError(original_error=exc)
    elif isinstance(exc, aiohttp.ServerDisconnectedError):
        return TradeStationNetworkError(
            message="Server disconnected unexpectedly. Please try again.", original_error=exc
        )
    elif isinstance(exc, aiohttp.ClientPayloadError):
        return TradeStationAPIError(
            message="Error processing server response payload.", original_error=exc
        )
    elif isinstance(exc, aiohttp.ClientTimeout):
        return TradeStationTimeoutError(original_error=exc)
    else:
        # For unexpected exceptions, wrap in base API error
        return TradeStationAPIError(message=f"Unexpected error: {str(exc)}", original_error=exc)
