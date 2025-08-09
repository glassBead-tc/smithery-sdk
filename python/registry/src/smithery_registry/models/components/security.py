"""Security model for Smithery Registry SDK."""

from typing import Optional
from pydantic import BaseModel, Field


class Security(BaseModel):
    """Security configuration for API authentication."""
    
    api_key: Optional[str] = Field(
        default=None,
        alias="apiKey",
        description="API key for authentication"
    )
    
    bearer_token: Optional[str] = Field(
        default=None,
        alias="bearerToken", 
        description="Bearer token for authentication"
    )
    
    class Config:
        populate_by_name = True