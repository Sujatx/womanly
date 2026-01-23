from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON

# Forward reference
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .category import Category

class ProductBase(SQLModel):
    title: str
    description: str
    price: float
    brand: Optional[str] = None
    thumbnail: Optional[str] = None
    images: List[str] = Field(default=[], sa_column=Column(JSON))
    tags: List[str] = Field(default=[], sa_column=Column(JSON))
    category_slug: str # Denormalized for easy access, or just use the relation

class Product(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    category_link: Optional["Category"] = Relationship(back_populates="products")
