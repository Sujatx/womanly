"""
API v1 Router

This module combines all v1 API endpoints into a single router.
"""

from fastapi import APIRouter
from app.api import products, auth, cart, payments, addresses
from app.api import orders, wishlist, discounts, shipping, batch

# Create v1 router
v1_router = APIRouter(prefix="/api/v1")

# Include all API endpoint routers
v1_router.include_router(products.router, prefix="/products", tags=["v1-products"])
v1_router.include_router(auth.router, prefix="/auth", tags=["v1-auth"])
v1_router.include_router(cart.router, prefix="/cart", tags=["v1-cart"])
v1_router.include_router(payments.router, prefix="/payments", tags=["v1-payments"])
v1_router.include_router(addresses.router, prefix="/addresses", tags=["v1-addresses"])

# Phase 3 routers
v1_router.include_router(orders.router, prefix="/orders", tags=["v1-orders"])
v1_router.include_router(wishlist.router, prefix="/wishlist", tags=["v1-wishlist"])
v1_router.include_router(discounts.router, prefix="/discounts", tags=["v1-discounts"])
v1_router.include_router(shipping.router, tags=["v1-shipping"])

# Phase 4 performance routers
v1_router.include_router(batch.router, tags=["v1-batch"])
