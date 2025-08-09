"""Pagination utilities."""

from typing import AsyncIterator, Generic, TypeVar, Optional, Callable, Awaitable, List, Dict, Any


T = TypeVar('T')


class PageIterator(Generic[T], AsyncIterator[T]):
    """Async iterator for paginated API responses."""
    
    def __init__(
        self,
        fetch_page: Callable[[int], Awaitable[Dict[str, Any]]],
        initial_page: int = 1
    ):
        """Initialize the page iterator.
        
        Args:
            fetch_page: Function to fetch a page of results
            initial_page: Starting page number
        """
        self._fetch_page = fetch_page
        self._current_page = initial_page
        self._current_items: List[T] = []
        self._has_next = True
    
    def __aiter__(self) -> AsyncIterator[T]:
        """Return the iterator."""
        return self
    
    async def __anext__(self) -> T:
        """Get the next item from the paginated results."""
        if not self._current_items and self._has_next:
            page_data = await self._fetch_page(self._current_page)
            self._current_items = page_data.get("items", [])
            self._has_next = page_data.get("has_next", False)
            self._current_page = page_data.get("next_page", self._current_page + 1)
        
        if not self._current_items:
            raise StopAsyncIteration
        
        return self._current_items.pop(0)
    
    async def collect(self) -> List[T]:
        """Collect all items from all pages."""
        items = []
        async for item in self:
            items.append(item)
        return items