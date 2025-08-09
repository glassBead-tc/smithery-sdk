from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Dict, Optional

import httpx
from httpx_sse import aconnect_sse

from .url import create_smithery_url


@dataclass
class SmitheryUrlOptions:
    api_key: Optional[str] = None
    profile: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class McpHttpClientTransport:
    """
    Minimal HTTP/SSE transport compatible with MCP client patterns.

    Notes:
    - This is a parity-aligned lightweight transport that provides:
      - async request() for JSON HTTP calls
      - async sse() for Server-Sent Events stream (GET /mcp)
    - It leverages httpx.AsyncClient and httpx_sse for SSE.
    """

    def __init__(self, base_url: str, client: Optional[httpx.AsyncClient] = None) -> None:
        self.base_url = base_url.rstrip("/")
        self._client = client or httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
        self._owns_client = client is None

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> httpx.Response:
        """
        Perform an HTTP request relative to the transport base_url.
        Raises for non-successful status codes.
        """
        req = self._client.build_request(
            method=method.upper(),
            url=path,
            params=params,
            json=json,
            headers=headers,
            timeout=timeout,
        )
        resp = await self._client.send(req)
        resp.raise_for_status()
        return resp

    async def sse(
        self,
        path: str = "/mcp",
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Connect to an SSE endpoint (default: /mcp) and yield events.

        Yields dicts with keys like: { "event": str | None, "data": str, "id": str | None }
        """
        async with aconnect_sse(
            self._client,
            method="GET",
            url=path,
            params=params,
            headers=headers,
            timeout=timeout,
        ) as sse:
            async for event in sse.aiter_sse():
                yield {"event": event.event, "data": event.data, "id": event.id}

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> "McpHttpClientTransport":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()


def create_transport(
    base_url: str,
    options: Optional[SmitheryUrlOptions] = None,
    *,
    client: Optional[httpx.AsyncClient] = None,
) -> McpHttpClientTransport:
    """
    Parity target for TS createTransport(baseUrl, options?).

    - Builds a Smithery URL via create_smithery_url with provided options.
    - Returns a minimal MCP-like HTTP/SSE transport.

    Example:
        transport = create_transport(
            "https://api.smithery.ai",
            SmitheryUrlOptions(api_key="sk-...", profile="default", config={"foo": "bar"})
        )
        async with transport:
            # JSON request
            resp = await transport.request("GET", "/status")
            print(resp.json())

            # SSE stream
            async for evt in transport.sse("/mcp"):
                print(evt)
                break  # stop after first event for demo
    """
    opts = options or SmitheryUrlOptions()
    url = create_smithery_url(base_url, api_key=opts.api_key, profile=opts.profile, config=opts.config)
    return McpHttpClientTransport(url, client=client)
