"""Request identifier helpers used by rate limiters."""

from collections.abc import Awaitable, Callable

from starlette.requests import Request
from starlette.websockets import WebSocket

Identifier = Callable[[Request | WebSocket], Awaitable[str]]


async def default_identifier(
    request: Request | WebSocket,
) -> str:
    """Build a client-and-path key used for rate limiting."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ip = forwarded.split(",")[0]
    elif request.client:
        ip = request.client.host
    else:
        ip = "127.0.0.1"
    return ip + ":" + request.scope["path"]
