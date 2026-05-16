"""
Order management endpoints: cancellation, refunds, status history, delivery tracking webhooks.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Path, status
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from app.db import get_session
from app.di_container import get as di_get
from pydantic import BaseModel
from typing import List, Dict
from app.deps import get_current_user
from app.models import Order, OrderItem, User, RefundRequest, ShippingUpdate, OrderStatusHistoryRead
from app.models.product import ProductVariant
from app.models.refund import Refund, OrderStatusHistory
from app.models.inventory import refund_stock_for_order
from app.core.exceptions import OrderNotFoundException
from app.core.exceptions import ExternalServiceException
from app.core.logging import get_structured_logger
from app.services.razorpay_service import create_razorpay_refund
from app.services import send_shipping_notification

router = APIRouter()
logger = get_structured_logger(__name__)

LOW_REFUND_RATE_THRESHOLD = 0.05  # Alert if >5% of orders refunded


# ─────────────────────────── Helpers ───────────────────────────

def _get_order_or_404(session: Session, order_id: int, user_id: int) -> Order:
    """Fetch a non-deleted order belonging to the current user."""
    order_repo = di_get("order_repo")
    # Use repository to fetch by id then validate ownership and soft-delete
    order = order_repo.get_by_id(session, order_id)
    if not order or getattr(order, "deleted_at", None) is not None or order.user_id != user_id:
        raise OrderNotFoundException(order_id)
    # Ensure items are loaded similarly to previous behavior
    # Fallback: if not preloaded, access .items to trigger lazy load
    _ = getattr(order, "items", None)
    return order


def _restore_inventory(session: Session, order: Order, user_id: int) -> None:
    """Restore stock for every item in the order."""
    for item in order.items:
        # Prefer direct lookup first for legacy rows that may already carry a variant-like id.
        variant = session.get(ProductVariant, item.product_id)

        # OrderItem currently stores product_id, not variant_id.
        # Fall back to the first variant for this product so stock is still restored.
        if not variant:
            product_repo = di_get("product_repo")
            variant = product_repo.get_first_variant_for_product(session, item.product_id)

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
        except ExternalServiceException:
            raise
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

    # Transition order state (writes OrderStatusHistory) via repository
    order = di_get("order_repo").update_status(
        session=session,
        order_id=order.id,
        new_status="cancelled",
        reason="Cancelled by customer",
    )
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
    existing_refund = di_get("order_repo").has_pending_refund(session, order_id)
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
        except ExternalServiceException:
            raise
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
        # Use repository to update status
        di_get("order_repo").update_status(
            session=session,
            order_id=order.id,
            new_status="cancelled",
            reason=f"Refunded: {body.reason}",
        )

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

    history = di_get("order_repo").get_order_history(session, order_id)

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
    order = di_get("order_repo").get_by_tracking_number(session, provider, body.tracking_number)

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


class OrderStatusUpdateItem(BaseModel):
    id: int
    new_status: str


@router.post("/batch", status_code=status.HTTP_200_OK)
def batch_update_order_status(
    items: List[OrderStatusUpdateItem],
    session: Session = Depends(get_session),
):
    """Batch update order statuses in a single transaction.

    Each item must include `id` and `new_status`.
    """
    order_repo = di_get("order_repo")
    results = []
    try:
        with session.begin():
            for it in items:
                order = order_repo.update_status(session=session, order_id=it.id, new_status=it.new_status)
                results.append({"id": it.id, "status": order.status})
            # commit
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Batch update failed: {str(e)}")

    return {"updated": results}
