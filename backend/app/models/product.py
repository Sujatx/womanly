from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON
from decimal import Decimal

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
    price_adjustment: float = Field(default=0.0)
    stock_quantity: int = Field(default=0)
    is_available: bool = Field(default=True)
    
    product: "Product" = Relationship(back_populates="variants")

class ProductBase(SQLModel):
    title: str
    description: str
    price: float
    brand: Optional[str] = None
    thumbnail: Optional[str] = None
    category_slug: str

class Product(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    category_link: Optional["Category"] = Relationship(back_populates="products")
    
    variants: List[ProductVariant] = Relationship(back_populates="product")
    product_images: List[ProductImage] = Relationship(back_populates="product")