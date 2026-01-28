# GEMINI.md - Project Context

## Project Overview
**Womanly** is a modern full-stack e-commerce platform built with **Next.js 15** (Frontend) and **FastAPI** (Backend). It features a robust architecture with server-side state management, secure authentication, and real-time payments via Razorpay.

### Directory Structure
- `frontend/`: Next.js client application.
- `backend/`: FastAPI server, Dockerized with PostgreSQL.

### Current Status (Completed)
**Backend:** ✅ Running in Docker
- FastAPI server (`http://localhost:8000`)
- PostgreSQL database (seeded with 100 products)
- JWT Authentication (Signup/Login)
- Server-side Cart & Wishlist persistence
- Razorpay Payments (Order creation & verification)
- `/orders/me` endpoint for order history

**Frontend:** ✅ Complete
- Professional Minimal UI (Lucide Icons, Sonner Toasts)
- Centralized `AuthContext` (Single source of truth)
- Continuous Signup/Login Flow
- Dedicated `WishlistDrawer` & `CartDrawer`
- Full Checkout Flow with Razorpay integration
- Order History page (`/account/orders`)

## Tech Stack
### Frontend
- **Framework:** Next.js 15 (App Router)
- **Language:** TypeScript
- **Styling:** CSS Modules & Global CSS (Glassmorphism effects)
- **State Management:** React Context (Auth) + Custom Hooks (Cart/Wishlist)
- **UI Libraries:** Lucide React (Icons), Sonner (Toasts)

### Backend
- **Framework:** FastAPI (Python 3.12)
- **Database:** PostgreSQL 15
- **ORM:** SQLModel (SQLAlchemy + Pydantic)
- **Migrations:** Alembic
- **Auth:** OAuth2 with Password (Bearer JWT), Argon2 hashing
- **Payments:** Razorpay

## Key Workflows
### Authentication
1. User signs up -> Backend creates user & returns JWT -> Frontend authenticates immediately.
2. User logs in -> Backend validates & returns JWT -> Frontend stores token & syncs state.

### Cart Logic
- **Guest:** LocalStorage-based cart.
- **Logged In:** Server-side cart (PostgreSQL).
- **Sync:** Frontend automatically switches to API calls when authenticated.

### Payment Flow
1. User clicks "Pay with Razorpay" -> Frontend calls `createPaymentOrder`.
2. Backend creates pending Order & Razorpay Order.
3. Razorpay Checkout modal opens.
4. On success -> Frontend calls `verifyPayment`.
5. Backend verifies signature -> Marks Order as "Paid" -> Clears Cart.

## Running the Project
1. **Start Backend (Docker):**
   ```bash
   docker compose up --build -d
   ```
2. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```
3. **Access:**
   - Frontend: `http://localhost:3000`
   - API Docs: `http://localhost:8000/docs`