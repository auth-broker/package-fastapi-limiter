"""Request skip helpers used by rate limiters."""

from collections.abc import Awaitable, Callable

from starlette.requests import Request
from starlette.websockets import WebSocket

Skip = Callable[[Request | WebSocket], Awaitable[bool]]
