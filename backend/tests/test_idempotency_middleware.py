from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.idempotency import IDEMPOTENT_ENDPOINTS, IdempotencyMiddleware


def test_idempotent_endpoints_are_versioned_paths() -> None:
    assert "/api/v1/payments/create-order" in IDEMPOTENT_ENDPOINTS
    assert "/api/v1/payments/verify" in IDEMPOTENT_ENDPOINTS


def test_idempotency_key_is_required_for_create_order() -> None:
    app = FastAPI()
    app.add_middleware(IdempotencyMiddleware)

    @app.post("/api/v1/payments/create-order")
    async def create_order() -> dict[str, bool]:
        return {"ok": True}

    client = TestClient(app)
    response = client.post("/api/v1/payments/create-order")

    assert response.status_code == 400
    assert "Idempotency-Key header is required" in response.json()["detail"]


def test_idempotency_key_format_is_validated() -> None:
    app = FastAPI()
    app.add_middleware(IdempotencyMiddleware)

    @app.post("/api/v1/payments/create-order")
    async def create_order() -> dict[str, bool]:
        return {"ok": True}

    client = TestClient(app)
    response = client.post(
        "/api/v1/payments/create-order",
        headers={"Idempotency-Key": "short"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid Idempotency-Key format"


def test_non_idempotent_paths_do_not_require_header() -> None:
    app = FastAPI()
    app.add_middleware(IdempotencyMiddleware)

    @app.post("/api/v1/orders")
    async def create_order() -> dict[str, bool]:
        return {"ok": True}

    client = TestClient(app)
    response = client.post("/api/v1/orders")

    assert response.status_code == 200
    assert response.json() == {"ok": True}
