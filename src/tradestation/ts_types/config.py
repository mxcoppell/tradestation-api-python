from typing import Any, Literal, Optional, TypeVar, Union

from pydantic import BaseModel, BeforeValidator, field_validator
from typing_extensions import Annotated

T = TypeVar("T")


def normalize_environment(v: Optional[str]) -> Optional[str]:
    """
    Normalize environment string to proper case.

    Args:
        v: Input environment string

    Returns:
        Normalized environment string ("Simulation" or "Live") or None
    """
    if v is None:
        return None

    if isinstance(v, str):
        if v.lower() == "simulation":
            return "Simulation"
        elif v.lower() == "live":
            return "Live"

    # Return original value to allow Literal validation to fail naturally
    return v


# Define a type that first normalizes the environment string
NormalizedEnvironment = Annotated[
    Optional[Literal["Simulation", "Live"]], BeforeValidator(normalize_environment)
]


class ClientConfig(BaseModel):
    """
    Configuration settings for the TradeStation API client.
    """

    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    refresh_token: Optional[str] = None
    max_concurrent_streams: Optional[int] = None
    environment: NormalizedEnvironment = None

    @field_validator("environment")
    @classmethod
    def normalize_environment(cls, env: Optional[str]) -> Optional[str]:
        """
        Normalize the environment value to either "Simulation" or "Live"
        regardless of the input case.
        """
        if env is None:
            return None
        if env.lower() == "simulation":
            return "Simulation"
        return "Live"

    def get(self, key: str, default: Any = None) -> Any:
        """
        Dictionary-like get method for compatibility with code expecting a dict.

        Args:
            key: The attribute name to get
            default: Default value if attribute doesn't exist

        Returns:
            The attribute value or default if not found
        """
        return getattr(self, key, default)


class AuthResponse(BaseModel):
    """
    Response from the authentication endpoint.
    """

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str
    expires_in: int


class ApiError(BaseModel):
    """
    Error response from API endpoints.
    """

    error: str
    error_description: Optional[str] = None
    status: Optional[int] = None
