"""
Rate limiting middleware to prevent brute force attacks.
Uses in-memory store for rate limiting (can be upgraded to Redis).
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class RateLimitStore:
    """In-memory rate limit store."""
    
    def __init__(self):
        self.attempts = defaultdict(list)  # key -> [timestamps]
    
    def is_rate_limited(self, key: str, max_attempts: int, window_seconds: int) -> bool:
        """
        Check if a key is rate limited.
        
        Args:
            key: Unique identifier (e.g., IP, email)
            max_attempts: Maximum attempts allowed in time window
            window_seconds: Time window in seconds
        
        Returns:
            True if rate limited, False otherwise
        """
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=window_seconds)
        
        # Remove old attempts outside the window
        self.attempts[key] = [
            attempt_time for attempt_time in self.attempts[key]
            if attempt_time > cutoff
        ]
        
        # Check if limit exceeded
        if len(self.attempts[key]) >= max_attempts:
            return True
        
        # Record this attempt
        self.attempts[key].append(now)
        return False
    
    def get_remaining(self, key: str, max_attempts: int) -> int:
        """Get number of remaining attempts."""
        return max(0, max_attempts - len(self.attempts.get(key, [])))
    
    def reset(self, key: str):
        """Reset rate limit for a key."""
        if key in self.attempts:
            del self.attempts[key]


# Global rate limit store
rate_limit_store = RateLimitStore()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware for protecting against brute force attacks.
    """
    
    # Rate limit configurations per endpoint
    RATE_LIMITS = {
        "/auth/login": {
            "max_attempts": 5,
            "window_seconds": 15 * 60,  # 15 minutes
        },
        "/auth/signup": {
            "max_attempts": 3,
            "window_seconds": 60 * 60,  # 1 hour
        },
        "/auth/verify-email": {
            "max_attempts": 10,
            "window_seconds": 60 * 60,  # 1 hour
        },
    }
    
    async def dispatch(self, request: Request, call_next):
        # Only rate limit configured endpoints
        path = request.url.path
        
        if path not in self.RATE_LIMITS:
            response = await call_next(request)
            return response
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Get rate limit config
        config = self.RATE_LIMITS[path]
        max_attempts = config["max_attempts"]
        window_seconds = config["window_seconds"]
        
        # Use IP as rate limit key
        rate_limit_key = f"{path}:{client_ip}"
        
        # Check rate limit
        if rate_limit_store.is_rate_limited(rate_limit_key, max_attempts, window_seconds):
            logger.warning(f"Rate limit exceeded for {path} from IP {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many attempts. Please try again later.",
                headers={
                    "Retry-After": str(window_seconds),
                    "X-RateLimit-Limit": str(max_attempts),
                    "X-RateLimit-Remaining": "0",
                }
            )
        
        # Proceed with request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = rate_limit_store.get_remaining(rate_limit_key, max_attempts)
        response.headers["X-RateLimit-Limit"] = str(max_attempts)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int((datetime.utcnow() + timedelta(seconds=window_seconds)).timestamp()))
        
        return response


def get_rate_limit_key(request: Request, identifier: str = None) -> str:
    """
    Get rate limit key for a request.
    
    Args:
        request: FastAPI request
        identifier: Optional identifier (e.g., email) to use instead of IP
    
    Returns:
        Rate limit key
    """
    if identifier:
        return f"{request.url.path}:{identifier}"
    
    client_ip = request.client.host if request.client else "unknown"
    return f"{request.url.path}:{client_ip}"


def check_rate_limit(
    key: str,
    max_attempts: int = 5,
    window_seconds: int = 900  # 15 minutes default
) -> bool:
    """
    Check if a specific key is rate limited.
    
    Can be used in endpoints for custom rate limiting logic.
    """
    return rate_limit_store.is_rate_limited(key, max_attempts, window_seconds)
