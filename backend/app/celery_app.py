"""
Celery application bootstrap for background tasks.

Connects to Redis broker configured from `app.config.settings` and
autodiscover tasks under `app.tasks`.
"""
from celery import Celery
from prometheus_client import Counter
from app.config import settings
from app.core.logging import get_structured_logger

logger = get_structured_logger(__name__)

# Prometheus metrics for Celery
CELERY_TASKS_RECEIVED = Counter("womanly_celery_tasks_received_total", "Total Celery tasks received")
CELERY_TASKS_SUCCEEDED = Counter("womanly_celery_tasks_succeeded_total", "Total Celery tasks succeeded")
CELERY_TASKS_FAILED = Counter("womanly_celery_tasks_failed_total", "Total Celery tasks failed")


def make_celery(app_name: str = "womanly") -> Celery:
    broker_url = getattr(settings, "CELERY_BROKER_URL", None) or getattr(settings, "REDIS_URL", None) or settings.REDIS_URL
    backend_url = getattr(settings, "CELERY_RESULT_BACKEND", None) or getattr(settings, "REDIS_URL", None) or settings.REDIS_URL

    celery = Celery(app_name, broker=broker_url, backend=backend_url)

    # Recommended Celery settings
    celery.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone=getattr(settings, "TIMEZONE", "UTC"),
        enable_utc=True,
        task_acks_late=True,
        worker_prefetch_multiplier=1,
        task_track_started=True,
    )

    # Auto-discover tasks
    celery.autodiscover_tasks(["app.tasks"], related_name="app.tasks")
    # Wire Celery signals for metrics and DLQ
    try:
        from celery.signals import task_failure, task_prerun, task_postrun
        from app.tasks.utils import push_to_dlq

        def _on_task_failure(sender=None, task_id=None, exception=None, args=None, kwargs=None, **kw):
            try:
                CELERY_TASKS_FAILED.inc()
            except Exception:
                pass
            try:
                push_to_dlq(sender.name if sender else "unknown", task_id, args, kwargs, exception)
            except Exception:
                logger.exception("DLQ handler failed")

        def _on_task_prerun(sender=None, task_id=None, task=None, args=None, kwargs=None, **kw):
            try:
                CELERY_TASKS_RECEIVED.inc()
            except Exception:
                pass

        def _on_task_postrun(sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None, **kw):
            try:
                # state may be 'SUCCESS' or others
                if state == "SUCCESS":
                    CELERY_TASKS_SUCCEEDED.inc()
            except Exception:
                pass

        task_failure.connect(_on_task_failure)
        task_prerun.connect(_on_task_prerun)
        task_postrun.connect(_on_task_postrun)
    except Exception:
        logger.warning("Could not wire Celery signals for metrics/DLQ handler")

    logger.info("Celery configured", broker=broker_url)
    return celery


# Example beat schedule for periodic jobs
try:
    celery_app.conf.beat_schedule = {
        "inventory-sync-every-5-minutes": {
            "task": "app.tasks.inventory.sync_inventory",
            "schedule": 300.0,
            "args": ("warehouse_api",),
        },
    }
except Exception:
    # Celery might not be importable in this environment; ignore at runtime compile
    pass


celery_app = make_celery()
