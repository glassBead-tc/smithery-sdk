"""
Smithery Registry SDK for Python

A Python client library for interacting with the Smithery Registry API.
"""

from .client import SmitheryRegistry
from .core.config import SDKConfig
from .models.errors import (
    SmitheryRegistryError,
    UnauthorizedError,
    NotFoundError,
    ServerError,
    ValidationError,
)

__version__ = "0.4.0"
__all__ = [
    "SmitheryRegistry",
    "SDKConfig",
    "SmitheryRegistryError",
    "UnauthorizedError",
    "NotFoundError",
    "ServerError",
    "ValidationError",
]