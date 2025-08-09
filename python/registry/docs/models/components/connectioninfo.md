# ConnectionInfo

## Overview

Connection configuration for an MCP server, specifying how to connect to and configure the server.

## Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `type` | *ConnectionInfoType* | ✅ | Connection type (http or stdio) |
| `deployment_url` | *Optional[str]* | ➖ | HTTP URL to connect to (for http type) |
| `config_schema` | *Dict[str, Any]* | ✅ | JSON Schema defining required configuration options |
| `published` | *Optional[bool]* | ➖ | Whether the server is published on npm/pypi/uv (for stdio type) |
| `stdio_function` | *Optional[str]* | ➖ | Lambda function for stdio connection configuration |

## ConnectionInfoType Enum

```python
from enum import Enum

class ConnectionInfoType(str, Enum):
    HTTP = "http"
    STDIO = "stdio"
```

## Example Usage

```python
from smithery_registry.models.components import ConnectionInfo, ConnectionInfoType

# HTTP connection example
http_connection = ConnectionInfo(
    type=ConnectionInfoType.HTTP,
    deployment_url="https://api.example.com/mcp",
    config_schema={
        "type": "object",
        "properties": {
            "api_key": {
                "type": "string",
                "description": "API key for authentication"
            }
        },
        "required": ["api_key"]
    }
)

# STDIO connection example
stdio_connection = ConnectionInfo(
    type=ConnectionInfoType.STDIO,
    config_schema={
        "type": "object",
        "properties": {
            "workspace_path": {
                "type": "string",
                "description": "Path to workspace"
            }
        }
    },
    published=True,
    stdio_function="(config) => ({ command: 'npx', args: ['mcp-server', config.workspace_path] })"
)
```

## Connection Types

### HTTP Connection

For HTTP-based MCP servers:

```python
if connection.type == ConnectionInfoType.HTTP:
    print(f"Connect via HTTP: {connection.deployment_url}")
    # Use the config_schema to validate configuration
```

### STDIO Connection

For standard I/O based MCP servers:

```python
if connection.type == ConnectionInfoType.STDIO:
    if connection.published:
        print("Server is available via package manager")
    if connection.stdio_function:
        print("Custom stdio configuration available")
```

## Config Schema

The `config_schema` field contains a JSON Schema that defines the configuration options required for the connection:

```python
# Example: Validating configuration against schema
import jsonschema

config = {"api_key": "secret-key"}
jsonschema.validate(config, connection.config_schema)
```

## JSON Structure

```json
{
  "type": "stdio",
  "configSchema": {
    "type": "object",
    "properties": {
      "apiKey": {
        "type": "string",
        "description": "API key for authentication"
      }
    },
    "required": ["apiKey"]
  },
  "published": true,
  "stdioFunction": "(config) => ({ command: 'node', args: ['server.js'] })"
}
```

## Field Mappings

| API Field | Python Field |
|-----------|--------------|
| `deploymentUrl` | `deployment_url` |
| `configSchema` | `config_schema` |
| `stdioFunction` | `stdio_function` |