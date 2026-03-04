"""
Inventory management models and utilities.

Tracks all inventory changes with full audit trail.
"""

from typing import Optional
from datetime import datetime, timezone
from enum import Enum
from sqlmodel import SQLModel, Field
from app.core.logging import get_structured_logger

logger = get_structured_logger(__name__)


class InventoryTransactionType(str, Enum):
    """Types of inventory transactions."""
    ORDER = "order"           # Stock deducted for order
    REFUND = "refund"         # Stock returned due to refund/cancellation
    ADJUSTMENT = "adjustment" # Manual stock adjustment (admin)
    RESTOCK = "restock"       # New stock added from supplier
    DAMAGED = "damaged"       # Stock marked as damaged/unusable


class InventoryTransaction(SQLModel, table=True):
    """
    Audit trail for all inventory changes.
    
    Every change to stock_quantity must create a corresponding transaction.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # What was changed
    product_id: int = Field(foreign_key="product.id", index=True)
    variant_id: int = Field(foreign_key="productvariant.id", index=True)
    
    # Type of transaction
    transaction_type: str = Field(
        description="Type: order, refund, adjustment, restock, damaged"
    )
    
    # Quantity change (positive for addition, negative for deduction)
    quantity_change: int = Field(
        description="Quantity change (positive = add, negative = subtract)"
    )
    
    # Balance after transaction
    quantity_after: int = Field(
        ge=0,
        description="Stock quantity after this transaction"
    )
    
    # Reference to related entity (order_id, refund_id, etc.)
    reference_type: Optional[str] = Field(
        default=None,
        description="Type of reference: order, refund, user"
    )
    reference_id: Optional[int] = Field(
        default=None,
        description="ID of the referenced entity"
    )
    
    # Who made the change
    user_id: Optional[int] = Field(
        default=None,
        foreign_key="user.id",
        description="User who initiated the transaction (for orders/refunds)"
    )
    admin_id: Optional[int] = Field(
        default=None,
        description="Admin who made manual adjustment"
    )
    
    # Metadata
    notes: Optional[str] = Field(
        default=None,
        description="Optional notes about the transaction"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        index=True
    )


def create_inventory_transaction(
    session,
    product_id: int,
    variant_id: int,
    transaction_type: InventoryTransactionType,
    quantity_change: int,
    quantity_after: int,
    reference_type: Optional[str] = None,
    reference_id: Optional[int] = None,
    user_id: Optional[int] = None,
    admin_id: Optional[int] = None,
    notes: Optional[str] = None
) -> InventoryTransaction:
    """
    Create an inventory transaction record.
    
    Args:
        session: Database session
        product_id: Product ID
        variant_id: Product variant ID
        transaction_type: Type of transaction
        quantity_change: Quantity change (positive or negative)
        quantity_after: Stock quantity after the transaction
        reference_type: Type of reference (order, refund, etc.)
        reference_id: ID of the referenced entity
        user_id: User who initiated the transaction
        admin_id: Admin who made manual adjustment
        notes: Optional notes
    
    Returns:
        Created InventoryTransaction
    """
    transaction = InventoryTransaction(
        product_id=product_id,
        variant_id=variant_id,
        transaction_type=transaction_type.value,
        quantity_change=quantity_change,
        quantity_after=quantity_after,
        reference_type=reference_type,
        reference_id=reference_id,
        user_id=user_id,
        admin_id=admin_id,
        notes=notes
    )
    
    session.add(transaction)
    
    logger.info(
        "Inventory transaction created",
        product_id=product_id,
        variant_id=variant_id,
        transaction_type=transaction_type.value,
        quantity_change=quantity_change,
        quantity_after=quantity_after,
        reference_type=reference_type,
        reference_id=reference_id
    )
    
    return transaction


def deduct_stock_for_order(
    session,
    variant,
    quantity: int,
    order_id: int,
    user_id: int
) -> None:
    """
    Deduct stock for an order and create transaction record.
    
    Args:
        session: Database session
        variant: ProductVariant instance
        quantity: Quantity to deduct
        order_id: Order ID
        user_id: User ID who placed the order
    """
    # Deduct stock
    variant.stock_quantity -= quantity
    quantity_after = variant.stock_quantity
    
    # Create transaction record
    create_inventory_transaction(
        session=session,
        product_id=variant.product_id,
        variant_id=variant.id,
        transaction_type=InventoryTransactionType.ORDER,
        quantity_change=-quantity,  # Negative for deduction
        quantity_after=quantity_after,
        reference_type="order",
        reference_id=order_id,
        user_id=user_id,
        notes=f"Stock deducted for order {order_id}"
    )


def refund_stock_for_order(
    session,
    variant,
    quantity: int,
    order_id: int,
    user_id: int
) -> None:
    """
    Return stock for a refunded/cancelled order.
    
    Args:
        session: Database session
        variant: ProductVariant instance
        quantity: Quantity to return
        order_id: Order ID
        user_id: User ID who placed the order
    """
    # Return stock
    variant.stock_quantity += quantity
    quantity_after = variant.stock_quantity
    
    # Create transaction record
    create_inventory_transaction(
        session=session,
        product_id=variant.product_id,
        variant_id=variant.id,
        transaction_type=InventoryTransactionType.REFUND,
        quantity_change=quantity,  # Positive for addition
        quantity_after=quantity_after,
        reference_type="order",
        reference_id=order_id,
        user_id=user_id,
        notes=f"Stock refunded for order {order_id}"
    )


def adjust_stock(
    session,
    variant,
    quantity_change: int,
    admin_id: int,
    notes: str
) -> None:
    """
    Manually adjust stock (admin only).
    
    Args:
        session: Database session
        variant: ProductVariant instance
        quantity_change: Quantity change (positive or negative)
        admin_id: Admin user ID
        notes: Reason for adjustment
    """
    # Adjust stock
    variant.stock_quantity += quantity_change
    quantity_after = variant.stock_quantity
    
    # Validate non-negative
    if quantity_after < 0:
        raise ValueError(f"Stock cannot be negative. Current: {variant.stock_quantity - quantity_change}, Change: {quantity_change}")
    
    # Create transaction record
    create_inventory_transaction(
        session=session,
        product_id=variant.product_id,
        variant_id=variant.id,
        transaction_type=InventoryTransactionType.ADJUSTMENT,
        quantity_change=quantity_change,
        quantity_after=quantity_after,
        admin_id=admin_id,
        notes=notes
    )
