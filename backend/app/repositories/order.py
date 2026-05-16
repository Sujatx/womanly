"""Order repository for data access operations."""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from sqlmodel import select
from app.models import Order
from app.models.refund import Refund, OrderStatusHistory
from app.repositories.base import BaseRepository, PaginationParams, SortParams
from app.core.logging import get_structured_logger
from app.core.exceptions import AppException

logger = get_structured_logger(__name__)

# Valid order statuses
ORDER_STATUSES = ["pending", "paid", "processing", "shipped", "delivered", "cancelled", "refund_initiated", "refund_completed", "refund_failed"]


class OrderRepository(BaseRepository[Order]):
    """Repository for Order entity operations."""
    
    def __init__(self):
        super().__init__(Order)
    
    def get_orders_by_user(
        self,
        session: Session,
        user_id: int,
        pagination: Optional[PaginationParams] = None,
        sort: Optional[SortParams] = None,
    ) -> Tuple[List[Order], int]:
        """Get all orders for a user with pagination."""
        return self.find(
            session,
            filters={"user_id": user_id},
            sort=sort or SortParams("created_at", "desc"),
            pagination=pagination,
        )
    
    def get_orders_by_status(
        self,
        session: Session,
        status: str,
        pagination: Optional[PaginationParams] = None,
    ) -> Tuple[List[Order], int]:
        """Get orders by status."""
        query = select(Order).where(Order.status == status)
        
        # Count total
        total_count = len(session.exec(select(Order).where(Order.status == status)).all())
        
        # Apply pagination
        if pagination:
            query = query.offset(pagination.offset).limit(pagination.page_size)
        
        return session.exec(query).all(), total_count
    
    def get_orders_created_after(
        self,
        session: Session,
        created_after: datetime,
        pagination: Optional[PaginationParams] = None,
    ) -> Tuple[List[Order], int]:
        """Get orders created after a specific date."""
        query = select(Order).where(Order.created_at >= created_after)
        
        total_count = len(
            session.exec(select(Order).where(Order.created_at >= created_after)).all()
        )
        
        if pagination:
            query = query.offset(pagination.offset).limit(pagination.page_size)
        
        return session.exec(query).all(), total_count
    
    def update_status(
        self,
        session: Session,
        order_id: int,
        new_status: str,
        reason: Optional[str] = None,
    ) -> Order:
        """Update order status with reason tracking."""
        order = self.get_by_id_or_raise(session, order_id)
        
        # Validate status is valid
        if new_status not in ORDER_STATUSES:
            raise AppException(
                code="E-ORDER-003",
                message=f"Invalid order status: {new_status}",
                status_code=400,
            )
        
        # Validate status transition
        if not self._is_valid_transition(order.status, new_status):
            raise AppException(
                code="E-ORDER-003",
                message=f"Invalid order state transition from {order.status} to {new_status}",
                status_code=400,
            )
        
        order.status = new_status
        
        if reason:
            logger.info(
                f"Order status changed",
                order_id=order_id,
                old_status=order.status,
                new_status=new_status,
                reason=reason,
            )
        
        session.flush()
        return order
    
    def get_orders_needing_fulfillment(
        self,
        session: Session,
        pagination: Optional[PaginationParams] = None,
    ) -> Tuple[List[Order], int]:
        """Get confirmed/paid orders that need fulfillment."""
        return self.get_orders_by_status(
            session,
            status="paid",
            pagination=pagination,
        )

    def get_by_razorpay_order_id(self, session: Session, rzp_order_id: str) -> Optional[Order]:
        """Fetch an order by its Razorpay order id."""
        return session.exec(select(Order).where(Order.razorpay_order_id == rzp_order_id)).first()

    def has_pending_refund(self, session: Session, order_id: int) -> bool:
        """Return True if there is a pending or processed refund for an order."""
        return session.exec(
            select(Refund).where(
                Refund.order_id == order_id,
                Refund.status.in_(["pending", "processed"]),
            )
        ).first() is not None

    def get_order_history(self, session: Session, order_id: int):
        """Return OrderStatusHistory rows for an order ordered by timestamp."""
        return session.exec(
            select(OrderStatusHistory).where(OrderStatusHistory.order_id == order_id).order_by(OrderStatusHistory.timestamp)
        ).all()

    def get_by_tracking_number(self, session: Session, provider: str, tracking_number: str) -> Optional[Order]:
        """Find an order by tracking number and provider."""
        return session.exec(
            select(Order).where(
                Order.tracking_number == tracking_number,
                Order.shipping_provider == provider,
                Order.deleted_at.is_(None),
            )
        ).first()
    
    def get_pending_refunds(
        self,
        session: Session,
        pagination: Optional[PaginationParams] = None,
    ) -> Tuple[List[Order], int]:
        """Get orders with pending refunds."""
        return self.get_orders_by_status(
            session,
            status="refund_initiated",
            pagination=pagination,
        )
    
    def get_user_order_count(self, session: Session, user_id: int) -> int:
        """Get total order count for a user."""
        return self.count(session, filters={"user_id": user_id})
    
    def get_user_total_spent(self, session: Session, user_id: int) -> float:
        """Calculate total amount spent by a user."""
        orders = session.exec(
            select(Order).where(
                and_(
                    Order.user_id == user_id,
                    Order.status != "cancelled",
                )
            )
        ).all()
        
        return sum(order.total_amount for order in orders if order.total_amount)
    
    @staticmethod
    def _is_valid_transition(current_status: str, new_status: str) -> bool:
        """
        Validate order status transitions.
        
        Allowed transitions:
        - pending -> paid
        - paid -> processing, cancelled, refund_initiated
        - processing -> shipped, cancelled, refund_initiated
        - shipped -> delivered, refund_initiated
        - delivered -> refund_initiated
        - refund_initiated -> refund_completed, refund_failed
        """
        valid_transitions = {
            "pending": ["paid", "cancelled"],
            "paid": ["processing", "cancelled", "refund_initiated"],
            "processing": ["shipped", "cancelled", "refund_initiated"],
            "shipped": ["delivered", "refund_initiated"],
            "delivered": ["refund_initiated"],
            "cancelled": [],
            "refund_initiated": ["refund_completed", "refund_failed"],
            "refund_completed": [],
            "refund_failed": [],
        }
        
        return new_status in valid_transitions.get(current_status, [])
