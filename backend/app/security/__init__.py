"""
Consolidated authentication/security helpers.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Dict
import uuid
import logging

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: str | Any, expires_delta: Optional[timedelta] = None) -> str:
    now = datetime.now(timezone.utc)
    expire = now + expires_delta if expires_delta else now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "exp": expire,
        "iat": now,
        "sub": str(subject),
        "type": "access",
        "aud": "womanly-backend",
    }
    return jwt.encode(to_encode, settings.SECRET_KEY.get_secret_value(), algorithm=settings.ALGORITHM)


def create_refresh_token(subject: str | Any, expires_delta: Optional[timedelta] = None) -> str:
    now = datetime.now(timezone.utc)
    expire = now + expires_delta if expires_delta else now + timedelta(days=7)
    to_encode = {
        "exp": expire,
        "iat": now,
        "sub": str(subject),
        "type": "refresh",
        "jti": str(uuid.uuid4()),
        "aud": "womanly-backend",
    }
    return jwt.encode(to_encode, settings.SECRET_KEY.get_secret_value(), algorithm=settings.ALGORITHM)


def verify_token(token: str, token_type: str = "access") -> Optional[Dict]:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY.get_secret_value(),
            algorithms=[settings.ALGORITHM],
            options={"verify_aud": False},
        )
        if payload.get("type") != token_type:
            logger.warning(f"Invalid token type. Expected {token_type}, got {payload.get('type')}")
            return None
        if not payload.get("sub"):
            logger.warning("Token missing 'sub' claim")
            return None
        return payload
    except jwt.ExpiredSignatureError:
        logger.debug(f"Token expired: {token[:20]}...")
        return None
    except JWTError as e:
        logger.warning(f"JWT validation error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error validating token: {str(e)}")
        return None


def verify_refresh_token(token: str) -> Optional[Dict]:
    return verify_token(token, token_type="refresh")


def verify_access_token(token: str) -> Optional[Dict]:
    return verify_token(token, token_type="access")
