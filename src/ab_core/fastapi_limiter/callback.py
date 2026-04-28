"""Callback helpers used by FastAPI rate limiters."""

from collections.abc import Awaitable, Callable

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from starlette.websockets import WebSocket

Callback = Callable[[Request | WebSocket, Response | None], Awaitable[None]]


async def default_callback(
    _request: Request | WebSocket,
    _response: Response | None = None,
) -> None:
    """Raise an HTTP 429 error when a rate limit is exceeded."""
    raise HTTPException(
        status_code=HTTP_429_TOO_MANY_REQUESTS,
        detail="Too Many Requests",
    )


MiddlewareCallback = Callable[[Request], Awaitable[Response]]


async def default_middleware_callback(
    _request: Request,
) -> Response:
    """Return a 429 response when a rate limit is exceeded in middleware."""
    # HTTPException in middleware actually results in a 500, therefore we
    # need to epxlicitly return a JSONResponse with the correct with 429
    return JSONResponse(
        status_code=HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Too Many Requests"},
    )
