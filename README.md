# Womanly - Full Stack E-commerce Platform

A modern, high-performance e-commerce application built with Next.js 15 and FastAPI.

## Features
- 🛍️ **Full E-commerce Flow:** Browse, Add to Cart, Wishlist, Checkout.
- 🔐 **Authentication:** Secure Signup/Login with JWT & Argon2 hashing.
- 💳 **Payments:** Integrated Razorpay checkout with backend verification.
- 🛒 **Smart Cart:** Hybrid local/server-side cart management.
- 🎨 **Modern UI:** Minimalist aesthetic with glassmorphism, toast notifications, and smooth animations.
- 📦 **Order History:** Track past purchases.

## Quick Start

### Prerequisites
- Docker Desktop
- Node.js (v18+)
- Python 3.12 (optional, for local script execution)

### 1. Start the Backend (Docker)
The backend and database run in Docker containers.
```bash
docker compose up --build -d
```
*   **API:** `http://localhost:8000`
*   **Docs:** `http://localhost:8000/docs`

### 2. Start the Frontend
```bash
cd frontend
npm install
npm run dev
```
*   **App:** `http://localhost:3000`

## Configuration
Create a `.env` file in the root for backend secrets (already set up for dev) and `frontend/.env.local` for frontend public keys.

**Root `.env` (Backend):**
```env
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=womanly
SECRET_KEY=your_secret_key
RAZORPAY_KEY_ID=your_test_key_id
RAZORPAY_KEY_SECRET=your_test_key_secret
```

**`frontend/.env.local`:**
```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_RAZORPAY_KEY_ID=your_test_key_id
```

## Architecture
*   **Frontend:** Next.js 15, TypeScript, Lucide React, Sonner.
*   **Backend:** FastAPI, SQLModel, PostgreSQL, Alembic.
*   **Infrastructure:** Docker Compose.
