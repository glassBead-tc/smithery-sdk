"""Base error classes for the SDK."""

from typing import Optional, Dict, Any


class SmitheryRegistryError(Exception):
    """Base exception for all SDK errors."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class UnauthorizedError(SmitheryRegistryError):
    """Raised when authentication fails (401)."""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, status_code=401, **kwargs)


class NotFoundError(SmitheryRegistryError):
    """Raised when a resource is not found (404)."""
    
    def __init__(self, message: str = "Resource not found", **kwargs):
        super().__init__(message, status_code=404, **kwargs)


class ServerError(SmitheryRegistryError):
    """Raised for server errors (5xx)."""
    
    def __init__(self, message: str = "Server error occurred", status_code: int = 500, **kwargs):
        super().__init__(message, status_code=status_code, **kwargs)


class ValidationError(SmitheryRegistryError):
    """Raised when request or response validation fails."""
    
    def __init__(self, message: str = "Validation failed", **kwargs):
        super().__init__(message, status_code=400, **kwargs)