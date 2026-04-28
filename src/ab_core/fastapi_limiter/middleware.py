"""Middleware-based rate limiting for FastAPI applications."""

from pyrate_limiter import Limiter
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from ab_core.fastapi_limiter.callback import default_callback
from ab_core.fastapi_limiter.identifier import default_identifier


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Apply rate limiting to all incoming requests in middleware."""

    def __init__(
        self,
        app,
        limiter: Limiter,
        identifier=default_identifier,
        callback=default_callback,
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
