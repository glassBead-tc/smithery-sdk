# Smithery Registry Python SDK

A Python client library for interacting with the Smithery Registry API.

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
        
        # Get server details
        server = await client.servers.get({"qualified_name": "anthropic/mcp-server-slack"})
        print(f"Tools: {len(server.tools or [])}")

asyncio.run(main())
```

## Features

- 🚀 Async/await support with httpx
- 📄 Full type hints and Pydantic models
- 🔄 Automatic retry with exponential backoff
- 📖 Pagination support with async iterators
- 🔒 Bearer token authentication
- 🎣 Request/response hooks for middleware

## Documentation

See the [examples](./examples) directory for more usage examples.

## License

MIT