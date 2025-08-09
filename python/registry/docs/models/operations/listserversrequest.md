# ListServersRequest

## Overview

Request parameters for listing servers with pagination and optional filtering.

## Properties

| Property | Type | Required | Description | Default |
|----------|------|----------|-------------|---------|
| `page` | *Optional[int]* | ➖ | Page number to retrieve (1-indexed) | 1 |
| `page_size` | *Optional[int]* | ➖ | Number of items per page (1-100) | 20 |
| `q` | *Optional[str]* | ➖ | Search query to filter servers | None |

## Example Usage

```python
from smithery_registry import SmitheryRegistry
from smithery_registry.models.operations import ListServersRequest

async with SmitheryRegistry() as client:
    # Default pagination
    request = ListServersRequest()
    async for server in await client.servers.list(request):
        print(server.qualified_name)
    
    # Custom pagination
    request = ListServersRequest(
        page=2,
        page_size=50
    )
    results = await client.servers.list(request)
    
    # Search for specific servers
    request = ListServersRequest(
        q="slack",
        page_size=10
    )
    async for server in await client.servers.list(request):
        print(f"Found: {server.display_name}")
```

## Pagination

The `page` and `page_size` parameters control pagination:

```python
# Get first page with 10 items
request = ListServersRequest(page=1, page_size=10)

# Get second page
request = ListServersRequest(page=2, page_size=10)

# Maximum page size
request = ListServersRequest(page_size=100)  # Maximum allowed
```

## Search Filtering

The `q` parameter enables text search across server names and descriptions:

```python
# Search for Slack-related servers
request = ListServersRequest(q="slack")

# Search with custom pagination
request = ListServersRequest(
    q="github",
    page=1,
    page_size=25
)

# Complex search terms
request = ListServersRequest(q="data analysis python")
```

## Validation

The SDK validates request parameters:

- `page`: Must be >= 1
- `page_size`: Must be between 1 and 100
- `q`: Any string value

```python
from pydantic import ValidationError

try:
    # Invalid page size
    request = ListServersRequest(page_size=200)  # Will raise ValidationError
except ValidationError as e:
    print(f"Validation error: {e}")
```

## Default Behavior

When no request is provided, defaults are used:

```python
# These are equivalent
await client.servers.list()
await client.servers.list(ListServersRequest())
await client.servers.list(ListServersRequest(page=1, page_size=20))
```

## Complete Example

```python
import asyncio
from smithery_registry import SmitheryRegistry
from smithery_registry.models.operations import ListServersRequest

async def search_and_paginate():
    async with SmitheryRegistry() as client:
        # Search with pagination
        request = ListServersRequest(
            q="anthropic",
            page=1,
            page_size=5
        )
        
        # Get first page
        page_iterator = await client.servers.list(request)
        
        # Process results
        servers = []
        async for server in page_iterator:
            servers.append(server)
            print(f"Page 1: {server.qualified_name}")
        
        # Get next page if needed
        if len(servers) == 5:  # Full page, might have more
            request.page = 2
            async for server in await client.servers.list(request):
                print(f"Page 2: {server.qualified_name}")

asyncio.run(search_and_paginate())
```

## Field Mappings

| API Parameter | Python Field | JSON Key |
|---------------|--------------|----------|
| `page` | `page` | `page` |
| `page_size` | `page_size` | `pageSize` |
| `q` | `q` | `q` |