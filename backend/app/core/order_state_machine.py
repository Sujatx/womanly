"""
Order State Machine

Defines valid order status transitions and enforces business rules.

ORDER LIFECYCLE:
===============

pending → paid → processing → shipped → delivered
                    ↓
                cancelled

RULES:
- pending: Order created but payment not confirmed
- paid: Payment confirmed, stock reserved
- processing: Order is being prepared
- shipped: Order has been shipped to customer
- delivered: Order received by customer
- cancelled: Order was cancelled (only from pending or paid)

INVALID TRANSITIONS:
- Cannot go from delivered → any other state (final state)
- Cannot go from shipped → pending/paid
- Cannot cancel after processing has started
"""

from enum import Enum
from typing import Set, Dict, Optional
from datetime import datetime, timezone
from app.core.exceptions import InvalidOrderTransitionException
from app.core.logging import get_structured_logger

logger = get_structured_logger(__name__)


class OrderStatus(str, Enum):
    """Valid order statuses."""
    PENDING = "pending"
    PAID = "paid"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


# Define valid state transitions
VALID_TRANSITIONS: Dict[OrderStatus, Set[OrderStatus]] = {
    OrderStatus.PENDING: {
        OrderStatus.PAID,
        OrderStatus.CANCELLED
    },
    OrderStatus.PAID: {
        OrderStatus.PROCESSING,
        OrderStatus.CANCELLED
    },
    OrderStatus.PROCESSING: {
        OrderStatus.SHIPPED,
        # Note: Cannot cancel after processing starts
    },
    OrderStatus.SHIPPED: {
        OrderStatus.DELIVERED
    },
    OrderStatus.DELIVERED: set(),  # Final state - no transitions allowed
    OrderStatus.CANCELLED: set()   # Final state - no transitions allowed
}


def is_valid_transition(from_status: str, to_status: str) -> bool:
    """
    Check if a status transition is valid.
    
    Args:
        from_status: Current order status
        to_status: Desired new status
        
    Returns:
        True if transition is valid, False otherwise
    """
    try:
        from_enum = OrderStatus(from_status)
        to_enum = OrderStatus(to_status)
    except ValueError:
        return False
    
    return to_enum in VALID_TRANSITIONS.get(from_enum, set())


def validate_transition(from_status: str, to_status: str, order_id: Optional[int] = None) -> None:
    """
    Validate a status transition and raise exception if invalid.
    
    Args:
        from_status: Current order status
        to_status: Desired new status
        order_id: Order ID for logging
        
    Raises:
        InvalidOrderTransitionException: If transition is not allowed
    """
    if not is_valid_transition(from_status, to_status):
        logger.warning(
            "Invalid order status transition attempted",
            order_id=order_id,
            from_status=from_status,
            to_status=to_status
        )
        raise InvalidOrderTransitionException(from_status, to_status)


def get_allowed_transitions(current_status: str) -> Set[str]:
    """
    Get all allowed transitions from the current status.
    
    Args:
        current_status: Current order status
        
    Returns:
        Set of allowed next statuses
    """
    try:
        status_enum = OrderStatus(current_status)
        return {s.value for s in VALID_TRANSITIONS.get(status_enum, set())}
    except ValueError:
        return set()


def is_final_status(status: str) -> bool:
    """
    Check if a status is a final state (no further transitions).
    
    Args:
        status: Order status to check
        
    Returns:
        True if status is final (delivered or cancelled)
    """
    try:
        status_enum = OrderStatus(status)
        return len(VALID_TRANSITIONS.get(status_enum, set())) == 0
    except ValueError:
        return False


def can_cancel_order(current_status: str) -> bool:
    """
    Check if an order can be cancelled from the current status.
    
    Args:
        current_status: Current order status
        
    Returns:
        True if order can be cancelled
    """
    return OrderStatus.CANCELLED in get_allowed_transitions(current_status)


class OrderTransition:
    """
    Record of an order status transition.
    
    This should be stored in a separate OrderStatusHistory table for audit trail.
    """
    
    def __init__(
        self,
        order_id: int,
        from_status: str,
        to_status: str,
        updated_by: Optional[int] = None,
        notes: Optional[str] = None
    ):
        self.order_id = order_id
        self.from_status = from_status
        self.to_status = to_status
        self.timestamp = datetime.now(timezone.utc)
        self.updated_by = updated_by  # User ID who made the change
        self.notes = notes
    
    def to_dict(self):
        """Convert to dictionary for logging/storage."""
        return {
            "order_id": self.order_id,
            "from_status": self.from_status,
            "to_status": self.to_status,
            "timestamp": self.timestamp.isoformat(),
            "updated_by": self.updated_by,
            "notes": self.notes
        }
