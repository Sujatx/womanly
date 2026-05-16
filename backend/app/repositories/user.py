"""User repository for data access operations."""

from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlmodel import select
from app.models import User
from app.repositories.base import BaseRepository, PaginationParams, SortParams
from app.core.logging import get_structured_logger

logger = get_structured_logger(__name__)


class UserRepository(BaseRepository[User]):
    """Repository for User entity operations."""
    
    def __init__(self):
        super().__init__(User)
    
    def get_by_email(self, session: Session, email: str) -> Optional[User]:
        """Get user by email address."""
        return session.exec(
            select(User).where(User.email == email.lower())
        ).first()
    
    def get_by_phone(self, session: Session, phone: str) -> Optional[User]:
        """Get user by phone number."""
        return session.exec(
            select(User).where(User.phone == phone)
        ).first()
    
    def email_exists(self, session: Session, email: str) -> bool:
        """Check if email is already registered."""
        return self.get_by_email(session, email) is not None
    
    def get_verified_users(
        self,
        session: Session,
        pagination: Optional[PaginationParams] = None,
    ) -> Tuple[List[User], int]:
        """Get users with verified email."""
        query = select(User).where(User.is_email_verified == True)
        total_count = len(session.exec(query).all())
        
        if pagination:
            query = query.offset(pagination.offset).limit(pagination.page_size)
        
        users = session.exec(query).all()
        return users, total_count
    
    def get_active_users(
        self,
        session: Session,
        pagination: Optional[PaginationParams] = None,
    ) -> Tuple[List[User], int]:
        """Get active (non-disabled) users."""
        query = select(User).where(User.is_active == True)
        total_count = len(session.exec(query).all())
        
        if pagination:
            query = query.offset(pagination.offset).limit(pagination.page_size)
        
        users = session.exec(query).all()
        return users, total_count
    
    def mark_email_verified(self, session: Session, user_id: int) -> User:
        """Mark user's email as verified."""
        user = self.get_by_id_or_raise(session, user_id)
        user.is_email_verified = True
        session.flush()
        logger.info(f"Email verified for user", user_id=user_id)
        return user
    
    def disable_account(self, session: Session, user_id: int) -> User:
        """Disable user account."""
        user = self.get_by_id_or_raise(session, user_id)
        user.is_active = False
        session.flush()
        logger.info(f"User account disabled", user_id=user_id)
        return user
    
    def enable_account(self, session: Session, user_id: int) -> User:
        """Re-enable user account."""
        user = self.get_by_id_or_raise(session, user_id)
        user.is_active = True
        session.flush()
        logger.info(f"User account enabled", user_id=user_id)
        return user

    def get_refresh_token(self, session: Session, token: str):
        """Retrieve a refresh token record by token string."""
        from app.models.user import RefreshToken
        return session.exec(select(RefreshToken).where(RefreshToken.token == token)).first()

    def get_verification_token(self, session: Session, token: str):
        """Retrieve an email verification token by token string."""
        from app.models.user import EmailVerificationToken
        return session.exec(
            select(EmailVerificationToken)
            .where(EmailVerificationToken.token == token)
            .where(EmailVerificationToken.is_used == False)
            .where(EmailVerificationToken.expires_at > datetime.utcnow())
        ).first()
