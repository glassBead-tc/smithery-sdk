"""Server list item models."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class ServerListItem(BaseModel):
    """Summary information about an MCP server."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    qualified_name: str = Field(alias="qualifiedName")
    display_name: str = Field(alias="displayName")
    icon_url: Optional[str] = Field(None, alias="iconUrl")
    remote: Optional[bool] = False