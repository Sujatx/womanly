from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Dict
from jose import jwt, JWTError
from app.config import settings
import uuid
import logging

logger = logging.getLogger(__name__)


def create_access_token(subject: str | Any, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create an access token with proper JWT claims.
    
    JWT claims included:
    - exp: Token expiration
    - iat: Issued-at time
    - sub: Subject (user email)
    - type: Token type (access)
    - aud: Audience (backend domain)
    """
    now = datetime.now(timezone.utc)
    
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "exp": expire,
        "iat": now,
        "sub": str(subject),
        "type": "access",
        "aud": "womanly-backend"  # Audience validation
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY.get_secret_value(),
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(subject: str | Any, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a refresh token with 7-day expiration (unless specified).
    
    JWT claims included:
    - exp: Token expiration
    - iat: Issued-at time
    - sub: Subject (user email)
    - type: Token type (refresh)
    - jti: JWT ID (unique identifier for token rotation)
    - aud: Audience (backend domain)
    """
    now = datetime.now(timezone.utc)
    
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=7)
    
    jti = str(uuid.uuid4())  # JWT ID for unique identification
    to_encode = {
        "exp": expire,
        "iat": now,
        "sub": str(subject),
        "type": "refresh",
        "jti": jti,
        "aud": "womanly-backend"  # Audience validation
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY.get_secret_value(),
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[Dict]:
    """
    Verify and decode a JWT token with claim validation.
    
    Args:
        token: JWT token to verify
        token_type: Expected token type ('access' or 'refresh')
    
    Returns:
        Decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY.get_secret_value(),
            algorithms=[settings.ALGORITHM]
        )
        
        # Validate token type
        if payload.get("type") != token_type:
            logger.warning(f"Invalid token type. Expected {token_type}, got {payload.get('type')}")
            return None
        
        # Validate audience
        if payload.get("aud") != "womanly-backend":
            logger.warning(f"Invalid token audience: {payload.get('aud')}")
            return None
        
        # Validate iat (issued-at) claim
        iat = payload.get("iat")
        if not iat:
            logger.warning("Token missing 'iat' claim")
            return None
        
        # Ensure token was issued in the past
        if iat > datetime.now(timezone.utc).timestamp():
            logger.warning("Token 'iat' claim is in the future")
            return None
        
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.debug(f"Token expired: {token[:20]}...")
        return None
    except jwt.JWTError as e:
        logger.warning(f"JWT validation error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error validating token: {str(e)}")
        return None


def verify_refresh_token(token: str) -> Optional[Dict]:
    """Verify refresh token and return payload."""
    return verify_token(token, token_type="refresh")


def verify_access_token(token: str) -> Optional[Dict]:
    """Verify access token and return payload."""
    return verify_token(token, token_type="access")
