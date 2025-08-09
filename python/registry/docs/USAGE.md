# Smithery Registry Python SDK - Usage Guide

## Installation

```bash
pip install smithery-registry
```

## Quick Start

```python
import asyncio
from smithery_registry import SmitheryRegistry

async def main():
    async with SmitheryRegistry() as client:
        # List all servers
        async for server in await client.servers.list():
            print(f"{server.qualified_name}: {server.display_name}")

asyncio.run(main())
```

## Authentication

The SDK supports Bearer token authentication for accessing protected resources:

```python
from smithery_registry import SmitheryRegistry, SDKConfig

# Configure with API token
config = SDKConfig(
    auth_token="your-api-token"
)

client = SmitheryRegistry(config)
```

### Environment Variables

Store your API token securely:

```python
import os
from smithery_registry import SmitheryRegistry, SDKConfig

config = SDKConfig(
    auth_token=os.getenv("SMITHERY_API_TOKEN")
)

client = SmitheryRegistry(config)
```

## Common Operations

### Listing Servers

```python
from smithery_registry.models.operations import ListServersRequest

# Basic listing
async for server in await client.servers.list():
    print(server.qualified_name)

# With pagination
request = ListServersRequest(page=1, page_size=50)
async for server in await client.servers.list(request):
    print(server.display_name)

# With search
request = ListServersRequest(q="slack")
results = await (await client.servers.list(request)).collect()
print(f"Found {len(results)} Slack-related servers")
```

### Getting Server Details

```python
from smithery_registry.models.operations import GetServerRequest

request = GetServerRequest(qualified_name="anthropic/mcp-server-slack")
server = await client.servers.get(request)

print(f"Server: {server.display_name}")
print(f"Tools: {len(server.tools or [])}")

# Check connections
for conn in server.connections:
    print(f"Connection type: {conn.type}")
    if conn.type == "http":
        print(f"  URL: {conn.deployment_url}")
```

## Error Handling

The SDK provides specific exception types for different error scenarios:

```python
from smithery_registry import (
    NotFoundError,
    UnauthorizedError,
    ServerError,
    ValidationError
)

try:
    server = await client.servers.get({"qualified_name": "unknown/server"})
except NotFoundError:
    print("Server not found")
except UnauthorizedError:
    print("Authentication required or invalid token")
except ServerError as e:
    print(f"Server error ({e.status_code}): {e.message}")
except ValidationError as e:
    print(f"Invalid request: {e.message}")
```

## Advanced Configuration

### Custom Timeouts

```python
from smithery_registry import SDKConfig

config = SDKConfig(
    timeout=60.0  # 60 second timeout
)
```

### Retry Configuration

```python
from smithery_registry import SDKConfig
from smithery_registry.core.retry import RetryConfig, RetryStrategy

config = SDKConfig(
    retry_config=RetryConfig(
        strategy=RetryStrategy.BACKOFF,
        max_attempts=5,
        initial_interval=1.0,
        max_interval=30.0,
        exponent=2.0
    )
)
```

### Custom Headers

```python
config = SDKConfig(
    headers={
        "X-Custom-Header": "value",
        "X-Request-ID": "12345"
    },
    user_agent="my-app/1.0.0"
)
```

## Pagination Patterns

### Async Iteration

```python
# Process servers one by one
async for server in await client.servers.list():
    # Process each server
    if server.qualified_name.startswith("anthropic/"):
        print(f"Anthropic server: {server.display_name}")
```

### Collect All Results

```python
# Get all servers at once
all_servers = await (await client.servers.list()).collect()
print(f"Total servers: {len(all_servers)}")

# Process in batches
for i in range(0, len(all_servers), 10):
    batch = all_servers[i:i+10]
    # Process batch
```

### Manual Pagination

```python
page = 1
while True:
    request = ListServersRequest(page=page, page_size=20)
    page_iterator = await client.servers.list(request)
    
    servers = await page_iterator.collect()
    if not servers:
        break
    
    for server in servers:
        print(server.qualified_name)
    
    page += 1
```

## Request Options

Override settings for individual requests:

```python
from smithery_registry.core.config import RequestOptions

options = RequestOptions(
    timeout=120.0,  # Override timeout for this request
    headers={"X-Priority": "high"}
)

server = await client.servers.get(
    {"qualified_name": "example/server"},
    request_options=options
)
```

## Context Manager Usage

The SDK supports async context managers for automatic cleanup:

```python
async with SmitheryRegistry() as client:
    # Client is automatically closed when exiting
    servers = await client.servers.list()
```

Manual cleanup:

```python
client = SmitheryRegistry()
try:
    servers = await client.servers.list()
finally:
    await client.close()
```

## Complete Example

```python
import asyncio
import os
from smithery_registry import (
    SmitheryRegistry,
    SDKConfig,
    NotFoundError,
    UnauthorizedError
)
from smithery_registry.models.operations import (
    ListServersRequest,
    GetServerRequest
)

async def explore_registry():
    # Configure client
    config = SDKConfig(
        auth_token=os.getenv("SMITHERY_API_TOKEN"),
        timeout=30.0
    )
    
    async with SmitheryRegistry(config) as client:
        # Search for specific servers
        search_request = ListServersRequest(
            q="github",
            page_size=10
        )
        
        print("Searching for GitHub-related servers...")
        servers = await (await client.servers.list(search_request)).collect()
        
        for server in servers:
            print(f"\nFound: {server.qualified_name}")
            
            try:
                # Get detailed information
                details = await client.servers.get({
                    "qualified_name": server.qualified_name
                })
                
                print(f"  Name: {details.display_name}")
                print(f"  Connections: {len(details.connections)}")
                
                if details.tools:
                    print(f"  Tools: {len(details.tools)}")
                    for tool in details.tools[:3]:  # Show first 3 tools
                        print(f"    - {tool.name}")
                
                if details.security and details.security.scan_passed:
                    print("  Security: ✅ Passed")
                    
            except NotFoundError:
                print("  Details not available")
            except UnauthorizedError:
                print("  Authentication required for details")

if __name__ == "__main__":
    asyncio.run(explore_registry())
```

## Best Practices

1. **Always use async context managers** for automatic resource cleanup
2. **Handle specific exceptions** rather than catching all exceptions
3. **Use environment variables** for API tokens
4. **Configure appropriate timeouts** for your use case
5. **Enable retries** for production applications
6. **Use pagination** when dealing with large result sets
7. **Cache server details** when making multiple requests for the same server