from typing import Optional
from sqlalchemy.orm import Session
from sqlmodel import select
from app.models.shipping import ShippingRate, Tax
from app.repositories.base import BaseRepository


class ShippingRepository:
    def __init__(self):
        # lightweight helper; not a BaseRepository because logic is custom
        pass

    def find_shipping_rate(self, session: Session, country: str, state: Optional[str], postal_code: Optional[str]) -> Optional[ShippingRate]:
        country_u = country.upper() if country else country
        # 1. Exact: country + state + postal prefix
        if postal_code and state:
            rate = session.exec(
                select(ShippingRate).where(
                    ShippingRate.country == country_u,
                    ShippingRate.state == state,
                    ShippingRate.is_active == True,
                )
            ).all()
            for r in rate:
                if r.postal_code_pattern and postal_code.startswith(r.postal_code_pattern):
                    return r

        # 2. Country + state
        if state:
            rate = session.exec(
                select(ShippingRate).where(
                    ShippingRate.country == country_u,
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
                ShippingRate.country == country_u,
                ShippingRate.state.is_(None),
                ShippingRate.postal_code_pattern.is_(None),
                ShippingRate.is_active == True,
            )
        ).first()
        return rate


class TaxRepository:
    def __init__(self):
        pass

    def find_applicable_tax(self, session: Session, country: str, state: Optional[str], category: Optional[str]):
        country_u = country.upper() if country else country
        state_val = state if state else None

        # Try exact category then fallback to None
        for cat_filter in [category, None]:
            if state_val:
                stmt_state = select(Tax).where(
                    Tax.country == country_u,
                    Tax.is_active == True,
                    Tax.category == cat_filter,
                    Tax.state == state_val,
                )
                tax_rule = session.exec(stmt_state).first()
                if tax_rule:
                    return tax_rule
                tax_rule = session.exec(select(Tax).where(
                    Tax.country == country_u,
                    Tax.is_active == True,
                    Tax.category == cat_filter,
                    Tax.state.is_(None),
                )).first()
                if tax_rule:
                    return tax_rule
            else:
                tax_rule = session.exec(select(Tax).where(
                    Tax.country == country_u,
                    Tax.is_active == True,
                    Tax.category == cat_filter,
                    Tax.state.is_(None),
                )).first()
                if tax_rule:
                    return tax_rule

        return None
