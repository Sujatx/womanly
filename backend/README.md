# Womanly Backend API

FastAPI-based backend for the Womanly e-commerce platform.

## Features
*   **REST API:** Fully typed endpoints for Products, Cart, Orders, and Auth.
*   **Database:** PostgreSQL with SQLModel ORM.
*   **Auth:** OAuth2 compatible Token flow (JWT).
*   **Payments:** Razorpay integration.

## Local Development (Without Docker)
If you prefer running locally without Docker:

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run Server:**
    ```bash
    uvicorn app.main:app --reload
    ```
3.  **Database:** You will need a local PostgreSQL instance running and configured in `.env`.

## Seeding Data
To populate the database with dummy products:
```bash
# Ensure DB is running
python -m scripts.seed
```