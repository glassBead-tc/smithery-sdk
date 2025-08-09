# Servers

## Overview

The Servers resource provides operations for listing and retrieving information about MCP servers in the Smithery Registry.

## Available Operations

- [list](#list) - List all available servers with optional filtering
- [get](#get) - Get detailed information about a specific server

---

## list

List all available servers with optional filtering and pagination.

### Method Signature

```python
async def list(
    request: Optional[ListServersRequest] = None,
    request_options: Optional[RequestOptions] = None
) -> PageIterator[ServerListItem]
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `request` | *Optional[ListServersRequest]* | ➖ | Request parameters for listing servers |
| `request_options` | *Optional[RequestOptions]* | ➖ | Optional request configuration |

### Returns

Returns a `PageIterator[ServerListItem]` that can be used to iterate through all servers asynchronously.

### Example Usage

```python
from smithery_registry import SmitheryRegistry
from smithery_registry.models.operations import ListServersRequest

async with SmitheryRegistry() as client:
    # List all servers with default pagination
    async for server in await client.servers.list():
        print(f"{server.qualified_name}: {server.display_name}")
    
    # List with custom parameters
    request = ListServersRequest(
        page=1,
        page_size=50,
        q="search term"
    )
    
    async for server in await client.servers.list(request):
        print(server.qualified_name)
    
    # Collect all results at once
    all_servers = await (await client.servers.list()).collect()
    print(f"Total servers: {len(all_servers)}")
```

### Response Structure

Each `ServerListItem` contains:

| Field | Type | Description |
|-------|------|-------------|
| `qualified_name` | *str* | Qualified name in format `owner/repository` |
| `display_name` | *str* | Human-readable name |
| `icon_url` | *Optional[str]* | URL to the server's icon |
| `remote` | *Optional[bool]* | Whether this is a remote server |

---

## get

Get detailed information about a specific server by its qualified name.

### Method Signature

```python
async def get(
    request: GetServerRequest,
    request_options: Optional[RequestOptions] = None
) -> ServerDetailResponse
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `request` | *GetServerRequest* | ✅ | Request containing the server's qualified name |
| `request_options` | *Optional[RequestOptions]* | ➖ | Optional request configuration |

### Returns

Returns a `ServerDetailResponse` with complete server information.

### Example Usage

```python
from smithery_registry import SmitheryRegistry
from smithery_registry.models.operations import GetServerRequest

async with SmitheryRegistry() as client:
    # Get server details
    request = GetServerRequest(qualified_name="anthropic/mcp-server-slack")
    server = await client.servers.get(request)
    
    print(f"Server: {server.display_name}")
    print(f"Qualified Name: {server.qualified_name}")
    
    # Check connections
    for connection in server.connections:
        print(f"Connection Type: {connection.type}")
        if connection.deployment_url:
            print(f"  URL: {connection.deployment_url}")
    
    # List available tools
    if server.tools:
        print(f"Available tools: {len(server.tools)}")
        for tool in server.tools:
            print(f"  - {tool.name}: {tool.description}")
```

### Response Structure

The `ServerDetailResponse` contains:

| Field | Type | Description |
|-------|------|-------------|
| `qualified_name` | *str* | Qualified name (`owner/repository`) |
| `display_name` | *str* | Human-readable name |
| `icon_url` | *Optional[str]* | URL to server icon |
| `remote` | *Optional[bool]* | Whether this is a remote server |
| `connections` | *List[ConnectionInfo]* | Connection configurations |
| `security` | *Optional[ServerSecurity]* | Security status information |
| `tools` | *Optional[List[Tool]]* | Available tools |

### Error Handling

```python
from smithery_registry import NotFoundError, UnauthorizedError

try:
    server = await client.servers.get({"qualified_name": "unknown/server"})
except NotFoundError:
    print("Server not found")
except UnauthorizedError:
    print("Authentication required")
```

## Pagination

The `list` operation returns a `PageIterator` that handles pagination automatically:

```python
# Automatic pagination with async iteration
async for server in await client.servers.list():
    print(server.qualified_name)

# Manual pagination control
request = ListServersRequest(page=1, page_size=10)
page_iterator = await client.servers.list(request)

# Process items one by one
async for server in page_iterator:
    if server.qualified_name.startswith("anthropic/"):
        print(f"Found Anthropic server: {server.display_name}")

# Or collect all at once
all_servers = await page_iterator.collect()
```

## Request Options

Both operations support optional request configuration:

```python
from smithery_registry.core.config import RequestOptions
from smithery_registry.core.retry import RetryConfig

options = RequestOptions(
    timeout=60.0,  # Override default timeout
    headers={"X-Custom-Header": "value"},
    retry_config=RetryConfig(max_attempts=5)
)

servers = await client.servers.list(request_options=options)
```