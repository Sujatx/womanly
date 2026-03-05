"""
Shipping and Tax models.
"""

from typing import Optional
from sqlmodel import SQLModel, Field


class ShippingRate(SQLModel, table=True):
    """
    Shipping rate for a specific region.
    Postal code pattern is a simple prefix — e.g. '110' matches all Delhi postcodes.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    country: str = Field(index=True, description="ISO country code, e.g. 'IN', 'US'")
    state: Optional[str] = Field(default=None, description="State/province code")
    postal_code_pattern: Optional[str] = Field(default=None, description="Postcode prefix to match")
    rate: float = Field(ge=0, description="Shipping cost in base currency (INR)")
    delivery_days: int = Field(ge=0, description="Estimated delivery days")
    is_active: bool = Field(default=True)


class ShippingCountry(SQLModel, table=True):
    """Countries supported for shipping."""

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(unique=True, index=True, description="ISO country code, e.g. 'IN'")
    name: str
    is_supported: bool = Field(default=True)
    customs_info: Optional[str] = Field(default=None, description="Customs/duties information shown to customer")


class Tax(SQLModel, table=True):
    """
    Tax rate for a country/state and product category combination.
    category=None applies to all products.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    country: str = Field(index=True, description="ISO country code")
    state: Optional[str] = Field(default=None, description="State code (None = country-wide)")
    tax_rate: float = Field(ge=0, le=100, description="Tax rate as a percentage")
    category: Optional[str] = Field(default=None, description="Product category slug (None = all categories)")
    description: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
