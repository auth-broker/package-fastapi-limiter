"""Example FastAPI app demonstrating regex path-based middleware limiting."""

import uvicorn
from fastapi import FastAPI
from pyrate_limiter import Duration, Limiter, Rate

from ab_core.fastapi_limiter.middleware import PathBasedRateLimiterMiddleware

app = FastAPI()


app.add_middleware(
    PathBasedRateLimiterMiddleware,
    limiter=Limiter(Rate(2, Duration.SECOND * 5)),
    path_pattern=r"^/path/based/\d+$",
)


@app.get("/")
async def index():
    """Return the default route response."""
    return {"msg": "Hello World"}


@app.get("/path/based/1")
async def path_based_route_1():
    """Return a response from a numeric route matched by the regex."""
    return {"msg": "This route has a regex-based rate limit configuration"}


@app.get("/path/based/2")
async def path_based_route_2():
    """Return a response from a numeric route matched by the regex."""
    return {"msg": "This route has a regex-based rate limit configuration (2)"}


@app.get("/path/based/nan")
async def path_based_route_nan():
    """Return a response from a non-matching route skipped by the regex."""
    return {"msg": "This route is not matched by the regex"}


if __name__ == "__main__":
    uvicorn.run("regex_path_based_middleware:app", reload=True)
