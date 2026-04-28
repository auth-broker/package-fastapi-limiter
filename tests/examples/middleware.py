"""Example FastAPI app demonstrating middleware-based rate limiting."""

import uvicorn
from fastapi import FastAPI
from fastapi.requests import Request
from pyrate_limiter import Duration, Limiter, Rate

from ab_core.fastapi_limiter.middleware import RateLimiterMiddleware

app = FastAPI()


async def skip(request: Request):
    """Skip rate limiting for the dedicated skip route."""
    return request.scope["path"] == "/skip"


app.add_middleware(
    RateLimiterMiddleware,
    limiter=Limiter(Rate(2, Duration.SECOND * 5)),
    skip=skip,
)


@app.get("/")
async def index():
    """Return the default route response."""
    return {"msg": "Hello World"}


@app.get("/other")
async def other():
    """Return an alternate route response."""
    return {"msg": "Other"}


@app.get("/skip")
async def skip_route():
    """Return a response from a route excluded from limiting."""
    return {"msg": "This route skips rate limiting"}


if __name__ == "__main__":
    uvicorn.run("middleware:app", reload=True)
