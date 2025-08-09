from __future__ import annotations

import asyncio
import uuid
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Callable, Dict, Generic, Optional, Type, TypeVar, Union

from pydantic import BaseModel
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from sse_starlette.sse import EventSourceResponse

from ..config import Ok as ParseOk, Err as ParseErr, parse_and_validate_config

T = TypeVar("T")


@dataclass
class CreateServerArg(Generic[T]):
    session_id: str
    config: T


# Minimal session store interface + LRU implementation
class SessionStore(Generic[T]):
    def get(self, session_id: str) -> Optional[T]:
        raise NotImplementedError

    def set(self, session_id: str, value: T) -> None:
        raise NotImplementedError

    def delete(self, session_id: str) -> None:
        raise NotImplementedError

    def __contains__(self, session_id: str) -> bool:
        raise NotImplementedError


class LruSessionStore(SessionStore[Any]):
    def __init__(self, capacity: int = 100) -> None:
        self.capacity = capacity
        self._map: "OrderedDict[str, Any]" = OrderedDict()

    def get(self, session_id: str) -> Optional[Any]:
        if session_id not in self._map:
            return None
        value = self._map.pop(session_id)
        self._map[session_id] = value
        return value

    def set(self, session_id: str, value: Any) -> None:
        if session_id in self._map:
            self._map.pop(session_id)
        elif len(self._map) >= self.capacity:
            self._map.popitem(last=False)
        self._map[session_id] = value

    def delete(self, session_id: str) -> None:
        if session_id in self._map:
            del self._map[session_id]

    def __contains__(self, session_id: str) -> bool:
        return session_id in self._map


# Placeholder type for an MCP Server; callers supply whatever server object they use.
# We only keep it in the store and (optionally) expose a close() coroutine when deleting.
class _StoredSession:
    def __init__(self, server: Any, config: Any) -> None:
        self.server = server
        self.config = config


def _schema_headers() -> Dict[str, str]:
    return {
        "Content-Type": "application/schema+json; charset=utf-8",
        "x-mcp-version": "1.0",
        "x-query-style": "dot+bracket",
    }


def create_stateful_server(
    create_mcp_server: Callable[[CreateServerArg[T]], Any],
    *,
    session_store: Optional[SessionStore[_StoredSession]] = None,
    schema: Optional[Type[BaseModel]] = None,
    app: Optional[Starlette] = None,
) -> Dict[str, Any]:
    """
    Create a Starlette app exposing stateful MCP-like endpoints.

    Endpoints:
      - POST /mcp
        - Creates or reuses a session. Returns { sessionId }.
        - Reads configuration from query (base64 'config', dot/bracket params).
      - GET /mcp (SSE)
        - Requires 'mcp-session-id' header. Streams basic heartbeats for demo parity.
      - DELETE /mcp
        - Requires 'mcp-session-id' header. Terminates session; returns 204.
      - GET /.well-known/mcp-config
        - Returns JSON Schema (if provided) and discovery headers.

    Notes:
      - This is a parity-focused minimal implementation. It does not implement
        full MCP wire semantics, but provides endpoint shapes and lifecycle.
    """
    store = session_store or LruSessionStore()

    async def get_config(request: Request) -> Response:
        if schema is None:
            # No schema — return empty schema with required headers
            return JSONResponse(
                {"type": "object", "title": "Smithery Config", "properties": {}},
                headers=_schema_headers(),
            )
        # Return Pydantic JSON schema
        return JSONResponse(schema.model_json_schema(), headers=_schema_headers())

    async def post_mcp(request: Request) -> Response:
        # Parse/validate config from query params
        parsed = parse_and_validate_config(request, schema)
        if isinstance(parsed, ParseErr):
            status = int(parsed.problem.get("status", 400))
            return JSONResponse(parsed.problem, status_code=status)

        config_value: Union[T, Dict[str, Any]]
        if isinstance(parsed, ParseOk):
            config_value = parsed.value  # Either Pydantic model instance or dict
        else:
            config_value = {}  # Fallback; shouldn't happen

        # Allow clients to pass a header to reuse a session; otherwise create one.
        session_id = request.headers.get("mcp-session-id") or str(uuid.uuid4())

        # Create server instance using caller-provided factory.
        try:
            server = create_mcp_server(CreateServerArg(session_id=session_id, config=config_value))
        except Exception as e:
            problem = {
                "title": "Server initialization failed",
                "status": 500,
                "detail": str(e),
                "instance": str(request.url.path),
            }
            return JSONResponse(problem, status_code=500)

        store.set(session_id, _StoredSession(server=server, config=config_value))
        return JSONResponse({"sessionId": session_id}, status_code=201)

    async def require_session(request: Request) -> Optional[str]:
        session_id = request.headers.get("mcp-session-id")
        if not session_id:
            # 400 missing header
            problem = {
                "title": "Missing session header",
                "status": 400,
                "detail": "Header 'mcp-session-id' is required.",
                "instance": str(request.url.path),
            }
            return JSONResponse(problem, status_code=400)  # type: ignore[return-value]
        if session_id not in store:
            # 404 not found
            problem = {
                "title": "Session not found",
                "status": 404,
                "detail": "The specified session was not found or has expired.",
                "instance": str(request.url.path),
            }
            return JSONResponse(problem, status_code=404)  # type: ignore[return-value]
        return session_id

    async def get_mcp(request: Request) -> Response:
        # SSE stream
        session_or_response = await require_session(request)
        if isinstance(session_or_response, Response):
            return session_or_response
        session_id = session_or_response
        _ = store.get(session_id)  # bump LRU
        # Minimal heartbeat stream; real implementations should proxy server events.
        async def event_generator() -> AsyncGenerator[Dict[str, Any], None]:
            # Send an initial "ready" event
            yield {"event": "ready", "data": session_id}
            # Heartbeats to keep connection alive
            while True:
                await asyncio.sleep(10)
                yield {"event": "ping", "data": session_id}

        return EventSourceResponse(event_generator())

    async def delete_mcp(request: Request) -> Response:
        session_or_response = await require_session(request)
        if isinstance(session_or_response, Response):
            return session_or_response
        session_id = session_or_response
        stored = store.get(session_id)
        if stored and hasattr(stored.server, "close"):
            try:
                maybe_coro = stored.server.close()
                if asyncio.iscoroutine(maybe_coro):
                    await maybe_coro
            except Exception:
                # Best-effort cleanup
                pass
        store.delete(session_id)
        return Response(status_code=204)

    routes = [
        Route("/.well-known/mcp-config", get_config, methods=["GET"]),
        Route("/mcp", post_mcp, methods=["POST"]),
        Route("/mcp", get_mcp, methods=["GET"]),
        Route("/mcp", delete_mcp, methods=["DELETE"]),
    ]

    starlette_app = app or Starlette(routes=routes)
    if app is not None:
        # If an existing app was provided, we must mount the routes onto it.
        # Starlette doesn't provide dynamic route extension by default in a typed way;
        # but we can append to router.routes.
        for r in routes:
            app.router.routes.append(r)

    return {"app": starlette_app}
