"""Error models for the SDK."""

from .base_error import (
    SmitheryRegistryError,
    UnauthorizedError,
    NotFoundError,
    ServerError,
    ValidationError,
)

__all__ = [
    "SmitheryRegistryError",
    "UnauthorizedError",
    "NotFoundError",
    "ServerError",
    "ValidationError",
]