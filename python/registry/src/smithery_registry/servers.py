"""Servers resource operations."""

from typing import Optional, Dict, Any
import httpx
from .models.components import ServerDetailResponse, ServerListItem
from .models.operations import ListServersRequest, GetServerRequest
from .models.errors import NotFoundError, UnauthorizedError, ServerError, ValidationError
from .core.config import SDKConfig, RequestOptions
from .core.http_client import HTTPClient
from .utils.pagination import PageIterator


class Servers:
    """Operations for managing and retrieving server information."""
    
    def __init__(self, config: SDKConfig, http_client: HTTPClient):
        """Initialize the servers resource.
        
        Args:
            config: SDK configuration
            http_client: HTTP client instance
        """
        self._config = config
        self._http_client = http_client
    
    async def list(
        self,
        request: Optional[ListServersRequest] = None,
        request_options: Optional[RequestOptions] = None
    ) -> PageIterator[ServerListItem]:
        """List all available servers with optional filtering.
        
        Args:
            request: Request parameters for listing servers
            request_options: Optional request configuration
        
        Returns:
            A paginated iterator of server items
        """
        if request is None:
            request = ListServersRequest()
        
        async def fetch_page(page: int):
            params = {
                "page": page,
                "pageSize": request.page_size,
            }
            if request.q:
                params["q"] = request.q
            
            try:
                response = await self._http_client.request(
                    method="GET",
                    path="/servers",
                    params=params,
                    timeout=request_options.timeout if request_options else None,
                    headers=request_options.headers if request_options else None,
                )
                
                data = response.json()
                items = [ServerListItem(**item) for item in data.get("data", {}).get("resultArray", [])]
                pagination = data.get("pagination", {})
                
                return {
                    "items": items,
                    "has_next": pagination.get("hasNextPage", False),
                    "next_page": page + 1 if pagination.get("hasNextPage", False) else None,
                }
                
            except httpx.HTTPStatusError as e:
                self._handle_error(e)
        
        return PageIterator(fetch_page, initial_page=request.page or 1)
    
    async def get(
        self,
        request: GetServerRequest,
        request_options: Optional[RequestOptions] = None
    ) -> ServerDetailResponse:
        """Get detailed information about a specific server.
        
        Args:
            request: The request containing the server's qualified name
            request_options: Optional request configuration
        
        Returns:
            Detailed server information
        
        Raises:
            NotFoundError: If the server doesn't exist
            UnauthorizedError: If authentication fails
            ServerError: For server-side errors
        """
        try:
            response = await self._http_client.request(
                method="GET",
                path=f"/servers/{request.qualified_name}",
                timeout=request_options.timeout if request_options else None,
                headers=request_options.headers if request_options else None,
            )
            
            data = response.json()
            return ServerDetailResponse(**data)
            
        except httpx.HTTPStatusError as e:
            self._handle_error(e)
    
    def _handle_error(self, error: httpx.HTTPStatusError):
        """Handle HTTP errors and raise appropriate exceptions."""
        if error.response.status_code == 401:
            raise UnauthorizedError(
                "Authentication failed",
                response_body=error.response.json() if error.response.content else None
            )
        elif error.response.status_code == 404:
            raise NotFoundError(
                "Server not found",
                response_body=error.response.json() if error.response.content else None
            )
        elif 500 <= error.response.status_code < 600:
            raise ServerError(
                f"Server error: {error.response.status_code}",
                status_code=error.response.status_code,
                response_body=error.response.json() if error.response.content else None
            )
        else:
            raise ValidationError(
                f"Request failed: {error.response.status_code}",
                response_body=error.response.json() if error.response.content else None
            )