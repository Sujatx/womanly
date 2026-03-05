"""
Stock Alert and Stock Reservation models.

StockReservation: temporary hold on inventory during checkout (released after 30 min if payment not completed).
StockAlert: created when a variant's stock falls below the threshold.
"""

from typing import Optional
from datetime import datetime, timezone, timedelta
from sqlmodel import SQLModel, Field

STOCK_ALERT_THRESHOLD = 20
RESERVATION_TTL_MINUTES = 30


class StockReservation(SQLModel, table=True):
    """
    Temporary reservation of stock during the checkout window.

    Reserved stock is subtracted from available_stock but NOT from stock_quantity.
    If payment is not confirmed within RESERVATION_TTL_MINUTES the reservation expires
    and reserved_quantity is decremented by a background cleanup task.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    variant_id: int = Field(foreign_key="productvariant.id", index=True)
    order_id: Optional[int] = Field(default=None, foreign_key="order.id", index=True)
    quantity: int = Field(gt=0)
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(minutes=RESERVATION_TTL_MINUTES)
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    released_at: Optional[datetime] = Field(default=None)

    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def is_active(self) -> bool:
        return self.released_at is None and not self.is_expired


class StockAlert(SQLModel, table=True):
    """
    Alert created when variant stock falls below STOCK_ALERT_THRESHOLD.
    Resolved when stock is restocked above the threshold.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    variant_id: int = Field(foreign_key="productvariant.id", index=True)
    product_id: int = Field(foreign_key="product.id", index=True)
    current_stock: int
    threshold: int = Field(default=STOCK_ALERT_THRESHOLD)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = Field(default=None)

    @property
    def is_resolved(self) -> bool:
        return self.resolved_at is not None
