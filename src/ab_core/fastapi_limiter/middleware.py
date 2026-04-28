"""Middleware-based rate limiting for FastAPI applications."""

from pyrate_limiter import Limiter
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from ab_core.fastapi_limiter.callback import MiddlewareCallback, default_middleware_callback
from ab_core.fastapi_limiter.identifier import Identifier, default_identifier


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
        skip=None,
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
    """Apply path-based rate limiting to all incoming requests in middleware."""

    def __init__(
        self,
        app,
        *,
        limiter: Limiter,
        path_prefix: str,
        identifier: Identifier = default_identifier,
        callback: MiddlewareCallback = default_middleware_callback,
        blocking: bool = False,
    ):
        """Create middleware with limiter and callback settings."""
        super().__init__(
            app,
            limiter=limiter,
            identifier=identifier,
            callback=callback,
            blocking=blocking,
            skip=self.skip,
        )
        self.path_prefix = path_prefix

    def skip(self, request: Request):
        """Skip rate limiting for the dedicated skip route."""
        return not request.scope["path"].startswith(self.path_prefix)
