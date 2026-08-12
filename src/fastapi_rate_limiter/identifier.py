"""Identifier helpers used by FastAPI rate limiters."""

from collections.abc import Awaitable, Callable

from starlette.requests import Request
from starlette.websockets import WebSocket

Identifier = Callable[[Request | WebSocket], Awaitable[str]]


async def default_identifier(request: Request | WebSocket) -> str:
    """Return a stable rate-limit key for a request or websocket."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ip = forwarded.split(",")[0]
    elif request.client:
        ip = request.client.host
    else:
        ip = "127.0.0.1"
    return ip + ":" + request.scope["path"]
