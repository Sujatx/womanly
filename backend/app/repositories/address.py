from typing import List
from sqlalchemy.orm import Session
from sqlmodel import select
from app.models import Address
from app.repositories.base import BaseRepository


class AddressRepository(BaseRepository[Address]):
    def __init__(self):
        super().__init__(Address)

    def list_by_user(self, session: Session, user_id: int) -> List[Address]:
        return session.exec(select(Address).where(Address.user_id == user_id)).all()

    def unset_defaults(self, session: Session, user_id: int, exclude_id: int | None = None) -> None:
        query = select(Address).where(Address.user_id == user_id)
        if exclude_id is not None:
            query = query.where(Address.id != exclude_id)
        for addr in session.exec(query).all():
            addr.is_default = False
            session.add(addr)
