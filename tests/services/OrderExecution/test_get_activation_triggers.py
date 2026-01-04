import pytest

from tradestation.ts_types.order_execution import ActivationTrigger, ActivationTriggers


class TestGetActivationTriggers:
    """Tests for the get_activation_triggers method in OrderExecutionService"""

    @pytest.mark.asyncio
    async def test_get_activation_triggers_success(self, order_execution_service, http_client_mock):
        """Test successful retrieval of activation triggers"""
        # Mock response data
        mock_response = {
            "ActivationTriggers": [
                {"Key": "Ask", "Name": "Ask", "Description": "Last ask price for the symbol"},
                {"Key": "Bid", "Name": "Bid", "Description": "Last bid price for the symbol"},
                {"Key": "Last", "Name": "Last", "Description": "Last trade price for the symbol"},
            ]
        }

        # Configure mock
        http_client_mock.get.return_value = mock_response

        # Call the method
        result = await order_execution_service.get_activation_triggers()

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with("/v3/orderexecution/activationtriggers")

        # Verify the result
        assert isinstance(result, ActivationTriggers)
        assert len(result.ActivationTriggers) == 3

        # Check first trigger
        assert isinstance(result.ActivationTriggers[0], ActivationTrigger)
        assert result.ActivationTriggers[0].Key == "Ask"
        assert result.ActivationTriggers[0].Name == "Ask"
        assert result.ActivationTriggers[0].Description == "Last ask price for the symbol"

        # Check second trigger
        assert result.ActivationTriggers[1].Key == "Bid"
        assert result.ActivationTriggers[1].Name == "Bid"
        assert result.ActivationTriggers[1].Description == "Last bid price for the symbol"

        # Check third trigger
        assert result.ActivationTriggers[2].Key == "Last"
        assert result.ActivationTriggers[2].Name == "Last"
        assert result.ActivationTriggers[2].Description == "Last trade price for the symbol"

    @pytest.mark.asyncio
    async def test_get_activation_triggers_empty(self, order_execution_service, http_client_mock):
        """Test getting an empty list of activation triggers"""
        # Mock response data with empty triggers array
        mock_response = {"ActivationTriggers": []}

        # Configure mock
        http_client_mock.get.return_value = mock_response

        # Call the method
        result = await order_execution_service.get_activation_triggers()

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with("/v3/orderexecution/activationtriggers")

        # Verify the result
        assert isinstance(result, ActivationTriggers)
        assert len(result.ActivationTriggers) == 0

    @pytest.mark.asyncio
    async def test_get_activation_triggers_network_error(
        self, order_execution_service, http_client_mock
    ):
        """Test network error handling when getting activation triggers"""
        # Configure mock to raise exception
        http_client_mock.get.side_effect = Exception("Network error")

        # Verify the exception is propagated
        with pytest.raises(Exception, match="Network error"):
            await order_execution_service.get_activation_triggers()

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with("/v3/orderexecution/activationtriggers")

    @pytest.mark.asyncio
    async def test_get_activation_triggers_unauthorized(
        self, order_execution_service, http_client_mock
    ):
        """Test unauthorized error handling when getting activation triggers"""
        # Configure mock to raise unauthorized exception
        http_client_mock.get.side_effect = Exception("Unauthorized")

        # Verify the exception is propagated
        with pytest.raises(Exception, match="Unauthorized"):
            await order_execution_service.get_activation_triggers()

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with("/v3/orderexecution/activationtriggers")

    @pytest.mark.asyncio
    async def test_get_activation_triggers_forbidden(
        self, order_execution_service, http_client_mock
    ):
        """Test forbidden error handling when getting activation triggers"""
        # Configure mock to raise forbidden exception
        http_client_mock.get.side_effect = Exception("Forbidden")

        # Verify the exception is propagated
        with pytest.raises(Exception, match="Forbidden"):
            await order_execution_service.get_activation_triggers()

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with("/v3/orderexecution/activationtriggers")

    @pytest.mark.asyncio
    async def test_get_activation_triggers_bad_request(
        self, order_execution_service, http_client_mock
    ):
        """Test bad request error handling when getting activation triggers"""
        # Configure mock to raise bad request exception
        http_client_mock.get.side_effect = Exception("Bad request")

        # Verify the exception is propagated
        with pytest.raises(Exception, match="Bad request"):
            await order_execution_service.get_activation_triggers()

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with("/v3/orderexecution/activationtriggers")

    @pytest.mark.asyncio
    async def test_get_activation_triggers_rate_limit_exceeded(
        self, order_execution_service, http_client_mock
    ):
        """Test rate limit exceeded error handling when getting activation triggers"""
        # Configure mock to raise rate limit exceeded exception
        http_client_mock.get.side_effect = Exception("Rate limit exceeded")

        # Verify the exception is propagated
        with pytest.raises(Exception, match="Rate limit exceeded"):
            await order_execution_service.get_activation_triggers()

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with("/v3/orderexecution/activationtriggers")

    @pytest.mark.asyncio
    async def test_get_activation_triggers_service_unavailable(
        self, order_execution_service, http_client_mock
    ):
        """Test service unavailable error handling when getting activation triggers"""
        # Configure mock to raise service unavailable exception
        http_client_mock.get.side_effect = Exception("Service unavailable")

        # Verify the exception is propagated
        with pytest.raises(Exception, match="Service unavailable"):
            await order_execution_service.get_activation_triggers()

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with("/v3/orderexecution/activationtriggers")

    @pytest.mark.asyncio
    async def test_get_activation_triggers_gateway_timeout(
        self, order_execution_service, http_client_mock
    ):
        """Test gateway timeout error handling when getting activation triggers"""
        # Configure mock to raise gateway timeout exception
        http_client_mock.get.side_effect = Exception("Gateway timeout")

        # Verify the exception is propagated
        with pytest.raises(Exception, match="Gateway timeout"):
            await order_execution_service.get_activation_triggers()

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with("/v3/orderexecution/activationtriggers")
