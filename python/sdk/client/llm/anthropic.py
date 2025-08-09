"""Anthropic LLM integration helpers."""

from typing import Any, Dict, List, Optional


async def create_anthropic_tools(client: Any) -> List[Dict[str, Any]]:
    """
    Create Anthropic-compatible tool definitions from an MCP client.
    
    This is a parity implementation for Anthropic integration.
    It converts MCP tool definitions to Anthropic's tool format.
    
    Args:
        client: An MCP client with listTools method
        
    Returns:
        List of tool definitions in Anthropic format
    """
    tools = []
    
    # Get tools from the MCP server
    if hasattr(client, 'list_tools'):
        list_tools_result = await client.list_tools()
    elif hasattr(client, 'listTools'):
        list_tools_result = await client.listTools()
    else:
        raise AttributeError("Client must have list_tools or listTools method")
    
    # Convert to Anthropic format
    for tool in list_tools_result.get('tools', []):
        anthropic_tool = {
            'name': tool.get('name'),
            'description': tool.get('description', ''),
            'input_schema': tool.get('inputSchema', {
                'type': 'object',
                'properties': {},
                'required': []
            })
        }
        tools.append(anthropic_tool)
    
    return tools


def format_anthropic_tool_call(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a tool call for Anthropic's API.
    
    Args:
        tool_name: Name of the tool to call
        arguments: Arguments for the tool
        
    Returns:
        Formatted tool call for Anthropic
    """
    return {
        'type': 'tool_use',
        'name': tool_name,
        'input': arguments
    }


def parse_anthropic_tool_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse a tool result from MCP into Anthropic's expected format.
    
    Args:
        result: Raw result from MCP tool call
        
    Returns:
        Formatted result for Anthropic
    """
    # If the result has content array (MCP format), convert it
    if isinstance(result, dict) and 'content' in result:
        content = result['content']
        if isinstance(content, list) and len(content) > 0:
            # Take the first content item
            first_content = content[0]
            if first_content.get('type') == 'text':
                return {
                    'type': 'tool_result',
                    'content': first_content.get('text', '')
                }
    
    # Default format
    return {
        'type': 'tool_result',
        'content': str(result)
    }