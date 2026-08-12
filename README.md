# FastAPI Rate Limiter

A request rate limiter for FastAPI, built on top of
[`pyrate-limiter`](https://github.com/vutran1710/PyrateLimiter).

This package is a modernized fork of `fastapi-limiter` with the import namespace
standardized to `fastapi_rate_limiter`.

## Installation

```bash
pip install fastapi-rate-limiter
```

```bash
uv add fastapi-rate-limiter
```

```bash
poetry add fastapi-rate-limiter
```

## Dependency-Based Limiting

```python
from fastapi import Depends, FastAPI
from pyrate_limiter import Duration, Limiter, Rate

from fastapi_rate_limiter.depends import RateLimiter

app = FastAPI()


@app.get(
    "/",
    dependencies=[
        Depends(RateLimiter(limiter=Limiter(Rate(2, Duration.SECOND * 5)))),
    ],
)
async def index():
    return {"msg": "Hello World"}
```

## Multiple Limits

```python
from fastapi import Depends, FastAPI
from pyrate_limiter import Duration, Limiter, Rate

from fastapi_rate_limiter.depends import RateLimiter

app = FastAPI()


@app.get(
    "/multiple",
    dependencies=[
        Depends(RateLimiter(limiter=Limiter(Rate(1, Duration.SECOND * 5)))),
        Depends(RateLimiter(limiter=Limiter(Rate(2, Duration.SECOND * 15)))),
    ],
)
async def multiple():
    return {"msg": "Hello World"}
```

## Skipping Requests

```python
from fastapi import Depends, FastAPI
from fastapi.requests import Request
from pyrate_limiter import Duration, Limiter, Rate

from fastapi_rate_limiter.depends import RateLimiter

app = FastAPI()


async def skip(request: Request) -> bool:
    return request.scope["path"] == "/skip"


@app.get(
    "/skip",
    dependencies=[
        Depends(
            RateLimiter(
                limiter=Limiter(Rate(1, Duration.SECOND * 5)),
                skip=skip,
            )
        )
    ],
)
async def skip_route():
    return {"msg": "This route skips rate limiting"}
```

## Middleware-Based Limiting

```python
from fastapi import FastAPI
from pyrate_limiter import Duration, Limiter, Rate

from fastapi_rate_limiter.middleware import RateLimiterMiddleware

app = FastAPI()

app.add_middleware(
    RateLimiterMiddleware,
    limiter=Limiter(Rate(2, Duration.SECOND * 5)),
)
```

## Path-Based Middleware

```python
from fastapi import FastAPI
from pyrate_limiter import Duration, Limiter, Rate

from fastapi_rate_limiter.middleware import PathBasedRateLimiterMiddleware

app = FastAPI()

app.add_middleware(
    PathBasedRateLimiterMiddleware,
    limiter=Limiter(Rate(2, Duration.SECOND * 5)),
    path_prefix="/api",
)
```

You can also match paths using regular expressions:

```python
app.add_middleware(
    PathBasedRateLimiterMiddleware,
    limiter=Limiter(Rate(2, Duration.SECOND * 5)),
    path_pattern=r"^/api/v\d+/",
)
```

## WebSockets

```python
from fastapi import FastAPI, HTTPException, WebSocket
from pyrate_limiter import Duration, Limiter, Rate
from starlette.websockets import WebSocketDisconnect

from fastapi_rate_limiter.depends import WebSocketRateLimiter

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    ratelimit = WebSocketRateLimiter(limiter=Limiter(Rate(1, Duration.SECOND * 5)))

    while True:
        try:
            data = await websocket.receive_text()
            await ratelimit(websocket, context_key=data)
            await websocket.send_text("Hello, world")
        except WebSocketDisconnect:
            break
        except HTTPException:
            await websocket.send_text("Rate limited")
```

## Development

```bash
uv sync
uv run ruff check
uv run ruff format --check
uv run pytest -v -m "not integration"
```
