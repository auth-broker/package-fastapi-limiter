"""Middleware-based rate limiting for FastAPI applications."""

import re
from re import Pattern

from pyrate_limiter import Limiter
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.websockets import WebSocket

from .callback import MiddlewareCallback, default_middleware_callback
from .identifier import Identifier, default_identifier
from .skip import Skip


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Apply rate limiting to all incoming requests in middleware."""

    def __init__(
        self,
        app,
        *,
        limiter: Limiter,
        identifier: Identifier = default_identifier,
        callback: MiddlewareCallback = default_middleware_callback,
        blocking: bool = False,
        skip: Skip | None = None,
    ):
        """Create middleware with limiter, identifier, and callback settings."""
        super().__init__(app)
        self.limiter = limiter
        self.identifier = identifier
        self.callback = callback
        self.blocking = blocking
        self.skip = skip

    async def dispatch(self, request: Request, call_next):
        """Limit the request or pass it through to the next handler."""
        if self.skip and await self.skip(request):
            return await call_next(request)
        rate_key = await self.identifier(request)
        success = await self.limiter.try_acquire_async(rate_key, blocking=self.blocking)
        if not success:
            return await self.callback(request)

        return await call_next(request)


class PathBasedRateLimiterMiddleware(RateLimiterMiddleware):
    """Apply path-based or pattern-based rate limiting to all incoming requests."""

    def __init__(
        self,
        app,
        *,
        limiter: Limiter,
        path_prefix: str | None = None,
        path_pattern: str | Pattern[str] | None = None,
        identifier: Identifier = default_identifier,
        callback: MiddlewareCallback = default_middleware_callback,
        blocking: bool = False,
    ):
        """Initialize the path-based rate limiter middleware."""
        if not path_prefix and not path_pattern:
            raise ValueError("Either path_prefix or path_pattern must be provided")
        if path_prefix and path_pattern:
            raise ValueError("Provide only one of path_prefix or path_pattern")

        super().__init__(
            app,
            limiter=limiter,
            identifier=identifier,
            callback=callback,
            blocking=blocking,
            skip=self.skip,
        )

        self.path_prefix = path_prefix
        if isinstance(path_pattern, str):
            self.path_pattern: Pattern[str] | None = re.compile(path_pattern)
        else:
            self.path_pattern = path_pattern

    async def skip(self, request: Request | WebSocket) -> bool:
        """Determine whether to skip rate limiting based on the request path."""
        path = request.scope["path"]

        # Prefix mode (fast)
        if self.path_prefix is not None:
            return not path.startswith(self.path_prefix)

        # Regex mode (flexible)
        if self.path_pattern is not None:
            return self.path_pattern.search(path) is None

        return True  # fallback safety
