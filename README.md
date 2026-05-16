# Womanly E-commerce Platform

Production-ready e-commerce platform with a FastAPI backend and React frontend.

## Highlights

- FastAPI + SQLModel + Alembic for the API and migrations
- PostgreSQL 15 and Redis 7
- JWT auth with email verification flows
- Celery background tasks via Redis
- Docker Compose for dev and prod
- Sentry error monitoring and Prometheus metrics hooks
- GitHub Actions CI/CD pipeline

## Architecture

**Backend:** FastAPI, SQLModel, Alembic, JWT auth
**Frontend:** React 18, Vite 6, Tailwind CSS 4
**Data/Infra:** PostgreSQL 15, Redis 7
**Background tasks:** Celery worker + Redis broker

## Repository Layout

- backend/ : API, models, services, tasks
- frontend/ : React app
- docker-compose.yml : local dev stack
- docker-compose.prod.yml : production stack
- scripts/ : backup, restore, ops utilities
- docs/ops/ : runbooks and release evidence
- secrets/ : Docker secrets files (gitignored)

## Local Development

1) Create backend/.env (required for SECRET_KEY).

```bash
cp .env.example backend/.env
```

2) Start the dev stack.

```bash
docker compose up -d --build
```

3) Run migrations.

```bash
docker compose exec backend alembic upgrade head
```

4) (Optional) Run the frontend dev server.

```bash
cd frontend
npm install
npm run dev
```

### Local endpoints

- Frontend (dev server): http://localhost:5173
- Backend API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Production Deployment

### Prerequisites

- Docker Engine with Compose v2
- DNS + TLS termination in front of containers
- Container registry access (GHCR, ECR, Docker Hub, etc.)

### 1) Prepare production env

- Copy .env.prod.example to .env.prod
- Set non-secret values in .env.prod
- Place secret values in files under secrets/ (see secrets/README.md)

Required secret files:

- secrets/postgres_password.txt
- secrets/secret_key.txt
- secrets/smtp_password.txt
- secrets/sentry_dsn.txt
- secrets/razorpay_key_id.txt
- secrets/razorpay_key_secret.txt

### 2) Start production stack

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T backend alembic upgrade head
```

### 3) Runtime endpoints (default ports)

- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health: http://localhost:8000/health

## CI/CD

GitHub Actions workflow builds, tests, and publishes container images. Deploy steps run on main and require environment secrets.

## Backups and Restore

Run backups and restores via scripts (schedule externally via cron/CI):

```powershell
# Backup (default 30-day retention)
powershell -ExecutionPolicy Bypass -File ./scripts/backup_db.ps1 -EnvFilePath ./.env.prod

# Restore from a specific backup file
powershell -ExecutionPolicy Bypass -File ./scripts/restore_db.ps1 -BackupFile ./backups/womanly_YYYYMMDD_HHMMSS.sqlc -EnvFilePath ./.env.prod
```

Linux hosts:

```bash
bash ./scripts/backup_db.sh ./.env.prod ./backups 30
```

See docs/ops/backup-runbook.md for operational details.

## Seed Data

```bash
python backend/scripts/seed.py
```

## Notes

- Verification links use hash routes: #/auth/verify?token=...
- Use a verified sender domain for production email deliverability.

## License

MIT License
