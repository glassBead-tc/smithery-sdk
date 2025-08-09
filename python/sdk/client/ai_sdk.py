"""AI SDK integration helpers for MCP clients."""

from typing import Any, Callable, Dict, List, Optional
import asyncio
import json


async def watch_tools(client: Any) -> Dict[str, Callable]:
    """
    Watches the MCP client for tool changes and updates the tools object accordingly.
    
    This is a parity implementation of the TypeScript watchTools function.
    It sets up a notification handler for tool list changes and returns a dictionary
    of tool implementations.
    
    Args:
        client: An MCP client with listTools, callTool, and setNotificationHandler methods
        
    Returns:
        A dictionary mapping tool names to their callable implementations
    """
    tools: Dict[str, Callable] = {}
    
    # Define the notification handler for tool list changes
    async def handle_tool_list_changed(notification: Any) -> None:
        """Update tools when the list changes."""
        updated_tools = await list_tools(client)
        tools.clear()
        tools.update(updated_tools)
    
    # Set up the notification handler
    # Note: The exact schema name may vary based on the MCP implementation
    if hasattr(client, 'set_notification_handler'):
        client.set_notification_handler('tools/list_changed', handle_tool_list_changed)
    elif hasattr(client, 'setNotificationHandler'):
        client.setNotificationHandler('tools/list_changed', handle_tool_list_changed)
    
    # Get initial tools
    initial_tools = await list_tools(client)
    tools.update(initial_tools)
    
    return tools


async def list_tools(client: Any) -> Dict[str, Callable]:
    """
    Returns a set of wrapped AI SDK tools from the MCP server.
    
    This is a parity implementation of the TypeScript listTools function.
    It fetches available tools from the server and wraps them in callable functions.
    
    Args:
        client: An MCP client with listTools and callTool methods
        
    Returns:
        A dictionary mapping tool names to their callable implementations
    """
    tools: Dict[str, Callable] = {}
    
    # Get the list of tools from the server
    if hasattr(client, 'list_tools'):
        list_tools_result = await client.list_tools()
    elif hasattr(client, 'listTools'):
        list_tools_result = await client.listTools()
    else:
        raise AttributeError("Client must have list_tools or listTools method")
    
    # Process each tool
    tools_list = list_tools_result.get('tools', [])
    for tool_info in tools_list:
        name = tool_info.get('name')
        description = tool_info.get('description', '')
        input_schema = tool_info.get('inputSchema', {})
        
        # Create a wrapped function for this tool
        async def create_tool_executor(tool_name: str):
            """Create a closure that captures the tool name."""
            async def execute(
                args: Dict[str, Any],
                options: Optional[Dict[str, Any]] = None
            ) -> Any:
                """
                Execute the tool with the given arguments.
                
                Args:
                    args: Tool arguments
                    options: Execution options (e.g., abort signal)
                    
                Returns:
                    Tool execution result
                """
                # Check for abort signal if provided
                if options and 'abortSignal' in options:
                    abort_signal = options['abortSignal']
                    if hasattr(abort_signal, 'throwIfAborted'):
                        abort_signal.throwIfAborted()
                
                # Call the tool
                if hasattr(client, 'call_tool'):
                    result = await client.call_tool({
                        'name': tool_name,
                        'arguments': args
                    })
                elif hasattr(client, 'callTool'):
                    result = await client.callTool({
                        'name': tool_name,
                        'arguments': args
                    })
                else:
                    raise AttributeError("Client must have call_tool or callTool method")
                
                return result
            
            return execute
        
        # Create the tool executor with captured name
        executor = await create_tool_executor(name)
        
        # Store the tool with metadata
        tools[name] = {
            'description': description,
            'parameters': input_schema,
            'execute': executor
        }
    
    return tools