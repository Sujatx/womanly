"""
API v1 Router

This module combines all v1 API endpoints into a single router.
"""

from fastapi import APIRouter
from app.api import products, auth, cart, payments, addresses

# Create v1 router
v1_router = APIRouter(prefix="/api/v1")

# Include all API endpoint routers
v1_router.include_router(products.router, prefix="/products", tags=["v1-products"])
v1_router.include_router(auth.router, prefix="/auth", tags=["v1-auth"])
v1_router.include_router(cart.router, prefix="/cart", tags=["v1-cart"])
v1_router.include_router(payments.router, prefix="/payments", tags=["v1-payments"])
v1_router.include_router(addresses.router, prefix="/addresses", tags=["v1-addresses"])
