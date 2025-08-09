"""Pagination models."""

from pydantic import BaseModel, Field
from typing import Optional


class Pagination(BaseModel):
    """Pagination information."""
    
    has_next_page: bool = Field(alias="hasNextPage")
    has_previous_page: bool = Field(False, alias="hasPreviousPage")
    page: Optional[int] = 1
    page_size: Optional[int] = Field(20, alias="pageSize")
    total_pages: Optional[int] = Field(None, alias="totalPages")
    total_items: Optional[int] = Field(None, alias="totalItems")