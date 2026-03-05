# Womanly E-commerce Platform

Modern e-commerce platform with FastAPI backend and React frontend.

## Tech Stack

**Backend:**
- FastAPI 0.115+ with async/await
- PostgreSQL 15 with SQLModel ORM
- Alembic database migrations
- JWT Authentication (HS256, Argon2 hashing)
- Email verification & SMTP (Mailtrap)
- CORS & CSRF middleware
- Razorpay Payment Gateway

**Frontend:**
- React 18 with TypeScript
- Vite 6 build tool
- Tailwind CSS 4 with custom theme
- Framer Motion animations
- Hash-based routing (#/)
- TailwindCSS UI components

**Features:**
- User authentication (signup/login/logout)
- Email verification with token expiry
- Product catalog with search & filtering
- Shopping cart (client-side)
- Wishlist functionality
- User profile management
- Order management system
- Responsive mobile-friendly UI

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 15 (or use Docker)

### Local Development

**Backend:**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Database Setup:**
```bash
cd backend
alembic upgrade head  # Run migrations
python scripts/seed.py  # Seed sample data
```

### Docker Deployment

```bash
docker compose up --build -d
docker-compose exec backend alembic upgrade head
docker-compose exec backend python scripts/seed.py
```

### Access Points
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs
- **API Docs (ReDoc):** http://localhost:8000/redoc

## Configuration

### Backend Environment Variables

Create `backend/.env` file:

```env
# Database
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=womanly
DATABASE_URL=postgresql://user:password@db:5432/womanly

# Security
SECRET_KEY=your_secure_32_character_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Configuration (Mailtrap)
SMTP_HOST=sandbox.smtp.mailtrap.io
SMTP_PORT=2525
SMTP_USER=your_mailtrap_username
SMTP_PASSWORD=your_mailtrap_password
SMTP_FROM=noreply@womanly.com

# Payment Gateway (Optional)
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_secret_key

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### API Authentication

The API uses JWT Bearer tokens for authentication:

```bash
# Signup
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email":"user@example.com",
    "password":"securepassword",
    "full_name":"User Name"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email":"user@example.com",
    "password":"securepassword"
  }'

# Use returned access_token in subsequent requests
curl -X GET http://localhost:8000/api/v1/products \
  -H "Authorization: Bearer <your_access_token>"
```

## License

MIT License
