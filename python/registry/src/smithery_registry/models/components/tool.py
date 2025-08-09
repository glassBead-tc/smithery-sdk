"""Tool models."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from enum import Enum


class ToolType(str, Enum):
    """Tool type."""
    
    FUNCTION = "function"
    RESOURCE = "resource"
    PROMPT = "prompt"


class Tool(BaseModel):
    """Tool provided by an MCP server."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    type: ToolType
    name: str
    description: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = Field(None, alias="inputSchema")