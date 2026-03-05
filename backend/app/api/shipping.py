"""
Shipping & Tax calculation endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, SQLModel

from app.db import get_session
from app.models.shipping import ShippingRate, Tax
from app.core.logging import get_structured_logger

router = APIRouter()
logger = get_structured_logger(__name__)


# ─────────────────────────── Schemas ───────────────────────────

class AddressInput(SQLModel):
    country: str
    state: Optional[str] = None
    postal_code: Optional[str] = None


class CartItemInput(SQLModel):
    product_id: int
    quantity: int
    category_slug: Optional[str] = None


class ShippingCalculateRequest(SQLModel):
    address: AddressInput
    items: List[CartItemInput]


class ShippingCalculateResponse(SQLModel):
    cost: float
    delivery_days: int
    provider: str = "standard"


class TaxCalculateRequest(SQLModel):
    address: AddressInput
    items: List[CartItemInput]
    subtotal: float


class TaxBreakdownItem(SQLModel):
    category: Optional[str]
    rate: float
    amount: float
    description: Optional[str]


class TaxCalculateResponse(SQLModel):
    tax_amount: float
    effective_rate: float
    breakdown: List[TaxBreakdownItem]


# ─────────────────────────── Helpers ───────────────────────────

def _find_shipping_rate(session: Session, country: str, state: Optional[str], postal_code: Optional[str]) -> Optional[ShippingRate]:
    """Find the best matching (most specific) active shipping rate."""
    # 1. Exact: country + state + postal prefix
    if postal_code and state:
        rate = session.exec(
            select(ShippingRate).where(
                ShippingRate.country == country.upper(),
                ShippingRate.state == state,
                ShippingRate.is_active == True,
            )
        ).all()
        # Filter by postal prefix
        for r in rate:
            if r.postal_code_pattern and postal_code.startswith(r.postal_code_pattern):
                return r

    # 2. Country + state
    if state:
        rate = session.exec(
            select(ShippingRate).where(
                ShippingRate.country == country.upper(),
                ShippingRate.state == state,
                ShippingRate.postal_code_pattern.is_(None),
                ShippingRate.is_active == True,
            )
        ).first()
        if rate:
            return rate

    # 3. Country only
    rate = session.exec(
        select(ShippingRate).where(
            ShippingRate.country == country.upper(),
            ShippingRate.state.is_(None),
            ShippingRate.postal_code_pattern.is_(None),
            ShippingRate.is_active == True,
        )
    ).first()
    return rate


# ─────────────────────────── Endpoints ───────────────────────────

@router.post("/shipping/calculate", response_model=ShippingCalculateResponse)
def calculate_shipping(
    body: ShippingCalculateRequest,
    session: Session = Depends(get_session),
):
    """
    Calculate shipping cost for a given address and cart items.
    Returns the cheapest matching rate. Falls back to a default rate if no match.
    """
    rate = _find_shipping_rate(
        session,
        body.address.country,
        body.address.state,
        body.address.postal_code,
    )

    if not rate:
        # Default: no shipping rate configured → free shipping with long delivery window
        logger.warning(
            "No shipping rate found, using default",
            country=body.address.country,
            state=body.address.state,
        )
        return ShippingCalculateResponse(cost=0.0, delivery_days=14, provider="standard")

    logger.info(
        "Shipping rate found",
        country=body.address.country,
        rate=rate.rate,
        delivery_days=rate.delivery_days,
    )
    return ShippingCalculateResponse(
        cost=rate.rate,
        delivery_days=rate.delivery_days,
    )


@router.post("/tax/calculate", response_model=TaxCalculateResponse)
def calculate_tax(
    body: TaxCalculateRequest,
    session: Session = Depends(get_session),
):
    """
    Calculate tax for a given address and order.
    Looks up the applicable tax rate(s) by country/state and category.
    """
    country = body.address.country.upper()
    state = body.address.state

    # Collect applicable categories from items
    categories = list({item.category_slug for item in body.items if item.category_slug})

    breakdown: List[TaxBreakdownItem] = []
    total_tax = 0.0

    # For each category (and a catch-all for None), find the best matching tax rate
    checked_categories = set(categories) | {None}
    applied_rates: dict = {}  # rate_id → TaxBreakdownItem

    for category in checked_categories:
        # Build query: exact match (country + state + category), then fallbacks
        for cat_filter in [category, None]:
            state_filter_val = state if state else None

            stmt = select(Tax).where(
                Tax.country == country,
                Tax.is_active == True,
                Tax.category == cat_filter,
            )
            if state_filter_val:
                stmt_state = stmt.where(Tax.state == state_filter_val)
                tax_rule = session.exec(stmt_state).first()
                if not tax_rule:
                    tax_rule = session.exec(stmt.where(Tax.state.is_(None))).first()
            else:
                tax_rule = session.exec(stmt.where(Tax.state.is_(None))).first()

            if tax_rule and tax_rule.id not in applied_rates:
                # Prorate by items in this category
                if category is not None:
                    cat_items = [i for i in body.items if i.category_slug == category]
                    item_fraction = sum(i.quantity for i in cat_items) / max(1, sum(i.quantity for i in body.items))
                    taxable = body.subtotal * item_fraction
                else:
                    taxable = body.subtotal

                amount = round(taxable * tax_rule.tax_rate / 100, 2)
                total_tax += amount
                entry = TaxBreakdownItem(
                    category=cat_filter,
                    rate=tax_rule.tax_rate,
                    amount=amount,
                    description=tax_rule.description,
                )
                breakdown.append(entry)
                applied_rates[tax_rule.id] = entry
                break

    effective_rate = round((total_tax / body.subtotal * 100), 2) if body.subtotal > 0 else 0.0

    return TaxCalculateResponse(
        tax_amount=round(total_tax, 2),
        effective_rate=effective_rate,
        breakdown=breakdown,
    )
