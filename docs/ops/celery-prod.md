Celery Production Runbook (systemd)

Example `systemd` unit files for running the Celery worker and a separate DLQ consumer on a Linux host.

Prerequisites:
- Redis reachable at the `REDIS_URL` used by the app
- The backend application deployed (virtualenv or container) and `app` package available
- `alembic upgrade head` should be run during deployment

Note: Adapt `User`, `Group`, `WorkingDirectory`, and `Environment` values to your environment.

1) Celery worker (systemd unit)

File: `/etc/systemd/system/womanly-celery.service`

```
[Unit]
Description=Womanly Celery Worker
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/srv/womanly/backend
Environment=PATH=/srv/womanly/.venv/bin
Environment=REDIS_URL=redis://127.0.0.1:6379/0
ExecStart=/srv/womanly/.venv/bin/celery -A app.celery_app.celery_app worker --loglevel=info --concurrency=4
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

2) DLQ consumer (systemd unit)

File: `/etc/systemd/system/womanly-dlq.service`

```
[Unit]
Description=Womanly DLQ Consumer
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/srv/womanly/backend
Environment=PATH=/srv/womanly/.venv/bin
Environment=REDIS_URL=redis://127.0.0.1:6379/0
ExecStart=/srv/womanly/.venv/bin/python -m app.tasks.dlq_consumer
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3) Monitoring notes
- The app exposes a small metrics endpoint (`/api/v1/tasks/metrics`) that reports DLQ length and a sample. Scrape your FastAPI app with Prometheus.
- For Celery-specific metrics, consider running the `prometheus-celery-exporter` or instrumenting tasks using `prometheus_client` counters (already added for DLQ and lifecycle counters).

4) Deployment checklist
- Ensure Redis is reachable and configured (auth, TLS as required)
- Run database migrations: `alembic -c alembic.ini upgrade head` during deployment
- Start or restart systemd services:
  - `systemctl daemon-reload`
  - `systemctl enable --now womanly-celery`
  - `systemctl enable --now womanly-dlq`
- Verify logs: `journalctl -u womanly-celery -f`

Contact ops for any questions about scaling or HA.
