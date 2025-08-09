# UnauthorizedError

## Overview

Exception raised when authentication fails (HTTP 401).

## Class Hierarchy

```python
SmitheryRegistryError
    └── UnauthorizedError
```

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `message` | *str* | Error message (default: "Authentication failed") |
| `status_code` | *int* | HTTP status code (always 401) |
| `response_body` | *Optional[Dict[str, Any]]* | Response body from the API if available |

## Constructor

```python
UnauthorizedError(
    message: str = "Authentication failed",
    response_body: Optional[Dict[str, Any]] = None,
    **kwargs
)
```

## Example Usage

```python
from smithery_registry import SmitheryRegistry, UnauthorizedError

async with SmitheryRegistry() as client:
    try:
        # Attempt to access protected resource
        server = await client.servers.get({"qualified_name": "private/server"})
    except UnauthorizedError as e:
        print(f"Authentication failed: {e.message}")
        print(f"Status code: {e.status_code}")  # Always 401
        
        if e.response_body:
            print(f"API response: {e.response_body}")
```

## Handling Authentication Errors

### Missing Token

```python
from smithery_registry import SmitheryRegistry, SDKConfig, UnauthorizedError

# Client without authentication
client = SmitheryRegistry()

try:
    await client.servers.get({"qualified_name": "protected/server"})
except UnauthorizedError:
    print("API token required. Please provide authentication.")
    
    # Retry with authentication
    config = SDKConfig(auth_token="your-api-token")
    authenticated_client = SmitheryRegistry(config)
```

### Invalid Token

```python
config = SDKConfig(auth_token="invalid-token")
client = SmitheryRegistry(config)

try:
    await client.servers.list()
except UnauthorizedError as e:
    print("Invalid API token. Please check your credentials.")
    
    # Log the full error details
    import logging
    logging.error(f"Auth error: {e.message}, Body: {e.response_body}")
```

## Common Causes

1. **Missing API Token**: No authentication provided when required
2. **Invalid Token**: Token is malformed or expired
3. **Insufficient Permissions**: Token lacks required scopes
4. **Rate Limiting**: Token has exceeded rate limits

## Best Practices

```python
import os
from smithery_registry import SmitheryRegistry, SDKConfig, UnauthorizedError

async def create_authenticated_client():
    """Create an authenticated client with error handling."""
    
    # Get token from environment
    token = os.getenv("SMITHERY_API_TOKEN")
    
    if not token:
        raise ValueError("SMITHERY_API_TOKEN environment variable not set")
    
    config = SDKConfig(auth_token=token)
    client = SmitheryRegistry(config)
    
    # Verify authentication works
    try:
        await client.servers.list({"page_size": 1})
    except UnauthorizedError:
        raise ValueError("Invalid API token")
    
    return client
```

## Related Errors

- [NotFoundError](./notfounderror.md) - Resource not found (404)
- [ServerError](./servererror.md) - Server-side errors (5xx)
- [ValidationError](./validationerror.md) - Request validation errors