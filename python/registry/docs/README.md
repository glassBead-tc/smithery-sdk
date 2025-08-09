# Smithery Registry Python SDK Documentation

## Overview

This directory contains comprehensive documentation for the Smithery Registry Python SDK, which provides a Python client library for interacting with the Smithery Registry API to discover and connect to MCP (Model Context Protocol) servers.

## Documentation Structure

### Core SDK Documentation

- **[SmitheryRegistry](./sdks/smitheryregistry/README.md)** - Main SDK client class
- **[Servers](./sdks/servers/README.md)** - Server operations (list, get)
- **[Usage Guide](./USAGE.md)** - Complete usage examples and patterns

### Model Documentation

#### Components
- **[ServerDetailResponse](./models/components/serverdetailresponse.md)** - Detailed server information
- **[ServerListItem](./models/components/serverlistitem.md)** - Server summary for list operations
- **[ConnectionInfo](./models/components/connectioninfo.md)** - Connection configuration
- **[Tool](./models/components/tool.md)** - Tool/function information
- **[Pagination](./models/components/pagination.md)** - Pagination metadata

#### Operations
- **[ListServersRequest](./models/operations/listserversrequest.md)** - Parameters for listing servers
- **[GetServerRequest](./models/operations/getserverrequest.md)** - Parameters for getting server details

#### Errors
- **[UnauthorizedError](./models/errors/unauthorizederror.md)** - Authentication failures (401)
- **[NotFoundError](./models/errors/notfounderror.md)** - Resource not found (404)
- **[ServerError](./models/errors/servererror.md)** - Server-side errors (5xx)

### Configuration & Utilities
- **[RetryConfig](./lib/utils/retryconfig.md)** - Retry configuration with exponential backoff

## Quick Start

```python
import asyncio
from smithery_registry import SmitheryRegistry

async def main():
    async with SmitheryRegistry() as client:
        # List all servers
        async for server in await client.servers.list():
            print(f"{server.qualified_name}: {server.display_name}")
        
        # Get server details
        details = await client.servers.get({
            "qualified_name": "anthropic/mcp-server-slack"
        })
        print(f"Tools available: {len(details.tools or [])}")

asyncio.run(main())
```

## Key Features

- 🚀 **Async/Await Support** - Built on httpx for modern async Python
- 📄 **Full Type Hints** - Complete type annotations with Pydantic models
- 🔄 **Automatic Retry** - Configurable exponential backoff retry logic
- 📖 **Pagination** - Built-in async iterators for paginated results
- 🔒 **Authentication** - Bearer token authentication support
- 🎣 **Hooks** - Request/response hooks for middleware

## Common Use Cases

### 1. Discovering MCP Servers

```python
from smithery_registry import SmitheryRegistry
from smithery_registry.models.operations import ListServersRequest

async with SmitheryRegistry() as client:
    # Search for specific servers
    request = ListServersRequest(q="github")
    async for server in await client.servers.list(request):
        print(server.qualified_name)
```

### 2. Getting Server Connection Details

```python
server = await client.servers.get({"qualified_name": "example/server"})
for connection in server.connections:
    if connection.type == "http":
        print(f"HTTP endpoint: {connection.deployment_url}")
    elif connection.type == "stdio":
        print("STDIO connection available")
```

### 3. Error Handling

```python
from smithery_registry import NotFoundError, UnauthorizedError

try:
    server = await client.servers.get({"qualified_name": "private/server"})
except NotFoundError:
    print("Server not found")
except UnauthorizedError:
    print("Authentication required")
```

## Installation

```bash
pip install smithery-registry
```

## Requirements

- Python 3.8+
- httpx >= 0.25.0
- pydantic >= 2.0.0
- python-dateutil >= 2.8.0

## API Reference

The SDK provides a clean, Pythonic interface to the Smithery Registry API:

- **Client**: `SmitheryRegistry` - Main entry point
- **Resources**: `Servers` - Server operations
- **Models**: Pydantic models for type safety
- **Errors**: Specific exceptions for error handling

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/smithery-ai/sdk).

## License

MIT