"""
Refund and Order Status History models.
"""

from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field


class Refund(SQLModel, table=True):
    """Tracks refunds issued for orders."""

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id", index=True)
    reason: str = Field(min_length=1, max_length=500, description="Reason for refund")
    amount: float = Field(gt=0, description="Amount refunded")
    status: str = Field(
        default="pending",
        description="Refund status: pending, processed, failed"
    )
    razorpay_refund_id: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processed_at: Optional[datetime] = Field(default=None)
    notes: Optional[str] = Field(default=None)


class OrderStatusHistory(SQLModel, table=True):
    """
    Immutable log of every order status transition.
    Written whenever Order.update_status() is called.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id", index=True)
    from_status: str
    to_status: str
    updated_by: Optional[int] = Field(default=None, foreign_key="user.id")
    notes: Optional[str] = Field(default=None)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
