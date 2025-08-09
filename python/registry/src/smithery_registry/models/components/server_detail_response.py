"""Server detail response models."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from .connection_info import ConnectionInfo
from .tool import Tool


class ServerSecurity(BaseModel):
    """Information about the server's security status."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    scan_passed: Optional[bool] = Field(None, alias="scanPassed")


class ServerDetailResponse(BaseModel):
    """Detailed information about an MCP server."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    qualified_name: str = Field(alias="qualifiedName")
    display_name: str = Field(alias="displayName")
    icon_url: Optional[str] = Field(None, alias="iconUrl")
    remote: Optional[bool] = False
    connections: List[ConnectionInfo]
    security: Optional[ServerSecurity] = None
    tools: Optional[List[Tool]] = None