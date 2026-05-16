from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship


class WishlistItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    wishlist_id: Optional[int] = Field(default=None, foreign_key="wishlist.id")
    product_id: int

    wishlist: Optional["Wishlist"] = Relationship(back_populates="items")


class Wishlist(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")

    items: List[WishlistItem] = Relationship(back_populates="wishlist")


class WishlistItemRead(SQLModel):
    id: int
    product_id: int
    title: Optional[str] = None
    thumbnail: Optional[str] = None
    price: Optional[float] = None


class WishlistAddRequest(SQLModel):
    product_id: int


class WishlistRead(SQLModel):
    id: int
    items: List[WishlistItemRead]
    count: int
