"""Callback helpers used by FastAPI rate limiters."""

from fastapi import HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS


def default_callback(*_args, **_kwargs):
    """Raise an HTTP 429 error when a rate limit is exceeded."""
    raise HTTPException(
        HTTP_429_TOO_MANY_REQUESTS,
        "Too Many Requests",
    )
