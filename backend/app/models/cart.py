from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

from .product import Product, ProductVariant

class CartItemBase(SQLModel):
    variant_id: int = Field(foreign_key="productvariant.id")
    quantity: int = 1
    # selected_options is redundant if we have variant_id, but can be kept for display cache
    selected_options: Optional[str] = None 

class CartItem(CartItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cart_id: Optional[int] = Field(default=None, foreign_key="cart.id")
    cart: Optional["Cart"] = Relationship(back_populates="items")
    
    variant: Optional["ProductVariant"] = Relationship()

class Cart(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    
    items: List[CartItem] = Relationship(back_populates="cart")

# Schemas
class CartItemCreate(CartItemBase):
    pass

class CartItemRead(CartItemBase):
    id: int
    variant: Optional["ProductVariant"] = None

class CartRead(SQLModel):
    id: int
    items: List[CartItemRead]
    count: int = 0
    subtotal: float = 0.0
