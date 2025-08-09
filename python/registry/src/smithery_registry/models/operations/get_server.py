"""Get server operation models."""

from pydantic import BaseModel, Field


class GetServerRequest(BaseModel):
    """Request parameters for getting server details."""
    
    qualified_name: str = Field(alias="qualifiedName")