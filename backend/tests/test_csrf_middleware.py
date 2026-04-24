from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.csrf import CSRFProtectionMiddleware


def test_csrf_blocks_state_change_without_token() -> None:
    app = FastAPI()
    app.add_middleware(CSRFProtectionMiddleware)

    @app.post("/api/v1/orders")
    async def create_order() -> dict[str, bool]:
        return {"ok": True}

    client = TestClient(app)
    response = client.post("/api/v1/orders")

    assert response.status_code == 403
    assert "CSRF token missing" in response.json()["detail"]


def test_csrf_allows_bearer_authenticated_state_change() -> None:
    app = FastAPI()
    app.add_middleware(CSRFProtectionMiddleware)

    @app.post("/api/v1/orders")
    async def create_order() -> dict[str, bool]:
        return {"ok": True}

    client = TestClient(app)
    response = client.post(
        "/api/v1/orders",
        headers={"Authorization": "Bearer fake-token"},
    )

    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_csrf_excluded_auth_paths_bypass_token_check() -> None:
    app = FastAPI()
    app.add_middleware(CSRFProtectionMiddleware)

    @app.post("/api/v1/auth/login")
    async def login() -> dict[str, bool]:
        return {"ok": True}

    client = TestClient(app)
    response = client.post("/api/v1/auth/login")

    assert response.status_code == 200
    assert response.json() == {"ok": True}
