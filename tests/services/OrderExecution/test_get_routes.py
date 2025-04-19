import pytest
from src.ts_types.order_execution import Routes, Route


class TestGetRoutes:
    """Tests for the get_routes method in OrderExecutionService"""

    @pytest.mark.asyncio
    async def test_get_routes_success(self, order_execution_service, http_client_mock):
        """Test successful retrieval of routes"""
        # Mock response data
        mock_response = {
            "Routes": [
                {"Id": "AMEX", "AssetTypes": ["STOCK"], "Name": "AMEX"},
                {"Id": "ARCA", "AssetTypes": ["STOCK"], "Name": "ARCX"},
                {"Id": "Intelligent", "AssetTypes": ["STOCK", "OPTION"], "Name": "Intelligent"},
            ]
        }

        # Configure mock
        http_client_mock.get.return_value = mock_response

        # Call the method
        result = await order_execution_service.get_routes()

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with("/v3/orderexecution/routes")

        # Verify the result
        assert isinstance(result, Routes)
        assert len(result.Routes) == 3

        # Check first route
        assert isinstance(result.Routes[0], Route)
        assert result.Routes[0].Id == "AMEX"
        assert result.Routes[0].AssetTypes == ["STOCK"]
        assert result.Routes[0].Name == "AMEX"

        # Check second route
        assert result.Routes[1].Id == "ARCA"
        assert result.Routes[1].AssetTypes == ["STOCK"]
        assert result.Routes[1].Name == "ARCX"

        # Check third route
        assert result.Routes[2].Id == "Intelligent"
        assert result.Routes[2].AssetTypes == ["STOCK", "OPTION"]
        assert result.Routes[2].Name == "Intelligent"

    @pytest.mark.asyncio
    async def test_get_routes_empty(self, order_execution_service, http_client_mock):
        """Test getting an empty list of routes"""
        # Mock response data with empty routes array
        mock_response = {"Routes": []}

        # Configure mock
        http_client_mock.get.return_value = mock_response

        # Call the method
        result = await order_execution_service.get_routes()

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with("/v3/orderexecution/routes")

        # Verify the result
        assert isinstance(result, Routes)
        assert len(result.Routes) == 0

    @pytest.mark.asyncio
    async def test_get_routes_network_error(self, order_execution_service, http_client_mock):
        """Test network error handling when getting routes"""
        # Configure mock to raise exception
        http_client_mock.get.side_effect = Exception("Network error")

        # Verify the exception is propagated
        with pytest.raises(Exception, match="Network error"):
            await order_execution_service.get_routes()

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with("/v3/orderexecution/routes")

    @pytest.mark.asyncio
    async def test_get_routes_unauthorized(self, order_execution_service, http_client_mock):
        """Test unauthorized error handling when getting routes"""
        # Configure mock to raise unauthorized exception
        http_client_mock.get.side_effect = Exception("Unauthorized")

        # Verify the exception is propagated
        with pytest.raises(Exception, match="Unauthorized"):
            await order_execution_service.get_routes()

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with("/v3/orderexecution/routes")

    @pytest.mark.asyncio
    async def test_get_routes_forbidden(self, order_execution_service, http_client_mock):
        """Test forbidden error handling when getting routes"""
        # Configure mock to raise forbidden exception
        http_client_mock.get.side_effect = Exception("Forbidden")

        # Verify the exception is propagated
        with pytest.raises(Exception, match="Forbidden"):
            await order_execution_service.get_routes()

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with("/v3/orderexecution/routes")

    @pytest.mark.asyncio
    async def test_get_routes_bad_request(self, order_execution_service, http_client_mock):
        """Test bad request error handling when getting routes"""
        # Configure mock to raise bad request exception
        http_client_mock.get.side_effect = Exception("Bad request")

        # Verify the exception is propagated
        with pytest.raises(Exception, match="Bad request"):
            await order_execution_service.get_routes()

        # Verify the API was called correctly
        http_client_mock.get.assert_called_once_with("/v3/orderexecution/routes")
