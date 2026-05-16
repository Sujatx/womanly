"""
Shipping and Tax models.
"""

from typing import List, Optional
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
