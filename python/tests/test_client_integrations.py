"""Tests for client integration features."""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from sdk.client import wrap_error, watch_tools, list_tools
from sdk.client.llm import create_anthropic_tools, create_openai_tools


class TestWrapError:
    """Test cases for the wrap_error function."""
    
    @pytest.mark.asyncio
    async def test_wrap_error_success(self):
        """Test that successful calls pass through unchanged."""
        client = AsyncMock()
        client.call_tool = AsyncMock(return_value={"result": "success"})
        
        wrapped = wrap_error(client)
        result = await wrapped.call_tool({"name": "test_tool", "arguments": {}})
        
        assert result == {"result": "success"}
        client.call_tool.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_wrap_error_catches_exception(self):
        """Test that exceptions are caught and returned as content."""
        client = AsyncMock()
        original_call_tool = AsyncMock(side_effect=ValueError("Test error"))
        client.call_tool = original_call_tool
        
        wrapped = wrap_error(client)
        result = await wrapped.call_tool({"name": "test_tool", "arguments": {}})
        
        assert result["isError"] is True
        assert len(result["content"]) == 1
        assert result["content"][0]["type"] == "text"
        
        error_data = json.loads(result["content"][0]["text"])
        assert error_data["type"] == "ValueError"
        assert error_data["message"] == "Test error"
        assert "traceback" in error_data


class TestAISdkIntegration:
    """Test cases for AI SDK integration functions."""
    
    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test listing tools from an MCP client."""
        client = AsyncMock()
        client.list_tools = AsyncMock(return_value={
            "tools": [
                {
                    "name": "test_tool",
                    "description": "A test tool",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "param": {"type": "string"}
                        }
                    }
                }
            ]
        })
        client.call_tool = AsyncMock(return_value={"result": "success"})
        
        tools = await list_tools(client)
        
        assert "test_tool" in tools
        assert tools["test_tool"]["description"] == "A test tool"
        assert "execute" in tools["test_tool"]
        
        # Test execution
        executor = tools["test_tool"]["execute"]
        result = await executor({"param": "value"})
        assert result == {"result": "success"}
    
    @pytest.mark.asyncio
    async def test_watch_tools(self):
        """Test watching for tool changes."""
        client = AsyncMock()
        client.list_tools = AsyncMock(return_value={
            "tools": [
                {
                    "name": "initial_tool",
                    "description": "Initial tool",
                    "inputSchema": {}
                }
            ]
        })
        client.set_notification_handler = MagicMock()
        client.call_tool = AsyncMock(return_value={"result": "success"})
        
        tools = await watch_tools(client)
        
        assert "initial_tool" in tools
        client.set_notification_handler.assert_called_once()


class TestLLMIntegrations:
    """Test cases for LLM-specific integrations."""
    
    @pytest.mark.asyncio
    async def test_create_anthropic_tools(self):
        """Test creating Anthropic-compatible tool definitions."""
        client = AsyncMock()
        client.list_tools = AsyncMock(return_value={
            "tools": [
                {
                    "name": "test_tool",
                    "description": "A test tool",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "param": {"type": "string"}
                        },
                        "required": ["param"]
                    }
                }
            ]
        })
        
        tools = await create_anthropic_tools(client)
        
        assert len(tools) == 1
        assert tools[0]["name"] == "test_tool"
        assert tools[0]["description"] == "A test tool"
        assert tools[0]["input_schema"]["type"] == "object"
        assert "param" in tools[0]["input_schema"]["properties"]
    
    @pytest.mark.asyncio
    async def test_create_openai_tools(self):
        """Test creating OpenAI-compatible tool definitions."""
        client = AsyncMock()
        client.list_tools = AsyncMock(return_value={
            "tools": [
                {
                    "name": "test_tool",
                    "description": "A test tool",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "param": {"type": "string"}
                        },
                        "required": ["param"]
                    }
                }
            ]
        })
        
        tools = await create_openai_tools(client)
        
        assert len(tools) == 1
        assert tools[0]["type"] == "function"
        assert tools[0]["function"]["name"] == "test_tool"
        assert tools[0]["function"]["description"] == "A test tool"
        assert tools[0]["function"]["parameters"]["type"] == "object"
        assert "param" in tools[0]["function"]["parameters"]["properties"]