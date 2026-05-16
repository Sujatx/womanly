"""Core application utilities and infrastructure."""

from collections import defaultdict
from datetime import datetime
from typing import Callable, Dict, List, Optional, Type, TypeVar

from fastapi import APIRouter, Request, Response
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy import Select
from sqlmodel import SQLModel, Session, select

from app.config import settings
from app.core.error_handler import add_error_handlers
from app.core.exceptions import AppException
from app.core.logging import get_structured_logger

logger = get_structured_logger(__name__)

T = TypeVar("T", bound=SQLModel)

# API versioning metadata
CURRENT_VERSION = "v1"
SUPPORTED_VERSIONS = ["v1"]
DEPRECATED_VERSIONS = []
LEGACY_API_DEPRECATION_DATE = datetime(2026, 9, 1)
LEGACY_API_SUNSET_DATE = datetime(2027, 3, 1)


def create_versioned_router(prefix: str, version: str = "v1") -> APIRouter:
    return APIRouter(prefix=f"/api/{version}/{prefix}")


def add_deprecation_warning(response: Response, sunset_date: datetime) -> None:
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = sunset_date.strftime("%a, %d %b %Y %H:%M:%S GMT")
    response.headers["Link"] = '<https://docs.womanly.com/api/migration>; rel="deprecation"'


async def deprecation_middleware(request: Request, call_next: Callable):
    path = request.url.path
    is_legacy_route = not path.startswith("/api/v") and path not in ["/", "/health", "/docs", "/redoc", "/openapi.json"]

    if is_legacy_route:
        logger.warning(
            "Legacy API endpoint accessed",
            path=path,
            method=request.method,
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            deprecation_date=LEGACY_API_DEPRECATION_DATE.isoformat(),
            sunset_date=LEGACY_API_SUNSET_DATE.isoformat(),
        )

    response = await call_next(request)
    if is_legacy_route:
        add_deprecation_warning(response, LEGACY_API_SUNSET_DATE)
    return response


def get_api_version_info() -> dict:
    return {
        "current_version": CURRENT_VERSION,
        "supported_versions": SUPPORTED_VERSIONS,
        "deprecated_versions": DEPRECATED_VERSIONS,
        "legacy_api_deprecation_date": LEGACY_API_DEPRECATION_DATE.isoformat(),
        "legacy_api_sunset_date": LEGACY_API_SUNSET_DATE.isoformat(),
        "migration_guide": "https://docs.womanly.com/api/migration",
    }


class QueryMonitor:
    def __init__(self, request_id: str):
        self.request_id = request_id
        self.queries: List[Dict] = []
        self.table_counts: Dict[str, int] = defaultdict(int)

    def add_query(self, statement: str, duration_ms: float):
        self.queries.append({"statement": statement[:200], "duration_ms": duration_ms})
        statement_lower = statement.lower()
        for word in statement_lower.split():
            if any(kw in statement_lower for kw in ["from ", "join ", "update ", "into "]):
                self.table_counts[word] += 1

    def check_n_plus_one(self) -> bool:
        for table, count in self.table_counts.items():
            if count > 2:
                return True
        return False

    def get_stats(self) -> Dict:
        total_queries = len(self.queries)
        total_duration = sum(q["duration_ms"] for q in self.queries)
        return {
            "request_id": self.request_id,
            "total_queries": total_queries,
            "total_duration_ms": round(total_duration, 2),
            "avg_duration_ms": round(total_duration / total_queries, 2) if total_queries > 0 else 0,
            "table_counts": dict(self.table_counts),
            "has_n_plus_one": self.check_n_plus_one(),
        }


_request_query_counts: Dict[str, Dict[str, int]] = {}
_active_monitors: Dict[str, QueryMonitor] = {}


def start_query_monitoring(request_id: str):
    _active_monitors[request_id] = QueryMonitor(request_id)


def stop_query_monitoring(request_id: str) -> Dict:
    monitor = _active_monitors.pop(request_id, None)
    return monitor.get_stats() if monitor else {}


def get_current_monitor(request_id: str) -> Optional[QueryMonitor]:
    return _active_monitors.get(request_id)


if settings.ENV_NAME == "dev":

    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault("query_start_time", []).append(__import__("time").perf_counter())

    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        query_start_times = conn.info.get("query_start_time", [])
        if query_start_times:
            start_time = query_start_times.pop()
            duration_ms = (__import__("time").perf_counter() - start_time) * 1000
            if duration_ms > 100:
                logger.warning("Slow query detected", duration_ms=round(duration_ms, 2), statement=statement[:200])


async def query_monitoring_middleware(request: Request, call_next):
    request_id = getattr(request.state, "request_id", None)
    if request_id and settings.ENV_NAME == "dev":
        start_query_monitoring(request_id)

    response = await call_next(request)

    if request_id and settings.ENV_NAME == "dev":
        stats = stop_query_monitoring(request_id)
        if stats.get("total_queries", 0) > 10:
            logger.warning("High query count detected", path=request.url.path, **stats)
        if stats.get("has_n_plus_one"):
            logger.warning("Potential N+1 query problem detected", path=request.url.path, **stats)

    return response


def exclude_deleted(query: Select, model: Type[T]) -> Select:
    if hasattr(model, "deleted_at"):
        return query.where(model.deleted_at.is_(None))
    return query


def only_deleted(query: Select, model: Type[T]) -> Select:
    if hasattr(model, "deleted_at"):
        return query.where(model.deleted_at.isnot(None))
    return query


def get_active_record(session: Session, model: Type[T], record_id: int) -> Optional[T]:
    query = select(model).where(model.id == record_id)
    query = exclude_deleted(query, model)
    return session.exec(query).first()


def soft_delete_record(session: Session, record: SQLModel) -> None:
    if hasattr(record, "soft_delete"):
        record.soft_delete()
        session.add(record)
        session.commit()
    else:
        raise ValueError(f"{type(record).__name__} does not support soft delete")


def restore_record(session: Session, record: SQLModel) -> None:
    if hasattr(record, "deleted_at"):
        record.deleted_at = None
        if hasattr(record, "is_active"):
            record.is_active = True
        session.add(record)
        session.commit()
    else:
        raise ValueError(f"{type(record).__name__} does not support soft delete")


def hard_delete_record(session: Session, record: SQLModel) -> None:
    session.delete(record)
    session.commit()


__all__ = [
    "AppException",
    "add_error_handlers",
    "create_versioned_router",
    "add_deprecation_warning",
    "deprecation_middleware",
    "get_api_version_info",
    "query_monitoring_middleware",
    "exclude_deleted",
    "only_deleted",
    "get_active_record",
    "soft_delete_record",
    "restore_record",
    "hard_delete_record",
]
