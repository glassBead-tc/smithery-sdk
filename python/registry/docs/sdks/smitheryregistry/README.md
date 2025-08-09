# SmitheryRegistry

## Overview

The main SDK client for interacting with the Smithery Registry API. This client provides access to all API resources and handles authentication, retries, and HTTP communication.

## Constructor

```python
SmitheryRegistry(config: Optional[SDKConfig] = None)
```

### Parameters

- `config` (*Optional[SDKConfig]*): SDK configuration object. If not provided, defaults will be used.

### Example

```python
from smithery_registry import SmitheryRegistry, SDKConfig

# Using default configuration
client = SmitheryRegistry()

# With custom configuration
config = SDKConfig(
    base_url="https://api.smithery.ai/v1",
    auth_token="your-api-token",
    timeout=60.0
)
client = SmitheryRegistry(config)
```

## Properties

### servers

Access the servers resource for server-related operations.

**Type:** `Servers`

**Example:**

```python
async with SmitheryRegistry() as client:
    # Access servers resource
    servers = client.servers
    
    # List servers
    async for server in await servers.list():
        print(server.qualified_name)
```

## Methods

### close()

Close the SDK client and cleanup resources.

```python
async def close() -> None
```

**Example:**

```python
client = SmitheryRegistry()
try:
    # Use the client
    servers = await client.servers.list()
finally:
    await client.close()
```

## Context Manager

The SDK supports async context manager protocol for automatic resource cleanup:

```python
async with SmitheryRegistry() as client:
    # Client is automatically closed when exiting the context
    servers = await client.servers.list()
```

## Configuration

The SDK can be configured using the `SDKConfig` class:

```python
from smithery_registry import SDKConfig
from smithery_registry.core.retry import RetryConfig

config = SDKConfig(
    base_url="https://api.smithery.ai/v1",
    auth_token="your-bearer-token",
    timeout=30.0,
    headers={"X-Custom-Header": "value"},
    retry_config=RetryConfig(
        max_attempts=3,
        initial_interval=0.5,
        max_interval=60.0
    ),
    user_agent="my-app/1.0.0"
)
```

## Error Handling

The SDK raises specific exceptions for different error scenarios:

```python
from smithery_registry import (
    SmitheryRegistry,
    NotFoundError,
    UnauthorizedError,
    ServerError
)

async with SmitheryRegistry() as client:
    try:
        server = await client.servers.get({"qualified_name": "example/server"})
    except NotFoundError:
        print("Server not found")
    except UnauthorizedError:
        print("Authentication failed")
    except ServerError as e:
        print(f"Server error: {e.status_code}")
```

## Complete Example

```python
import asyncio
from smithery_registry import SmitheryRegistry, SDKConfig
from smithery_registry.models.operations import ListServersRequest

async def main():
    # Configure the client
    config = SDKConfig(
        auth_token="your-api-token",
        timeout=60.0
    )
    
    async with SmitheryRegistry(config) as client:
        # List servers with filtering
        request = ListServersRequest(
            page=1,
            page_size=20,
            q="slack"
        )
        
        async for server in await client.servers.list(request):
            print(f"Found: {server.qualified_name}")
            
            # Get detailed information
            details = await client.servers.get({
                "qualified_name": server.qualified_name
            })
            print(f"  Tools: {len(details.tools or [])}")
            print(f"  Connections: {len(details.connections)}")

if __name__ == "__main__":
    asyncio.run(main())
```