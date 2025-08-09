"""Error wrapping utility for MCP client tool calls."""

from typing import Any, Callable, Dict, List, Optional
import json
import traceback


def wrap_error(client: Any) -> Any:
    """
    Wraps each tool call so any errors get sent back to the LLM instead of throwing.
    
    This is a parity implementation of the TypeScript wrapError function.
    It patches the client's call_tool method to catch exceptions and return them
    as content instead of raising.
    
    Args:
        client: An MCP client with a call_tool method
        
    Returns:
        The same client with wrapped error handling
    """
    original_call_tool = client.call_tool
    
    async def wrapped_call_tool(
        params: Dict[str, Any],
        result_schema: Optional[Any] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Wrapped call_tool that catches errors and returns them as content.
        
        Args:
            params: Tool call parameters
            result_schema: Optional result schema
            options: Optional request options
            
        Returns:
            Tool result or error content
        """
        try:
            return await original_call_tool(params, result_schema, options)
        except Exception as err:
            # Convert exception to JSON-serializable format
            error_dict = {
                "type": type(err).__name__,
                "message": str(err),
                "traceback": traceback.format_exc()
            }
            
            # Add any additional exception attributes
            for attr in dir(err):
                if not attr.startswith('_') and attr not in ['args', 'with_traceback']:
                    try:
                        value = getattr(err, attr)
                        if not callable(value):
                            error_dict[attr] = str(value)
                    except:
                        pass
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(error_dict, indent=2)
                    }
                ],
                "isError": True
            }
    
    # Replace the original method
    client.call_tool = wrapped_call_tool
    
    return client