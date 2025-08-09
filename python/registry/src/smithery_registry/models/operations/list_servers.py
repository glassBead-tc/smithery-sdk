"""List servers operation models."""

from pydantic import BaseModel, Field
from typing import Optional, List
from ..components.server_list_item import ServerListItem
from ..components.pagination import Pagination


class ListServersRequest(BaseModel):
    """Request parameters for listing servers."""
    
    page: Optional[int] = Field(1, ge=1)
    page_size: Optional[int] = Field(20, ge=1, le=100, alias="pageSize")
    q: Optional[str] = None


class ListServersResponse(BaseModel):
    """Response from listing servers."""
    
    items: List[ServerListItem]
    pagination: Pagination