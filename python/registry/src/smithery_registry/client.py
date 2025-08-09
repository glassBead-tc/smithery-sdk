"""Main SDK client for Smithery Registry."""

from typing import Optional
from .servers import Servers
from .core.config import SDKConfig
from .core.http_client import HTTPClient, HTTPClientOptions


class SmitheryRegistry:
    """Main SDK client for interacting with the Smithery Registry API."""
    
    def __init__(self, config: Optional[SDKConfig] = None):
        """Initialize the SDK client.
        
        Args:
            config: Optional SDK configuration. If not provided, defaults will be used.
        """
        self._config = config or SDKConfig()
        
        # Initialize HTTP client
        http_options = HTTPClientOptions(
            base_url=self._config.base_url,
            timeout=self._config.timeout,
            headers=self._config.headers,
            auth_token=self._config.auth_token,
            retry_config=self._config.retry_config,
            user_agent=self._config.user_agent,
        )
        self._http_client = HTTPClient(http_options)
        
        # Initialize resources
        self._servers: Optional[Servers] = None
    
    @property
    def servers(self) -> Servers:
        """Access the servers resource."""
        if self._servers is None:
            self._servers = Servers(self._config, self._http_client)
        return self._servers
    
    async def close(self):
        """Close the SDK client and cleanup resources."""
        await self._http_client.close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()