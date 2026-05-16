"""
Discount models: Coupons, Bulk Discounts, Customer Tiers.
"""

from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field
from pydantic import field_validator


CUSTOMER_TIERS = {"regular", "silver", "gold"}
DISCOUNT_TYPES = {"percentage", "fixed"}


class Coupon(SQLModel, table=True):
    """
    Coupon code that provides a discount at checkout.
    
    discount_type='percentage': value is 0-100 (percent off)
    discount_type='fixed': value is a fixed currency amount off
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(unique=True, index=True, min_length=2, max_length=50)
    discount_type: str = Field(description="'percentage' or 'fixed'")
    value: float = Field(gt=0, description="Discount value (percent or fixed amount)")
    max_uses: Optional[int] = Field(default=None, ge=1, description="Total redemption limit")
    uses_per_user: int = Field(default=1, ge=1, description="Max uses per individual user")
    expiry_date: Optional[datetime] = Field(default=None)
    min_order_value: float = Field(default=0.0, ge=0, description="Minimum order to apply coupon")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("discount_type")
    @classmethod
    def validate_discount_type(cls, v):
        if v not in DISCOUNT_TYPES:
            raise ValueError(f"discount_type must be one of {DISCOUNT_TYPES}")
        return v

    @field_validator("value")
    @classmethod
    def validate_value(cls, v, info):
        data = info.data if hasattr(info, "data") else {}
        if data.get("discount_type") == "percentage" and v > 100:
            raise ValueError("Percentage discount cannot exceed 100")
        return v


class CouponUsage(SQLModel, table=True):
    """Records each time a coupon is redeemed."""

    id: Optional[int] = Field(default=None, primary_key=True)
    coupon_id: int = Field(foreign_key="coupon.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    order_id: int = Field(foreign_key="order.id", index=True)
    discount_amount: float = Field(ge=0)
    used_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BulkDiscount(SQLModel, table=True):
    """
    Quantity-based discount for a specific product.
    e.g. Buy 3+ of product_id=5, get 10% off.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id", index=True)
    min_quantity: int = Field(ge=2, description="Minimum quantity to trigger discount")
    discount_percent: float = Field(gt=0, le=100, description="Percent discount to apply")
    is_active: bool = Field(default=True)


class CustomerTier(SQLModel, table=True):
    """
    Customer loyalty tier with associated discount.
    Users are promoted based on their lifetime_value.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, description="'regular', 'silver', or 'gold'")
    min_ltv: float = Field(ge=0, description="Minimum lifetime value (LTV) to qualify for this tier")
    discount_percent: float = Field(ge=0, le=100, description="Order discount applied for this tier")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v not in CUSTOMER_TIERS:
            raise ValueError(f"Tier name must be one of {CUSTOMER_TIERS}")
        return v


class CouponValidateResponse(SQLModel):
    valid: bool
    discount_type: Optional[str] = None
    discount_amount: Optional[float] = None
    discount_value: Optional[float] = None
    message: str


class CouponCreate(SQLModel):
    code: str
    discount_type: str
    value: float
    max_uses: Optional[int] = None
    uses_per_user: int = 1
    expiry_date: Optional[datetime] = None
    min_order_value: float = 0.0
    is_active: bool = True


class BulkDiscountCreate(SQLModel):
    product_id: int
    min_quantity: int
    discount_percent: float
