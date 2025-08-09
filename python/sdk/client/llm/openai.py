"""OpenAI LLM integration helpers."""

from typing import Any, Dict, List, Optional
import json


async def create_openai_tools(client: Any) -> List[Dict[str, Any]]:
    """
    Create OpenAI-compatible tool definitions from an MCP client.
    
    This is a parity implementation for OpenAI integration.
    It converts MCP tool definitions to OpenAI's function calling format.
    
    Args:
        client: An MCP client with listTools method
        
    Returns:
        List of tool definitions in OpenAI format
    """
    tools = []
    
    # Get tools from the MCP server
    if hasattr(client, 'list_tools'):
        list_tools_result = await client.list_tools()
    elif hasattr(client, 'listTools'):
        list_tools_result = await client.listTools()
    else:
        raise AttributeError("Client must have list_tools or listTools method")
    
    # Convert to OpenAI format
    for tool in list_tools_result.get('tools', []):
        openai_tool = {
            'type': 'function',
            'function': {
                'name': tool.get('name'),
                'description': tool.get('description', ''),
                'parameters': tool.get('inputSchema', {
                    'type': 'object',
                    'properties': {},
                    'required': []
                })
            }
        }
        tools.append(openai_tool)
    
    return tools


def format_openai_tool_call(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a tool call for OpenAI's API.
    
    Args:
        tool_name: Name of the tool to call
        arguments: Arguments for the tool
        
    Returns:
        Formatted tool call for OpenAI
    """
    return {
        'type': 'function',
        'function': {
            'name': tool_name,
            'arguments': json.dumps(arguments)
        }
    }


def parse_openai_tool_result(result: Dict[str, Any], tool_call_id: str) -> Dict[str, Any]:
    """
    Parse a tool result from MCP into OpenAI's expected format.
    
    Args:
        result: Raw result from MCP tool call
        tool_call_id: OpenAI's tool call ID
        
    Returns:
        Formatted result for OpenAI
    """
    # Extract content from MCP format
    content = ""
    
    if isinstance(result, dict) and 'content' in result:
        content_list = result['content']
        if isinstance(content_list, list):
            # Combine all text content
            text_parts = []
            for item in content_list:
                if item.get('type') == 'text':
                    text_parts.append(item.get('text', ''))
            content = '\n'.join(text_parts)
    else:
        content = json.dumps(result)
    
    return {
        'tool_call_id': tool_call_id,
        'role': 'tool',
        'content': content
    }