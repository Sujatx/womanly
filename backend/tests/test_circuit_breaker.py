import time

import pytest

from app.core.circuit_breaker import CircuitBreaker
from app.core.exceptions import ExternalServiceException


def test_circuit_breaker_opens_and_recovers(monkeypatch):
    breaker = CircuitBreaker("test-service", "email", failure_threshold=2, recovery_timeout=1)
    breaker._redis = None

    assert breaker.call(lambda: "ok") == "ok"
    assert breaker.status().state == breaker.CLOSED

    def boom():
        raise ValueError("boom")

    with pytest.raises(ExternalServiceException):
        breaker.call(boom)
    with pytest.raises(ExternalServiceException):
        breaker.call(boom)

    assert breaker.status().state == breaker.OPEN

    assert breaker.call(lambda: "fallback", fallback=lambda: "queued") == "queued"

    breaker._set("opened_at", str(time.time() - 2))
    breaker._set("state", breaker.OPEN)
    assert breaker.call(lambda: "recovered") == "recovered"
    assert breaker.status().state == breaker.CLOSED
