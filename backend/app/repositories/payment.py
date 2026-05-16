"""Payment repository for data access operations."""

from typing import Optional, Tuple, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlmodel import select
from app.models import Order  # Using Order as payment is tracked via Order
from app.repositories.base import BaseRepository, PaginationParams, SortParams
from app.core.logging import get_structured_logger

logger = get_structured_logger(__name__)

# Valid payment statuses
PAYMENT_STATUSES = ["pending", "success", "failed", "cancelled"]


class PaymentRepository:
    """Repository for payment operations (via Order model)."""
    
    def __init__(self):
        self.entity_type = Order
    
    def get_order_payments(
        self,
        session: Session,
        user_id: int,
        pagination: Optional[PaginationParams] = None,
        sort: Optional[SortParams] = None,
    ) -> Tuple[List[Order], int]:
        """Get all orders (with payment info) for a user."""
        query = select(Order).where(Order.user_id == user_id)
        
        if sort:
            if sort.sort_order == "desc":
                query = query.order_by(getattr(Order, sort.sort_by).desc())
            else:
                query = query.order_by(getattr(Order, sort.sort_by).asc())
        else:
            query = query.order_by(Order.created_at.desc())
        
        total_count = len(session.exec(select(Order).where(Order.user_id == user_id)).all())
        
        if pagination:
            query = query.offset(pagination.offset).limit(pagination.page_size)
        
        orders = session.exec(query).all()
        return orders, total_count
    
    def get_orders_by_razorpay_id(
        self,
        session: Session,
        razorpay_payment_id: str,
    ) -> Optional[Order]:
        """Get order by Razorpay payment ID."""
        return session.exec(
            select(Order).where(Order.razorpay_payment_id == razorpay_payment_id)
        ).first()
    
    def get_paid_orders(
        self,
        session: Session,
        pagination: Optional[PaginationParams] = None,
    ) -> Tuple[List[Order], int]:
        """Get orders with successful payment (status != pending, cancelled)."""
        query = select(Order).where(
            (Order.razorpay_payment_id.isnot(None)) |
            (Order.status.in_(["paid", "processing", "shipped", "delivered"]))
        )
        
        total_count = len(session.exec(query).all())
        
        if pagination:
            query = query.offset(pagination.offset).limit(pagination.page_size)
        
        orders = session.exec(query).all()
        return orders, total_count
    
    def get_failed_payments(
        self,
        session: Session,
        pagination: Optional[PaginationParams] = None,
    ) -> Tuple[List[Order], int]:
        """Get orders with failed/pending payments."""
        query = select(Order).where(Order.status == "pending")
        
        total_count = len(session.exec(query).all())
        
        if pagination:
            query = query.offset(pagination.offset).limit(pagination.page_size)
        
        orders = session.exec(query).all()
        return orders, total_count
    
    def get_revenue_by_date_range(
        self,
        session: Session,
        start_date: datetime,
        end_date: datetime,
    ) -> float:
        """Calculate total revenue in a date range (successful payments only)."""
        orders = session.exec(
            select(Order).where(
                (Order.created_at >= start_date) &
                (Order.created_at <= end_date) &
                (Order.status.in_(["paid", "processing", "shipped", "delivered"]))
            )
        ).all()
        
        return sum(order.total_amount for order in orders if order.total_amount)
    
    def get_payment_stats(self, session: Session) -> dict:
        """Get payment statistics."""
        all_orders = session.exec(select(Order)).all()
        
        stats = {
            "total_orders": len(all_orders),
            "total_revenue": sum(o.total_amount for o in all_orders if o.total_amount),
            "by_status": {},
        }
        
        # Count by status
        for status in ["pending", "paid", "processing", "shipped", "delivered", "cancelled"]:
            count = len([o for o in all_orders if o.status == status])
            stats["by_status"][status] = count
        
        return stats
