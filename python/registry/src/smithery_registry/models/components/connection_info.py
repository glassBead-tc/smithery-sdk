"""Connection information models."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from enum import Enum


class ConnectionInfoType(str, Enum):
    """Connection type."""
    
    HTTP = "http"
    STDIO = "stdio"


class ConnectionInfo(BaseModel):
    """Connection configuration for an MCP server."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    type: ConnectionInfoType
    deployment_url: Optional[str] = Field(None, alias="deploymentUrl")
    config_schema: Dict[str, Any] = Field(default_factory=dict, alias="configSchema")
    published: Optional[bool] = None
    stdio_function: Optional[str] = Field(None, alias="stdioFunction")