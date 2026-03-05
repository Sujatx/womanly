from typing import List, Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator

class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: Optional[int] = Field(default=None, foreign_key="order.id")
    product_id: int
    quantity: int = Field(
        gt=0,  # Must be > 0
        description="Item quantity"
    )
    price_at_purchase: float = Field(
        gt=0,  # Must be > 0
        le=1000000,  # Maximum price
        description="Price at time of purchase"
    )
    
    order: Optional["Order"] = Relationship(back_populates="items")

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    status: str = Field(
        default="pending",
        description="Order status: pending, paid, processing, shipped, delivered, cancelled"
    )
    total_amount: float = Field(
        gt=0,  # Must be > 0
        le=10000000,  # Maximum order total
        description="Total order amount"
    )
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Order financials
    shipping_cost: float = Field(default=0.0, ge=0, description="Shipping cost")
    tax_amount: float = Field(default=0.0, ge=0, description="Tax collected")
    discount_amount: float = Field(default=0.0, ge=0, description="Coupon/discount applied")

    # Shipping tracking
    shipping_provider: Optional[str] = Field(default=None, description="e.g. 'dhl', 'fedex', 'local'")
    tracking_number: Optional[str] = Field(default=None)
    
    # Timestamps for tracking order lifecycle
    paid_at: Optional[datetime] = None
    processing_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    
    # Soft delete support (for GDPR compliance)
    deleted_at: Optional[datetime] = Field(default=None, index=True)
    
    items: List[OrderItem] = Relationship(back_populates="order")
    
    def soft_delete(self):
        """Mark order as deleted (soft delete) for compliance."""
        self.deleted_at = datetime.now(timezone.utc)
    
    def is_deleted(self) -> bool:
        """Check if order is soft deleted."""
        return self.deleted_at is not None
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        """Validate order status is one of allowed values."""
        allowed_statuses = {'pending', 'paid', 'processing', 'shipped', 'delivered', 'cancelled'}
        if v not in allowed_statuses:
            raise ValueError(f'status must be one of {allowed_statuses}')
        return v
    
    def update_status(self, new_status: str, updated_by: Optional[int] = None, notes: Optional[str] = None, session=None):
        """
        Update order status with state machine validation.
        
        Args:
            new_status: New status to transition to
            updated_by: User ID making the change
            notes: Optional notes about the transition
            
        Raises:
            InvalidOrderTransitionException: If transition is not allowed
        """
        from app.core.order_state_machine import validate_transition, OrderTransition
        from app.core.logging import get_structured_logger
        
        logger = get_structured_logger(__name__)
        
        # Validate transition
        validate_transition(self.status, new_status, self.id)
        
        # Log the transition
        transition = OrderTransition(
            order_id=self.id,
            from_status=self.status,
            to_status=new_status,
            updated_by=updated_by,
            notes=notes
        )
        
        logger.info(
            "Order status transition",
            **transition.to_dict()
        )
        
        # Update status
        old_status = self.status
        self.status = new_status

        # Write OrderStatusHistory record if session provided
        if session is not None:
            from app.models.refund import OrderStatusHistory
            history = OrderStatusHistory(
                order_id=self.id,
                from_status=old_status,
                to_status=new_status,
                updated_by=updated_by,
                notes=notes,
            )
            session.add(history)

        # Update lifecycle timestamps
        now = datetime.now(timezone.utc)
        if new_status == "paid":
            self.paid_at = now
        elif new_status == "processing":
            self.processing_at = now
        elif new_status == "shipped":
            self.shipped_at = now
        elif new_status == "delivered":
            self.delivered_at = now
        elif new_status == "cancelled":
            self.cancelled_at = now

