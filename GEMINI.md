# GEMINI.md - Project Context

## Project Overview
**Womanly** is a modern e-commerce platform transitioning to a full-stack architecture. It consists of a **Next.js 15** frontend and a planned **FastAPI** backend (Python).

### Directory Structure
- `frontend/`: The Next.js client application (formerly the root).
- `backend/`: The FastAPI server.
- `BACKEND_ROADMAP.md`: The implementation plan for the backend.

### Current Status (Updated: 2026-01-26)
**Backend:** ✅ Running in Docker
- FastAPI server running at `http://localhost:8000`
- PostgreSQL database initialized and **seeded with 100 products**
- API documentation available at `http://localhost:8000/docs`
- Auth, Cart, and Razorpay Payments implemented

**Frontend:** ✅ Integrated with Backend
- Migrated from DummyJSON to internal FastAPI
- Auth flow (Signup/Login) working
- Persistent server-side cart
- Razorpay Checkout integrated

**Completed Milestones:**
1. ✅ Backend skeleton + Docker
2. ✅ Database schema + migrations + Seeding
3. ✅ Authentication system
4. ✅ Cart & Wishlist backend sync
5. ✅ Razorpay payment integration

**Next Steps:**
- Troubleshoot frontend connection issue (`localhost:3000`)
- Hardening & production deployment (Gunicorn)

## Frontend (Next.js)
Located in `frontend/`.

### Main Technologies
- **Framework:** Next.js 15 (App Router)
- **Language:** TypeScript
- **Styling:** CSS Modules & Global CSS
- **State Management:** Server-side via FastAPI (Cart synced to user)
- **Payments:** Razorpay Checkout SDK
- **Data Source:** FastAPI Backend (formerly DummyJSON)

### Key Files (Frontend)
- `frontend/app/layout.tsx`: Root shell.
- `frontend/lib/dummyjson.ts`: API client (to be replaced).
- `frontend/lib/cart.ts`: Client-side cart logic.
- `frontend/components/ProductCard.tsx`: Product display component.

### Building and Running (Frontend)
Run these commands from inside the `frontend/` directory:

| Action | Command |
| :--- | :--- |
| Install Dependencies | `npm install` |
| Development Server | `npm run dev` |
| Build for Production | `npm run build` |

---

# Womanly Backend — Finalized Plan

## 1. Architecture
*   **Type:** Monolithic REST API
*   **Trust model:** Backend is the single source of truth
*   **State:** Centralized in database
*   **Clients:** Next.js frontend only

## 2. Core Tech Stack (Locked)
### Backend
*   **Language:** Python 3.12
*   **Framework:** FastAPI
*   **Server:** Uvicorn (ASGI)
*   **API Style:** REST (JSON)

### Data
*   **Database:** PostgreSQL
*   **ORM:** SQLModel
*   **Migrations:** Alembic

### Auth
*   **Primary:** Email + password
*   **Tokens:** JWT (access + refresh)
*   **OAuth:** Google login (optional path, same JWT issued)

### Payments
*   **Provider:** Razorpay
*   **Flow:** Orders + Signature Verification
*   **Verification:** Backend-only (Signature)

### Infrastructure
*   **Containerization:** Docker
*   **Local orchestration:** docker-compose
*   **Secrets:** Environment variables only

## 3. Repository Layout
```
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── auth.py
│   │   ├── products.py
│   │   ├── cart.py
│   │   ├── orders.py
│   │   └── payments.py
│   ├── models/
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── stripe_service.py
│   │   └── order_service.py
│   └── security/
├── alembic/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env
```

## 4. Data Ownership Rules
*   Prices, stock, and totals are backend-controlled
*   Frontend is untrusted
*   Orders are immutable after payment
*   Payment confirmation requires Stripe webhook verification

## 5. Authentication Flow (Final)
### Local Login
1.  User submits email/password
2.  Backend verifies credentials
3.  Backend issues JWT (access + refresh)

### Google Login
1.  User authenticates with Google
2.  Backend verifies Google ID token
3.  Backend finds/creates user
4.  Backend issues JWT (same format)
*   All protected routes use JWT only.

## 6. E-commerce Flow (Final)
### Cart
*   Stored server-side
*   Synced to user account
*   localStorage used only for UI cache

### Order
1.  Backend validates cart
2.  Backend locks inventory
3.  Backend creates order (pending)

### Payment
1.  Backend creates Stripe PaymentIntent
2.  Frontend completes payment
3.  Stripe webhook confirms payment
4.  Backend marks order as paid

## 7. Docker Execution Model
### Containers
*   API container (FastAPI + Uvicorn)
*   PostgreSQL container (persistent volume)

### Local Run
*   `docker-compose up --build`

### Production
*   Same containers
*   HTTPS via reverse proxy

## 8. Deployment
*   **Frontend:** Vercel
*   **Backend:** VPS / Managed PaaS
*   **Database:** Managed PostgreSQL or containerized

## 9. Security Requirements
*   HTTPS only
*   Password hashing (bcrypt)
*   JWT secrets rotated via env vars
*   Stripe webhook signature verification
*   Rate limiting on auth routes

## 10. Milestones (Execution Order)
1.  Backend skeleton + Docker
2.  Database schema + migrations
3.  Product APIs (replace DummyJSON)
4.  Auth (local + Google)
5.  Cart & wishlist backend sync
6.  Orders
7.  Stripe payments
8.  Hardening & monitoring

## 11. Definition of Done
*   DummyJSON removed
*   Server-side cart and orders live
*   Stripe payments verified via webhook
*   Google + email login working
*   Dockerized backend deployable
