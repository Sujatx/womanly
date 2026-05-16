Local Celery + Redis Runbook

Purpose: quick steps to run Celery worker, Redis, and DLQ consumer locally for development and to run the integration test used in CI.

Prereqs:
- Docker (for Redis) or a local Redis installation
- Python virtualenv with project deps installed (backend/requirements.txt)

1) Start Redis (Docker)

PowerShell:
```
# Run Redis in a container
docker run --rm -p 6379:6379 --name womanly-redis redis:7
```

Linux / macOS:
```
docker run --rm -p 6379:6379 --name womanly-redis redis:7
```

2) Start a Celery worker (backend)

PowerShell (in repo root):
```
cd backend
# Activate venv if needed
celery -A app.celery_app.celery_app worker --loglevel=info
```

3) (Optional) Start a beat scheduler if periodic tasks are used

```
cd backend
celery -A app.celery_app.celery_app beat --loglevel=info
```

4) Run DLQ consumer (reads `womanly:dlq` Redis list and processes items)

```
cd backend
python -m app.tasks.dlq_consumer
```

5) Run the integration test locally (mirrors CI)

PowerShell:
```
cd backend
# set env to enable running the integration test which expects Redis + a worker
$env:RUN_CELERY_INTEGRATION = 'true'
pytest -q tests/test_integration_celery.py
```

Notes & troubleshooting:
- If tasks fail to import due to missing Celery in a minimal dev environment, see `backend/tests/test_tasks.py` which demonstrates a technique to place a minimal fake `celery` module in `sys.modules` for import-time checks.
- CI uses a Redis service and launches a worker in the `celery-integration.yml` workflow.

Contact: ops@yourorg.example (placeholder)
