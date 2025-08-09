"""Tests for Registry SDK hook system."""

import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock

from registry.src.smithery_registry.core.http_client import HTTPClient, HTTPClientOptions
from registry.src.smithery_registry.core.config import SDKConfig


class TestHTTPClientHooks:
    """Test cases for HTTP client hook system."""
    
    @pytest.mark.asyncio
    async def test_before_request_hook(self):
        """Test that beforeRequest hooks are called correctly."""
        options = HTTPClientOptions(
            base_url="https://api.example.com",
            timeout=30.0
        )
        client = HTTPClient(options)
        
        # Mock the underlying httpx client
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        client._client.send = AsyncMock(return_value=mock_response)
        
        # Add a beforeRequest hook
        hook_called = False
        async def before_hook(request):
            nonlocal hook_called
            hook_called = True
            # Modify the request
            request.headers["X-Custom-Header"] = "test"
            return request
        
        client.add_hook("beforeRequest", before_hook)
        
        # Make a request
        await client.request("GET", "/test")
        
        assert hook_called
        # Verify the request was sent
        client._client.send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_response_hook(self):
        """Test that response hooks are called correctly."""
        options = HTTPClientOptions(
            base_url="https://api.example.com",
            timeout=30.0
        )
        client = HTTPClient(options)
        
        # Mock the underlying httpx client
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        client._client.send = AsyncMock(return_value=mock_response)
        
        # Add a response hook
        hook_called = False
        captured_response = None
        async def response_hook(response, request):
            nonlocal hook_called, captured_response
            hook_called = True
            captured_response = response
        
        client.add_hook("response", response_hook)
        
        # Make a request
        result = await client.request("GET", "/test")
        
        assert hook_called
        assert captured_response == mock_response
        assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_request_error_hook(self):
        """Test that requestError hooks are called on errors."""
        options = HTTPClientOptions(
            base_url="https://api.example.com",
            timeout=30.0
        )
        client = HTTPClient(options)
        
        # Mock the underlying httpx client to raise an error
        test_error = httpx.ConnectError("Connection failed")
        client._client.send = AsyncMock(side_effect=test_error)
        
        # Add an error hook
        hook_called = False
        captured_error = None
        async def error_hook(error, request):
            nonlocal hook_called, captured_error
            hook_called = True
            captured_error = error
        
        client.add_hook("requestError", error_hook)
        
        # Disable retries for this test
        client.options.retry_config.max_retries = 0
        
        # Make a request that will fail
        with pytest.raises(httpx.ConnectError):
            await client.request("GET", "/test")
        
        assert hook_called
        assert captured_error == test_error
    
    @pytest.mark.asyncio
    async def test_multiple_hooks(self):
        """Test that multiple hooks can be registered and called."""
        options = HTTPClientOptions(
            base_url="https://api.example.com",
            timeout=30.0
        )
        client = HTTPClient(options)
        
        # Mock the underlying httpx client
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        client._client.send = AsyncMock(return_value=mock_response)
        
        # Track hook calls
        hook_calls = []
        
        # Add multiple hooks
        async def hook1(request):
            hook_calls.append("before1")
            return request
        
        async def hook2(request):
            hook_calls.append("before2")
            return request
        
        async def response_hook(response, request):
            hook_calls.append("response")
        
        client.add_hook("beforeRequest", hook1)
        client.add_hook("beforeRequest", hook2)
        client.add_hook("response", response_hook)
        
        # Make a request
        await client.request("GET", "/test")
        
        # All hooks should be called in order
        assert hook_calls == ["before1", "before2", "response"]