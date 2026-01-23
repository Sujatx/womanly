# Womanly Backend API

FastAPI-based backend for the Womanly e-commerce platform.

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL 15
- **ORM:** SQLModel
- **Migrations:** Alembic
- **Authentication:** JWT (python-jose)
- **Password Hashing:** bcrypt (passlib)
- **Payments:** Stripe
- **Containerization:** Docker + docker-compose

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- `.env` file configured (see below)

### Running Locally

```bash
# From the project root
docker compose up --build
```

The API will be available at:
- **API:** http://localhost:8000
- **Interactive Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Environment Variables

Create a `.env` file in the project root:

```env
# Database
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=womanly

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Stripe (optional for development)
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=

# Environment
ENV_NAME=dev
```

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration and settings
│   ├── db.py                # Database connection
│   ├── deps.py              # Dependency injection
│   ├── api/                 # API route handlers
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── products.py      # Product endpoints
│   │   ├── cart.py          # Cart endpoints
│   │   └── payments.py      # Payment endpoints
│   ├── models/              # SQLModel database models
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── category.py
│   │   ├── cart.py
│   │   ├── order.py
│   │   └── wishlist.py
│   ├── security/            # Security utilities
│   │   ├── hashing.py       # Password hashing
│   │   └── token.py         # JWT token handling
│   └── services/            # Business logic
├── alembic/                 # Database migrations
│   ├── versions/            # Migration scripts
│   └── env.py               # Alembic configuration
├── scripts/                 # Utility scripts
├── Dockerfile               # Docker image definition
├── requirements.txt         # Python dependencies
└── alembic.ini              # Alembic configuration
```

## Database

### Migrations

The project uses Alembic for database migrations.

```bash
# Generate a new migration (inside container)
docker compose exec backend alembic revision --autogenerate -m "Description"

# Apply migrations
docker compose exec backend alembic upgrade head

# Rollback one migration
docker compose exec backend alembic downgrade -1
```

### Database Schema

Current tables:
- `user` - User accounts
- `product` - Product catalog
- `category` - Product categories
- `cart` - User shopping carts
- `cartitem` - Items in carts
- `order` - Completed orders
- `orderitem` - Items in orders
- `wishlist` - User wishlists
- `wishlistitem` - Items in wishlists

### Accessing the Database

```bash
# Connect to PostgreSQL
docker compose exec db psql -U user -d womanly

# List tables
\dt

# Describe a table
\d user

# Exit
\q
```

## API Endpoints

### Authentication
- `POST /auth/signup` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user info (protected)

### Products
- `GET /products` - List products (with pagination)
- `GET /products/{id}` - Get product details
- `GET /categories` - List categories

### Cart
- `GET /cart` - Get user's cart (protected)
- `POST /cart/items` - Add item to cart (protected)
- `DELETE /cart/items/{id}` - Remove item from cart (protected)

### Payments
- `POST /payments/create-intent` - Create Stripe payment intent (protected)
- `POST /webhooks/stripe` - Stripe webhook handler

## Development

### Running Commands in Container

```bash
# Access backend container shell
docker compose exec backend bash

# Run Python shell with app context
docker compose exec backend python

# View logs
docker compose logs backend -f
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Document functions with docstrings

## Deployment

### Production Considerations

1. **Security:**
   - Use strong `SECRET_KEY`
   - Enable HTTPS only
   - Configure CORS properly
   - Set up rate limiting

2. **Database:**
   - Use managed PostgreSQL service
   - Enable connection pooling
   - Set up regular backups

3. **Server:**
   - Use Gunicorn with Uvicorn workers
   - Configure proper logging
   - Set up monitoring and alerts

### Docker Production Build

```bash
# Build production image
docker build -t womanly-backend:latest .

# Run with production settings
docker run -p 8000:8000 --env-file .env.production womanly-backend:latest
```

## Current Status

✅ **Completed:**
- Backend skeleton with Docker setup
- Database schema and migrations
- User authentication (JWT)
- Cart and wishlist models
- Payment integration structure

🚧 **In Progress:**
- Product data seeding
- Product API implementation
- Frontend integration

📋 **Planned:**
- Google OAuth integration
- Order processing
- Email notifications
- Admin dashboard

## Contributing

See the main project README and `BACKEND_ROADMAP.md` for development guidelines.

## License

MIT - See LICENSE file for details.
