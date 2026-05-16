from typing import List, Optional
from sqlalchemy.orm import Session
from sqlmodel import select
from app.models import Wishlist, WishlistItem


class WishlistRepository:
    def __init__(self):
        pass

    def get_or_create(self, session: Session, user_id: int) -> Wishlist:
        stmt = select(Wishlist).where(Wishlist.user_id == user_id)
        wishlist = session.exec(stmt).first()
        if not wishlist:
            wishlist = Wishlist(user_id=user_id)
            session.add(wishlist)
            session.commit()
            session.refresh(wishlist)
        return wishlist

    def add_item(self, session: Session, wishlist_id: int, product_id: int) -> WishlistItem:
        item = WishlistItem(wishlist_id=wishlist_id, product_id=product_id)
        session.add(item)
        session.flush()
        return item

    def remove_item(self, session: Session, wishlist_id: int, product_id: int) -> None:
        stmt = select(WishlistItem).where(WishlistItem.wishlist_id == wishlist_id, WishlistItem.product_id == product_id)
        item = session.exec(stmt).first()
        if item:
            session.delete(item)

    def list_items(self, session: Session, wishlist_id: int) -> List[WishlistItem]:
        stmt = select(WishlistItem).where(WishlistItem.wishlist_id == wishlist_id)
        return session.exec(stmt).all()
