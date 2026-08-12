from pyrate_limiter import Limiter
from starlette.requests import Request
from starlette.responses import Response
from starlette.websockets import WebSocket

from fastapi_rate_limiter.callback import Callback, default_callback
from fastapi_rate_limiter.identifier import Identifier, default_identifier
from fastapi_rate_limiter.skip import Skip


class _BaseRateLimiter:
    def __init__(
        self,
        limiter: Limiter,
        identifier: Identifier = default_identifier,
        callback: Callback = default_callback,
        blocking: bool = False,
        skip: Skip | None = None,
    ):
        self.limiter = limiter
        self.identifier = identifier
        self.callback = callback
        self.blocking = blocking
        self.skip = skip


class RateLimiter(_BaseRateLimiter):
    async def __call__(self, request: Request, response: Response) -> None:
        if self.skip and await self.skip(request):
            return
        rate_key = await self.identifier(request)
        success = await self.limiter.try_acquire_async(rate_key, blocking=self.blocking)
        if not success:
            return await self.callback(request, response)


class WebSocketRateLimiter(_BaseRateLimiter):
    async def __call__(self, ws: WebSocket, context_key: str = "") -> None:
        if self.skip and await self.skip(ws):
            return
        rate_key = await self.identifier(ws)
        key = f"{rate_key}:{context_key}"
        success = await self.limiter.try_acquire_async(key, blocking=self.blocking)
        if not success:
            return await self.callback(ws)
