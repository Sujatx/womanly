# Womanly E-commerce Platform

Modern e-commerce platform with FastAPI backend and React frontend.

## Tech Stack

**Backend:**
- FastAPI 0.115+ with async/await
- PostgreSQL 15 with SQLModel ORM
- Redis 7 for caching
- Alembic database migrations
- JWT auth with refresh/logout flows
- Resend SMTP for verification emails
- Sentry error monitoring

**Frontend:**
- React 18 + TypeScript
- Vite 6 + Tailwind CSS 4
- Hash-based routing (`#/...`)
- Lazy-loaded route/components
- PWA basics (service worker + manifest)

## Production Deployment (Phase 5 Baseline)

### Prerequisites

- Docker Engine with Compose v2
- Production DNS and TLS termination in front of containers
- Access to a container registry (Docker Hub, ECR, GHCR, etc.)

### 1) Prepare production env

- Copy .env.prod.example to .env.prod
- Set non-secret values in .env.prod
- Place secret values in files under secrets/

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
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### 3) Runtime endpoints (default ports)

- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Production artifacts added

- backend/Dockerfile.prod (multi-stage, health check, non-root)
- backend/docker/entrypoint.prod.sh (loads Docker secret files into env)
- frontend/Dockerfile.prod + frontend/nginx.prod.conf
- docker-compose.prod.yml (versioned image tags, secrets files, health checks)
- .github/workflows/ci-cd.yml (PR checks, image build, staging/prod deploy placeholders)
- scripts/backup_db.ps1 and scripts/restore_db.ps1

### Database backup and restore

```powershell
# Backup (keeps 30-day chain by default)
powershell -ExecutionPolicy Bypass -File ./scripts/backup_db.ps1 -EnvFilePath ./.env.prod

# Restore from a specific backup file
powershell -ExecutionPolicy Bypass -File ./scripts/restore_db.ps1 -BackupFile ./backups/womanly_YYYYMMDD_HHMMSS.sqlc -EnvFilePath ./.env.prod
```

Use task scheduler or CI cron to run backup_db.ps1 daily, then upload artifacts to encrypted object storage (S3/GCS/Azure Blob).

## API Auth Example

```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email":"user@example.com",
    "password":"securepassword",
    "full_name":"User Name"
  }'
```

## Notes

- Verification links use hash routes: `#/auth/verify?token=...`
- Use a verified sender domain in Resend for production deliverability.

## License

MIT License
