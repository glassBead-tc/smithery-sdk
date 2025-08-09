"""
Smithery Python SDK
==================

SDK for using Smithery in Python.

Parity targets (TS → PY):
- create_smithery_url (URL builder with base64 config, api_key, profile)
- parse_and_validate_config (Starlette request parsing + Pydantic validation)
"""

from .url import create_smithery_url
from .config import parse_and_validate_config
from .transport import create_transport, SmitheryUrlOptions, McpHttpClientTransport
from .server import create_stateful_server, CreateServerArg, SessionStore, LruSessionStore
from .client import wrap_error, watch_tools, list_tools
from .client.llm import create_anthropic_tools, create_openai_tools

__version__ = "0.1.3"

__all__ = [
    "create_smithery_url",
    "parse_and_validate_config",
    "create_transport",
    "SmitheryUrlOptions",
    "McpHttpClientTransport",
    "create_stateful_server",
    "CreateServerArg",
    "SessionStore",
    "LruSessionStore",
    "wrap_error",
    "watch_tools",
    "list_tools",
    "create_anthropic_tools",
    "create_openai_tools",
]
