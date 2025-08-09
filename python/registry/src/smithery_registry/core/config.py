"""SDK configuration management."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from .retry import RetryConfig


@dataclass
class SDKConfig:
    """Configuration for the Smithery Registry SDK."""
    
    base_url: str = "https://api.smithery.ai/v1"
    auth_token: Optional[str] = None
    timeout: float = 30.0
    headers: Dict[str, str] = field(default_factory=dict)
    retry_config: Optional[RetryConfig] = None
    user_agent: str = "smithery-registry-python/0.4.0"
    
    def __post_init__(self):
        if self.retry_config is None:
            self.retry_config = RetryConfig()


@dataclass
class RequestOptions:
    """Options for individual requests."""
    
    timeout: Optional[float] = None
    headers: Optional[Dict[str, str]] = None
    retry_config: Optional[RetryConfig] = None
    server_url: Optional[str] = None