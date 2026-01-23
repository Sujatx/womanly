from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

class WishlistItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    wishlist_id: Optional[int] = Field(default=None, foreign_key="wishlist.id")
    product_id: int # Just the ID, or link to Product
    
    wishlist: Optional["Wishlist"] = Relationship(back_populates="items")

class Wishlist(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    
    items: List[WishlistItem] = Relationship(back_populates="wishlist")
