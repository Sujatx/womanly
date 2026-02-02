# Womanly - Full-Stack Editorial E-commerce

A modern, high-performance e-commerce platform featuring a specialized FastAPI backend and a high-end React frontend built with Vite and Tailwind CSS 4.

## Features
- 🛍️ **Headless API:** FastAPI-powered backend with PostgreSQL and SQLModel.
- 🎨 **Editorial UI:** Vite/React frontend with a "VEXO" editorial aesthetic.
- 🔐 **Secure Auth:** JWT-based authentication with Argon2 hashing.
- 💳 **Payments:** Integrated Razorpay checkout with backend verification.
- 📦 **Order Management:** Full lifecycle tracking from pending to delivered.
- 🛒 **Interactive Cart:** Portal-based cart, search, and product detail modals.

## Quick Start

### 1. Start the Backend (Docker)
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
*   **App:** `http://localhost:5173`

## Configuration
Create a `.env` file in the root for backend secrets.

**Root `.env` (Backend):**
```env
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=womanly
SECRET_KEY=your_secret_key
RAZORPAY_KEY_ID=your_test_key_id
RAZORPAY_KEY_SECRET=your_test_key_secret

# SMTP Configuration
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your_username
SMTP_PASSWORD=your_password
SMTP_FROM=hello@womanly.com
```

## Architecture
- **Frontend:** React 18, Vite 6, Tailwind CSS 4, Radix UI.
- **Backend:** FastAPI, SQLModel, PostgreSQL.
- **Infrastructure:** Docker Compose.
