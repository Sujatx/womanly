"""Lightweight circuit breaker for external service calls.

The breaker prefers Redis for cross-process coordination and falls back to an
in-memory state store when Redis is unavailable.
"""

from __future__ import annotations

import inspect
import logging
import time
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Optional, TypeVar

import redis

from app.config import settings
from app.core.exceptions import ExternalServiceException

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class CircuitBreakerStatus:
    state: str
    failures: int
    opened_at: Optional[float]
    retry_after_seconds: int


class _MemoryStore:
    def __init__(self):
        self._state: dict[str, dict[str, Any]] = {}

    def get(self, key: str) -> Optional[str]:
        data = self._state.get(key)
        return None if data is None else str(data.get("value"))

    def set(self, key: str, value: str, ex: Optional[int] = None) -> None:
        self._state[key] = {"value": value, "expires_at": time.time() + ex if ex else None}

    def incr(self, key: str) -> int:
        current = int(self._state.get(key, {}).get("value", 0)) + 1
        self._state[key] = {"value": current, "expires_at": None}
        return current

    def delete(self, *keys: str) -> None:
        for key in keys:
            self._state.pop(key, None)


class CircuitBreaker:
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

    def __init__(
        self,
        name: str,
        service_name: str,
        failure_threshold: int = 3,
        recovery_timeout: int = 60,
    ):
        self.name = name
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._redis = self._init_redis()
        self._memory = _MemoryStore()

    def _init_redis(self):
        try:
            return redis.from_url(settings.REDIS_URL, decode_responses=True)
        except Exception as exc:
            logger.warning("Circuit breaker using in-memory state for %s: %s", self.name, exc)
            return None

    def _key(self, suffix: str) -> str:
        return f"circuit:{self.name}:{suffix}"

    def _get(self, suffix: str) -> Optional[str]:
        if self._redis:
            try:
                return self._redis.get(self._key(suffix))
            except Exception as exc:
                logger.warning("Circuit breaker redis get failed for %s: %s", self.name, exc)
                self._redis = None
        return self._memory.get(self._key(suffix))

    def _set(self, suffix: str, value: Any, ex: Optional[int] = None) -> None:
        if self._redis:
            try:
                self._redis.set(self._key(suffix), value, ex=ex)
                return
            except Exception as exc:
                logger.warning("Circuit breaker redis set failed for %s: %s", self.name, exc)
                self._redis = None
        self._memory.set(self._key(suffix), str(value), ex=ex)

    def _delete(self, *suffixes: str) -> None:
        keys = [self._key(suffix) for suffix in suffixes]
        if self._redis:
            try:
                self._redis.delete(*keys)
                return
            except Exception as exc:
                logger.warning("Circuit breaker redis delete failed for %s: %s", self.name, exc)
                self._redis = None
        self._memory.delete(*keys)

    def status(self) -> CircuitBreakerStatus:
        state = self._get("state") or self.CLOSED
        failures = int(self._get("failures") or 0)
        opened_at_raw = self._get("opened_at")
        opened_at = float(opened_at_raw) if opened_at_raw else None
        retry_after = 0
        if state == self.OPEN and opened_at is not None:
            elapsed = time.time() - opened_at
            retry_after = max(0, int(self.recovery_timeout - elapsed))
        return CircuitBreakerStatus(
            state=state,
            failures=failures,
            opened_at=opened_at,
            retry_after_seconds=retry_after,
        )

    def _open(self) -> None:
        self._set("state", self.OPEN)
        self._set("opened_at", str(time.time()))
        self._set("failures", str(self.failure_threshold))

    def _close(self) -> None:
        self._delete("state", "opened_at", "failures")

    def _half_open(self) -> None:
        self._set("state", self.HALF_OPEN)

    def _before_call(self) -> bool:
        status = self.status()
        if status.state == self.CLOSED:
            return True
        if status.state == self.HALF_OPEN:
            return True
        if status.opened_at is None:
            self._open()
            return False
        if time.time() - status.opened_at >= self.recovery_timeout:
            self._half_open()
            return True
        return False

    def _record_success(self) -> None:
        self._close()

    def _record_failure(self) -> None:
        current = int(self._get("failures") or 0) + 1
        self._set("failures", str(current))
        if current >= self.failure_threshold:
            self._open()

    def call(
        self,
        func: Callable[..., T],
        *args: Any,
        fallback: Optional[Callable[[], T]] = None,
        **kwargs: Any,
    ) -> T:
        if not self._before_call():
            if fallback:
                return fallback()
            raise ExternalServiceException(self.service_name, "temporarily unavailable", {"circuit": "open"})

        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result
        except Exception as exc:
            self._record_failure()
            if fallback:
                return fallback()
            raise ExternalServiceException(self.service_name, str(exc), {"circuit": self.status().state}) from exc

    async def acall(
        self,
        func: Callable[..., Awaitable[T]],
        *args: Any,
        fallback: Optional[Callable[[], T] | Callable[[], Awaitable[T]]] = None,
        **kwargs: Any,
    ) -> T:
        if not self._before_call():
            if fallback:
                result = fallback()
                return await result if inspect.isawaitable(result) else result
            raise ExternalServiceException(self.service_name, "temporarily unavailable", {"circuit": "open"})

        try:
            result = await func(*args, **kwargs)
            self._record_success()
            return result
        except Exception as exc:
            self._record_failure()
            if fallback:
                result = fallback()
                return await result if inspect.isawaitable(result) else result
            raise ExternalServiceException(self.service_name, str(exc), {"circuit": self.status().state}) from exc
