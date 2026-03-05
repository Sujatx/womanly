from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON
from decimal import Decimal
from datetime import datetime
from pydantic import field_validator

# Forward reference
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .category import Category

class ProductImage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    image_url: str
    alt_text: Optional[str] = None
    display_order: int = Field(default=0)
    is_primary: bool = Field(default=False)
    
    product: "Product" = Relationship(back_populates="product_images")

class ProductVariant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    sku: str = Field(unique=True, index=True)
    size: Optional[str] = None
    color: Optional[str] = None
    material: Optional[str] = None
    price_adjustment: float = Field(
        default=0.0,
        description="Price adjustment (can be positive or negative)"
    )
    stock_quantity: int = Field(
        default=0,
        ge=0,  # Must be >= 0
        description="Stock quantity"
    )
    reserved_quantity: int = Field(
        default=0,
        ge=0,
        description="Quantity currently reserved (pending payments)"
    )
    is_available: bool = Field(default=True)

    @property
    def available_stock(self) -> int:
        """Actual stock available for new orders (stock minus reservations)."""
        return max(0, self.stock_quantity - self.reserved_quantity)
    
    product: "Product" = Relationship(back_populates="variants")
    
    @field_validator('price_adjustment')
    @classmethod
    def validate_price_adjustment(cls, v):
        """Ensure price adjustment doesn't exceed max value."""
        if v < -1000000 or v > 1000000:
            raise ValueError('price_adjustment must be between -1000000 and 1000000')
        return v

class ProductBase(SQLModel):
    title: str
    description: str
    price: float = Field(
        gt=0,  # Must be > 0
        le=1000000,  # Maximum price
        description="Product price (must be positive)"
    )
    brand: Optional[str] = None
    thumbnail: Optional[str] = None
    category_slug: str

class Product(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    category_link: Optional["Category"] = Relationship(back_populates="products")
    
    # Soft delete support
    deleted_at: Optional[datetime] = Field(default=None, index=True)
    
    variants: List[ProductVariant] = Relationship(back_populates="product")
    product_images: List[ProductImage] = Relationship(back_populates="product")
    
    def soft_delete(self):
        """Mark product as deleted (soft delete)."""
        self.deleted_at = datetime.utcnow()
    
    def is_deleted(self) -> bool:
        """Check if product is soft deleted."""
        return self.deleted_at is not None