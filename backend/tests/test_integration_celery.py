import os
import time
import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_CELERY_INTEGRATION", "false").lower() != "true",
    reason="Integration test for Celery+Redis disabled by default",
)


def test_celery_failure_pushes_to_dlq():
    """Start a task that fails and assert an entry appears in Redis DLQ.

    This test is intended to run in CI where Redis and a Celery worker are available.
    """
    import redis
    from app.celery_app import celery_app

    client = redis.from_url(celery_app.conf.broker_url, decode_responses=True)

    # Ensure DLQ is empty
    client.delete("womanly:dlq")

    # Send failing task
    celery_app.send_task("app.tasks.debug.fail_task")

    # Poll for DLQ entry
    timeout = 30
    start = time.time()
    while time.time() - start < timeout:
        if client.llen("womanly:dlq") > 0:
            break
        time.sleep(1)

    assert client.llen("womanly:dlq") > 0, "No DLQ entry found after worker processed failing task"
