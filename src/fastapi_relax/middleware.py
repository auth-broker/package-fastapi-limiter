"""Middleware-based rate limiting for FastAPI applications."""

import re
from collections.abc import Sequence
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
    """Apply path-based or pattern-based rate limiting to matching paths."""

    def __init__(
        self,
        app,
        *,
        limiter: Limiter,
        path_prefix: str | None = None,
        path_pattern: str | Pattern[str] | None = None,
        path_prefixes: Sequence[str] | None = None,
        path_patterns: Sequence[str | Pattern[str]] | None = None,
        identifier: Identifier = default_identifier,
        callback: MiddlewareCallback = default_middleware_callback,
        blocking: bool = False,
    ):
        """Initialize the path-based rate limiter middleware."""
        all_prefixes = tuple(
            prefix
            for prefix in ([path_prefix] if path_prefix is not None else [])
            + list(path_prefixes or [])
        )
        raw_patterns = ([path_pattern] if path_pattern is not None else []) + list(
            path_patterns or []
        )
        all_patterns = tuple(
            re.compile(pattern) if isinstance(pattern, str) else pattern
            for pattern in raw_patterns
        )
        if not all_prefixes and not all_patterns:
            raise ValueError(
                "At least one of path_prefix, path_pattern, path_prefixes, or path_patterns must be provided"
            )

        super().__init__(
            app,
            limiter=limiter,
            identifier=identifier,
            callback=callback,
            blocking=blocking,
            skip=self.skip,
        )

        self.path_prefixes = all_prefixes
        self.path_patterns = all_patterns

    async def skip(self, request: Request | WebSocket) -> bool:
        """Determine whether to skip rate limiting based on the request path."""
        path = request.scope["path"]

        matches_prefix = any(path.startswith(prefix) for prefix in self.path_prefixes)

        matches_pattern = any(
            pattern.search(path) is not None for pattern in self.path_patterns
        )

        return not (matches_prefix or matches_pattern)
