"""
Idempotency middleware for payment endpoints.
Ensures duplicate requests return the same response.
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from sqlmodel import Session, select
from datetime import datetime, timedelta, timezone
import hashlib
import json
import logging

logger = logging.getLogger(__name__)

# Endpoints that require idempotency
IDEMPOTENT_ENDPOINTS = {
    "/api/v1/payments/create-order",
    "/api/v1/payments/verify"
}

# TTL for idempotency keys (1 hour)
IDEMPOTENCY_KEY_TTL = timedelta(hours=1)


async def store_idempotency_key(
    session: Session,
    idempotency_key: str,
    user_id: int,
    endpoint: str,
    request_body: bytes,
    response_json: str,
    response_status: int
):
    """Store idempotency key and response."""
    from app.models.idempotency import IdempotencyKey
    
    request_hash = hashlib.sha256(request_body).hexdigest()
    
    key = IdempotencyKey(
        idempotency_key=idempotency_key,
        user_id=user_id,
        endpoint=endpoint,
        request_hash=request_hash,
        response_json=response_json,
        response_status_code=response_status,
        expires_at=datetime.now(timezone.utc) + IDEMPOTENCY_KEY_TTL
    )
    
    session.add(key)
    session.commit()
    
    logger.info(f"Stored idempotency key: {idempotency_key} for {endpoint}")


async def get_cached_response(
    session: Session,
    idempotency_key: str,
    endpoint: str,
    user_id: int
):
    """Retrieve cached response for idempotency key."""
    from app.models.idempotency import IdempotencyKey
    
    key = session.exec(
        select(IdempotencyKey)
        .where(IdempotencyKey.idempotency_key == idempotency_key)
        .where(IdempotencyKey.endpoint == endpoint)
        .where(IdempotencyKey.user_id == user_id)
    ).first()
    
    if not key:
        return None
    
    # Check if expired
    if key.is_expired():
        session.delete(key)
        session.commit()
        return None
    
    return key


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """
    Idempotency middleware for payment endpoints.
    
    Clients should send Idempotency-Key header with a unique identifier.
    If the same key is received again within the TTL, the original response is returned.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Only apply to idempotent endpoints
        if request.url.path not in IDEMPOTENT_ENDPOINTS:
            response = await call_next(request)
            return response
        
        # Check for Idempotency-Key header
        idempotency_key = request.headers.get("Idempotency-Key")
        
        if not idempotency_key:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Idempotency-Key header is required for payment endpoints"},
            )
        
        # Validate key format (should be a UUID or similar)
        if len(idempotency_key) < 8 or len(idempotency_key) > 255:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Invalid Idempotency-Key format"},
            )
        
        # Note: Actual idempotency checking happens in payment endpoints
        # This middleware just validates the header presence
        
        response = await call_next(request)
        return response


def get_idempotency_key_from_request(request: Request) -> str:
    """Extract idempotency key from request headers."""
    idempotency_key = request.headers.get("Idempotency-Key")
    
    if not idempotency_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Idempotency-Key header is required"
        )
    
    return idempotency_key
