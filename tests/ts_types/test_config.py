import pytest
from pydantic import ValidationError

from src.ts_types.config import ClientConfig, AuthResponse, ApiError


class TestClientConfig:
    def test_default_values(self):
        """Test that default values are correctly applied."""
        config = ClientConfig()
        assert config.client_id is None
        assert config.client_secret is None
        assert config.refresh_token is None
        assert config.max_concurrent_streams is None
        assert config.environment is None

    def test_setting_values(self):
        """Test that values can be properly set."""
        config = ClientConfig(
            client_id="test_id",
            client_secret="test_secret",
            refresh_token="test_refresh_token",
            max_concurrent_streams=5,
            environment="Simulation",
        )
        assert config.client_id == "test_id"
        assert config.client_secret == "test_secret"
        assert config.refresh_token == "test_refresh_token"
        assert config.max_concurrent_streams == 5
        assert config.environment == "Simulation"

    def test_environment_validation(self):
        """Test that environment only accepts valid values."""
        # Valid values
        ClientConfig(environment="Simulation")
        ClientConfig(environment="Live")

        # Invalid value
        with pytest.raises(ValidationError):
            ClientConfig(environment="Invalid")


class TestAuthResponse:
    def test_required_fields(self):
        """Test that all required fields must be provided."""
        with pytest.raises(ValidationError):
            AuthResponse()

        # Valid response
        auth = AuthResponse(
            access_token="access_token_value",
            refresh_token="refresh_token_value",
            token_type="bearer",
            expires_in=3600,
        )
        assert auth.access_token == "access_token_value"
        assert auth.refresh_token == "refresh_token_value"
        assert auth.token_type == "bearer"
        assert auth.expires_in == 3600


class TestApiError:
    def test_minimal_error(self):
        """Test that an error can be created with just the error field."""
        error = ApiError(error="Unauthorized")
        assert error.error == "Unauthorized"
        assert error.error_description is None
        assert error.status is None

    def test_complete_error(self):
        """Test that an error can be created with all fields."""
        error = ApiError(error="Unauthorized", error_description="Invalid credentials", status=401)
        assert error.error == "Unauthorized"
        assert error.error_description == "Invalid credentials"
        assert error.status == 401
