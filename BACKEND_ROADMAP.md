# Womanly Backend Implementation Roadmap

This document outlines the step-by-step plan to migrate Womanly from a frontend-only mock application to a full-stack e-commerce platform.

## Phase 1: Infrastructure & Boilerplate ✅
**Goal:** Get the backend running in Docker with a database connection.
- [x] Create `backend/` directory structure.
- [x] Create `backend/Dockerfile` and `backend/requirements.txt`.
- [x] Create `docker-compose.yml` (FastAPI + PostgreSQL).
- [x] Initialize FastAPI app in `backend/app/main.py`.
- [x] Configure environment variables (`.env`, `backend/app/config.py`).
- [x] Verify container orchestration (`docker-compose up` works).
- [x] Fixed `ImportError` for `UserCreate` and `UserRead` in models.
- [x] Resolved OpenAPI schema generation error.

**Status:** ✅ **COMPLETED** - Backend running at `http://localhost:8000`, API docs at `/docs`

## Phase 2: Database Setup & Products (The "Read" Layer) ✅
**Goal:** Replace DummyJSON product fetching with our own database.
- [x] Set up SQLModel (ORM) and Alembic (Migrations).
- [x] Define `Product` and `Category` models in `backend/app/models/`.
- [x] Create initial migration and apply schema.
- [x] Database tables created: `user`, `product`, `category`, `cart`, `cartitem`, `order`, `orderitem`, `wishlist`, `wishlistitem`.
- [x] Implement Public APIs:
    - [x] `GET /products` (with pagination/filtering)
    - [x] `GET /products/{id}`
    - [x] `GET /categories`
- [x] Seeded database with 100 products from DummyJSON.

**Status:** ✅ **COMPLETED**

## Phase 3: Authentication (The "User" Layer) ✅
**Goal:** Allow users to register and log in.
- [x] Define `User` model.
- [x] Setup `passlib` for password hashing (bcrypt).
- [x] Setup `python-jose` for JWT generation/validation.
- [x] Implement Auth APIs:
    - [x] `POST /auth/signup`
    - [x] `POST /auth/login` (returns Access token)
    - [x] `GET /auth/me` (Protected route test)
- [x] Create `get_current_user` dependency for route protection.

**Status:** ✅ **COMPLETED**

## Phase 4: Cart & Wishlist (The "State" Layer) ✅
**Goal:** Move cart state from `localStorage` to PostgreSQL.
- [x] Define `Cart` and `CartItem` models.
- [x] Define `Wishlist` and `WishlistItem` models.
- [x] Implement Cart APIs:
    - [x] `GET /cart` (Get user's active cart)
    - [x] `POST /cart/items` (Add/Update item)
    - [x] `DELETE /cart/items/{id}`
- [ ] Implement "Merge" logic: When an anonymous user logs in, merge their session cart with their DB cart. *(Deferred)*

**Status:** ✅ **COMPLETED** (Server-side cart active)

## Phase 5: Orders & Payments (The "Transactional" Layer) ✅
**Goal:** Process real payments via Razorpay.
- [x] Define `Order` and `OrderItem` models (updated for Razorpay).
- [x] Set up Razorpay Python SDK.
- [x] Implement Checkout APIs:
    - [x] `POST /payments/create-order` (Creates Razorpay order)
    - [x] `POST /payments/verify` (Verifies Razorpay payment signature)

**Status:** ✅ **COMPLETED** (Razorpay integrated)

## Phase 6: Frontend Integration ✅
**Goal:** Connect the Next.js frontend to the new Backend APIs.
- [x] Create a `lib/api-client.ts` in Next.js to replace `lib/dummyjson.ts` calls.
- [x] Update `app/page.tsx` and product pages to use the new client.
- [x] Create a Sign Up / Login UI form at `/auth`.
- [x] Refactor `CartDrawer` to fetch from API instead of reading `localStorage`.
- [x] Integrate Razorpay checkout in `CheckoutButtons`.

**Status:** ✅ **COMPLETED**

## Phase 7: Deployment & Cleanup
- [x] Remove `lib/dummyjson.ts`.
- [ ] Configure `gunicorn` for production serving.
- [ ] Finalize `Dockerfile` for production (multi-stage build).
- [ ] Resolve frontend `ERR_CONNECTION_REFUSED` (Check if `npm run dev` is still running or blocked).
