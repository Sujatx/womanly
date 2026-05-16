"""DLQ consumer utility to process items from Redis DLQ.

Provides a simple CLI-friendly consumer that can be run as a one-off or scheduled.
"""
import json
import time
from typing import Callable, Any
import redis
from app.config import settings
from app.core.logging import get_structured_logger
from prometheus_client import Counter

logger = get_structured_logger(__name__)
DLQ_PROCESSED = Counter("womanly_dlq_processed_total", "Number of DLQ entries processed")


def get_redis_client():
    return redis.from_url(settings.REDIS_URL, decode_responses=True)


def consume_dlq(process_fn: Callable[[dict], Any] | None = None, batch: int = 10, poll_interval: float = 1.0):
    client = get_redis_client()
    while True:
        try:
            items = client.lrange("womanly:dlq", 0, batch - 1)
            if not items:
                time.sleep(poll_interval)
                continue

            for raw in items:
                try:
                    data = json.loads(raw)
                    if process_fn:
                        process_fn(data)
                    # Remove the item once processed
                    client.lrem("womanly:dlq", 0, raw)
                    DLQ_PROCESSED.inc()
                except Exception:
                    logger.exception("Failed processing DLQ item")

        except Exception:
            logger.exception("DLQ consumer encountered an error; retrying in 5s")
            time.sleep(5)


if __name__ == "__main__":
    # Simple runner that just prints entries
    def _print_item(d):
        print("DLQ:", d)

    consume_dlq(process_fn=_print_item)
