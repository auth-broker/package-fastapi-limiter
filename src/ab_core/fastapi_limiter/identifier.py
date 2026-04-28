"""Request identifier helpers used by rate limiters."""

from starlette.requests import Request
from starlette.websockets import WebSocket


async def default_identifier(request: Request | WebSocket):
    """Build a client-and-path key used for rate limiting."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ip = forwarded.split(",")[0]
    elif request.client:
        ip = request.client.host
    else:
        ip = "127.0.0.1"
    return ip + ":" + request.scope["path"]
