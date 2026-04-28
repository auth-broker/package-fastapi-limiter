"""Integration-style tests for dependency and middleware rate limiting."""

from time import sleep

from starlette.testclient import TestClient

from tests.examples.main import app
from tests.examples.middleware import app as middleware_app


def test_limiter():
    """Validate per-route request limits for GET and POST endpoints."""
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200

        response = client.get("/")
        assert response.status_code == 200

        response = client.get("/")
        assert response.status_code == 429

        response = client.post("/")
        assert response.status_code == 200

        response = client.post("/")
        assert response.status_code == 429
        sleep(5)

        response = client.get("/")
        assert response.status_code == 200

        response = client.post("/")
        assert response.status_code == 200


def test_limiter_multiple():
    """Validate behavior when multiple limiters apply to one endpoint."""
    with TestClient(app) as client:
        response = client.get("/multiple")
        assert response.status_code == 200

        response = client.get("/multiple")
        assert response.status_code == 429
        sleep(5)

        response = client.get("/multiple")
        assert response.status_code == 200

        response = client.get("/multiple")
        assert response.status_code == 429
        sleep(10)

        response = client.get("/multiple")
        assert response.status_code == 200


def test_limiter_websockets():
    """Validate WebSocket rate limiting with context keys."""
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            ws.send_text("Hi")
            data = ws.receive_text()
            assert data == "Hello, world"

            ws.send_text("Hi")
            data = ws.receive_text()
            assert data == "Hello again"

            ws.send_text("Hi 2")
            data = ws.receive_text()
            assert data == "Hello again"
            ws.close()


def test_skip_limiter():
    """Validate routes configured to skip limiting are never blocked."""
    with TestClient(app) as client:
        for _ in range(5):
            response = client.get("/skip")
            assert response.status_code == 200


def test_middleware():
    """Validate middleware-level limiting across different routes."""
    with TestClient(middleware_app) as client:
        response = client.get("/")
        assert response.status_code == 200

        response = client.get("/")
        assert response.status_code == 200

        # Global limit of 2 per 5s reached
        response = client.get("/")
        assert response.status_code == 429

        # Different path but same global limiter
        response = client.get("/other")
        assert response.status_code == 429

        sleep(5)

        response = client.get("/")
        assert response.status_code == 200
