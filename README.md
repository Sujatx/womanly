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

## Production Deployment

### Prerequisites

- Docker and Docker Compose
- PostgreSQL and Redis endpoints
- Resend API key and verified sender domain
- Sentry project DSN

### Container Start

```bash
# create .env from template and set real secrets first
# cp .env.example .env

docker compose up --build -d
docker compose exec backend alembic upgrade head
```

### Runtime Endpoints

- Frontend: `https://yourdomain.com`
- Backend API: `https://api.yourdomain.com`
- Swagger: `https://api.yourdomain.com/docs`
- ReDoc: `https://api.yourdomain.com/redoc`

## Production Configuration

Create `backend/.env` with production values:

```env
# Core
ENV_NAME=prod
POSTGRES_USER=replace_me
POSTGRES_PASSWORD=replace_me
POSTGRES_DB=womanly
DATABASE_URL=postgresql://replace_me:replace_me@db-host:5432/womanly
READ_DATABASE_URL=postgresql://replace_me:replace_me@read-replica-host:5432/womanly
REDIS_URL=redis://redis-host:6379/0

# Auth/Security
SECRET_KEY=replace_with_32_plus_random_chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Frontend URL used in email verification links
FRONTEND_URL=https://yourdomain.com

# SMTP (Resend)
SMTP_HOST=smtp.resend.com
SMTP_PORT=587
SMTP_USER=resend
SMTP_PASSWORD=re_replace_with_resend_api_key
SMTP_FROM=noreply@yourdomain.com

# Monitoring
SENTRY_DSN=https://replace_me.ingest.sentry.io/replace_me
SENTRY_ENVIRONMENT=prod
SENTRY_TRACES_SAMPLE_RATE=0.1

# Optional payments
RAZORPAY_KEY_ID=replace_me
RAZORPAY_KEY_SECRET=replace_me
```

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
