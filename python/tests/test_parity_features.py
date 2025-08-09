"""Tests for TypeScript-Python SDK parity features."""

import json
import base64
import pytest
from unittest.mock import MagicMock
from starlette.testclient import TestClient
from starlette.applications import Starlette
from pydantic import BaseModel

from sdk import (
    create_smithery_url,
    parse_and_validate_config,
    create_transport,
    create_stateful_server,
    SmitheryUrlOptions,
)
from sdk.config import Ok, Err


class TestSmitheryUrl:
    """Test cases for Smithery URL creation (parity with TS)."""
    
    def test_create_basic_url(self):
        """Test basic URL creation."""
        url = create_smithery_url("https://api.smithery.ai/namespace")
        assert str(url) == "https://api.smithery.ai/namespace/mcp"
    
    def test_create_url_with_api_key(self):
        """Test URL creation with API key."""
        url = create_smithery_url(
            "https://api.smithery.ai/namespace",
            api_key="sk-test-key"
        )
        assert "api_key=sk-test-key" in str(url)
    
    def test_create_url_with_profile(self):
        """Test URL creation with profile."""
        url = create_smithery_url(
            "https://api.smithery.ai/namespace",
            profile="production"
        )
        assert "profile=production" in str(url)
    
    def test_create_url_with_config(self):
        """Test URL creation with config object."""
        config = {"debug": True, "timeout": 30}
        url = create_smithery_url(
            "https://api.smithery.ai/namespace",
            config=config
        )
        
        # Extract and decode the config parameter
        url_str = str(url)
        assert "config=" in url_str
        
        # Get the base64 encoded config
        config_param = url_str.split("config=")[1].split("&")[0]
        decoded = json.loads(base64.b64decode(config_param))
        assert decoded == config
    
    def test_create_url_with_all_options(self):
        """Test URL creation with all options."""
        config = {"feature": "enabled"}
        url = create_smithery_url(
            "https://api.smithery.ai/namespace",
            api_key="sk-test",
            profile="dev",
            config=config
        )
        
        url_str = str(url)
        assert "api_key=sk-test" in url_str
        assert "profile=dev" in url_str
        assert "config=" in url_str


class TestConfigParsing:
    """Test cases for config parsing and validation (parity with TS)."""
    
    def test_parse_base64_config(self):
        """Test parsing base64-encoded config."""
        from starlette.requests import Request
        from starlette.datastructures import QueryParams
        
        config = {"server": {"host": "localhost", "port": 8080}}
        encoded = base64.b64encode(json.dumps(config).encode()).decode()
        
        # Create mock request
        request = MagicMock(spec=Request)
        request.query_params = QueryParams(f"config={encoded}")
        request.url.path = "/test"
        
        result = parse_and_validate_config(request)
        
        assert isinstance(result, Ok)
        assert result.value == config
    
    def test_parse_dot_notation_params(self):
        """Test parsing dot-notation query parameters."""
        from starlette.requests import Request
        from starlette.datastructures import QueryParams
        
        # Create mock request with dot notation params
        request = MagicMock(spec=Request)
        request.query_params = QueryParams("server.host=localhost&server.port=8080&debug=true")
        request.url.path = "/test"
        
        result = parse_and_validate_config(request)
        
        assert isinstance(result, Ok)
        assert result.value == {
            "server": {
                "host": "localhost",
                "port": "8080"
            },
            "debug": "true"
        }
    
    def test_parse_with_validation(self):
        """Test parsing with Pydantic schema validation."""
        from starlette.requests import Request
        from starlette.datastructures import QueryParams
        
        class ServerConfig(BaseModel):
            host: str
            port: int
            debug: bool = False
        
        # Valid config
        config = {"host": "localhost", "port": 8080, "debug": True}
        encoded = base64.b64encode(json.dumps(config).encode()).decode()
        
        request = MagicMock(spec=Request)
        request.query_params = QueryParams(f"config={encoded}")
        request.url.path = "/test"
        
        result = parse_and_validate_config(request, ServerConfig)
        
        assert isinstance(result, Ok)
        assert isinstance(result.value, ServerConfig)
        assert result.value.host == "localhost"
        assert result.value.port == 8080
        assert result.value.debug is True
    
    def test_parse_validation_error(self):
        """Test parsing with validation errors."""
        from starlette.requests import Request
        from starlette.datastructures import QueryParams
        
        class ServerConfig(BaseModel):
            host: str
            port: int
        
        # Invalid config (port is string instead of int)
        config = {"host": "localhost", "port": "not_a_number"}
        encoded = base64.b64encode(json.dumps(config).encode()).decode()
        
        request = MagicMock(spec=Request)
        request.query_params = QueryParams(f"config={encoded}")
        request.url.path = "/test"
        
        result = parse_and_validate_config(request, ServerConfig)
        
        assert isinstance(result, Err)
        assert result.problem["status"] == 422
        assert "errors" in result.problem
        assert len(result.problem["errors"]) > 0
        assert "configSchema" in result.problem
    
    def test_parse_invalid_base64(self):
        """Test parsing with invalid base64 encoding."""
        from starlette.requests import Request
        from starlette.datastructures import QueryParams
        
        request = MagicMock(spec=Request)
        request.query_params = QueryParams("config=not_valid_base64!")
        request.url.path = "/test"
        
        result = parse_and_validate_config(request)
        
        assert isinstance(result, Err)
        assert result.problem["status"] == 400
        assert "Invalid config encoding" in result.problem["title"]


class TestTransport:
    """Test cases for transport creation (parity with TS)."""
    
    def test_create_transport_basic(self):
        """Test basic transport creation."""
        transport = create_transport("https://api.smithery.ai")
        
        assert transport is not None
        assert hasattr(transport, "request")
        assert hasattr(transport, "sse")
        assert "smithery.ai" in transport.base_url
    
    def test_create_transport_with_options(self):
        """Test transport creation with options."""
        options = SmitheryUrlOptions(
            api_key="sk-test",
            profile="dev",
            config={"timeout": 60}
        )
        
        transport = create_transport("https://api.smithery.ai", options)
        
        assert transport is not None
        # URL should include the options
        assert "api_key=sk-test" in transport.base_url
        assert "profile=dev" in transport.base_url


class TestStatefulServer:
    """Test cases for stateful server (parity with TS)."""
    
    def test_well_known_endpoint(self):
        """Test /.well-known/mcp-config endpoint."""
        
        class TestConfig(BaseModel):
            feature: str
            timeout: int = 30
        
        def create_test_server(arg):
            return MagicMock()
        
        result = create_stateful_server(
            create_test_server,
            schema=TestConfig
        )
        
        app = result["app"]
        client = TestClient(app)
        
        response = client.get("/.well-known/mcp-config")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/schema+json; charset=utf-8"
        assert response.headers["x-mcp-version"] == "1.0"
        assert response.headers["x-query-style"] == "dot+bracket"
        
        schema = response.json()
        assert "properties" in schema
        assert "feature" in schema["properties"]
        assert "timeout" in schema["properties"]
    
    def test_session_creation(self):
        """Test POST /mcp session creation."""
        
        def create_test_server(arg):
            assert arg.session_id is not None
            assert arg.config == {"test": "value"}
            return MagicMock()
        
        result = create_stateful_server(create_test_server)
        app = result["app"]
        client = TestClient(app)
        
        config = {"test": "value"}
        encoded = base64.b64encode(json.dumps(config).encode()).decode()
        
        response = client.post(f"/mcp?config={encoded}")
        
        assert response.status_code == 201
        data = response.json()
        assert "sessionId" in data
        assert len(data["sessionId"]) > 0