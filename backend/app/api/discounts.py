"""
Discount & coupon endpoints.
Coupon validation for customers + admin CRUD (accessible via existing /admin router if desired,
but provided here as a self-contained router mounted at /discounts).
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, SQLModel, func
from datetime import datetime, timezone

from app.db import get_session
from app.deps import get_current_user
from app.models import User
from app.models.discount import (
    Coupon,
    CouponUsage,
    BulkDiscount,
    CustomerTier,
    CouponValidateResponse,
    CouponCreate,
    BulkDiscountCreate,
)
from app.core.logging import get_structured_logger
from app.di_container import get as di_get

router = APIRouter()
logger = get_structured_logger(__name__)


# ─────────────────────────── Helpers ───────────────────────────

def calculate_coupon_discount(coupon: Coupon, order_total: float) -> float:
    """Compute the discount amount for a given coupon and order total."""
    if coupon.discount_type == "percentage":
        return round(order_total * coupon.value / 100, 2)
    else:  # fixed
        return min(coupon.value, order_total)


def validate_coupon_for_user(
    coupon: Coupon,
    user_id: int,
    order_total: float,
    session: Session
) -> tuple[bool, str]:
    """
    Returns (is_valid, message).
    Checks: active, not expired, min order, max uses, per-user limit.
    """
    if not coupon.is_active:
        return False, "This coupon is inactive."

    now = datetime.now(timezone.utc)
    if coupon.expiry_date and now > coupon.expiry_date:
        return False, "This coupon has expired."

    if order_total < coupon.min_order_value:
        return False, f"Minimum order of ₹{coupon.min_order_value:.2f} required to use this coupon."

    if coupon.max_uses is not None:
        discount_repo = di_get("discount_repo")
        total_uses = discount_repo.count_coupon_uses(session, coupon.id)
        if total_uses >= coupon.max_uses:
            return False, "This coupon has reached its maximum usage limit."

    discount_repo = di_get("discount_repo")
    user_uses = discount_repo.count_coupon_uses_by_user(session, coupon.id, user_id)
    if user_uses >= coupon.uses_per_user:
        return False, "You have already used this coupon the maximum number of times."

    return True, "Coupon is valid."


# ─────────────────────────── Endpoints ───────────────────────────

@router.get("/coupons/validate/{code}", response_model=CouponValidateResponse)
def validate_coupon(
    code: str,
    order_total: float = 0.0,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Validate a coupon code for the current user.
    Pass `order_total` as a query param to get the computed discount_amount.
    """
    coupon = di_get("discount_repo").get_by_code(session, code)
    if not coupon:
        return CouponValidateResponse(valid=False, message="Coupon code not found.")

    is_valid, message = validate_coupon_for_user(coupon, current_user.id, order_total, session)
    if not is_valid:
        return CouponValidateResponse(valid=False, message=message)

    discount_amount = calculate_coupon_discount(coupon, order_total) if order_total > 0 else None
    return CouponValidateResponse(
        valid=True,
        discount_type=coupon.discount_type,
        discount_amount=discount_amount,
        discount_value=coupon.value,
        message=message,
    )


@router.get("/coupons", response_model=List[Coupon])
def list_coupons(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Admin: list all coupons."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")
    return di_get("discount_repo").list_all(session)


@router.post("/coupons", response_model=Coupon, status_code=status.HTTP_201_CREATED)
def create_coupon(
    body: CouponCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Admin: create a new coupon."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")

    existing = di_get("discount_repo").get_by_code(session, body.code)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Coupon code already exists.")

    coupon = Coupon(**body.model_dump())
    coupon.code = coupon.code.upper()
    di_get("discount_repo").create_coupon(session, coupon)
    session.commit()
    session.refresh(coupon)
    logger.info("Coupon created", code=coupon.code, admin_id=current_user.id)
    return coupon


@router.delete("/coupons/{coupon_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_coupon(
    coupon_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Admin: deactivate (soft-delete) a coupon by setting is_active=False."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")
    coupon = session.get(Coupon, coupon_id)
    if not coupon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coupon not found.")
    coupon.is_active = False
    session.add(coupon)
    session.commit()


@router.get("/bulk-discounts", response_model=List[BulkDiscount])
def list_bulk_discounts(session: Session = Depends(get_session)):
    """Return all active bulk discounts (public — used by frontend cart logic)."""
    return di_get("bulk_discount_repo").list_active(session)


@router.post("/bulk-discounts", response_model=BulkDiscount, status_code=status.HTTP_201_CREATED)
def create_bulk_discount(
    body: BulkDiscountCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Admin: create a bulk quantity discount."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")
    discount = BulkDiscount(**body.model_dump())
    session.add(discount)
    session.commit()
    session.refresh(discount)
    return discount


@router.get("/tiers", response_model=List[CustomerTier])
def list_tiers(session: Session = Depends(get_session)):
    """Return all customer tiers (public)."""
    return di_get("tier_repo").list_all(session)


@router.post("/tiers", response_model=CustomerTier, status_code=status.HTTP_201_CREATED)
def create_tier(
    body: CustomerTier,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Admin: create or update a customer tier."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")
    session.add(body)
    session.commit()
    session.refresh(body)
    return body
