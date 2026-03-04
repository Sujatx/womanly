# Womanly E-commerce Platform

Modern e-commerce platform with FastAPI backend and React frontend.

## Tech Stack

**Backend:**
- FastAPI 0.115+
- PostgreSQL 15
- SQLModel + Alembic
- Redis
- Razorpay Payment Gateway

**Frontend:**
- React 18
- Vite 6
- Tailwind CSS 4
- Radix UI

**Infrastructure:**
- Docker Compose
- JWT Authentication
- CSRF Protection

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+

### Run the Application

**Backend:**
```bash
docker compose up --build -d
docker-compose exec backend alembic upgrade head
docker-compose exec backend python scripts/seed.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Access
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Configuration

Create `.env` file in project root:

```env
# Database
DATABASE_URL=postgresql://user:password@db:5432/womanly

# Security
SECRET_KEY=your_secure_secret_key_here
REFRESH_TOKEN_SECRET=your_refresh_token_secret_here

# Services
RAZORPAY_KEY_ID=your_key_id
RAZORPAY_KEY_SECRET=your_key_secret
REDIS_URL=redis://redis:6379/0
```

## License

MIT License
