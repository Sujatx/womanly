import logging

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.error_handler import add_error_handlers
from app.core.logging import RequestIdLogFilter, reset_request_id, set_request_id


def test_request_id_log_filter_uses_context_value() -> None:
    record = logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="hello",
        args=(),
        exc_info=None,
    )

    filter_ = RequestIdLogFilter()
    token = set_request_id("req-abc-123")
    try:
        allowed = filter_.filter(record)
    finally:
        reset_request_id(token)

    assert allowed is True
    assert getattr(record, "request_id", None) == "req-abc-123"


def test_request_id_header_is_passthrough_and_returned() -> None:
    app = FastAPI()
    add_error_handlers(app)

    @app.get("/ping")
    def ping() -> dict[str, bool]:
        return {"ok": True}

    client = TestClient(app)
    response = client.get("/ping", headers={"X-Request-ID": "req-inbound-42"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-inbound-42"