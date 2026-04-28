"""Example FastAPI app demonstrating middleware-based rate limiting."""

import uvicorn
from fastapi import FastAPI
from pyrate_limiter import Duration, Limiter, Rate

from ab_core.fastapi_limiter.middleware import PathBasedRateLimiterMiddleware

app = FastAPI()


app.add_middleware(
    PathBasedRateLimiterMiddleware,
    limiter=Limiter(Rate(2, Duration.SECOND * 5)),
    path_prefix="/path/based",
)


@app.get("/")
async def index():
    """Return the default route response."""
    return {"msg": "Hello World"}


@app.get("/path/based/1")
async def path_based_route_1():
    """Return a response from a route excluded from limiting."""
    return {"msg": "This route has a unique rate limit configuration"}


@app.get("/path/based/2")
async def path_based_route_2():
    """Return a response from a route excluded from limiting."""
    return {"msg": "This route has a unique rate limit configuration (2)"}


if __name__ == "__main__":
    uvicorn.run("path_based_middleware:app", reload=True)
