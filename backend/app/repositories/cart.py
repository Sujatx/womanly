from typing import Optional
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from app.repositories.base import BaseRepository
from app.models import Cart, CartItem
from app.models.product import ProductVariant, Product


class CartRepository(BaseRepository):
    def __init__(self):
        super().__init__(Cart)

    def get_cart_with_items(self, session: Session, user_id: int) -> Optional[Cart]:
        stmt = (
            select(Cart)
            .where(Cart.user_id == user_id)
            .options(
                selectinload(Cart.items).options(
                    selectinload(CartItem.variant).selectinload(ProductVariant.product)
                )
            )
        )
        return session.exec(stmt).first()

    def clear_cart(self, session: Session, user_id: int) -> None:
        cart = session.exec(select(Cart).where(Cart.user_id == user_id)).first()
        if cart:
            session.delete(cart)
            session.commit()
