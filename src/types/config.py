from typing import Literal, Optional
from pydantic import BaseModel


class ClientConfig(BaseModel):
    """
    Configuration settings for the TradeStation API client.
    """

    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    refresh_token: Optional[str] = None
    max_concurrent_streams: Optional[int] = None
    environment: Optional[Literal["Simulation", "Live"]] = None


class AuthResponse(BaseModel):
    """
    Response from the authentication endpoint.
    """

    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class ApiError(BaseModel):
    """
    Error response from API endpoints.
    """

    error: str
    error_description: Optional[str] = None
    status: Optional[int] = None
