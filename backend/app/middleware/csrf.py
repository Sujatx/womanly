"""
CSRF (Cross-Site Request Forgery) protection middleware for FastAPI.
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from sqlmodel import Session, select
from datetime import datetime, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    CSRF protection middleware.
    - Generates CSRF tokens for safe request
    - Validates CSRF tokens on state-changing requests (POST/PUT/DELETE)
    """
    
    EXCLUDED_PATHS = {
        "/health", 
        "/", 
        "/api/v1/auth/signup",
        "/api/v1/auth/login",
        "/api/v1/auth/verify-email",
        "/auth/signup",
        "/auth/login",
        "/auth/verify-email",
        "/docs",
        "/openapi.json"
    }  # Paths that don't need CSRF protection
    STATE_CHANGING_METHODS = {"POST", "PUT", "DELETE", "PATCH"}
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip CSRF check for excluded paths and GET requests
        if request.url.path in self.EXCLUDED_PATHS or request.method not in self.STATE_CHANGING_METHODS:
            response = await call_next(request)
            return response
        
        # Skip CSRF check for authenticated requests (Bearer token provides CSRF protection)
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            response = await call_next(request)
            return response
        
        # For state-changing requests without auth, validate CSRF token
        csrf_token = request.headers.get("X-CSRF-Token")
        
        if not csrf_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token missing. Include X-CSRF-Token header for state-changing requests."
            )
        
        # Note: Actual token validation happens in a dependency
        # This middleware just validates that the header is present
        
        response = await call_next(request)
        return response


def generate_csrf_token_value() -> str:
    """Generate a secure CSRF token."""
    return str(uuid.uuid4())


def create_csrf_token_in_db(session: Session, session_id: str = None) -> str:
    """Create and store a CSRF token in the database."""
    from app.models.user import CSRFToken
    
    token = generate_csrf_token_value()
    csrf_token = CSRFToken(
        token=token,
        session_id=session_id or str(uuid.uuid4()),
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    session.add(csrf_token)
    session.commit()
    
    return token


def validate_csrf_token(session: Session, token: str) -> bool:
    """Validate a CSRF token."""
    from app.models.user import CSRFToken
    
    csrf_token = session.exec(
        select(CSRFToken).where(CSRFToken.token == token)
    ).first()
    
    if not csrf_token:
        logger.warning(f"Invalid CSRF token attempted: {token[:10]}...")
        return False
    
    # Check if token is expired
    if csrf_token.expires_at < datetime.utcnow():
        logger.warning("CSRF token expired")
        return False
    
    # Check if token has already been used
    if csrf_token.is_used:
        logger.warning("CSRF token already used")
        return False
    
    # Mark token as used
    csrf_token.is_used = True
    session.add(csrf_token)
    session.commit()
    
    return True


def get_csrf_token_dependency(request: Request, session: Session):
    """
    Dependency to validate CSRF token.
    Use this in endpoints that modify state.
    """
    csrf_token = request.headers.get("X-CSRF-Token")
    
    if not csrf_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing"
        )
    
    if not validate_csrf_token(session, csrf_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired CSRF token"
        )
    
    return True
