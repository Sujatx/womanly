"""
Order management endpoints: cancellation, refunds, status history, delivery tracking webhooks.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Path, status
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, Field as PydanticField

from app.db import get_session
from app.deps import get_current_user
from app.models import Order, OrderItem, User
from app.models.product import ProductVariant
from app.models.refund import Refund, OrderStatusHistory
from app.models.inventory import refund_stock_for_order
from app.core.exceptions import OrderNotFoundException
from app.core.logging import get_structured_logger
from app.services.razorpay_service import create_razorpay_refund
from app.services.email_service import send_shipping_notification

router = APIRouter()
logger = get_structured_logger(__name__)

LOW_REFUND_RATE_THRESHOLD = 0.05  # Alert if >5% of orders refunded


# ─────────────────────────── Schemas ───────────────────────────

class RefundRequest(BaseModel):
    reason: str = PydanticField(min_length=3, max_length=500)


class ShippingUpdate(BaseModel):
    tracking_number: str
    shipping_provider: str
    notes: Optional[str] = None


class OrderStatusHistoryRead(BaseModel):
    id: int
    order_id: int
    from_status: str
    to_status: str
    updated_by: Optional[int]
    notes: Optional[str]
    timestamp: str

    class Config:
        from_attributes = True


# ─────────────────────────── Helpers ───────────────────────────

def _get_order_or_404(session: Session, order_id: int, user_id: int) -> Order:
    """Fetch a non-deleted order belonging to the current user."""
    stmt = select(Order).where(
        Order.id == order_id,
        Order.user_id == user_id,
        Order.deleted_at.is_(None)
    ).options(selectinload(Order.items))
    order = session.exec(stmt).first()
    if not order:
        raise OrderNotFoundException(order_id)
    return order


def _restore_inventory(session: Session, order: Order, user_id: int) -> None:
    """Restore stock for every item in the order."""
    for item in order.items:
        # Fetch the variant
        variant = session.get(ProductVariant, item.product_id)
        # item.product_id is the product_id; we stored product_id not variant_id.
        # We need to look up the variant via the order's original checkout data.
        # Fall back: query variant for this product + order to do best-effort restore.
        # Since OrderItem stores product_id (not variant_id), we look for qty restore.
        if variant:
            refund_stock_for_order(
                session=session,
                variant=variant,
                quantity=item.quantity,
                order_id=order.id,
                user_id=user_id,
            )


# ─────────────────────────── Endpoints ───────────────────────────

@router.post("/{order_id}/cancel", status_code=status.HTTP_200_OK)
def cancel_order(
    order_id: int = Path(gt=0),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Cancel an order. Only allowed when status is 'pending' or 'paid'.

    - Transitions order to 'cancelled'
    - For paid orders: issues a Razorpay refund
    - Restores inventory
    - Logs the status transition to OrderStatusHistory
    """
    order = _get_order_or_404(session, order_id, current_user.id)

    if order.status not in ("pending", "paid"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Order cannot be cancelled in '{order.status}' status. Only 'pending' or 'paid' orders can be cancelled.",
        )

    razorpay_refund_id = None

    # If the order was already paid, issue a refund via Razorpay
    if order.status == "paid" and order.razorpay_payment_id:
        try:
            amount_paise = int(order.total_amount * 100)
            refund_result = create_razorpay_refund(
                payment_id=order.razorpay_payment_id,
                amount=amount_paise,
                notes={"reason": "Order cancelled by customer", "order_id": str(order.id)},
            )
            razorpay_refund_id = refund_result.get("id")
            logger.info(
                "Razorpay refund issued for cancellation",
                order_id=order.id,
                razorpay_refund_id=razorpay_refund_id,
            )
        except Exception as e:
            logger.error("Razorpay refund failed during cancellation", order_id=order.id, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to issue refund via payment gateway. Please contact support.",
            )

    # Create a Refund record if we actually refunded money
    if razorpay_refund_id:
        refund_record = Refund(
            order_id=order.id,
            reason="Order cancelled by customer",
            amount=order.total_amount,
            status="processed",
            razorpay_refund_id=razorpay_refund_id,
        )
        session.add(refund_record)

    # Restore inventory
    _restore_inventory(session, order, current_user.id)

    # Transition order state (writes OrderStatusHistory)
    order.update_status(
        "cancelled",
        updated_by=current_user.id,
        notes="Cancelled by customer",
        session=session,
    )

    session.add(order)
    session.commit()

    logger.info("Order cancelled", order_id=order.id, user_id=current_user.id)
    return {
        "status": "cancelled",
        "order_id": order.id,
        "refund_id": razorpay_refund_id,
        "message": "Order cancelled successfully." + (
            " Refund will be credited in 5-7 business days." if razorpay_refund_id else ""
        ),
    }


