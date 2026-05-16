"""Category repository for data access operations."""

from typing import List
from sqlalchemy.orm import Session
from sqlmodel import select

from app.models import Category
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self):
        super().__init__(Category)

    def list_all(self, session: Session) -> List[Category]:
        return session.exec(select(Category)).all()
