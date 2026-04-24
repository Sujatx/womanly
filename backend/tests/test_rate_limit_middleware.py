from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.rate_limit import RateLimitMiddleware, RateLimitStore, rate_limit_store


def test_rate_limit_store_enforces_limit_after_max_attempts() -> None:
    store = RateLimitStore()
    key = "login:127.0.0.1"

    assert store.is_rate_limited(key, max_attempts=1, window_seconds=60) is False
    assert store.is_rate_limited(key, max_attempts=1, window_seconds=60) is True


def test_rate_limit_middleware_blocks_after_configured_limit() -> None:
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware)

    @app.post("/api/v1/auth/login")
    async def login() -> dict[str, bool]:
        return {"ok": True}

    rate_limit_store.reset("/api/v1/auth/login:testclient")
    client = TestClient(app)

    for _ in range(5):
        response = client.post("/api/v1/auth/login")
        assert response.status_code == 200

    blocked = client.post("/api/v1/auth/login")
    assert blocked.status_code == 429
    assert blocked.json()["detail"] == "Too many attempts. Please try again later."


def test_rate_limit_headers_are_added_for_limited_paths() -> None:
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware)

    @app.post("/api/v1/auth/login")
    async def login() -> dict[str, bool]:
        return {"ok": True}

    rate_limit_store.reset("/api/v1/auth/login:testclient")
    client = TestClient(app)

    response = client.post("/api/v1/auth/login")
    assert response.status_code == 200
    assert response.headers["X-RateLimit-Limit"] == "5"
    assert "X-RateLimit-Remaining" in response.headers