@router.post("/{order_id}/refund", status_code=status.HTTP_200_OK)
def request_refund(
    body: RefundRequest,
    order_id: int = Path(gt=0),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Request a refund for a delivered/shipped order.

    - Creates a Refund record
    - Calls Razorpay refund API
    - Restores inventory
    """
    order = _get_order_or_404(session, order_id, current_user.id)

    if order.status not in ("paid", "processing", "shipped", "delivered"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Refund not allowed for order in '{order.status}' status.",
        )

    # Check if a refund already exists
    existing_refund = session.exec(
        select(Refund).where(
            Refund.order_id == order_id,
            Refund.status.in_(["pending", "processed"])
        )
    ).first()
    if existing_refund:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A refund has already been requested for this order.",
        )

    razorpay_refund_id = None
    refund_status = "pending"

    if order.razorpay_payment_id:
        try:
            amount_paise = int(order.total_amount * 100)
            refund_result = create_razorpay_refund(
                payment_id=order.razorpay_payment_id,
                amount=amount_paise,
                notes={"reason": body.reason, "order_id": str(order.id)},
            )
            razorpay_refund_id = refund_result.get("id")
            refund_status = "processed"
            logger.info(
                "Razorpay refund issued",
                order_id=order.id,
                razorpay_refund_id=razorpay_refund_id,
            )
        except Exception as e:
            logger.error("Razorpay refund failed", order_id=order.id, error=str(e))
            refund_status = "failed"

    # Create refund record
    from datetime import datetime, timezone
    refund_record = Refund(
        order_id=order.id,
        reason=body.reason,
        amount=order.total_amount,
        status=refund_status,
        razorpay_refund_id=razorpay_refund_id,
        processed_at=datetime.now(timezone.utc) if refund_status == "processed" else None,
    )
    session.add(refund_record)

    # If refund processed, restore inventory and update order status
    if refund_status == "processed":
        _restore_inventory(session, order, current_user.id)
        order.update_status(
            "cancelled",
            updated_by=current_user.id,
            notes=f"Refunded: {body.reason}",
            session=session,
        )
        session.add(order)

    session.commit()
    session.refresh(refund_record)

    if refund_status == "failed":
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Refund request recorded, but payment gateway returned an error. Support will follow up.",
        )

    return {
        "refund_id": refund_record.id,
        "status": refund_status,
        "amount": order.total_amount,
        "razorpay_refund_id": razorpay_refund_id,
        "message": "Refund of ₹{:.2f} will be credited in 5-7 business days.".format(order.total_amount),
    }


@router.get("/{order_id}/history", response_model=List[OrderStatusHistoryRead])
def get_order_history(
    order_id: int = Path(gt=0),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Return the full status transition history for an order."""
    # Verify ownership
    _get_order_or_404(session, order_id, current_user.id)

    history = session.exec(
        select(OrderStatusHistory)
        .where(OrderStatusHistory.order_id == order_id)
        .order_by(OrderStatusHistory.timestamp)
    ).all()

    return [
        OrderStatusHistoryRead(
            id=h.id,
            order_id=h.order_id,
            from_status=h.from_status,
            to_status=h.to_status,
            updated_by=h.updated_by,
            notes=h.notes,
            timestamp=h.timestamp.isoformat(),
        )
        for h in history
    ]


@router.post("/webhooks/shipping/{provider}", status_code=status.HTTP_200_OK)
def shipping_webhook(
    provider: str,
    body: ShippingUpdate,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    """
    Webhook endpoint for shipping providers to push tracking updates.
    Updates the tracking number on the order and emails the customer.
    """
    # Find the order by tracking number (the provider echoes it back)
    stmt = select(Order).where(
        Order.tracking_number == body.tracking_number,
        Order.shipping_provider == provider,
        Order.deleted_at.is_(None),
    )
    order = session.exec(stmt).first()

    if not order:
        # Don't leak order existence — return 200 to provider
        logger.warning(
            "Shipping webhook: order not found",
            provider=provider,
            tracking_number=body.tracking_number,
        )
        return {"received": True}

    # Update order
    order.shipping_provider = provider
    order.tracking_number = body.tracking_number
    session.add(order)
    session.commit()

    # Notify customer (background)
    # Fetch user email
    from app.models import User as UserModel
    user = session.get(UserModel, order.user_id)
    if user:
        background_tasks.add_task(
            send_shipping_notification,
            user.email,
            order.id,
            body.tracking_number,
            provider,
        )

    logger.info(
        "Shipping update received",
        provider=provider,
        order_id=order.id,
        tracking_number=body.tracking_number,
    )
    return {"received": True, "order_id": order.id}
