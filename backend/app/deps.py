from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session, select
from app.db import get_session
from app.config import settings
from app.models import User
from app.models.user import BlacklistedToken
from app.security.token import verify_access_token
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: Session = Depends(get_session)) -> User:
    """
    Get current authenticated user from JWT token.
    
    Uses improved JWT validation with claim verification.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        logger.info(f"Validating token: {token[:20]}...")
        # Verify token with proper claim validation
        payload = verify_access_token(token)
        if not payload:
            logger.warning("Token validation failed: payload is None")
            raise credentials_exception
        
        email: str = payload.get("sub")
        if email is None:
            logger.warning("Token validation failed: missing 'sub' claim")
            raise credentials_exception
        
        logger.info(f"Token validated for email: {email}")
            
    except JWTError as e:
        logger.warning(f"JWT validation error: {str(e)}")
        raise credentials_exception
    
    # Check if token is blacklisted (revoked)
    blacklisted = session.exec(
        select(BlacklistedToken).where(BlacklistedToken.token == token)
    ).first()
    
    if blacklisted:
        logger.warning(f"Attempted use of blacklisted token for user: {email}")
        raise credentials_exception
        
    # Get user from database (exclude soft-deleted users)
    user = session.exec(select(User).where(User.email == email, User.deleted_at.is_(None))).first()
    if user is None:
        logger.warning(f"User not found for email in token: {email}")
        raise credentials_exception
    
    return user


from fastapi.security import OAuth2PasswordBearer as _OAuth2Opt
from typing import Optional as _Opt

_oauth2_optional = _OAuth2Opt(tokenUrl="auth/login", auto_error=False)

def get_current_user_optional(
    token: _Opt[str] = Depends(_oauth2_optional),
    session: Session = Depends(get_session),
) -> _Opt[User]:
    """
    Like get_current_user but returns None instead of 401 for anonymous requests.
    Used by endpoints that work for both authenticated and anonymous users.
    """
    if not token:
        return None
    try:
        payload = verify_access_token(token)
        if not payload:
            return None
        email: str = payload.get("sub")
        if not email:
            return None
        user = session.exec(select(User).where(User.email == email, User.deleted_at.is_(None))).first()
        return user
    except Exception:
        return None
