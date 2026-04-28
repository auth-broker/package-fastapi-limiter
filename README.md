<div align="center">

# FastAPI Limiter
FastAPI-Limiter is a rate limiting tool for [fastapi](https://github.com/tiangolo/fastapi) routes, powered by [pyrate-limiter](https://github.com/vutran1710/PyrateLimiter).

![Python](https://img.shields.io/badge/Python-3.12-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![UV](https://img.shields.io/badge/UV-Fast-6E40C9?style=for-the-badge)
![Hatchling](https://img.shields.io/badge/Hatchling-PEP517-6E40C9?style=for-the-badge)
![Ruff](https://img.shields.io/badge/Ruff-Lint-000000?style=for-the-badge)
![Pre-commit](https://img.shields.io/badge/Pre--commit-Hooks-000000?style=for-the-badge)
![Pytest](https://img.shields.io/badge/Pytest-Unit%2BAsync-08979C?style=for-the-badge)
![Coverage](https://img.shields.io/badge/Cov-Reports-08979C?style=for-the-badge)
![GitHub Actions](https://img.shields.io/badge/Actions-CI%2FCD-F7B500?style=for-the-badge&logo=github-actions)
![PyPI](https://img.shields.io/badge/PyPI-Publish-6E40C9?style=for-the-badge)
![Makefile](https://img.shields.io/badge/Makefile-Scripts-F7B500?style=for-the-badge)

🦜🕸️

[![CI](https://github.com/auth-broker/package-fastapi-limiter/actions/workflows/ci.yaml/badge.svg?branch=main)](https://github.com/auth-broker/package-fastapi-limiter/actions/workflows/ci.yaml)

</div>

NOTE: This is a fork of (https://github.com/long2ice/fastapi-limiter), currently because the original maintainer [@long2ice](https://github.com/long2ice) has not published the latest version which supports FastAPI middleware.

[<img width="1662" height="470" alt="image" src="https://github.com/user-attachments/assets/aaa72fd0-56e5-4b04-bb7d-848e630ea95b" />](https://github.com/long2ice/fastapi-limiter/actions)


______________________________________________________________________

## Table of Contents

<!-- toc -->

- [Introduction](#introduction)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Formatting and linting](#formatting-and-linting)
- [CICD](#cicd)

<!-- tocstop -->

______________________________________________________________________

## Introduction

FastAPI-Limiter is a rate limiting tool for [fastapi](https://github.com/tiangolo/fastapi) routes, powered by [pyrate-limiter](https://github.com/vutran1710/PyrateLimiter).

______________________________________________________________________

## Quick Start

Since this is just a package, and not a service, there is no real "run" action.
But you can run the tests immediately.

Here are a list of available commands via make.

### Bare Metal (i.e. your machine)

1. `make install` - install the required dependencies.
1. `make test` - runs the tests.

### Docker

1. `make build-docker` - build the docker image.
1. `make run-docker` - run the docker compose services.
1. `make test-docker` - run the tests in docker.
1. `make clean-docker` - remove all docker containers etc.

______________________________________________________________________

## Installation

### For Dev work on the repo

Install `uv`, (_if you haven't already_)
https://docs.astral.sh/uv/getting-started/installation/#installation-methods

```shell
brew install uv
```

Initialise pre-commit (validates ruff on commit.)

```shell
uv run pre-commit install
```

Install dependencies (including dev dependencies)

```shell
uv sync
```

If you are adding a new dev dependency, please run:

```shell
uv add --dev {your-new-package}
```

### Namespaces

Packages all share the same namespace `ab_core`. To import this package into
your project:

```python
from ab_core.template import placeholder_func
```

We encourage you to make your package available to all of ab via this
`ab_core` namespace. The goal is to streamline development, POCs and overall
collaboration.

______________________________________________________________________

## Usage

### Adding the dependency to your project

The library is available on PyPI. You can install it using the following
command:

**Using pip**:

```shell
pip install ab-fastapi-limiter
```

**Using UV**

Note: there is currently no nice way like poetry, hence we still needd to
provide the full url. https://github.com/astral-sh/uv/issues/10140

Add the dependency

```shell
uv add ab-fastapi-limiter
```

**Using poetry**:

Then run the following command to install the package:

```shell
poetry add ab-fastapi-limiter
```

### How tos

## Quick Start

FastAPI-Limiter is simple to use, which just provides a dependency `RateLimiter`. The following example allows `2` requests per `5` seconds on route `/`.

```py
import uvicorn
from fastapi import Depends, FastAPI
from pyrate_limiter import Duration, Limiter, Rate

from ab_core.fastapi_limiter.depends import RateLimiter

app = FastAPI()

@app.get(
    "/",
    dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(2, Duration.SECOND * 5))))],
)
async def index():
    return {"msg": "Hello World"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
```

## Usage

### RateLimiter

`RateLimiter` accepts the following parameters:

- `limiter`: A `pyrate_limiter.Limiter` instance that defines the rate limiting rules.
- `identifier`: A callable to identify the request source, default is by IP + path.
- `callback`: A callable invoked when the rate limit is exceeded, default raises `HTTPException` with `429` status code.
- `blocking`: Whether to block the request when the rate limit is exceeded, default is `False`.
- `skip`: An async callable that takes a request and returns `True` to skip rate limiting, default is `None`.

### Identifier

Identifier of route limit, default is `ip + path`, you can override it such as `userid` and so on.

```py
async def default_identifier(request: Union[Request, WebSocket]):
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ip = forwarded.split(",")[0]
    elif request.client:
        ip = request.client.host
    else:
        ip = "127.0.0.1"
    return ip + ":" + request.scope["path"]
```

### Callback

Callback when rate limit is exceeded, default raises `HTTPException` with `429` status code.

```py
def default_callback(*args, **kwargs):
    raise HTTPException(
        HTTP_429_TOO_MANY_REQUESTS,
        "Too Many Requests",
    )
```

### Multiple limiters

You can use multiple limiters in one route.

```py
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

Note that you should keep the stricter limiter (lower `seconds/times` ratio) first.

### Skip rate limiting

You can pass a `skip` callable to `RateLimiter` to conditionally skip rate limiting for a specific route. The callable receives the request and should return `True` to skip.

```py
from fastapi.requests import Request

async def skip(request: Request):
    return request.scope["path"] == "/skip"

@app.get(
    "/skip",
    dependencies=[
        Depends(RateLimiter(limiter=Limiter(Rate(1, Duration.SECOND * 5)), skip=skip))
    ],
)
async def skip_route():
    return {"msg": "This route skips rate limiting"}
```

### Middleware

You can also use `RateLimiterMiddleware` to apply rate limiting globally to all routes without adding dependencies to each route individually.

```py
from fastapi import FastAPI
from pyrate_limiter import Duration, Limiter, Rate

from ab_core.fastapi_limiter.middleware import RateLimiterMiddleware

app = FastAPI()

app.add_middleware(
    RateLimiterMiddleware,
    limiter=Limiter(Rate(2, Duration.SECOND * 5)),
)


@app.get("/")
async def index():
    return {"msg": "Hello World"}
```

`RateLimiterMiddleware` accepts the same `identifier`, `callback`, `blocking`, and `skip` parameters as `RateLimiter`.

### Rate limiting within a websocket

While the above examples work with REST requests, FastAPI also allows easy usage
of websockets, which require a slightly different approach.

Because websockets are likely to be long lived, you may want to rate limit in
response to data sent over the socket.

You can do this by rate limiting within the body of the websocket handler:

```py
from ab_core.fastapi_limiter.depends import WebSocketRateLimiter

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    ratelimit = WebSocketRateLimiter(limiter=Limiter(Rate(1, Duration.SECOND * 5)))
    while True:
        try:
            data = await websocket.receive_text()
            await ratelimit(websocket, context_key=data)  # NB: context_key is optional
            await websocket.send_text("Hello, world")
        except HTTPException:
            await websocket.send_text("Hello again")
```

______________________________________________________________________

## Formatting and linting

We use Ruff as the formatter and linter. The pre-commit has hooks which runs
checking and applies linting automatically. The CI validates the linting,
ensuring main is always looking clean.

You can manually use these commands too:

1. `make lint` - check for linting issues.
1. `make format` - fix linting issues.

______________________________________________________________________

## CICD

### Publishing to PyPI

We publish to PyPI using Github releases. Steps are as follows:

1. Manually update the version in `pyproject.toml` file using a PR and merge to
   main. Use `uv version --bump {patch/minor/major}` to update the version.
1. Create a new release in Github with the tag name as the version number. This
   will trigger the `publish` workflow. In the Release window, type in the
   version number and it will prompt to create a new tag.
1. Verify the release in
   [PyPI](https://pypi.org/project/ab-fastapi-limiter/)
