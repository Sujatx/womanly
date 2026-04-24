from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.metrics import router as metrics_router
from app.middleware.metrics import metrics_middleware


def test_metrics_endpoint_exposes_prometheus_format() -> None:
    app = FastAPI()
    app.middleware("http")(metrics_middleware)

    @app.get("/ok")
    def ok() -> dict[str, bool]:
        return {"ok": True}

    app.include_router(metrics_router)
    client = TestClient(app)

    response = client.get("/ok")
    assert response.status_code == 200

    metrics_response = client.get("/metrics")
    assert metrics_response.status_code == 200
    assert "text/plain" in metrics_response.headers["content-type"]

    body = metrics_response.text
    assert "womanly_http_requests_total" in body
    assert "womanly_http_request_duration_seconds" in body
    assert "womanly_http_inflight_requests" in body
    assert "path=\"/ok\"" in body