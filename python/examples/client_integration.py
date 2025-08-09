"""Example of using Smithery SDK client integrations."""

import asyncio
from smithery import (
    wrap_error,
    watch_tools,
    list_tools,
    create_anthropic_tools,
    create_openai_tools,
)


async def main():
    """Demonstrate client integration features."""
    
    # Assume we have an MCP client instance
    # In real usage, this would be your actual MCP client
    from mcp import Client  # This would be your MCP client
    
    # Example 1: Wrap client for error handling
    print("=== Error Handling ===")
    # client = Client(...)  # Your MCP client initialization
    # wrapped_client = wrap_error(client)
    
    # Now errors are caught and returned as content
    # result = await wrapped_client.call_tool({
    #     "name": "risky_tool",
    #     "arguments": {"param": "value"}
    # })
    # 
    # if result.get("isError"):
    #     print(f"Tool call failed: {result['content'][0]['text']}")
    # else:
    #     print(f"Tool succeeded: {result}")
    
    print("\n=== AI SDK Integration ===")
    # List available tools
    # tools = await list_tools(client)
    # print(f"Available tools: {list(tools.keys())}")
    # 
    # for name, tool in tools.items():
    #     print(f"  - {name}: {tool['description']}")
    #     print(f"    Parameters: {tool['parameters']}")
    
    # Watch for tool changes
    # watched_tools = await watch_tools(client)
    # print(f"Watching {len(watched_tools)} tools")
    
    print("\n=== LLM Integration ===")
    # Convert to Anthropic format
    # anthropic_tools = await create_anthropic_tools(client)
    # print(f"Anthropic tools: {len(anthropic_tools)}")
    # for tool in anthropic_tools:
    #     print(f"  - {tool['name']}: {tool['description']}")
    
    # Convert to OpenAI format
    # openai_tools = await create_openai_tools(client)
    # print(f"OpenAI tools: {len(openai_tools)}")
    # for tool in openai_tools:
    #     print(f"  - {tool['function']['name']}: {tool['function']['description']}")
    
    print("\nNote: This example shows the API usage.")
    print("In real usage, replace the commented code with your actual MCP client.")


if __name__ == "__main__":
    asyncio.run(main())