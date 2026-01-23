from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

class CategoryBase(SQLModel):
    name: str = Field(index=True, unique=True)
    slug: str = Field(index=True, unique=True)

class Category(CategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    products: List["Product"] = Relationship(back_populates="category_link")
