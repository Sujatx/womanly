"""Simple dependency injection container for app services and repositories.

Provides application-scoped singletons and factory helpers for testing.
"""
from typing import Dict
from app.repositories import (
    OrderRepository,
    ProductRepository,
    UserRepository,
    PaymentRepository,
)
from app.repositories.discount import DiscountRepository, BulkDiscountRepository, TierRepository
from app.repositories.address import AddressRepository
from app.repositories.shipping import ShippingRepository, TaxRepository
from app.repositories.wishlist import WishlistRepository
from app.repositories.cart import CartRepository
from app.repositories.category import CategoryRepository
from app.db import get_session

_container: Dict[str, object] = {}


def init_container():
    # Create repository singletons
    _container["order_repo"] = OrderRepository()
    _container["product_repo"] = ProductRepository()
    _container["user_repo"] = UserRepository()
    _container["payment_repo"] = PaymentRepository()
    _container["discount_repo"] = DiscountRepository()
    _container["bulk_discount_repo"] = BulkDiscountRepository()
    _container["tier_repo"] = TierRepository()
    _container["address_repo"] = AddressRepository()
    _container["shipping_repo"] = ShippingRepository()
    _container["tax_repo"] = TaxRepository()
    _container["wishlist_repo"] = WishlistRepository()
    _container["cart_repo"] = CartRepository()
    _container["category_repo"] = CategoryRepository()


def get(name: str):
    return _container.get(name)


def get_db_session():
    # Return a new session generator from app.db
    return next(get_session())


# Initialize on import for simplicity
try:
    init_container()
except Exception:
    # Defer initialization errors to runtime (testing environments may patch)
    pass
