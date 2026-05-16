"""Utility helpers for Celery tasks: DLQ handling and failure signal wiring."""
from typing import Any, Dict
import json
import traceback
import redis
from app.config import settings
from app.core.logging import get_structured_logger
from prometheus_client import Counter

logger = get_structured_logger(__name__)

# Prometheus metric: count of pushes to DLQ
DLQ_PUSHES = Counter("womanly_dlq_push_total", "Number of tasks pushed to DLQ")


def get_redis_client():
    return redis.from_url(settings.REDIS_URL, decode_responses=True)


def push_to_dlq(task_name: str, task_id: str, args: Any, kwargs: Dict[str, Any], exc: Exception) -> None:
    """Push failed task details to a Redis-backed DLQ list for inspection.

    Stored as JSON entries under key `womanly:dlq`.
    """
    try:
        client = get_redis_client()
        payload = {
            "task_name": task_name,
            "task_id": task_id,
            "args": args,
            "kwargs": kwargs,
            "error": str(exc),
            "traceback": traceback.format_exc(),
            "ts": __import__("time").time(),
        }
        client.lpush("womanly:dlq", json.dumps(payload))
        DLQ_PUSHES.inc()
        logger.warning("Pushed task to DLQ", task=task_name, id=task_id)
    except Exception as e:
        logger.error("Failed to push to DLQ", error=str(e))
