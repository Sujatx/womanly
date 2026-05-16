from app.celery_app import celery_app


@celery_app.task(bind=True, name="app.tasks.debug.fail_task", max_retries=0)
def fail_task(self):
    """A simple task that always raises to exercise DLQ behavior."""
    raise RuntimeError("intentional failure for integration test")
