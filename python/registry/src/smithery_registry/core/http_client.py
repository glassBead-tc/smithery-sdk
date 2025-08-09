"""HTTP client implementation with retry and hook support."""

from typing import Optional, Dict, Any, List, Callable, Awaitable
import httpx
from dataclasses import dataclass
from .retry import RetryHandler, RetryConfig


BeforeRequestHook = Callable[[httpx.Request], Awaitable[Optional[httpx.Request]]]
ResponseHook = Callable[[httpx.Response, httpx.Request], Awaitable[None]]
RequestErrorHook = Callable[[Exception, httpx.Request], Awaitable[None]]


@dataclass
class HTTPClientOptions:
    """Options for HTTP client configuration."""
    
    base_url: str = ""
    timeout: float = 30.0
    headers: Optional[Dict[str, str]] = None
    auth_token: Optional[str] = None
    retry_config: Optional[RetryConfig] = None
    user_agent: Optional[str] = None


class HTTPClient:
    """Async HTTP client with retry and hook support."""
    
    def __init__(self, options: HTTPClientOptions):
        self.options = options
        self._client = httpx.AsyncClient(
            base_url=options.base_url,
            timeout=options.timeout,
            headers=self._build_headers()
        )
        self._request_hooks: List[BeforeRequestHook] = []
        self._response_hooks: List[ResponseHook] = []
        self._error_hooks: List[RequestErrorHook] = []
        self._retry_handler = RetryHandler(options.retry_config or RetryConfig())
    
    def _build_headers(self) -> Dict[str, str]:
        """Build default headers."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        
        if self.options.headers:
            headers.update(self.options.headers)
        
        if self.options.user_agent:
            headers["User-Agent"] = self.options.user_agent
        
        if self.options.auth_token:
            headers["Authorization"] = f"Bearer {self.options.auth_token}"
        
        return headers
    
    async def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> httpx.Response:
        """Execute an HTTP request with hooks and retry logic."""
        
        # Build request
        request_headers = self._client.headers.copy()
        if headers:
            request_headers.update(headers)
        
        request = self._client.build_request(
            method=method,
            url=path,
            params=params,
            json=json,
            headers=request_headers,
            timeout=timeout or self.options.timeout,
        )
        
        # Apply before-request hooks
        for hook in self._request_hooks:
            result = await hook(request)
            if result:
                request = result
        
        async def _execute():
            try:
                response = await self._client.send(request)
                
                # Apply response hooks
                for hook in self._response_hooks:
                    await hook(response, request)
                
                response.raise_for_status()
                return response
                
            except Exception as e:
                # Apply error hooks
                for hook in self._error_hooks:
                    await hook(e, request)
                raise
        
        def _should_retry(error: Exception) -> bool:
            if isinstance(error, httpx.ConnectError):
                return self.options.retry_config.retry_connection_errors
            
            if isinstance(error, httpx.HTTPStatusError):
                status_code = str(error.response.status_code)
                for retry_code in self.options.retry_config.retry_codes:
                    if retry_code == "5XX" and 500 <= error.response.status_code < 600:
                        return True
                    elif retry_code == status_code:
                        return True
            
            return False
        
        return await self._retry_handler.execute_with_retry(
            _execute,
            _should_retry
        )
    
    def add_hook(self, hook_type: str, hook: Callable) -> None:
        """Register a hook for request lifecycle events."""
        if hook_type == "beforeRequest":
            self._request_hooks.append(hook)
        elif hook_type == "response":
            self._response_hooks.append(hook)
        elif hook_type == "requestError":
            self._error_hooks.append(hook)
        else:
            raise ValueError(f"Unknown hook type: {hook_type}")
    
    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()