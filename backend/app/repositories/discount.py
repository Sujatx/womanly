from typing import List, Optional
from sqlalchemy.orm import Session
from sqlmodel import select
from app.models.discount import Coupon, BulkDiscount, CustomerTier
from app.repositories.base import BaseRepository
from sqlmodel import select, func




class DiscountRepository(BaseRepository[Coupon]):
    def __init__(self):
        super().__init__(Coupon)

    def get_by_code(self, session: Session, code: str) -> Optional[Coupon]:
        return session.exec(select(Coupon).where(Coupon.code == code.upper())).first()

    def count_coupon_uses(self, session: Session, coupon_id: int) -> int:
        from app.models.discount import CouponUsage
        return session.exec(
            select(func.count(CouponUsage.id)).where(CouponUsage.coupon_id == coupon_id)
        ).one()

    def count_coupon_uses_by_user(self, session: Session, coupon_id: int, user_id: int) -> int:
        from app.models.discount import CouponUsage
        return session.exec(
            select(func.count(CouponUsage.id)).where(
                CouponUsage.coupon_id == coupon_id,
                CouponUsage.user_id == user_id,
            )
        ).one()

    def list_all(self, session: Session) -> List[Coupon]:
        return session.exec(select(Coupon)).all()

    def create_coupon(self, session: Session, coupon: Coupon) -> Coupon:
        session.add(coupon)
        session.flush()
        return coupon


class BulkDiscountRepository(BaseRepository[BulkDiscount]):
    def __init__(self):
        super().__init__(BulkDiscount)

    def list_active(self, session: Session) -> List[BulkDiscount]:
        return session.exec(select(BulkDiscount).where(BulkDiscount.is_active == True)).all()


class TierRepository(BaseRepository[CustomerTier]):
    def __init__(self):
        super().__init__(CustomerTier)

    def list_all(self, session: Session) -> List[CustomerTier]:
        return session.exec(select(CustomerTier)).all()
