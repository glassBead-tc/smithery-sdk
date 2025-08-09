"""Example: List servers from the Smithery Registry."""

import asyncio
from smithery_registry import SmitheryRegistry, SDKConfig
from smithery_registry.models.operations import ListServersRequest


async def main():
    """List servers example."""
    
    # Initialize client with optional configuration
    config = SDKConfig(
        # base_url="https://api.smithery.ai/v1",  # Default
        # auth_token="your-api-token",  # Optional authentication
    )
    
    async with SmitheryRegistry(config) as client:
        # List servers with pagination
        print("Listing MCP servers from Smithery Registry:\n")
        
        # Option 1: Iterate through servers one by one
        request = ListServersRequest(page_size=10)
        async for server in await client.servers.list(request):
            print(f"• {server.qualified_name}")
            print(f"  Name: {server.display_name}")
            if server.icon_url:
                print(f"  Icon: {server.icon_url}")
            print()
        
        # Option 2: Collect all servers at once
        print("\nCollecting all servers...")
        all_servers = await (await client.servers.list()).collect()
        print(f"Total servers found: {len(all_servers)}")
        
        # Option 3: Search for specific servers
        print("\nSearching for specific servers...")
        search_request = ListServersRequest(q="slack", page_size=5)
        search_results = await (await client.servers.list(search_request)).collect()
        for server in search_results:
            print(f"Found: {server.qualified_name}")


if __name__ == "__main__":
    asyncio.run(main())