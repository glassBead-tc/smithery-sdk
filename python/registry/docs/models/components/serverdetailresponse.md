# ServerDetailResponse

## Overview

Detailed information about an MCP server in the Smithery Registry.

## Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `qualified_name` | *str* | ✅ | Qualified name of the MCP server in the format `owner/repository` |
| `display_name` | *str* | ✅ | Human-readable name of the MCP server |
| `icon_url` | *Optional[str]* | ➖ | URL to the server's icon image |
| `remote` | *Optional[bool]* | ➖ | Whether this server is a remote server (default: False) |
| `connections` | *List[ConnectionInfo]* | ✅ | List of connection configurations for this server |
| `security` | *Optional[ServerSecurity]* | ➖ | Information about the server's security status |
| `tools` | *Optional[List[Tool]]* | ➖ | List of tools that this server provides |

## Example Usage

```python
from smithery_registry import SmitheryRegistry
from smithery_registry.models.operations import GetServerRequest

async with SmitheryRegistry() as client:
    request = GetServerRequest(qualified_name="anthropic/mcp-server-slack")
    server = await client.servers.get(request)
    
    # Access server details
    print(f"Server: {server.display_name}")
    print(f"Qualified Name: {server.qualified_name}")
    
    if server.icon_url:
        print(f"Icon: {server.icon_url}")
    
    print(f"Remote: {server.remote}")
    print(f"Connections: {len(server.connections)}")
    
    # Check security status
    if server.security and server.security.scan_passed:
        print("Security: ✅ Passed security checks")
    
    # List available tools
    if server.tools:
        print(f"Available tools ({len(server.tools)}):")
        for tool in server.tools:
            print(f"  - {tool.name}: {tool.description}")
```

## Related Types

- [ConnectionInfo](./connectioninfo.md) - Connection configuration details
- [ServerSecurity](./serversecurity.md) - Security status information
- [Tool](./tool.md) - Tool information

## JSON Structure

```json
{
  "qualifiedName": "anthropic/mcp-server-slack",
  "displayName": "Slack MCP Server",
  "iconUrl": "https://example.com/icon.png",
  "remote": false,
  "connections": [
    {
      "type": "stdio",
      "configSchema": {},
      "published": true
    }
  ],
  "security": {
    "scanPassed": true
  },
  "tools": [
    {
      "type": "function",
      "name": "send_message",
      "description": "Send a message to a Slack channel"
    }
  ]
}
```

## Field Mappings

The Python SDK uses snake_case internally but handles camelCase from the API:

| API Field | Python Field |
|-----------|--------------|
| `qualifiedName` | `qualified_name` |
| `displayName` | `display_name` |
| `iconUrl` | `icon_url` |
| `scanPassed` | `scan_passed` |