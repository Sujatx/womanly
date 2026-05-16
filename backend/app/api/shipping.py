"""
Shipping & Tax calculation endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db import get_session
from app.models.shipping import (
    ShippingRate,
    Tax,
    AddressInput,
    CartItemInput,
    ShippingCalculateRequest,
    ShippingCalculateResponse,
    TaxCalculateRequest,
    TaxBreakdownItem,
    TaxCalculateResponse,
)
from app.core.logging import get_structured_logger
from app.di_container import get as di_get

router = APIRouter()
logger = get_structured_logger(__name__)


# ─────────────────────────── Helpers ───────────────────────────

def _find_shipping_rate(session: Session, country: str, state: Optional[str], postal_code: Optional[str]) -> Optional[ShippingRate]:
    # Delegate to repository
    return di_get("shipping_repo").find_shipping_rate(session, country, state, postal_code)


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
        tax_repo = di_get("tax_repo")
        tax_rule = tax_repo.find_applicable_tax(session, country, state, category)
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
