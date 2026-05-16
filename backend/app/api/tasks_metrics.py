"""Simple task metrics endpoints for monitoring Celery queues and DLQ."""
from fastapi import APIRouter, Response, status
from app.core.logging import get_structured_logger
from app.config import settings

router = APIRouter()
logger = get_structured_logger(__name__)


@router.get("/tasks/metrics")
async def tasks_metrics():
    """Return basic Celery queue and DLQ stats.

    This endpoint attempts to contact Redis and report counts. It is best-effort.
    """
    try:
        import redis
        import json
        client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        dlq_len = client.llen("womanly:dlq")
        # Optionally, show first 5 DLQ entries (truncated)
        raw = client.lrange("womanly:dlq", 0, 4)
        dlq_sample = [json.loads(x) for x in raw]
        return {"dlq_count": dlq_len, "dlq_sample": dlq_sample}
    except Exception as e:
        logger.warning("Could not fetch task metrics", error=str(e))
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content="{}")
