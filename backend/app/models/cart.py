from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

from .product import Product

class CartItemBase(SQLModel):
    product_id: int
    quantity: int = 1
    selected_options: Optional[str] = None 

class CartItem(CartItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cart_id: Optional[int] = Field(default=None, foreign_key="cart.id")
    cart: Optional["Cart"] = Relationship(back_populates="items")
    
    # Unidirectional relationship to Product
    # We need to import Product in the file where we use this, or use string forward ref
    # But SQLModel Relationship needs to know the target.
    # Since we use string "Product", we need to make sure Product is registered in metadata
    # by importing it in models/__init__.py
    product: Optional["Product"] = Relationship()

class Cart(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    
    items: List[CartItem] = Relationship(back_populates="cart")

# Schemas
class CartItemCreate(CartItemBase):
    pass

class CartItemRead(CartItemBase):
    id: int
    product: Optional["Product"] = None

class CartRead(SQLModel):
    id: int
    items: List[CartItemRead]
    count: int = 0
    subtotal: float = 0.0